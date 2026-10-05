"""Print the exact text fragments that differ on the key-codes page."""
import pathlib
import re

from lxml import html as lxml_html

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PAGE = "firebolt-key-codes.html"


def visible(path):
    tree = lxml_html.fromstring(path.read_text(encoding="utf-8"))
    for node in tree.xpath("//script | //style | //template"):
        node.getparent().remove(node)
    main = tree.xpath("//main")
    target = main[0] if main else tree
    return [t for t in (re.sub(r"\s+", " ", x).strip() for x in target.itertext()) if t]


legacy = visible(ROOT / "legacy" / "video" / "rdk8" / PAGE)
fresh = visible(ROOT / "video" / "rdk8" / PAGE)

print("only in legacy:")
for item in [t for t in legacy if t not in fresh]:
    print("   ", repr(item), [hex(ord(c)) for c in item])

print("only in new:")
for item in [t for t in fresh if t not in legacy]:
    print("   ", repr(item))
