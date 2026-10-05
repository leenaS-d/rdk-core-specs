"""RDKV home-page generator."""
import json

from build import ROOT, cards, esc, hero, linked_metric_cards, load, shell


CONTACT_EMAIL = "LeenaSunthari_DhanapalRaju@comcast.com"


CONTACT_WIDGET = """
<style>
.contact-toggle{position:fixed;right:22px;bottom:22px;z-index:20;display:grid;place-items:center;width:52px;height:52px;border:0;border-radius:50%;background:#2457d6;color:#fff;box-shadow:0 8px 22px #0b122044;cursor:pointer}
.contact-toggle svg{width:23px;height:23px}.contact-panel{display:none;position:fixed;right:22px;bottom:86px;z-index:21;width:min(360px,calc(100vw - 32px));background:#fff;border:1px solid #e2e7f0;border-radius:10px;box-shadow:0 14px 36px #0b122044;overflow:hidden}.contact-panel.open{display:block}.contact-head{padding:14px 16px;background:#080d18;color:#fff}.contact-head-row{display:flex;align-items:center;justify-content:space-between}.contact-head strong{font-size:.95rem}.contact-note{margin:3px 0 0;color:#9fb2cf;font-size:.72rem}.contact-close{border:0;background:none;color:#fff;font-size:1.2rem;cursor:pointer}.contact-form{display:grid;gap:10px;padding:16px}.contact-form label{display:grid;gap:4px;color:#0b1220;font-size:.78rem;font-weight:700}.contact-form input,.contact-form textarea{width:100%;border:1px solid #e2e7f0;border-radius:6px;padding:9px 10px;font:inherit;font-size:.85rem}.contact-form textarea{min-height:100px;resize:vertical}.contact-submit{border:0;border-radius:6px;padding:10px;background:#0aa66e;color:#fff;font-weight:700;cursor:pointer}.contact-fallback{display:none;color:#2457d6;font-size:.78rem;text-align:center}.contact-status{min-height:1.2em;margin:0;text-align:center;font-size:.78rem;color:#5b6472}
</style>
<button class="contact-toggle" id="contact-toggle" type="button" aria-label="Open contact form" title="Contact us"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="m3 7 9 6 9-6"></path></svg></button>
<section class="contact-panel" id="contact-panel" aria-label="Contact form"><div class="contact-head"><div class="contact-head-row"><strong>Contact us</strong><button class="contact-close" id="contact-close" type="button" aria-label="Close contact form">&times;</button></div><p class="contact-note">Send a message - we'll get it by email</p></div><form class="contact-form" id="contact-form"><label>Name<input name="name" type="text" required></label><label>Email<input name="email" type="email" required></label><label>Message<textarea name="message" required></textarea></label><button class="contact-submit" type="submit">Send message</button><p class="contact-status" id="contact-status" role="status"></p><a class="contact-fallback" id="contact-fallback" href="#">Open email app</a></form></section>
<script>(function(){const toggle=document.querySelector('#contact-toggle'),panel=document.querySelector('#contact-panel'),close=document.querySelector('#contact-close'),form=document.querySelector('#contact-form'),status=document.querySelector('#contact-status'),fallback=document.querySelector('#contact-fallback');if(!toggle||!panel||!close||!form)return;toggle.addEventListener('click',()=>panel.classList.toggle('open'));close.addEventListener('click',()=>panel.classList.remove('open'));form.addEventListener('submit',event=>{event.preventDefault();const button=form.querySelector('button[type=submit]');button.disabled=true;fallback.style.display='none';status.textContent='Sending...';const values=Object.fromEntries(new FormData(form));fetch('https://formsubmit.co/ajax/__CONTACT_EMAIL__',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({...values,_subject:'New message from RDK8 website',_captcha:'false'})}).then(response=>{if(!response.ok)throw new Error('Request failed');return response.json()}).then(()=>{status.textContent='Message sent successfully.';form.reset()}).catch(()=>{status.textContent='Unable to send. Use the email app option below.';fallback.href='mailto:__CONTACT_EMAIL__?subject='+encodeURIComponent('New message from RDK8 website')+'&body='+encodeURIComponent('Name: '+values.name+'\nEmail: '+values.email+'\n\n'+values.message);fallback.style.display='block'}).finally(()=>{button.disabled=false})})})();</script>
""".replace("__CONTACT_EMAIL__", CONTACT_EMAIL).replace("\nEmail:", "\\nEmail:").replace("\n\n", "\\n\\n")
CONTACT_WIDGET = ""


def benefit_cards(items: list[list[str]]) -> str:
    cards_html = "".join(
        f'<article class="card"><h3>{esc(item[0])}</h3><p>{esc(item[1])}</p></article>'
        for item in items
    )
    return f'<style>.benefit-cards{{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:650px){{.benefit-cards{{grid-template-columns:1fr}}}}</style><div class="grid benefit-cards">{cards_html}</div>'


def build_home() -> None:
    content = load("home-content.json")
    components = load("components.json")
    non_core_components = json.loads((ROOT / "rdk8-non-core-components.json").read_text(encoding="utf-8"))
    northbound = load("northbound-apis.json")
    southbound = load("southbound-apis.json")
    body = hero("", content["title"], content["description"], content["badges"], include_release=False)
    title_html = '<h1 style="font-size:clamp(1.9rem,3.6vw,3.5rem)">' + esc(content["title"]) + '</h1>'
    tagline_parts = ["RDK-V", "RDK8 for Video", "Powering Next-Generation Video Experiences"]
    tagline_html = "".join(f'<div class="hero-tagline-badge">{part}</div>' for part in tagline_parts)
    intro_html = f'<div class="hero-tagline">{tagline_html}</div>'
    body = body.replace(title_html, intro_html + title_html, 1)
    if content.get("descriptionAddendum"):
        description_html = f'<p>{esc(content["description"])}</p>'
        addendum_html = description_html + f'<p>{esc(content["descriptionAddendum"])}</p>'
        body = body.replace(description_html, addendum_html, 1)
    architecture = content["architecture"]
    architecture_links = ["component-catalog.html", "northbound-api-spec.html", "southbound-api-spec.html"]
    architecture_metrics = [len(components.get("components", [])) + len(non_core_components.get("components", [])), len(northbound.get("apis", [])), len(southbound.get("apis", []))]
    body += f'''<section class="section alt home-release"><div class="eyebrow">Current release</div><h2>RDK8 Release Overview</h2><p class="lede">{esc(content["release_overview"])}</p></section>'''
    body += f'''<section class="section"><div class="eyebrow">Components and interfaces</div><h2>Explore the Core RDK platform</h2>{linked_metric_cards(architecture["cards"][:3], architecture_links, architecture_metrics)}</section>'''
    benefits = content["benefits"]
    body += f'''<section class="section alt"><div class="eyebrow">RDK8 benefits</div><h2>{esc(benefits["title"])}</h2>{benefit_cards(benefits["cards"])}</section>'''
    footer = "Copyright © 2026 RDK Management, LLC"
    page = shell("RDKV. Core RDK Entertainment Platform", "home", body, footer)
    (ROOT / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    build_home()
