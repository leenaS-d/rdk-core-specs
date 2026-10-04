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
CONTACT_EMAIL = "LeenaSunthari_DhanapalRaju@comcast.com"


CONTACT_WIDGET = f'''<style>.site-contact-toggle{{position:fixed;right:22px;bottom:22px;z-index:20;display:grid;place-items:center;width:52px;height:52px;border:0;border-radius:50%;background:#2457d6;color:#fff;box-shadow:0 8px 22px #0b122044;cursor:pointer}}.site-contact-toggle svg{{width:23px;height:23px}}.site-contact-panel{{display:none;position:fixed;right:22px;bottom:86px;z-index:21;width:min(360px,calc(100vw - 32px));background:#fff;border:1px solid #e2e7f0;border-radius:10px;box-shadow:0 14px 36px #0b122044;overflow:hidden}}.site-contact-panel.open{{display:block}}.site-contact-head{{padding:14px 16px;background:#080d18;color:#fff}}.site-contact-head-row{{display:flex;align-items:center;justify-content:space-between}}.site-contact-note{{margin:3px 0 0;color:#9fb2cf;font-size:.72rem}}.site-contact-close{{border:0;background:none;color:#fff;font-size:1.2rem;cursor:pointer}}.site-contact-form{{display:grid;gap:10px;padding:16px}}.site-contact-form label{{display:grid;gap:4px;color:#0b1220;font-size:.78rem;font-weight:700}}.site-contact-form input,.site-contact-form textarea{{width:100%;border:1px solid #e2e7f0;border-radius:6px;padding:9px 10px;font:inherit;font-size:.85rem}}.site-contact-form textarea{{min-height:100px;resize:vertical}}.site-contact-submit{{border:0;border-radius:6px;padding:10px;background:#0aa66e;color:#fff;font-weight:700;cursor:pointer}}.site-contact-fallback{{display:none;color:#2457d6;font-size:.78rem;text-align:center}}.site-contact-status{{min-height:1.2em;margin:0;text-align:center;font-size:.78rem;color:#5b6472}}</style><button class="site-contact-toggle" id="site-contact-toggle" type="button" aria-label="Open contact form" title="Contact us"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="m3 7 9 6 9-6"></path></svg></button><section class="site-contact-panel" id="site-contact-panel" aria-label="Contact form"><div class="site-contact-head"><div class="site-contact-head-row"><strong>Contact us</strong><button class="site-contact-close" id="site-contact-close" type="button" aria-label="Close contact form">&times;</button></div><p class="site-contact-note">Send a message - we'll get it by email</p></div><form class="site-contact-form" id="site-contact-form"><label>Name<input name="name" type="text" required></label><label>Email<input name="email" type="email" required></label><label>Message<textarea name="message" required></textarea></label><button class="site-contact-submit" type="submit">Send message</button><p class="site-contact-status" id="site-contact-status" role="status"></p><a class="site-contact-fallback" id="site-contact-fallback" href="#">Open email app</a></form></section><script>(function(){{const t=document.querySelector('#site-contact-toggle'),p=document.querySelector('#site-contact-panel'),c=document.querySelector('#site-contact-close'),f=document.querySelector('#site-contact-form'),s=document.querySelector('#site-contact-status'),a=document.querySelector('#site-contact-fallback');if(!t||!p||!c||!f)return;t.addEventListener('click',()=>p.classList.toggle('open'));c.addEventListener('click',()=>p.classList.remove('open'));f.addEventListener('submit',e=>{{e.preventDefault();const b=f.querySelector('button[type=submit]'),v=Object.fromEntries(new FormData(f));b.disabled=true;s.textContent='Sending...';fetch('https://formsubmit.co/ajax/{CONTACT_EMAIL}',{{method:'POST',headers:{{'Content-Type':'application/json','Accept':'application/json'}},body:JSON.stringify({{...v,_subject:'New message from RDK8 website',_captcha:'false'}})}}).then(r=>{{if(!r.ok)throw Error();return r.json()}}).then(()=>{{s.textContent='Message sent successfully.';f.reset()}}).catch(()=>{{s.textContent='Unable to send. Use the email app option below.';a.href='mailto:{CONTACT_EMAIL}?subject='+encodeURIComponent('New message from RDK8 website')+'&body='+encodeURIComponent('Name: '+v.name+' | Email: '+v.email+' | Message: '+v.message);a.style.display='block'}}).finally(()=>b.disabled=false)}})}})();</script>'''
CONTACT_WIDGET = ""


