"""RDKE RDK9 home-page generator."""
from build import ROOT, esc, hero, load, shell


def platform_metric_cards(items: list[list[str]], links: list[str], metrics: list[int]) -> str:
    return '<div class="grid">' + ''.join(
        f'<a class="card" style="display:block;text-decoration:none;color:inherit" href="{esc(links[index])}"><strong style="display:block;min-height:44px;font-size:2.4rem;color:#2457d6">{metrics[index]}</strong><h3>{esc(item[0])}</h3><p>{esc(item[1])}</p></a>'
        for index, item in enumerate(items)
    ) + '</div>'


def build_home() -> None:
    content = load("home-content.json")
    components = load("components.json")
    non_core_components = load("rdk9-non-core-components.json")
    southbound = load("southbound-apis.json")
    from gen_nbi_page import extract_api_spec_methods
    northbound_count = len(extract_api_spec_methods("Firebolt 9 API Specifications.pdf")[0])

    body = hero("", content["title"], content["description"], content["badges"])
    title_html = '<h1 style="font-size:clamp(1.9rem,3.6vw,3.5rem)">' + esc(content["title"]) + '</h1>'
    badge_style = 'display:inline-flex;align-items:center;padding:5px 12px;border:1px solid #b8df63;border-radius:999px;color:#b8df63;font:700 .72rem/1 JetBrains Mono,monospace;letter-spacing:.08em'
    tagline_parts = ["RDK-V", "RDK9 for Video", "Powering Next-Generation Video Experiences"]
    tagline_html = "".join(f'<div style="{badge_style}">{part}</div>' for part in tagline_parts)
    intro_html = f'<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px;line-height:1">{tagline_html}</div>'
    body = body.replace(title_html, intro_html + title_html, 1)

    architecture = content["architecture"]
    body += f'<section class="section alt home-release"><div class="eyebrow">Upcoming Release</div><h2 style="font-family:Space Grotesk,Inter,sans-serif;letter-spacing:0">RDK9 release</h2><p class="lede">{esc(content["release_overview"])}</p></section>'

    links = ["component-registry.html", "northbound-apis.html", "southbound-apis.html"]
    metrics = [len(components.get("components", [])) + len(non_core_components.get("components", [])), northbound_count, len(southbound.get("apis", []))]
    body += f'<section class="section"><div class="eyebrow">RDK9 platform</div><h2>Explore the RDK9 platform</h2><p class="lede">Explore the RDK9 core and non-core components alongside standardized interfaces connecting applications, middleware, and vendor-layer implementations.</p>{platform_metric_cards(content["architecture"]["cards"][:3], links, metrics)}</section>'

    footer = "Copyright © 2026 RDK Management, LLC"
    (ROOT / "index.html").write_text(shell("RDKE. Core RDK Entertainment Platform", "home", body, footer), encoding="utf-8")


if __name__ == "__main__":
    build_home()
