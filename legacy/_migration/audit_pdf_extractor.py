"""Report how much of the legacy Firebolt generator is hand-maintained data."""
import pathlib
import re

SRC = pathlib.Path(__file__).resolve().parent.parent / "video" / "rdk8" / "gen_nbi_page.py"
text = SRC.read_text(encoding="utf-8")
lines = text.splitlines()
print("total lines:", len(lines))

names = [
    "PARAMETER_OVERRIDES",
    "RETURN_OVERRIDES",
    "DOCUMENT_TABLE_LAYOUTS",
    "FIREBOLT_DOCUMENT_DESCRIPTIONS",
    "FIREBOLT_DOCUMENTS",
]

hardcoded = 0
for name in names:
    match = re.search(rf"^{name}\s*=\s*[({{](.*?)^[)}}]", text, re.S | re.M)
    if not match:
        continue
    block = match.group(0)
    count = len(block.splitlines())
    hardcoded += count
    entries = len(re.findall(r'^\s{4}"', match.group(1), re.M))
    print(f"{name:32} {count:4} lines, {entries:3} entries")

print(f"\nhand-maintained constants: {hardcoded} lines "
      f"({hardcoded * 100 // len(lines)}% of file)")

print("\n--- functions ---")
for index, line in enumerate(lines, 1):
    if line.startswith("def "):
        print(f"  {index:4}  {line.strip()}")

print("\n--- colour-dependent logic ---")
for index, line in enumerate(lines, 1):
    if re.search(r"API_SPEC_(RED|GREEN)|non_stroking_color|fill", line):
        print(f"  {index:4}  {line.strip()[:110]}")
