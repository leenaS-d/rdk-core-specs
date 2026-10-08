"""Page-specific raw-PDF to site-schema converters for RDK9."""
from __future__ import annotations

import copy
import re
from io import BytesIO
from pathlib import Path
from typing import Any, Callable

import pdfplumber
from PIL import Image


Converter = Callable[[str, str, dict[str, Any]], dict[str, Any]]
ROOT = Path(__file__).resolve().parents[2]
SUPPORT_COLUMN_SPLIT_X = 390
PDF_AMBER_SOURCE = (1.0, 0.92549, 0.92157)


def _support_icon_state(page: Any, image: dict[str, Any]) -> str:
    try:
        with Image.open(BytesIO(image["stream"].get_data())).convert("RGB") as pixels:
            width, height = pixels.size
            center_x, center_y = width // 2, height // 2
            samples = [
                pixels.getpixel((center_x + delta_x, center_y + delta_y))
                for delta_x in range(-2, 3)
                for delta_y in range(-2, 3)
                if 0 <= center_x + delta_x < width and 0 <= center_y + delta_y < height
            ]
    except OSError:
        try:
            pixels = page.crop((image["x0"], image["top"], image["x1"], image["bottom"])).to_image(resolution=144).original.convert("RGB")
            width, height = pixels.size
            center_x, center_y = width // 2, height // 2
            samples = [
                pixels.getpixel((center_x + delta_x, center_y + delta_y))
                for delta_x in range(-4, 5)
                for delta_y in range(-4, 5)
                if 0 <= center_x + delta_x < width and 0 <= center_y + delta_y < height
            ]
        except (OSError, ValueError):
            return ""
    red = sum(sample[0] for sample in samples) / len(samples)
    green = sum(sample[1] for sample in samples) / len(samples)
    blue = sum(sample[2] for sample in samples) / len(samples)
    return "supported" if green >= red and green >= blue else "unsupported"


def _api_support_states(raw: dict[str, Any]) -> dict[int, tuple[str, str]]:
    pdf_path = ROOT / "assets" / "pdf" / str(raw.get("source", ""))
    if not pdf_path.exists():
        return {}
    states: dict[int, tuple[str, str]] = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            marks = [
                (
                    image["top"],
                    image["bottom"],
                    "cpp17" if image["x0"] < SUPPORT_COLUMN_SPLIT_X else "js",
                    _support_icon_state(page, image),
                )
                for image in page.images
            ]
            for table in page.find_tables():
                rows = table.extract()
                if not rows or len(rows[0]) != 11:
                    continue
                for row_index, row in enumerate(rows):
                    identifier = _clean(row[0])
                    if not identifier.isdigit():
                        continue
                    top, _, _, bottom = table.rows[row_index].bbox
                    cpp17 = js = ""
                    for mark_top, mark_bottom, column, state in marks:
                        if not state or max(0.0, min(mark_bottom, bottom) - max(mark_top, top)) <= 0:
                            continue
                        if column == "cpp17":
                            cpp17 = state
                        else:
                            js = state
                    states[int(identifier)] = (cpp17 or "unknown", js or "unknown")
    return states

def _support_state(value: str) -> str:
    value = _clean(value).casefold()
    if value == "yes":
        return "supported" # renders as tick
    if value == "no":
        return "not-supported" # renders as cross
    return "unknown"

def _crypto_support_states(rows: list[list[Any]]) -> dict[int, tuple[str, str]]:
    """C++ / JS support comes from the Yes/No text columns of the (already merged) method rows."""
    return {
        int(_clean(row[0])): (_support_state(row[CRYPTO_CPP_COLUMN]), _support_state(row[CRYPTO_JS_COLUMN]))
        for row in rows
        if _clean(row[0]).isdigit()
    }

def _pdf_row_is_amber(page: Any, bbox: tuple[float, float, float, float]) -> bool:
    top, bottom = bbox[1], bbox[3]
    best_color = None
    best_overlap = 0.0
    for rect in page.rects:
        color = tuple(rect.get("non_stroking_color") or ())
        overlap = max(0.0, min(rect["bottom"], bottom) - max(rect["top"], top))
        if overlap > best_overlap:
            best_color = color
            best_overlap = overlap
    return best_color == PDF_AMBER_SOURCE


def _api_amber_method_ids(raw: dict[str, Any]) -> set[int]:
    pdf_path = ROOT / "assets" / "pdf" / str(raw.get("source", ""))
    if not pdf_path.exists():
        return set()
    method_ids: set[int] = set()
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.find_tables():
                rows = table.extract()
                if not rows or len(rows[0]) != 11:
                    continue
                for index, row in enumerate(rows):
                    identifier = _clean(row[0])
                    if identifier.isdigit() and _pdf_row_is_amber(page, table.rows[index].bbox):
                        method_ids.add(int(identifier))
    return method_ids


def _app_service_amber_methods(raw: dict[str, Any]) -> set[str]:
    pdf_path = ROOT / "assets" / "pdf" / str(raw.get("source", ""))
    if not pdf_path.exists():
        return set()
    methods: set[str] = set()
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.find_tables():
                rows = table.extract()
                if not rows:
                    continue
                headers = [_clean(value).casefold() for value in rows[0]]
                if "method" not in headers:
                    continue
                method_index = headers.index("method")
                for index, row in enumerate(rows[1:], start=1):
                    if method_index < len(row) and _clean(row[method_index]) and _pdf_row_is_amber(page, table.rows[index].bbox):
                        methods.add(_method_text(row[method_index]))
    return methods


def _api_error_red_row_ids(raw: dict[str, Any]) -> set[int]:
    pdf_path = ROOT / "assets" / "pdf" / str(raw.get("source", ""))
    if not pdf_path.exists():
        return set()
    row_ids: set[int] = set()
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.find_tables():
                rows = table.extract()
                if not rows or max(map(len, rows)) != 7:
                    continue
                for index, row in enumerate(rows):
                    identifier = _clean(row[0])
                    if identifier.isdigit() and _pdf_row_is_amber(page, table.rows[index].bbox):
                        row_ids.add(int(identifier))
    return row_ids


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def _lines(value: Any) -> list[str]:
    return [" ".join(part.split()) for part in str(value or "").splitlines() if part.strip()]


