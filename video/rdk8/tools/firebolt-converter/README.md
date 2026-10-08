# Firebolt PDF converter

This isolated converter creates review candidates without changing the existing
curated JSON, Markdown, HTML, or CSS files.

## Run

From the RDK8 video directory:

```powershell
py tools/extract_firebolt_specs.py all
py tools/firebolt-converter/generate.py all
```

Run one page at a time with `api`, `intents`, or `key-codes`.

The converter reads:

- `generated/firebolt-pdf/*.json` as the raw PDF extraction
- `assets/data/firebolt-*.json` as the current schema and manual-content reference

It writes candidates to:

```text
generated/firebolt-converted/
  assets/data/firebolt-api-spec.json
  assets/data/firebolt-intents.json
  assets/data/firebolt-key-codes.json
  firebolt-api-spec.md
  firebolt-intents.md
  firebolt-key-codes.md
```

The candidate JSON preserves the current schema and manual content, while adding
PDF hash/page metadata under `generator`. The candidate Markdown contains the
PDF-extracted pages for review. No existing file is overwritten.

After review, approved changes can be copied manually into the canonical
`assets/data` files and then validated with:

```powershell
py build.py --check
```
