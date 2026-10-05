"""Dump the full structure of one api-spec detail template."""
import pathlib
import re
import sys

from lxml import html as lxml_html

LEGACY = pathlib.Path(__file__).resolve().parent.parent / "video" / "rdk8"
target = sys.argv[1] if len(sys.argv) > 1 else "tmpl-api-10"

doc = lxml_html.fromstring((LEGACY / "firebolt-api-spec.html").read_text(encoding="utf-8"))
node = doc.xpath(f"//template[@id='{target}']")[0]

for entry in node.xpath(".//section"):
    for child in entry.iterchildren():
        cls = child.get("class") or ""
        text = re.sub(r"\s+", " ", child.text_content() or "")[:90]
        print(f"<{child.tag} class={cls!r}> {text!r}")
        if child.tag == "dl":
            for row in child.xpath("./div"):
                dt = row.xpath("./dt")
                dd = row.xpath("./dd")
                kids = [c.tag + "." + (c.get("class") or "") for c in dd[0]] if dd else []
                print(f"    row dt={re.sub(r'\\s+',' ', dt[0].text_content()) if dt else ''!r} dd children={kids}")
