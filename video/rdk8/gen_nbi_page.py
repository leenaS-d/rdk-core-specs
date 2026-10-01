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
    ("Firebolt 8 JSON-RPC spec.pdf", "firebolt-json-rpc.html", "Firebolt 8 JSON-RPC Specification", "Approved"),
    ("Firebolt 8 Intent Spec.pdf", "firebolt-intents.html", "Firebolt 8 Intents Specification", "Approved"),
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


def _clean_cell(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _clean_field_cell(value: object) -> str:
    return "\n".join(line.rstrip() for line in str(value or "").splitlines() if line.strip())


_FIELD_DECLARATION = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s-\s")
_FIELD_SUBITEM = re.compile(r"^(?:[\[{(\"']|list\b|one\b|true\b|false\b|null\b|\d)", re.IGNORECASE)


def _render_field(value: str) -> str:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    declarations: list[list[object]] = []
    for line in lines:
        if _FIELD_DECLARATION.match(line):
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
            return f'<span class="api-detail-text">{escape(value)}</span>'
    if not declarations:
        return '<span class="api-detail-text">None</span>'
    rendered = []
    for declaration, details in declarations:
        detail_html = ""
        if details:
            detail_html = '<ul class="api-detail-sublist">' + "".join(f"<li>{escape(detail)}</li>" for detail in details) + "</ul>"
        rendered.append(f"<li>{escape(declaration)}{detail_html}</li>")
    return '<ul class="api-detail-list">' + "".join(rendered) + "</ul>"


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
    return [
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

    methods = _extract_api_methods()
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
            <p class="spec-entry-overview">{escape(method["description"])}</p></section></template>'''
        for method in methods
    )
    body = hero(
        "Firebolt 8",
        "Firebolt 8 API Specification",
        "Standardized APIs that give RDK8 applications consistent access to device and platform capabilities through Firebolt.",
        include_release=False,
        status="Approved",
    )
    body += (
        '<section class="section spec-document" style="padding-top:42px">'
        '<section class="spec-intro api-spec-content">'
        '<div class="toolbar northbound-toolbar"><input id="api-search" type="search" placeholder="Search APIs" aria-label="Search APIs">'
        '<select id="api-module"><option value="">All modules</option>'
        f'{"".join(f"<option>{escape(module)}</option>" for module in modules)}</select></div>'
        f'{_render_api_references(types, errors)}'
        '<div class="table-wrap"><table><thead><tr><th>Module</th><th>Methods</th><th>API version</th><th>Details</th></tr></thead><tbody id="api-rows"></tbody></table></div></section>'
        '</section>'
        f'{detail_templates}'
        '<div class="spec-modal" id="spec-modal" aria-hidden="true"><div class="spec-modal-backdrop" data-modal-close></div><div class="spec-modal-dialog" role="dialog" aria-modal="true"><button type="button" class="spec-modal-close" data-modal-close aria-label="Close">&times;</button><div class="spec-modal-body" id="spec-modal-body"></div></div></div>'
        f'''<script>const DATA={rows};const esc=s=>{{const d=document.createElement('div');d.textContent=s;return d.innerHTML}};const search=document.querySelector('#api-search'),moduleFilter=document.querySelector('#api-module'),modal=document.querySelector('#spec-modal'),modalBody=document.querySelector('#spec-modal-body');function render(){{const q=search.value.toLowerCase();const rows=DATA.filter(item=>(!q||Object.values(item).join(' ').toLowerCase().includes(q))&&(!moduleFilter.value||item.module===moduleFilter.value));document.querySelector('#api-rows').innerHTML=rows.length?rows.map(item=>`<tr><td>${{esc(item.module)}}</td><td style="white-space:pre-line">${{esc(item.method)}}</td><td><span class="pill">${{esc(item.version)}}</span></td><td><a class="pill spec-modal-trigger" href="#${{item.id}}" data-modal-target="${{item.id}}">View details</a></td></tr>`).join(''):'<tr><td class="empty" colspan="4">No matching APIs.</td></tr>'}}function closeModal(){{modal.classList.remove('open');modal.setAttribute('aria-hidden','true');document.body.style.overflow=''}}document.addEventListener('click',event=>{{const trigger=event.target.closest('.spec-modal-trigger');if(trigger){{event.preventDefault();const template=document.querySelector(`#tmpl-${{trigger.dataset.modalTarget}}`);modalBody.innerHTML='';modalBody.appendChild(template.content.cloneNode(true));modal.classList.add('open');modal.setAttribute('aria-hidden','false');document.body.style.overflow='hidden'}}}});modal.querySelectorAll('[data-modal-close]').forEach(element=>element.addEventListener('click',closeModal));document.addEventListener('keydown',event=>{{if(event.key==='Escape')closeModal()}});[search,moduleFilter].forEach(element=>element.addEventListener('input',render));render()</script>'''
    )
    footer = 'Source file: <a href="Firebolt 8 API Spec.pdf" target="_blank" rel="noopener">Firebolt 8 API Spec.pdf</a>'
    (ROOT / "firebolt-api-spec.html").write_text(shell("Firebolt 8 API Specification | RDK8", "northbound", body, footer), encoding="utf-8")


def _render_table(rows: list[list[object]], headers_override: tuple[str, ...] | None = None) -> str:
    normalized = [[_clean_cell(cell) for cell in row] for row in rows if any(_clean_cell(cell) for cell in row)]
    if len(normalized) < 2:
        return ""
    if normalized[0][0].casefold() in {"document status", "author", "reviewers"}:
        return ""
    headers = list(headers_override) if headers_override else normalized[0]
    body_rows = normalized if headers_override else normalized[1:]
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    rows_html = "".join(
        "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>"
        for row in body_rows
    )
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


def build_firebolt_documents() -> None:
    from build import hero, shell

    for pdf_name, output_file, title, status in FIREBOLT_DOCUMENTS:
        summary, tables = _extract_document(pdf_name)
        section_title, _headers_override = DOCUMENT_TABLE_LAYOUTS.get(pdf_name, ("", None))
        first_table = f'<h2>{escape(section_title)}</h2>{tables[0]}' if section_title and tables else (tables[0] if tables else "")
        table_sections = "".join(
            f'<section class="spec-intro">{table}</section>'
            for table in ([first_table] + tables[1:]) if table
        )
        body = hero(
            "Firebolt 8",
            title,
            FIREBOLT_DOCUMENT_DESCRIPTIONS[output_file],
            include_release=False,
            status=status,
        )
        body += (
            '<section class="section spec-document" style="padding-top:42px">'
            '<section class="spec-intro">'
            '<h2>Overview</h2>'
            f'<p>{escape(summary)}</p>'
            '</section>'
            f'{table_sections or "<p class=\"lede\">No structured tables were extracted from this document.</p>"}'
            '</section>'
        )
        footer = f'Source file: <a href="{escape(pdf_name)}" target="_blank" rel="noopener">{escape(pdf_name)}</a>'
        (ROOT / output_file).write_text(shell(f"{title} | RDK8", "northbound", body, footer), encoding="utf-8")


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
    standard_markup = f'<div class="key-codes-table">{_render_table([headers, *standard_rows])}</div>'
    partner_markup = f'<div class="key-codes-table">{_render_table([headers, *partners])}</div>'

    body = hero(
        "Firebolt 8",
        "Firebolt 8 Key Codes Specification",
        FIREBOLT_DOCUMENT_DESCRIPTIONS["firebolt-key-codes.html"],
        include_release=False,
        status="Approved",
    )
    body += (
        '<section class="section spec-document" style="padding-top:42px">'
        f'<section class="spec-intro" id="standard-keys"><h2>Standard RCU keys</h2>{standard_markup}</section>'
        f'<section class="spec-intro" id="partner-buttons"><h2>Partner buttons</h2>'
        f'<p>{escape(_clean_cell(partner_intro))}</p>{partner_markup}'
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
        title="Northbound API Specifications",
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
    build_firebolt_key_codes()

if __name__ == "__main__":
    build_northbound()
