"""
Convert Philly investigation markdown docs to professional PDFs.
Uses fpdf2 — parses markdown structure and renders styled PDF.

Usage: python scripts/convert-philly-docs.py
Output: PDFs alongside the source .md files
"""

import os
import re
from fpdf import FPDF

NAVY = (22, 48, 82)
ACCENT = (41, 98, 163)
DARK = (40, 40, 40)
MED = (90, 90, 90)
LIGHT = (130, 130, 130)
WHITE = (255, 255, 255)
DIVIDER = (200, 210, 220)
ROW_ALT = (244, 246, 249)
TABLE_HDR_BG = (22, 48, 82)
TABLE_HDR_FG = (255, 255, 255)


class InvestigationPDF(FPDF):
    def __init__(self, title, subtitle):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.doc_title = title
        self.doc_subtitle = subtitle
        self.set_auto_page_break(auto=True, margin=22)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(*LIGHT)
        self.cell(0, 5, self.doc_title, align="L")
        self.cell(0, 5, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*DIVIDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-16)
        self.set_draw_color(*DIVIDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*LIGHT)
        self.ln(2)
        self.cell(0, 4, "City of Philadelphia  |  Office of Property & Code Enforcement Analytics  |  Public Record Review", align="C")


def parse_and_render(md_path):
    """Parse a markdown file and render it as a styled PDF."""
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Extract title from first H1
    title = ""
    subtitle = ""
    for line in lines:
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            break

    # Find subtitle from first **Prepared by** or bold metadata
    for line in lines:
        if "File Reference:" in line:
            m = re.search(r"PIU-[\d-]+[A-Z]?(?:\s*\(Supplement\))?", line)
            if m:
                subtitle = m.group(0)
            break

    title = sanitize_text(title)
    subtitle = sanitize_text(subtitle)
    pdf = InvestigationPDF(title, subtitle)
    pdf.set_margins(18, 15, 18)
    pdf.add_page()
    usable_w = pdf.w - pdf.l_margin - pdf.r_margin

    # ── COVER HEADER ───────────────────────────────────────────
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 38, "F")
    pdf.set_y(10)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*WHITE)
    pdf.multi_cell(0, 8, title, align="L")
    if subtitle:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(180, 200, 220)
        pdf.cell(0, 6, subtitle, align="L")
    pdf.set_y(44)

    # ── PARSE AND RENDER ───────────────────────────────────────
    i = 0
    # Skip the H1 line since we already rendered it
    while i < len(lines):
        line = lines[i]

        # Skip the H1 title (already rendered)
        if line.startswith("# ") and line[2:].strip() == title:
            i += 1
            continue

        # Horizontal rule
        if line.strip() in ("---", "***", "___"):
            pdf.set_draw_color(*DIVIDER)
            pdf.line(pdf.l_margin, pdf.get_y() + 2, pdf.w - pdf.r_margin, pdf.get_y() + 2)
            pdf.ln(6)
            i += 1
            continue

        # H2
        if line.startswith("## "):
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(*NAVY)
            text = sanitize_text(line[3:].strip())
            pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(*ACCENT)
            pdf.set_line_width(0.5)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 45, pdf.get_y())
            pdf.set_line_width(0.2)
            pdf.ln(3)
            i += 1
            continue

        # H3
        if line.startswith("### "):
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 10.5)
            pdf.set_text_color(*ACCENT)
            text = sanitize_text(line[4:].strip())
            pdf.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            i += 1
            continue

        # Table
        if "|" in line and i + 1 < len(lines) and re.match(r"\s*\|[\s\-:|]+\|", lines[i + 1]):
            # Parse the full table
            headers = [c.strip() for c in line.split("|")[1:-1]]
            i += 2  # skip header and separator
            rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].split("|")[1:-1]]
                rows.append(cells)
                i += 1

            render_table(pdf, headers, rows, usable_w)
            pdf.ln(3)
            continue

        # Code block
        if line.strip().startswith("```"):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i].rstrip())
                i += 1
            i += 1  # skip closing ```

            pdf.set_font("Courier", "", 7)
            pdf.set_text_color(*MED)
            pdf.set_fill_color(248, 249, 250)
            code_lines = [sanitize_text(cl) for cl in code_lines]
            for cl in code_lines:
                pdf.set_x(pdf.l_margin + 4)
                pdf.cell(usable_w - 8, 3.8, cl, fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*DARK)
            pdf.ln(3)
            continue

        # Bold metadata lines (e.g., **Prepared by:** ...)
        if line.startswith("**") and ":**" in line:
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(*MED)
            rendered = render_inline(pdf, line.strip(), 8.5)
            if not rendered:
                pdf.multi_cell(0, 4.5, line.strip())
            pdf.ln(1)
            i += 1
            continue

        # Bullet points
        if re.match(r"\s*[-*]\s", line):
            text = re.sub(r"^\s*[-*]\s+", "", line).strip()
            if not text:
                i += 1
                continue
            pdf.set_x(pdf.l_margin + 5)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*MED)
            pdf.write(5, "- ")
            pdf.set_text_color(*DARK)
            write_rich_text(pdf, text, 9)
            pdf.ln(5.5)
            i += 1
            continue

        # Numbered list
        if re.match(r"\s*\d+\.\s", line):
            m = re.match(r"\s*(\d+\.)\s+(.*)", line)
            if m:
                num, text = m.group(1), m.group(2).strip()
                pdf.set_x(pdf.l_margin + 5)
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(*ACCENT)
                pdf.write(5, num + " ")
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(*DARK)
                write_rich_text(pdf, text, 9)
                pdf.ln(5.5)
            i += 1
            continue

        # Italic/emphasis paragraph (starts with *)
        if line.strip().startswith("*") and line.strip().endswith("*") and not line.strip().startswith("**"):
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(*LIGHT)
            text = sanitize_text(line.strip().strip("*").strip())
            pdf.multi_cell(0, 4.5, text)
            pdf.ln(3)
            i += 1
            continue

        # Regular paragraph
        text = line.strip()
        if text:
            # Collect continuation lines
            while i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].startswith("#") \
                    and not lines[i + 1].startswith("|") and not lines[i + 1].startswith("```") \
                    and not lines[i + 1].strip().startswith("- ") and not lines[i + 1].strip().startswith("* ") \
                    and not re.match(r"\s*\d+\.\s", lines[i + 1]) \
                    and not lines[i + 1].strip() in ("---", "***", "___") \
                    and not (lines[i + 1].startswith("**") and ":**" in lines[i + 1]):
                i += 1
                text += " " + lines[i].strip()

            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*DARK)
            pdf.multi_cell(0, 5, clean_bold_italic(sanitize_text(text)))
            pdf.ln(2)

        i += 1

    return pdf