def _value(value: Any, nested: bool = True) -> Any:
    source_lines = _lines(value)
    if not source_lines:
        return ""
    if nested and source_lines[0].casefold() == "enum":
        enum_items: list[str] = []
        for line in source_lines[1:]:
            if re.match(r"^[a-z][\w-]*\s+-\s", line):
                enum_items.append(line)
            elif enum_items and " - " in enum_items[-1]:
                enum_items[-1] += " " + line
            else:
                enum_items.append(line)
        enum_items = [item.replace(" /", "/") for item in enum_items]
        return {"type": "list", "items": [{"text": "enum", "items": enum_items}]}
    lines: list[str] = []
    enum_mode = False
    for line in source_lines:
        if enum_mode:
            if re.match(r"^[a-z][\w-]*\s+-\s", line):
                lines.append(line)
                enum_mode = False
            else:
                lines.append(line)
            continue
        if not lines:
            lines.append(line)
        elif lines[-1].count('"') % 2:
            lines[-1] += ("" if line.startswith('"') else " ") + line
        elif line.startswith("/"):
            lines[-1] += line
        elif lines[-1].endswith("-"):
            lines[-1] += " " + line
        elif line.startswith("- "):
            lines[-1] += " " + line
        elif line == "-":
            lines[-1] += " -"
        elif line.startswith("|"):
            lines[-1] += " " + line
        elif lines[-1].count("(") > lines[-1].count(")"):
            lines[-1] += " " + line
        elif line.endswith(" -") and " " not in lines[-1] and lines[-1][:1].islower():
            lines[-1] += line
        elif line.endswith(" -") and " - " in lines[-1] and len(lines[-1].rsplit(" ", 1)[-1]) <= 4:
            lines[-1] += line
        elif " - " in line and " " not in lines[-1] and lines[-1][:1].islower() and not re.match(r"^[a-z][\w-]*\s+-\s", line):
            lines[-1] += line
        elif ((lines[-1].casefold() in {"list of one or more", "list of zero or more"} and not re.match(r"^[a-z][\w-]*\s+-\s", line)) or lines[-1].endswith("of") or lines[-1].endswith("or") or lines[-1].endswith("not") or line.startswith("or more") or line.startswith("(")):
            lines[-1] += " " + line
        else:
            lines.append(line)
        if lines[-1].casefold().endswith("- enum"):
            enum_mode = True
    groups: list[list[str]] = []
    for line in lines:
        if re.match(r"^(?:[a-z][\w-]*|[A-Z][\w]*_[\w]+)\s+-\s", line):
            groups.append([line])
        elif groups:
            groups[-1].append(line)
        else:
            groups.append([line])
    if len(groups) == 1 and len(groups[0]) == 1:
        return groups[0][0]
    if groups and groups[0][0].casefold().startswith(("list, of length", "list of length")):
        remaining_text = " ".join(" ".join(group) for group in groups[1:])
        remaining = [item.strip() for item in re.split(r"(?<!\w)(?=[a-z][\w-]*\s+-\s)", remaining_text) if item.strip()]
        return {"type": "list", "items": ["change - list of one lifecycle state change", *remaining]}
    if nested and " - object" in groups[0][0].casefold() and len(groups) > 1:
        child_items = [" ".join(group) for group in groups[1:]]
        return {"type": "list", "items": [{"text": groups[0][0], "items": child_items}]}
    if nested and groups[0][0].casefold().startswith("list of") and len(groups) > 1:
        child_items: list[Any] = []
        for child in groups[1:]:
            if len(child) == 1:
                child_items.append(child[0])
            else:
                child_values = child[1:]
                if child[0].casefold().endswith("- enum"):
                    compact_values: list[str] = []
                    for value in child_values:
                        if compact_values and len(value) <= 4 and (compact_values[-1].endswith("_") or len(compact_values[-1]) > 6 or value.startswith("_")):
                            compact_values[-1] += value
                        else:
                            compact_values.append(value)
                    child_values = compact_values
                child_items.append({"text": child[0], "items": child_values})
        return {"type": "list", "items": [{"text": groups[0][0], "items": child_items}]}
    if nested and groups[0][0].casefold() == "enum" and len(groups) > 1:
        enum_items = [" ".join(group) for group in groups[1:]]
        return {"type": "list", "items": [{"text": "enum", "items": enum_items}]}
    items: list[Any] = []
    for group in groups:
        parent = group[0]
        if not nested:
            items.append(" ".join(group))
            continue
        if len(group) == 1:
            items.append(parent)
        else:
            nested = group[1:]
            if parent.casefold().endswith("- enum"):
                if parent.casefold() == "event - enum":
                    event_names = ["synthesisStarting", "playbackStarting", "paused", "resumed", "completed", "interrupted", "networkFailed", "synthesisFailed", "playbackFailed"]
                    combined = "".join(nested)
                    event_items = [name for name in event_names if name in combined]
                    items.append({"text": parent, "items": event_items})
                    continue
                enum_items: list[str] = []
                for enum_item in nested:
                    if enum_items and len(enum_item) <= 4 and (enum_items[-1].endswith("_") or len(enum_items[-1]) > 6 or enum_item.startswith("_")):
                        enum_items[-1] += enum_item
                    else:
                        enum_items.append(enum_item)
                items.append({"text": parent, "items": enum_items})
                continue
            if nested and nested[0].startswith("one of"):
                parent += " one of"
                nested[0] = nested[0][len("one of "):]
            elif nested and nested[0].startswith("of "):
                parent += " of"
                nested[0] = nested[0][len("of "):]
            if parent.casefold().startswith("keys - list of"):
                items.append(parent + " " + " ".join(nested))
                continue
            if parent.casefold().startswith("string, either") and nested:
                match = re.search(r"\s+(?=1 or more characters)", nested[0])
                if match:
                    nested = [nested[0][:match.start()].strip(), nested[0][match.start():].strip()]
                else:
                    parts = re.split(r"\)\s+", nested[0], maxsplit=1)
                    if len(parts) == 2:
                        nested = [parts[0].strip() + ")", parts[1].strip()]
            if len(nested) == 1 and not nested[0].startswith(('[]', '"')):
                items.append(parent + " " + nested[0])
                continue
            if len(nested) > 2 and nested[0].startswith("[]"):
                nested = [nested[0], " ".join(nested[1:])]
            compact_nested: list[str] = []
            for nested_item in nested:
                if nested_item.startswith('"'):
                    compact_nested.append(nested_item)
                elif compact_nested and compact_nested[-1].startswith('"'):
                    compact_nested[-1] += " " + nested_item
                elif compact_nested and nested_item == "inclusive":
                    compact_nested[-1] += " inclusive"
                else:
                    compact_nested.append(nested_item)
            nested = compact_nested
            if parent.casefold().startswith("string, either") and len(nested) == 1:
                parts = re.split(r"\)\s+", nested[0], maxsplit=1)
                if len(parts) == 2:
                    nested = [parts[0].strip() + ")", parts[1].strip()]
            items.append({"text": parent, "items": nested})
    return {"type": "list", "items": items}


def _method_text(value: Any) -> str:
    parts = []
    for part in str(value or "").split("/"):
        text = ""
        for line in _lines(part):
            fragment = "".join(line.split())
            if re.match(r"^on[A-Z]", fragment) and text:
                parts.append(text)
                text = fragment
            else:
                text += fragment
        status_callback = re.search(r"(?<=Status)on(?=[A-Z])", text)
        if status_callback:
            parts.extend((text[:status_callback.start()], text[status_callback.start():]))
            continue
        if text:
            parts.append(text)
    return "\n".join(part for part in parts if part)


def _tables(raw: dict[str, Any]) -> list[list[list[Any]]]:
    return [table for page in raw.get("pages", []) for table in page.get("tables", []) if table]


def _api_rows(raw: dict[str, Any]) -> list[list[Any]]:
    candidates: list[list[Any]] = []
    for table in _tables(raw):
        if not table:
            continue
        header = [_clean(cell).casefold() for cell in table[0]]
        if "module" in header and "method" in header and "description" in header:
            rows = [row for row in table[1:] if len(row) >= len(header) and _clean(row[1])]
            candidates.extend(rows)
            continue
        continuation = [
            row for row in table
            if len(row) >= 11 and _clean(row[0]).isdigit() and _clean(row[1])
        ]
        candidates.extend(continuation)
    unique: dict[str, list[Any]] = {}
    for row in candidates:
        unique.setdefault(_clean(row[0]), row)
    return list(unique.values())


def _network_interface_statistics_return() -> dict[str, Any]:
    interface_fields = [
        "txPackets - unsigned | null",
        "txError - unsigned | null",
        "txDropped - unsigned | null",
        "txFifoErrors - unsigned | null",
        "txCarrierErrors - unsigned | null",
        "rxPackets - unsigned | null",
        "rxError - unsigned | null",
        "rxDropped - unsigned | null",
        "rxFifoErrors - unsigned | null",
        "rxFrameErrors - unsigned | null",
        "linkTxBitRate - unsigned | null",
        "linkRxBitRate - unsigned | null",
    ]
    wireless_fields = [
        "wirelessFrequency - unsigned | null",
        "wirelessQuality - unsigned | null",
        "wirelessSignal - integer | null",
        "wirelessTxBitrate - unsigned | null",
        "wirelessRxBitrate - unsigned | null",
        "wirelessInactiveTime - unsigned | null",
        "wirelessRxBytes - unsigned | null",
        "wirelessRxPackets - unsigned | null",
        "wirelessRxDropped - unsigned | null",
        "wirelessTxBytes - unsigned | null",
        "wirelessTxPackets - unsigned | null",
        "wirelessTxRetries - unsigned | null",
        "wirelessTxFailed - unsigned | null",
        "wirelessExpectedThroughput - unsigned | null",
    ]
    return {"type": "list", "items": [{"text": "interfaceStats - object - optional", "items": interface_fields}, {"text": "wirelessStats - object - optional", "items": wireless_fields}]}


