"""Show the legacy markup for the detail link and the spec-document section."""
import pathlib
import re

from lxml import html as lxml_html

SRC = pathlib.Path(__file__).resolve().parent.parent / "video" / "rdk8" / "firebolt-key-codes.html"
doc = lxml_html.fromstring(SRC.read_text(encoding="utf-8"))

section = doc.xpath("//section[contains(@class,'spec-document')]")[0]
print("spec-document class:", section.get("class"))
print("spec-document style:", section.get("style"))

link = doc.xpath("//main//td//a[starts-with(@href,'#')]")[0]
print("\nlink markup:", lxml_html.tostring(link, encoding="unicode").strip())
print("link class:", link.get("class"))
print("link style:", link.get("style"))

cell = link.getparent()
print("cell markup:", lxml_html.tostring(cell, encoding="unicode").strip()[:300])

intro = doc.xpath("//section[contains(@class,'spec-intro')]")[0]
print("\nspec-intro class:", intro.get("class"), "style:", intro.get("style"))
wrap = doc.xpath("//div[contains(@class,'spec-table-wrap')]")[0]
print("table-wrap class:", wrap.get("class"), "style:", wrap.get("style"))
table = wrap.xpath(".//table")[0]
print("table class:", table.get("class"), "style:", table.get("style"))
