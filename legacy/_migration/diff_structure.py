"""Compare section child structure between the legacy and new key-codes page."""
import pathlib

from lxml import html as lxml_html

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PAGE = "firebolt-key-codes.html"

for side, path in (
    ("legacy", ROOT / "legacy" / "video" / "rdk8" / PAGE),
    ("new", ROOT / "video" / "rdk8" / PAGE),
):
    doc = lxml_html.fromstring(path.read_text(encoding="utf-8"))
    print(f"--- {side}")
    container = doc.xpath("//section[contains(@class,'spec-document')]")
    if container:
        kids = [(c.tag, c.get("class") or c.get("id") or "") for c in container[0].iterchildren() if c.tag != "template"]
        print("  spec-document children:", kids)
    for section in doc.xpath("//section[contains(@class,'spec-intro')]"):
        kids = [(c.tag, c.get("class") or "") for c in section.iterchildren() if c.tag != "template"]
        print(f"  #{section.get('id')}: {kids}")
