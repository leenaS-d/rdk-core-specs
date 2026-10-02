"""RDKE hardware specifications generator."""
import json
from build import ROOT, esc, hero, load, shell
from extract_hardware_spec import extract as extract_hardware_pdf


def build_hardware() -> None:
    hardware_pdf = ROOT / "hardware-spec.pdf"
    if hardware_pdf.exists():
        (ROOT / "hardware-spec.json").write_text(
            json.dumps(extract_hardware_pdf(hardware_pdf), indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    data = load("hardware-spec.json")
    body = hero(
        "Reference hardware",
        "Hardware specifications",
        "Minimum CPU, RAM, flash, and required peripheral hardware per RDK-V device profile (Work In Progress)",
    )
    body += '<section class="section">'
    sections = data.get("sections", [])
    if sections:
        section_html = []
        for section in sections:
            text_html = "".join(f"<p>{esc(line)}</p>" for line in section.get("text", []))
            table_html = ""
            for table in section.get("tables", []):
                table_rows = "".join("<tr>" + "".join(f"<td>{esc(cell)}</td>" for cell in row) + "</tr>" for row in table)
                table_html += f'<div class="table-wrap pdf-table"><table><tbody>{table_rows}</tbody></table></div>'
            section_html.append(f'<article class="card pdf-section"><h3>Page {esc(section.get("page"))}</h3>{text_html}{table_html}</article>')
        body += '<div class="subhead">Extracted specification</div><div class="pdf-sections">' + "".join(section_html) + "</div>"
    body += "</section>"
    (ROOT / "hardware-specifications.html").write_text(shell("Hardware Specifications | RDKE", "hardware", body), encoding="utf-8")

if __name__ == "__main__":
    build_hardware()
