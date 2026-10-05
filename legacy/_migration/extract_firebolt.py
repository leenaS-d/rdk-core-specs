"""Bootstrap the three remaining Firebolt pages into the shared block schema.

    python extract_firebolt.py            # all three
    python extract_firebolt.py intents    # one page
"""
from __future__ import annotations

import json
import sys

from extract_spec import DATA, ROOT, hero_of, load, sections_to_blocks, summarise

PAGES = {
    "intents": ("firebolt-intents.html", "Firebolt 8 Intent Spec.pdf"),
    "json-rpc": ("firebolt-json-rpc.html", "Firebolt 8 JSON-RPC spec.pdf"),
    "api-spec": ("firebolt-api-spec.html", "Firebolt 8 API Spec.pdf"),
}


def build(name: str) -> None:
    page, pdf = PAGES[name]
    doc, templates = load(page)
    definitions: dict = {}
    blocks = sections_to_blocks(doc, definitions, templates)

    payload = {
        "schemaVersion": "1.0",
        "hero": hero_of(doc),
        "source": {"label": pdf, "href": f"assets/pdf/{pdf}"},
        "blocks": blocks,
        "definitions": definitions,
    }
    payload["status"] = payload["hero"]["status"] or "Published"

    out = DATA / f"firebolt-{name}.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  wrote {out.relative_to(ROOT)}")
    summarise(payload)


def main() -> None:
    names = sys.argv[1:] or list(PAGES)
    for name in names:
        print(f"[{name}]")
        build(name)


if __name__ == "__main__":
    main()
