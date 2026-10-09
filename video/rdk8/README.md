# RDK8 Video specification site

Content lives in Markdown and JSON. Styling lives in CSS. `build.py` turns them
into the `.html` files that GitHub Pages serves.

Nothing here reads a PDF or a spreadsheet at build time — the JSON *is* the
source of truth.

---

## Build

```powershell
cd video\rdk8
python build.py            # regenerate every page
python build.py --check    # regenerate, then validate the data
```

Run this after changing **any** `.md`, `.json`, `.yaml` or template file. CSS and
JS changes do *not* need a rebuild — they are linked, not inlined — but a rebuild
is harmless.

Commit the generated `.html` alongside your source change. GitHub Pages serves
those files directly; there is no CI build step.

### Dependencies

```powershell
python -m pip install markdown PyYAML Jinja2 pdfplumber
```

Tested with markdown 3.11, PyYAML 6.0.3, Jinja2 3.1.6 on Python 3.14.

### Refreshing content from PDFs

The three Firebolt PDFs can be extracted into review files with:

```powershell
py tools/extract_firebolt_specs.py all
```

This writes raw page JSON and readable Markdown under `generated/firebolt-pdf/`.
Use `api`, `intents`, or `key-codes` instead of `all` to refresh one document.
Each run records the PDF SHA-256 in `manifest.json`, making it clear which PDF
version produced the candidates.

The extractor does not overwrite `assets/data/firebolt-*.json`. Those files use
the site's curated block schema and may contain manual corrections, nested lists,
or presentation details that a PDF parser cannot infer safely. Review the
generated Markdown/JSON, merge approved changes into the matching curated JSON,
then run `py build.py --check` and commit the JSON and generated HTML together.

### What `--check` catches

- a page whose `data:` file is missing
- an unknown block `type`
- a table row with a key not declared in that table's `columns`
- an `actions` item whose `ref` has no matching entry in `definitions`
- a record missing a required field (`name`, `category`, `layer`, …)
- duplicate component or HAL interface names

It will not catch wording mistakes or broken external URLs.

---

## Files

### Content — edit these often

| File | Holds |
|---|---|
| `index.md` | Home page: hero, release overview, 3 metric cards, 8 benefit cards |
| `component-catalog.md` | Catalog page furniture: title, columns, filters |
| `southbound-api-spec.md` | Southbound table furniture |
| `firebolt-api-spec.md` | Points at `firebolt-api-spec.json` |
| `firebolt-intents.md` | Points at `firebolt-intents.json` |
| `firebolt-json-rpc.md` | Points at `firebolt-json-rpc.json` |
| `firebolt-key-codes.md` | Points at `firebolt-key-codes.json` |

A `.md` file is YAML front matter (between `---` markers) plus a Markdown body.
Front matter is page *structure*; the body is page *prose*.

In `index.md` the body drives the layout:

```markdown
## Key benefits of RDK8          <- becomes a section
### Lower risk for operators     <- becomes a card in that section
Helps operators assess ...       <- becomes the card body
```

Add a ninth benefit card by appending another `###` block. Nothing else changes.

### Data — edit these often

| File | Holds | Notes |
|---|---|---|
| `assets/data/components.json` | 81 core components | `status` / `version` are hand-edited and never overwritten |
| `assets/data/rdk8-non-core-components.json` | 96 non-core components | Merged with the above to make the 177-row catalog |
| `assets/data/southbound-apis.json` | 5 HAL interfaces | |
| `assets/data/firebolt-*.json` | The four Firebolt spec documents | Use the block schema below |

Changing a catalog from Draft to Published is a one-word edit to `status` in the
relevant JSON file.

### Structure — edit these occasionally

| File | Holds |
|---|---|
| `site.yaml` | Nav menu and dropdown, brand/logo, footer text, fonts, **stylesheet order** |
| `_templates/base.html` | The HTML shell: `<head>`, nav include, `<main>`, footer |
| `_templates/layouts/home.html` | Section and card rendering for the home page |
| `_templates/layouts/data-table.html` | Toolbar, filters, note callout, table shell |
| `_templates/layouts/spec-document.html` | Firebolt pages: blocks, source link, modal dialog |
| `_templates/partials/nav.html` | Header, logo, nav links, dropdown |
| `_templates/partials/hero.html` | Hero: tagline, eyebrow, title, badges, status badge |
| `_templates/partials/status-legend.html` | The Draft / Approved / Published explainer |
| `_templates/partials/block.html` | Renders every block type. The busiest file |

### Styling

| File | Holds |
|---|---|
| `assets/css/tokens.css` | Colours, shadows and spacing as CSS variables. Change `--link` here to recolour the whole site |
| `assets/css/base.css` | Reset and typography |
| `assets/css/layout.css` | Nav, hero, sections, footer |
| `assets/css/components.css` | Cards, pills, badges, toolbars |
| `assets/css/tables.css` | Table shells |
| `assets/css/spec.css` | Firebolt spec documents, entries, modal |
| `assets/css/overrides.css` | Rules that must beat the themed files |
| `assets/css/site.css` | Hand-written additions. **Loaded last, so it wins** |

