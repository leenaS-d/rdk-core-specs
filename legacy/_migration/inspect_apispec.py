"""Inspect the api-spec client-side DATA array and its detail templates."""
import json
import pathlib
import re

from lxml import html as lxml_html

LEGACY = pathlib.Path(__file__).resolve().parent.parent / "video" / "rdk8"
text = (LEGACY / "firebolt-api-spec.html").read_text(encoding="utf-8")

match = re.search(r"const DATA=(\[.*?\]);", text, re.S)
rows = json.loads(match.group(1))
print("records:", len(rows))
print("keys:", sorted({k for row in rows for k in row}))
print("\nfirst record:")
print(json.dumps(rows[0], indent=2)[:900])

doc = lxml_html.fromstring(text)
templates = doc.xpath("//template")
print(f"\ntemplates: {len(templates)}")
method_templates = [t for t in templates if not t.get("id", "").startswith("tmpl-reference")]
print("method templates:", len(method_templates))
if method_templates:
    node = method_templates[0]
    print("id:", node.get("id"))
    print(lxml_html.tostring(node, encoding="unicode")[:1500])

print("\n--- render script (DATA -> rows) ---")
for script in doc.xpath("//script"):
    body = script.text_content() or ""
    if "DATA" in body:
        start = body.find("const render")
        print(body[start:start + 1200] if start >= 0 else body[:1200])
        break
