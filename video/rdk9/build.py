"""Build the self-contained RDKE static reference site.

Usage:
    python build.py
    python build.py --page components
    python build.py --page all --check

All inputs and outputs are kept inside this directory. The northbound,
southbound, and hardware pages intentionally support empty datasets until
their source workbook and profiles are provided.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


NORTHBOUND_MENU = [
    ("northbound-apis.html", "Firebolt Core API Specification"),
    ("firebolt-app-actions.html", "Firebolt App Actions Specification"),
    ("firebolt-intents.html", "Firebolt Intents Specification"),
    ("firebolt-key-codes.html", "Firebolt Key Codes Specification"),
]

NORTHBOUND_KEYS = {"northbound"}


def nav(active: str) -> str:
    links = [
        ("index.html", "Home", "home"),
        ("component-registry.html", "Components Catalog", "components"),
        ("southbound-apis.html", "Southbound API Spec", "southbound"),
        ("hardware-specifications.html", "Hardware specifications", "hardware"),
    ]
    items = "".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>'
        for href, label, key in links[:2]
    )
    menu_items = "".join(f'<a href="{href}">{label}</a>' for href, label in NORTHBOUND_MENU)
    dropdown_active = "active" if active in NORTHBOUND_KEYS else ""
    dropdown = (
        f'<details class="nav-dropdown"><summary class="nav-dropdown-summary {dropdown_active}">Northbound API Spec</summary>'
        f'<div class="nav-dropdown-menu">{menu_items}</div></details>'
    )
    items += dropdown
    items += "".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>'
        for href, label, key in links[2:]
    )
    return f'''<div class="accent"></div>
<header class="nav"><a class="brand" href="index.html"><img src="RDK-logo.png" alt="RDK"></a><nav class="navlinks">{items}</nav></header>'''


def shell(title: str, active: str, body: str, footer: str = "") -> str:
    footer_html = f'<footer class="footer"><div class="wrap">{footer}</div></footer>' if footer else ""
    control_styles = '<style>.api-controls{display:grid;grid-template-columns:minmax(0,1fr) minmax(260px,auto);align-items:center;gap:20px;margin-bottom:24px}.api-controls>.toolbar{justify-self:end;min-width:260px}@media(max-width:760px){.api-controls{grid-template-columns:1fr}.api-controls>.toolbar{justify-self:stretch;min-width:0}}</style>' if active != "home" else ""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<link rel="stylesheet" href="styles.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>body{{font-family:"Inter",-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}h1,h2,h3{{font-family:"Space Grotesk","Inter",sans-serif}}code,.mono,.release-pill{{font-family:"JetBrains Mono",ui-monospace,monospace!important}}</style>
<style>.hero .wrap{{max-width:none}}</style>
<style>@media(max-width:650px){{.hero{{height:auto!important;min-height:0!important;padding:48px 20px 44px!important}}.hero h1{{font-size:clamp(1.9rem,9vw,2.8rem)!important}}.hero p{{font-size:1rem!important;line-height:1.5}}.hero .badges{{margin-top:18px}}}}</style>{control_styles}
</head>
<body>
{nav(active)}
<main>
{body}
</main>
{footer_html}
</body>
</html>
'''


def status_explainer() -> str:
    return '''<details style="position:relative;min-width:150px"><summary style="cursor:pointer;color:#2457d6;font-size:.84rem;font-weight:700">Status legend</summary><dl style="position:absolute;z-index:2;left:0;right:auto;top:calc(100% + 8px);width:min(420px,calc(100vw - 40px));margin:0;padding:16px 18px;border:1px solid var(--border);border-radius:6px;background:#fff;box-shadow:var(--shadow);font-size:.84rem;line-height:1.45"><dt style="font-weight:700;color:var(--ink)">Draft</dt><dd style="margin:2px 0 10px;color:var(--muted)">Specifications drafted and undergoing internal reviews and RTAB Approval</dd><dt style="font-weight:700;color:var(--ink)">Approved</dt><dd style="margin:2px 0 10px;color:var(--muted)">All review feedback has been addressed; RTAB has voted and approved the spec</dd><dt style="font-weight:700;color:var(--ink)">Published</dt><dd style="margin:2px 0 0;color:var(--muted)">Tagged and versioned against an official RDK release</dd></dl></details>'''


def hero(eyebrow: str, title: str, description: str, badges: list[str] | None = None, subtitle: str = "", status: str | None = None) -> str:
    badge_html = "" if not badges else '<div class="badges">' + "".join(
        f'<span class="badge">{esc(item)}</span>' for item in badges
    ) + "</div>"
    eyebrow_html = f'<div class="eyebrow" style="font-size:1.1rem;letter-spacing:.08em">{esc(eyebrow)}</div>' if eyebrow else ""
    subtitle_html = f'<div class="hero-subtitle" style="font-size:.95rem;font-weight:600;color:#b8df63;margin:-4px 0 18px">{esc(subtitle)}</div>' if subtitle else ""
    status_class = " approved" if (status or "").casefold() == "approved" else ""
    status_html = "" if status is None else (
        f'<div class="hero-catalog-status"><span class="hero-status-badge{status_class}"><span>Catalog status:</span> '
        f'{esc(status)}</span>{status_explainer()}</div>'
    )
    return f'''<section class="hero" style="min-height:clamp(360px,32vw,440px);padding:52px 5vw 42px;display:flex;align-items:center;overflow:visible"><div class="wrap" style="width:100%">{eyebrow_html}<h1 style="font-size:clamp(1.9rem,3.6vw,3.5rem)">{esc(title)}</h1>{subtitle_html}<p>{esc(description)}</p>{badge_html}{status_html}</div></section>'''


def cards(items: list[list[str]]) -> str:
    return '<div class="grid">' + "".join(
        f'<article class="card"><h3>{esc(item[0])}</h3><p>{esc(item[1])}</p></article>'
        for item in items
    ) + "</div>"


def grouped_cards(groups: list[dict]) -> str:
    rendered = []
    for group in groups:
        description = f'<p>{esc(group["description"])}</p>' if group.get("description") else ""
        items = "".join(f'<li>{esc(item)}</li>' for item in group.get("items", []))
        rendered.append(f'<article class="card"><h3>{esc(group["title"])}</h3>{description}<ul>{items}</ul></article>')
    return '<div class="grid">' + "".join(rendered) + "</div>"


def build_api(
    *,
    data_file: str,
    output_file: str,
    active: str,
    title: str,
    description: str,
    columns: list[str],
    fields: list[str],
    link_field: str | None = None,
    search_placeholder: str | None = None,
    empty_message: str | None = None,
    sort_field: str | None = None,
    draft_note: str = "This page contains an evolving list of API components. The current list is a draft and will continue to be updated.",
) -> None:
    data = load(data_file)
    records = data.get("apis", [])
    column_html = "".join(f"<th>{esc(column)}</th>" for column in columns)
    ordered_records = sorted(records, key=lambda item: str(item.get(sort_field, "")).casefold()) if sort_field else records
    row_data = [[item.get(field, "") for field in fields] for item in ordered_records]
    rows = f'<tr><td class="empty" colspan="{len(fields)}">{esc(empty_message or f"No {title.lower()} have been loaded.")}</td></tr>' if not records else ""
    script = ""
    search = ""
    table_id = f"{active}-rows"
    if search_placeholder:
        search_id = f"{active}-search"
        search = f'<div class="toolbar catalog-search-toolbar"><input id="{search_id}" type="search" placeholder="{esc(search_placeholder)}" aria-label="{esc(search_placeholder)}"></div>'
        script_data = json.dumps(row_data, ensure_ascii=True)
        link_index = fields.index(link_field) if link_field else -1
        cells = "".join(
            f'''<td style="white-space:pre-line"><a href="${{esc(item[{index}])}}" target="_blank" rel="noopener">${{esc(item[{index}])}}</a></td>'''
            if index == link_index else f"<td style=\"white-space:pre-line\">${{esc(item[{index}])}}</td>"
            for index in range(len(fields))
        )
        script = f'''<script>const DATA={script_data};const esc=s=>{{const d=document.createElement('div');d.textContent=s;return d.innerHTML}};const search=document.querySelector('#{search_id}');const render=()=>{{const q=search.value.toLowerCase();const rows=DATA.filter(item=>item.join(' ').toLowerCase().includes(q));document.querySelector('#{table_id}').innerHTML=rows.length?rows.map(item=>`<tr>{cells}</tr>`).join(''):'<tr><td class="empty" colspan="{len(fields)}">No matching records.</td></tr>'}};search.addEventListener('input',render);render()</script>'''
    else:
        rows = "".join(
            "<tr>" + "".join(
                f'<td><a href="{esc(item.get(field, ""))}" target="_blank" rel="noopener">{esc(item.get(field, ""))}</a></td>'
                if field == link_field else f'<td>{esc(item.get(field, ""))}</td>'
                for field in fields
            ) + "</tr>"
            for item in ordered_records
        )
    table_body = f'''<div class="table-wrap" style="margin-top:24px"><table><thead><tr>{column_html}</tr></thead><tbody id="{table_id}">{rows}</tbody></table></div>'''
    status_badge = '<span style="display:inline-flex;align-items:center;padding:9px 14px;border:1px solid #edcf7a;border-radius:5px;background:#fff4d8;color:#8a5a00;font:700 .75rem/1 JetBrains Mono,monospace;letter-spacing:.04em"><span style="color:#9a731f;font-weight:600;margin-right:6px">Catalog status:</span> Draft</span>'
    body = hero("Interface catalog", title, description, status="Draft") + f'''<section class="section"><div class="notice" style="margin:0 0 24px"><strong>Note</strong><br>{esc(draft_note)}</div><div class="api-controls">{search}</div>{table_body}</section>'''
    body += script
    (ROOT / output_file).write_text(shell(f"{title} | RDKE", active, body), encoding="utf-8")


def build(page: str) -> None:
    from gen_base_page import build_home
    from gen_component_registry_page import build_components
    from gen_hwcompat_page import build_hardware
    from gen_nbi_page import build_northbound
    from gen_sbi_page import build_southbound

    if page in ("all", "home"):
        build_home()
    if page in ("all", "components"):
        build_components()
    if page in ("all", "northbound"):
        build_northbound()
    if page in ("all", "southbound"):
        build_southbound()
    if page in ("all", "hardware"):
        build_hardware()


def check() -> None:
    required = ["index.html", "component-registry.html", "northbound-apis.html", "southbound-apis.html", "hardware-specifications.html"]
    missing = [name for name in required if not (ROOT / name).exists()]
    if missing:
        raise SystemExit("Missing generated pages: " + ", ".join(missing))
    for name in ("home-content.json", "components.json", "southbound-apis.json", "hardware-spec.json"):
        load(name)
    print(f"RDKE build check passed: {len(load('components.json')['components'])} components")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", choices=["all", "home", "components", "northbound", "southbound", "hardware"], default="all")
    parser.add_argument("--check", action="store_true", help="Validate inputs and generated page presence")
    args = parser.parse_args()
    build(args.page)
    if args.check:
        check()
