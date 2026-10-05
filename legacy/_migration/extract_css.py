"""Extract and consolidate CSS from the legacy RDK8 video pages.

The legacy pages load `styles.css` first, then 5-7 inline <style> blocks that
override it. Cascade order is therefore load-bearing: this script preserves the
exact original order while splitting the result into readable, named files.

Outputs to video/rdk8/assets/css/.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from lxml import html as lxml_html

ROOT = Path(__file__).resolve().parent.parent.parent
LEGACY = ROOT / "legacy" / "video" / "rdk8"
OUT = ROOT / "video" / "rdk8" / "assets" / "css"

PAGES = [
    "index.html",
    "component-catalog.html",
    "northbound-api-spec.html",
    "southbound-api-spec.html",
    "firebolt-api-spec.html",
    "firebolt-json-rpc.html",
    "firebolt-intents.html",
    "firebolt-key-codes.html",
]


def inline_blocks() -> dict[str, list[str]]:
    """Return ordered inline <style> contents per page."""
    result: dict[str, list[str]] = {}
    for name in PAGES:
        path = LEGACY / name
        if not path.exists():
            continue
        doc = lxml_html.fromstring(path.read_text(encoding="utf-8"))
        result[name] = [(node.text or "").strip() for node in doc.xpath("//style") if (node.text or "").strip()]
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    blocks = inline_blocks()

    # Which inline blocks are identical across every page -> shared overrides.
    counts: Counter[str] = Counter()
    for name, items in blocks.items():
        for item in items:
            counts[item] += 1
    total_pages = len(blocks)

    shared = [css for css, n in counts.items() if n == total_pages]
    page_specific = {
        name: [css for css in items if counts[css] != total_pages]
        for name, items in blocks.items()
    }

    report = OUT.parent.parent.parent.parent / "legacy" / "_migration" / "css-report.txt"
    lines = [
        f"pages analysed: {total_pages}",
        f"distinct inline blocks: {len(counts)}",
        f"blocks shared by ALL pages: {len(shared)}",
        "",
        "shared block sizes: " + ", ".join(str(len(css)) for css in shared),
        "",
    ]
    for name, items in page_specific.items():
        lines.append(f"{name}: {len(items)} page-specific block(s)")
        for css in items:
            preview = re.sub(r"\s+", " ", css)[:150]
            lines.append(f"    ({len(css)} chars) {preview}")
    report.write_text("\n".join(lines), encoding="utf-8")

    (OUT / "_shared-inline.css").write_text(
        "\n\n".join(shared), encoding="utf-8"
    )
    for name, items in page_specific.items():
        if items:
            stem = name.replace(".html", "")
            (OUT / f"_page-{stem}.css").write_text("\n\n".join(items), encoding="utf-8")

    print("\n".join(lines[:8]))
    print(f"\nwrote raw extracts to {OUT}")
    print(f"report: {report}")


if __name__ == "__main__":
    main()
