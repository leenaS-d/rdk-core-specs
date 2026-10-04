"""RDKE northbound API list generator."""
import json
import re
from io import BytesIO
from html import escape
from build import hero, shell, status_explainer
from pathlib import Path
from PIL import Image
from pypdf import PdfReader
import pdfplumber

ROOT = Path(__file__).resolve().parent

# Row highlight colors used by the Firebolt 9 API Specifications PDF (see its "Key" section):
# green = "Approved - ready for development", red = "Not approved - not ready for development".
API_SPEC_RED = (1.0, 0.92549, 0.92157)
API_SPEC_GREEN = (0.86275, 1.0, 0.9451)

# These two narrow PDF cells split field names and enum values across individual
# syllables, so their extracted lines cannot be reconstructed reliably.
PARAMETER_OVERRIDES = {
    67: """text - string
lang - string - BCP 47 - optional
voice - string - optional
volume - double - optional
rate - double - optional
pitch - double - optional
pii - bool - optional""",
    71: """utteranceId - unsigned
event - enum
- synthesisStarting
- playbackStarting
- paused
- resumed
- completed
- interrupted
- networkFailed
- synthesisFailed
- playbackFailed""",
}


def _dewrap_identifier(value: str) -> str:
    """Join a PDF table cell's hard-wrapped lines back into a single identifier (no inner spaces)."""
    text = "".join(line.strip() for line in str(value or "").splitlines())
    if text == "mediaRenditionChanged":
        return text
    # Method cells pair a property getter with its change event, e.g. "name" + "onNameChanged".
    return re.sub(r"(?<!^)(on[A-Z])", r"\n\1", text, count=1)


def _row_highlight(page, bbox: tuple) -> str | None:
    """Classify a table row's approval color by its strongest vertical overlap with a highlight rect."""
    top, bottom = bbox[1], bbox[3]
    best_color, best_overlap = None, 0.0
    for rect in page.rects:
        color = rect.get("non_stroking_color")
        if color not in (API_SPEC_RED, API_SPEC_GREEN):
            continue
        overlap = max(0.0, min(rect["bottom"], bottom) - max(rect["top"], top))
        if overlap > best_overlap:
            best_color, best_overlap = color, overlap
    if best_color == API_SPEC_RED:
        return "red"
    if best_color == API_SPEC_GREEN:
        return "green"
    return None


# The C++17/JS columns use small green-check / red-cross circle icons rather than text,
# with the C++17 icon always to the left of the JS icon within the same table row.
_MARK_COLUMN_SPLIT_X = 390


def _classify_mark_image(page, image: dict) -> str:
    """Classify a small status icon image as "check" (green) or "cross" (red) by its average color."""
    try:
        with Image.open(BytesIO(image["stream"].get_data())).convert("RGB") as pixels:
            width, height = pixels.size
            center_x, center_y = width // 2, height // 2
            samples = [
                pixels.getpixel((center_x + dx, center_y + dy))
                for dx in range(-2, 3) for dy in range(-2, 3)
                if 0 <= center_x + dx < width and 0 <= center_y + dy < height
            ]
    except OSError:
        try:
            pixels = page.crop((image["x0"], image["top"], image["x1"], image["bottom"])).to_image(resolution=144).original.convert("RGB")
            width, height = pixels.size
            center_x, center_y = width // 2, height // 2
            samples = [
                pixels.getpixel((center_x + dx, center_y + dy))
                for dx in range(-4, 5) for dy in range(-4, 5)
                if 0 <= center_x + dx < width and 0 <= center_y + dy < height
            ]
        except (OSError, ValueError):
            return ""
    red = sum(sample[0] for sample in samples) / len(samples)
    green = sum(sample[1] for sample in samples) / len(samples)
    blue = sum(sample[2] for sample in samples) / len(samples)
    return "check" if green >= red and green >= blue else "cross"


def _row_marks(page, bbox: tuple, marks: list[tuple]) -> tuple[str, str]:
    """Find the C++17/JS status icons overlapping a table row and return their (cpp17, js) marks."""
    top, bottom = bbox[1], bbox[3]
    cpp17 = js = ""
    for mark_top, mark_bottom, column, mark in marks:
        overlap = max(0.0, min(mark_bottom, bottom) - max(mark_top, top))
        if overlap <= 0:
            continue
        if column == "cpp17":
            cpp17 = mark
        else:
            js = mark
    return cpp17, js


def extract_api_spec_methods(pdf_name: str) -> tuple[list[dict], int]:
    """Parse the Module/Method table from the Firebolt 9 API Specifications PDF.

    Rows highlighted red ("Not approved - not ready for development") are dropped; only
    green ("Approved - ready for development") rows are returned. Returns the approved
    entries plus a count of the red entries that were excluded.
    """
    entries: list[dict] = []
    excluded_red = 0
    current: dict | None = None
    existing_marks = {}
    existing_marks = {}
    with pdfplumber.open(ROOT / pdf_name) as pdf:
        for page in pdf.pages:
            marks = [
                (
                    image["top"], image["bottom"],
                    "cpp17" if image["x0"] < _MARK_COLUMN_SPLIT_X else "js",
                    _classify_mark_image(page, image),
                )
                for image in page.images
            ]
            for table in page.find_tables():
                rows = table.extract()
                if not rows or len(rows[0]) != 11:
                    continue
                for row_index, row in enumerate(rows):
                    cells = [cell or "" for cell in row]
                    first = cells[0].strip()
                    if first == "" and cells[1] == "Module":
                        continue
                    if re.match(r"^\d+$", first):
                        bbox = table.rows[row_index].bbox
                        color = _row_highlight(page, bbox)
                        cpp17, js = _row_marks(page, bbox, marks)
                        saved_cpp17, saved_js = existing_marks.get(int(first), ("", ""))
                        cpp17 = cpp17 or saved_cpp17
                        js = js or saved_js
                        current = {"cells": cells, "color": color, "cpp17": cpp17, "js": js}
                        if color == "red":
                            excluded_red += 1
                        else:
                            entries.append(current)
                    elif current is not None:
                        for col_index, cell in enumerate(cells):
                            cell = cell.strip()
                            if not cell:
                                continue
                            previous = current["cells"][col_index]
                            current["cells"][col_index] = f"{previous}\n{cell}" if previous else cell

    methods = []
    for entry in entries:
        cells = entry["cells"]
        method_id = int(cells[0].strip())
        methods.append({
            "id": method_id,
            "component": _dewrap_identifier(cells[1]),
            "name": _dewrap_identifier(cells[2]),
            "parameters": PARAMETER_OVERRIDES.get(method_id, clean_lines(cells[3])),
            "returns": clean_lines(cells[4]),
            "specificErrors": clean_lines(cells[5]),
            "releaseTag": clean_cell(cells[6]),
            "deprecatedReleaseTag": clean_cell(cells[7]),
            "cpp17": entry["cpp17"],
            "js": entry["js"],
            "description": clean_lines(cells[10]),
        })
    return methods, excluded_red


