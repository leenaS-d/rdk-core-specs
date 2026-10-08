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

"""One-time generator for south-bound-apis.html.

Same two-level pattern as gen_nbi_page.py (list -> click -> fetch raw JSON
from GitHub -> render), but for the rdkb-halif-* HAL interface repos instead
of DML/TR-181 data. Unlike north-bound-apis.html, there's no separate
"components/ethwan-router-components.json" backing list to join against --
hal-repos.json IS the full list here, since HAL interfaces are a standalone
set of repos, not tied to the broadband device-profile component list.

Which HAL interfaces exist, which repo, which branch (defaults to main),
and which filename is controlled entirely by hal-repos.json -- same
{repo, file, branch} shape as dml-repos.json. Add a line there as a new HAL
repo publishes its spec JSON; no code changes needed.

The exact JSON shape emit_hal_spec_json.py produces per repo isn't
independently known here (custom in-house tooling, not a public schema), so
rendering is intentionally generic: render any flat array of objects as a
table, otherwise fall back to a readable JSON tree. This is the same
fallback gen_nbi_page.py already uses successfully for DML shapes it
doesn't specifically recognize.

This is a static, one-time-generated page -- rerun only if the page design
changes, not for new data (new HAL repos come from editing hal-repos.json).

Usage:
    python3 gen_sbi_page.py --out-dir .
"""
from __future__ import annotations

import argparse
from pathlib import Path

from layout import render_hero, render_page

