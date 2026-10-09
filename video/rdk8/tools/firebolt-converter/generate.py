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

ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS = {
    "api": ("firebolt-api-spec", "Firebolt 8 Core API Specification"),
    "intents": ("firebolt-intents", "Firebolt 8 Intents Specification"),
    "key-codes": ("firebolt-key-codes", "Firebolt 8 Key Codes Specification"),
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
        "mode": "reference-preserving-candidate",
        "source": source_metadata(raw),
        "note": "Review PDF-derived content before replacing the curated file.",
    }
    return candidate


def candidate_markdown(name: str, title: str, raw: dict[str, Any]) -> str:
    lines = [
        "---",
        "layout: spec-document",
        f"title: {title} | RDK8",
        "nav: northbound",
        "footer: true",
        f"data: assets/data/{name}.json",
        "---",
        "",
        f"# PDF extraction candidate: {raw.get('source', name)}",
        "",
        "> This is an isolated review artifact. The curated page Markdown was not modified.",
        "",
    ]
    for page in raw.get("pages", []):
        lines.extend([f"## Extracted page {page.get('page', '?')}", "", "```text", page.get("text", ""), "```", ""])
    return "\n".join(lines)


def write_candidate(key: str, raw_dir: Path, reference_dir: Path, output_dir: Path) -> None:
    name, title = DOCUMENTS[key]
    raw = read_json(raw_dir / f"{name}.json")
    reference = read_json(reference_dir / f"{name}.json")
    write_json(output_dir / "assets" / "data" / f"{name}.json", candidate_json(reference, raw))
    page = candidate_markdown(name, title, raw)
    page_path = output_dir / f"{name}.md"
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(page, encoding="utf-8")
    print(f"generated {page_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", choices=[*DOCUMENTS, "all"])
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "generated" / "firebolt-pdf")
    parser.add_argument("--reference-dir", type=Path, default=ROOT / "assets" / "data")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "generated" / "firebolt-converted")
    args = parser.parse_args()
    keys = list(DOCUMENTS) if args.document == "all" else [args.document]
    for key in keys:
        write_candidate(key, args.raw_dir, args.reference_dir, args.output_dir)
    print(f"output: {args.output_dir}")


if __name__ == "__main__":
    main()
