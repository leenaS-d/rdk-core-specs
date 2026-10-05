"""Refresh assets/data/*.json from the spreadsheets in assets/xlsx/.

Run this whenever a workbook is updated, then run build.py:

    python refresh_data.py            # refresh every dataset
    python refresh_data.py --only northbound
    python refresh_data.py --dry-run  # report changes without writing

Column mappings live in data-sources.yaml. Reading .xlsx uses only the standard
library, so no spreadsheet dependency is required.

Editorial fields in the JSON (`status`, `version`, `schemaVersion`) are
preserved; only the records array is replaced.
"""
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "data-sources.yaml"

SHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NAMESPACE = {"main": SHEET_NS, "relationships": REL_NS}


def column_index(coordinate: str) -> int:
    index = 0
    for character in coordinate:
        if not character.isalpha():
            break
        index = index * 26 + ord(character.upper()) - ord("A") + 1
    return index - 1


def read_rows(workbook: Path) -> list[list[str]]:
    """Read the first worksheet of an .xlsx as a list of string rows."""
    with zipfile.ZipFile(workbook) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = [
                "".join(node.text or "" for node in item.iter(f"{{{SHEET_NS}}}t"))
                for item in root.findall("main:si", NAMESPACE)
            ]

        book = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in rels}
        sheet = book.find("main:sheets/main:sheet", NAMESPACE)
        if sheet is None:
            raise ValueError(f"{workbook.name} has no worksheets")

        target = targets[sheet.attrib[f"{{{REL_NS}}}id"]].lstrip("/")
        target = target if target.startswith("xl/") else "xl/" + target
        worksheet = ET.fromstring(archive.read(target))

        rows: list[list[str]] = []
        for row in worksheet.findall(".//main:sheetData/main:row", NAMESPACE):
            values: dict[int, str] = {}
            for cell in row.findall("main:c", NAMESPACE):
                node = cell.find("main:v", NAMESPACE)
                raw = "" if node is None else node.text or ""
                if cell.attrib.get("t") == "inlineStr":
                    raw = "".join(n.text or "" for n in cell.iter(f"{{{SHEET_NS}}}t"))
                elif cell.attrib.get("t") == "s" and raw:
                    raw = shared[int(raw)]
                values[column_index(cell.attrib.get("r", "A1"))] = raw
            rows.append([values.get(i, "") for i in range(max(values, default=-1) + 1)])
    return rows


def extract(dataset: dict[str, Any], rows: list[list[str]]) -> list[dict[str, str]]:
    headers = [str(value).strip().lower() for value in rows[0]]
    optional = set(dataset.get("optional", []))

    positions: dict[str, int | None] = {}
    for field, aliases in dataset["columns"].items():
        position = next((headers.index(a) for a in aliases if a in headers), None)
        if position is None and field not in optional:
            raise SystemExit(
                f"[{dataset['name']}] no column found for '{field}'. "
                f"Looked for {aliases}; sheet has {headers}. "
                f"Add the new header to data-sources.yaml."
            )
        positions[field] = position

    defaults = dataset.get("defaults", {})
    records = []
    for row in rows[1:]:
        record = {}
        for field, index in positions.items():
            value = row[index].strip() if index is not None and index < len(row) and row[index] else ""
            rule = defaults.get(field)
            if rule and (not value or value in rule.get("when_blank_or", [])):
                value = rule["value"]
            record[field] = value
        if any(record.values()):
            records.append(record)
    return records


def resolve_workbook(dataset: dict[str, Any]) -> Path | None:
    """Return the first configured workbook that exists."""
    entry = dataset["workbook"]
    candidates = entry if isinstance(entry, list) else [entry]
    return next((ROOT / name for name in candidates if (ROOT / name).exists()), None)


def refresh(dataset: dict[str, Any], dry_run: bool) -> str:
    workbook = resolve_workbook(dataset)
    output = ROOT / dataset["output"]
    if workbook is None:
        return f"[{dataset['name']}] SKIPPED - no workbook found for {dataset['workbook']}"

    rows = read_rows(workbook)
    if not rows:
        raise SystemExit(f"[{dataset['name']}] {workbook.name} has no rows")
    records = extract(dataset, rows)

    existing = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
    previous = len(existing.get(dataset["collection"], []))
    existing[dataset["collection"]] = records
    payload = json.dumps(existing, indent=2, ensure_ascii=True) + "\n"

    changed = not output.exists() or output.read_text(encoding="utf-8") != payload
    if not dry_run and changed:
        output.write_text(payload, encoding="utf-8")

    state = "unchanged" if not changed else ("would update" if dry_run else "updated")
    return f"[{dataset['name']}] {state}: {previous} -> {len(records)} records  (from {workbook.name})"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="refresh a single dataset by name")
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    args = parser.parse_args()

    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    datasets = config["datasets"]
    if args.only:
        datasets = [d for d in datasets if d["name"] == args.only]
        if not datasets:
            raise SystemExit(f"no dataset named {args.only!r} in data-sources.yaml")

    for dataset in datasets:
        print(refresh(dataset, args.dry_run))


if __name__ == "__main__":
    main()
