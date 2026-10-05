"""RDK9 Components Catalog generator."""
import json

from build import ROOT, esc, hero, load, shell, status_explainer


def _source_url(item: dict) -> str:
    url = item.get("url") or ""
    return url[0] if isinstance(url, list) else url


def build_components() -> None:
    core_source = load("components.json")
    non_core_source = load("rdk9-non-core-components.json")
    core_names = {
        str(item.get("name") or "").casefold()
        for item in core_source.get("components", [])
        if item.get("name")
    }
    records = [
        {
            **item,
            "type": "core" if str(item.get("name") or "").casefold() in core_names else "non-core",
        }
        for item in [*core_source.get("components", []), *non_core_source.get("components", [])]
    ]
    data = [
        [
            item.get("name", ""),
            "video" if str(item.get("category", "")).casefold() == "video" else item.get("category", ""),
            item.get("layer", ""),
            item["type"],
            "develop",
            _source_url(item),
        ]
        for item in records
    ]
    data.sort(key=lambda row: str(row[0]).casefold())
    categories = sorted({row[1] for row in data})
    layers = sorted({row[2] for row in data})
    types = sorted({row[3] for row in data})
    body = hero(
        "Core and non-core components",
        "Components Catalog",
        "Explore the RDK9 Core and Non-core Components Catalog, connecting application-facing capabilities with middleware and vendor-layer implementations.",
        status="Draft",
    )
    body += f'''<style>
        .api-controls{{display:flex;flex-direction:column;align-items:stretch;gap:16px}}
        .api-controls>.toolbar{{display:grid;grid-template-columns:minmax(0,2fr) repeat(3,minmax(0,1fr));gap:12px;width:100%;margin:0;min-width:0}}
        .api-controls>.toolbar input,.api-controls>.toolbar select{{width:100%;min-width:0;margin:0}}
        @media(max-width:760px){{.api-controls>.toolbar{{grid-template-columns:1fr}}}}
    </style>
    <section class="section"><div class="api-controls">
        <div class="toolbar" style="margin:0">
            <input id="search" type="search" placeholder="Search components" aria-label="Search components">
            <select id="category"><option value="">All categories</option>{''.join(f'<option>{esc(item)}</option>' for item in categories)}</select>
            <select id="layer"><option value="">All layers</option>{''.join(f'<option>{esc(item)}</option>' for item in layers)}</select>
            <select id="type"><option value="">All types</option>{''.join(f'<option>{esc(item)}</option>' for item in types)}</select>
        </div>
    </div>
    <div class="table-wrap" style="margin-top:24px"><table class="component-catalog-table"><thead><tr><th>Component</th><th>Category</th><th>Layer</th><th>Type</th><th>Version</th><th>Source</th></tr></thead><tbody id="rows"></tbody></table></div>
    </section>'''
    rows = json.dumps(data, ensure_ascii=True)
    script = f'''<script>
        const DATA={rows};
        const esc=s=>{{const d=document.createElement('div');d.textContent=s;return d.innerHTML}};
        const search=document.querySelector('#search'),category=document.querySelector('#category'),layer=document.querySelector('#layer'),type=document.querySelector('#type');
        function render(){{
            const q=search.value.toLowerCase();
            const rows=DATA.filter(c=>(!q||c.join(' ').toLowerCase().includes(q))&&(!category.value||c[1]===category.value)&&(!layer.value||c[2]===layer.value)&&(!type.value||c[3]===type.value));
            document.querySelector('#rows').innerHTML=rows.length?rows.map(c=>`<tr><td>${{esc(c[0])}}</td><td><span class="pill">${{esc(c[1])}}</span></td><td>${{esc(c[2])}}</td><td><span class="pill ${{c[3] === 'non-core' ? 'non-core' : 'core'}}">${{esc(c[3])}}</span></td><td>${{esc(c[4])}}</td><td><a href="${{esc(c[5])}}" target="_blank" rel="noopener">${{esc(c[5])}}</a></td></tr>`).join(''):'<tr><td class="empty" colspan="6">No components match the current filters.</td></tr>';
        }}
        [search,category,layer,type].forEach(element=>element.addEventListener('input',render));
        render();
    </script>'''
    body = body.replace('<section class="section">', '<style>.pill.core{background:#dff7ea;color:#1d6b43;border:1px solid #a8e1bd}.pill.non-core{background:#e6f3fb;color:#12577d;border:1px solid #b7dcec}</style><section class="section">', 1)
    (ROOT / "component-registry.html").write_text(shell("Core RDK Components | RDKE", "components", body + script), encoding="utf-8")


if __name__ == "__main__":
    build_components()