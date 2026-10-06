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

"""One-time generator for north-bound-apis.html.

Unlike the other stub pages (gen_stub_pages.py), this one isn't a generic
"fetch one JSON/XML file" template — it's a two-level page:

  1. A table of every component, built from components/all-components.json
     (every RDK-B Core Broadband component relevant to any device profile --
     the North Bound API surface isn't scoped to one profile, so this list
     isn't either).
  2. Clicking a component with a known DML source fetches
     docs/hlapis/<repo>/<file> (local mirror; no network fetch needed) and
     renders it. Which components have a DML source, which repo, which
     branch (defaults to main), and which filename is controlled entirely
     by dml-repos.json — a component's data file doesn't have to be
     literally named dml.json or live on main (e.g. wanmanager_interface_v3.json
     on main, ethagent_interface_v1.json on develop both work), no
     HTML/script changes needed either way.
  3. Renders whatever shape the file turns out to be: a real TR-181-style
     export ({componentInterfaceDefinition, elements: {"Device.X...": {...}}}),
     a simpler {objects, parameters} export, a flat array, or anything else
     (falls back to a readable JSON tree).

This is still a static, one-time-generated page — rerun this only if the
page's design changes, not for new data (new components come from
re-running build_site.py's xlsx step; new DML repos come from editing
dml-repos.json).

Usage:
    python3 gen_nbi_page.py --out-dir .
"""
from __future__ import annotations

import argparse
from pathlib import Path

from layout import render_hero, render_page

