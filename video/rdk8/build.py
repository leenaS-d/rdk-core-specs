"""Build the RDK8 Video specification site from Markdown + JSON.

Content lives in the sibling `.md` files (YAML front matter + Markdown body),
shared chrome in `_templates/`, styling in `assets/css/`, and tabular data in
`assets/data/`. Output is plain `.html` written next to the sources so GitHub
Pages can serve it directly with no CI step.

Usage:
    python build.py            # build every page
    python build.py --check    # build, then verify expected pages exist
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import markdown
import yaml
from jinja2 import ChainableUndefined, Environment, FileSystemLoader
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "_templates"
DATA = ROOT / "assets" / "data"

EXPECTED_PAGES = [
    "index.html",
    "component-catalog.html",
    "northbound-api-spec.html",
    "southbound-api-spec.html",
]

MD = markdown.Markdown(extensions=["tables", "attr_list", "sane_lists"])


def render_markdown(text: str) -> str:
    MD.reset()
    return MD.convert(text.strip()) if text.strip() else ""


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    _, _, remainder = text.partition("---\n")
    raw, _, body = remainder.partition("\n---")
    return yaml.safe_load(raw) or {}, body.lstrip("\n")


def parse_sections(body: str) -> tuple[list[str], list[dict[str, Any]]]:
    """Split a Markdown body into leading paragraphs and `##` sections.

    Within a section, `###` headings become cards; text before the first `###`
    becomes the section's prose.
    """
    chunks = re.split(r"^## ", body, flags=re.M)
    intro = [p.strip() for p in chunks[0].strip().split("\n\n") if p.strip()]

    sections: list[dict[str, Any]] = []
    for chunk in chunks[1:]:
        heading, _, rest = chunk.partition("\n")
        card_parts = re.split(r"^### ", rest, flags=re.M)
        prose = card_parts[0].strip()
        cards = []
        for card in card_parts[1:]:
            card_title, _, card_body = card.partition("\n")
            cards.append({"title": card_title.strip(), "body": card_body.strip()})
        sections.append({"heading": heading.strip(), "prose": prose, "cards": cards})
    return intro, sections


def load_json(name: str) -> dict[str, Any]:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def source_url(item: dict[str, Any]) -> str:
    url = item.get("url") or ""
    return url[0] if isinstance(url, list) else url


def catalog_rows() -> list[list[str]]:
    """Merge core and non-core components, tagging each with its type."""
    core = load_json("assets/data/components.json")
    non_core = load_json("assets/data/rdk8-non-core-components.json")
    core_names = {
        str(item.get("name") or "").casefold()
        for item in core.get("components", [])
        if item.get("name")
    }
    rows = []
    for item in [*core.get("components", []), *non_core.get("components", [])]:
        name = str(item.get("name") or "")
        category = item.get("category", "")
        rows.append([
            name,
            "video" if str(category).casefold() == "video" else category,
            item.get("layer", ""),
            "core" if name.casefold() in core_names else "non-core",
            item.get("releaseTag") or "",
            source_url(item),
        ])
    rows.sort(key=lambda row: str(row[0]).casefold())
    return rows


def table_rows(config: dict[str, Any]) -> tuple[list[list[str]], dict[str, Any]]:
    if config.get("source") == "catalog":
        core = load_json("assets/data/components.json")
        return catalog_rows(), {"status": core.get("status", "Published"), "version": core.get("version", "")}

    data = load_json(config["source"])
    records = data.get("apis", [])
    if config.get("sort_field"):
        records = sorted(records, key=lambda item: str(item.get(config["sort_field"], "")).casefold())
    fields = config["fields"]
    rows = [[str(item.get(field, "") or "") for field in fields] for item in records]
    if config.get("strip_release_path") and config.get("link_column") is not None:
        index = config["link_column"]
        for row in rows:
            row[index] = re.sub(r"/releases/tag/[^/]+/?$", "", row[index])
    return rows, {"status": data.get("status", "Draft"), "version": data.get("version", "")}


def metric_value(token: str) -> int:
    kind = token.split(":", 1)[1]
    if kind == "components":
        return len(catalog_rows())
    if kind == "northbound":
        return len(load_json("assets/data/northbound-apis.json").get("apis", []))
    if kind == "southbound":
        return len(load_json("assets/data/southbound-apis.json").get("apis", []))
    raise ValueError(f"unknown metric {token!r}")


BLOCK_TYPES = {
    "section", "prose", "heading", "table", "fields", "entry", "code", "examples",
    "actions", "list", "details", "reference", "badge", "toolbar", "apiMethod",
}


def render_inline(text: str) -> Markup:
    """Render the inline Markdown allowed inside prose bodies."""
    if not text:
        return Markup("")
    MD.reset()
    html = MD.convert(str(text)).strip()
    if html.startswith("<p>") and html.endswith("</p>"):
        html = html[3:-4]
    return Markup(html)


def walk_blocks(blocks: list[dict[str, Any]], path: str, definitions: set[str], problems: list[str]) -> None:
    """Validate block types, column/row agreement and definition references."""
    for index, block in enumerate(blocks):
        where = f"{path}[{index}]"
        kind = block.get("type")
        if kind not in BLOCK_TYPES:
            problems.append(f"{where}: unknown block type {kind!r}")
            continue

        if kind == "actions":
            for item in block.get("items", []):
                if item.get("ref") and item["ref"] not in definitions:
                    problems.append(f"{where}: ref {item['ref']!r} has no matching definition")

        if kind == "table":
            known = {column["key"] for column in block.get("columns", [])}
            for row_index, row in enumerate(block.get("rows", [])):
                unknown = set(row) - known
                if unknown:
                    problems.append(f"{where}: row {row_index} has keys not in columns: {sorted(unknown)}")
                for value in row.values():
                    if isinstance(value, dict):
                        walk_blocks([value], f"{where}.cell", definitions, problems)

        for key in ("blocks",):
            if isinstance(block.get(key), list):
                walk_blocks(block[key], f"{where}.{key}", definitions, problems)


def validate_doc(doc: dict[str, Any], label: str) -> list[str]:
    problems: list[str] = []
    definitions = set(doc.get("definitions", {}))
    walk_blocks(doc.get("blocks", []), f"{label}.blocks", definitions, problems)
    for key, definition in doc.get("definitions", {}).items():
        walk_blocks([definition], f"{label}.definitions[{key}]", definitions, problems)
    return problems


def build_page(env: Environment, site: dict[str, Any], path: Path) -> str:
    meta, body = split_front_matter(path.read_text(encoding="utf-8"))
    intro, sections = parse_sections(body)

    hero = meta.setdefault("hero", {})
    hero["description"] = intro
    # Every legacy page rendered the compact hero; keep that the default.
    hero.setdefault("compact", True)

    if meta.get("data"):
        doc = load_json(meta["data"])
        problems = validate_doc(doc, path.stem)
        if problems:
            raise SystemExit(f"{path.name} data invalid:\n  " + "\n  ".join(problems))
        meta["doc"] = doc
        for field in ("eyebrow", "title", "status"):
            if doc.get("hero", {}).get(field):
                hero.setdefault(field, doc["hero"][field])
        if not hero["description"] and doc.get("hero", {}).get("description"):
            hero["description"] = [doc["hero"]["description"]]

    if meta.get("layout") == "home":
        configured = meta.get("sections", [])
        merged = []
        for index, section in enumerate(sections):
            config = dict(configured[index]) if index < len(configured) else {}
            config["heading"] = section["heading"]
            if config.get("layout") == "prose":
                css = "lede" if config.pop("lede", False) else ""
                html = render_markdown(section["prose"])
                if css:
                    html = html.replace("<p>", f'<p class="{css}">', 1)
                config["html"] = Markup(html)
            else:
                cards = []
                for card_index, card in enumerate(section["cards"]):
                    entry = dict(config.get("cards", [])[card_index]) if card_index < len(config.get("cards", [])) else {}
                    entry["title"] = card["title"]
                    entry["body"] = card["body"]
                    if isinstance(entry.get("metric"), str) and entry["metric"].startswith("count:"):
                        entry["metric"] = metric_value(entry["metric"])
                    cards.append(entry)
                config["cards"] = cards
            merged.append(config)
        meta["sections"] = merged
    else:
        meta["body_html"] = Markup("")

    if "table" in meta:
        rows, state = table_rows(meta["table"])
        meta["table"].setdefault("status", state["status"])
        if meta["table"].get("show_version") is False:
            meta["table"]["version"] = ""
        else:
            meta["table"].setdefault("version", state["version"])
        config = meta["table"]
        link_column = config.get("link_column")
        pill_columns = set(config.get("pill_columns", []))
        variant_columns = set(config.get("pill_variant_columns", []))
        columns = []
        for index in range(len(config["columns"])):
            if index == link_column:
                columns.append({"kind": "link", "strip": False})
            elif index in variant_columns:
                columns.append({"kind": "pill-variant"})
            elif index in pill_columns:
                columns.append({"kind": "pill"})
            else:
                columns.append({"kind": "text"})
        payload = json.dumps(
            {
                "id": config["id"],
                "columns": columns,
                "rows": rows,
                "empty": config.get("empty_message", "No matching records."),
            },
            ensure_ascii=True,
        )
        # Escape `<` so the payload can never terminate the enclosing <script>.
        meta["table"]["payload"] = Markup(payload.replace("<", "\\u003c"))
        for filter_config in meta["table"].get("filters", []):
            column = filter_config["column"]
            filter_config["options"] = sorted({str(row[column]) for row in rows if str(row[column])})

    template = env.get_template(f"layouts/{meta['layout']}.html")
    return template.render(site=site, page=meta)


def build() -> None:
    site = yaml.safe_load((ROOT / "site.yaml").read_text(encoding="utf-8"))
    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        undefined=ChainableUndefined,
        trim_blocks=True,
        lstrip_blocks=False,
        autoescape=True,
    )
    env.filters["inline"] = render_inline
    for path in sorted(ROOT.glob("*.md")):
        meta, _ = split_front_matter(path.read_text(encoding="utf-8"))
        # A Markdown file without a layout is documentation (e.g. README), not a page.
        if not meta.get("layout"):
            print(f"skipped {path.name} (no layout)")
            continue
        output = ROOT / f"{path.stem}.html"
        output.write_text(build_page(env, site, path), encoding="utf-8")
        print(f"built {output.name}")


# Hand-edited JSON is now the source of truth for most datasets, so validate
# the fields each page renders rather than letting blanks reach the page.
DATA_RULES = [
    ("assets/data/components.json", "components", ["name", "category", "layer"]),
    ("assets/data/rdk8-non-core-components.json", "components", ["name", "category", "layer"]),
    ("assets/data/northbound-apis.json", "apis", ["component", "name", "releaseTag"]),
    ("assets/data/southbound-apis.json", "apis", ["halInterface", "releaseTag", "source"]),
]


def validate_data() -> list[str]:
    problems: list[str] = []
    for name, collection, required in DATA_RULES:
        path = ROOT / name
        if not path.exists():
            problems.append(f"{name}: missing")
            continue
        data = load_json(name)
        records = data.get(collection)
        if not isinstance(records, list):
            problems.append(f"{name}: expected a '{collection}' array")
            continue
        for index, record in enumerate(records):
            for field in required:
                if not str(record.get(field, "") or "").strip():
                    label = record.get("name") or record.get("halInterface") or f"index {index}"
                    problems.append(f"{name}: '{label}' is missing {field}")
        labels = [str(r.get("name") or r.get("halInterface") or "").casefold() for r in records]
        duplicates = {label for label in labels if label and labels.count(label) > 1}
        for label in sorted(duplicates):
            problems.append(f"{name}: duplicate entry '{label}'")
    return problems


def check() -> None:
    missing = [name for name in EXPECTED_PAGES if not (ROOT / name).exists()]
    if missing:
        raise SystemExit("missing generated pages: " + ", ".join(missing))
    problems = validate_data()
    if problems:
        raise SystemExit("data validation failed:\n  " + "\n  ".join(problems))
    print(f"check passed: {len(catalog_rows())} components, data valid")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    build()
    if args.check:
        check()