def _api_reference_definitions(raw: dict[str, Any]) -> dict[str, Any]:
    interpretation_rows = []
    type_rows = []
    error_rows = []
    current_class = ""
    error_red_row_ids = _api_error_red_row_ids(raw)
    for table in _tables(raw):
        if not table:
            continue
        headers = [_clean(value).casefold() for value in table[0]]
        if "term" in headers and "meaning" in headers:
            for row in table[1:]:
                if len(row) > 2 and _clean(row[1]):
                    interpretation_rows.append({"term": _clean(row[1]), "meaning": _clean(row[2])})
        elif "type" in headers and "definition" in headers:
            for row in table[1:]:
                if len(row) > 2 and _clean(row[1]):
                    type_rows.append({"type": _clean(row[1]), "definition": _clean(row[2])})
        is_error_continuation = len(table[0]) == 7 and any(_clean(row[0]).isdigit() for row in table[1:])
        if "class" in headers or is_error_continuation:
            rows = table[1:] if "class" in headers else table
            for row in rows:
                if len(row) < 7 or not _clean(row[0]).isdigit():
                    continue
                current_class = _clean(row[1]) or current_class
                error_data = {"class": current_class, "value": _clean(row[2]), "name": _clean(row[3]), "description": _clean(row[4]), "examples": _clean(row[5]), "openIssues": _clean(row[6])}
                if int(_clean(row[0])) in error_red_row_ids:
                    error_data["classes"] = "pdf-red-row"
                error_rows.append(error_data)
    definitions: dict[str, Any] = {}
    if interpretation_rows:
        definitions["reference-interpretation"] = {"type": "entry", "heading": "Interpretation", "blocks": [{"type": "table", "columns": [{"key": "term", "label": "Term"}, {"key": "meaning", "label": "Meaning"}], "rows": interpretation_rows}]}
    if type_rows:
        definitions["reference-types"] = {"type": "entry", "heading": "Types", "blocks": [{"type": "table", "columns": [{"key": "type", "label": "Type"}, {"key": "definition", "label": "Definition"}], "rows": type_rows}]}
    if error_rows:
        definitions["reference-error-values"] = {"type": "entry", "heading": "Error values", "blocks": [{"type": "table", "columns": [{"key": "class", "label": "Class"}, {"key": "value", "label": "Value"}, {"key": "name", "label": "Name"}, {"key": "description", "label": "Description"}, {"key": "examples", "label": "Examples"}, {"key": "openIssues", "label": "Open issues"}], "rows": error_rows}]}
    return definitions


# --------------------------------------------------------------------------------------------------
# Crypto page helpers
#
# The crypto "Methods" table is a 10 column table:
#   0 id | 1 Module | 2 Method | 3 Parameters | 4 Returns | 5 Specific errors | 6 Firebolt global
#   | 7 C++ | 8 JS | 9 Description
# Parameters / Returns / Specific errors are narrow columns, so the PDF hard-wraps them (sometimes in
# the middle of a word) and draws bullets as vector shapes, which a plain text extraction loses.
# These cells are therefore rebuilt from the PDF geometry (bullets, indentation, line gaps).
# --------------------------------------------------------------------------------------------------
CRYPTO_METHOD_COLUMNS = 10
CRYPTO_FIELD_COLUMNS = {"parameters": 3, "returns": 4, "errors": 5}
CRYPTO_GLOBAL_COLUMN = 6
CRYPTO_CPP_COLUMN = 7
CRYPTO_JS_COLUMN = 8
CRYPTO_DESCRIPTION_COLUMN = 9
CRYPTO_BULLET_MIN_SIZE = 1.0
CRYPTO_BULLET_MAX_SIZE = 4.5
CRYPTO_BULLET_LINE_TOLERANCE = 3.0
CRYPTO_LINE_MERGE_TOLERANCE = 2.0
CRYPTO_CELL_GAP_LIMIT = 40.0  # a bigger vertical jump inside a cell is page furniture (footer), not content
CRYPTO_PARAGRAPH_FACTOR = 1.5  # gap > 1.5 x normal line pitch starts a new un-bulleted paragraph
CRYPTO_MIN_KNOWN_WORD = 3
CRYPTO_SOURCE_PDF = "Firebolt 9 Crypto API Specifications.pdf"  # used when the raw JSON carries no "source"


def _crypto_is_table(value: Any) -> bool:
    """A table is a non-empty list of rows, a row is a list of plain cells (str / None)."""
    return (
        isinstance(value, list) and bool(value)
        and all(isinstance(row, list) for row in value)
        and all(not isinstance(cell, (list, dict)) for row in value for cell in row)
    )


def _crypto_normalize_raw(raw: Any) -> dict[str, Any]:
    """Accept the raw JSON in any of its usual shapes and return {"source", "pages": [{"tables": [...]}]}:
    a dict with "pages", a list of page dicts, a list of pages (each a list of tables), a flat list of
    tables, or a single table."""
    if isinstance(raw, dict):
        pages = raw.get("pages")
        if pages is None:
            pages = raw.get("tables")
            pages = [{"tables": pages}] if pages is not None else []
        normalized = dict(raw)
        raw = pages
    else:
        normalized = {}
    items = list(raw) if isinstance(raw, list) else []
    if _crypto_is_table(items):
        pages = [{"tables": [items]}]  # a single table
    elif items and all(_crypto_is_table(item) for item in items):
        pages = [{"tables": items}]  # flat list of tables
    else:
        pages = []
        for item in items:
            if isinstance(item, dict):
                pages.append({**item, "tables": item.get("tables") or []})
            elif isinstance(item, list):
                pages.append({"tables": [table for table in item if _crypto_is_table(table)]})
    normalized["pages"] = pages
    normalized["source"] = str(normalized.get("source") or CRYPTO_SOURCE_PDF)
    return normalized


def _crypto_pdf_path(raw: dict[str, Any]) -> Path | None:
    """ROOT/assets/pdf/<source>; if that exact file is missing, the only *crypto*.pdf in that folder."""
    folder = ROOT / "assets" / "pdf"
    exact = folder / str(raw.get("source", ""))
    if exact.is_file():
        return exact
    matches = sorted(path for path in folder.glob("*.pdf") if "crypto" in path.name.casefold())
    return matches[0] if len(matches) == 1 else None


def _crypto_error_id(value: Any) -> str:
    compact = "".join(str(value or "").split())
    return compact if re.fullmatch(r"-?xxxx[a-z]", compact) else ""


def _crypto_name(value: Any) -> str:
    """Module / method names are wrapped mid-word ("deriveSessi" / "onKeys"), so drop every line break.
    (_method_text is not used here: it treats a fragment such as "onKeys" as an on<Event> callback name.)"""
    return "".join(str(value or "").split())


def _crypto_text(value: Any) -> str:
    """Wrapped prose: join lines with a space, but not after a hyphen wrap ("confidentiality-" / "protected")."""
    text = ""
    for line in _lines(value):
        text = text + line if text.endswith("-") and not text.endswith(" -") else (text + " " + line if text else line)
    return text


def _crypto_rows(raw: dict[str, Any]) -> list[list[Any]]:
    """Method rows of the crypto table. A row with an empty id is the spill-over of the previous method
    (e.g. getKeyInfo's keyAlgo lands on the next page) and is merged back into it."""
    rows: list[list[Any]] = []
    for table in _tables(raw):
        if len(table[0]) != CRYPTO_METHOD_COLUMNS:
            continue
        for row in table:
            if len(row) < CRYPTO_METHOD_COLUMNS:
                continue
            identifier = _clean(row[0])
            if identifier.isdigit() and _clean(row[1]):
                rows.append([str(cell or "") for cell in row])
            elif not identifier and rows and _clean(row[1]).casefold() != "module" and any(_clean(cell) for cell in row):
                for index, cell in enumerate(row):
                    if _clean(cell):
                        rows[-1][index] = f"{rows[-1][index]}\n{cell}" if _clean(rows[-1][index]) else str(cell)
    unique: dict[str, list[Any]] = {}
    for row in rows:
        unique.setdefault(_clean(row[0]), row)
    return list(unique.values())


def _crypto_vocabulary(pdf: Any) -> set[str]:
    """Words that appear *unbroken* in the wide cells of the PDF (descriptions, error table, ...).
    Used to decide whether a wrapped line break is a word boundary or a break inside a word."""
    vocabulary: set[str] = set()
    for page in pdf.pages:
        for table in page.find_tables():
            for row in table.extract():
                cells = [row[CRYPTO_DESCRIPTION_COLUMN]] if len(row) == CRYPTO_METHOD_COLUMNS else row
                for cell in cells:
                    for word in re.findall(r"[A-Za-z][A-Za-z0-9_]*", str(cell or "")):
                        vocabulary.add(word)
                        vocabulary.add(word.lower())
    return vocabulary