def release_state() -> dict:
    return load("release-state.json")


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


NORTHBOUND_MENU = [
    ("firebolt-api-spec.html", "Firebolt Core API Specification"),
    ("firebolt-json-rpc.html", "Firebolt JSON-RPC Specification"),
    ("firebolt-intents.html", "Firebolt Intents Specification"),
    ("firebolt-key-codes.html", "Firebolt Key Codes Specification"),
]


def nav(active: str) -> str:
    links = [
        ("index.html", "Home", "home"),
        ("component-catalog.html", "Components Catalog", "components"),
        ("northbound-api-spec.html", "Northbound API Spec", "northbound"),
        ("southbound-api-spec.html", "Southbound API Spec", "southbound"),
    ]
    items = "".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>'
        for href, label, key in links[:2]
    )
    menu_items = "".join(f'<a href="{href}">{label}</a>' for href, label in NORTHBOUND_MENU)
    dropdown_active = "active" if active == "northbound" else ""
    items += (
        f'<details class="nav-dropdown"><summary class="nav-dropdown-summary {dropdown_active}">Northbound API Spec</summary>'
        f'<div class="nav-dropdown-menu">{menu_items}</div></details>'
    )
    items += "".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>'
        for href, label, key in links[3:]
    )
    return f'''<div class="accent"></div>
<header class="nav"><a class="brand" href="index.html"><img src="RDK-logo.png" alt="RDK"></a><nav class="navlinks">{items}</nav></header>'''


