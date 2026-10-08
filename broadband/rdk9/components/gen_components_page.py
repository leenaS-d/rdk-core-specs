# If not stated otherwise in this file or this component's LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2023 RDK Management
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generate components/index.html from ethwan-router-components.json, using
the same shared site shell (topnav + hero banner) as every other page —
unlike full-list.html or the other gen_*.py outputs in this folder, this one
now goes through layout.py's render_page()/render_hero()/render_topnav()
instead of a standalone hand-authored <style> block.

components/index.html sits one directory below the repo root, so this script
passes path_prefix="../" to render_page() — that's what makes the logo, nav
links, and search index fetch resolve correctly from inside components/.

Usage:
    python3 gen_components_page.py --json ethwan-router-components.json --out index.html

Run this whenever ethwan-router-components.json changes (i.e. after
extract_components.py / build_site.py step 4), so the page stays in sync
with the .xlsx it's derived from.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from layout import render_hero, render_page  # noqa: E402

FULL_DETAILS_URL = "full-list.html"

TIER_DESCRIPTIONS = {
    "common-core": "Core components common across all RDK-B sub-profiles such as EthWAN Router, Gateway with DOCSIS/PON access profile support, Wifi Extender etc.",
    "required": "Core components required for the EthWAN Router sub-profile",
    "optional": "Optional components on the EthWAN Router sub-profile.",
}

# Same fixed/rotating palettes as gen_simple_html.py, kept in sync so the
# type/category pill colors look identical to the rest of the components
# tooling (full-list.html, any other gen_simple_html.py output).
TIER_COLORS = {
    "gold":  {"bg": "#fef3c7", "fg": "#92400e"},
    "blue":  {"bg": "#dbeafe", "fg": "#1e40af"},
    "gray":  {"bg": "#f3f4f6", "fg": "#374151"},
    "green": {"bg": "#d1fae5", "fg": "#065f46"},
}
CATEGORY_PALETTE = [
    {"bg": "#e8eaf6", "fg": "#1e3a5f"},
]


# Fixed style for the Layer pill (always Middleware for all RDK-B components)
LAYER_STYLE = {"bg": "#f0fdf4", "fg": "#166534"}


def category_color(category: str) -> dict:
    idx = int(hashlib.md5(category.encode("utf-8")).hexdigest(), 16) % len(CATEGORY_PALETTE)
    return CATEGORY_PALETTE[idx]


def esc(s) -> str:
    return html.escape("" if s is None else str(s))


