"""
Generate demo-guide.pdf from docs/sources/demo-guide.md.
Reads the markdown source and renders it as a styled PDF using fpdf2.

Usage: python scripts/generate-demo-guide-pdf.py
Output: docs/demo-guide.pdf
"""

from fpdf import FPDF
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "sources", "demo-guide.md")
OUT_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "demo-guide.pdf")

# -- Colors ------------------------------------------------------------------
NAVY = (22, 48, 82)
ACCENT = (41, 98, 163)
DARK = (40, 40, 40)
MED = (90, 90, 90)
LIGHT = (130, 130, 130)
WHITE = (255, 255, 255)
DIVIDER = (200, 210, 220)
CODE_BG = (245, 245, 245)
CODE_BORDER = (220, 220, 220)
QUOTE_BG = (248, 249, 252)
QUOTE_BORDER = (41, 98, 163)
TABLE_HEADER_BG = (22, 48, 82)
TABLE_HEADER_FG = (255, 255, 255)
ROW_ALT = (241, 245, 249)
ROW_WHT = (255, 255, 255)
CHECK_COLOR = (41, 98, 163)


def sanitize(text):
    """Replace Unicode chars Helvetica can't render."""
    return (
        text
        .replace("\u2014", "--")
        .replace("\u2013", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2026", "...")
        .replace("\u2192", "->")
        .replace("\u2022", "-")
        .replace("\u2003", " ")
    )


def strip_md_bold(text):
    """Remove ** markers and return (cleaned_text, [(start, end), ...]) ranges."""
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text)


class DemoGuidePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=22)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT)
        self.cell(0, 6, "AI Agent Accuracy Spectrum -- Demo Guide", align="L")
        self.cell(0, 6, f"Page {self.page_no()}", align="R",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*DIVIDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-16)
        self.set_draw_color(*DIVIDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*LIGHT)
        self.ln(3)
        self.cell(0, 4, "Confidential  |  March 2026", align="C")


def render_inline_markdown(pdf, text, base_style="", base_size=9.5, color=DARK):
    """Render text with **bold** inline spans using write()."""
    text = sanitize(text)
    pdf.set_text_color(*color)
    parts = re.split(r"(\*\*.+?\*\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            pdf.set_font("Helvetica", "B", base_size)
            pdf.write(5.5, part[2:-2])
        else:
            pdf.set_font("Helvetica", base_style, base_size)
            pdf.write(5.5, part)


def parse_table(lines):
    """Parse markdown table lines into headers and rows."""
    rows = []
    for line in lines:
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line[1:-1].split("|")]
            # Skip separator rows (|---|---|)
            if all(re.match(r"^-+$", c) or c == "" for c in cells):
                continue
            rows.append(cells)
    if len(rows) < 2:
        return None, None
    return rows[0], rows[1:]


def render_table(pdf, headers, rows):
    """Render a simple table."""
    n_cols = len(headers)
    usable_w = pdf.w - pdf.l_margin - pdf.r_margin
    col_w = usable_w / n_cols

    # Header
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(*TABLE_HEADER_BG)
    pdf.set_text_color(*TABLE_HEADER_FG)
    for h in headers:
        pdf.cell(col_w, 7, sanitize(h), border=0, align="C", fill=True)
    pdf.ln()

    # Rows
    pdf.set_font("Helvetica", "", 7.5)
    for r_idx, row in enumerate(rows):
        bg = ROW_ALT if r_idx % 2 == 0 else ROW_WHT
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*DARK)
        for i, cell in enumerate(row):
            align = "L" if i == 0 else "C"
            pdf.cell(col_w, 6, sanitize(cell), border=0, align=align, fill=True)
        pdf.ln()
    pdf.ln(2)


