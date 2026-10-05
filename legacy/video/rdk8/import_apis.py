"""Generic RDK8 Excel-to-JSON importer."""
from __future__ import annotations

import argparse
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NAMESPACE = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "relationships": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def _column_index(coordinate: str) -> int:
    index = 0
    for character in coordinate:
        if not character.isalpha():
            break
        index = index * 26 + ord(character.upper()) - ord("A") + 1
    return index - 1


def read_excel_rows(workbook_path: Path) -> list[list[str]]:
    with zipfile.ZipFile(workbook_path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(node.text or "" for node in item.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")) for item in root.findall("main:si", NAMESPACE)]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in rels}
        sheet = workbook.find("main:sheets/main:sheet", NAMESPACE)
        if sheet is None:
            raise ValueError(f"{workbook_path.name} has no worksheets")
        rid = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target = targets[rid].lstrip("/")
        target = target if target.startswith("xl/") else "xl/" + target
        worksheet = ET.fromstring(archive.read(target))
        rows = []
        for row in worksheet.findall(".//main:sheetData/main:row", NAMESPACE):
            values = {}
            for cell in row.findall("main:c", NAMESPACE):
                value = cell.find("main:v", NAMESPACE)
                raw = "" if value is None else value.text or ""
                if cell.attrib.get("t") == "inlineStr":
                    raw = "".join(node.text or "" for node in cell.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
                elif cell.attrib.get("t") == "s" and raw:
                    raw = shared[int(raw)]
                values[_column_index(cell.attrib.get("r", "A1"))] = raw
            rows.append([values.get(index, "") for index in range(max(values, default=-1) + 1)])
    return rows


def convert_excel_to_json(workbook_path: Path, output_path: Path, field_mapping: dict[str, tuple[str, ...]], optional_fields: set[str] | None = None, collection_key: str = "apis") -> int:
    if not workbook_path.exists():
        return 0
    rows = read_excel_rows(workbook_path)
    if not rows:
        raise ValueError(f"{workbook_path.name} has no data rows")
    headers = [str(value).strip().lower() for value in rows[0]]
    optional_fields = optional_fields or set()
    positions = {}
    for field, aliases in field_mapping.items():
        position = next((headers.index(alias) for alias in aliases if alias in headers), None)
        if position is None and field not in optional_fields:
            raise ValueError(f"{workbook_path.name} is missing a column for {field}")
        positions[field] = position
    records = []
    for row in rows[1:]:
        record = {field: row[index].strip() if index is not None and index < len(row) and row[index] else "" for field, index in positions.items()}
        if any(record.values()):
            records.append(record)
    data = json.loads(output_path.read_text(encoding="utf-8"))
    data[collection_key] = records
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return len(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--map", dest="mappings", action="append", required=True)
    args = parser.parse_args()
    mapping = {value.split("=", 1)[0]: (value.split("=", 1)[1].lower(),) for value in args.mappings}
    print(f"Imported {convert_excel_to_json(args.workbook, args.output, mapping)} records")
