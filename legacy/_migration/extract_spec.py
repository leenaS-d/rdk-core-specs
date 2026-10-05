"""Convert legacy spec HTML into the shared block schema.

The legacy Firebolt pages are built from a small, consistent vocabulary of
markup (spec-intro, spec-entry, spec-table-wrap, spec-examples, allowed-actions),
so one converter serves all of them. Page-specific wiring lives in the
`extract_<page>.py` drivers.

This runs once per spec release; it is not part of the site build.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from lxml import html as lxml_html

ROOT = Path(__file__).resolve().parent.parent.parent
LEGACY = ROOT / "legacy" / "video" / "rdk8"
DATA = ROOT / "video" / "rdk8" / "assets" / "data"


def inline_text(node) -> str:
    """Flatten a node to text, keeping inline emphasis as Markdown."""
    parts: list[str] = [node.text or ""]
    for child in node:
        inner = inline_text(child)
        tag = child.tag
        if tag == "code":
            parts.append(f"`{inner}`")
        elif tag in ("strong", "b"):
            parts.append(f"**{inner}**")
        elif tag in ("em", "i"):
            parts.append(f"*{inner}*")
        elif tag == "a" and child.get("href"):
            parts.append(f"[{inner}]({child.get('href')})")
        else:
            parts.append(inner)
        parts.append(child.tail or "")
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def flat(node) -> str:
    return re.sub(r"\s+", " ", node.text_content() or "").strip()


def block_text(node) -> str:
    """Preserve line structure inside <pre>-style content."""
    for br in node.xpath(".//br"):
        br.tail = "\n" + (br.tail or "")
    raw = node.text_content() or ""
    lines = [re.sub(r"[ \t]+", " ", line).rstrip() for line in raw.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def slug(value: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", value).strip().lower()
    parts = re.split(r"[\s_-]+", cleaned)
    if not parts or not parts[0]:
        return "col"
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def classes_of(node) -> set[str]:
    return set((node.get("class") or "").split())


def resolve_template(ref: str, templates: dict):
    """Legacy triggers point at `#foo` while the template is `tmpl-foo`."""
    for candidate in (ref, f"tmpl-{ref}"):
        if candidate in templates:
            return templates[candidate]
    return None


def actions_block(node, definitions: dict[str, Any], templates: dict) -> dict[str, Any]:
    items = []
    decorated = False
    for child in node.xpath(".//a | .//span"):
        if "allowed-action" in classes_of(child):
            decorated = True
        href = child.get("href") or ""
        if href.startswith("#") or child.get("data-modal-target"):
            ref = href.lstrip("#") or child.get("data-modal-target") or ""
            template = resolve_template(ref, templates)
            if template is not None and ref not in definitions:
                definitions[ref] = None  # placeholder guards against recursion
                definitions[ref] = template_to_block(template, definitions, templates)
            items.append({"label": flat(child), "ref": ref})
        elif href:
            items.append({"label": flat(child), "href": href})
        else:
            items.append({"label": flat(child)})
    block: dict[str, Any] = {"type": "actions", "items": items}
    # Legacy uses a bare `pill` in some tables and `pill allowed-action` in
    # others; carry that distinction through rather than normalising it.
    if not decorated:
        block["plain"] = True
    return block


def table_block(table, definitions: dict[str, Any], templates: dict, wrapper=None) -> dict[str, Any]:
    headers = [flat(th) for th in table.xpath("./thead//th")]
    keys = [slug(h) or f"col{i}" for i, h in enumerate(headers)]
    # Disambiguate repeated header names so row keys stay unique.
    seen: dict[str, int] = {}
    for index, key in enumerate(keys):
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 1:
            keys[index] = f"{key}{seen[key]}"

    rows = []
    for tr in table.xpath("./tbody/tr"):
        cells = tr.xpath("./td")
        if not cells:
            continue
        record: dict[str, Any] = {}
        for key, cell in zip(keys, cells):
            record[key] = cell_value(cell, definitions, templates)
        rows.append(record)

    block: dict[str, Any] = {
        "type": "table",
        "columns": [{"key": key, "label": label} for key, label in zip(keys, headers)],
        "rows": rows,
    }
    wrapper_classes = classes_of(wrapper) if wrapper is not None else set()
    if "nested" in classes_of(table.getparent()):
        block["nested"] = True
    extra = wrapper_classes - {"spec-table-wrap"}
    if extra:
        block["classes"] = " ".join(sorted(extra))
    table_extra = classes_of(table) - {"spec-table"}
    if table_extra:
        block["tableClasses"] = " ".join(sorted(table_extra))
    return block


def cell_value(cell, definitions: dict[str, Any], templates: dict) -> Any:
    """A cell is plain text, an actions pill group, or a nested block."""
    disclosures = cell.xpath("./details[contains(@class,'spec-details')]")
    if disclosures:
        node = disclosures[0]
        summary = node.xpath("./summary")
        children = [c for c in node.iterchildren() if c.tag != "summary"]
        return {
            "type": "details",
            "summary": flat(summary[0]) if summary else "",
            "blocks": children_to_blocks(children, definitions, templates),
        }
    action_hosts = cell.xpath("./div[contains(@class,'allowed-actions')]")
    if action_hosts:
        return actions_block(action_hosts[0], definitions, templates)
    if cell.xpath(".//a[starts-with(@href,'#')]") and not cell.xpath(".//table"):
        return actions_block(cell, definitions, templates)
    nested = cell.xpath(".//table")
    if nested:
        inner = table_block(nested[0], definitions, templates)
        inner["nested"] = True
        return inner
    lists = cell.xpath("./ul")
    if lists:
        return {
            "type": "list",
            "items": [flat(li) for li in lists[0].xpath("./li")],
        }
    return block_text(cell)


def template_to_block(template, definitions: dict[str, Any], templates: dict) -> dict[str, Any]:
    entries = template.xpath(".//section[contains(@class,'spec-entry')]")
    node = entries[0] if entries else template
    return entry_block(node, definitions, templates)


def entry_block(node, definitions: dict[str, Any], templates: dict) -> dict[str, Any]:
    block: dict[str, Any] = {"type": "entry"}
    head = node.xpath("./div[contains(@class,'spec-entry-head')]")
    if head:
        eyebrow = head[0].xpath("./*[contains(@class,'spec-entry-eyebrow')]")
        heading = head[0].xpath("./h2|./h3")
        if eyebrow:
            block["eyebrow"] = flat(eyebrow[0])
        if heading:
            block["heading"] = flat(heading[0])
    overview = node.xpath("./p[contains(@class,'spec-entry-overview')]")
    if overview:
        block["overview"] = flat(overview[0])

    skip = set(head) | set(overview)
    children = [c for c in node.iterchildren() if c not in skip and isinstance(c.tag, str)]
    block["blocks"] = children_to_blocks(children, definitions, templates)
    return block


def children_to_blocks(nodes, definitions: dict[str, Any], templates: dict) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for node in nodes:
        tag = node.tag
        cls = classes_of(node)
        if tag in ("template", "script", "style", "h2"):
            continue
        if tag == "p":
            entry = {"type": "prose", "body": inline_text(node)}
            if node.get("class"):
                entry["variant"] = node.get("class")
            blocks.append(entry)
        elif tag in ("h3", "h4"):
            blocks.append({"type": "heading", "body": flat(node)})
        elif tag == "pre":
            entry = {"type": "code", "body": block_text(node)}
            if node.get("class"):
                entry["variant"] = node.get("class")
            blocks.append(entry)
        elif tag == "section" and "spec-entry" in cls:
            blocks.append(entry_block(node, definitions, templates))
        elif tag == "div" and "spec-examples" in cls:
            blocks.append({
                "type": "examples",
                "blocks": children_to_blocks(list(node.iterchildren()), definitions, templates),
            })
        elif tag == "div" and "allowed-actions" in cls:
            blocks.append(actions_block(node, definitions, templates))
        elif tag == "div" and "api-reference" in cls:
            title = node.xpath("./div[contains(@class,'api-reference-title')]")
            hosts = node.xpath("./div[contains(@class,'reference-actions')]")
            reference = {"type": "reference", "title": flat(title[0]) if title else ""}
            reference["items"] = actions_block(hosts[0], definitions, templates)["items"] if hosts else []
            blocks.append(reference)
        elif tag == "table":
            blocks.append(table_block(node, definitions, templates))
        elif tag == "div":
            tables = node.xpath("./table") or node.xpath("./div/table")
            if tables:
                wrapper = tables[0].getparent()
                block = table_block(tables[0], definitions, templates, wrapper)
                extra = cls - {"spec-table-wrap"}
                if extra:
                    block["classes"] = " ".join(sorted(extra))
                blocks.append(block)
            else:
                blocks.extend(children_to_blocks(list(node.iterchildren()), definitions, templates))
    return blocks


def hero_of(doc) -> dict[str, str]:
    section = doc.xpath("//section[contains(@class,'hero')]")[0]
    eyebrow = section.xpath(".//div[contains(@class,'eyebrow')]")
    description = section.xpath(".//p")
    status = section.xpath(".//span[contains(@class,'hero-status-badge')]")
    return {
        "eyebrow": flat(eyebrow[0]) if eyebrow else "",
        "title": flat(section.xpath(".//h1")[0]),
        "description": flat(description[0]) if description else "",
        "status": flat(status[0]).replace("Catalog status:", "").strip() if status else "",
    }


def load(page: str):
    doc = lxml_html.fromstring((LEGACY / page).read_text(encoding="utf-8"))
    templates = {node.get("id"): node for node in doc.xpath("//template") if node.get("id")}
    return doc, templates


def sections_to_blocks(doc, definitions: dict[str, Any], templates: dict) -> list[dict[str, Any]]:
    blocks = []
    for section in doc.xpath("//main//section[contains(@class,'spec-intro')]"):
        heading = section.xpath("./h2")
        children = children_to_blocks(list(section.iterchildren()), definitions, templates)
        block: dict[str, Any] = {"type": "section", "blocks": children}
        if section.get("id"):
            block["id"] = section.get("id")
        if heading:
            block["heading"] = flat(heading[0])
        extra = classes_of(section) - {"spec-intro"}
        if extra:
            block["classes"] = " ".join(sorted(extra))
        blocks.append(block)
    return blocks


def summarise(payload: dict[str, Any]) -> None:
    def count(blocks, kind):
        total = 0
        for block in blocks:
            if block.get("type") == kind:
                total += 1
            for key in ("blocks",):
                if isinstance(block.get(key), list):
                    total += count(block[key], kind)
            if block.get("type") == "table":
                for row in block.get("rows", []):
                    for value in row.values():
                        if isinstance(value, dict):
                            total += count([value], kind)
        return total

    blocks = payload["blocks"]
    for kind in ("section", "prose", "table", "entry", "code", "examples", "actions"):
        found = count(blocks, kind)
        if found:
            print(f"    {kind}: {found}")
    print(f"    definitions: {len(payload.get('definitions', {}))}")
