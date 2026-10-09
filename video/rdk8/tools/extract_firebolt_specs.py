"""Extract the Firebolt PDFs into reviewable Markdown and raw JSON.

The output is intentionally separate from assets/data. PDF extraction cannot
reliably infer the site's nested block semantics, so the generated candidates
can be reviewed and merged without overwriting manual corrections.

Usage:
    py tools/extract_firebolt_specs.py all
    py tools/extract_firebolt_specs.py api
    py tools/extract_firebolt_specs.py intents --output-dir generated/firebolt
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import pdfplumber
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: install it with `py -m pip install pdfplumber`."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
PDFS = {
    "api": ("Firebolt 8 API Spec.pdf", "firebolt-api-spec"),
    "intents": ("Firebolt 8 Intent Spec.pdf", "firebolt-intents"),
    "key-codes": ("Firebolt 8 key code Spec.pdf", "firebolt-key-codes"),
}


def pdf_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_document(path: Path, key: str) -> dict[str, Any]:
    pages: list[dict[str, Any]] = []
    with pdfplumber.open(path) as pdf:
        for number, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text(layout=True) or "").strip()
            tables = [table for table in page.extract_tables() if table]
            pages.append({"page": number, "text": text, "tables": tables})

    return {
        "schemaVersion": "pdf-extract-1.0",
        "document": key,
        "source": path.name,
        "sha256": pdf_sha256(path),
        "extractedAt": datetime.now(timezone.utc).isoformat(),
        "pages": pages,
    }


def markdown_for(document: dict[str, Any]) -> str:
    lines = [
        f"# Extracted {document['document']}",
        "",
        f"Source: `{document['source']}`",
        f"SHA-256: `{document['sha256']}`",
        "",
        "> This file is generated from the PDF for review. It is not a replacement for the curated JSON.",
        "",
    ]
    for page in document["pages"]:
        lines.extend([f"## Page {page['page']}", "", "```text", page["text"], "```", ""])
        for index, table in enumerate(page["tables"], start=1):
            lines.extend([f"### Table {index}", "", "```text"])
            lines.extend(" | ".join("" if cell is None else str(cell) for cell in row) for row in table)
            lines.extend(["```", ""])
    return "\n".join(lines)


def write_document(document: dict[str, Any], output_dir: Path) -> None:
    stem = document["document"]
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{stem}.json").write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / f"{stem}.md").write_text(markdown_for(document), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", choices=[*PDFS, "all"])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "generated" / "firebolt-pdf",
        help="Directory for generated review files.",
    )
    args = parser.parse_args()
    keys = list(PDFS) if args.document == "all" else [args.document]
    manifest: list[dict[str, str]] = []
    for key in keys:
        filename, stem = PDFS[key]
        path = ROOT / "assets" / "pdf" / filename
        if not path.exists():
            raise SystemExit(f"PDF not found: {path}")
        document = extract_document(path, stem)
        write_document(document, args.output_dir)
        manifest.append({"document": stem, "source": filename, "sha256": document["sha256"]})
        print(f"extracted {filename} -> {args.output_dir}")
    (args.output_dir / "manifest.json").write_text(
        json.dumps({"schemaVersion": "pdf-extract-manifest-1.0", "documents": manifest}, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()