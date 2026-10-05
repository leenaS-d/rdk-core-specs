"""Locate specific missing fragments in the legacy pages."""
import pathlib
import re

from lxml import html as lxml_html

LEGACY = pathlib.Path(__file__).resolve().parent.parent / "video" / "rdk8"

TARGETS = {
    "firebolt-intents.html": ["Context fields"],
    "firebolt-json-rpc.html": ["References", "Definitions", "JSON RPC 2.0 Spec"],
}

for page, needles in TARGETS.items():
    doc = lxml_html.fromstring((LEGACY / page).read_text(encoding="utf-8"))
    print(f"=== {page}")
    for needle in needles:
        for node in doc.xpath(f"//*[text()[contains(., '{needle}')]]"):
            chain = []
            current = node
            while current is not None and current.tag != "html":
                label = current.tag
                if current.get("class"):
                    label += "." + current.get("class").replace(" ", ".")
                if current.get("id"):
                    label += "#" + current.get("id")
                chain.append(label)
                current = current.getparent()
            print(f"  {needle!r}: {' < '.join(chain[:5])}")
            print(f"      markup: {lxml_html.tostring(node, encoding='unicode')[:180].strip()}")
            break
