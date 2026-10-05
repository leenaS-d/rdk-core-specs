"""Locate the stray glyph in the legacy key-codes page."""
import pathlib
import re

SRC = pathlib.Path(__file__).resolve().parent.parent / "video" / "rdk8" / "firebolt-key-codes.html"
text = SRC.read_text(encoding="utf-8")

for match in re.finditer("\u256b", text):
    start = max(0, match.start() - 300)
    print(repr(text[start:match.start() + 80]))
    print("-" * 60)

print("occurrences:", text.count("\u256b"))