Load order is set by `stylesheets:` in `site.yaml` and is load-bearing: later
files intentionally override earlier ones. Put new rules in `site.css` unless
they clearly belong to a theme file.

### Scripts

| File | Does |
|---|---|
| `assets/js/table-search.js` | Search and filter for the catalog and API tables |
| `assets/js/spec-modal.js` | Opens a `definitions` entry in the dialog; Escape closes |
| `assets/js/spec-filter.js` | Search and module filter on the Firebolt API spec table |

Rows are rendered server-side and only *hidden* by filtering, so the pages still
read correctly with JavaScript disabled.

### Generated — do not hand-edit

`*.html` in this folder. Overwritten on every build.

---

## Block schema

The four Firebolt pages share one schema. A page is an ordered list of blocks;
a block may contain other blocks, and a table cell may contain a whole block.

```jsonc
{
  "hero":   { "eyebrow": "...", "title": "...", "description": "...", "status": "Published" },
  "source": { "label": "Firebolt 8 key code Spec.pdf", "href": "assets/pdf/..." },
  "blocks": [ /* page content */ ],
  "definitions": { "key-0": { /* opened in the modal by an actions ref */ } }
}
```

### Block types

| `type` | Renders | Key fields |
|---|---|---|
| `section` | A titled section | `heading`, `blocks` |
| `prose` | A paragraph (inline Markdown allowed) | `body`, `variant` |
| `heading` | An `<h3>` | `body` |
| `table` | A table | `columns`, `rows`, `classes` |
| `list` | A bullet list, nestable | `items`, `variant` |
| `details` | A collapsible disclosure | `summary`, `blocks` |
| `code` | Preformatted text | `body`, `variant` |
| `examples` | A group of code blocks | `blocks` |
| `actions` | Pills; `ref` opens a definition, `href` links out | `items`, `plain` |
| `badge` | A single pill | `label` |
| `reference` | A titled row of reference links | `title`, `items` |
| `fields` | Label/value pairs as a table | `fields` |
| `entry` | A titled spec panel | `eyebrow`, `heading`, `overview`, `blocks` |
| `toolbar` | Search box and filter selects | `target`, `search`, `filters` |
| `apiMethod` | A Firebolt method detail panel | `module`, `method`, `support`, `fields`, `trailing` |

### Tables

```jsonc
{
  "type": "table",
  "columns": [
    { "key": "button",  "label": "RCU Button" },
    { "key": "methods", "label": "Methods", "wrap": "preline" },  // keeps line breaks
    { "key": "details", "label": "View details" }
  ],
  "rows": [
    { "button": "Power", "methods": "a\nb",
      "details": { "type": "actions",
                   "items": [ { "label": "View details", "ref": "key-0" } ] } }
  ]
}
```

A cell value is either a string or a nested block. Every row key must appear in
`columns` or `--check` fails.

### Bullet lists

Nesting is recursive, so depth is a data question, not a template one:

```jsonc
{ "type": "list", "items": [
    "enabled - bool",
    { "text": "preferredLanguages - list of strings",
      "items": [ "[] (if not initialized)", "list of one or more ISO 639-2/B" ] }
] }
```

### Colour coding

JSON carries *meaning*, CSS carries colour:

```jsonc
"support": [ { "label": "C++", "state": "supported" },
             { "label": "JS",  "state": "unsupported" } ]
```

A new state means one new CSS rule in `site.css`:

```css
.api-support-mark.deprecated { background: #fff4d8; color: #8a5a00; }
```

---

## Common tasks

| Goal | Do this |
|---|---|
| Fix a typo | Edit the `.md` or `.json`, rebuild |
| Add a table row | Append an object to `rows`, rebuild |
| Add a table column | Add to `columns` **and** add that key to every row, rebuild |
| Add a whole table | Append a `table` block, rebuild |
| Add a bullet | Append to `items`, rebuild |
| Mark a catalog Published | Change `status` in its JSON, rebuild |
| Recolour the site | Change a variable in `tokens.css` |
| Add a nav item | Edit `nav:` in `site.yaml`, rebuild |
| Add a page | Create `newpage.md` with front matter, rebuild — `build.py` globs `*.md` |

A `.md` file **without** a `layout:` key is treated as documentation and skipped,
which is why this README does not become a page.

### Front matter keys

```yaml
layout: spec-document      # home | data-table | spec-document
title: Page title | RDK8   # <title>
nav: northbound            # which nav item is highlighted
footer: true               # show the footer
data: assets/data/x.json   # spec-document only
permalink: /video/rdk8/x.html   # optional; defaults to <filename>.html
```

---

## Gotchas

- **`.nojekyll` at the repo root is required.** Without it GitHub Pages runs
  Jekyll, which would try to render these `.md` files over the generated `.html`.
- **Do not set a global `permalink` style.** It would rewrite every URL and break
  the links from the root landing page.
- **Stylesheet order matters.** Reordering `stylesheets:` in `site.yaml` can
  silently change which rule wins.
- **Generated `.html` must be committed.** Pages serves from the branch; there is
  no build step on GitHub.
- In templates, use `block['items']` not `block.items` — the latter resolves to
  Python's `dict.items` method.