def render_table(pdf, headers, rows, usable_w):
    """Render a markdown table as a styled PDF table."""
    n_cols = len(headers)
    if n_cols == 0:
        return

    # Calculate column widths based on content
    col_widths = []
    for j in range(n_cols):
        max_len = len(headers[j])
        for row in rows:
            if j < len(row):
                max_len = max(max_len, len(row[j]))
        col_widths.append(max_len)

    total = sum(col_widths)
    if total > 0:
        col_widths = [w / total * usable_w for w in col_widths]
    else:
        col_widths = [usable_w / n_cols] * n_cols

    # Clamp minimum width
    for j in range(n_cols):
        col_widths[j] = max(col_widths[j], 14)

    # Rescale to fit
    scale = usable_w / sum(col_widths)
    col_widths = [w * scale for w in col_widths]

    # Header
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(*TABLE_HDR_BG)
    pdf.set_text_color(*TABLE_HDR_FG)
    for j, h in enumerate(headers):
        pdf.cell(col_widths[j], 6, h, border=0, align="C" if j > 0 else "L", fill=True)
    pdf.ln()

    # Rows
    pdf.set_font("Helvetica", "", 7.5)
    for r_idx, row in enumerate(rows):
        bg = ROW_ALT if r_idx % 2 == 0 else WHITE
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*DARK)
        for j in range(n_cols):
            val = row[j] if j < len(row) else ""
            val = clean_bold_italic(val)
            pdf.cell(col_widths[j], 5.5, val, border=0, align="C" if j > 0 else "L", fill=True)
        pdf.ln()


def sanitize_text(text):
    """Replace Unicode characters unsupported by Helvetica with ASCII equivalents."""
    text = text.replace("\u2014", "--")   # em dash
    text = text.replace("\u2013", "-")    # en dash
    text = text.replace("\u2018", "'")    # left single quote
    text = text.replace("\u2019", "'")    # right single quote
    text = text.replace("\u201c", '"')    # left double quote
    text = text.replace("\u201d", '"')    # right double quote
    text = text.replace("\u2026", "...")   # ellipsis
    text = text.replace("\u00a0", " ")    # non-breaking space
    text = text.replace("\u2192", "->")   # right arrow
    text = text.replace("\u2190", "<-")   # left arrow
    # Strip any remaining non-latin-1 characters
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text


def clean_bold_italic(text):
    """Strip markdown bold/italic markers for plain text rendering."""
    text = sanitize_text(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    return text


def render_inline(pdf, text, size):
    """Attempt to render a line with bold spans using write()."""
    text = sanitize_text(text)
    parts = re.split(r"(\*\*.*?\*\*)", text)
    if len(parts) <= 1:
        return False
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            pdf.set_font("Helvetica", "B", size)
            pdf.write(4.5, part[2:-2])
        else:
            pdf.set_font("Helvetica", "", size)
            pdf.write(4.5, part)
    return True


def write_rich_text(pdf, text, size):
    """Write text with bold spans inline."""
    text = sanitize_text(text)
    parts = re.split(r"(\*\*.*?\*\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            pdf.set_font("Helvetica", "B", size)
            pdf.set_text_color(*DARK)
            pdf.write(5, part[2:-2])
        else:
            pdf.set_font("Helvetica", "", size)
            pdf.set_text_color(*DARK)
            pdf.write(5, part)


def convert_file(md_path):
    """Convert a single markdown file to PDF."""
    pdf_path = md_path.replace(".md", ".pdf")
    pdf = parse_and_render(md_path)
    pdf.output(pdf_path)
    pages = pdf.page_no()
    size_kb = os.path.getsize(pdf_path) / 1024
    print(f"  {os.path.basename(pdf_path):50s} {pages} pages, {size_kb:.0f} KB")


def main():
    base = os.path.join(os.path.dirname(__file__), "..", "sharepoint-docs")

    dirs = [
        os.path.join(base, "Philly-GEENA-LLC"),
        os.path.join(base, "Philly-2400-Bryn-Mawr"),
    ]

    # Also convert the comparison prompts
    prompts_md = os.path.join(base, "Philly_Comparison_Prompts.md")

    print("Converting Philly investigation documents to PDF...\n")
    for d in dirs:
        print(f"  {os.path.basename(d)}/")
        for fname in sorted(os.listdir(d)):
            if fname.endswith(".md"):
                convert_file(os.path.join(d, fname))

    if os.path.exists(prompts_md):
        print(f"\n  Comparison Prompts/")
        convert_file(prompts_md)

    print("\nDone.")


if __name__ == "__main__":
    main()
