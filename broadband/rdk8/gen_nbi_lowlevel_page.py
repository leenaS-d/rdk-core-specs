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

"""Generator for north-bound-lowlevel-apis.html.

Unlike gen_nbi_page.py (which is a dynamic two-level component/DML browser),
this page is fully static: it documents the IPC communication matrix and links
to the reference documentation for each IPC technology used between RDK-B
components and apps.

IPC matrix:
  Component ↔ Component  →  rbus
  Component ↔ App        →  rbus
  App        ↔ Component  →  rbus
  App        ↔ App        →  rbus

Reference links:
  rbus    → docs/doxygen-out/html/index.html  (local Doxygen output; formats: html, latex, xml)

Rerun this only if the page design changes.  The content above is hard-coded
here rather than pulled from a JSON file because it's definitional architecture
policy, not a data file that grows over time.

Usage:
    python3 gen_nbi_lowlevel_page.py --out-dir .
"""
from __future__ import annotations

import argparse
from pathlib import Path

from layout import render_hero, render_page

EXTRA_CSS = """
<style>
  /* ---- IPC matrix table ---- */
  table.ipc-table {
    width: 100%; max-width: 820px; border-collapse: separate; border-spacing: 0;
    margin: 14px 0 36px; font-size: 0.92rem;
    border: 1px solid var(--border); border-radius: 12px;
    overflow: hidden; box-shadow: var(--shadow-sm);
  }
  table.ipc-table thead tr {
    background: #1a2540;
  }
  table.ipc-table th {
    font-family: "Inter", "Segoe UI", sans-serif; font-size: 0.74rem;
    text-transform: uppercase; letter-spacing: 0.07em; font-weight: 700; color: #fff;
    background: transparent;
    padding: 14px 18px; text-align: left; border-bottom: none;
  }
  table.ipc-table th:first-child { border-top-left-radius: 12px; }
  table.ipc-table th:last-child  { border-top-right-radius: 12px; }
  table.ipc-table tbody tr { border-bottom: 1px solid var(--border); }
  table.ipc-table tbody tr:last-child { border-bottom: none; }
  table.ipc-table tbody tr:nth-child(odd)  { background: #fbfcff; }
  table.ipc-table tbody tr:nth-child(even) { background: #fff; }
  table.ipc-table tbody tr:hover { background: var(--cloud-bg); }
  table.ipc-table td { padding: 14px 18px; vertical-align: middle; color: var(--muted);
                        border-right: 1px solid var(--border); }
  table.ipc-table td:last-child { border-right: none; }
  table.ipc-table td:first-child {
    color: var(--ink); font-weight: 700; font-family: "Space Grotesk", sans-serif;
    font-size: 0.94rem; border-left: 3px solid var(--rdk-blue);
    background: rgba(41,182,232,0.04); width: 35%;
  }
  /* ---- pill badges ---- */
  .ipc-pill {
    display: inline-block; font-size: 0.78rem; font-weight: 600; padding: 4px 11px;
    border-radius: 999px; margin: 2px 3px 2px 0; border: none;
  }
  .ipc-pill-rbus  { background: #e0e7ff; color: #3730a3; }
  /* ---- reference cards ---- */
  .ref-grid { display: grid; grid-template-columns: 1fr; gap: 20px; max-width: 480px; margin-top: 4px; }

  .ref-card {
    background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px;
    padding: 22px 24px; box-shadow: var(--shadow-sm); transition: box-shadow 0.15s, transform 0.15s;
  }
  .ref-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
  .ref-card.rbus { border-left: 3px solid var(--rdk-blue); }
  .ref-card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
  .ref-card-icon {
    width: 40px; height: 40px; border-radius: 10px; display: flex;
    align-items: center; justify-content: center; flex: 0 0 auto;
  }
  .ref-card-icon.rbus { background: linear-gradient(135deg,#e0e7ff,#c7d2fe); }
  .ref-card h3 { font-size: 1rem; margin-bottom: 2px; }
  .ref-card .ref-sub { font-size: 0.78rem; color: var(--muted); margin: 0; }
  .ref-card p  { font-size: 0.9rem; margin-bottom: 14px; }
  .ref-btn {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 16px; border-radius: 999px; font-size: 0.82rem; font-weight: 600;
    text-decoration: none; color: #fff;
  }
  .ref-btn.rbus { background: linear-gradient(90deg, var(--rdk-blue), #7c3aed); }
  .ref-meta {
    font-size: 0.75rem; color: var(--muted); margin-top: 10px; margin-bottom: 0;
    line-height: 1.6;
  }
  .ref-meta code { font-size: 0.72rem; background: #f1f3f9; padding: 1px 6px; border-radius: 4px; }
</style>
"""