def _crypto_is_known(token: str, vocabulary: set[str]) -> bool:
    return len(token) >= CRYPTO_MIN_KNOWN_WORD and (token in vocabulary or token.lower() in vocabulary)


def _crypto_glue(previous: str, following: str, vocabulary: set[str], identifiers: bool) -> str:
    """Join two wrapped lines of one bullet, restoring words that the PDF broke across lines."""
    if previous.endswith(" ") or following.startswith(" "):
        return previous + following  # wrapped at a real space
    if following == "-" or following.startswith("- "):
        return previous + " " + following  # "primePDataLength" / "- unsigned"
    if previous.endswith(" -"):
        return previous + " " + following
    if previous.endswith("-"):
        return previous + following  # hyphen wrap: "pre-" / "provisioned"
    if following[:1] in ".,;:)":
        return previous + following  # "ordered" / "."
    if identifiers and previous[-1:].islower() and following[:1].isupper():
        return previous + following  # camelCase identifier cut in two: "encrypt" / "DataOff"
    tail = re.search(r"[A-Za-z0-9_]+$", previous)
    head = re.match(r"[A-Za-z0-9_]+", following)
    if tail and head:
        left, right = tail.group(), head.group()
        # two real words that do not form a real word ("represent" + "valid") are a word boundary
        if _crypto_is_known(left, vocabulary) and _crypto_is_known(right, vocabulary) and not _crypto_is_known(left + right, vocabulary):
            return previous + " " + following
    return previous + following  # break inside a word: "Authentic" / "ation"