def extract_interpretation_terms(pdf_name: str) -> list[tuple[str, str]]:
    """Parse the page 1 "Interpretation" (Term/Meaning) table used to read the API spec."""
    with pdfplumber.open(ROOT / pdf_name) as pdf:
        for table in pdf.pages[0].find_tables():
            rows = table.extract()
            if rows and [clean_cell(cell) for cell in rows[0][1:3]] == ["Term", "Meaning"]:
                return [(clean_cell(row[1]), clean_cell(row[2])) for row in rows[1:] if (row[1] or "").strip()]
    return []


def extract_types(pdf_name: str) -> list[tuple[str, str]]:
    """Parse the Types table from the Firebolt API specification's first page."""
    with pdfplumber.open(ROOT / pdf_name) as pdf:
        for table in pdf.pages[0].find_tables():
            rows = table.extract()
            if rows and [clean_cell(cell) for cell in rows[0][1:3]] == ["Type", "Definition"]:
                return [(clean_cell(row[1]), clean_cell(row[2])) for row in rows[1:] if (row[1] or "").strip()]
    return []


def extract_error_values(pdf_name: str) -> list[dict]:
    """Parse the "Errors" table (spans pages 1-2) listing generic and specific error values.

    Rows highlighted red ("Not approved - not ready for development") are excluded, matching
    the same convention used for the main Module/Method table.
    """
    rows_out: list[dict] = []
    current_class = ""
    with pdfplumber.open(ROOT / pdf_name) as pdf:
        for page in pdf.pages[:2]:
            for table in page.find_tables():
                rows = table.extract()
                if not rows or len(rows[0]) != 7:
                    continue
                for row_index, row in enumerate(rows):
                    cells = [cell or "" for cell in row]
                    if not any(cell.strip() for cell in cells):
                        continue
                    if clean_cell(cells[1]) == "Class":
                        continue
                    if not re.match(r"^\d+$", cells[0].strip()):
                        continue
                    if cells[1].strip():
                        current_class = clean_cell(cells[1])
                    if _row_highlight(page, table.rows[row_index].bbox) == "red":
                        continue
                    rows_out.append({
                        "class": current_class,
                        "value": clean_cell(cells[2]),
                        "name": clean_cell(cells[3]),
                        "description": clean_cell(cells[4]),
                        "examples": clean_cell(cells[5]),
                        "openIssues": clean_cell(cells[6]),
                    })
    return rows_out


def _mark_badge(mark: str) -> str:
    """Render a method's C++17/JS support as the same check/cross badge style used in the source PDF."""
    if mark == "check":
        return '<span class="api-support-mark supported" role="img" aria-label="Supported">&#10003;</span>'
    if mark == "cross":
        return '<span class="api-support-mark unsupported" role="img" aria-label="Not supported">&#10007;</span>'
    return '<span class="api-support-mark unknown" aria-label="Support unknown">&mdash;</span>'


_FIELD_DECLARATION = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s-\s")
_FIELD_SUBITEM = re.compile(r"^(?:[\[{(\"']|list\b|one\b|true\b|false\b|null\b|\d)", re.IGNORECASE)
_FIELD_BULLET = re.compile(r"^\s*(?:[-*]|\u2022)\s*(.+)$")
_LIST_MARKER = re.compile(r"^(?P<indent>\s*)(?P<marker>[-*]|\u2022|\d+\.)\s+(?P<text>.+)$")
_DESCRIPTION_NUMBERED_ITEM = re.compile(r"^(\d+)\.\s+(.+)$")
_DESCRIPTION_KEYED_ITEM = re.compile(r"^(.+?)\s-\s(.+)$")


def _field_lines(value: str) -> list[str]:
    lines = [line.rstrip() for line in str(value or "").splitlines() if line.strip()]
    repaired: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        previous = repaired[-1] if repaired else ""
        joined = f"{previous}{line}"
        if previous.endswith("-"):
            repaired[-1] = f"{previous} {line}"
        elif previous and not _FIELD_DECLARATION.match(previous) and (len(previous) >= 8 or any(char.isupper() for char in previous[1:])) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s-", joined):
            repaired[-1] = joined
        elif previous and not _FIELD_DECLARATION.match(previous) and line.startswith("-") and not _FIELD_BULLET.match(line):
            repaired[-1] = f"{previous} {line}"
        elif previous and re.search(r"\b(?:list of|list of (?:one|zero)(?: or)?|one or more|zero or more|or more)$", previous, re.IGNORECASE):
            repaired[-1] = f"{previous} {line}"
        elif previous and not _FIELD_DECLARATION.match(line) and line.endswith("-") and re.search(r"-\s[A-Za-z]+$", previous):
            repaired[-1] = f"{previous}{line}"
        else:
            repaired.append(raw_line if _FIELD_BULLET.match(raw_line) else line)
    return repaired


def _list_item(line: str) -> tuple[int, str] | None:
    """Return a marker's nesting level and text, preserving PDF indentation when present."""
    marker = _LIST_MARKER.match(line)
    if not marker:
        return None
    indentation = len(marker.group("indent").expandtabs(2))
    return indentation // 2, marker.group("text")


def _render_nested_list(items: list[tuple[int, str]], class_name: str) -> str:
    """Render marker-delimited items, nesting only when the source indentation increases."""
    def render(index: int, level: int) -> tuple[str, int]:
        rendered = []
        while index < len(items):
            item_level, text = items[index]
            if item_level < level:
                break
            if item_level > level:
                nested, index = render(index, item_level)
                rendered[-1] = rendered[-1][:-5] + nested + "</li>"
                continue
            rendered.append(f"<li>{text}</li>")
            index += 1
        return f'<ul class="{class_name}">{"".join(rendered)}</ul>', index

    return render(0, items[0][0])[0] if items else ""


def _render_field_block(value: str) -> str:
    """Render PDF field declarations as bullets with their value constraints as nested bullets."""
    declarations: list[list[object]] = []
    preamble: list[str] = []
    lines = _field_lines(value)
    index = 0
    while index < len(lines):
        line = lines[index]
        bullet = _list_item(line)
        if _FIELD_DECLARATION.match(line):
            declarations.append([line, []])
        elif bullet and declarations:
            declarations[-1][1].append(bullet)
        elif index + 1 < len(lines) and _FIELD_BULLET.match(lines[index + 1]):
            declarations.append([f"{line} {lines[index + 1]}", []])
            index += 1
        elif declarations:
            details = declarations[-1][1]
            if details:
                level, text = details[-1]
                details[-1] = level, f"{text} {line}"
            else:
                declarations[-1][0] = f"{declarations[-1][0]} {line}"
        else:
            preamble.append(line)
        index += 1
    if not declarations:
        return '<span class="api-detail-text">None</span>'
    rendered = []
    for declaration, details in declarations:
        detail_html = ""
        if details:
            detail_html = _render_nested_list(
                [(level, escape(text)) for level, text in details], "api-detail-sublist"
            )
        rendered.append(f"<li>{escape(declaration)}{detail_html}</li>")
    intro = f'<span class="api-detail-text">{escape(" ".join(preamble))}</span>' if preamble else ""
    return intro + '<ul class="api-detail-list">' + "".join(rendered) + "</ul>"


