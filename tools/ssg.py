"""Markdown-driven static site generator for the RDK core specification sites.

A site is any directory containing `site.yaml`, a `_templates/` directory and
one or more `.md` content files. Each Markdown file carries YAML front matter
that selects a layout and supplies structured page furniture; the Markdown body
holds the prose. Output HTML is written next to the source `.md`, so the
published URLs match the source paths exactly.

Usage:
    python build.py video/rdk8
    python build.py video/rdk8 --check
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from lxml import html as lxml_html

MARKDOWN_EXTENSIONS = ["tables", "attr_list", "fenced_code", "sane_lists", "md_in_html"]


@dataclass
class Page:
    source: Path
    meta: dict[str, Any]
    body: str
    sections: list[dict[str, Any]] = field(default_factory=list)
    body_html: str = ""

    @property
    def output_name(self) -> str:
        return self.meta.get("permalink") or f"{self.source.stem}.html"


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    _, _, remainder = text.partition("---\n")
    raw_meta, _, body = remainder.partition("\n---")
    return yaml.safe_load(raw_meta) or {}, body.lstrip("\n")


def render_markdown(body: str) -> str:
    return markdown.Markdown(extensions=MARKDOWN_EXTENSIONS).convert(body)


def _inner_html(node) -> str:
    parts = [node.text or ""]
    parts += [lxml_html.tostring(child, encoding="unicode") for child in node]
    return "".join(parts).strip()


def _node_html(node) -> str:
    return lxml_html.tostring(node, encoding="unicode").strip()


def split_sections(body_html: str) -> list[dict[str, Any]]:
    """Split rendered Markdown into sections delimited by <h2> headings."""
    if not body_html.strip():
        return []
    root = lxml_html.fragment_fromstring(body_html, create_parent="div")
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for node in root:
        if node.tag == "h2":
            current = {"heading": _inner_html(node), "nodes": []}
            sections.append(current)
        elif current is not None:
            current["nodes"].append(node)
    for section in sections:
        section["html"] = "\n".join(_node_html(node) for node in section["nodes"])
    return sections


def extract_cards(nodes: list) -> list[dict[str, str]]:
    """Turn a run of <h3> + following block(s) into card dictionaries."""
    cards: list[dict[str, str]] = []
    for node in nodes:
        if node.tag == "h3":
            cards.append({"title": _inner_html(node), "body": ""})
        elif cards:
            text = _inner_html(node)
            cards[-1]["body"] = f"{cards[-1]['body']} {text}".strip()
    return cards


def count_records(site_dir: Path, reference: str) -> int:
    filename, _, key = reference.partition(":")
    payload = json.loads((site_dir / "assets" / "data" / filename).read_text(encoding="utf-8"))
    return len(payload.get(key, []))


def build_sections(site_dir: Path, page: Page) -> list[dict[str, Any]]:
    rendered = split_sections(page.body_html)
    declared = page.meta.get("sections") or []
    sections: list[dict[str, Any]] = []
    for index, source_section in enumerate(rendered):
        meta = dict(declared[index]) if index < len(declared) else {}
        section: dict[str, Any] = {
            "heading": source_section["heading"],
            "html": source_section["html"],
            **meta,
        }
        if section.get("layout") in {"cards", "metric-cards"}:
            cards = extract_cards(source_section["nodes"])
            declared_cards = meta.get("cards") or []
            for position, card in enumerate(cards):
                if position < len(declared_cards):
                    card.update(declared_cards[position])
                if card.get("metric_from"):
                    card["metric"] = sum(
                        count_records(site_dir, reference) for reference in card["metric_from"]
                    )
            section["cards"] = cards
        sections.append(section)
    return sections


COLUMN_KINDS = {"text", "link", "pill", "pill-variant"}


def build_table(site_dir: Path, spec: dict[str, Any]) -> dict[str, Any]:
    source = json.loads(
        (site_dir / "assets" / "data" / spec["data"]).read_text(encoding="utf-8")
    )
    records = source.get(spec.get("collection", "apis"), [])
    if spec.get("sort_field"):
        records = sorted(records, key=lambda item: str(item.get(spec["sort_field"], "")).casefold())

    columns = spec["columns"]
    rows: list[list[str]] = []
    for record in records:
        row = []
        for column in columns:
            value = record.get(column["field"], "")
            if isinstance(value, list):
                value = value[0] if value else ""
            row.append(value if value is not None else "")
        rows.append(row)

    if spec.get("sort_rows_by") is not None:
        rows.sort(key=lambda item: str(item[spec["sort_rows_by"]]).casefold())

    filters = []
    for declared in spec.get("filters", []) or []:
        index = declared["column"]
        filters.append(
            {
                **declared,
                "options": sorted({str(row[index]) for row in rows if str(row[index])}),
            }
        )

    payload = {
        "id": spec["id"],
        "columns": [
            {"kind": column.get("kind", "text"), "strip": bool(column.get("strip"))}
            for column in columns
        ],
        "rows": rows,
        "empty": spec.get("empty_message", "No records have been loaded."),
    }
    return {
        **spec,
        "columns": [column["label"] for column in columns],
        "filters": filters,
        "payload": json.dumps(payload, ensure_ascii=True),
        "status": spec.get("status", source.get("state", source.get("status", "Draft"))),
        "version": spec.get("version") or (source.get("version") if spec.get("show_version") else None),
    }


def build_site(site_dir: Path, check: bool = False) -> list[Path]:
    site = yaml.safe_load((site_dir / "site.yaml").read_text(encoding="utf-8"))
    env = Environment(
        loader=FileSystemLoader(site_dir / "_templates"),
        undefined=StrictUndefined,
        trim_blocks=False,
        lstrip_blocks=False,
    )

    written: list[Path] = []
    for source in sorted(site_dir.glob("*.md")):
        meta, body = parse_front_matter(source.read_text(encoding="utf-8"))
        if not meta:
            continue
        page = Page(source=source, meta=meta, body=body)
        page.body_html = render_markdown(body)

        context_page: dict[str, Any] = {
            "title": meta.get("title", site["title"]),
            "nav_key": meta.get("nav_key"),
            "hero": meta.get("hero") or {},
            "note": meta.get("note"),
            "footer": meta.get("footer", False),
            "body_html": "",
            "sections": [],
        }
        layout = meta.get("layout", "home")
        if layout == "home":
            context_page["sections"] = build_sections(site_dir, page)
        else:
            context_page["body_html"] = page.body_html
        if meta.get("table"):
            context_page["table"] = build_table(site_dir, meta["table"])

        template = env.get_template(f"layouts/{layout}.html")
        output = site_dir / page.output_name
        html = template.render(site=site, page=context_page)
        if not check:
            output.write_text(html, encoding="utf-8")
        written.append(output)
    return written


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    site_dir = Path(argv[0]).resolve()
    check = "--check" in argv
    written = build_site(site_dir, check=check)
    verb = "would write" if check else "wrote"
    for path in written:
        print(f"{verb} {path.relative_to(Path.cwd())}")
    print(f"{len(written)} page(s)")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
