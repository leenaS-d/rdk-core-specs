# If not stated otherwise in this file or this component's LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 RDK Management
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#!/usr/bin/env python3
"""
Approach
--------
Work with the PDF geometry (pdfplumber chars / curves / images) instead of text:
  * every table cell is turned into LINES (text + x position + bullet flag)
  * lines are re-joined into logical items: a wrapped line has no trailing space
    char (mid-word wrap) or a trailing space (word wrap); a bullet is a small
    drawn circle left of the line; a paragraph break is a large vertical gap
  * bullet nesting comes from the x offset of the bullet text
  * icons are classified green (supported) / red (not supported) by pixel colour
  * rows with an empty "#" cell are merged into the previous row (page breaks)
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys

import pdfplumber

try:
    from jsonschema import Draft7Validator
except ImportError:  # keep the tool usable without jsonschema
    Draft7Validator = None

##############################################################################
# JSON SCHEMA
##############################################################################

API_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "RDK API Specification",
    "type": "object",
    "required": ["module", "method", "description", "apiVersion", "approved", "support"],
    "properties": {
        "module": {"type": "string"},
        "method": {"type": "string"},
        "events": {"type": "array", "items": {"$ref": "#/definitions/event"}},
        "description": {"$ref": "#/definitions/description"},
        "apiVersion": {"type": "string"},
        "deprecatedVersion": {"type": ["string", "null"]},
        "approved": {"type": "boolean"},
        "support": {
            "type": "object",
            "required": ["cpp17", "javascript"],
            "properties": {
                "cpp17": {"type": "boolean"},
                "javascript": {"type": "boolean"},
            },
        },
        "parameters": {"type": "array", "items": {"$ref": "#/definitions/dataType"}},
        "returns": {"$ref": "#/definitions/dataType"},
        "specificErrors": {"type": "array", "items": {"$ref": "#/definitions/error"}},
    },
    "definitions": {
        "description": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "details": {"type": "array", "items": {"type": "string"}},
            },
        },
        "event": {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}, "description": {"type": "string"}},
        },
        "error": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "code": {"type": "string"},
                "description": {"type": "string"},
                "examples": {"type": "string"},
                "openIssues": {"type": "string"},
            },
        },
        "dataType": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "required": {"type": "boolean"},
                "description": {"type": "string"},
                "format": {"type": "string"},
                "enum": {"type": "array", "items": {"type": "string"}},
                "enumDescriptions": {"type": "object"},
                "representation": {
                    "type": "object",
                    "properties": {"jsonrpc": {"type": "string"}, "cpp17": {"type": "string"}},
                },
                "oneOf": {"type": "array", "items": {"type": "string"}},
                "ordered": {"type": "boolean"},
                "monotonic": {"type": "boolean"},
                "properties": {"type": "array", "items": {"$ref": "#/definitions/dataType"}},
                "items": {"$ref": "#/definitions/dataType"},
            },
        },
    },
}


def _fallback_errors(value, schema, root, path=()):
    """Tiny validator for the subset of JSON-schema used above."""
    errs = []
    if "$ref" in schema:
        node = root
        for part in schema["$ref"].lstrip("#/").split("/"):
            node = node[part]
        return _fallback_errors(value, node, root, path)
    types = schema.get("type")
    if types:
        types = types if isinstance(types, list) else [types]
        pytypes = {"string": str, "boolean": bool, "object": dict,
                   "array": list, "null": type(None)}
        if not any(isinstance(value, pytypes[t]) for t in types):
            return [(path, f"{value!r} is not of type {types}")]
    if isinstance(value, dict):
        for r in schema.get("required", []):
            if r not in value:
                errs.append((path, f"'{r}' is a required property"))
        for k, sub in schema.get("properties", {}).items():
            if k in value:
                errs += _fallback_errors(value[k], sub, root, path + (k,))
    if isinstance(value, list) and "items" in schema:
        for i, v in enumerate(value):
            errs += _fallback_errors(v, schema["items"], root, path + (i,))
    return errs


def validate_api(api):
    if Draft7Validator is not None:
        errors = [(list(e.path), e.message) for e in Draft7Validator(API_SCHEMA).iter_errors(api)]
    else:
        errors = [(list(p), m) for p, m in _fallback_errors(api, API_SCHEMA, API_SCHEMA)]
    if errors:
        print(f"\nValidation failed for {api.get('method')}", file=sys.stderr)
        for path, msg in errors:
            print(f"  Path={path} Error={msg}", file=sys.stderr)
        raise ValueError("Schema validation failed")


##############################################################################
# CONSTANTS
##############################################################################

TYPE_MAP = {
    "boolean": "bool",
    "integer": "int",
    "iso 8601 date and time in utc": "datetime",
    "date and time": "datetime",
}

NONE_VALUES = {"", "none", "null", "-"}      # "None": nothing is returned / no parameters
NOT_APPLICABLE = {"n/a"}                      # "N/A": the column does not apply (notifications)

# Interpretation table: an enum is a string in JSON-RPC but an integer in C++
ENUM_REPRESENTATION = {"jsonrpc": "string", "cpp17": "integer"}

# Key table: row background colour in the methods table
APPROVED_RGB = (220, 255, 241)       # green  - approved, ready for development
UNAPPROVED_RGB = (255, 236, 235)     # red    - not approved, not ready for development

# Table geometry (points)
METHOD_TABLE_COLS = 11
ERROR_TABLE_COLS = 7
PARAGRAPH_GAP = 9.0      # line pitch is ~6.1, paragraph break ~13.5
LEVEL_INDENT = 16.5      # x offset between bullet nesting levels
COL = dict(num=0, module=1, method=2, params=3, returns=4, errors=5,
           api=6, deprecated=7, cpp=8, js=9, desc=10)

##############################################################################
# TEXT HELPERS
##############################################################################

def clean_text(text):
    if text is None:
        return ""
    text = str(text).replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def normalize_type(value):
    """Map each '|' separated token through TYPE_MAP ('unsigned | null' is kept)."""
    tokens = [t.strip() for t in clean_text(value).split("|")]
    mapped = [TYPE_MAP.get(t.lower(), t) for t in tokens]
    return " | ".join(mapped)


def join_lines(lines, wide=False):
    """
    Re-join wrapped lines.  A line that was wrapped at a space ends with a space
    glyph; a line wrapped in the middle of a word does not.  For wide columns
    (descriptions) a missing space is only accepted after a hyphen.
    """
    out = ""
    for ln in lines:
        t = ln["text"]
        if not out:
            out = t
            continue
        if out.endswith(" ") or t.startswith(" ") or re.match(r"-\s", t):
            out = out.rstrip() + " " + t.lstrip()
        elif wide and not out.endswith("-") and not (out.endswith(".") and t[:1].islower()):
            out = out + " " + t
        else:
            out = out + t
    return clean_text(out)


##############################################################################
# PDF -> CELL LINES
##############################################################################

def center_in(obj, bbox):
    cx = (obj["x0"] + obj["x1"]) / 2
    cy = (obj["top"] + obj["bottom"]) / 2
    return bbox[0] <= cx <= bbox[2] and bbox[1] <= cy <= bbox[3]


def cell_lines(page, bbox, page_no):
    """Return the text lines of a cell: [{text, x0, top, bullet, page}]"""
    if bbox is None:
        return []
    chars = [c for c in page.chars if center_in(c, bbox)]
    chars.sort(key=lambda c: (c["top"], c["x0"]))

    groups, cur = [], []
    for ch in chars:
        if cur and ch["top"] - cur[0]["top"] > 2.0:
            groups.append(cur)
            cur = []
        cur.append(ch)
    if cur:
        groups.append(cur)

    # bullets are small (~2x2pt) drawn circles
    bullets = [c for c in page.curves
               if 1.0 < c["x1"] - c["x0"] < 4.0 and 1.0 < c["bottom"] - c["top"] < 4.0
               and center_in(c, bbox)]

    lines = []
    for grp in groups:
        grp.sort(key=lambda c: c["x0"])
        text = "".join(c["text"] for c in grp)
        first = next((c for c in grp if c["text"].strip()), None)
        if first is None:
            continue
        top = min(c["top"] for c in grp)
        bottom = max(c["bottom"] for c in grp)
        x0 = first["x0"]
        has_bullet = any(
            top - 1.5 <= b["top"] <= bottom and 0 < x0 - b["x1"] < 9 for b in bullets
        )
        lines.append(dict(text=text, x0=x0, top=top, bullet=has_bullet, page=page_no))
    return lines


def classify_icon(page_img, scale, page, bbox):
    """True for the green tick, False for the red cross / missing icon."""
    imgs = [i for i in page.images if center_in(i, bbox)]
    if not imgs:
        return False
    im = imgs[0]
    box = tuple(int(round(v * scale)) for v in (im["x0"], im["top"], im["x1"], im["bottom"]))
    region = page_img.crop(box)
    r = g = n = 0
    data = region.tobytes()
    for k in range(0, len(data), 3):
        pr, pg, pb = data[k], data[k + 1], data[k + 2]
        if pr + pg + pb > 690:      # skip (near) white background
            continue
        r += pr
        g += pg
        n += 1
    return n > 0 and g > r


def row_approved(page_img, scale, bbox):
    """
    Key table: green row = approved, red row = not approved.  The row background is the
    most common light colour inside the (description) cell.
    """
    box = tuple(int(round(v * scale)) for v in bbox)
    data = page_img.crop(box).tobytes()
    counts = {}
    for k in range(0, len(data), 3):
        rgb = (data[k], data[k + 1], data[k + 2])
        if sum(rgb) > 600:                       # ignore text / borders
            counts[rgb] = counts.get(rgb, 0) + 1
    if not counts:
        return True
    bg = max(counts, key=counts.get)
    d_ok = sum(abs(a - b) for a, b in zip(bg, APPROVED_RGB))
    d_bad = sum(abs(a - b) for a, b in zip(bg, UNAPPROVED_RGB))
    return d_ok <= d_bad


##############################################################################
# LINES -> NODE TREE
##############################################################################

def build_nodes(lines, wide=False):
    """
    Group lines into items.  A new item starts on a bullet, on a paragraph gap,
    on a page change or on an indent change.  Bullet items are nested by indent.
    Returns top level nodes: {text, bullet, children}
    """
    bullet_x = [l["x0"] for l in lines if l["bullet"]]
    base = min(bullet_x) if bullet_x else 0

    flat = []
    for ln in lines:
        prev = flat[-1] if flat else None
        if ln["bullet"]:
            level = max(0, int(round((ln["x0"] - base) / LEVEL_INDENT)))
            flat.append(dict(lines=[ln], bullet=True, level=level, children=[]))
        elif (prev and abs(ln["x0"] - prev["lines"][0]["x0"]) < 1.5
              and ln["page"] == prev["lines"][-1]["page"]
              and ln["top"] - prev["lines"][-1]["top"] < PARAGRAPH_GAP):
            prev["lines"].append(ln)                       # wrapped line
        else:
            flat.append(dict(lines=[ln], bullet=False, level=0, children=[]))

    roots, stack = [], []
    for node in flat:
        node["text"] = join_lines(node["lines"], wide)
        if not node["bullet"]:
            roots.append(node)
            stack = []
            continue
        while stack and stack[-1]["level"] >= node["level"]:
            stack.pop()
        if stack:
            stack[-1]["children"].append(node)
        else:
            roots.append(node)
        stack.append(node)
    return roots


def flatten(nodes):
    for n in nodes:
        yield n["text"]
        yield from flatten(n["children"])


def is_none(nodes):
    return clean_text(" ".join(n["text"] for n in nodes)).lower() in NONE_VALUES


##############################################################################
# DATA TYPE PARSING
##############################################################################

def split_parts(text):
    return [p.strip() for p in re.split(r"\s+-\s+", text) if p.strip()]


def make_enum(values, descs):
    """Interpretation table: enum = string in JSON-RPC, integer in C++."""
    out = {"type": "enum", "representation": dict(ENUM_REPRESENTATION)}
    if values:                      # some enums (e.g. oldState/newState) list no values in the PDF
        out["enum"] = values
    if descs:
        out["enumDescriptions"] = descs
    return out


def _enum_from_children(children):
    values, descs = [], {}
    for ch in children:
        parts = split_parts(ch["text"]) or [ch["text"]]
        value = parts[0].strip().strip('"').strip("'")
        values.append(value)
        if len(parts) > 1:
            descs[value] = " - ".join(parts[1:])
        for sub in ch["children"]:          # nested text becomes part of description
            descs[value] = (descs.get(value, "") + " " + sub["text"]).strip()
    return values, descs


def build_type(type_text, children=(), extra=()):
    """Build a dataType dict (no name) from the 'type' text and nested bullets."""
    raw = clean_text(type_text)
    low = raw.lower()
    either = bool(re.search(r",?\s*either\b", low))
    one_of = bool(re.search(r",?\s*one of\b", low))
    unordered = bool(re.search(r",?\s*unordered\b", low))
    base = re.sub(r",?\s*(either|one of|unordered)\b", "", raw, flags=re.I).strip(" ,")
    base_low = base.lower()
    out = {}
    desc = [e for e in extra if e]
    monotonic = any(e.lower() == "monotonic" for e in desc)
    desc = [e for e in desc if e.lower() != "monotonic"]

    if re.fullmatch(r"\d+\.\.\.\d+", base):          # e.g. TTS_Status - 0...3
        out["type"] = "unsigned"
        desc.insert(0, f"range {base}")

    elif base_low.startswith("list"):
        # Interpretation table: "list of" is ordered, "list of... unordered" is not
        out["type"] = "array"
        out["ordered"] = not unordered
        if "enum" in base_low:
            values, descs = _enum_from_children(children)
            items = make_enum(values, descs)
        elif "string" in base_low:
            items = {"type": "string"}
            if children:
                desc.append("; ".join(c["text"] for c in children))
        else:                                        # list of objects
            items = {"type": "object"}
            if children:
                items["properties"] = [parse_item(c) for c in children]
        out["items"] = items

    elif base_low == "enum":
        values, descs = _enum_from_children(children)
        out = make_enum(values, descs)

    elif one_of:
        # Interpretation table: "one of" = primitive type with predefined values, NOT an enum
        out["type"] = normalize_type(base)
        values, descs = _enum_from_children(children)
        if values:
            out["oneOf"] = values
        if descs:
            out["enumDescriptions"] = descs

    elif base_low == "object":
        out["type"] = "object"
        if children:
            out["properties"] = [parse_item(c) for c in children]

    else:
        out["type"] = normalize_type(base)
        if children:                                  # 'string, either' -> alternatives
            desc.append("; ".join(c["text"] for c in children))

    if monotonic:
        out["monotonic"] = True
    if desc:
        out["description"] = " - ".join(d for d in desc if d)
    return out


def parse_item(node):
    """'name - type - extra...' bullet -> dataType with name."""
    parts = split_parts(node["text"])
    if not parts:
        return {"name": node["text"]}
    item = {"name": parts[0]}
    if len(parts) == 1:
        if node["children"]:
            item["type"] = "object"
            item["properties"] = [parse_item(c) for c in node["children"]]
        return item
    extra = parts[2:]
    required = None
    if extra and extra[-1].lower() == "optional":
        required = False
        extra = extra[:-1]
    item.update(build_type(parts[1], node["children"], extra))
    if required is False:
        item["required"] = False
    return item


def segments(nodes):
    """Split top-level nodes into [(plain header or None, [bullet nodes])]."""
    segs, cur = [], (None, [])
    for n in nodes:
        if n["bullet"]:
            cur[1].append(n)
        else:
            if cur[0] is not None or cur[1]:
                segs.append(cur)
            cur = (n, list(n["children"]))
    if cur[0] is not None or cur[1]:
        segs.append(cur)
    return segs


def is_not_applicable(nodes):
    return clean_text(" ".join(n["text"] for n in nodes)).lower() in NOT_APPLICABLE


def parse_returns(nodes):
    """None -> returns nothing (null). N/A -> returns does not apply (None here)."""
    if is_not_applicable(nodes):
        return None
    if is_none(nodes):
        return {"type": "null"}
    segs = segments(nodes)
    header, bullets = segs[0]
    if header is None:                                # bullets only -> object
        result = {"type": "object", "properties": [parse_item(b) for b in bullets]}
    else:
        parts = split_parts(header["text"])
        result = build_type(parts[0], bullets, parts[1:])
    for hdr, vals in segs[1:]:                        # e.g. "One of" + values
        if hdr and hdr["text"].lower().startswith("one of"):
            result["oneOf"] = [v["text"] for v in vals]
        elif hdr:
            result.setdefault("description", hdr["text"])
    return result


def parse_parameters(nodes):
    if is_none(nodes) or is_not_applicable(nodes):
        return []
    params = []
    segs = segments(nodes)
    # a plain header without "name - type" followed by bullets describes one
    # composite parameter, e.g. "List, of length one, of the lifecycle state change"
    if len(segs) == 1 and segs[0][0] is not None and not split_parts(segs[0][0]["text"])[1:] \
            and segs[0][1]:
        hdr, bullets = segs[0]
        p = build_type(hdr["text"], bullets)
        p["required"] = True
        return [p]
    # "type - enum" printed as plain text, followed by its values as bullets
    # (Lifecycle2.close): the bullets are the values of that one parameter
    if len(segs) == 1 and segs[0][0] is not None and segs[0][1] \
            and split_parts(segs[0][0]["text"])[1:]:
        hdr, bullets = segs[0]
        node = dict(hdr, children=list(hdr["children"]) + list(bullets))
        item = parse_item(node)
        item.setdefault("required", True)
        return [item]
    for n in nodes:
        item = parse_item(n)
        item.setdefault("required", True)
        params.append(item)
    return params


##############################################################################
# OTHER COLUMNS
##############################################################################

def parse_description(nodes):
    texts = []
    for t in flatten(nodes):
        if re.match(r"1\.\s", t):                    # numbered list "1. a 2. b ..."
            texts.extend(re.split(r"\s+(?=\d+\.\s)", t))
        elif t:
            texts.append(t)
    if not texts:
        return {"summary": "", "details": []}
    return {"summary": texts[0], "details": texts[1:]}


def parse_method_and_events(nodes):
    texts = [n["text"].replace(" ", "") for n in nodes if n["text"]]
    if not texts:
        return "", []
    return texts[0], [{"name": t} for t in texts[1:]]


def find_error(name, error_lookup):
    """
    Look a method's error name up in the Errors table.  The method column often
    abbreviates ("Not supported" for "Method not supported"), so fall back to a
    unique table name that ends with the given name.
    """
    key = name.lower()
    if key in error_lookup:
        return error_lookup[key]
    matches = [v for k, v in error_lookup.items() if k.endswith(" " + key)]
    return matches[0] if len(matches) == 1 else None


def parse_errors(nodes, error_lookup):
    if is_none(nodes) or is_not_applicable(nodes):
        return []
    errs = []
    for text in flatten(nodes):
        code, _, name = text.partition("/")
        code, name = clean_text(code), clean_text(name)
        if not name:
            name, code = code, ""
        found = find_error(name, error_lookup)
        err = {"name": found["name"] if found else name}
        code = code or (found or {}).get("code", "")
        if code:
            err["code"] = code
        if found and found.get("description"):
            err["description"] = found["description"]
        errs.append(err)
    return errs


##############################################################################
# PDF EXTRACTION
##############################################################################

def extract(pdf_path):
    """
    Return (method records, error-table lookup name->description, reference tables).
    reference = {"interpretation": [...], "types": [...], "genericErrors": [...]}
    """
    records, error_lookup = [], {}
    reference = {"interpretation": [], "types": [], "genericErrors": [], "specificErrors": []}
    error_class = ""
    scale = 2.0
    with pdfplumber.open(pdf_path) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            page_img = None

            def get_img():
                nonlocal page_img
                if page_img is None:
                    page_img = page.to_image(resolution=72 * scale).original.convert("RGB")
                return page_img

            for table in page.find_tables():
                ncols = max((len(r.cells) for r in table.rows), default=0)

                # ------- Interpretation (#, Term, Meaning) / Types (#, Type, Definition) -------
                if ncols == 3:
                    header = join_lines(cell_lines(page, table.rows[0].cells[1], page_no))
                    target = {"Term": ("interpretation", "term", "meaning"),
                              "Type": ("types", "name", "definition")}.get(header)
                    if target:
                        key, k1, k2 = target
                        for row in table.rows[1:]:
                            cells = [cell_lines(page, c, page_no) for c in row.cells]
                            if join_lines(cells[0]).isdigit():
                                reference[key].append({k1: join_lines(cells[1]),
                                                       k2: join_lines(cells[2], wide=True)})
                    continue

                # ---------------- Errors table (7 columns) -----------------
                if ncols == ERROR_TABLE_COLS:
                    for row in table.rows:
                        cells = [cell_lines(page, c, page_no) for c in row.cells]
                        if not cells or not join_lines(cells[0]).isdigit():
                            continue
                        error_class = join_lines(cells[1]) or error_class
                        name = join_lines(cells[3])
                        if name:
                            entry = {"code": join_lines(cells[2]), "name": name,
                                     "description": join_lines(cells[4], wide=True)}
                            error_lookup[name.lower()] = entry
                            if error_class.lower() == "generic":
                                reference["genericErrors"].append(dict(entry))
                            else:
                                spec = dict(entry)
                                for key, i in (("examples", 5), ("openIssues", 6)):
                                    text = join_lines(cells[i], wide=True) if len(cells) > i else ""
                                    if text:
                                        spec[key] = text
                                reference["specificErrors"].append(spec)
                    continue

                # ---------------- Methods table (11 columns) ---------------
                if ncols != METHOD_TABLE_COLS:
                    continue
                for row in table.rows:
                    bboxes = list(row.cells) + [None] * (METHOD_TABLE_COLS - len(row.cells))
                    cells = [cell_lines(page, b, page_no) for b in bboxes]
                    num = join_lines(cells[COL["num"]])
                    if join_lines(cells[COL["module"]]) == "Module":      # header row
                        continue
                    if not any(cells):
                        continue

                    if num.isdigit():                                      # new method
                        rec = {"cells": cells, "icons": {}, "approved": True}
                        if bboxes[COL["desc"]] is not None:
                            rec["approved"] = row_approved(get_img(), scale, bboxes[COL["desc"]])
                        records.append(rec)
                    elif records:                                          # continues previous page
                        rec = records[-1]
                        for i, extra in enumerate(cells):
                            rec["cells"][i] = rec["cells"][i] + extra
                    else:
                        continue

                    for key in ("cpp", "js"):
                        i = COL[key]
                        if bboxes[i] is not None and any(
                                center_in(im, bboxes[i]) for im in page.images):
                            rec["icons"][key] = classify_icon(get_img(), scale, page, bboxes[i])
    return records, error_lookup, reference


##############################################################################
# ROW CONVERTER
##############################################################################

def build_api(rec, error_lookup):
    c = rec["cells"]
    method, events = parse_method_and_events(build_nodes(c[COL["method"]]))
    deprecated = join_lines(c[COL["deprecated"]])

    api = {
        "module": join_lines(c[COL["module"]]),
        "method": method,
        "events": events,
        "description": parse_description(build_nodes(c[COL["desc"]], wide=True)),
        "apiVersion": join_lines(c[COL["api"]]),
        "deprecatedVersion": deprecated or None,
        "approved": rec["approved"],
        "support": {
            "cpp17": rec["icons"].get("cpp", False),
            "javascript": rec["icons"].get("js", False),
        },
        "parameters": parse_parameters(build_nodes(c[COL["params"]])),
        "returns": parse_returns(build_nodes(c[COL["returns"]])),
        "specificErrors": parse_errors(build_nodes(c[COL["errors"]]), error_lookup),
    }
    if api["returns"] is None:          # "N/A" - not applicable, so no 'returns' at all
        del api["returns"]
    validate_api(api)
    return api


##############################################################################
# SOURCE METADATA / OUTPUT NAME
##############################################################################

GENERATOR = {"script": "pdftojson.py", "version": "2.2"}


def _iso(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _pdf_header_version(path):
    """'%PDF-1.5' header -> '1.5' (None if not found)."""
    with open(path, "rb") as fp:
        m = re.match(rb"%PDF-(\d+\.\d+)", fp.read(16))
    return m.group(1).decode() if m else None


def _cover_info(first_page_text):
    """Title / status / author / note printed on the first page of the spec."""
    lines = [clean_text(x) for x in (first_page_text or "").splitlines() if clean_text(x)]
    info = {}
    if lines:
        info["title"] = lines[0]
        m = re.search(r"(\d+(?:\.\d+)*)", lines[0])
        if m:
            info["specVersion"] = m.group(1)
    for ln in lines[1:12]:
        for key, pattern in (("status", r"^Document status\s+(.+)$"),
                             ("author", r"^Author\s+(.+)$"),
                             ("note", r"^Note:\s*(.+)$")):
            m = re.match(pattern, ln, re.I)
            if m and key not in info:
                info[key] = m.group(1)
    return info


def build_metadata(pdf_path, api_count):
    stat = os.stat(pdf_path)
    meta = {
        "sourceFile": os.path.basename(pdf_path),
        "sourceFileSize": stat.st_size,
        "sourceSha256": _sha256(pdf_path),
        "sourceModified": _iso(stat.st_mtime),
        "pdfVersion": _pdf_header_version(pdf_path),
        "generatedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": dict(GENERATOR),
        "apiCount": api_count,
    }
    with pdfplumber.open(pdf_path) as pdf:
        meta["pageCount"] = len(pdf.pages)
        # PDF /Info dictionary (Title, Author, Producer, CreationDate ...) - often empty
        meta["pdfInfo"] = {str(k): str(v) for k, v in (pdf.metadata or {}).items() if v}
        meta["document"] = _cover_info(pdf.pages[0].extract_text() if pdf.pages else "")
    return meta


def resolve_output(pdf_path, output=None):
    """
    Default: <input name>.json next to the PDF.
    -o may be a file name, or an existing directory / path ending in a separator,
    in which case <input name>.json is created inside it.
    """
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    default_name = stem + ".json"
    if not output:
        return os.path.join(os.path.dirname(os.path.abspath(pdf_path)), default_name)
    if os.path.isdir(output) or output.endswith(("/", os.sep)):
        return os.path.join(output, default_name)
    return output


##############################################################################
# MAIN
##############################################################################

def convert_pdf_to_json(pdf_path, output_file=None):
    output_file = resolve_output(pdf_path, output_file)
    records, error_lookup, reference = extract(pdf_path)
    apis = [build_api(r, error_lookup) for r in records]

    metadata = build_metadata(pdf_path, len(apis))
    metadata["approvedCount"] = sum(1 for a in apis if a["approved"])
    metadata["unapprovedCount"] = sum(1 for a in apis if not a["approved"])

    document = {
        "metadata": metadata,
        "interpretation": reference["interpretation"],
        "types": reference["types"],
        "genericErrors": reference["genericErrors"],
        "specificErrors": reference["specificErrors"],
        "apis": apis,
    }

    out_dir = os.path.dirname(os.path.abspath(output_file))
    os.makedirs(out_dir, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as fp:
        json.dump(document, fp, indent=2, ensure_ascii=False)

    print(f"Generated {output_file}")
    print(f"APIs extracted: {len(apis)}")
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Convert Firebolt/RDK API PDF to JSON")
    parser.add_argument("pdf", help="Input PDF file")
    parser.add_argument("-o", "--output", default=None,
                        help="Output JSON file or directory "
                             "(default: <pdf name>.json next to the PDF)")
    args = parser.parse_args()
    convert_pdf_to_json(args.pdf, args.output)


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
