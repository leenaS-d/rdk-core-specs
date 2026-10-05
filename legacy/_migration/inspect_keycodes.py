"""Inspect the legacy firebolt-key-codes page structure.

Reports how the main key tables and the per-key detail tables are wired
together, so the block-schema extractor targets the right nodes.
"""
from __future__ import annotations

import re
from pathlib import Path

from lxml import html as lxml_html

LEGACY = Path(__file__).resolve().parent.parent / "video" / "rdk8"
PAGE = LEGACY / "firebolt-key-codes.html"


def text(node) -> str:
    return re.sub(r"\s+", " ", node.text_content() or "").strip()


def main() -> None:
    doc = lxml_html.fromstring(PAGE.read_text(encoding="utf-8"))

    print("=== sections in <main> ===")
    for section in doc.xpath("//main//section"):
        ident = section.get("id") or ""
        cls = section.get("class") or ""
        heading = section.xpath(".//h1|.//h2|.//h3")
        label = text(heading[0]) if heading else ""
        print(f"  section id={ident!r} class={cls!r} heading={label!r}")

    print("\n=== top-level tables (not inside <template>) ===")
    for table in doc.xpath("//main//table"):
        if table.xpath("ancestor::template"):
            continue
        headers = [text(th) for th in table.xpath(".//thead//th")]
        rows = table.xpath(".//tbody/tr")
        print(f"  headers={headers}  rows={len(rows)}  class={table.get('class')!r}")
        if rows:
            cells = rows[0].xpath("./td")
            print("    first row cells:")
            for index, cell in enumerate(cells):
                link = cell.xpath(".//a|.//button")
                target = (link[0].get("data-template") or link[0].get("href") or "") if link else ""
                print(f"      [{index}] {text(cell)[:60]!r} target={target!r}")

    templates = doc.xpath("//template")
    print(f"\n=== templates: {len(templates)} ===")
    for node in templates[:2]:
        print(f"  template id={node.get('id')!r}")
        for entry in node.xpath(".//section[contains(@class,'spec-entry')]"):
            heading = entry.xpath(".//h2|.//h3")
            print(f"    entry heading={text(heading[0]) if heading else ''!r}")
            for child in entry:
                tag = child.tag
                cls = child.get("class") or ""
                if tag == "div" and "table" in cls:
                    for table in child.xpath(".//table"):
                        rows = table.xpath(".//tr")
                        print(f"      table rows={len(rows)} class={table.get('class')!r}")
                        for row in rows:
                            cells = [text(c) for c in row.xpath("./th|./td")]
                            tags = [c.tag for c in row.xpath("./th|./td")]
                            print(f"        {tags} {cells}")
                else:
                    print(f"      <{tag} class={cls!r}> {text(child)[:70]!r}")

    print("\n=== modal trigger wiring ===")
    for script in doc.xpath("//script"):
        body = script.text_content() or ""
        for pattern in (r"data-[a-z-]+", r"getElementById\(['\"][^'\"]+", r"querySelectorAll\(['\"][^'\"]+"):
            for hit in sorted(set(re.findall(pattern, body)))[:12]:
                print("   ", hit)


if __name__ == "__main__":
    main()
