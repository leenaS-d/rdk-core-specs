# If not stated otherwise in this file or this component's LICENSE file the
# following copyright and licenses apply:
# Copyright 2023 RDK Management
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Render the viewport-fitted Core RDK Broadband home page.

Usage:
    python3 gen_base_page.py docs/spec-content.json docs/about-content.json --out-dir .
Retains the existing JSON inputs and shared layout.py navigation and colors.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from layout import esc, render_page, TABS_SCRIPT

COMPONENTS_URL = "components/"
COMPONENTS_FULL_URL = "components/full-list.html"
SPEC_WIKI_URL = "https://wiki.rdkcentral.com/spaces/RDK/pages/498925914/RDK9+Core+RDK+Broadband+Specification+Approved+by+TAB"

FOOTER = f"""
<footer id="home-footer">
  <div class="footer-links">
    <a href="{COMPONENTS_URL}">Components — profiles<span>Required / optional components per device profile</span></a>
    <a href="{COMPONENTS_FULL_URL}">Components — full workbook<span>Interactive component list, all profiles</span></a>
    <a href="{SPEC_WIKI_URL}">Core RDK Broadband Spec<span>TAB-approved specification (wiki)</span></a>
    <a href="https://github.com/rdkcentral">rdkcentral on GitHub<span>Component source repositories</span></a>
  </div>
  <div class="footer-meta">Copyright &copy; 2026 RDK Management, LLC</div>
</footer>
"""

HOME_STYLE = """
<style>
  html, body { margin: 0; padding: 0; }
  #home-main {
    display: flex;
    flex-direction: column;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box;
  }
  #home-main .hero {
    flex: 1 1 auto;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 24px 40px !important;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  #home-main .hero-flex { justify-content: center; width: 100%; }
  #home-main .hero-inner { text-align: center; max-width: none; }
  #home-main h1 { font-size: clamp(2.4rem, 5vw, 4rem); margin: 0; }
  #home-footer {
    margin: 0 !important;
    padding: 28px 40px 22px !important;
    box-sizing: border-box;
  }
  #home-footer .footer-links {
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 24px;
    margin: 0;
  }
  #home-footer .footer-links a { min-width: 0; }
  #home-footer .footer-links span { display: block; margin-top: 6px; }
  #home-footer .footer-meta { margin-top: 22px; text-align: center; }
  @media (max-width: 900px) {
    #home-footer .footer-links { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
  }
  @media (max-width: 520px) {
    #home-main .hero { padding: 20px !important; }
    #home-footer { padding: 20px !important; }
    #home-footer .footer-links { grid-template-columns: 1fr; }
  }
</style>
"""

# Measure the rendered navigation and footer instead of assuming a 61px header.
# This also works when layout.py wraps the generated content in a container.
FIT_SCRIPT = """
<script>
(() => {
  const main = document.getElementById('home-main');
  const footer = document.getElementById('home-footer');
  if (!main || !footer) return;
  let frame;
  function fit() {
    main.style.height = 'auto';
    const top = main.getBoundingClientRect().top + window.scrollY;
    const viewport = document.documentElement.clientHeight;
    const gap = Math.max(0, footer.getBoundingClientRect().top - main.getBoundingClientRect().bottom);
    const available = Math.max(0, viewport - top - footer.offsetHeight - gap);
    main.style.height = available + 'px';
  }
  function schedule() {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(fit);
  }
  window.addEventListener('resize', schedule);
  window.addEventListener('load', schedule);
  if (document.fonts) document.fonts.ready.then(schedule);
  if ('ResizeObserver' in window) new ResizeObserver(schedule).observe(footer);
  schedule();
})();
</script>
"""


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def render_goals(goals: list[dict]) -> str:
    return "\n".join(
        f'<div class="card" id="{slugify(g["title"])}" style="margin-bottom:16px; scroll-margin-top:140px;">'
        f'<h3>{esc(g["title"])}</h3><p><strong style="color:var(--ink);">Goal —</strong> {esc(g["goal"])}</p>'
        f'<p style="margin-bottom:0;"><strong style="color:var(--amber-fg);">Challenge —</strong> {esc(g["challenge"])}</p></div>'
        for g in goals
    )


def render_rdk_ready(items: list[dict]) -> str:
    cards = ''.join(f'<div class="card"><h3>{esc(it["title"])}</h3><p style="margin-bottom:0;">{esc(it["body"])}</p></div>' for it in items)
    return f'<div class="two-col">{cards}</div>'


def render_benefits(groups: list[dict]) -> str:
    cols = []
    for g in groups:
        items = ''.join(f'<li>{esc(i)}</li>' for i in g['items'])
        cols.append(f'<div style="flex:1; min-width:220px;"><div class="card" style="height:100%; box-sizing:border-box;"><h3>{esc(g["category"])}</h3><ul style="margin:0; padding-left:18px; font-size:0.92rem; color:var(--muted);">{items}</ul></div></div>')
    return '<div style="display:flex; gap:20px; flex-wrap:wrap; align-items:stretch;">' + ''.join(cols) + '</div>'


def render_five_tier(tiers: list[dict]) -> str:
    out = []
    for t in sorted(tiers, key=lambda x: -x['tier']):
        if 'split' in t:
            cols = ''.join(f'<div class="split-col"><h4>{esc(c["title"])}</h4><p>{esc(c["text"])}</p></div>' for c in t['split'])
            body = f'<div class="body body-split">{cols}</div>'
        else:
            body = f'<div class="body"><h4>{esc(t["layer"])}</h4><p>{esc(t["description"])}</p></div>'
        out.append(f'<div class="tier t{t["tier"]}"><div class="num">{t["tier"]}</div>{body}</div>')
    return '\n'.join(out)


