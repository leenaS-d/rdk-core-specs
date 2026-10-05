"""RDK8 northbound API and Firebolt document generators."""
import json
import re
from html import escape
from build import build_api
from import_apis import convert_excel_to_json
from pathlib import Path
from pypdf import PdfReader
import pdfplumber

ROOT = Path(__file__).resolve().parent


FIREBOLT_DOCUMENTS = (
    ("Firebolt 8 JSON-RPC spec.pdf", "firebolt-json-rpc.html", "Firebolt 8 JSON-RPC Specification", "Published"),
)
FIREBOLT_DOCUMENT_DESCRIPTIONS = {
    "firebolt-json-rpc.html": "The Firebolt JSON-RPC specification defines the request and response protocol used by RDK8 applications and platform services.",
    "firebolt-intents.html": "Intent definitions for applications to request device and content experiences through the RDK8 video platform.",
    "firebolt-key-codes.html": "Definition of the Key Codes made available to Firebolt Apps on the RDK8 video platform.",
}
API_SPEC_RED = (1.0, 0.92549, 0.92157)
API_SPEC_GREEN = (0.86275, 1.0, 0.9451)
DOCUMENT_TABLE_LAYOUTS = {
    "Firebolt 8 Intent Spec.pdf": (
        "Constituent parts of an intent",
        ("Part", "Type", "Mandatory", "Description", "Allowed values"),
    ),
}

PARAMETER_OVERRIDES = {
    "watched": """entityId - string
progress - double - optional
completed - bool - optional
watchedOn - ISO 8601 date and time in UTC - optional
agePolicy - string - optional""",
    "close": """type - enum
- deactivate
- unload
- killReload
- killReactivate""",
    "onStateChanged": """change - list of one lifecycle state change
oldState - enum
newState - enum""",
    "startContent": "entityId - string - optional\nagePolicy - string - optional",
    "stopContent": "entityId - string - optional\nagePolicy - string - optional",
    "page": "pageId - string\nagePolicy - string - optional",
    "error": """type - enum
- network
- media
- restriction
- entitlement
- other
code - string
description - string
visible - bool
parameters - arg list - optional
agePolicy - string - optional""",
    "mediaLoadStart": "entityId - string\nagePolicy - string - optional",
    "mediaPlay": "entityId - string\nagePolicy - string - optional",
    "mediaPlaying": "entityId - string\nagePolicy - string - optional",
    "mediaPause": "entityId - string\nagePolicy - string - optional",
    "mediaWaiting": "entityId - string\nagePolicy - string - optional",
    "mediaEnded": "entityId - string\nagePolicy - string - optional",
    "mediaSeeking": "entityId - string\ntarget - double\nagePolicy - string - optional",
    "mediaSeeked": "entityId - string\nposition - double\nagePolicy - string - optional",
    "mediaRateChanged": "entityId - string\nrate - double\nagePolicy - string - optional",
    "mediaRenditionChanged": """entityId - string
bitrate - unsigned
width - unsigned
height - unsigned
profile - string - optional
agePolicy - string - optional""",
    "event": "schema - uri\ndata - string\nagePolicy - string - optional",
}

RETURN_OVERRIDES = {
    "advertisingId": """ifa - string - a UUID
ifa_type - string, one of
- \"dpid\" - device provided ID
- \"sspid\" - SSP provided ID
- \"sessionid\" - session / synthetic ID
lmt - string, one of
- \"0\"
- \"1\"""",
    "uid": "value - string - a UUID",
    "deviceClass": """deviceClass - enum
- ott - no tuner / demod, no integrated display
- stb - with tuner / demod, no integrated display
- tv - possibly tuner / demod, with integrated display""",
    "chipsetId": "chipsetId - string - see Chipset Id in Devices table",
    "state": """state - enum
- initializing
- active
- paused
- suspended
- hibernated
- terminating""",
    "getspeechstate": """speechstate - enum
- SPEECH_PENDING
- SPEECH_IN_PROGRESS
- SPEECH_PAUSED
- SPEECH_NOT_FOUND
TTS_Status - 0...3
success - bool""",
    "country\nonCountryChanged": """value - string, either
- \"\" (if not initialized)
- ISO 3166-1 alpha-2 (see Country in Devices table)""",
    "preferredAudioLanguages\nonPreferredAudioLanguagesChanged": """value - list of strings, either
- [] (if not initialized)
- list of one or more ISO 639-2/B (see Secondary Audio Language in Devices table)""",
    "presentationLanguage\nonPresentationLanguageChanged": """value - string, either
- \"\" (if not initialized)
- BCP 47 (see Presentation Languages in Devices table)""",
}