def shell(title: str, active: str, body: str, footer: str = "") -> str:
    footer_html = f'<footer class="footer"><div class="wrap">{footer}</div></footer>' if footer else ""
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
<style>.hero .wrap{{max-width:none}}.api-controls{{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap;margin-bottom:24px}}.api-controls .release-panel{{margin-bottom:0}}.api-controls .toolbar{{margin:0 0 0 auto}}.api-controls input{{min-width:260px}}.release-panel{{display:flex;gap:12px;flex-wrap:wrap}}.release-pill{{display:inline-flex;align-items:center;gap:6px;padding:9px 14px;border:1px solid var(--border);border-radius:5px;color:var(--ink);background:#fff;box-shadow:var(--shadow);font:700 .75rem/1 Consolas,monospace;letter-spacing:.04em}}.release-pill span{{color:var(--muted);font-weight:600}}.table-wrap{{overflow-x:auto;border:1px solid var(--border);border-radius:4px;background:#fff}}table{{width:100%;border-collapse:collapse;table-layout:auto}}td,th{{vertical-align:top;padding:14px 16px;line-height:1.45}}th{{white-space:nowrap}}td{{min-width:120px;white-space:pre-line}}td:first-child{{min-width:220px}}td a{{overflow-wrap:anywhere}}.pill{{display:inline-block;padding:4px 10px;border-radius:999px;background:#eaf2ff;color:#2249a2;font-size:.8rem;font-weight:700;text-decoration:none}}.pill.core{{background:#dff7ea;color:#1d6b43;border:1px solid #a8e1bd}}@media(max-width:650px){{.api-controls{{align-items:flex-start;flex-direction:column}}.api-controls .toolbar{{width:100%;margin:0}}.api-controls input{{width:100%;min-width:0}}}}</style>
<style>@media(max-width:650px){{.hero{{height:auto!important;min-height:0!important;padding:48px 20px 44px!important}}.hero h1{{font-size:clamp(1.9rem,9vw,2.8rem)!important}}.hero p{{font-size:1rem!important;line-height:1.5}}.hero .badges{{margin-top:18px}}}}</style>
<style>.status-published{{background:#e5f6eb;border-color:#9bd4aa;color:#1d6b43}}.status-published span{{color:#397a4d}}.status-draft{{background:#fff4d8;border-color:#edcf7a;color:#8a5a00}}.status-draft span{{color:#9a731f}}.version-pill{{background:#edf3ff;border-color:#b8c9ef;color:#2457d6}}.version-pill span{{color:#5873af}}</style>
<style>.api-controls{{display:grid;grid-template-columns:minmax(0,1fr) minmax(260px,auto);align-items:center;gap:20px}}.api-controls>.release-panel{{min-width:0}}.api-controls>.toolbar{{justify-self:end;margin:0;min-width:260px}}.api-controls>.catalog-search-toolbar{{grid-column:1/-1;justify-self:stretch;width:100%;min-width:0}}.catalog-search-toolbar input{{width:100%;min-width:0}}@media(max-width:650px){{.api-controls{{grid-template-columns:1fr;gap:14px}}.api-controls>.toolbar{{justify-self:stretch;width:100%;min-width:0}}}}</style>
</head>
<body>
{nav(active)}
<main>
{body}
</main>
{footer_html}
{CONTACT_WIDGET}
</body>
</html>
'''


def status_explainer() -> str:
    return '''<details style="position:relative;min-width:150px"><summary style="cursor:pointer;color:#2457d6;font-size:.84rem;font-weight:700">Status legend</summary><dl style="position:absolute;z-index:2;left:0;right:auto;top:calc(100% + 8px);width:min(420px,calc(100vw - 40px));margin:0;padding:16px 18px;border:1px solid var(--border);border-radius:6px;background:#fff;box-shadow:var(--shadow);font-size:.84rem;line-height:1.45"><dt style="font-weight:700;color:var(--ink)">Draft</dt><dd style="margin:2px 0 10px;color:var(--muted)">Specifications drafted and undergoing internal reviews and RTAB Approval</dd><dt style="font-weight:700;color:var(--ink)">Approved</dt><dd style="margin:2px 0 10px;color:var(--muted)">All review feedback has been addressed; RTAB has voted and approved the spec</dd><dt style="font-weight:700;color:var(--ink)">Published</dt><dd style="margin:2px 0 0;color:var(--muted)">Tagged and versioned against an official RDK release</dd></dl></details>'''


def hero(eyebrow: str, title: str, description: str, badges: list[str] | None = None, subtitle: str = "", subtitle_before_title: bool = False, include_release: bool = True, status: str | None = None) -> str:
    badge_html = "" if not badges else '<div class="badges">' + "".join(
        f'<span class="badge">{esc(item)}</span>' for item in badges
    ) + "</div>"
    eyebrow_html = f'<div class="eyebrow" style="font-size:1.1rem;letter-spacing:.08em">{esc(eyebrow)}</div>' if eyebrow else ""
    subtitle_html = f'<div class="hero-subtitle" style="font-size:.95rem;font-weight:600;color:#b8df63;margin:-4px 0 18px">{esc(subtitle)}</div>' if subtitle else ""
    title_html = f'<h1 style="font-size:clamp(1.9rem,3.6vw,3.5rem)">{esc(title)}</h1>'
    title_block = f"{subtitle_html}{title_html}" if subtitle_before_title else f"{title_html}{subtitle_html}"
    state = release_state() if include_release else {}
    release_html = f'<div class="release"><span>STATE: {esc(state.get("state", "Draft"))}</span><span>VERSION: {esc(state.get("version", "RDK8"))}</span><span>UPDATED: {esc(state.get("updated", "TBD"))}</span></div>' if include_release else ""
    status_class = " approved" if (status or "").casefold() in {"approved", "published"} else ""
    status_html = "" if status is None else (
        f'<div class="hero-catalog-status"><span class="hero-status-badge{status_class}"><span>Catalog status:</span> '
        f'{esc(status)}</span>{status_explainer()}</div>'
    )
    return f'''<section class="hero" style="min-height:clamp(360px,32vw,440px);padding:52px 5vw 42px;display:flex;align-items:center"><div class="wrap" style="width:100%">{eyebrow_html}{title_block}<p>{esc(description)}</p>{badge_html}{status_html}{release_html}</div></section>'''


def release_panel(label: str, state: dict | None = None, show_version: bool = True) -> str:
    state = state or release_state()
    status = state.get("state", state.get("status", "Draft"))
    status_class = "published" if str(status).casefold() == "published" else "draft"
    version_html = f'<span class="release-pill version-pill"><span>Version:</span> {esc(state.get("version", "RDK8"))}</span>' if show_version else ""
    return f'''<div class="release-panel"><span class="release-pill status-{status_class}"><span>Catalog status:</span> {esc(status)}</span>{version_html}</div>'''
def cards(items: list[list[str]]) -> str:
    return '<div class="grid">' + "".join(
        f'<article class="card"><h3>{esc(item[0])}</h3><p>{esc(item[1])}</p></article>'
        for item in items
    ) + "</div>"


def linked_cards(items: list[list[str]], links: list[str]) -> str:
    return '<div class="grid">' + "".join(
        f'<a class="card" style="display:block;text-decoration:none;color:inherit" href="{esc(links[index])}"><h3>{esc(item[0])}</h3><p>{esc(item[1])}</p></a>'
        for index, item in enumerate(items)
    ) + "</div>"


def linked_metric_cards(items: list[list[str]], links: list[str], metrics: list[object]) -> str:
    return '<div class="grid">' + "".join(
        f'<a class="card" style="display:block;text-decoration:none;color:inherit" href="{esc(links[index])}"><strong style="display:block;min-height:44px;font-size:2.4rem;color:#2457d6">{esc(metrics[index]) if metrics[index] is not None else "&nbsp;"}</strong><h3>{esc(item[0])}</h3><p>{esc(item[1])}</p></a>'
        for index, item in enumerate(items)
    ) + "</div>"


def stacked_cards(items: list[list[str]]) -> str:
    return '<div class="grid" style="max-width:980px">' + "".join(
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
    draft_note: str | None = None,
    pill_fields: list[str] | None = None,
    strip_release_path: bool = False,
    show_version: bool = True,
    show_status_explainer: bool = True,
    hero_status: str | None = None,
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
        pill_indexes = {fields.index(field) for field in (pill_fields or []) if field in fields}
        link_value = f'String(item[{link_index}]).replace(/\\/releases\\/tag\\/[^/]+\\/?$/, "")' if strip_release_path and link_index >= 0 else f'item[{link_index}]'
        cells = "".join(
            f'''<td style="white-space:pre-line"><a href="${{esc({link_value})}}" target="_blank" rel="noopener">${{esc({link_value})}}</a></td>'''
            if index == link_index else f'''<td style="white-space:pre-line">{'<span class="pill${item[' + str(index) + '].toLowerCase()==="core" ? " core" : ""}">${esc(item[' + str(index) + '])}</span>' if index in pill_indexes else '${esc(item[' + str(index) + '])}'}</td>'''
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
    note = f'<aside role="note" aria-label="Note" style="width:100%;margin:0 0 20px;padding:14px 18px;border:1px solid #edcf7a;border-left:4px solid #b45309;border-radius:8px;background:#fff4d8;color:#8a5a00;font-size:.92rem;line-height:1.5;box-shadow:var(--shadow);"><strong style="display:block;margin-bottom:4px;color:#8a5a00;font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;">Note</strong><span style="display:block;max-width:900px;">{esc(draft_note)}</span></aside>' if draft_note else ""
    status_html = status_explainer() if show_status_explainer else ""
    status_block = "" if hero_status is not None else f'<div class="api-status" style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">{release_panel("RDK8 list state", data, show_version)}{status_html}</div>'
    body = hero("Interface catalog", title, description, include_release=False, status=hero_status) + f'''<section class="section"><div class="api-controls">{status_block}{search}</div>{note}{table_body}</section>'''
    body += script
    (ROOT / output_file).write_text(shell(f"{title} | RDK8", active, body), encoding="utf-8")


def build(page: str) -> None:
    from gen_base_page import build_home
    from gen_component_registry_page import build_components
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


def check() -> None:
    required = [
        "index.html", "component-catalog.html", "northbound-api-spec.html", "southbound-api-spec.html",
        *(href for href, _ in NORTHBOUND_MENU),
    ]
    missing = [name for name in required if not (ROOT / name).exists()]
    if missing:
        raise SystemExit("Missing generated pages: " + ", ".join(missing))
    for name in ("home-content.json", "components.json", "northbound-apis.json", "southbound-apis.json"):
        load(name)
    print(f"RDKE build check passed: {len(load('components.json')['components'])} components")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", choices=["all", "home", "components", "northbound", "southbound"], default="all")
    parser.add_argument("--check", action="store_true", help="Validate inputs and generated page presence")
    args = parser.parse_args()
    build(args.page)
    if args.check:
        check()
