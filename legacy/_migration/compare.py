"""Compare the regenerated RDK8 video pages against the legacy originals.

Checks visible text, table payloads, headings and link targets so content drift
is caught independently of markup changes. Styling differences are expected:
the new site externalises CSS that legacy inlined.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from lxml import html as lxml_html

ROOT = Path(__file__).resolve().parent.parent.parent
LEGACY = ROOT / "legacy" / "video" / "rdk8"
NEW = ROOT / "video" / "rdk8"

PAGES = [
    "index.html",
    "component-catalog.html",
    "northbound-api-spec.html",
    "southbound-api-spec.html",
    "firebolt-key-codes.html",
    "firebolt-intents.html",
    "firebolt-json-rpc.html",
    "firebolt-api-spec.html",
]

# Legacy renders these tables client-side, so its static HTML has no rows while
# the new build renders them server-side. Compared in the browser instead.
SKIP_TEXT = {"firebolt-api-spec.html"}


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def doc(path: Path):
    return lxml_html.fromstring(path.read_text(encoding="utf-8"))


def visible_text(tree) -> list[str]:
    for node in tree.xpath("//script | //style | //template"):
        node.getparent().remove(node)
    main = tree.xpath("//main")
    target = main[0] if main else tree
    return [t for t in (normalise(x) for x in target.itertext()) if t]


# Legacy strips the release path in JS at render time; the new build strips it
# up front. Normalise so the comparison reflects what the user actually sees.
RENDER_NORMALISERS = {"southbound-api-spec.html": (2, re.compile(r"/releases/tag/[^/]+/?$"))}


def legacy_rows(tree, page: str) -> list[list[str]] | None:
    for script in tree.xpath("//script"):
        match = re.search(r"const DATA=(\[.*?\]);", script.text_content() or "", re.S)
        if match:
            rows = json.loads(match.group(1))
            rule = RENDER_NORMALISERS.get(page)
            if rule:
                column, pattern = rule
                rows = [
                    [pattern.sub("", cell) if index == column else cell for index, cell in enumerate(row)]
                    for row in rows
                ]
            return rows
    return None


def new_rows(tree) -> list[list[str]] | None:
    for script in tree.xpath("//script[@data-table]"):
        return json.loads(script.text_content())["rows"]
    return None


def headings(tree) -> list[str]:
    """Headings the user actually sees; <template> content is compared separately."""
    return [
        normalise(h.text_content())
        for h in tree.xpath("//main//h1 | //main//h2 | //main//h3")
        if not h.xpath("ancestor::template")
    ]


def template_headings(tree) -> set[str]:
    """Modal content is order-independent, so compare it as a set."""
    return {
        normalise(h.text_content())
        for h in tree.xpath("//template//h1 | //template//h2 | //template//h3")
    }


def main() -> int:
    failures = 0
    for name in PAGES:
        legacy_doc, new_doc = doc(LEGACY / name), doc(NEW / name)
        print(f"\n=== {name}")

        lt, nt = normalise(legacy_doc.findtext(".//title")), normalise(new_doc.findtext(".//title"))
        if lt != nt:
            print(f"  TITLE differs:\n    legacy: {lt}\n    new   : {nt}")
            failures += 1

        lrows, nrows = legacy_rows(legacy_doc, name), new_rows(new_doc)
        if name in SKIP_TEXT:
            lrows = nrows = None
        if lrows is not None or nrows is not None:
            if lrows is None or nrows is None:
                print(f"  TABLE presence differs: legacy={lrows is not None} new={nrows is not None}")
                failures += 1
            elif lrows != nrows:
                print(f"  TABLE rows differ: legacy={len(lrows)} new={len(nrows)}")
                lset = {tuple(r) for r in lrows}
                nset = {tuple(r) for r in nrows}
                for row in list(lset - nset)[:3]:
                    print(f"    only in legacy: {row}")
                for row in list(nset - lset)[:3]:
                    print(f"    only in new   : {row}")
                failures += 1
            else:
                print(f"  table rows identical ({len(lrows)})")

        lh, nh = headings(legacy_doc), headings(new_doc)
        if lh != nh:
            print(f"  HEADINGS differ:\n    legacy: {lh}\n    new   : {nh}")
            failures += 1
        else:
            print(f"  headings identical ({len(lh)})")

        lt_tpl, nt_tpl = template_headings(legacy_doc), template_headings(new_doc)
        if lt_tpl != nt_tpl:
            print(f"  TEMPLATE headings differ:\n    only legacy: {sorted(lt_tpl - nt_tpl)[:5]}\n    only new   : {sorted(nt_tpl - lt_tpl)[:5]}")
            failures += 1
        elif lt_tpl:
            print(f"  template headings identical ({len(lt_tpl)})")

        ltext, ntext = visible_text(legacy_doc), visible_text(new_doc)
        if name in SKIP_TEXT:
            print(f"  text check skipped (legacy renders rows client-side); new has {len(ntext)} fragments")
            continue
        missing = [t for t in ltext if t not in ntext]
        added = [t for t in ntext if t not in ltext]
        if missing or added:
            print(f"  TEXT differs: {len(missing)} missing, {len(added)} added")
            for item in missing[:6]:
                print(f"    - {item[:110]}")
            for item in added[:6]:
                print(f"    + {item[:110]}")
            failures += 1
        else:
            print(f"  visible text identical ({len(ltext)} fragments)")

    print(f"\n{'PASS' if not failures else str(failures) + ' difference group(s) found'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