def _render_description(value: str) -> str:
    """Render description paragraphs and categorized lists without PDF line-wrap artifacts."""
    blocks: list[tuple[str, str, list[tuple[int, str, str]]]] = []
    paragraph = ""
    category = ""
    items: list[tuple[int, str, str]] = []

    def item_parts(line: str) -> tuple[int, str, str] | None:
        numbered = _DESCRIPTION_NUMBERED_ITEM.match(line)
        if numbered:
            return 0, f"{numbered.group(1)}.", numbered.group(2)
        bullet = _list_item(line)
        if bullet:
            level, text = bullet
            return level, "", text
        keyed = _DESCRIPTION_KEYED_ITEM.match(line)
        if keyed:
            return 0, keyed.group(1), keyed.group(2)
        return None

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(("paragraph", paragraph, []))
            paragraph = ""

    def flush_items() -> None:
        nonlocal category, items
        if items:
            blocks.append(("list", category, items))
            category = ""
            items = []

    lines = [line.strip() for line in str(value or "").splitlines() if line.strip()]
    index = 0
    while index < len(lines):
        line = lines[index]
        item = item_parts(line)
        next_item = item_parts(lines[index + 1]) if index + 1 < len(lines) else None
        if not item and next_item and not line.endswith((".", "!", "?", ":")):
            flush_paragraph()
            flush_items()
            category = line
        elif item:
            flush_paragraph()
            items.append(item)
        elif items:
            level, name, description = items[-1]
            items[-1] = level, name, f"{description} {line}"
        else:
            paragraph = f"{paragraph} {line}".strip()
            if line.endswith((".", "!", "?", ":")):
                flush_paragraph()
        index += 1
    flush_items()
    flush_paragraph()

    rendered = []
    for kind, text, block_items in blocks:
        if kind == "paragraph":
            rendered.append(f'<p class="spec-entry-overview">{escape(text)}</p>')
            continue
        list_items = [
            (
                level,
                f"<strong>{escape(name)}</strong> - {escape(description)}"
                if name else escape(description),
            )
            for level, name, description in block_items
        ]
        heading = f'<h3 class="spec-entry-event-category">{escape(text)}</h3>' if text else ""
        rendered.append(f'{heading}{_render_nested_list(list_items, "spec-entry-overview api-detail-list")}')
    return "".join(rendered)


def render_northbound_templates(methods: list[dict]) -> str:
    """Build the modal detail template for each method's parameters, returns, errors and description."""
    templates_html = []
    for method in methods:
        slug = f"api-{method['id']}"
        meta_pills = [f'<span class="pill">API version {escape(method["releaseTag"])}</span>']
        if method["deprecatedReleaseTag"]:
            meta_pills.append(f'<span class="pill warn">To be deprecated (post RDK9): {escape(method["deprecatedReleaseTag"])}</span>')
        templates_html.append(
            f'<template id="tmpl-{slug}"><section class="spec-entry">'
            f'<div class="spec-entry-head"><span class="spec-entry-eyebrow">Module</span><h2>{escape(method["component"])}</h2></div>'
            f'<div class="api-detail-method"><code>{escape(method["name"])}</code></div>'
            f'<div class="api-detail-meta">{"".join(meta_pills)}'
            f'<span class="api-support"><span class="api-support-label">C++17</span>{_mark_badge(method["cpp17"])}</span>'
            f'<span class="api-support"><span class="api-support-label">JS</span>{_mark_badge(method["js"])}</span>'
            '</div>'
            '<dl class="api-detail-fields">'
            f'<div class="api-detail-row"><dt>Parameters</dt><dd>{_render_field_block(method["parameters"])}</dd></div>'
            f'<div class="api-detail-row"><dt>Returns</dt><dd>{_render_field_block(method["returns"])}</dd></div>'
            f'<div class="api-detail-row"><dt>Specific errors</dt><dd>{_render_field_block(method["specificErrors"])}</dd></div>'
            '</dl>'
            f'{_render_description(method["description"])}'
            '</section></template>'
        )
    return "".join(templates_html)


def render_reference_section(terms: list[tuple[str, str]], types: list[tuple[str, str]], errors: list[dict]) -> str:
    """Render compact reference triggers with centered modal tables."""
    interpretation_table = render_spec_table(["Term", "Meaning"], [list(term) for term in terms])
    types_table = render_spec_table(["Type", "Definition"], [list(item) for item in types])
    error_rows = [[error["class"], error["value"], error["name"], error["description"], error["examples"], error["openIssues"]] for error in errors]
    errors_table = render_spec_table(["Class", "Value", "Name", "Description", "Examples", "Open issues"], error_rows, code_column=1)
    references = (
        ("interpretation", "Interpretation", interpretation_table),
        ("types", "Types", types_table),
        ("error-values", "Error values", errors_table),
    )
    triggers = "".join(
        f'<a class="reference-trigger spec-modal-trigger" href="#reference-{slug}" data-modal-target="reference-{slug}">{title}</a>'
        for slug, title, _ in references
    )
    templates = "".join(
        f'<template id="tmpl-reference-{slug}"><section class="spec-entry reference-modal-entry">'
        f'<div class="spec-entry-head"><h2>{title}</h2></div>{table}</section></template>'
        for slug, title, table in references
    )
    return (
        '<div class="api-reference">'
        '<div class="api-reference-title">References</div>'
        f'<div class="reference-actions">{triggers}</div>'
        f'{templates}</div>'
    )


def _render_key_code_table(headers: list[str], rows: list[list[str]], template_prefix: str) -> str:
    visible_headers = headers[:3] + ["View details"]
    rows_html = []
    templates = []
    for index, values in enumerate(rows):
        template_id = f"{template_prefix}-{index}"
        detail_rows = "".join(
            f"<tr><th>{escape(header)}</th><td>{escape(value)}</td></tr>"
            for header, value in zip(headers, values)
        )
        rows_html.append(
            "<tr>"
            + "".join(f"<td>{escape(value)}</td>" for value in values[:3])
            + f'<td><a class="pill allowed-action spec-modal-trigger" href="#{template_id}" data-modal-target="{template_id}">View details</a></td></tr>'
        )
        templates.append(
            f'<template id="{template_id}"><section class="spec-entry"><div class="spec-entry-head">'
            f'<span class="spec-entry-eyebrow">Key code details</span><h2>{escape(values[0])}</h2></div>'
            f'<div class="spec-table-wrap key-code-detail-table"><table class="spec-table"><tbody>{detail_rows}</tbody></table></div>'
            "</section></template>"
        )
    header_html = "".join(f"<th>{escape(header)}</th>" for header in visible_headers)
    return (
        f'<div class="key-codes-table"><div class="spec-table-wrap"><table class="spec-table"><thead><tr>{header_html}</tr></thead>'
        f'<tbody>{"".join(rows_html)}</tbody></table></div></div>{"".join(templates)}'
    )