def _crypto_cell_lines(page: Any, bbox: tuple[float, float, float, float], bullets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    left, top, right, bottom = bbox
    box = (max(0.0, left), max(0.0, top), min(float(page.width), right), min(float(page.height), bottom))
    if box[2] <= box[0] or box[3] <= box[1]:
        return []
    chars = sorted(page.crop(box).chars, key=lambda char: (char["top"], char["x0"]))
    groups: list[list[dict[str, Any]]] = []
    for char in chars:
        if groups and abs(char["top"] - groups[-1][0]["top"]) <= CRYPTO_LINE_MERGE_TOLERANCE:
            groups[-1].append(char)
        else:
            groups.append([char])
    lines: list[dict[str, Any]] = []
    for group in groups:
        group.sort(key=lambda char: char["x0"])
        visible = [char for char in group if char["text"].strip()]
        if not visible:
            continue
        middle = (visible[0]["top"] + visible[0]["bottom"]) / 2
        level = 0
        for bullet in bullets:
            bullet_middle = (bullet["top"] + bullet["bottom"]) / 2
            if abs(bullet_middle - middle) <= CRYPTO_BULLET_LINE_TOLERANCE and box[0] - 1 <= bullet["x0"] and bullet["x1"] <= visible[0]["x0"] + 1:
                level = 1 if bullet.get("fill") and not bullet.get("stroke") else 2  # filled = bullet, hollow = sub bullet
                break
        lines.append({"text": "".join(char["text"] for char in group), "top": group[0]["top"], "level": level})
    return lines


def _crypto_cell_entries(lines: list[dict[str, Any]], vocabulary: set[str], identifiers: bool) -> list[dict[str, Any]]:
    gaps = [after["top"] - before["top"] for before, after in zip(lines, lines[1:]) if 0 < after["top"] - before["top"] <= CRYPTO_CELL_GAP_LIMIT]
    paragraph_gap = (min(gaps) if gaps else 7.0) * CRYPTO_PARAGRAPH_FACTOR
    entries: list[dict[str, Any]] = []
    previous_top: float | None = None
    for line in lines:
        gap = 0.0 if previous_top is None else line["top"] - previous_top
        if gap > CRYPTO_CELL_GAP_LIMIT:
            break
        previous_top = line["top"]
        if not entries or line["level"] or gap > paragraph_gap:
            entries.append({"level": line["level"], "text": line["text"].lstrip()})
        else:
            entries[-1]["text"] = _crypto_glue(entries[-1]["text"], line["text"], vocabulary, identifiers)
    for entry in entries:
        entry["text"] = _clean(entry["text"])
    return [entry for entry in entries if entry["text"]]


def _crypto_pdf_cells(raw: dict[str, Any]) -> dict[int, dict[str, list[dict[str, Any]]]]:
    """method id -> {"parameters"|"returns"|"errors": [{"level": 0|1|2, "text": str}, ...]}"""
    pdf_path = _crypto_pdf_path(raw)
    if pdf_path is None:
        return {}
    cells: dict[int, dict[str, list[dict[str, Any]]]] = {}
    with pdfplumber.open(pdf_path) as pdf:
        vocabulary = _crypto_vocabulary(pdf)
        current: int | None = None
        for page in pdf.pages:
            bullets = [
                curve for curve in page.curves
                if CRYPTO_BULLET_MIN_SIZE <= curve["width"] <= CRYPTO_BULLET_MAX_SIZE
                and CRYPTO_BULLET_MIN_SIZE <= curve["height"] <= CRYPTO_BULLET_MAX_SIZE
            ]
            for table in page.find_tables():
                extracted = table.extract()
                if not extracted or len(extracted[0]) != CRYPTO_METHOD_COLUMNS:
                    continue
                for index, row in enumerate(table.rows):
                    identifier = _clean(extracted[index][0])
                    if identifier.isdigit():
                        current = int(identifier)  # new method
                    elif _clean(extracted[index][1]).casefold() == "module" or current is None:
                        continue  # header row; any other row with an empty id continues the previous method
                    target = cells.setdefault(current, {field: [] for field in CRYPTO_FIELD_COLUMNS})
                    for field, column in CRYPTO_FIELD_COLUMNS.items():
                        bbox = row.cells[column] if column < len(row.cells) else None
                        if bbox is None:
                            continue
                        lines = _crypto_cell_lines(page, bbox, bullets)
                        target[field].extend(_crypto_cell_entries(lines, vocabulary, identifiers=field != "errors"))
    return cells


def _crypto_render(entries: list[dict[str, Any]]) -> Any:
    """Turn bullet entries into the site's list schema: plain string for a single line, otherwise
    {"type": "list", "items": [str | {"text": str, "items": [...]}]}."""
    nodes: list[dict[str, Any]] = []
    for entry in entries:
        if entry["level"] >= 2 and nodes:
            nodes[-1]["items"].append(entry["text"])  # hollow bullet = child of the last bullet
        else:
            nodes.append({"text": entry["text"], "items": [], "plain": entry["level"] == 0})

    def item(node: dict[str, Any]) -> Any:
        return {"text": node["text"], "items": node["items"]} if node["items"] else node["text"]

    # "Optional parameter for X:" / "{" / bullets / "}"  ->  the paragraph becomes the parent of the bullets
    result: list[dict[str, Any]] = []
    index = 0
    while index < len(nodes):
        node = nodes[index]
        if node["text"] == "{" and result and result[-1]["plain"] and not result[-1]["items"]:
            end = index + 1
            while end < len(nodes) and nodes[end]["text"] != "}":
                result[-1]["items"].append(item(nodes[end]))
                end += 1
            index = end + 1
            continue
        result.append(node)
        index += 1
    if not result:
        return ""
    if len(result) == 1 and not result[0]["items"]:
        return result[0]["text"]
    return {"type": "list", "items": [item(node) for node in result]}


def _crypto_reference_definitions(raw: dict[str, Any]) -> dict[str, Any]:
    interpretation_rows = []
    type_rows = []
    error_rows = []
    current_class = ""
    for table in _tables(raw):
        headers = [_clean(value).casefold() for value in table[0]]
        if "term" in headers and "meaning" in headers:
            for row in table[1:]:
                if len(row) > 2 and _clean(row[1]):
                    interpretation_rows.append({"term": _clean(row[1]), "meaning": _clean(row[2])})
        elif "type" in headers and "definition" in headers:
            for row in table[1:]:
                if len(row) > 2 and _clean(row[1]):
                    type_rows.append({"type": _clean(row[1]), "definition": _clean(row[2])})
        elif len(table[0]) == 5 and ("id" in headers or any(len(row) > 1 and _crypto_error_id(row[1]) for row in table)):
            # Errors table. It starts on page 1 (with a header) and continues on page 2 (without one).
            for row in table:
                if len(row) < 5 or not _crypto_error_id(row[1]):
                    continue
                current_class = "".join(str(row[0] or "").split()) or current_class  # "Specifi\nc" -> "Specific"
                notes = " ".join(part for part in (_clean(row[3]), _clean(row[4])) if part)
                error_rows.append({"class": current_class, "ID": _crypto_error_id(row[1]), "Error": _clean(row[2]), "Notes": notes})
    definitions: dict[str, Any] = {}
    if interpretation_rows:
        definitions["reference-interpretation"] = {"type": "entry", "heading": "Interpretation", "blocks": [{"type": "table", "columns": [{"key": "term", "label": "Term"}, {"key": "meaning", "label": "Meaning"}], "rows": interpretation_rows}]}
    if type_rows:
        definitions["reference-types"] = {"type": "entry", "heading": "Types", "blocks": [{"type": "table", "columns": [{"key": "type", "label": "Type"}, {"key": "definition", "label": "Definition"}], "rows": type_rows}]}
    if error_rows:
        definitions["reference-error-values"] = {"type": "entry", "heading": "Error values", "blocks": [{"type": "table", "columns": [{"key": "class", "label": "Specific"}, {"key": "ID", "label": "ID"}, {"key": "Error", "label": "Error"}, {"key": "Notes", "label": "Notes"}], "rows": error_rows}]}
    return definitions


def _api_document(name: str, title: str, raw: dict[str, Any]) -> dict[str, Any]:
    rows = []
    definitions: dict[str, Any] = _api_reference_definitions(raw)
    modules: set[str] = set()
    support_states = _api_support_states(raw)
    amber_method_ids = _api_amber_method_ids(raw)
    for index, row in enumerate(_api_rows(raw)):
        module = _method_text(row[1])
        method = _method_text(row[2])
        returns = _network_interface_statistics_return() if module == "Network" and method == "interfaceStatistics" else _value(row[4]) or "None"
        deprecated = _clean(row[7])
        reference = f"api-{index}"
        modules.add(module)
        row_data = {
            "module": module,
            "methods": method,
            "version": _clean(row[6]),
            "deprecated": deprecated or "-",
            "details": {"type": "actions", "plain": True, "items": [{"label": "View Details", "ref": reference}]},
        }
        if int(_clean(row[0])) in amber_method_ids:
            row_data["classes"] = "pdf-red-row"
        rows.append(row_data)
        cpp17_state, js_state = support_states.get(int(_clean(row[0])), ("unknown", "unknown"))
        support = [{"label": "C++17", "state": cpp17_state}, {"label": "JS", "state": js_state}]
        definitions[reference] = {
            "type": "apiMethod",
            "eyebrow": "Module",
            "module": module,
            "method": method,
            "version": _clean(row[6]),
            "deprecated": deprecated,
            "support": support,
            "fields": [
                {"label": "Parameters", "value": _value(row[3], nested=bool(re.search(r"\b(enum|list|object)\b", str(row[3]), re.I))) or "None"},
                {"label": "Returns", "value": returns},
                {"label": "Specific errors", "value": _value(row[5], nested=False) or "None"},
            ],
            "overview": _clean(row[10]),
            "trailing": [],
        }
    return {
        "schemaVersion": "1.0",
        "hero": {"eyebrow": "Firebolt 9", "title": title, "description": "Standardized Firebolt 9 APIs.", "status": "Draft"},
        "source": {"label": raw.get("source", name), "href": f"assets/pdf/{raw.get('source', '')}"},
        "blocks": [{
            "type": "section",
            "classes": "api-spec-content",
            "blocks": [
                {"type": "toolbar", "target": "api-methods", "classes": "northbound-toolbar", "search": {"placeholder": "Search APIs"}, "filters": [{"key": "module", "column": 0, "allLabel": "All modules", "options": sorted(modules)}]},
                {"type": "reference", "title": "References", "items": [{"label": "Interpretation", "ref": "reference-interpretation"}, {"label": "Types", "ref": "reference-types"}, {"label": "Error values", "ref": "reference-error-values"}]},
                {"type": "table", "id": "api-methods", "columns": [{"key": "module", "label": "Module"}, {"key": "methods", "label": "Methods", "wrap": "preline"}, {"key": "version", "label": "API version"}, {"key": "deprecated", "label": "To be deprecated (post RDK9)"}, {"key": "details", "label": "View Details"}], "rows": rows},
            ],
        }],
        "definitions": definitions,
    }

def _crypto_document(name: str, title: str, raw: Any) -> dict[str, Any]:
    raw = _crypto_normalize_raw(raw)
    rows = []
    definitions: dict[str, Any] = _crypto_reference_definitions(raw)
    modules: set[str] = set()
    method_rows = _crypto_rows(raw)
    support_states = _crypto_support_states(method_rows)
    pdf_cells = _crypto_pdf_cells(raw)
    for index, row in enumerate(method_rows):
        method_id = int(_clean(row[0]))
        module = _crypto_name(row[1])
        method = _crypto_name(row[2])
        firebolt_global = _clean(row[CRYPTO_GLOBAL_COLUMN])
        reference = f"api-{index}"
        modules.add(module)
        rows.append({
            "module": module,
            "methods": method,
            "firebolt-global": firebolt_global,
            "details": {"type": "actions", "plain": True, "items": [{"label": "View Details", "ref": reference}]},
        })
        cpp_state, js_state = support_states.get(method_id, ("unknown", "unknown"))
        cells = pdf_cells.get(method_id)
        if cells:  # rebuilt from the PDF: one line per bullet, sub bullets nested
            parameters = _crypto_render(cells["parameters"])
            returns = _crypto_render(cells["returns"])
            errors = _crypto_render(cells["errors"])
        else:  # PDF not available: best effort from the raw table text
            parameters = _value(row[3], nested=bool(re.search(r"\b(enum|list|object)\b", str(row[3]), re.I)))
            returns = _value(row[4])
            errors = _value(row[5], nested=False)
        definitions[reference] = {
            "type": "apiMethod",
            "eyebrow": "Module",
            "module": module,
            "method": method,
            "firebolt-global": firebolt_global,
            "support": [{"label": "C++", "state": cpp_state}, {"label": "JS", "state": js_state}],
            "fields": [
                {"label": "Parameters", "value": parameters or "None"},
                {"label": "Returns", "value": returns or "None"},
                {"label": "Specific errors", "value": errors or "None"},
            ],
            "overview": _crypto_text(row[CRYPTO_DESCRIPTION_COLUMN]),
            "trailing": [],
        }
    return {
        "schemaVersion": "1.0",
        "hero": {"eyebrow": "Firebolt 9", "title": title, "description": "Standardized Firebolt 9 Crypto APIs.", "status": "Draft"},
        "source": {"label": raw.get("source", name), "href": f"assets/pdf/{raw.get('source', '')}"},
        "blocks": [{
            "type": "section",
            "classes": "api-spec-content",
            "blocks": [
                {"type": "toolbar", "target": "api-methods", "classes": "northbound-toolbar", "search": {"placeholder": "Search APIs"}, "filters": [{"key": "module", "column": 0, "allLabel": "All modules", "options": sorted(modules)}]},
                {"type": "reference", "title": "References", "items": [{"label": "Interpretation", "ref": "reference-interpretation"}, {"label": "Types", "ref": "reference-types"}, {"label": "Error values", "ref": "reference-error-values"}]},
                {"type": "table", "id": "api-methods", "columns": [{"key": "module", "label": "Module"}, {"key": "methods", "label": "Methods", "wrap": "preline"}, {"key": "firebolt-global", "label": "Firebolt global"}, {"key": "details", "label": "View Details"}], "rows": rows},
            ],
        }],
        "definitions": definitions,
    }


def _key_sections(raw: dict[str, Any]) -> tuple[list[list[Any]], list[list[Any]]]:
    standard: list[list[Any]] = []
    partner: list[list[Any]] = []
    for table in _tables(raw):
        if not table:
            continue
        if "RCU" in _clean(table[0][0]) and len(table[0]) >= 8:
            for row in table[1:]:
                if _clean(row[0]) and not _clean(row[0]).casefold().startswith("partner buttons"):
                    standard.append(row)
        elif len(table[0]) >= 8 and _clean(table[0][0]) and _clean(table[0][0]).casefold() not in {"document status", "author"}:
            partner.extend(row for row in table[1:] if _clean(row[0]))
    return standard, partner


def _key_document(name: str, title: str, raw: dict[str, Any]) -> dict[str, Any]:
    standard_rows, partner_rows = _key_sections(raw)
    rows = []
    partner_table_rows = []
    definitions = {}
    def convert_rows(source_rows: list[list[Any]], prefix: str, target_rows: list[dict[str, Any]]) -> None:
      for index, row in enumerate(source_rows):
        reference = f"{prefix}-{index}"
        button = _clean(row[0])
        target_rows.append({"button": button, "mandatory": _clean(row[1]), "linuxCode": _clean(row[2]), "details": {"type": "actions", "items": [{"label": "View Details", "ref": reference}]}})
        labels = ["RCU Button", "Mandatory", "Linux key code", "JS event key", "JS event code", "Deprecated keyCode/which", "Flutter logical key", "Flutter logical key (Hex)", "System Key", "Manifest name"]
        definitions[reference] = {"type": "fields", "eyebrow": "Key code", "heading": button, "fields": [{"label": label, "value": _clean(row[pos]) if pos < len(row) else ""} for pos, label in enumerate(labels)]}
    convert_rows(standard_rows, "standard-key", rows)
    convert_rows(partner_rows, "partner-key", partner_table_rows)
    columns = [{"key": "button", "label": "RCU Button"}, {"key": "mandatory", "label": "Key is mandatorily supported on a remote"}, {"key": "linuxCode", "label": "Linux Key code (Sent via Wayland)"}, {"key": "details", "label": "View Details"}]
    return {
        "schemaVersion": "1.0",
        "hero": {"eyebrow": "Firebolt 9", "title": title, "description": "Key Codes made available to Firebolt applications.", "status": "Approved"},
        "source": {"label": raw.get("source", name), "href": f"assets/pdf/{raw.get('source', '')}"},
        "blocks": [{"type": "section", "id": "standard-keys", "heading": "Standard RCU keys", "blocks": [{"type": "table", "classes": "key-codes-table", "columns": columns, "rows": rows}]}, {"type": "section", "id": "partner-keys", "heading": "Partner Buttons", "blocks": [{"type": "prose", "body": "These are buttons on some RCU that are labelled Netflix, YouTube, etc. The key codes for these buttons are artificially generated within the window manager, based on the RCU type and the physical button pressed."}, {"type": "table", "classes": "key-codes-table", "columns": columns, "rows": partner_table_rows}]}],
        "definitions": definitions,
    }


def _intent_table(raw: dict[str, Any]) -> tuple[list[str], list[list[Any]]]:
    for table in _tables(raw):
        if table and "Part" in _clean(table[0][0]) and len(table[0]) >= 5:
            return [_clean(value) for value in table[0][:5]], [row[:5] for row in table[1:] if _clean(row[0])]
    return ["Part", "Type", "Mandatory", "Description", "Allowed values"], []


def _nested_intent_table(table: list[list[Any]]) -> dict[str, Any]:
    columns = [{"key": "name", "label": "Name"}, {"key": "type", "label": "Type"}, {"key": "mandatory", "label": "Mandatory"}, {"key": "allowedValues", "label": "Allowed values"}, {"key": "description", "label": "Description"}]
    rows = []
    current_nested: list[dict[str, Any]] = []
    for raw_row in table:
        values = [_clean(value) for value in raw_row]
        if values and values[0].casefold() == "name":
            continue
        if values and values[0]:
            if current_nested:
                rows[-1]["allowedValues"] = {"type": "details", "summary": f"{rows[-1]['name']} fields", "blocks": [{"type": "table", "columns": columns, "rows": current_nested}]}
                current_nested = []
            rows.append({"name": values[0], "type": values[1] if len(values) > 1 else "", "mandatory": values[2] if len(values) > 2 else "", "allowedValues": values[3] if len(values) > 3 else "", "description": values[-1] if len(values) > 4 else ""})
        elif len(values) > 3 and values[3]:
            tail = values[4:]
            mandatory_index = next((index for index, value in enumerate(tail) if value in {"Yes", "No", "yes", "no"}), None)
            if mandatory_index is not None:
                field_type = next((value for value in tail[:mandatory_index] if value), "")
                allowed = next((value for value in tail[mandatory_index + 1:] if value), "")
                allowed_position = next((index for index, value in enumerate(tail[mandatory_index + 1:], mandatory_index + 1) if value), mandatory_index + 1)
                description = next((value for value in tail[allowed_position + 1:] if value), "")
            else:
                field_type = tail[0] if tail else ""
                allowed = ""
                description = ""
            current_nested.append({"name": _method_text(values[3]), "type": field_type, "mandatory": tail[mandatory_index] if mandatory_index is not None else "", "allowedValues": allowed, "description": description})
    if current_nested and rows:
        rows[-1]["allowedValues"] = {"type": "details", "summary": f"{rows[-1]['name']} fields", "blocks": [{"type": "table", "columns": columns, "rows": current_nested}]}
    return {"type": "table", "columns": columns, "rows": rows}


def _app_action_table(table: list[list[Any]]) -> dict[str, Any]:
    def field_name(value: Any) -> str:
        return "".join(str(value or "").split())

    columns = [
        {"key": "part", "label": "Part"},
        {"key": "type", "label": "Type"},
        {"key": "mandatory", "label": "Mandatory"},
        {"key": "description", "label": "Description"},
        {"key": "allowedValues", "label": "Allowed values"},
    ]
    nested_columns = [
        {"key": "part", "label": "Part"},
        {"key": "type", "label": "Type"},
        {"key": "mandatory", "label": "Mandatory"},
        {"key": "description", "label": "Description"},
    ]
    rows = []
    nested_rows = []
    for raw_row in table[1:]:
        values = [_clean(value) for value in raw_row]
        if values and values[0]:
            if nested_rows:
                rows[-1]["allowedValues"] = {
                    "type": "details",
                    "summary": f"{rows[-1]['part']} fields",
                    "blocks": [{"type": "table", "columns": nested_columns, "rows": nested_rows}],
                }
                nested_rows = []
            allowed = values[4] if len(values) > 4 else ""
            if values[0] == "environment" and "\n" in str(raw_row[4] if len(raw_row) > 4 else ""):
                allowed = {"type": "list", "items": [item for item in _lines(raw_row[4]) if item]}
            rows.append({
                "part": field_name(values[0]),
                "type": values[1] if len(values) > 1 else "",
                "mandatory": values[2] if len(values) > 2 else "",
                "description": values[3] if len(values) > 3 else "",
                "allowedValues": allowed,
            })
        elif len(values) >= 8 and values[4]:
            nested_rows.append({
                "part": field_name(values[4]),
                "type": values[5],
                "mandatory": values[6],
                "description": values[7],
            })
    if nested_rows and rows:
        rows[-1]["allowedValues"] = {
            "type": "details",
            "summary": f"{rows[-1]['part']} fields",
            "blocks": [{"type": "table", "columns": nested_columns, "rows": nested_rows}],
        }
    return {"type": "table", "columns": columns, "rows": rows}


def _json_objects(value: str) -> list[str]:
    objects: list[str] = []
    start = -1
    depth = 0
    in_string = False
    escaped = False
    for index, character in enumerate(value):
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character == "{":
            if depth == 0:
                start = index
            depth += 1
        elif character == "}" and depth:
            depth -= 1
            if depth == 0 and start >= 0:
                objects.append(value[start:index + 1].strip())
                start = -1
    return objects


def _intent_document(name: str, title: str, raw: dict[str, Any]) -> dict[str, Any]:
    headers, source_rows = _intent_table(raw)
    action_names = []
    for line in str(raw.get("pages", [{}])[0].get("text", "")).splitlines():
        match = re.match(r"\s*([A-Za-z][A-Za-z-]*) action type\s*$", line)
        if match:
            action_names.append(match.group(1).casefold())
    definitions = {}
    all_text = "\n".join(str(page.get("text", "")) for page in raw.get("pages", []))
    action_sections = {}
    detail_tables: list[dict[str, Any]] = []
    for table in _tables(raw):
        if not table or _clean(table[0][0]) != "Name":
            continue
        rows = []
        for item in table[1:]:
            if len(item) < 5 or not _clean(item[0]):
                continue
            rows.append({"name": _clean(item[0]), "type": _clean(item[1]), "mandatory": _clean(item[2]), "allowedValues": _clean(item[3]), "description": _clean(item[4])})
        if rows:
            detail_tables.append({"type": "table", "columns": [{"key": "name", "label": "Name"}, {"key": "type", "label": "Type"}, {"key": "mandatory", "label": "Mandatory"}, {"key": "allowedValues", "label": "Allowed values"}, {"key": "description", "label": "Description"}], "rows": rows})
    section_matches = list(re.finditer(r"^\s*(.+?) action type\s*$", all_text, re.MULTILINE))
    for position, match in enumerate(section_matches):
        action_title = match.group(1).strip()
        end = section_matches[position + 1].start() if position + 1 < len(section_matches) else len(all_text)
        section_text = all_text[match.end():end]
        prose = [" ".join(line.split()) for line in section_text.splitlines() if len(line.strip()) > 35]
        definition_text = ""
        example_text = ""
        definition_match = re.search(r"Definition of data object(.*?)(?=Example|$)", section_text, re.S | re.I)
        if definition_match:
            definition_text = " ".join(definition_match.group(1).split())
        example_match = re.search(r"Example(.*?)(?=\n\s*[A-Za-z][A-Za-z-]* action type|$)", section_text, re.S | re.I)
        if example_match:
            example_body = example_match.group(1)
            start = example_body.find("{")
            end_brace = example_body.rfind("}")
            if start >= 0 and end_brace > start:
                example_text = example_body[start:end_brace + 1].strip()
        blocks = []
        if definition_text:
            blocks.extend([{"type": "heading", "body": "Definition of data object"}, {"type": "code", "body": definition_text, "variant": "spec-definition-text"}])
        if example_text:
            blocks.extend([{"type": "heading", "body": "Example"}, {"type": "examples", "blocks": [{"type": "code", "body": example_text, "variant": "spec-example"}]}])
        action_sections[action_title.casefold()] = {"overview": prose[0] if prose else f"The {action_title} action type.", "blocks": blocks}
    action_refs = []
    unique_actions = list(dict.fromkeys(action_names))
    action_blocks: dict[str, list[dict[str, Any]]] = {action: [] for action in unique_actions}
    table_targets = ["launch", "entity", None, "search", "section", None, "tune", "play-query"]
    for table_index, table in enumerate(detail_tables):
        if table_index >= len(table_targets):
            break
        target = table_targets[table_index]
        if target:
            action_blocks[target].extend([{"type": "heading", "body": "Definition of data object"}, table])
    pages = {page.get("page"): page for page in raw.get("pages", [])}
    if pages.get(6) and pages[6].get("tables"):
        action_blocks["tune"] = [{"type": "heading", "body": "Definition of data object"}, _nested_intent_table(pages[6]["tables"][0])]
    if pages.get(6) and len(pages[6].get("tables", [])) > 1:
        action_blocks["play-entity"] = [{"type": "heading", "body": "Definition of data object"}, _nested_intent_table(pages[6]["tables"][1])]
    if pages.get(7) and pages[7].get("tables"):
        action_blocks["play-query"] = [{"type": "heading", "body": "Definition of data object"}, _nested_intent_table(pages[7]["tables"][0])]
    if action_blocks.get("entity"):
        action_blocks["playback"] = copy.deepcopy(action_blocks["entity"])
    for action in unique_actions:
        reference = f"intent-{action}"
        action_refs.append({"label": action, "ref": reference})
        section = action_sections.get(action.casefold(), {"overview": f"Definition of the {action} action type.", "blocks": []})
        table_blocks = action_blocks.get(action.casefold(), [])
        trailing_blocks = section["blocks"]
        if any(block.get("type") == "table" for block in table_blocks):
            trailing_blocks = [
                block for block in trailing_blocks
                if not (block.get("type") == "heading" and block.get("body") == "Definition of data object")
                and not (block.get("type") == "code" and block.get("variant") == "spec-definition-text")
            ]
        blocks = table_blocks + trailing_blocks
        definitions[reference] = {"type": "entry", "eyebrow": "Intent action", "heading": f"{action.title()} action type", "overview": section["overview"], "blocks": blocks}
    rows = []
    for row in source_rows:
        values = [_clean(value) for value in row]
        if values[0] == "action" and action_refs:
            values[4] = {"type": "actions", "items": action_refs}
        elif values[0] == "data":
            values[4] = "Click an action type above for more details."
        row = dict(zip(("part", "type", "mandatory", "description", "allowedValues"), values))
        if values[0] == "context":
            context_rows = []
            for table in _tables(raw):
                if table and _clean(table[0][0]) == "Name":
                    context_rows.extend({"name": _clean(item[0]), "type": _clean(item[1]), "mandatory": _clean(item[2]), "allowedValues": _clean(item[3]), "description": _clean(item[4])} for item in table[1:] if len(item) >= 5 and _clean(item[0]))
                    break
            if context_rows:
                row["allowedValues"] = {"type": "details", "summary": "Context fields", "blocks": [{"type": "table", "columns": [{"key": "name", "label": "Name"}, {"key": "type", "label": "Type"}, {"key": "mandatory", "label": "Mandatory"}, {"key": "allowedValues", "label": "Allowed values"}, {"key": "description", "label": "Description"}], "rows": context_rows}]}
        rows.append(row)
    return {
        "schemaVersion": "1.0",
        "hero": {"eyebrow": "Firebolt 9", "title": title, "description": "Intent definitions for Firebolt 9 applications.", "status": "Approved"},
        "source": {"label": raw.get("source", name), "href": f"assets/pdf/{raw.get('source', '')}"},
        "blocks": [{"type": "section", "id": "overview", "classes": "intent-overview", "blocks": [{"type": "prose", "body": "An Intent is a message object sent to an application requesting a specific action. This may occur as part of the launch of the application or when it is already loaded. The application shall treat the receipt of an intent as an explicit request to carry out the intent and immediately action it, irrespective of what the application is currently doing. The only exception to this if the application is carrying out some process that can not be interrupted eg processing a payment."}, {"type": "prose", "body": "An application may support multiple intent action types or none, however if an application receives an intent that it does not support, or one that does not contain enough data for an application to fulfil it, it shall ignore it and not present any error to the user."}]}, {"type": "section", "classes": "intent-actions-section", "blocks": [{"type": "table", "columns": [{"key": "part", "label": headers[0]}, {"key": "type", "label": headers[1]}, {"key": "mandatory", "label": headers[2]}, {"key": "description", "label": headers[3]}, {"key": "allowedValues", "label": headers[4]}], "rows": rows}]}],
        "definitions": definitions,
    }


def _app_action_document(name: str, title: str, raw: dict[str, Any]) -> dict[str, Any]:
    headers, source_rows = _intent_table(raw)
    action_refs = []
    definitions = {}
    action_names = []
    full_text = "\n".join(str(page.get("text", "")) for page in raw.get("pages", []))
    text = "\n".join(str(page.get("text", "")) for page in raw.get("pages", []))
    seen_actions: set[str] = set()
    for label, action_type in re.findall(r"^\s*([^\n(]+?)\s*\((org\.rdk\.[^)]+)\)", text, re.MULTILINE):
        if action_type in seen_actions:
            continue
        seen_actions.add(action_type)
        action_names.append(action_type)
        reference = f"app-action-{len(action_refs)}"
        action_refs.append({"label": action_type, "ref": reference})
        definitions[reference] = {"type": "entry", "eyebrow": "App Action", "heading": label.strip(), "overview": f"App action type {action_type}.", "blocks": []}
    action_matches = list(re.finditer(r"([^\n(]+?)\s*\((org\.rdk\.[^)]+)\)", full_text))
    for index, reference in enumerate([f"app-action-{i}" for i in range(len(action_names))]):
        if index >= len(action_matches):
            continue
        start = action_matches[index].end()
        end = action_matches[index + 1].start() if index + 1 < len(action_matches) else len(full_text)
        section = full_text[start:end]
        first_object = section.find("{")
        last_object = section.rfind("}")
        if first_object >= 0 and last_object > first_object:
            definitions[reference]["blocks"].extend([{"type": "heading", "body": "Example"}, {"type": "examples", "blocks": [{"type": "code", "body": section[first_object:last_object + 1].strip(), "variant": "spec-example"}]}])
    for index, action_type in enumerate(action_names):
        start = full_text.find(f'"actionType": "{action_type}"')
        if start < 0:
            continue
        object_start = full_text.rfind("{", 0, start)
        if object_start >= 0:
            start = object_start
        next_start = min([position for position in (full_text.find(f'"actionType": "{next_type}"', start + 1) for next_type in action_names if next_type != action_type) if position >= 0] or [len(full_text)])
        snippet = full_text[start:next_start]
        for example in _json_objects(snippet):
            if f'"actionType": "{action_type}"' in example:
                definitions[f"app-action-{index}"]["blocks"].append({"type": "examples", "blocks": [{"type": "code", "body": example, "variant": "spec-example"}]})
    action_tables: list[dict[str, Any]] = []
    for table in _tables(raw):
        if not table or _clean(table[0][0]) != "Part":
            continue
        rows = []
        for row in table[1:]:
            values = [_clean(value) for value in row]
            if values and values[0]:
                rows.append({"part": values[0], "type": values[1] if len(values) > 1 else "", "mandatory": values[2] if len(values) > 2 else "", "description": values[3] if len(values) > 3 else "", "allowedValues": values[4] if len(values) > 4 else ""})
        if rows:
            action_tables.append(_app_action_table(table))
    table_targets = [None, *[f"app-action-{index}" for index in range(len(action_names))]]
    for index, table in enumerate(action_tables):
        if index >= len(table_targets) or not table_targets[index]:
            continue
        reference = table_targets[index]
        definitions[reference]["blocks"].extend([{"type": "heading", "body": "Definition of action data"}, table])
    for definition in definitions.values():
        data_blocks = [block for block in definition["blocks"] if block.get("type") != "examples"]
        example_blocks = [block for block in definition["blocks"] if block.get("type") == "examples"]
        if example_blocks:
            definition["blocks"] = data_blocks + [{"type": "heading", "body": "Example"}] + example_blocks
        else:
            definition["blocks"] = data_blocks
    rows = []
    for row in source_rows:
        values = [_clean(value) for value in row]
        if values[0] == "actionType" and action_refs:
            values[4] = {"type": "actions", "items": action_refs}
        elif values[0] == "actionData":
            values[4] = "Click an action type above for more details."
        rows.append(dict(zip(("part", "type", "mandatory", "description", "allowedValues"), values)))
    return {
        "schemaVersion": "1.0",
        "hero": {"eyebrow": "Firebolt 9", "title": title, "description": "App Actions available to Firebolt applications.", "status": "Approved"},
        "source": {"label": raw.get("source", name), "href": f"assets/pdf/{raw.get('source', '')}"},
        "blocks": [{"type": "section", "classes": "app-actions-section", "blocks": [{"type": "table", "columns": [{"key": "part", "label": headers[0]}, {"key": "type", "label": headers[1]}, {"key": "mandatory", "label": headers[2]}, {"key": "description", "label": headers[3]}, {"key": "allowedValues", "label": headers[4]}], "rows": rows}]}],
        "definitions": definitions,
    }


def _app_service_document(name: str, title: str, raw: dict[str, Any]) -> dict[str, Any]:
    definitions = {}
    index = 0
    amber_methods = _app_service_amber_methods(raw)
    services = [
        ("Native Player App Service - org.rdk.nativeplayer", "This app service offers functionality to play live IP native channels."),
        ("Parental App Service - org.rdk.parental", "This app service offers PIN and parental control functionality."),
    ]
    sections = []
    service_index = 0
    for table in _tables(raw):
        if not table or "Method" not in _clean(table[0][1] if len(table[0]) > 1 else ""):
            continue
        service_name, service_description = services[min(service_index, len(services) - 1)]
        service_index += 1
        rows = []
        for row in table[1:]:
            if len(row) < 7 or not _clean(row[1]):
                continue
            reference = f"app-service-{index}"
            index += 1
            method = _method_text(row[1])
            version = _clean(row[5])
            row_data = {"methods": method, "version": version, "details": {"type": "actions", "plain": True, "items": [{"label": "View Details", "ref": reference}]}}
            if method in amber_methods:
                row_data["classes"] = "pdf-red-row"
            rows.append(row_data)
            definitions[reference] = {"type": "apiMethod", "eyebrow": "App Service", "module": service_name, "method": method, "version": version, "support": [], "fields": [{"label": "Parameters", "value": _value(row[2], nested=bool(re.search(r"\b(enum|list|object)\b", str(row[2]), re.I))) or "None"}, {"label": "Returns", "value": _value(row[3]) or "None"}, {"label": "Specific errors", "value": _value(row[4], nested=False) or "None"}], "overview": _clean(row[6]), "trailing": []}
        if rows:
            sections.append({"type": "section", "classes": "api-spec-content", "heading": service_name, "blocks": [{"type": "prose", "body": service_description}, {"type": "table", "id": f"app-services-{service_index}", "columns": [{"key": "methods", "label": "Methods", "wrap": "preline"}, {"key": "version", "label": "API version"}, {"key": "details", "label": "View Details"}], "rows": rows}]})
    return {
        "schemaVersion": "1.0",
        "hero": {"eyebrow": "Firebolt 9", "title": title, "description": "App Services available to Firebolt applications.", "status": "Draft"},
        "source": {"label": raw.get("source", name), "href": f"assets/pdf/{raw.get('source', '')}"},
        "blocks": sections,
        "definitions": definitions,
    }


def _table_block(table: list[list[Any]], page: int) -> dict[str, Any]:
    width = max((len(row) for row in table), default=0)
    columns = [{"key": f"column{index}", "label": f"Column {index + 1}"} for index in range(width)]
    rows = [{column["key"]: row[index] if index < len(row) and row[index] is not None else "" for index, column in enumerate(columns)} for row in table]
    return {"type": "table", "id": f"extracted-page-{page}-table", "columns": columns, "rows": rows}


def _document(name: str, title: str, raw: dict[str, Any], page_heading: str) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    for page in raw.get("pages", []):
        page_number = page.get("page", "?")
        page_blocks: list[dict[str, Any]] = []
        text = str(page.get("text", "")).strip()
        if text:
            page_blocks.append({"type": "prose", "body": text})
        for table in page.get("tables", []):
            if table:
                page_blocks.append(_table_block(table, int(page_number) if str(page_number).isdigit() else 0))
        if page_blocks:
            blocks.append({"type": "section", "heading": f"{page_heading} - page {page_number}", "blocks": page_blocks})
    return {
        "schemaVersion": "1.0",
        "hero": {
            "eyebrow": "Firebolt 9",
            "title": title,
            "description": f"Extracted content from {raw.get('source', name)}.",
            "status": "Draft",
        },
        "source": {"label": raw.get("source", name), "href": f"assets/pdf/{raw.get('source', '')}"},
        "blocks": blocks,
        "definitions": {},
    }


def convert_api(name: str, title: str, raw: dict[str, Any]) -> dict[str, Any]:
    return _api_document(name, title, raw)


def convert_intents(name: str, title: str, raw: dict[str, Any]) -> dict[str, Any]:
    return _intent_document(name, title, raw)


def convert_key_codes(name: str, title: str, raw: dict[str, Any]) -> dict[str, Any]:
    return _key_document(name, title, raw)


def convert_app_actions(name: str, title: str, raw: dict[str, Any]) -> dict[str, Any]:
    return _app_action_document(name, title, raw)


def convert_app_services(name: str, title: str, raw: dict[str, Any]) -> dict[str, Any]:
    return _app_service_document(name, title, raw)

def convert_crypto(name: str, title: str, raw: Any) -> dict[str, Any]:
    return _crypto_document(name, title, raw)

CONVERTERS: dict[str, Converter] = {
    "firebolt-api-spec": convert_api,
    "firebolt-intents": convert_intents,
    "firebolt-key-codes": convert_key_codes,
    "firebolt-app-actions": convert_app_actions,
    "firebolt-app-services": convert_app_services,
    "firebolt-crypto": convert_crypto,
}