def render_test_suites(rows: list[dict]) -> str:
    return '\n'.join(f'<tr><td class="mono">{esc(r["name"])}</td><td>{esc(r["definition"])}</td><td>{esc(r["owner"])}</td></tr>' for r in rows)


STATS_SECTION = """
<div class="stats" style="margin:-32px 44px 0; position:relative; z-index:2;">
  <div class="stat">
    <span class="stat-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12" rx="1.5"/><path d="M9 3v3M15 3v3M9 18v3M15 18v3M3 9h3M3 15h3M18 9h3M18 15h3"/></svg></span>
    <div><div class="num" id="stat-components">&mdash;</div><div class="lbl">Core Components</div></div>
  </div>
  <div class="stat">
    <span class="stat-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l9 5v8l-9 5-9-5V8z"/><path d="M12 12v9M3 8l9 4 9-4"/></svg></span>
    <div><div class="num" id="stat-nb">&mdash;</div><div class="lbl">North-bound APIs</div></div>
  </div>
  <div class="stat">
    <span class="stat-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg></span>
    <div><div class="num" id="stat-sb">&mdash;</div><div class="lbl">South-bound APIs</div></div>
  </div>
</div>
<script>
(function(){
  fetch('components/ethwan-router-components.json',{cache:'no-store'})
    .then(r=>r.ok?r.json():Promise.reject()).then(d=>{
      var t=(d.required||[]).length+(d['common-core']||[]).length+(d.optional||[]).length;
      document.getElementById('stat-components').textContent=t;
    }).catch(function(){});
  fetch('north-bound-apis.json',{cache:'no-store'})
    .then(r=>r.ok?r.json():Promise.reject()).then(d=>{
      var a=Array.isArray(d)?d:(d.apis||d.items||d.parameters||null);
      if(a)document.getElementById('stat-nb').textContent=a.length;
    }).catch(function(){});
  fetch('south-bound-apis.json',{cache:'no-store'})
    .then(r=>r.ok?r.json():Promise.reject()).then(d=>{
      var a=Array.isArray(d)?d:(d.apis||d.items||d.interfaces||null);
      if(a)document.getElementById('stat-sb').textContent=a.length;
    }).catch(function(){});
})();
</script>
"""

EXPLORE_SECTION = """
<section style="padding:52px 44px 40px; max-width:1520px;">
  <div class="section-head">
    <span class="eyebrow-lt" style="color:#7dd3fc;">Components and Interfaces</span>
    <h2>Explore the Core RDK platform</h2>
  </div>
  <div class="quicklink-row grid">
    <a class="quicklink-card" href="components/" style="--ql-color:var(--rdk-blue);">
      <span class="ql-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12" rx="1.5"/><path d="M9 3v3M15 3v3M9 18v3M15 18v3M3 9h3M3 15h3M18 9h3M18 15h3"/></svg></span>
      <div class="ql-title">Component Catalog</div>
      <div class="ql-desc">A list of RDK components categorized as core and optional.</div>
    </a>
    <a class="quicklink-card" href="north-bound-apis.html" style="--ql-color:var(--rdk-green);">
      <span class="ql-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l9 5v8l-9 5-9-5V8z"/><path d="M12 12v9M3 8l9 4 9-4"/></svg></span>
      <div class="ql-title">North-bound APIs</div>
      <div class="ql-desc">APIs that can be used by applications to access system services and resources.</div>
    </a>
    <a class="quicklink-card" href="south-bound-apis.html" style="--ql-color:var(--rdk-amber);">
      <span class="ql-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg></span>
      <div class="ql-title">South-bound APIs</div>
      <div class="ql-desc">Hardware Abstraction Layer (HAL) specifications to aid silicon platform porting.</div>
    </a>
  </div>
</section>
"""


def build_about_page(spec: dict, about: dict) -> str:
    badges_html = (
        '<span class="badge" style="background:transparent;color:#a3e635;border-color:#a3e635;">RDK-B</span>'
        '<span class="badge" style="background:transparent;color:#a3e635;border-color:#a3e635;">RDK8 for Broadband</span>'
    )
    from layout import render_hero
    hero = render_hero(
        eyebrow="",
        title="Core RDK Broadband",
        lede=("Core RDK Broadband (RDK-B) defines the common platform foundation for RDK-based Broadband solutions "
              "through governed capabilities, standardized interfaces, lifecycle policies, and conformance requirements."),
        badges_html=badges_html,
        visual_key="about",
    )
    body = f'''
{HOME_STYLE}
{hero}
{EXPLORE_SECTION}
{FOOTER}
'''
    return render_page('about', '<title>Core RDK Broadband</title>', body,
                       script=TABS_SCRIPT + FIT_SCRIPT)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('spec_json', help='spec-content.json')
    ap.add_argument('about_json', help='about-content.json')
    ap.add_argument('--out-dir', default='.')
    args = ap.parse_args()
    spec = json.loads(Path(args.spec_json).read_text(encoding='utf-8'))
    about = json.loads(Path(args.about_json).read_text(encoding='utf-8'))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'index.html').write_text(build_about_page(spec, about), encoding='utf-8')
    print(f'Wrote {out_dir / "index.html"}')


if __name__ == '__main__':
    main()