SCRIPT = r"""
<script>
const COMPONENTS_JSON = 'components/all-components.json';
const REPO_MAP_JSON = 'dml-repos.json';
const LOCAL_BASE = 'docs/hlapis/'; // local mirror — docs/hlapis/<repo>/<file>

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s ?? '';
  return d.innerHTML;
}

// dml-repos.json entries can be either:
//   "Component Name": "RepoSlug"                                  (file defaults to dml.json, branch defaults to main)
//   "Component Name": { "repo": "RepoSlug", "file": "custom.json" }                    (explicit filename, still main)
//   "Component Name": { "repo": "RepoSlug", "file": "custom.json", "branch": "develop" } (explicit filename + branch)
// so each component's data file doesn't have to be literally named dml.json,
// or live on main -- some repos publish their interface file on develop or
// another branch before it's merged.
function resolveRepoEntry(mapValue) {
  if (typeof mapValue === 'string') return { repo: mapValue, file: 'dml.json', branch: 'main' };
  return { repo: mapValue.repo, file: mapValue.file || 'dml.json', branch: mapValue.branch || 'main' };
}

// ---- generic renderer for whatever shape dml.json turns out to be ----
function findRecordArray(value) {
  if (Array.isArray(value)) return value;
  if (value && typeof value === 'object') {
    for (const v of Object.values(value)) {
      const found = findRecordArray(v);
      if (found) return found;
    }
  }
  return null;
}

function renderRecordTable(rows) {
  const isFlatObjectArray = rows.every(r => r && typeof r === 'object' && !Array.isArray(r));
  if (!isFlatObjectArray) {
    return '<ul style="list-style:none;padding:0;">' +
      rows.map(r => `<li style="padding:9px 12px;border-bottom:1px solid var(--border);font-family:'JetBrains Mono',monospace;font-size:0.85rem;">${esc(String(r))}</li>`).join('') +
      '</ul>';
  }
  const cols = Object.keys(rows[0]);
  return `<table class="def-table"><thead><tr>${cols.map(c => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>` +
    rows.map(r => `<tr>${cols.map(c => `<td class="mono">${esc(typeof r[c] === 'object' ? JSON.stringify(r[c]) : r[c])}</td>`).join('')}</tr>`).join('') +
    '</tbody></table>';
}

function renderTree(value) {
  return `<pre style="background:#0b1220;color:#cbd5e1;padding:20px;border-radius:10px;overflow-x:auto;font-size:0.82rem;max-height:600px;">${esc(JSON.stringify(value, null, 2))}</pre>`;
}

// ---- BBF-style hierarchical tree (matches the official TR-181 USP HTML
// data model browser layout: Device. -> Device.X_RDK_WanManager. -> nested
// objects, each showing its own parameters before its child objects) ----

function isObjectPath(path) {
  return path.trim().endsWith('.');
}

function buildBbfTree(elements) {
  // root node represents the implicit top-level "Device" umbrella; every
  // element's path is threaded down through it segment by segment.
  const root = { name: 'Device', children: {}, own: null };
  for (const [path, meta] of Object.entries(elements)) {
    const clean = path.trim().replace(/\.$/, '');
    const segments = clean.split('.');
    let node = root;
    for (let i = 1; i < segments.length; i++) { // start at 1: segment 0 is always "Device" itself
      const seg = segments[i];
      if (!node.children[seg]) node.children[seg] = { name: seg, children: {}, own: null };
      node = node.children[seg];
    }
    node.own = { path, meta, isObject: isObjectPath(path) };
  }
  return root;
}

function isNumberOfEntriesName(name) {
  return /NumberOfEntries$/i.test(name);
}

function splitLeafAndObjectChildren(node) {
  const entries = Object.entries(node.children);
  const leaves = [];
  const objects = [];
  for (const [name, child] of entries) {
    const hasGrandchildren = Object.keys(child.children).length > 0;
    if (hasGrandchildren || (child.own && child.own.isObject)) {
      objects.push([name, child]);
    } else {
      leaves.push([name, child]);
    }
  }
  // BBF convention: *NumberOfEntries parameters first, then the rest
  // alphabetically (the source data carries no explicit schema order, so
  // alphabetical is the most defensible default for everything else).
  leaves.sort(([a], [b]) => {
    const aNoe = isNumberOfEntriesName(a), bNoe = isNumberOfEntriesName(b);
    if (aNoe !== bNoe) return aNoe ? -1 : 1;
    return a.localeCompare(b);
  });
  objects.sort(([a], [b]) => a.localeCompare(b));
  return { leaves, objects };
}

function renderParamRow(name, child, pathPrefix) {
  const meta = child.own ? child.own.meta : {};
  const type = meta.type || '';
  const access = Array.isArray(meta.access) ? meta.access.join(', ') : (meta.access || '');
  const desc = (meta.description || '').trim();
  const isMethod = name.endsWith('()');
  const isEvent = Array.isArray(meta.access) && meta.access.includes('subscribeOnChange') && !type;
  const isCount = isNumberOfEntriesName(name);

  let rowClass = 'bbf-row-param';
  let tag = '';
  if (isCount) { rowClass = 'bbf-row-count'; tag = '<span class="bbf-tag bbf-tag-count">count</span>'; }
  else if (isMethod) { rowClass = 'bbf-row-method'; tag = '<span class="bbf-tag bbf-tag-method">method</span>'; }
  else if (isEvent) { rowClass = 'bbf-row-event'; tag = '<span class="bbf-tag bbf-tag-event">event</span>'; }

  const descCell = desc
    ? `<td class="bbf-desc">${esc(desc)}</td>`
    : `<td class="bbf-desc bbf-desc-empty">not documented</td>`;

  return `<tr class="${rowClass}">
    <td class="bbf-name">${esc(name)}${tag}</td>
    <td class="bbf-type">${esc(type || (isMethod ? 'method' : ''))}</td>
    <td class="bbf-access">${esc(access)}</td>
    ${descCell}
  </tr>`;
}

function renderObjectNode(node, pathPrefix, depth) {
  const { leaves, objects } = splitLeafAndObjectChildren(node);
  const fullPath = pathPrefix + node.name + (Object.keys(node.children).length ? '.' : '');
  const meta = node.own ? node.own.meta : {};
  const headClass = 'bbf-object-head' + (leaves.length ? ' bbf-object-head-with-table' : '');
  let html = `<div style="margin-left:${depth * 18}px; margin-bottom:18px;">`;
  html += `<div class="${headClass}" style="font-size:${depth === 0 ? '0.95rem' : '0.86rem'};">${esc(fullPath)}${leaves.length ? `<span class="bbf-count">${leaves.length} ${leaves.length === 1 ? 'entry' : 'entries'}</span>` : ''}</div>`;
  if (meta.description && meta.description.trim()) {
    html += `<p class="bbf-desc">${esc(meta.description)}</p>`;
  }
  if (leaves.length) {
    html += `<div class="bbf-table-wrap"><table class="bbf-table"><thead><tr><th>Name</th><th>Type</th><th>Access</th><th>Description</th></tr></thead><tbody>` +
      leaves.map(([name, child]) => renderParamRow(name, child, fullPath)).join('') +
      `</tbody></table></div>`;
  }
  html += '</div>';
  for (const [, child] of objects) {
    html += renderObjectNode(child, fullPath, depth + 1);
  }
  return html;
}

function renderBbfTree(elements) {
  const root = buildBbfTree(elements);
  // root itself ("Device") is never a real object with its own params --
  // skip straight to rendering its real children (e.g. X_RDK_WanManager).
  const { objects } = splitLeafAndObjectChildren(root);
  if (!objects.length) return renderTree(elements); // defensive fallback, shouldn't normally happen
  return `<div class="bbf-object-head bbf-object-head-root">Device.</div>` +
    objects.map(([, child]) => renderObjectNode(child, 'Device.', 0)).join('');
}

function renderDmlPayload(data) {
  // Shape A: { componentInterfaceDefinition: {...}, elements: { "Device.X...": {...}, ... } }
  // A real TR-181-style export, keyed by full parameter path rather than an
  // array. Rendered as a genuine hierarchical tree matching the BBF USP HTML
  // data model browser convention (e.g. tr-181-2-21-0-usp.html): Device. ->
  // Device.X_RDK_WanManager. -> nested objects, each object showing its own
  // direct parameters before its child objects, with *NumberOfEntries
  // parameters hoisted to the top of that list (BBF convention: the count
  // parameter for a table is documented immediately under its parent
  // object, ahead of the table's own row schema).
  if (data && typeof data === 'object' && data.elements && typeof data.elements === 'object' && !Array.isArray(data.elements)) {
    const def = data.componentInterfaceDefinition || {};
    let out = '';
    if (def.name || def.description) {
      out += `<div class="card" style="margin-bottom:16px;">
        <h3>${esc(def.name || 'Interface')}${def.version ? ' <span class="mono" style="font-weight:400;font-size:0.8rem;color:var(--muted);">v' + esc(def.version) + '</span>' : ''}</h3>
        <p style="margin-bottom:6px;">${esc(def.description || '')}</p>
        <p class="mono" style="font-size:0.78rem; margin-bottom:0;">${esc(def.moduleName || '')}${def.generated ? ' · generated ' + esc(def.generated) : ''}</p>
      </div>`;
    }
    out += renderBbfTree(data.elements);
    return out;
  }

  // Shape B: a DML export that already separates "objects" from "parameters"
  // as flat arrays -- render each as its own table when present, otherwise
  // fall back to the generic array/tree detection.
  if (data && typeof data === 'object' && !Array.isArray(data) && (data.objects || data.parameters)) {
    let out = '';
    if (data.objects) {
      out += `<div class="subhead" style="margin-top:0;">Objects (${data.objects.length})</div>` + renderRecordTable(data.objects);
    }
    if (data.parameters) {
      out += `<div class="subhead">Parameters (${data.parameters.length})</div>` + renderRecordTable(data.parameters);
    }
    return out;
  }
  const records = findRecordArray(data);
  return records ? renderRecordTable(records) : renderTree(data);
}

// ---- page state ----
let allComponents = [];
let repoMap = {};

function componentRowHtml(c) {
  const repoEntry = repoMap[c.name];
  const action = repoEntry
    ? `<button class="dml-btn" data-name="${esc(c.name)}">View DML</button>`
    : `<span class="muted" style="font-size:0.85rem;">Not available yet</span>`;
  return `<tr>
    <td>${esc(c.name)}</td>
    <td><span class="tbl-pill">${esc(c.category || 'Uncategorized')}</span></td>
    <td>${action}</td>
  </tr>`;
}

function renderComponentTable(filterText) {
  const q = (filterText || '').trim().toLowerCase();
  const rows = allComponents.filter(c => repoMap[c.name] && (!q || c.name.toLowerCase().includes(q) || (c.category || '').toLowerCase().includes(q)));
  document.getElementById('component-table-body').innerHTML = rows.map(componentRowHtml).join('');
  document.getElementById('component-count').textContent = `${rows.length} of ${allComponents.filter(c => repoMap[c.name]).length} components`;
  document.querySelectorAll('.dml-btn').forEach(btn => {
    btn.addEventListener('click', () => loadDml(btn.dataset.name));
  });
}

function loadDml(name) {
  const { repo, file, branch } = resolveRepoEntry(repoMap[name]);
  const panel = document.getElementById('dml-panel');
  const url = LOCAL_BASE + repo + '/' + file;
  panel.innerHTML = `
    <div class="subhead" style="margin-top:0;">${esc(name)} <span class="mono" style="font-weight:400;font-size:0.8rem;color:var(--muted);">// ${esc(repo)}</span></div>
    <p>Loading <code>${esc(url)}</code>&hellip;</p>`;
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });

  fetch(url, { cache: 'no-store' })
    .then(res => { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
    .then(data => {
      panel.innerHTML = `
        <div class="subhead" style="margin-top:0;">${esc(name)} <span class="mono" style="font-weight:400;font-size:0.8rem;color:var(--muted);">// ${esc(repo)}</span></div>
        <p><a href="${esc(url)}" target="_blank" rel="noopener">${esc(url)}</a></p>
        ${renderDmlPayload(data)}`;
    })
    .catch(err => {
      panel.innerHTML = `
        <div class="empty-state">
          <div class="icon">⚠️</div>
          <h3>Could not load DML for ${esc(name)}</h3>
          <p>Tried: <code>${esc(url)}</code></p>
          <p style="margin-top:8px;">${esc(err.message)}</p>
        </div>`;
    });
}

Promise.all([
  fetch(COMPONENTS_JSON, { cache: 'no-store' }).then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }),
  fetch(REPO_MAP_JSON, { cache: 'no-store' }).then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }),
]).then(([componentsData, repoMapData]) => {
  allComponents = componentsData.components;
  repoMap = repoMapData;
  delete repoMap._comment;
  renderComponentTable('');
  document.getElementById('component-search').addEventListener('input', e => renderComponentTable(e.target.value));
}).catch(err => {
  document.getElementById('component-table-wrap').innerHTML = `
    <div class="empty-state">
      <div class="icon">📄</div>
      <h3>Could not load component list</h3>
      <p>${esc(err.message)}</p>
    </div>`;
});
</script>
"""

