"""Assemble the legacy CSS into organised, readable stylesheets.

Rules are parsed from the legacy `styles.css` plus the deduplicated inline
<style> blocks, then bucketed by selector into themed files. Cascade order is
preserved by emitting buckets in a fixed link order and keeping rule order
within each bucket. Duplicate selectors landing in different buckets are
reported so cascade regressions can be caught.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LEGACY = ROOT / "legacy" / "video" / "rdk8"
OUT = ROOT / "video" / "rdk8" / "assets" / "css"

# Emitted in this order; the HTML must <link> them in the same order.
BUCKETS = ["tokens", "base", "layout", "components", "tables", "spec", "overrides"]

MATCHERS: list[tuple[str, re.Pattern[str]]] = [
    ("tokens", re.compile(r"^(:root)\b")),
    ("base", re.compile(r"^(\*|html|body|h1|h2|h3|a|code|\.mono)\b")),
    ("spec", re.compile(r"(^|[\s,>])\.(spec-|api-detail|api-spec-content|api-support|api-reference|reference-|json-rpc|allowed-|key-code|intent-)")),
    ("tables", re.compile(r"(^|[\s,>])(table|thead|tbody|tr|td|th)\b|\.(table-wrap|component-catalog-table|key-codes-table)")),
    ("layout", re.compile(r"\.(accent|nav|navlinks|brand|wrap|hero|section|footer|eyebrow|lede)\b")),
    ("components", re.compile(r"\.(card|grid|badge|badges|pill|release|toolbar|status-|version-pill|benefit-cards)")),
]


# Page-specific blocks were scoped by virtue of living in one page's <style>.
# Once merged into shared files they would leak, so rewrite their selectors onto
# a page-specific class that the template applies.
PAGE_SCOPES: dict[str, list[tuple[str, str]]] = {
    "_page-component-catalog.css": [(".api-controls", ".catalog-controls")],
}


def scope_css(css: str, origin: str) -> str:
    """Rewrite a page-specific block's selectors, including inside @media."""
    for old, new in PAGE_SCOPES.get(origin, []):
        css = re.sub(rf"(?<![\w-]){re.escape(old)}(?![\w-])", new, css)
    return css


def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def split_rules(css: str) -> list[tuple[str, str]]:
    """Split CSS into (selector, body) pairs, keeping @media blocks whole."""
    rules: list[tuple[str, str]] = []
    depth = 0
    buffer = ""
    selector = ""
    index = 0
    while index < len(css):
        char = css[index]
        if char == "{":
            if depth == 0:
                selector = buffer.strip()
                buffer = ""
            else:
                buffer += char
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                rules.append((selector, buffer.strip()))
                buffer = ""
            else:
                buffer += char
        else:
            buffer += char
        index += 1
    return rules


def classify(selector: str) -> str:
    if selector.startswith("@media"):
        return "overrides"
    for bucket, pattern in MATCHERS:
        if pattern.search(selector):
            return bucket
    return "components"


def format_rule(selector: str, body: str, indent: str = "") -> str:
    if selector.startswith("@"):
        inner = "\n".join(
            format_rule(sub_sel, sub_body, indent + "  ")
            for sub_sel, sub_body in split_rules(body)
        )
        return f"{indent}{selector} {{\n{inner}\n{indent}}}"
    declarations = [d.strip() for d in body.split(";") if d.strip()]
    lines = "\n".join(f"{indent}  {d};" for d in declarations)
    pretty_sel = ",\n".join(part.strip() for part in selector.split(","))
    pretty_sel = "\n".join(f"{indent}{line}" for line in pretty_sel.splitlines())
    return f"{pretty_sel} {{\n{lines}\n{indent}}}"


def main() -> None:
    sources: list[tuple[str, str]] = [("styles.css", strip_comments((LEGACY / "styles.css").read_text(encoding="utf-8")))]
    for extract in sorted(OUT.glob("_shared-inline.css")) + sorted(OUT.glob("_page-*.css")):
        text = strip_comments(extract.read_text(encoding="utf-8"))
        sources.append((extract.name, scope_css(text, extract.name)))

    buckets: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    seen: dict[str, str] = {}
    conflicts: list[str] = []

    for origin, css in sources:
        for selector, body in split_rules(css):
            if not selector or not body:
                continue
            # Repair the f-string brace bug from gen_component_registry_page.py
            if selector.endswith("{") or body.startswith("{"):
                selector = selector.rstrip("{").strip()
                body = body.strip().lstrip("{").rstrip("}").strip()
            # Legacy loaded styles.css first, then the inline <style> blocks, so
            # inline rules beat themed ones regardless of selector. Preserve that
            # precedence by routing every inline rule to the last-loaded file.
            bucket = classify(selector) if origin == "styles.css" else "overrides"
            key = selector.replace(" ", "")
            if key in seen and seen[key] != bucket:
                conflicts.append(f"{selector!r}: {seen[key]} vs {bucket} (from {origin})")
            seen[key] = bucket
            buckets[bucket].append((selector, body, origin))

    OUT.mkdir(parents=True, exist_ok=True)
    summary = []
    for bucket in BUCKETS:
        rules = buckets.get(bucket, [])
        if not rules:
            continue
        header = f"/* {bucket}.css - generated from legacy sources, do not hand-merge */\n"
        chunks = [format_rule(sel, body) for sel, body, _ in rules]
        (OUT / f"{bucket}.css").write_text(header + "\n".join(chunks) + "\n", encoding="utf-8")
        summary.append(f"{bucket}.css: {len(rules)} rules")

    for temp in OUT.glob("_*.css"):
        temp.unlink()

    print("\n".join(summary))
    if conflicts:
        print(f"\nselector appears in multiple buckets ({len(conflicts)}):")
        for item in conflicts[:20]:
            print("  " + item)


if __name__ == "__main__":
    main()