def build_northbound() -> None:
    pdf_name = "Firebolt 9 API Specifications.pdf"
    methods, excluded_red = extract_api_spec_methods(pdf_name)
    modules = sorted({method["component"] for method in methods})
    deprecated_count = sum(1 for method in methods if method["deprecatedReleaseTag"])
    row_data = [
        [
            method["component"],
            method["name"],
            method["releaseTag"],
            method["deprecatedReleaseTag"],
            f"api-{method['id']}",
        ]
        for method in methods
    ]

    body = hero(
        "Firebolt 9",
        "Firebolt Core API Specification",
        "Standardized APIs the middleware exposes upward to the application layer, giving apps consistent access to device capabilities via Thunder and Firebolt.",
        status="Draft",
    )
    notice = '<strong>Note</strong><br>This page contains an evolving list of Firebolt Core API components for RDK9.'
    body += (
        '<section class="section">'
        f'<div class="notice" style="margin:0 0 24px">{notice}</div>'
        '<div class="toolbar northbound-toolbar"><input id="northbound-search" type="search" placeholder="Search Northbound APIs" aria-label="Search Northbound APIs">'
        '<select id="northbound-module"><option value="">All modules</option>'
        f'{"".join(f"<option>{escape(module)}</option>" for module in modules)}</select></div>'
        f'{render_reference_section(extract_interpretation_terms(pdf_name), extract_types(pdf_name), extract_error_values(pdf_name))}'
        '<div class="table-wrap" style="margin-top:24px"><table><thead><tr>'
        '<th>Module</th><th>Method</th><th>Version</th><th>To be deprecated (post RDK9)</th><th>Details</th>'
        '</tr></thead><tbody id="northbound-rows"></tbody></table></div>'
        '</section>'
        f'{render_northbound_templates(methods)}'
        '<div class="spec-modal" id="spec-modal" aria-hidden="true">'
        '<div class="spec-modal-backdrop" data-modal-close></div>'
        '<div class="spec-modal-dialog" role="dialog" aria-modal="true">'
        '<button type="button" class="spec-modal-close" data-modal-close aria-label="Close">&times;</button>'
        '<div class="spec-modal-body" id="spec-modal-body"></div>'
        '</div></div>'
    )
    rows = json.dumps(row_data, ensure_ascii=True)
    body += (
        f"<script>const DATA={rows};"
        "const esc=s=>{const d=document.createElement('div');d.textContent=s;return d.innerHTML};"
        "const search=document.querySelector('#northbound-search'),moduleFilter=document.querySelector('#northbound-module');"
        "function render(){"
        "const q=search.value.toLowerCase();"
        "const rows=DATA.filter(c=>(!q||c.join(' ').toLowerCase().includes(q))&&(!moduleFilter.value||c[0]===moduleFilter.value));"
        "document.querySelector('#northbound-rows').innerHTML=rows.length?rows.map(c=>"
        "`<tr><td>${esc(c[0])}</td><td style=\"white-space:pre-line\">${esc(c[1])}</td>"
        "<td><span class=\"pill\">${esc(c[2])}</span></td>"
        "<td>${c[3]?`<span class=\"pill warn\">${esc(c[3])}</span>`:'<span class=\"lede\">&mdash;</span>'}</td>"
        "<td><a class=\"pill spec-modal-trigger\" href=\"#${c[4]}\" data-modal-target=\"${c[4]}\">View details</a></td></tr>`"
        ").join(''):'<tr><td class=\"empty\" colspan=\"5\">No matching records.</td></tr>'"
        "}"
        "[search,moduleFilter].forEach(e=>e.addEventListener('input',render));render()</script>"
    )
    body += SPEC_MODAL_SCRIPT
    footer = f'Source file: <a href="{escape(pdf_name)}" target="_blank" rel="noopener">{escape(pdf_name)}</a>'
    (ROOT / "northbound-apis.html").write_text(shell("Firebolt Core API Specification | RDKE", "northbound", body, footer), encoding="utf-8")

    build_app_actions()
    build_intents()
    build_key_codes()


def split_json_blocks(value: str) -> list[str]:
    blocks = []
    depth = 0
    start = None
    in_string = False
    escaped = False
    for index, char in enumerate(value):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append(value[start:index + 1])
                start = None
    return blocks