SCRIPT = r"""
<script>
const REPO_MAP_JSON = 'hal-repos.json';
const LOCAL_BASE = 'docs/llapis/'; // local mirror — docs/llapis/<repo>/<file>

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s ?? '';
  return d.innerHTML;
}

// hal-repos.json entries can be either:
//   "Display Name": "RepoSlug"                                             (file falls back to repo-slug guess, branch defaults to main)
//   "Display Name": { "repo": "RepoSlug", "file": "custom.json" }           (explicit filename, still main)
//   "Display Name": { "repo": "RepoSlug", "file": "custom.json", "branch": "develop" }  (explicit filename + branch)
function resolveRepoEntry(mapValue, repoFallback) {
  if (typeof mapValue === 'string') return { repo: mapValue, file: repoFallback + '.json', branch: 'main' };
  return { repo: mapValue.repo, file: mapValue.file, branch: mapValue.branch || 'main' };
}

// ---- generic fallback renderer, used only if a repo's JSON doesn't match
// the {component, headers: [{file, api_count, apis: [...]}], ...} shape
// emit_hal_spec_json.py actually produces ----
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

// ---- dedicated renderer for emit_hal_spec_json.py's actual shape:
// { component, repo_dir, generated_at, total_api_count,
//   headers: [ { file, api_count, apis: [ {name, return_type, params,
//     param_count, signature, brief, params_doc, return_doc, deprecated,
//     line}, ... ] } ] } ----
function renderParamsTable(params, paramsDoc) {
  if (!params || !params.length) return '';
  return `<table class="hal-params"><thead><tr><th>Type</th><th>Name</th><th>Description</th></tr></thead><tbody>` +
    params.map(p => `<tr><td class="mono">${esc(p.type)}</td><td class="mono">${esc(p.name)}</td><td>${esc((paramsDoc && paramsDoc[p.name]) || '—')}</td></tr>`).join('') +
    `</tbody></table>`;
}

function formatDoc(text) {
  if (!text) return '';
  // Source doc-comments use a literal "\n" marker between sentences rather
  // than an actual newline; render each on its own line for readability.
  return esc(text).split('\\n').map(s => s.trim()).filter(Boolean).join('<br>');
}

function renderApiCard(api) {
  const deprecatedBadge = api.deprecated ? '<span class="hal-badge hal-badge-deprecated">deprecated</span>' : '';
  return `<div class="hal-api-card">
    <div class="hal-api-head">
      <span class="hal-api-name">${esc(api.name)}</span>
      <span class="hal-api-rt mono">${esc(api.return_type)}</span>
      ${deprecatedBadge}
    </div>
    <pre class="hal-api-sig">${esc(api.signature)}</pre>
    ${api.brief ? `<p class="hal-api-brief">${formatDoc(api.brief)}</p>` : ''}
    ${renderParamsTable(api.params, api.params_doc)}
    ${api.return_doc ? `<div class="hal-api-return"><strong>Returns:</strong> ${formatDoc(api.return_doc)}</div>` : ''}
    <div class="hal-api-meta">line ${esc(api.line)}</div>
  </div>`;
}

function renderHalSpecShape(data) {
  let out = `<div class="hal-summary">`;
  if (data.component) out += `<span><strong>Component:</strong> ${esc(data.component)}</span>`;
  if (data.repo_dir) out += `<span><strong>Repo:</strong> ${esc(data.repo_dir)}</span>`;
  if (data.generated_at) out += `<span><strong>Generated:</strong> ${esc(data.generated_at)}</span>`;
  out += `</div>`;
  for (const h of data.headers) {
    out += `<div class="hal-file-head"><span class="mono">${esc(h.file)}</span><span class="hal-file-count">${esc(h.api_count)} ${h.api_count === 1 ? 'API' : 'APIs'}</span></div>`;
    out += h.apis.map(renderApiCard).join('');
  }
  return out;
}

function isHalSpecShape(data) {
  return data && typeof data === 'object' && Array.isArray(data.headers) &&
    data.headers.every(h => h && typeof h.file === 'string' && Array.isArray(h.apis));
}

function renderHalPayload(data) {
  if (isHalSpecShape(data)) {
    return { count: data.total_api_count ?? null, html: renderHalSpecShape(data) };
  }
  const records = findRecordArray(data);
  const count = records ? records.length : null;
  const body = records ? renderRecordTable(records) : renderTree(data);
  return { count, html: body };
}

// ---- page state ----
let halNames = [];
let repoMap = {};

function halRowHtml(name) {
  const repoEntry = repoMap[name];
  const isTbd = !repoEntry || repoEntry.repo === 'TBD';
  const version = isTbd ? 'TBD' : (repoEntry.branch || 'main');
  const versionPill = isTbd
    ? `<span class="ver-pill ver-pill-tbd">${esc(version)}</span>`
    : `<span class="ver-pill">${esc(version)}</span>`;
  const action = !isTbd
    ? `<button class="dml-btn" data-name="${esc(name)}">View HAL APIs</button>`
    : `<span class="muted" style="font-size:0.85rem;">Not available yet</span>`;
  return `<tr>
    <td>${esc(name)}</td>
    <td>${versionPill}</td>
    <td>${action}</td>
  </tr>`;
}

function renderHalTable(filterText) {
  const q = (filterText || '').trim().toLowerCase();
  const available = halNames.filter(n => repoMap[n] && repoMap[n].repo !== 'TBD');
  const rows = available.filter(n => !q || n.toLowerCase().includes(q));
  document.getElementById('hal-table-body').innerHTML = rows.map(halRowHtml).join('');
  document.getElementById('hal-count').textContent = `${rows.length} of ${available.length} HAL interfaces`;
  document.querySelectorAll('.dml-btn').forEach(btn => {
    btn.addEventListener('click', () => loadHal(btn.dataset.name));
  });
}

function loadHal(name) {
  const raw = repoMap[name];
  const repoSlug = typeof raw === 'string' ? raw : raw.repo;
  const { repo, file, branch } = resolveRepoEntry(raw, repoSlug);
  const panel = document.getElementById('hal-panel');
  const url = LOCAL_BASE + repo + '/' + file; // served from docs/llapis/<repo>/<file>
  panel.innerHTML = `
    <div class="subhead" style="margin-top:0;">${esc(name)} <span class="mono" style="font-weight:400;font-size:0.8rem;color:var(--muted);">// ${esc(repo)}</span></div>
    <p>Loading <code>${esc(url)}</code>…</p>`;
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });

  fetch(url, { cache: 'no-store' })
    .then(res => { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
    .then(data => {
      const { count, html } = renderHalPayload(data);
      panel.innerHTML = `
        <div class="subhead" style="margin-top:0;">${esc(name)}${count !== null ? ` <span class="mono" style="font-weight:400;font-size:0.8rem;color:var(--muted);">(${count} APIs)</span>` : ''}</div>
        <p><a href="${esc(url)}" target="_blank" rel="noopener">${esc(url)}</a></p>
        ${html}`;
    })
    .catch(err => {
      panel.innerHTML = `
        <div class="empty-state">
          <div class="icon">⚠️</div>
          <h3>Could not load HAL spec for ${esc(name)}</h3>
          <p>Tried: <code>${esc(url)}</code></p>
          <p style="margin-top:8px;">${esc(err.message)}</p>
        </div>`;
    });
}

fetch(REPO_MAP_JSON, { cache: 'no-store' })
  .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
  .then(repoMapData => {
    repoMap = repoMapData;
    delete repoMap._comment;
    halNames = Object.keys(repoMap).sort((a, b) => a.localeCompare(b));
    renderHalTable('');
    document.getElementById('hal-search').addEventListener('input', e => renderHalTable(e.target.value));
  })
  .catch(err => {
    document.getElementById('hal-table-wrap').innerHTML = `
      <div class="empty-state">
        <div class="icon">📄</div>
        <h3>Could not load HAL interface list</h3>
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
  .search-row #hal-count { font-size: 0.85rem; color: var(--muted); white-space: nowrap; margin-left: 4px; }
  .ver-pill {
    display: inline-block; padding: 3px 10px; border-radius: 8px; font-size: 0.82rem;
    font-family: monospace; background: #f0f9ff; color: #0369a1; line-height: 1.5;
  }
  .ver-pill-tbd { background: #f3f4f6; color: #9ca3af; }
  .dml-btn {
    display: inline-block; padding: 7px 20px; border-radius: 999px; font-size: 0.88rem;
    font-weight: 700; cursor: pointer; border: none; background: #e8eef8; color: #2d4eb5;
  }
  .dml-btn:hover { background: #d5e0f3; color: #1e3fa0; }
  #hal-panel { margin-top: 20px; }

  /* ---- HAL API card rendering (emit_hal_spec_json.py shape) ---- */
  .hal-summary {
    display: flex; flex-wrap: wrap; gap: 18px; font-size: 0.82rem; color: var(--muted);
    padding: 10px 14px; background: #f8fafc; border: 1px solid var(--border); border-radius: 8px;
    margin-bottom: 16px;
  }
  .hal-summary strong { color: var(--ink); font-weight: 600; }
  .hal-file-head {
    display: flex; justify-content: space-between; align-items: center;
    background: var(--hal); color: #fff; padding: 9px 14px; border-radius: 8px;
    margin: 22px 0 10px; font-size: 0.85rem; font-weight: 600;
  }
  .hal-file-head:first-of-type { margin-top: 4px; }
  .hal-file-count { font-weight: 500; font-size: 0.78rem; opacity: 0.85; }
  .hal-api-card {
    border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px;
    margin-bottom: 12px; box-shadow: var(--shadow-sm);
  }
  .hal-api-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 6px; }
  .hal-api-name { font-family: "JetBrains Mono", monospace; font-weight: 700; font-size: 0.95rem; color: var(--ink); }
  .hal-api-rt { font-size: 0.78rem; color: #4338ca; background: #eef2ff; padding: 2px 8px; border-radius: 999px; }
  .hal-badge { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; padding: 2px 8px; border-radius: 999px; }
  .hal-badge-deprecated { background: #fee2e2; color: #991b1b; }
  .hal-api-sig {
    font-family: "JetBrains Mono", monospace; font-size: 0.8rem; color: var(--muted);
    background: #f8fafc; border-radius: 6px; padding: 8px 12px; overflow-x: auto; margin: 0 0 8px;
    white-space: pre-wrap;
  }
  .hal-api-brief { font-size: 0.86rem; color: var(--ink); margin: 0 0 10px; line-height: 1.55; }
  table.hal-params { width: 100%; border-collapse: collapse; margin: 0 0 10px; font-size: 0.82rem; }
  table.hal-params th {
    text-align: left; padding: 6px 10px; font-size: 0.7rem; text-transform: uppercase;
    letter-spacing: 0.03em; color: var(--muted); border-bottom: 1px solid var(--border);
  }
  table.hal-params td { padding: 6px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }
  .hal-api-return { font-size: 0.84rem; color: var(--muted); margin-bottom: 6px; }
  .hal-api-meta { font-size: 0.72rem; color: #9ca3af; font-family: "JetBrains Mono", monospace; }
</style>
"""


def build_page() -> str:
    body = f'''
{render_hero("South-bound APIs", "South-bound APIs",
    "Hardware Abstraction Layer (HAL) specifications to aid silicon platform porting.",
    compact=True, visual_key="sbi")}

<section class="tight-top">
  <div id="hal-table-wrap">
    <div class="search-row">
      <input id="hal-search" type="text" placeholder="Filter HAL interfaces…">
      <span id="hal-count" class="mono"></span>
    </div>
    <table class="def-table">
      <thead><tr><th>HAL Interface</th><th>Version</th><th>APIs</th></tr></thead>
      <tbody id="hal-table-body">
        <tr><td colspan="3">Loading HAL interfaces…</td></tr>
      </tbody>
    </table>
  </div>

  <div id="hal-panel"></div>
</section>
'''
    head_extra = "<title>South-bound APIs — RDK-B Core Broadband</title>\n" + EXTRA_CSS + SCRIPT
    return render_page("sbi", head_extra, body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "south-bound-apis.html"
    path.write_text(build_page(), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