def build_pdf():
    with open(MD_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pdf = DemoGuidePDF()
    pdf.set_margins(20, 20, 20)

    # ── Cover page ──────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 100, "F")

    pdf.set_y(30)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 12, "AI Agent Accuracy Spectrum", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(180, 200, 220)
    pdf.cell(0, 10, "Demo Guide", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(70)
    pdf.set_draw_color(80, 140, 200)
    pdf.set_line_width(0.4)
    pdf.line(pdf.w * 0.3, pdf.get_y(), pdf.w * 0.7, pdf.get_y())
    pdf.set_line_width(0.2)

    pdf.set_y(80)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 7, "Presenter Guide  |  March 2026", align="C",
             new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(115)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MED)
    pdf.multi_cell(0, 6, sanitize(
        "A five-level framework for demonstrating AI agent accuracy "
        "across government use cases. Includes demo script, talking points, "
        "timing guide, Q&A handling, and reference appendices."
    ), align="C")

    pdf.set_y(145)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 7, "50-60 minutes  |  5 levels  |  2 use cases  |  304 test runs",
             align="C", new_x="LMARGIN", new_y="NEXT")

    # ── Render markdown body ────────────────────────────────────────────
    pdf.add_page()

    i = 0
    in_code_block = False
    code_lines = []
    in_table = False
    table_lines = []

    # Skip the first H1 line (already on cover)
    while i < len(lines) and not lines[i].startswith("# "):
        i += 1
    if i < len(lines):
        i += 1  # skip the H1

    while i < len(lines):
        line = lines[i].rstrip("\n")
        raw = line

        # ── Code block toggle ──────────────────────────────────────
        if line.strip().startswith("```"):
            if in_code_block:
                # End code block — render it
                if code_lines:
                    y_start = pdf.get_y()
                    block_h = len(code_lines) * 4.5 + 6
                    if y_start + block_h > pdf.h - 25:
                        pdf.add_page()
                        y_start = pdf.get_y()
                    pdf.set_fill_color(*CODE_BG)
                    pdf.set_draw_color(*CODE_BORDER)
                    pdf.rect(pdf.l_margin + 4, y_start,
                             pdf.w - pdf.l_margin - pdf.r_margin - 8,
                             block_h, "FD")
                    pdf.set_xy(pdf.l_margin + 8, y_start + 3)
                    pdf.set_font("Courier", "", 8)
                    pdf.set_text_color(*DARK)
                    for cl in code_lines:
                        pdf.cell(0, 4.5, sanitize(cl), new_x="LMARGIN", new_y="NEXT")
                        pdf.set_x(pdf.l_margin + 8)
                    pdf.set_y(y_start + block_h + 2)
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # ── Table detection ────────────────────────────────────────
        if line.strip().startswith("|") and line.strip().endswith("|"):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
            i += 1
            continue
        elif in_table:
            # End of table — render
            headers, rows = parse_table(table_lines)
            if headers and rows:
                render_table(pdf, headers, rows)
            in_table = False
            table_lines = []
            # Don't skip this line, fall through to process it

        # ── Horizontal rule ────────────────────────────────────────
        if line.strip() == "---":
            pdf.ln(2)
            pdf.set_draw_color(*DIVIDER)
            pdf.line(pdf.l_margin, pdf.get_y(),
                     pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(4)
            i += 1
            continue

        # ── Empty line ─────────────────────────────────────────────
        if line.strip() == "":
            pdf.ln(2)
            i += 1
            continue

        # ── H1 ─────────────────────────────────────────────────────
        if line.startswith("# "):
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(*NAVY)
            pdf.cell(0, 11, sanitize(line[2:].strip()),
                     new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(*NAVY)
            pdf.set_line_width(0.6)
            pdf.line(pdf.l_margin, pdf.get_y(),
                     pdf.w - pdf.r_margin, pdf.get_y())
            pdf.set_line_width(0.2)
            pdf.ln(5)
            i += 1
            continue

        # ── H2 ─────────────────────────────────────────────────────
        if line.startswith("## "):
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(*NAVY)
            pdf.cell(0, 9, sanitize(line[3:].strip()),
                     new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(*ACCENT)
            pdf.set_line_width(0.5)
            pdf.line(pdf.l_margin, pdf.get_y(),
                     pdf.l_margin + 45, pdf.get_y())
            pdf.set_line_width(0.2)
            pdf.ln(4)
            i += 1
            continue

        # ── H3 ─────────────────────────────────────────────────────
        if line.startswith("### "):
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(*ACCENT)
            pdf.cell(0, 7, sanitize(line[4:].strip()),
                     new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            i += 1
            continue

        # ── Blockquote ─────────────────────────────────────────────
        if line.strip().startswith("> "):
            quote_text = line.strip()[2:]
            # Collect continuation lines
            while (i + 1 < len(lines) and
                   lines[i + 1].strip().startswith("> ")):
                i += 1
                quote_text += " " + lines[i].strip()[2:]

            y_start = pdf.get_y()
            pdf.set_x(pdf.l_margin + 6)
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(*MED)
            cell_w = pdf.w - pdf.l_margin - pdf.r_margin - 12
            pdf.multi_cell(cell_w, 5, sanitize(strip_md_bold(quote_text)))
            y_end = pdf.get_y()

            # Draw quote bar
            pdf.set_draw_color(*QUOTE_BORDER)
            pdf.set_line_width(0.8)
            pdf.line(pdf.l_margin + 3, y_start, pdf.l_margin + 3, y_end)
            pdf.set_line_width(0.2)
            pdf.ln(2)
            i += 1
            continue

        # ── Checkbox list item ─────────────────────────────────────
        if re.match(r"^- \[[ x]\] ", line.strip()):
            checked = "[x]" in line
            text = re.sub(r"^- \[[ x]\] ", "", line.strip())
            pdf.set_x(pdf.l_margin + 6)
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(*CHECK_COLOR if not checked else MED)
            marker = "[x]" if checked else "[ ]"
            pdf.write(5.5, marker + "  ")
            pdf.set_text_color(*DARK)
            pdf.set_font("Helvetica", "", 9.5)
            pdf.multi_cell(pdf.w - pdf.r_margin - pdf.get_x(), 5.5,
                           sanitize(strip_md_bold(text)))
            pdf.ln(1)
            i += 1
            continue

        # ── Bullet point ───────────────────────────────────────────
        if line.strip().startswith("- "):
            text = line.strip()[2:]
            pdf.set_x(pdf.l_margin + 6)
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(*MED)
            pdf.write(5.5, "- ")
            render_inline_markdown(pdf, text, base_size=9.5)
            pdf.ln(5.5)
            pdf.ln(1)
            i += 1
            continue

        # ── Regular paragraph ──────────────────────────────────────
        text = line.strip()
        # Collect continuation lines (non-empty, non-special)
        while (i + 1 < len(lines) and
               lines[i + 1].strip() != "" and
               not lines[i + 1].strip().startswith("#") and
               not lines[i + 1].strip().startswith(">") and
               not lines[i + 1].strip().startswith("- ") and
               not lines[i + 1].strip().startswith("|") and
               not lines[i + 1].strip().startswith("```") and
               not lines[i + 1].strip() == "---"):
            i += 1
            text += " " + lines[i].strip()

        render_inline_markdown(pdf, text, base_size=9.5)
        pdf.ln(5.5)
        pdf.ln(2)
        i += 1

    # Flush any remaining table
    if in_table and table_lines:
        headers, rows = parse_table(table_lines)
        if headers and rows:
            render_table(pdf, headers, rows)

    pdf.output(OUT_PATH)
    print(f"PDF generated: {os.path.abspath(OUT_PATH)}")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()
