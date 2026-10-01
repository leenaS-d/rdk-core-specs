"""RDKE northbound API list generator."""
import json
import re
from html import escape
from build import build_api, hero, shell
from import_apis import convert_excel_to_json
from pathlib import Path
from pypdf import PdfReader
import pdfplumber

ROOT = Path(__file__).resolve().parent


def build_northbound() -> None:
    convert_excel_to_json(
        ROOT / "northbound-apis-rdk9-draft.xlsx",
        ROOT / "northbound-apis.json",
        {
            "component": ("component", "service", "module", "modules"),
            "name": ("api", "api name", "interface", "methods"),
            "description": ("description", "details", "summary"),
            "reference": ("reference", "source", "url", "repo"),
            "releaseTag": ("release/tag version", "release", "tag", "version", "api version"),
        },
        optional_fields={"description", "reference"},
    )
    json_path = ROOT / "northbound-apis.json"
    source = json.loads(json_path.read_text(encoding="utf-8"))
    normalized_apis = []
    for api in source.get("apis", []):
        for field in ("component", "name", "releaseTag"):
            api[field] = re.sub(r"\s+", " ", str(api.get(field, ""))).strip()
        api["name"] = re.sub(r"\s+(?=on[A-Z])", "\n", api["name"])
        if api["name"].startswith("on") and normalized_apis:
            normalized_apis[-1]["name"] = f'{normalized_apis[-1]["name"]}\n{api["name"]}'
        else:
            normalized_apis.append(api)
    source["apis"] = normalized_apis
    json_path.write_text(json.dumps(source, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    build_api(
        data_file="northbound-apis.json",
        output_file="northbound-apis.html",
        active="northbound",
        title="Northbound API Specifications",
        description="Standardized APIs the middleware exposes upward to the application layer, giving apps consistent access to device capabilities via Thunder and Firebolt.",
        columns=["Modules", "Version", "Methods"],
        fields=["component", "releaseTag", "name"],
        link_field=None,
        search_placeholder="Search Northbound APIs",
        empty_message="No Northbound APIs have been loaded.",
        sort_field="component",
        draft_note="This page contains an evolving list of Northbound API components. The current list is a draft and will continue to be updated.",
    )
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


def clean_identifier(value: object) -> str:
    """Rejoin a field name PDF-wrapped mid-word (e.g. "fireboltMeth\nod") without adding a space."""
    return re.sub(r"\s+", "", str(value or "")).strip()


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
    'document.querySelectorAll(".spec-modal-trigger").forEach(function(el){'
    'el.addEventListener("click",function(e){'
    'e.preventDefault();'
    'openModal(el.getAttribute("data-modal-target"))'
    '})});'
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
        f'<a class="allowed-action spec-modal-trigger" href="#app-action-{escape(action_type)}" '
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
    )
    body += (
        '<section class="section" style="padding-top:34px"><div class="spec-content">'
        '<section class="spec-overview-card" id="overview"><div class="eyebrow">Overview</div>'
        '<h2 style="margin:8px 0 0">Firebolt 9 App Actions Specification</h2>'
        '<p>All App Actions follow the following format.</p>'
        '</section>'
        f'<section class="spec-entry" id="format"><h2>Format of Action</h2>{format_table}</section>'
        '</div></section>'
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
        f'<a class="allowed-action spec-modal-trigger" href="#intent-{escape(action.removesuffix(" action type").lower())}" '
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
    )
    body += (
        '<section class="section" style="padding-top:34px"><div class="spec-content">'
        '<section class="spec-overview-card" id="overview"><div class="eyebrow">Overview</div><h2 style="margin:8px 0 0">Firebolt 9 Intents Specification</h2>'
        '<p>An Intent is a message object sent to an application requesting a specific action. This may occur as part of the launch of the application or when it is already loaded. The application shall treat the receipt of an intent as an explicit request to carry out the intent and immediately action it, irrespective of what the application is currently doing. The only exception to this if the application is carrying out some process that can not be interrupted eg processing a payment.</p>'
        '<p>An application may support multiple intent action types or none, however if an application receives an intent that it does not support, or one that does not contain enough data for an application to fulfil it, it shall ignore it and not present any error to the user.</p>'
        '</section>'
        f'<section class="spec-entry" id="constituent-parts"><h2>Constituent parts of an intent</h2>'
        f'<div class="spec-table-wrap"><table class="spec-table"><thead><tr><th>Part</th><th>Type</th><th>Mandatory</th><th>Description</th><th>Allowed values</th></tr></thead><tbody>{constituent_html}</tbody></table></div>'
        f'<h3>Example</h3><pre class="spec-example">{escape(example)}</pre>'
        '</section>'
        '</div></section>'
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
        (partner_rows if in_partner else standard_rows).append(cleaned_row)

    standard_table = render_spec_table(headers, standard_rows)
    partner_table = render_spec_table(headers, partner_rows)

    body = hero(
        "Firebolt 9",
        "Firebolt Key Codes Specification",
        "Definition of the Key Codes made available to Firebolt Apps on the RDK9 video platform.",
    )
    body += (
        '<section class="section" style="padding-top:34px"><div class="spec-layout">'
        + render_spec_toc([
            ("Reference", '<a href="#overview">Overview</a><a href="#standard-keys">Standard RCU keys</a><a href="#partner-buttons">Partner buttons</a>'),
        ])
        + '<div class="spec-content">'
        '<section class="spec-overview-card" id="overview"><div class="eyebrow">Overview</div>'
        '<h2 style="margin:8px 0 0">Firebolt 9 Key Codes Specification</h2>'
        f'<p>{escape(summary)}</p>'
        '</section>'
        f'<section class="spec-entry" id="standard-keys"><h2>Standard RCU keys</h2>{standard_table}</section>'
        f'<section class="spec-entry" id="partner-buttons"><h2>Partner buttons</h2>'
        f'<p class="spec-entry-overview">{escape(partner_intro)}</p>{partner_table}'
        f'<p class="lede" style="margin-top:16px">{escape(closing_note)}</p>'
        '</section>'
        '</div></div></section>'
    )
    body += SPEC_TOC_SCRIPT
    footer = f'Source file: <a href="{escape(pdf_name)}" target="_blank" rel="noopener">{escape(pdf_name)}</a>'
    (ROOT / "firebolt-key-codes.html").write_text(shell("Firebolt Key Codes Specification | RDKE", "northbound", body, footer), encoding="utf-8")


if __name__ == "__main__":
    build_northbound()