EXTRA_CSS = """
<style>
  .search-row { margin-bottom: 12px; display: flex; align-items: center; gap: 8px; width: 100%; }
  .search-row input {
    flex: 1; min-width: 0; padding: 9px 14px; border: 1px solid var(--border); border-radius: 6px;
    font-family: inherit; font-size: 0.9rem;
  }
  .search-row #component-count { font-size: 0.85rem; color: var(--muted); white-space: nowrap; margin-left: 4px; }
  .dml-btn {
    display: inline-block; padding: 7px 20px; border-radius: 999px; font-size: 0.88rem;
    font-weight: 700; cursor: pointer; border: none; background: #e8eef8; color: #2d4eb5;
  }
  .dml-btn:hover { background: #d5e0f3; color: #1e3fa0; }
  #dml-panel { margin-top: 20px; }

  /* ---- BBF-inspired DML tree styling ---- */
  .bbf-object-head {
    background: linear-gradient(135deg, #fef9e7, #fef3c7); border: 1px solid #fde68a;
    border-radius: 8px; padding: 8px 14px; margin: 4px 0 0;
    font-family: "JetBrains Mono", monospace; font-weight: 700; color: #78350f;
  }
  .bbf-object-head-root {
    background: linear-gradient(135deg, #451a03, #78350f); border-color: #78350f;
    color: #fef3c7; font-size: 1rem; margin-bottom: 14px; box-shadow: var(--shadow-sm);
  }
  .bbf-object-head-with-table { border-radius: 8px 8px 0 0; margin-bottom: 0; }
  .bbf-object-head .bbf-count { font-weight: 500; font-size: 0.78rem; color: #92400e; margin-left: 8px; }
  .bbf-object-head-root .bbf-count { color: #fde68a; }
  .bbf-desc { font-size: 0.82rem; color: var(--muted); margin: 8px 0 0; padding: 0 14px; }
  .bbf-table-wrap {
    border: 1px solid var(--border); border-top: none; border-radius: 0 0 10px 10px;
    overflow: hidden; box-shadow: var(--shadow-sm); margin-bottom: 8px;
  }
  table.bbf-table { width: 100%; border-collapse: collapse; margin: 0; font-size: 0.85rem; }
  table.bbf-table th {
    background: #eef1f6; text-align: left; padding: 8px 12px; font-size: 0.72rem;
    text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); border-bottom: 2px solid var(--border);
  }
  table.bbf-table td { padding: 8px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
  table.bbf-table tbody tr.bbf-row-param:nth-child(even) { background: #f8fafc; }
  table.bbf-table tr.bbf-row-count { background: #eef2ff; }
  table.bbf-table tr.bbf-row-method { background: #ecfdf5; }
  table.bbf-table tr.bbf-row-event { background: #eff6ff; }
  table.bbf-table tr.bbf-row-param:hover,
  table.bbf-table tr.bbf-row-count:hover,
  table.bbf-table tr.bbf-row-method:hover,
  table.bbf-table tr.bbf-row-event:hover { filter: brightness(0.97); }
  table.bbf-table td.bbf-name { font-family: "JetBrains Mono", monospace; font-weight: 600; color: var(--ink); }
  table.bbf-table td.bbf-type { font-family: "JetBrains Mono", monospace; font-size: 0.8rem; color: #4338ca; }
  table.bbf-table td.bbf-access { font-size: 0.8rem; }
  table.bbf-table td.bbf-desc { color: var(--muted); font-size: 0.8rem; }
  table.bbf-table td.bbf-desc.bbf-desc-empty { color: #cbd5e1; font-style: italic; }
  .bbf-tag {
    display: inline-block; font-size: 0.64rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.03em; padding: 2px 7px; border-radius: 999px; margin-left: 7px;
  }
  .bbf-tag-count { background: #e0e7ff; color: #3730a3; }
  .bbf-tag-method { background: #d1fae5; color: #065f46; }
  .bbf-tag-event { background: #dbeafe; color: #1e40af; }
</style>
"""


def build_page() -> str:
    body = f'''
{render_hero("North-bound APIs", "North-bound APIs",
    "APIs that can be used by applications to access system services and resources.",
    compact=True, visual_key="nbi")}

<section class="tight-top">
  <div id="component-table-wrap">
    <div class="search-row">
      <input id="component-search" type="text" placeholder="Filter components…">
      <span id="component-count" class="mono"></span>
    </div>
    <table class="def-table">
      <thead><tr><th>Component</th><th>Category</th><th>DML</th></tr></thead>
      <tbody id="component-table-body">
        <tr><td colspan="3">Loading components…</td></tr>
      </tbody>
    </table>
  </div>

  <div id="dml-panel"></div>
</section>
'''
    head_extra = "<title>North-bound APIs — RDK-B Core Broadband</title>\n" + EXTRA_CSS + SCRIPT
    return render_page("nbi", head_extra, body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "north-bound-apis.html"
    path.write_text(build_page(), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
