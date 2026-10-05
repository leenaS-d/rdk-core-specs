"""One-time analysis of the legacy RDK8 video HTML pages.

Prints the structural outline of each page so the extractor can target the
right nodes. Not part of the site build.
"""
from __future__ import annotations

import re
from pathlib import Path

from lxml import html as lxml_html

LEGACY = Path(__file__).resolve().parent.parent / "video" / "rdk8"
PAGES = [
    "index.html",
    "component-catalog.html",
    "northbound-api-spec.html",
    "southbound-api-spec.html",
    "firebolt-api-spec.html",
    "firebolt-json-rpc.html",
    "firebolt-intents.html",
    "firebolt-key-codes.html",
]


def describe(node) -> str:
    tag = node.tag if isinstance(node.tag, str) else "comment"
    cls = node.get("class")
    ident = node.get("id")
    label = tag
    if cls:
        label += f".{'.'.join(cls.split())}"
    if ident:
        label += f"#{ident}"
    return label


def outline(node, depth: int, out: list[str], max_depth: int) -> None:
    if depth > max_depth:
        return
    for child in node:
        if not isinstance(child.tag, str):
            continue
        text = (child.text_content() or "").strip()
        preview = re.sub(r"\s+", " ", text)[:60]
        out.append(f"{'  ' * depth}{describe(child)}  | {preview}")
        if child.tag not in {"table", "script", "style"}:
            outline(child, depth + 1, out, max_depth)


def main() -> None:
    for name in PAGES:
        path = LEGACY / name
        if not path.exists():
            print(f"\n### {name}  (MISSING)")
            continue
        doc = lxml_html.fromstring(path.read_text(encoding="utf-8"))
        print(f"\n{'=' * 70}\n### {name}")
        title = doc.findtext(".//title") or ""
        print(f"title: {title!r}")

        inline_styles = doc.xpath("//style")
        styled_attrs = doc.xpath("//*[@style]")
        scripts = doc.xpath("//script")
        tables = doc.xpath("//table")
        print(
            f"inline <style> blocks: {len(inline_styles)} | "
            f"elements with style=: {len(styled_attrs)} | "
            f"<script>: {len(scripts)} | <table>: {len(tables)}"
        )
        for table in tables:
            headers = [th.text_content().strip() for th in table.xpath(".//thead//th")]
            rows = len(table.xpath(".//tbody/tr"))
            print(f"  table headers={headers} server_rows={rows}")
        for script in scripts:
            body = script.text_content() or ""
            match = re.search(r"const DATA=(\[.*?\]);", body, re.S)
            if match:
                print(f"  script embeds DATA array, {len(match.group(1))} chars")

        main_el = doc.xpath("//main")
        if main_el:
            lines: list[str] = []
            outline(main_el[0], 0, lines, max_depth=2)
            print("main outline:")
            print("\n".join(lines))


if __name__ == "__main__":
    main()
