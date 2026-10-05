"""Bootstrap firebolt-key-codes.json from the legacy generated page.

The legacy HTML is used as the source rather than the PDF because it already
contains the corrected content (post PARAMETER_OVERRIDES) and the resolved
colour-coded statuses. This runs once; afterwards the JSON is the source of
truth and this script is not part of the build.

Output: video/rdk8/assets/data/firebolt-key-codes.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from lxml import html as lxml_html

ROOT = Path(__file__).resolve().parent.parent.parent
LEGACY = ROOT / "legacy" / "video" / "rdk8" / "firebolt-key-codes.html"
OUT = ROOT / "video" / "rdk8" / "assets" / "data" / "firebolt-key-codes.json"

# Column header -> stable JSON key. Edit here if the spec renames a column.
COLUMN_KEYS = {
    "RCU Button": "button",
    "Key is mandatorily supported on a remote": "mandatory",
    "Linux Key code (Sent via Wayland)": "linuxCode",
    "View details": "details",
}


def cell_text(node) -> str:
    """Text of a cell, keeping line breaks but collapsing runs of spaces."""
    for br in node.xpath(".//br"):
        br.tail = "\n" + (br.tail or "")
    raw = node.text_content() or ""
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def flat(node) -> str:
    return re.sub(r"\s+", " ", node.text_content() or "").strip()


def detail_block(template) -> dict[str, Any] | None:
    entry = template.xpath(".//section[contains(@class,'spec-entry')]")
    if not entry:
        return None
    entry = entry[0]
    head = entry.xpath(".//div[contains(@class,'spec-entry-head')]")
    eyebrow = ""
    heading = ""
    if head:
        parts = head[0].xpath("./*")
        if parts:
            eyebrow = flat(parts[0])
            heading = flat(parts[1]) if len(parts) > 1 else ""
    fields = []
    for row in entry.xpath(".//table//tr"):
        label = row.xpath("./th")
        value = row.xpath("./td")
        if label and value:
            fields.append({"label": cell_text(label[0]), "value": cell_text(value[0])})
    return {"type": "fields", "eyebrow": eyebrow, "heading": heading, "fields": fields}


def main() -> None:
    doc = lxml_html.fromstring(LEGACY.read_text(encoding="utf-8"))
    templates = {node.get("id"): node for node in doc.xpath("//template")}

    hero_section = doc.xpath("//section[contains(@class,'hero')]")[0]
    eyebrow = hero_section.xpath(".//div[contains(@class,'eyebrow')]")
    description = hero_section.xpath(".//p")
    status = hero_section.xpath(".//span[contains(@class,'hero-status-badge')]")
    hero = {
        "eyebrow": flat(eyebrow[0]) if eyebrow else "",
        "title": flat(hero_section.xpath(".//h1")[0]),
        "description": flat(description[0]) if description else "",
        "status": flat(status[0]).replace("Catalog status:", "").strip() if status else "",
    }

    blocks: list[dict[str, Any]] = []
    definitions: dict[str, Any] = {}
    for section in doc.xpath("//main//section[contains(@class,'spec-intro')]"):
        heading_nodes = section.xpath("./h2")
        children: list[dict[str, Any]] = []

        # Walk children in document order so headings, prose and tables keep
        # the sequence the page was authored in.
        for child in section.iterchildren():
            # <template> holds the modal detail tables; they are pulled in via
            # the row that links to them, not rendered inline.
            if child.tag in ("template", "h2", "h3"):
                continue
            if child.tag == "p":
                prose = {"type": "prose", "body": flat(child)}
                if child.get("class"):
                    prose["variant"] = child.get("class")
                children.append(prose)
                continue

            tables = [child] if child.tag == "table" else child.xpath("./table|./div/table")
            if not tables:
                continue
            table = tables[0]
            headers = [flat(th) for th in table.xpath(".//thead//th")]
            keys = [COLUMN_KEYS.get(h, re.sub(r"\W+", "_", h).strip("_").lower()) for h in headers]
            columns = [{"key": key, "label": label} for key, label in zip(keys, headers)]

            rows = []
            for tr in table.xpath(".//tbody/tr"):
                cells = tr.xpath("./td")
                record: dict[str, Any] = {}
                for key, cell in zip(keys, cells):
                    link = cell.xpath(".//a[starts-with(@href,'#')]")
                    if link:
                        target = link[0].get("href").lstrip("#")
                        if target in templates and target not in definitions:
                            definitions[target] = detail_block(templates[target])
                        record[key] = {
                            "type": "actions",
                            "items": [{"label": flat(link[0]), "ref": target}],
                        }
                    else:
                        record[key] = cell_text(cell)
                rows.append(record)

            children.append({
                "type": "table",
                "classes": "key-codes-table",
                "columns": columns,
                "rows": rows,
            })

        blocks.append({
            "type": "section",
            "id": section.get("id") or "",
            "heading": flat(heading_nodes[0]) if heading_nodes else "",
            "blocks": children,
        })

    payload = {
        "schemaVersion": "1.0",
        "status": hero["status"] or "Published",
        "hero": hero,
        "source": {
            "label": "Firebolt 8 key code Spec.pdf",
            "href": "assets/pdf/Firebolt 8 key code Spec.pdf",
        },
        "blocks": blocks,
        "definitions": definitions,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    tables = [c for b in blocks for c in b["blocks"] if c["type"] == "table"]
    print(f"wrote {OUT.relative_to(ROOT)}")
    for section in blocks:
        kinds = ", ".join(c["type"] for c in section["blocks"])
        print(f"  section '{section['id']}' ({section['heading']}): {kinds}")
    for block in tables:
        print(f"  table: {len(block['rows'])} rows")
    print(f"  definitions: {len(definitions)}")


if __name__ == "__main__":
    main()