def clean_cell(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def clean_lines(value: object) -> str:
    """Normalize whitespace within each physical line of a cell while keeping line breaks intact."""
    lines = (re.sub(r"\s+", " ", line).strip() for line in str(value or "").splitlines())
    return "\n".join(line for line in lines if line)


def clean_identifier(value: object) -> str:
    """Rejoin a field name PDF-wrapped mid-word (e.g. "fireboltMeth\nod") without adding a space."""
    return re.sub(r"\s+", "", str(value or "")).strip()


def _catalog_status_bar() -> str:
    """The same "Catalog status" badge + legend used on the Firebolt API Spec page, for consistency."""
    status_badge = '<span style="display:inline-flex;align-items:center;padding:9px 14px;border:1px solid #edcf7a;border-radius:5px;background:#fff4d8;color:#8a5a00;font:700 .75rem/1 JetBrains Mono,monospace;letter-spacing:.04em"><span style="color:#9a731f;font-weight:600;margin-right:6px">Catalog status:</span> Draft</span>'
    return (
        '<section class="section" style="padding-bottom:0">'
        f'<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">{status_badge}{status_explainer()}</div>'
        '</section>'
    )


def render_spec_table(headers: list[str], rows: list[list[str]], code_column: int = 0, raw_cells: set[tuple[int, int]] | None = None, nested: bool = False) -> str:
    raw_cells = raw_cells or set()
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body_rows = []
    for row_index, row in enumerate(rows):
        cells = []
        for col_index, cell in enumerate(row):
            if (row_index, col_index) in raw_cells:
                cells.append(f"<td>{cell}</td>")
            elif col_index == code_column:
                cells.append(f"<td><code>{escape(cell)}</code></td>")
            else:
                cells.append(f"<td>{escape(cell)}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    wrap_class = "spec-table-wrap nested" if nested else "spec-table-wrap"
    return f'<div class="{wrap_class}"><table class="spec-table"><thead><tr>{header_html}</tr></thead><tbody>{"".join(body_rows)}</tbody></table></div>'

def render_spec_toc(groups: list[tuple[str, str]]) -> str:
    groups_html = "".join(
        f'<div class="spec-toc-group"><span class="spec-toc-label">{escape(label)}</span>{links_html}</div>'
        for label, links_html in groups
    )
    return (
        '<nav class="spec-toc">'
        '<div class="spec-toc-head"><span class="spec-toc-title">Reference</span>'
        '<button type="button" class="spec-toc-toggle" aria-label="Collapse reference panel" aria-expanded="true" title="Collapse reference panel">&#10094;</button></div>'
        f'<div class="spec-toc-body">{groups_html}</div>'
        '</nav>'
    )


SPEC_TOC_SCRIPT = (
    '<script>document.querySelectorAll(".spec-toc-toggle").forEach(function(btn){'
    'btn.addEventListener("click",function(){'
    'var layout=btn.closest(".spec-layout");'
    'var collapsed=layout.classList.toggle("toc-collapsed");'
    'btn.setAttribute("aria-expanded",String(!collapsed));'
    'btn.title=collapsed?"Expand reference panel":"Collapse reference panel"'
    '})})</script>'
)


APP_ACTIONS_MODAL_SCRIPT = SPEC_MODAL_SCRIPT = (
    '<script>(function(){'
    'var modal=document.getElementById("spec-modal");'
    'if(!modal)return;'
    'var body=document.getElementById("spec-modal-body");'
    'function openModal(id){'
    'var tmpl=document.getElementById("tmpl-"+id);'
    'if(!tmpl)return;'
    'body.innerHTML="";'
    'body.appendChild(tmpl.content.cloneNode(true));'
    'modal.classList.add("open");'
    'modal.setAttribute("aria-hidden","false");'
    'document.body.style.overflow="hidden"'
    '}'
    'function closeModal(){'
    'modal.classList.remove("open");'
    'modal.setAttribute("aria-hidden","true");'
    'document.body.style.overflow=""'
    '}'
    'document.addEventListener("click",function(e){'
    'var el=e.target.closest(".spec-modal-trigger");'
    'if(!el)return;'
    'e.preventDefault();'
    'openModal(el.getAttribute("data-modal-target"))'
    '});'
    'modal.querySelectorAll("[data-modal-close]").forEach(function(el){'
    'el.addEventListener("click",closeModal)'
    '});'
    'document.addEventListener("keydown",function(e){'
    'if(e.key==="Escape")closeModal()'
    '})'
    '})()</script>'
)


def build_app_actions() -> None:
    pdf_name = "Firebolt 9 App Actions.pdf"
    action_types = (
        ("Launch App", "org.rdk.app.launch"),
        ("Send App Metrics", "org.rdk.app.metrics.send"),
        ("Send App WatchHistory", "org.rdk.app.watchhistory.send"),
        ("Send DAB Request", "org.rdk.dab.request"),
        ("Set App API Token", "org.rdk.app.apitoken.set"),
        ("Set App Identifier", "org.rdk.app.identifier.set"),
    )
    text = "\n".join(page.extract_text() or "" for page in PdfReader(ROOT / pdf_name).pages)
    text = text.replace("Set App Identifier ( )org.rdk.app.identifier.set", "Set App Identifier (org.rdk.app.identifier.set)")

    with pdfplumber.open(ROOT / pdf_name) as pdf:
        page_tables = [page.extract_tables() for page in pdf.pages]

    headers = ["Part", "Type", "Mandatory", "Description", "Allowed values"]

    def data_rows(table: list, columns: slice = slice(0, 5)) -> list[list[str]]:
        rows = []
        for row in table[1:]:
            sliced = [clean_cell(cell) for cell in row[columns]]
            if sliced:
                sliced[0] = clean_identifier(row[columns][0])
            if sliced[0]:
                rows.append(sliced)
        return rows

    format_rows = data_rows(page_tables[0][1])
    action_type_pills = "".join(
        f'<a class="pill allowed-action spec-modal-trigger" href="#app-action-{escape(action_type)}" '
        f'data-modal-target="app-action-{escape(action_type)}" title="Open {escape(name)}">{escape(action_type)}</a>'
        for name, action_type in action_types
    )
    format_raw_cells = set()
    for row_index, row in enumerate(format_rows):
        if row[0] == "actionType":
            row[4] = f'<div class="allowed-actions">{action_type_pills}</div>'
            format_raw_cells.add((row_index, 4))
        elif row[0] == "actionData":
            # The PDF says "See below", but per-action fields now open in a modal rather than appearing further down the page.
            row[4] = "Depends on actionType — click a value above to view its fields"
    format_table = render_spec_table(headers, format_rows, raw_cells=format_raw_cells)

    # The "payload" field of Send App Metrics nests its own 4-column table of Firebolt-defined fields,
    # extracted from the same physical table (columns 4-7) as the main actionData table (columns 0-3).
    metrics_table_raw = page_tables[1][0]
    metrics_main_rows = data_rows(metrics_table_raw)
    payload_rows = [
        [clean_identifier(row[4])] + [clean_cell(cell) for cell in row[5:8]]
        for row in metrics_table_raw[1:]
        if not clean_cell(row[0]) and clean_cell(row[4])
    ]
    payload_table = render_spec_table(["Part", "Type", "Mandatory", "Description"], payload_rows, nested=True)
    payload_row_index = next(index for index, row in enumerate(metrics_main_rows) if row[0] == "payload")
    metrics_main_rows[payload_row_index][4] = f'<details class="spec-details"><summary>payload fields</summary>{payload_table}</details>'

    action_tables = {
        "org.rdk.app.launch": render_spec_table(headers, data_rows(page_tables[0][2])),
        "org.rdk.app.metrics.send": render_spec_table(headers, metrics_main_rows, raw_cells={(payload_row_index, 4)}),
        "org.rdk.app.watchhistory.send": render_spec_table(headers, data_rows(page_tables[2][0])),
        "org.rdk.dab.request": render_spec_table(headers, data_rows(page_tables[2][1])),
        "org.rdk.app.apitoken.set": render_spec_table(headers, data_rows(page_tables[3][0])),
        "org.rdk.app.identifier.set": render_spec_table(headers, data_rows(page_tables[3][1])),
    }

    sections = []
    for index, (name, action_type) in enumerate(action_types):
        marker = f"{name} ({action_type})"
        start = text.find(marker, text.find(marker) + len(marker))
        next_starts = []
        for next_name, next_type in action_types[index + 1:]:
            next_marker = f"{next_name} ({next_type})"
            next_start = text.find(next_marker, text.find(next_marker) + len(next_marker))
            if next_start >= 0:
                next_starts.append(next_start)
        section = text[start:min(next_starts) if next_starts else len(text)].strip()
        sections.append((name, action_type, section))

    entries = []
    for name, action_type, section in sections:
        heading = f"{name} ({action_type})"
        content = section[len(heading):].strip()
        data_marker = re.search(r"\nFormat of actionData\n", content)
        overview = content[:data_marker.start()].strip() if data_marker else content
        rest = content[data_marker.end():] if data_marker else ""
        example_match = re.search(r"\nExample\n", rest)
        examples = split_json_blocks(rest[example_match.end():]) if example_match else []
        table_markup = action_tables.get(action_type, '<p class="lede">No parameters are required for this action.</p>')
        example_markup = "".join(f'<pre class="spec-example">{escape(block)}</pre>' for block in examples)
        entries.append(
            f'<template id="tmpl-app-action-{escape(action_type)}"><section class="spec-entry">'
            f'<div class="spec-entry-head"><span class="spec-entry-eyebrow">App action type</span><h2>{escape(heading)}</h2></div>'
            f'<p class="spec-entry-overview">{escape(overview)}</p>'
            f'<h3>Format of actionData</h3>{table_markup}'
            f'<h3>Example</h3>{example_markup or "<p class=\"lede\">No example was included in the source PDF.</p>"}'
            f'</section></template>'
        )

    body = hero(
        "Firebolt 9",
        "Firebolt App Actions Specification",
        "App actions exposed by the RDK9 video platform for application-driven device and content experiences.",
        status="Approved",
    )
    body += (
        '<section class="section spec-document" style="padding-top:34px">'
        '<section class="spec-intro" id="format">'
        '<h2>App action JSON Format</h2>'
        '<p>All app actions follow the following format.</p>'
        f'{format_table}</section>'
        '</section>'
        f'{"".join(entries)}'
        '<div class="spec-modal" id="spec-modal" aria-hidden="true">'
        '<div class="spec-modal-backdrop" data-modal-close></div>'
        '<div class="spec-modal-dialog" role="dialog" aria-modal="true">'
        '<button type="button" class="spec-modal-close" data-modal-close aria-label="Close">&times;</button>'
        '<div class="spec-modal-body" id="spec-modal-body"></div>'
        '</div></div>'
    )
    body += SPEC_MODAL_SCRIPT
    footer = f'Source file: <a href="{escape(pdf_name)}" target="_blank" rel="noopener">{escape(pdf_name)}</a>'
    (ROOT / "firebolt-app-actions.html").write_text(shell("Firebolt App Actions Specification | RDKE", "northbound", body, footer), encoding="utf-8")


def build_intents() -> None:
    pdf_name = "Firebolt 9 Intents Specification.pdf"
    action_types = (
        "Home action type", "Launch action type", "Pre-load action type", "Entity action type",
        "Playback action type", "Search action type", "Section action type", "Tune action type",
        "Play-entity action type", "Play-query action type", "Previous action type", "Next action type",
        "Repeat action type", "Shuffle action type", "Skip-ad action type", "Skip-recap action type",
        "Skip-intro action type",
    )
    text = "\n".join(page.extract_text() or "" for page in PdfReader(ROOT / pdf_name).pages)
    action_starts = []
    for action in action_types:
        marker = action + "\n"
        first = text.find(marker)
        second = text.find(marker, first + len(marker))
        action_starts.append(second)
    action_sections = []
    for index, start in enumerate(action_starts):
        end = action_starts[index + 1] if index + 1 < len(action_starts) else len(text)
        action_sections.append((action_types[index], text[start:end].strip()))
    constituent_rows = [
        ("action", "string", "Yes", "A string specifying the implicit action being requested to be performed", "'home' 'launch' 'pre-load' 'entity' 'playback' 'search' 'section' 'tune' 'play-entity' 'play-query' 'previous' 'next' 'repeat' 'shuffle' 'skip-ad' 'skip-recap' 'skip-intro'"),
        ("data", "object", "No", "An optional object that contains data to be used by the application in order to fulfil the action", "Depends on action — click a value above to view its fields"),
        ("context", "object", "Yes", "An object defining the source of the intent and optionally properties of that source", "Name Type Mandatory Allowed values Description"),
    ]
    context_rows = (
        ("source", "string", "Yes", "Any", 'An undefined string indicating the source of the intent eg "voice"'),
        ("agePolicy", "string", "No", "'app: child' 'app: teen' 'app: adult'", "An optional string indicating an age group that the intent is targeting"),
    )
    context_html = "".join(
        f"<tr><td><code>{escape(name)}</code></td><td>{escape(value_type)}</td><td>{escape(mandatory)}</td><td>{escape(allowed)}</td><td>{escape(description)}</td></tr>"
        for name, value_type, mandatory, allowed, description in context_rows
    )
    context_table = (
        '<div class="spec-table-wrap"><table class="spec-table"><thead><tr><th>Name</th>'
        f'<th>Type</th><th>Mandatory</th><th>Allowed values</th><th>Description</th></tr></thead><tbody>{context_html}</tbody></table></div>'
    )
    action_values = "".join(
        f'<a class="pill allowed-action spec-modal-trigger" href="#intent-{escape(action.removesuffix(" action type").lower())}" '
        f'data-modal-target="intent-{escape(action.removesuffix(" action type").lower())}" title="Open {escape(action)}">{escape(action.removesuffix(" action type").lower())}</a>'
        for action in action_types
    )
    action_values = f'<div class="allowed-actions">{action_values}</div>'
    constituent_rows[0] = (*constituent_rows[0][:4], action_values)
    constituent_rows[2] = (*constituent_rows[2][:4], f'<details class="spec-details"><summary>Context fields</summary>{context_table}</details>')
    constituent_html_rows = []
    for part, value_type, mandatory, description, allowed in constituent_rows:
        base = f"<tr><td><code>{escape(part)}</code></td><td>{escape(value_type)}</td><td>{escape(mandatory)}</td><td>{escape(description)}</td>"
        if part == "action":
            constituent_html_rows.append(f'{base}<td rowspan="2">{allowed}</td></tr>')
        elif part == "data":
            constituent_html_rows.append(f"{base}</tr>")
        else:
            constituent_html_rows.append(f"{base}<td>{allowed}</td></tr>")
    constituent_html = "".join(constituent_html_rows)
    media_rows = (
        ("entityId", "string", "Yes", "Any", "The identifier of the entity, in the target App's scope."),
        ("assetId", "string", "No", "Any", "The identifier of the asset, in the target App's scope."),
        ("seasonId", "string", "No", "Any", "The identifier of the season, in the target App's scope."),
        ("seriesId", "string", "No", "Any", "The identifier of the series, in the target App's scope."),
        ("appContentData", "string", "No", "Any", "Any extra information required by the app to play the asset, in the target App's scope."),
        ("programType", "string", "No", "Any", "An optional indicator of the type of the programme eg 'movie'"),
        ("entityType", "string", "No", "program", "An indicator of the entity type"),
    )
    structured_definitions = {
        "Launch action type": (
            {"name": "dialPayload", "type": "URL encoded string", "mandatory": "No", "allowed": "Any", "description": "The optional DIAL payload"},
            {"name": "additionalDataUrl", "type": "URL encoded string", "mandatory": "No", "allowed": "Any", "description": "The optional DIAL URL which allows the first screen application to POST data back to the second screen application"},
        ),
        "Entity action type": tuple(
            {"name": name, "type": value_type, "mandatory": mandatory, "allowed": allowed, "description": description}
            for name, value_type, mandatory, allowed, description in (
                media_rows[:4] + (media_rows[4][0:4] + ("Any extra information required to load the entity page, in the target App's scope.",),) + media_rows[5:]
            )
        ),
        "Playback action type": tuple(
            {"name": name, "type": value_type, "mandatory": mandatory, "allowed": allowed, "description": description}
            for name, value_type, mandatory, allowed, description in media_rows
        ),
        "Search action type": (
            {"name": "query", "type": "string", "mandatory": "Yes", "allowed": "Any", "description": "The query string to be seeded in the search box"},
        ),
        "Section action type": (
            {"name": "sectionName", "type": "string", "mandatory": "Yes", "allowed": "Any", "description": "The section name, in the target App's scope."},
            {"name": "appContentData", "type": "string", "mandatory": "No", "allowed": "Any", "description": "Additional information for the app to present the correct content"},
        ),
        "Tune action type": (
            {"name": "entity", "type": "object", "mandatory": "Yes", "allowed": "", "description": "", "children": (
                {"name": "entityType", "type": "string", "mandatory": "Yes", "allowed": "'channel'", "description": ""},
                {"name": "channelType", "type": "string", "mandatory": "Yes", "allowed": "'streaming' 'overTheAir'", "description": ""},
                {"name": "entityId", "type": "string", "mandatory": "Yes", "allowed": "Any", "description": "ID of the channel, in the target App's scope."},
                {"name": "appContentData", "type": "string", "mandatory": "No", "allowed": "Any", "description": ""},
            )},
            {"name": "options", "type": "object", "mandatory": "No", "allowed": "", "description": "", "children": (
                {"name": "assetId", "type": "string", "mandatory": "No", "allowed": "Any", "description": "The ID of a specific 'listing', as scoped by the target App's ID-space, which the App should begin playback from."},
                {"name": "restartCurrentProgram", "type": "boolean", "mandatory": "No", "allowed": "true false", "description": "Denotes that the App should start playback at the most recent program boundary, rather than 'live.'"},
                {"name": "time", "type": "string", "mandatory": "No", "allowed": "ISO 8601 Date/Time", "description": "ISO 8601 Date/Time where the App should begin playback from."},
            )},
        ),
        "Play-entity action type": (
            {"name": "entity", "type": "object", "mandatory": "Yes", "allowed": "", "description": "", "children": (
                {"name": "entityType", "type": "string", "mandatory": "Yes", "allowed": "'playlist'", "description": ""},
                {"name": "entityId", "type": "string", "mandatory": "Yes", "allowed": "Any", "description": "ID of the playlist, in the target App's scope."},
            )},
            {"name": "options", "type": "object", "mandatory": "No", "allowed": "", "description": "", "children": (
                {"name": "playFirstId", "type": "string", "mandatory": "No", "allowed": "Any", "description": "The Id of the asset in the playlist to play first, in the target App's scope."},
                {"name": "playFirstTrack", "type": "number", "mandatory": "No", "allowed": "Any", "description": "The track number in the playlist to play first"},
            )},
        ),
        "Play-query action type": (
            {"name": "query", "type": "string", "mandatory": "Yes", "allowed": "Any", "description": "The query to be used to select the content to be played"},
            {"name": "options", "type": "object", "mandatory": "No", "allowed": "", "description": "", "children": (
                {"name": "programTypes", "type": "string array", "mandatory": "No", "allowed": "", "description": ""},
                {"name": "musicTypes", "type": "string array", "mandatory": "No", "allowed": "", "description": ""},
            )},
        ),
    }

    def render_definition_rows(rows: tuple) -> str:
        rows_html = ""
        for row in rows:
            children = row.get("children")
            if children:
                nested_table = render_definition_table(children)
                allowed_cell = f'<details class="spec-details"><summary>{escape(row["name"])} fields</summary>{nested_table}</details>'
                rows_html += (
                    f"<tr><td><code>{escape(row['name'])}</code></td><td>{escape(row['type'])}</td>"
                    f"<td>{escape(row['mandatory'])}</td><td>{allowed_cell}</td><td>{escape(row['description'])}</td></tr>"
                )
            else:
                rows_html += (
                    f"<tr><td><code>{escape(row['name'])}</code></td><td>{escape(row['type'])}</td>"
                    f"<td>{escape(row['mandatory'])}</td><td>{escape(row['allowed'])}</td><td>{escape(row['description'])}</td></tr>"
                )
        return rows_html

    def render_definition_table(rows: tuple) -> str:
        body_html = render_definition_rows(rows)
        return (
            '<div class="spec-table-wrap"><table class="spec-table"><thead><tr><th>Name</th>'
            f'<th>Type</th><th>Mandatory</th><th>Allowed values</th><th>Description</th></tr></thead><tbody>{body_html}</tbody></table></div>'
        )

    def split_json_blocks(text: str) -> list:
        blocks = []
        depth = 0
        start = None
        in_string = False
        escaped = False
        for index, char in enumerate(text):
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
                continue
            if char == "{":
                if depth == 0:
                    start = index
                depth += 1
            elif char == "}":
                if depth > 0:
                    depth -= 1
                    if depth == 0 and start is not None:
                        blocks.append(text[start:index + 1])
                        start = None
        return blocks

    action_entries = ""
    for action, content in action_sections:
        detail_text = content[len(action):].strip()
        definition_marker = "Definition of data object"
        overview, definition_and_example = detail_text.split(definition_marker, 1)
        example_match = re.search(r"\n(Examples?)\n", definition_and_example)
        if example_match:
            definition = definition_and_example[:example_match.start()].strip()
            example_heading = example_match.group(1)
            example_blocks = split_json_blocks(definition_and_example[example_match.end():])
        else:
            definition = definition_and_example.strip()
            example_heading = "Example"
            example_blocks = []
        definition_markup = f'<pre class="spec-definition-text">{escape(definition)}</pre>'
        table_rows = structured_definitions.get(action)
        if table_rows:
            definition_markup = render_definition_table(table_rows)
        examples_markup = "".join(f'<pre class="spec-example">{escape(block)}</pre>' for block in example_blocks)
        slug = escape(action.removesuffix(" action type").lower())
        action_entries += (
            f'<template id="tmpl-intent-{slug}"><section class="spec-entry">'
            f'<div class="spec-entry-head"><span class="spec-entry-eyebrow">Intent action</span><h2>{escape(action)}</h2></div>'
            f'<p class="spec-entry-overview">{escape(overview.strip())}</p>'
            f'<h3>Definition of data object</h3>{definition_markup}'
            f'<h3>{escape(example_heading)}</h3>{examples_markup}'
            f'</section></template>'
        )

    example = '''{
  "action": "playback",
  "data": {
    "entityId": "ABC123"
  },
  "context": {
    "source": "top_10_this_week",
    "agePolicy": "app:child"
  }
}'''
    body = hero(
        "Firebolt 9",
        "Firebolt Intents Specification",
        "Intent definitions for applications to request device and content experiences through the RDK9 video platform.",
        status="Approved",
    )
    body += (
        '<section class="section spec-document" style="padding-top:34px">'
        '<section class="spec-intro" id="overview">'
        '<p>An Intent is a message object sent to an application requesting a specific action. This may occur as part of the launch of the application or when it is already loaded. The application shall treat the receipt of an intent as an explicit request to carry out the intent and immediately action it, irrespective of what the application is currently doing. The only exception to this if the application is carrying out some process that can not be interrupted eg processing a payment.</p>'
        '<p>An application may support multiple intent action types or none, however if an application receives an intent that it does not support, or one that does not contain enough data for an application to fulfil it, it shall ignore it and not present any error to the user.</p>'
        '</section>'
        f'<section class="spec-intro" id="constituent-parts"><h2>Constituent parts of an intent</h2>'
        f'<div class="spec-table-wrap"><table class="spec-table"><thead><tr><th>Part</th><th>Type</th><th>Mandatory</th><th>Description</th><th>Allowed values</th></tr></thead><tbody>{constituent_html}</tbody></table></div>'
        f'<h3>Example</h3><pre class="spec-example">{escape(example)}</pre>'
        '</section>'
        '</section>'
        f'{action_entries}'
        '<div class="spec-modal" id="spec-modal" aria-hidden="true">'
        '<div class="spec-modal-backdrop" data-modal-close></div>'
        '<div class="spec-modal-dialog" role="dialog" aria-modal="true">'
        '<button type="button" class="spec-modal-close" data-modal-close aria-label="Close">&times;</button>'
        '<div class="spec-modal-body" id="spec-modal-body"></div>'
        '</div></div>'
    )
    body += SPEC_MODAL_SCRIPT
    footer = f'Source file: <a href="{pdf_name}" target="_blank" rel="noopener">{pdf_name}</a>'
    (ROOT / "firebolt-intents.html").write_text(shell("Firebolt Intents Specification | RDKE", "northbound", body, footer), encoding="utf-8")

def build_key_codes() -> None:
    pdf_name = "Firebolt 9 Key Codes Specification.pdf"
    text = "\n".join(page.extract_text() or "" for page in PdfReader(ROOT / pdf_name).pages)
    summary_match = re.search(r"Summary\n(.*?)\nDefinition\n", text, re.DOTALL)
    summary = clean_cell(summary_match.group(1)) if summary_match else ""
    note_match = re.search(r"(All Linux Function key codes.*)$", text.strip())
    closing_note = clean_cell(note_match.group(1)) if note_match else ""

    with pdfplumber.open(ROOT / pdf_name) as pdf:
        all_rows = []
        for page in pdf.pages:
            for table in page.extract_tables():
                if len(table[0]) >= 8:
                    all_rows.extend(table)

    headers = [clean_cell(cell) for cell in all_rows[0]]
    standard_rows, partner_rows, partner_intro = [], [], ""
    in_partner = False

    def clean_linux_key_codes(value: object) -> str:
        """Rejoin PDF-wrapped key-code names while retaining multiple distinct key codes."""
        codes: list[str] = []
        for line in str(value or "").splitlines():
            item = clean_cell(line)
            if not item:
                continue
            if item.startswith("KEY_"):
                codes.append(item)
            elif codes:
                codes[-1] += item
            else:
                codes.append(item)
        return " ".join(codes)

    for row in all_rows[1:]:
        if not any(clean_cell(cell) for cell in row):
            continue
        raw_first = str(row[0] or "")
        if raw_first.startswith("Partner Buttons"):
            in_partner = True
            _, _, body_part = raw_first.partition("\n")
            partner_intro = clean_cell(body_part)
            continue
        cleaned_row = [clean_cell(cell) for cell in row]
        cleaned_row[2] = clean_linux_key_codes(row[2])
        (partner_rows if in_partner else standard_rows).append(cleaned_row)

    standard_table = _render_key_code_table(headers, standard_rows, "standard-key")
    partner_table = _render_key_code_table(headers, partner_rows, "partner-key")

    body = hero(
        "Firebolt 9",
        "Firebolt Key Codes Specification",
        "Definition of the Key Codes made available to Firebolt Apps on the RDK9 video platform.",
        status="Approved",
    )
    body += (
        '<section class="section spec-document" style="padding-top:34px">'
        f'<section class="spec-intro" id="standard-keys"><h2>Standard RCU keys</h2>{standard_table}</section>'
        f'<section class="spec-intro" id="partner-buttons"><h2>Partner buttons</h2>'
        f'<p>{escape(partner_intro)}</p>{partner_table}'
        f'<p class="lede" style="margin-top:16px">{escape(closing_note)}</p>'
        '</section>'
        '<div class="spec-modal" id="spec-modal" aria-hidden="true"><div class="spec-modal-backdrop" data-modal-close></div><div class="spec-modal-dialog" role="dialog" aria-modal="true"><button type="button" class="spec-modal-close" data-modal-close aria-label="Close">&times;</button><div class="spec-modal-body" id="spec-modal-body"></div></div></div>'
        '<script>(function(){const modal=document.getElementById("spec-modal"),body=document.getElementById("spec-modal-body");if(!modal)return;function closeModal(){modal.classList.remove("open");modal.setAttribute("aria-hidden","true");document.body.style.overflow=""}document.addEventListener("click",event=>{const trigger=event.target.closest(".spec-modal-trigger");if(!trigger)return;event.preventDefault();const template=document.getElementById(trigger.dataset.modalTarget);if(!template)return;body.innerHTML="";body.appendChild(template.content.cloneNode(true));modal.classList.add("open");modal.setAttribute("aria-hidden","false");document.body.style.overflow="hidden"});modal.querySelectorAll("[data-modal-close]").forEach(element=>element.addEventListener("click",closeModal));document.addEventListener("keydown",event=>{if(event.key==="Escape")closeModal()})})()</script>'
        '</section>'
    )
    footer = f'Source file: <a href="{escape(pdf_name)}" target="_blank" rel="noopener">{escape(pdf_name)}</a>'
    (ROOT / "firebolt-key-codes.html").write_text(shell("Firebolt Key Codes Specification | RDKE", "northbound", body, footer), encoding="utf-8")


if __name__ == "__main__":
    build_northbound()

