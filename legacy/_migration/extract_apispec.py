"""Bootstrap firebolt-api-spec.json from the legacy page.

The method table is rendered client-side in legacy from a `const DATA=[...]`
array, and each method's detail panel is a generated <template>. Both are
derived from the same records, so this builds the JSON from that array rather
than scraping the generated markup: the result is far easier to hand-edit.

`cpp` and `js` already hold semantic "supported"/"unsupported" values, so the
PDF's colour coding survives as meaning rather than RGB.
"""
from __future__ import annotations

import json
import re
from typing import Any

from extract_spec import DATA, LEGACY, ROOT, actions_block, flat, hero_of, load

PDF = "Firebolt 8 API Spec.pdf"
TABLE_ID = "api-methods"

FIELD_LABELS = [("parameters", "Parameters"), ("returns", "Returns"), ("errors", "Specific errors")]
SUPPORT_LABELS = [("cpp", "C++"), ("js", "JS")]

# The workbook writes "not supported"; the stylesheet keys off `unsupported`.
SUPPORT_STATES = {
    "supported": "supported",
    "not supported": "unsupported",
    "unsupported": "unsupported",
}


def support_state(value: object) -> str:
    return SUPPORT_STATES.get(str(value or "").strip().lower(), "unknown")


def li_text(item) -> str:
    """Text of a list item, excluding any nested list."""
    parts = [item.text or ""]
    for child in item:
        if child.tag == "ul":
            parts.append(child.tail or "")
            continue
        parts.append(child.text_content() or "")
        parts.append(child.tail or "")
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def parse_list(node) -> list:
    items: list = []
    for item in node.xpath("./li"):
        nested = item.xpath("./ul")
        if nested:
            items.append({"text": li_text(item), "items": parse_list(nested[0])})
        else:
            items.append(li_text(item))
    return items


def field_value(cell):
    """A detail value is plain text or a (possibly nested) bullet list."""
    lists = cell.xpath("./ul")
    if lists:
        return {"type": "list", "items": parse_list(lists[0])}
    return re.sub(r"[ \t]+", " ", cell.text_content() or "").strip()


def trailing_blocks(template) -> list[dict[str, Any]]:
    """Content after the overview, e.g. the lifecycle transition list on api-10."""
    if template is None:
        return []
    blocks: list[dict[str, Any]] = []
    for entry in template.xpath(".//section"):
        for child in entry.iterchildren():
            if child.tag == "ul":
                blocks.append({
                    "type": "list",
                    "variant": child.get("class") or "api-detail-list",
                    "items": parse_list(child),
                })
    return blocks


def detail_fields(template) -> list[dict[str, Any]] | None:
    """Read the rendered field rows so PDF bullet structure is preserved."""
    if template is None:
        return None
    fields = []
    for row in template.xpath(".//div[contains(@class,'api-detail-row')]"):
        label = row.xpath("./dt")
        value = row.xpath("./dd")
        if label and value:
            fields.append({"label": flat(label[0]), "value": field_value(value[0])})
    return fields or None


def records(text: str) -> list[dict[str, Any]]:
    match = re.search(r"const DATA=(\[.*?\]);", text, re.S)
    if not match:
        raise SystemExit("no DATA array found in firebolt-api-spec.html")
    return json.loads(match.group(1))


def main() -> None:
    text = (LEGACY / "firebolt-api-spec.html").read_text(encoding="utf-8")
    doc, templates = load("firebolt-api-spec.html")
    rows_data = records(text)

    definitions: dict[str, Any] = {}
    rows = []
    for record in rows_data:
        ref = record["id"]
        template = templates.get(f"tmpl-{ref}")
        if template is None:
            template = templates.get(ref)
        fields = detail_fields(template) or [
            {"label": label, "value": record.get(key, "")}
            for key, label in FIELD_LABELS
        ]
        overview_nodes = template.xpath(".//p[contains(@class,'spec-entry-overview')]") if template is not None else []
        overview = flat(overview_nodes[0]) if overview_nodes else re.sub(r"\s+", " ", record.get("description", "")).strip()
        rows.append({
            "module": record.get("module", ""),
            "methods": record.get("method", ""),
            "version": {"type": "badge", "label": record.get("version", "")},
            "details": {
                "type": "actions",
                "plain": True,
                "items": [{"label": "View details", "ref": ref}],
            },
        })
        definitions[ref] = {
            "type": "apiMethod",
            "eyebrow": "Module",
            "module": record.get("module", ""),
            "method": record.get("method", ""),
            "version": record.get("version", ""),
            "support": [
                {"label": label, "state": support_state(record.get(key))}
                for key, label in SUPPORT_LABELS
            ],
            "fields": fields,
            "overview": overview,
            "trailing": trailing_blocks(template),
        }

    # The two reference modals (Types, Error values) keep their scraped content.
    reference_hosts = doc.xpath("//div[contains(@class,'api-reference')]")
    reference: dict[str, Any] = {"type": "reference", "title": "", "items": []}
    if reference_hosts:
        host = reference_hosts[0]
        title = host.xpath("./div[contains(@class,'api-reference-title')]")
        actions = host.xpath("./div[contains(@class,'reference-actions')]")
        reference["title"] = flat(title[0]) if title else ""
        if actions:
            reference["items"] = actions_block(actions[0], definitions, templates)["items"]

    select = doc.xpath("//select[@id='api-module']")
    options = [flat(option) for option in select[0].xpath("./option")] if select else []
    search = doc.xpath("//input[@id='api-search']")

    toolbar = {
        "type": "toolbar",
        "target": TABLE_ID,
        "classes": "northbound-toolbar",
        "search": {"placeholder": search[0].get("placeholder") if search else "Search"},
        "filters": [{
            "key": "module",
            "column": 0,
            "allLabel": options[0] if options else "All",
            "options": options[1:],
        }],
    }

    payload = {
        "schemaVersion": "1.0",
        "hero": hero_of(doc),
        "source": {"label": PDF, "href": f"assets/pdf/{PDF}"},
        "blocks": [{
            "type": "section",
            "classes": "api-spec-content",
            "blocks": [
                toolbar,
                reference,
                {
                    "type": "table",
                    "id": TABLE_ID,
                    "columns": [
                        {"key": "module", "label": "Module"},
                        {"key": "methods", "label": "Methods", "wrap": "preline"},
                        {"key": "version", "label": "API version"},
                        {"key": "details", "label": "Details"},
                    ],
                    "rows": rows,
                },
            ],
        }],
        "definitions": definitions,
    }
    payload["status"] = payload["hero"]["status"] or "Published"

    out = DATA / "firebolt-api-spec.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    print(f"  methods: {len(rows)}")
    print(f"  definitions: {len(definitions)} (incl. {len(definitions) - len(rows)} reference)")
    print(f"  module filter options: {len(options)}")


if __name__ == "__main__":
    main()