def _clean_cell(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _render_table_cell(value: object) -> str:
    text = str(value or "")
    quoted_items = re.findall(r"'[^']+'", " ".join(text.splitlines()))
    if len(quoted_items) > 1:
        return '<ul class="spec-cell-list">' + "".join(f"<li>{escape(item)}</li>" for item in quoted_items) + "</ul>"
    identifier_items = [line.strip() for line in text.splitlines() if line.strip()]
    if len(identifier_items) > 1 and all(re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", item) for item in identifier_items):
        return '<ul class="spec-cell-list">' + "".join(f"<li>{escape(item)}</li>" for item in identifier_items) + "</ul>"
    return escape(_clean_cell(value))


def _join_wrapped_identifier_list(value: object) -> str:
    joined = "".join(str(value or "").split())
    profile_values = re.findall(r"(?:child|teen|adult|household)Profile", joined)
    if profile_values:
        return "\n".join(profile_values)
    items: list[str] = []
    current = ""
    for line in (line.strip() for line in str(value or "").splitlines() if line.strip()):
        if current and current[-1].isupper() and line[0].islower():
            current += line
        else:
            if current:
                items.append(current)
            current = line
    if current:
        items.append(current)
    return "\n".join(items)


def _normalize_table_cell(value: object) -> str:
    lines = [line.strip() for line in str(value or "").splitlines() if line.strip()]
    if len(lines) > 1 and all(re.fullmatch(r"(?:[A-Za-z][A-Za-z0-9]*|'[^']+')", line) for line in lines):
        return "\n".join(lines)
    return _clean_cell(value)


def _clean_field_cell(value: object) -> str:
    lines = []
    for raw_line in str(value or "").splitlines():
        line = " ".join(raw_line.split())
        if not line:
            continue
        line = re.sub(
            r"(?<![A-Za-z])((?:[A-Za-z_]\s+){2,}[A-Za-z_])\s+-",
            lambda match: re.sub(r"\s+", "", match.group(1)) + " -",
            line,
        )
        lines.append(line)
    return "\n".join(lines)


_FIELD_DECLARATION = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s-\s")
_FIELD_SUBITEM = re.compile(r"^(?:[\[{(\"']|list\b|one\b|true\b|false\b|null\b|\d)", re.IGNORECASE)
_FIELD_DECLARATION_START = re.compile(r"(?<=\s)(?=[A-Za-z_][A-Za-z0-9_]*\s-\s)")
_LIST_MARKER = re.compile(r"^\s*(?:[-*]|\u2022|\d+\.)\s+(.+)$")


def _render_field(value: str) -> str:
    lines = [" ".join(raw_line.split()) for raw_line in value.splitlines() if raw_line.strip()]
    declarations: list[list[object]] = []
    for line in lines:
        marker = _LIST_MARKER.match(line)
        if marker and declarations:
            declarations[-1][1].append(marker.group(1))
        elif _FIELD_DECLARATION.match(line):
            declarations.append([line, []])
        elif declarations:
            declaration, details = declarations[-1]
            if details and not _FIELD_SUBITEM.match(line):
                details[-1] = f"{details[-1]} {line}"
            elif _FIELD_SUBITEM.match(line):
                details.append(line)
            else:
                declarations[-1][0] = f"{declaration} {line}"
        else:
            return f'<span class="api-detail-text">{escape(" ".join(lines))}</span>'
    if not declarations:
        return '<span class="api-detail-text">None</span>'
    rendered = []
    for declaration, details in declarations:
        detail_html = ""
        if details:
            detail_html = '<ul class="api-detail-sublist">' + "".join(f"<li>{escape(detail)}</li>" for detail in details) + "</ul>"
        rendered.append(f"<li>{escape(declaration)}{detail_html}</li>")
    return '<ul class="api-detail-list">' + "".join(rendered) + "</ul>"


def _render_description(value: str) -> str:
    """Join PDF-wrapped description lines, preserving only explicit bullet items."""
    paragraphs: list[str] = []
    bullets: list[str] = []
    current = ""
    for raw_line in value.splitlines():
        line = " ".join(raw_line.split())
        if not line:
            continue
        marker = _LIST_MARKER.match(line)
        if marker:
            if current:
                paragraphs.append(current)
                current = ""
            bullets.append(marker.group(1))
        elif bullets:
            bullets[-1] = f"{bullets[-1]} {line}"
        else:
            current = f"{current} {line}".strip()
    if current:
        paragraphs.append(current)
    rendered = [f'<p class="spec-entry-overview">{escape(text)}</p>' for text in paragraphs]
    if bullets:
        rendered.append('<ul class="api-detail-list">' + "".join(f"<li>{escape(item)}</li>" for item in bullets) + "</ul>")
    if not rendered:
        return '<span class="api-detail-text">None</span>'
    return "".join(rendered)


def _row_highlight(page, bbox: tuple) -> str | None:
    top, bottom = bbox[1], bbox[3]
    best_color, best_overlap = None, 0.0
    for rect in page.rects:
        color = rect.get("non_stroking_color")
        if color not in (API_SPEC_RED, API_SPEC_GREEN):
            continue
        overlap = max(0.0, min(rect["bottom"], bottom) - max(rect["top"], top))
        if overlap > best_overlap:
            best_color, best_overlap = color, overlap
    return "red" if best_color == API_SPEC_RED else "green" if best_color == API_SPEC_GREEN else None


def _row_marks(page, bbox: tuple, js_column_left: float) -> tuple[str, str]:
    top, bottom = bbox[1], bbox[3]
    marks = ["", ""]
    for image in page.images:
        overlap = max(0.0, min(image["bottom"], bottom) - max(image["top"], top))
        if overlap <= 0:
            continue
        pixels = page.crop((image["x0"], image["top"], image["x1"], image["bottom"])).to_image(resolution=72).original.convert("RGB")
        red, green, blue = pixels.resize((1, 1)).getpixel((0, 0))
        marks[0 if image["x0"] < js_column_left else 1] = "supported" if green >= red and green >= blue else "not supported"
    return tuple(marks)


def _support_mark(label: str, value: str) -> str:
    if value == "supported":
        return f'<span class="api-support"><span class="api-support-label">{escape(label)}</span><span class="api-support-mark supported" role="img" aria-label="{escape(label)} supported">&#10003;</span></span>'
    if value == "not supported":
        return f'<span class="api-support"><span class="api-support-label">{escape(label)}</span><span class="api-support-mark unsupported" role="img" aria-label="{escape(label)} not supported">&#10007;</span></span>'
    return f'<span class="api-support"><span class="api-support-label">{escape(label)}</span><span class="api-support-mark unknown" aria-label="{escape(label)} support unknown">&mdash;</span></span>'


def _join_identifier(value: object) -> str:
    text = "".join(str(value or "").split())
    if text == "mediaRenditionChanged":
        return text
    if text == "presentationLanguageonPresentationLanguageChanged":
        return "presentationLanguage\nonPresentationLanguageChanged"
    return re.sub(r"(?<!^)(on[A-Z])", r"\n\1", text, count=1)


def _extract_api_methods() -> list[dict]:
    methods = []
    with pdfplumber.open(ROOT / "Firebolt 8 API Spec.pdf") as pdf:
        for page in pdf.pages[1:]:
            for table in page.find_tables():
                rows = table.extract()
                if not rows or len(rows[0]) != 10:
                    continue
                js_column_left = table.rows[0].cells[8][0]
                current = None
                for row_index, row in enumerate(rows):
                    cells = [cell or "" for cell in row]
                    if cells[0].strip().isdigit():
                        if current and current["color"] != "red":
                            methods.append(current)
                        current = {"cells": cells, "color": _row_highlight(page, table.rows[row_index].bbox), "marks": _row_marks(page, table.rows[row_index].bbox, js_column_left)}
                    elif current:
                        for index, cell in enumerate(cells):
                            cell = cell.strip()
                            if cell:
                                current["cells"][index] = f'{current["cells"][index]}\n{cell}' if current["cells"][index] else cell
                if current and current["color"] != "red":
                    methods.append(current)
    extracted = [
        {
            "module": _join_identifier(item["cells"][1]),
            "method": _join_identifier(item["cells"][2]),
            "parameters": _clean_field_cell(item["cells"][3]),
            "returns": _clean_field_cell(item["cells"][4]),
            "errors": _clean_field_cell(item["cells"][5]),
            "version": _clean_cell(item["cells"][6]),
            "cpp": item["marks"][0],
            "js": item["marks"][1],
            "description": _clean_field_cell(item["cells"][9]),
        }
        for item in methods
    ]
    for method in extracted:
        method["parameters"] = PARAMETER_OVERRIDES.get(method["method"], method["parameters"])
        method["returns"] = RETURN_OVERRIDES.get(method["method"], method["returns"])
    return extracted


def _extract_api_references() -> tuple[list[list[str]], list[list[str]]]:
    with pdfplumber.open(ROOT / "Firebolt 8 API Spec.pdf") as pdf:
        tables = pdf.pages[0].extract_tables()
    types = [[_clean_cell(row[1]), _clean_cell(row[2])] for row in tables[3][1:] if _clean_cell(row[1])]
    errors = []
    error_class = ""
    for row in tables[4][1:]:
        if _clean_cell(row[1]):
            error_class = _clean_cell(row[1])
        if any(_clean_cell(cell) for cell in row[2:]):
            errors.append([error_class, *[_clean_cell(cell) for cell in row[2:]]])
    return types, errors


def _render_api_references(types: list[list[str]], errors: list[list[str]]) -> str:
    references = (
        ("types", "Types", _render_table([["Type", "Definition"], *types])),
        ("error-values", "Error values", _render_table([["Class", "Value", "Name", "Description", "Examples", "Open issues"], *errors])),
    )
    triggers = "".join(
        f'<a class="reference-trigger spec-modal-trigger" href="#reference-{slug}" data-modal-target="reference-{slug}">{title}</a>'
        for slug, title, _ in references
    )
    templates = "".join(
        f'<template id="tmpl-reference-{slug}"><section class="spec-entry reference-modal-entry"><div class="spec-entry-head"><h2>{title}</h2></div>{table}</section></template>'
        for slug, title, table in references
    )
    return '<div class="api-reference"><div class="api-reference-title">References</div>' f'<div class="reference-actions">{triggers}</div>{templates}</div>'


def build_firebolt_api() -> None:
    from build import hero, shell

    methods = [method for method in _extract_api_methods() if method["version"] != "???"]
    for index, method in enumerate(methods):
        method["id"] = f"api-{index}"
    types, errors = _extract_api_references()
    modules = sorted({method["module"] for method in methods})
    rows = json.dumps(methods, ensure_ascii=True)
    detail_templates = "".join(
        f'''<template id="tmpl-{method["id"]}"><section class="spec-entry">
            <div class="spec-entry-head"><span class="spec-entry-eyebrow">Module</span><h2>{escape(method["module"])}</h2></div>
            <div class="api-detail-method"><code>{escape(method["method"])}</code></div>
            <div class="api-detail-meta"><span class="pill">API version {escape(method["version"])}</span>{_support_mark("C++", method["cpp"])}{_support_mark("JS", method["js"])}</div>
            <dl class="api-detail-fields">
                <div class="api-detail-row"><dt>Parameters</dt><dd>{_render_field(method["parameters"])}</dd></div>
                <div class="api-detail-row"><dt>Returns</dt><dd>{_render_field(method["returns"])}</dd></div>
                <div class="api-detail-row"><dt>Specific errors</dt><dd>{_render_field(method["errors"])}</dd></div>
            </dl>
            {_render_description(method["description"])}</section></template>'''
        for method in methods
    )
    body = hero(
        "Firebolt 8",
        "Firebolt 8 Core API Specification",
        "Standardized APIs that give RDK8 applications consistent access to device and platform capabilities through Firebolt.",
        include_release=False,
        status="Published",
    )
    body += (
        '<section class="section spec-document" style="padding-top:42px">'
        '<section class="spec-intro api-spec-content">'
        '<div class="toolbar northbound-toolbar"><input id="api-search" type="search" placeholder="Search APIs" aria-label="Search APIs">'
        '<select id="api-module"><option value="">All modules</option>'
        f'{"".join(f"<option>{escape(module)}</option>" for module in modules)}</select></div>'
        f'{_render_api_references(types, errors)}'
        '<div class="spec-table-wrap"><table class="spec-table"><thead><tr><th>Module</th><th>Methods</th><th>API version</th><th>Details</th></tr></thead><tbody id="api-rows"></tbody></table></div></section>'
        '</section>'
        f'{detail_templates}'
        '<div class="spec-modal" id="spec-modal" aria-hidden="true"><div class="spec-modal-backdrop" data-modal-close></div><div class="spec-modal-dialog" role="dialog" aria-modal="true"><button type="button" class="spec-modal-close" data-modal-close aria-label="Close">&times;</button><div class="spec-modal-body" id="spec-modal-body"></div></div></div>'
        f'''<script>const DATA={rows};const esc=s=>{{const d=document.createElement('div');d.textContent=s;return d.innerHTML}};const search=document.querySelector('#api-search'),moduleFilter=document.querySelector('#api-module'),modal=document.querySelector('#spec-modal'),modalBody=document.querySelector('#spec-modal-body');function render(){{const q=search.value.toLowerCase();const rows=DATA.filter(item=>(!q||Object.values(item).join(' ').toLowerCase().includes(q))&&(!moduleFilter.value||item.module===moduleFilter.value));document.querySelector('#api-rows').innerHTML=rows.length?rows.map(item=>`<tr><td>${{esc(item.module)}}</td><td style="white-space:pre-line">${{esc(item.method)}}</td><td><span class="pill">${{esc(item.version)}}</span></td><td><a class="pill spec-modal-trigger" href="#${{item.id}}" data-modal-target="${{item.id}}">View details</a></td></tr>`).join(''):'<tr><td class="empty" colspan="4">No matching APIs.</td></tr>'}}function closeModal(){{modal.classList.remove('open');modal.setAttribute('aria-hidden','true');document.body.style.overflow=''}}document.addEventListener('click',event=>{{const trigger=event.target.closest('.spec-modal-trigger');if(trigger){{event.preventDefault();const template=document.querySelector(`#tmpl-${{trigger.dataset.modalTarget}}`);modalBody.innerHTML='';modalBody.appendChild(template.content.cloneNode(true));modal.classList.add('open');modal.setAttribute('aria-hidden','false');document.body.style.overflow='hidden'}}}});modal.querySelectorAll('[data-modal-close]').forEach(element=>element.addEventListener('click',closeModal));document.addEventListener('keydown',event=>{{if(event.key==='Escape')closeModal()}});[search,moduleFilter].forEach(element=>element.addEventListener('input',render));render()</script>'''
    )
    footer = 'Source file: <a href="Firebolt 8 API Spec.pdf" target="_blank" rel="noopener">Firebolt 8 API Spec.pdf</a>'
    (ROOT / "firebolt-api-spec.html").write_text(shell("Firebolt 8 Core API Specification | RDK8", "northbound", body, footer), encoding="utf-8")


def _render_table(rows: list[list[object]], headers_override: tuple[str, ...] | None = None) -> str:
    normalized = [[_normalize_table_cell(cell) for cell in row] for row in rows if any(_clean_cell(cell) for cell in row)]
    if len(normalized) < 2:
        return ""
    if normalized[0][0].casefold() in {"document status", "author", "reviewers"}:
        return ""
    headers = list(headers_override) if headers_override else normalized[0]
    body_rows = normalized if headers_override else normalized[1:]
    header_html = "".join(f"<th>{_render_table_cell(header)}</th>" for header in headers)
    rows_html = "".join(
        "<tr>" + "".join(f"<td>{_render_table_cell(cell)}</td>" for cell in row) + "</tr>"
        for row in body_rows
    )
    return f'<div class="spec-table-wrap"><table class="spec-table"><thead><tr>{header_html}</tr></thead><tbody>{rows_html}</tbody></table></div>'


def _render_nested_definition_table(rows: list[list[object]]) -> str:
    headers = ["Name", "Type", "Mandatory", "Allowed values", "Description"]
    fields: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    nested_columns: dict[str, int] = {}
    for row in rows[1:]:
        raw_values = [str(cell or "") for cell in row]
        values = [_clean_cell(cell) for cell in row]
        if values[0]:
            if current:
                fields.append(current)
            nested_columns = {
                value.casefold(): index
                for index, value in enumerate(values)
                if value.casefold() in {"name", "type", "mandatory", "allowed values", "description"}
            }
            current = {
                "values": [
                    values[0], values[1], values[2],
                    "" if nested_columns else values[3],
                    next((value for value in reversed(values[4:]) if value), ""),
                ],
                "children": [],
            }
            continue
        if not current or not nested_columns:
            continue
        name = values[nested_columns["name"]]
        if not name:
            continue
        current["children"].append([
            name,
            values[nested_columns.get("type", 0)],
            values[nested_columns.get("mandatory", 0)],
            raw_values[nested_columns.get("allowed values", 0)],
            values[nested_columns.get("description", 0)],
        ])
    if current:
        fields.append(current)

    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    rows_html = ""
    for field in fields:
        values = field["values"]
        children = field["children"]
        allowed_markup = escape(values[3])
        if children:
            child_headers = headers
            child_rows = children
            if not any(child[4] for child in children):
                child_headers = headers[:-1]
                child_rows = [child[:-1] for child in children]
            child_table = _render_table([child_headers, *child_rows])
            allowed_markup += f'<details class="spec-details"><summary>{escape(values[0])} fields</summary>{child_table}</details>'
        rows_html += "<tr>" + "".join(
            f"<td>{allowed_markup if index == 3 else escape(value)}</td>"
            for index, value in enumerate(values)
        ) + "</tr>"
    return f'<div class="spec-table-wrap"><table class="spec-table"><thead><tr>{header_html}</tr></thead><tbody>{rows_html}</tbody></table></div>'


def _extract_document(pdf_name: str) -> tuple[str, list[str]]:
    reader = PdfReader(ROOT / pdf_name)
    first_page_text = reader.pages[0].extract_text() or ""
    lines = [_clean_cell(line) for line in first_page_text.splitlines()]
    summary = next(
        (
            line for line in lines
            if len(line) > 120
            and not line.startswith(("Table of Contents", "RDK8 Firebolt", "Firebolt®", "Document status"))
        ),
        "Reference material extracted from the RDK8 Firebolt specification.",
    )
    tables = []
    _section_title, headers_override = DOCUMENT_TABLE_LAYOUTS.get(pdf_name, ("", None))
    with pdfplumber.open(ROOT / pdf_name) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                rendered = _render_table(table, headers_override if not tables else None)
                if rendered:
                    tables.append(rendered)
    return summary, tables


def _extract_json_rpc_sections() -> tuple[str, list[list[object]], list[list[object]]]:
    with pdfplumber.open(ROOT / "Firebolt 8 JSON-RPC spec.pdf") as pdf:
        first_page_tables = pdf.pages[0].extract_tables()
        second_page_tables = pdf.pages[1].extract_tables()
        third_page_tables = pdf.pages[2].extract_tables()

    def without_numbering(rows: list[list[object]]) -> list[list[object]]:
        return [row[1:] for row in rows if any(_clean_cell(cell) for cell in row)]

    def classify(rows: list[list[object]]) -> list[list[object]]:
        classified = []
        for description, example, notes in rows:
            try:
                payload = json.loads(_clean_cell(example))
                message_type = "Method" if "method" in payload else "Response"
            except json.JSONDecodeError:
                message_type = "Method" if '"method"' in str(example) else "Response"
            classified.append([message_type, description, example, notes])
        return classified

    definitions = _render_table(first_page_tables[1])
    method_calls = classify([
        *without_numbering(first_page_tables[2][1:]),
        *without_numbering(second_page_tables[0]),
    ])
    notifications = classify([
        *without_numbering(second_page_tables[1][1:]),
        *without_numbering(third_page_tables[0]),
    ])
    return definitions, method_calls, notifications


def _render_json_rpc_message_table(rows: list[list[object]], template_prefix: str) -> str:
    rows_html = []
    templates = []
    for index, (message_type, description, example, notes) in enumerate(rows):
        template_id = f"{template_prefix}-{index}"
        rows_html.append(
            '<tr>'
            f'<td>{escape(message_type)}</td>'
            f'<td>{escape(_clean_cell(description))}</td>'
            f'<td>{escape(_clean_cell(notes))}</td>'
            f'<td><a class="pill spec-modal-trigger" href="#{template_id}" data-modal-target="{template_id}">View example</a></td>'
            '</tr>'
            )
        templates.append(
            f'<template id="{template_id}"><section class="spec-entry">'
            f'<div class="spec-entry-head"><span class="spec-entry-eyebrow">{escape(message_type)}</span><h2>{escape(_clean_cell(description))}</h2></div>'
            f'<p class="spec-entry-overview"><strong>Message</strong>: {escape(message_type)}</p>'
            f'<h3>Example</h3><pre class="spec-example">{escape(_format_json_rpc_example(example))}</pre>'
            f'<h3>Notes</h3><p class="spec-entry-overview">{escape(_clean_cell(notes) or "No notes provided.")}</p>'
            '</section></template>'
        )
    return (
        '<div class="spec-table-wrap"><table class="spec-table json-rpc-message-table">'
        '<thead><tr><th>Message</th><th>Description</th><th>Notes</th><th>Example</th></tr></thead>'
        f'<tbody>{"".join(rows_html)}</tbody></table></div>{"".join(templates)}'
    )


def _format_json_rpc_example(value: object) -> str:
    text = _clean_cell(value)
    try:
        return json.dumps(json.loads(text), indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        return str(value or "").strip()


def build_firebolt_documents() -> None:
    from build import hero, shell

    for pdf_name, output_file, title, status in FIREBOLT_DOCUMENTS:
        body = hero(
            "Firebolt 8",
            title,
            FIREBOLT_DOCUMENT_DESCRIPTIONS[output_file],
            include_release=False,
            status=status,
        )
        if output_file == "firebolt-json-rpc.html":
            definitions, method_calls, notifications = _extract_json_rpc_sections()
            references = (
                '<div class="api-reference"><div class="api-reference-title">References</div><div class="reference-actions">'
                '<a class="reference-trigger spec-modal-trigger" href="#json-rpc-definitions" data-modal-target="json-rpc-definitions">Definitions</a>'
                '<a class="reference-trigger" href="https://www.jsonrpc.org/specification" target="_blank" rel="noopener">JSON RPC 2.0 Spec</a>'
                '</div><template id="tmpl-json-rpc-definitions"><section class="spec-entry reference-modal-entry">'
                f'<div class="spec-entry-head"><h2>Definitions</h2></div>{definitions}</section></template></div>'
            )
            method_table = _render_json_rpc_message_table(method_calls, "json-rpc-method")
            notification_table = _render_json_rpc_message_table(notifications, "json-rpc-notification")
            body += (
                '<section class="section spec-document" style="padding-top:42px">'
                f'<section class="spec-intro json-rpc-section">{references}</section>'
                '<section class="spec-intro json-rpc-section"><h2>JSON-RPC 2.0 Compliance</h2>'
                '<p>The URL used by the Firebolt Client Library to connect to the Firebolt API Gateway includes the <code>RPCv2=true</code> query parameter, confirming that the Client Library uses and accepts only compliant JSON-RPC as specified in this document.</p>'
                '<p>All names used for matching, including method and parameter names, are case sensitive as stated in Section 2 of the JSON-RPC 2.0 Specification.</p></section>'
                f'<section class="spec-intro json-rpc-section"><h2>Method Calls</h2>{method_table}</section>'
                f'<section class="spec-intro json-rpc-section"><h2>Notifications</h2>{notification_table}</section>'
                '</section>'
                '<div class="spec-modal" id="spec-modal" aria-hidden="true"><div class="spec-modal-backdrop" data-modal-close></div><div class="spec-modal-dialog" role="dialog" aria-modal="true"><button type="button" class="spec-modal-close" data-modal-close aria-label="Close">&times;</button><div class="spec-modal-body" id="spec-modal-body"></div></div></div>'
                '<script>(function(){const modal=document.getElementById("spec-modal"),body=document.getElementById("spec-modal-body");if(!modal)return;function closeModal(){modal.classList.remove("open");modal.setAttribute("aria-hidden","true");document.body.style.overflow=""}document.addEventListener("click",event=>{const trigger=event.target.closest(".spec-modal-trigger");if(!trigger)return;event.preventDefault();const template=document.getElementById(trigger.dataset.modalTarget);if(!template)return;body.innerHTML="";body.appendChild(template.content.cloneNode(true));modal.classList.add("open");modal.setAttribute("aria-hidden","false");document.body.style.overflow="hidden"});modal.querySelectorAll("[data-modal-close]").forEach(element=>element.addEventListener("click",closeModal));document.addEventListener("keydown",event=>{if(event.key==="Escape")closeModal()})})()</script>'
            )
        else:
            summary, tables = _extract_document(pdf_name)
            section_title, _headers_override = DOCUMENT_TABLE_LAYOUTS.get(pdf_name, ("", None))
            first_table = f'<h2>{escape(section_title)}</h2>{tables[0]}' if section_title and tables else (tables[0] if tables else "")
            table_sections = "".join(
                f'<section class="spec-intro">{table}</section>'
                for table in ([first_table] + tables[1:]) if table
            )
            body += (
                '<section class="section spec-document" style="padding-top:42px">'
                '<section class="spec-intro"><h2>Overview</h2>'
                f'<p>{escape(summary)}</p></section>'
                f'{table_sections or "<p class=\"lede\">No structured tables were extracted from this document.</p>"}'
                '</section>'
            )
        footer = f'Source file: <a href="{escape(pdf_name)}" target="_blank" rel="noopener">{escape(pdf_name)}</a>'
        (ROOT / output_file).write_text(shell(f"{title} | RDK8", "northbound", body, footer), encoding="utf-8")


def build_firebolt_intents() -> None:
    from build import hero, shell

    pdf_name = "Firebolt 8 Intent Spec.pdf"
    action_types = (
        "Home action type", "Launch action type", "Pre-load action type", "Entity action type",
        "Playback action type", "Search action type", "Section action type", "Tune action type",
        "Play-entity action type", "Play-query action type", "Previous action type", "Next action type",
        "Repeat action type", "Shuffle action type", "Skip-ad action type", "Skip-recap action type",
        "Skip-intro action type",
    )
    text = "\n".join(page.extract_text() or "" for page in PdfReader(ROOT / pdf_name).pages)
    with pdfplumber.open(ROOT / pdf_name) as pdf:
        rows = pdf.pages[1].extract_tables()[0]
        definition_tables = {
            "Launch action type": _render_table(pdf.pages[2].extract_tables()[0]),
            "Entity action type": _render_table(pdf.pages[3].extract_tables()[0]),
            "Playback action type": _render_table(pdf.pages[3].extract_tables()[1]),
            "Search action type": _render_table(pdf.pages[4].extract_tables()[0]),
            "Section action type": _render_table(pdf.pages[4].extract_tables()[1]),
            "Tune action type": _render_nested_definition_table(pdf.pages[5].extract_tables()[0]),
            "Play-entity action type": _render_nested_definition_table(pdf.pages[6].extract_tables()[0]),
            "Play-query action type": _render_nested_definition_table(pdf.pages[6].extract_tables()[1]),
        }

    action_row, data_row, context_row = rows[:3]
    context_headers = [_clean_cell(cell) for cell in context_row[4:9]]
    context_rows = []
    for row in rows[3:]:
        values = row[4:9]
        if not any(_clean_cell(cell) for cell in values):
            continue
        values[0] = "".join(str(values[0] or "").split())
        values[3] = _join_wrapped_identifier_list(values[3])
        context_rows.append(values)
    context_table = _render_table([context_headers, *context_rows])
    triggers = "".join(
        f'<a class="pill allowed-action spec-modal-trigger" href="#intent-{escape(action.removesuffix(" action type").lower())}" data-modal-target="intent-{escape(action.removesuffix(" action type").lower())}" title="Open {escape(action)}">{escape(action.removesuffix(" action type").lower())}</a>'
        for action in action_types
    )

    def split_json_blocks(value: str) -> list[str]:
        blocks, depth, start = [], 0, None
        in_string = escaped = False
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
                if depth == 0 and start is not None:
                    blocks.append(value[start:index + 1])
                    start = None
        return blocks

    constituent_rows = (
        '<tr>'
        f'<td><code>{escape(_clean_cell(action_row[0]))}</code></td><td>{escape(_clean_cell(action_row[1]))}</td><td>{escape(_clean_cell(action_row[2]))}</td><td>{escape(_clean_cell(action_row[3]))}</td><td rowspan="2"><div class="allowed-actions">{triggers}</div></td></tr>'
        '<tr>'
        f'<td><code>{escape(_clean_cell(data_row[0]))}</code></td><td>{escape(_clean_cell(data_row[1]))}</td><td>{escape(_clean_cell(data_row[2]))}</td><td>{escape(_clean_cell(data_row[3]))}</td></tr>'
        '<tr>'
        f'<td><code>{escape(_clean_cell(context_row[0]))}</code></td><td>{escape(_clean_cell(context_row[1]))}</td><td>{escape(_clean_cell(context_row[2]))}</td><td>{escape(_clean_cell(context_row[3]))}</td><td><details class="spec-details"><summary>Context fields</summary>{context_table}</details></td></tr>'
    )
    templates = []
    for index, action in enumerate(action_types):
        marker = f"{action}\n"
        first = text.find(marker)
        start = text.find(marker, first + len(marker))
        end = text.find(f"{action_types[index + 1]}\n", start + len(marker)) if index + 1 < len(action_types) else len(text)
        details = text[start + len(marker):end].strip() if start >= 0 else "Definition unavailable in the RDK8 source PDF."
        definition_marker = "Definition of data object"
        overview, definition_and_example = details.split(definition_marker, 1) if definition_marker in details else (details, "")
        example_match = re.search(r"\n(Examples?)\n", definition_and_example)
        if example_match:
            definition = definition_and_example[:example_match.start()].strip()
            example_heading = example_match.group(1)
            examples = definition_and_example[example_match.end():].strip()
        else:
            definition = definition_and_example.strip()
            example_heading = "Example"
            examples = ""
        slug = escape(action.removesuffix(" action type").lower())
        definition_markup = definition_tables.get(action, f'<pre class="spec-definition-text">{escape(definition or "No data object is required.")}</pre>')
        example_blocks = split_json_blocks(examples)
        examples_markup = (
            '<div class="spec-examples">'
            + "".join(f'<pre class="spec-example">{escape(block)}</pre>' for block in example_blocks)
            + "</div>"
            if example_blocks
            else ""
        )
        templates.append(
            f'<template id="tmpl-intent-{slug}"><section class="spec-entry"><div class="spec-entry-head"><span class="spec-entry-eyebrow">Intent action</span><h2>{escape(action)}</h2></div>'
            f'<p class="spec-entry-overview">{escape(overview.strip())}</p>'
            f'<h3>Definition of data object</h3>{definition_markup}'
            f'<h3>{escape(example_heading)}</h3>{examples_markup or "<p class=\"lede\">No example was included in the source PDF.</p>"}'
            '</section></template>'
        )

    body = hero("Firebolt 8", "Firebolt 8 Intents Specification", FIREBOLT_DOCUMENT_DESCRIPTIONS["firebolt-intents.html"], include_release=False, status="Published")
    body += (
        '<section class="section spec-document" style="padding-top:42px">'
        '<section class="spec-intro intent-overview" id="overview">'
        '<p>An Intent is a message object sent to an application requesting a specific action. This may occur as part of the launch of the application or when it is already loaded. The application shall treat the receipt of an intent as an explicit request to carry out the intent and immediately action it, irrespective of what the application is currently doing. The only exception to this if the application is carrying out some process that can not be interrupted eg processing a payment.</p>'
        '<p>An application may support multiple intent action types or none, however if an application receives an intent that it does not support, or one that does not contain enough data for an application to fulfil it, it shall ignore it and not present any error to the user.</p></section>'
        '<section class="spec-intro" id="constituent-parts"><h2>Constituent parts of an intent</h2><div class="spec-table-wrap"><table class="spec-table"><thead><tr><th>Part</th><th>Type</th><th>Mandatory</th><th>Description</th><th>Allowed values</th></tr></thead>'
        f'<tbody>{constituent_rows}</tbody></table></div></section></section>'
        f'{"".join(templates)}'
        '<div class="spec-modal" id="spec-modal" aria-hidden="true"><div class="spec-modal-backdrop" data-modal-close></div><div class="spec-modal-dialog" role="dialog" aria-modal="true"><button type="button" class="spec-modal-close" data-modal-close aria-label="Close">&times;</button><div class="spec-modal-body" id="spec-modal-body"></div></div></div>'
        '<script>const modal=document.querySelector("#spec-modal"),modalBody=document.querySelector("#spec-modal-body");function closeModal(){modal.classList.remove("open");modal.setAttribute("aria-hidden","true");document.body.style.overflow=""}document.addEventListener("click",event=>{const trigger=event.target.closest(".spec-modal-trigger");if(trigger){event.preventDefault();const template=document.querySelector(`#tmpl-${trigger.dataset.modalTarget}`);modalBody.innerHTML="";modalBody.appendChild(template.content.cloneNode(true));modal.classList.add("open");modal.setAttribute("aria-hidden","false");document.body.style.overflow="hidden"}});modal.querySelectorAll("[data-modal-close]").forEach(element=>element.addEventListener("click",closeModal));document.addEventListener("keydown",event=>{if(event.key==="Escape")closeModal()});</script>'
    )
    footer = f'Source file: <a href="{escape(pdf_name)}" target="_blank" rel="noopener">{escape(pdf_name)}</a>'
    (ROOT / "firebolt-intents.html").write_text(shell("Firebolt 8 Intents Specification | RDK8", "northbound", body, footer), encoding="utf-8")


def _clean_linux_key_codes(value: object) -> str:
    codes: list[str] = []
    for line in str(value or "").splitlines():
        item = _clean_cell(line)
        if not item:
            continue
        if item.startswith("KEY_"):
            codes.append(item)
        elif codes:
            codes[-1] += item
        else:
            codes.append(item)
    return " ".join(codes)


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


def build_firebolt_key_codes() -> None:
    from build import hero, shell

    pdf_name = "Firebolt 8 key code Spec.pdf"
    with pdfplumber.open(ROOT / pdf_name) as pdf:
        standard_table = pdf.pages[0].extract_tables()[1]
        partner_rows = pdf.pages[1].extract_tables()[0]
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    headers = [_clean_cell(cell) for cell in standard_table[0]]

    def normalize_rows(rows: list[list[object]]) -> list[list[str]]:
        normalized = []
        for row in rows:
            if not any(_clean_cell(cell) for cell in row):
                continue
            values = [_clean_cell(cell) for cell in row]
            values[2] = _clean_linux_key_codes(row[2])
            normalized.append(values)
        return normalized

    partner_intro = ""
    standard_source_rows = []
    for row in standard_table[1:]:
        first_cell = str(row[0] or "")
        if first_cell.startswith("Partner Buttons"):
            _, _, partner_intro = first_cell.partition("\n")
        else:
            standard_source_rows.append(row)
    standard_rows = normalize_rows(standard_source_rows)
    partners = normalize_rows(partner_rows)
    note_match = re.search(r"(All Linux Function key codes.*)$", text.strip())
    closing_note = _clean_cell(note_match.group(1)) if note_match else ""
    standard_markup = _render_key_code_table(headers, standard_rows, "standard-key")
    partner_markup = _render_key_code_table(headers, partners, "partner-key")

    body = hero(
        "Firebolt 8",
        "Firebolt 8 Key Codes Specification",
        FIREBOLT_DOCUMENT_DESCRIPTIONS["firebolt-key-codes.html"],
        include_release=False,
        status="Published",
    )
    body += (
        '<section class="section spec-document" style="padding-top:42px">'
        f'<section class="spec-intro" id="standard-keys"><h2>Standard RCU keys</h2>{standard_markup}</section>'
        f'<section class="spec-intro" id="partner-buttons"><h2>Partner buttons</h2>'
        f'<p>{escape(_clean_cell(partner_intro))}</p>{partner_markup}'
        '<div class="spec-modal" id="spec-modal" aria-hidden="true"><div class="spec-modal-backdrop" data-modal-close></div><div class="spec-modal-dialog" role="dialog" aria-modal="true"><button type="button" class="spec-modal-close" data-modal-close aria-label="Close">&times;</button><div class="spec-modal-body" id="spec-modal-body"></div></div></div>'
        '<script>(function(){const modal=document.getElementById("spec-modal"),body=document.getElementById("spec-modal-body");if(!modal)return;function closeModal(){modal.classList.remove("open");modal.setAttribute("aria-hidden","true");document.body.style.overflow=""}document.addEventListener("click",event=>{const trigger=event.target.closest(".spec-modal-trigger");if(!trigger)return;event.preventDefault();const template=document.getElementById(trigger.dataset.modalTarget);if(!template)return;body.innerHTML="";body.appendChild(template.content.cloneNode(true));modal.classList.add("open");modal.setAttribute("aria-hidden","false");document.body.style.overflow="hidden"});modal.querySelectorAll("[data-modal-close]").forEach(element=>element.addEventListener("click",closeModal));document.addEventListener("keydown",event=>{if(event.key==="Escape")closeModal()})})()</script>'
        f'<p class="lede" style="margin-top:16px">{escape(closing_note)}</p></section>'
        '</section>'
    )
    footer = f'Source file: <a href="{escape(pdf_name)}" target="_blank" rel="noopener">{escape(pdf_name)}</a>'
    (ROOT / "firebolt-key-codes.html").write_text(shell("Firebolt 8 Key Codes Specification | RDK8", "northbound", body, footer), encoding="utf-8")


def build_northbound() -> None:
    convert_excel_to_json(
        ROOT / "RDK8-northbound-api-spec.xlsx",
        ROOT / "northbound-apis.json",
        {
            "component": ("component", "service", "module", "modules"),
            "name": ("api", "api name", "interface", "methods"),
            "description": ("description", "details", "summary"),
            "reference": ("reference", "source", "url", "repo"),
            "type": ("type",),
            "releaseTag": ("release/tag version", "release", "tag", "version"),
        },
        optional_fields={"description", "reference", "type"},
    )
    json_path = ROOT / "northbound-apis.json"
    source = json.loads(json_path.read_text(encoding="utf-8"))
    source["status"] = "Published"
    source["version"] = "8.0.0"
    for api in source.get("apis", []):
        if not api.get("releaseTag") or api.get("releaseTag") == "???":
            api["releaseTag"] = "8.0.0"
    json_path.write_text(json.dumps(source, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    build_api(
        data_file="northbound-apis.json",
        output_file="northbound-api-spec.html",
        active="northbound",
        title="Firebolt Core API Specification",
        description="The RDK8 Northbound API Specifications provide a consistent app-facing layer for web and native applications to access RDK8 platform services through Firebolt.",
        columns=["Modules", "Version", "Methods"],
        fields=["component", "releaseTag", "name"],
        link_field=None,
        search_placeholder="Search Northbound APIs",
        empty_message="No Northbound APIs have been loaded.",
        sort_field="component",
        show_version=False,
        show_status_explainer=True,
        draft_note="Phase I - Core Defined: the first Firebolt API specification release is published for development preview and early validation of RDK8's standardized, versioned app API layer.",
    )
    build_firebolt_api()
    build_firebolt_documents()
    build_firebolt_intents()
    build_firebolt_key_codes()

if __name__ == "__main__":
    build_northbound()