def build_body(data: dict) -> str:
    subtitle = data.get("subtitle", "")
    schema_version = data["schemaVersion"]
    generated_at = data["generatedAt"]
    tiers = {t["id"]: t for t in data.get("tiers", [])}
    components = sorted(data["components"], key=lambda c: (c["tier"] != "common-core", c["name"].lower()))

    legend_html = (
        '<div style="display:table;border-spacing:0 6px;">' +
        "".join(
            f'<div style="display:table-row;">'
            f'<span style="display:table-cell;padding-right:12px;vertical-align:middle;white-space:nowrap;">'
            f'<span class="pill" style="background:{TIER_COLORS[t["color"]]["bg"]};color:{TIER_COLORS[t["color"]]["fg"]};">{esc(t["label"])}</span>'
            f'</span>'
            f'<span style="display:table-cell;vertical-align:middle;font-size:0.88rem;color:var(--muted);">{esc(TIER_DESCRIPTIONS.get(t["id"], ""))}</span>'
            f'</div>'
            for t in tiers.values()
        ) +
        '</div>'
    )

    # Unique categories and tier labels for filter dropdowns
    categories  = sorted({c["category"] or "Uncategorized" for c in components})
    tier_labels = sorted({tiers.get(c["tier"], {"label": c["tier"]})["label"] for c in components})
    # Layer is always Middleware for all RDK-B components
    layers = ["RDK"]

    rows_html = []
    for c in components:
        tier = tiers.get(c["tier"], {"label": c["tier"], "color": "gray"})
        tier_style = TIER_COLORS[tier["color"]]
        cat_style = category_color(c["category"] or "Uncategorized")
        url = c.get("url")
        repos = [u for u in [url, *c.get("supportingUrls", [])] if u]
        if repos:
            url_cell = '<div style="display:flex;flex-direction:column;gap:4px;">' + "".join(
                f'<a href="{esc(u)}" target="_blank" rel="noopener" style="font-size:0.86rem;">{esc(u)}</a>'
                for u in repos
            ) + '</div>'
        else:
            url_cell = '<span class="muted">—</span>'
        # data-* attrs drive JS filtering; layer is always Middleware
        version = esc(c.get("version") or "develop")
        rows_html.append(f'''<tr data-name="{esc(c["name"].lower())}" data-category="{esc(c["category"] or "Uncategorized")}" data-layer="RDK" data-type="{esc(tier["label"])}">
          <td style="font-weight:400;">{esc(c["name"])}</td>
          <td><span class="pill" style="background:#e8eef8;color:#2d4eb5;border:none;border-radius:999px;line-height:1.5;font-weight:700;">{esc(c["category"] or "Uncategorized")}</span></td>
          <td style="color:var(--muted);font-size:0.88rem;">RDK</td>
          <td><span class="type-pill" style="border-color:{tier_style["bg"]};color:{tier_style["fg"]};">{esc(tier["label"])}</span></td>
          <td style="font-family:monospace;font-size:0.85rem;color:var(--ink);">{version}</td>
          <td>{url_cell}</td>
        </tr>''')

    # Dropdown options
    cat_options   = '<option value="">All categories</option>' + "".join(
        f'<option value="{esc(c)}">{esc(c)}</option>' for c in categories)
    layer_options = '<option value="">All layers</option>' + "".join(
        f'<option value="{esc(l)}">{esc(l)}</option>' for l in layers)
    type_options  = '<option value="">All types</option>' + "".join(
        f'<option value="{esc(t)}">{esc(t)}</option>' for t in tier_labels)

    filter_bar = f"""
  <div class="comp-filter-bar">
    <input id="comp-search" type="text" placeholder="Search components" autocomplete="off">
    <select id="comp-cat">{cat_options}</select>
    <select id="comp-layer">{layer_options}</select>
    <select id="comp-type">{type_options}</select>
    <span id="comp-count" class="comp-count"></span>
  </div>"""

    filter_css = """
<style>
  .comp-filter-bar {
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 12px; width: 100%;
  }
  .comp-filter-bar input {
    flex: 2; min-width: 0;
    padding: 9px 14px; border: 1px solid var(--border); border-radius: 6px;
    font-family: inherit; font-size: 0.9rem;
    transition: border-color 0.15s;
  }
  .comp-filter-bar input:focus { outline: none; border-color: var(--middleware); }
  .comp-filter-bar select {
    flex: 1; min-width: 0;
    padding: 9px 28px 9px 12px; border: 1px solid var(--border); border-radius: 6px;
    font-family: inherit; font-size: 0.9rem; background: #fff;
    appearance: none; -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='7' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%235b6472' stroke-width='1.8' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 10px center;
    cursor: pointer; transition: border-color 0.15s;
  }
  .comp-filter-bar select:focus { outline: none; border-color: var(--middleware); }
  .comp-count { font-size: 0.84rem; color: var(--muted); white-space: nowrap; margin-left: 4px; }
  .type-pill {
    display: inline-block; padding: 3px 11px; border-radius: 999px; font-size: 0.82rem;
    font-weight: 600; background: transparent; border: 1.5px solid; line-height: 1.5;
  }
</style>"""

    filter_script = """
<script>
(function () {
  const searchEl = document.getElementById('comp-search');
  const catEl    = document.getElementById('comp-cat');
  const layerEl  = document.getElementById('comp-layer');
  const typeEl   = document.getElementById('comp-type');
  const countEl  = document.getElementById('comp-count');
  const rows     = Array.from(document.querySelectorAll('#comp-tbody tr'));

  function filter() {
    const q     = searchEl.value.trim().toLowerCase();
    const cat   = catEl.value;
    const layer = layerEl.value;
    const type  = typeEl.value;
    let visible = 0;
    rows.forEach(tr => {
      const show = (!q     || tr.dataset.name.includes(q))
                && (!cat   || tr.dataset.category === cat)
                && (!layer || tr.dataset.layer === layer)
                && (!type  || tr.dataset.type === type);
      tr.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    countEl.textContent = visible + ' of ' + rows.length + ' components';
  }

  searchEl.addEventListener('input', filter);
  catEl.addEventListener('change', filter);
  layerEl.addEventListener('change', filter);
  typeEl.addEventListener('change', filter);
  filter();
})();
</script>"""

    lede = "A list of RDK components categorized as core and optional."
    return f'''
{render_hero("Component Catalog", "EthWAN Router", lede, compact=True, visual_key="components")}

{filter_css}

<section class="tight-top">
  <p style="color:var(--muted); font-size:0.85rem; margin:0 0 14px;">
    Schema version: {esc(schema_version)} &nbsp;|&nbsp; Generated: {esc(generated_at)}
  </p>
  <div style="margin-bottom:18px;">{legend_html}</div>
  {filter_bar}
  <table class="def-table">
    <thead><tr><th>Name</th><th>Category</th><th>Layer</th><th>Type</th><th>Version</th><th>Repositories</th></tr></thead>
    <tbody id="comp-tbody">{"".join(rows_html)}</tbody>
  </table>
</section>
{filter_script}
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="ethwan-router-components.json")
    ap.add_argument("--versions", default="component-versions.json")
    ap.add_argument("--out", default="index.html")
    args = ap.parse_args()

    data = json.loads(Path(args.json).read_text(encoding="utf-8"))

    # Merge version overrides from separate versions file (if it exists)
    versions_path = Path(args.versions)
    if versions_path.exists():
        versions = json.loads(versions_path.read_text(encoding="utf-8"))
        for c in data["components"]:
            if c["name"] in versions:
                c["version"] = versions[c["name"]]

    body = build_body(data)
    page_title = data['title'].replace(" Components", "").strip()
    head_extra = f"<title>{esc(page_title)} — RDK-B Core Broadband</title>"
    html_out = render_page("components", head_extra, body, path_prefix="../")
    Path(args.out).write_text(html_out, encoding="utf-8")
    print(f"Wrote {args.out} ({len(data['components'])} components)")


if __name__ == "__main__":
    main()