# SVG icons inlined so the page stays self-contained (no external fetch)
_ICON_CODE = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>"""
_ICON_LAYERS = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>"""
_ICON_EXTLINK = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>"""


def build_page() -> str:
    body = f"""
{render_hero("North Bound APIs", "North Bound Low Level APIs",
    "Low-level inter-process communication (IPC) interfaces used between "
    "RDK-B components, apps, and the system layer.",
    compact=True, visual_key="nbi")}

<section class="tight-top">

  <div class="section-head">
    <span class="eyebrow-lt">IPC Communication Matrix</span>
    <h2>Component Communication Interfaces</h2>
    <p>Maps each communication pattern to the IPC technology used between
       RDK-B components and apps.</p>
  </div>

  <table class="ipc-table">
    <thead>
      <tr>
        <th>Communication Pattern</th>
        <th>IPC Technology</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Component &#8596; Component</td>
        <td><span class="ipc-pill ipc-pill-rbus">rbus</span></td>
      </tr>
      <tr>
        <td>Component &#8596; App</td>
        <td>
          <span class="ipc-pill ipc-pill-rbus">rbus</span>
        </td>
      </tr>
      <tr>
        <td>App &#8596; Component</td>
        <td>
          <span class="ipc-pill ipc-pill-rbus">rbus</span>
        </td>
      </tr>
      <tr>
        <td>App &#8596; App</td>
        <td>
          <span class="ipc-pill ipc-pill-rbus">rbus</span>
        </td>
      </tr>
    </tbody>
  </table>

  <div class="section-head" style="margin-top:48px;">
    <span class="eyebrow-lt">Reference Documentation</span>
    <h2>IPC Library References</h2>
    <p>Full API documentation and specifications for the underlying IPC technologies.</p>
  </div>

  <div class="ref-grid">

    <div class="ref-card rbus">
      <div class="ref-card-header">
        <div class="ref-card-icon rbus">{_ICON_CODE.format(color="#3730a3")}</div>
        <div>
          <h3>rbus</h3>
          <p class="ref-sub">RDK Message Bus &mdash; component-to-component IPC</p>
        </div>
      </div>
      <p>Generated Doxygen API reference for the rbus library. Covers the full
         C API used by RDK-B components to publish and consume data-model
         parameters, methods, and events over the bus.</p>
      <a class="ref-btn rbus" href="docs/doxygen-out/html/index.html"
         target="_blank" rel="noopener">
        {_ICON_EXTLINK} Open rbus Doxygen Docs
      </a>
      <p class="ref-meta">
        Path: <code>docs/doxygen-out/html/</code>&nbsp;&nbsp;
        Formats available: <code>html</code>&nbsp;<code>latex</code>&nbsp;<code>xml</code>
      </p>
    </div>

  </div>

</section>
"""
    head_extra = "<title>North Bound Low Level APIs — RDK-B Core Broadband</title>\n" + EXTRA_CSS
    return render_page("nbi-lowlevel", head_extra, body)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate north-bound-lowlevel-apis.html"
    )
    ap.add_argument("--out-dir", default=".", help="Directory to write the HTML file into")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "north-bound-lowlevel-apis.html"
    path.write_text(build_page(), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
