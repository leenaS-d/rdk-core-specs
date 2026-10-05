"""Dump the structure of a legacy spec page so its extractor can be written.

Usage:
    python inspect_page.py firebolt-intents.html
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from lxml import html as lxml_html

LEGACY = Path(__file__).resolve().parent.parent / "video" / "rdk8"


def flat(node) -> str:
    return re.sub(r"\s+", " ", node.text_content() or "").strip()


def describe(node, depth: int = 0, limit: int = 3) -> None:
    pad = "  " * depth
    cls = node.get("class") or ""
    ident = node.get("id") or ""
    label = f"{node.tag}"
    if cls:
        label += f".{cls.replace(' ', '.')}"
    if ident:
        label += f"#{ident}"
    if node.tag == "table":
        headers = [flat(th) for th in node.xpath(".//thead//th")] or [flat(th) for th in node.xpath(".//tr[1]/th")]
        rows = node.xpath(".//tbody/tr") or node.xpath(".//tr")
        print(f"{pad}{label}  headers={headers} rows={len(rows)}")
        return
    print(f"{pad}{label}  {flat(node)[:70]!r}")
    if depth >= limit:
        return
    for child in node:
        if isinstance(child.tag, str):
            describe(child, depth + 1, limit)


def main() -> None:
    name = sys.argv[1]
    doc = lxml_html.fromstring((LEGACY / name).read_text(encoding="utf-8"))

    print("=== main children (templates excluded) ===")
    for node in doc.xpath("//main")[0]:
        if node.tag == "template":
            continue
        describe(node, 0, 3)

    print("\n=== anchors/triggers pointing at templates ===")
    seen = set()
    for link in doc.xpath("//main//a[starts-with(@href,'#')] | //main//button[@data-modal-target]"):
        key = (link.get("class"), link.get("href") or link.get("data-modal-target"))
        if key[0] in seen:
            continue
        seen.add(key[0])
        print(f"  class={link.get('class')!r} target={key[1]!r} text={flat(link)[:40]!r}")

    templates = doc.xpath("//template")
    print(f"\n=== templates: {len(templates)} (showing 1) ===")
    if templates:
        for child in templates[0]:
            describe(child, 1, 4)


if __name__ == "__main__":
    main()
