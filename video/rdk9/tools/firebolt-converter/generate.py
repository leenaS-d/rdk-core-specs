"""Generate isolated Firebolt JSON/Markdown candidates from PDF extraction output.

This tool never edits the repository's curated assets/data or page files. It uses
those files as schema/content references and writes candidates under the output
folder for review before adoption.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from converters import CONVERTERS

ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS = {
    "api": ("firebolt-api-spec", "Firebolt 9 Core API Specification"),
    "intents": ("firebolt-intents", "Firebolt 9 Intents Specification"),
    "key-codes": ("firebolt-key-codes", "Firebolt 9 Key Codes Specification"),
    "app-actions":("firebolt-app-actions", "Firebolt 9 App Actions Specification"),
    "app-services":("firebolt-app-services", "Firebolt 9 App Services Specification"),
    "crypto":("firebolt-crypto","Firebolt 9 Crypto API Specifications.pdf")
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing input: {path}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_metadata(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "pdf": raw.get("source", ""),
        "sha256": raw.get("sha256", ""),
        "pageCount": len(raw.get("pages", [])),
        "extractedAt": raw.get("extractedAt", ""),
    }


def candidate_json(reference: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
    candidate = copy.deepcopy(reference)
    candidate["generator"] = {
        "name": "firebolt-converter",
        "mode": "reference-or-new-candidate",
        "source": source_metadata(raw),
        "note": "Review PDF-derived content before replacing the curated file.",
    }
    return candidate


def candidate_markdown(name: str, title: str, raw: dict[str, Any]) -> str:
    return "\n".join([
        "---",
        "layout: spec-document",
        f"title: {title} | RDK9",
        "nav: northbound",
        "footer: true",
        f"data: assets/data/{name}.json",
        "---",
        "",
    ])


def write_candidate(key: str, raw_dir: Path, output_dir: Path) -> None:
    name, title = DOCUMENTS[key]
    raw = read_json(raw_dir / f"{name}.json")
    document = CONVERTERS[name](name, title, raw)
    write_json(output_dir / "assets" / "data" / f"{name}.json", candidate_json(document, raw))
    page = candidate_markdown(name, title, raw)
    page_path = output_dir / f"{name}.md"
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(page, encoding="utf-8")
    print(f"generated {page_path}")


def run_one(key: str, raw_dir: Path | None = None, output_dir: Path | None = None) -> None:
    write_candidate(
        key,
        raw_dir or ROOT / "generated" / "all" / "raw",
        output_dir or ROOT,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", choices=[*DOCUMENTS, "all"])
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "generated" / "firebolt-pdf")
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    args = parser.parse_args()
    keys = list(DOCUMENTS) if args.document == "all" else [args.document]
    for key in keys:
        write_candidate(key, args.raw_dir, args.output_dir)
    print(f"output: {args.output_dir}")


if __name__ == "__main__":
    main()
