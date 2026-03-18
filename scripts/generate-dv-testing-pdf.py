"""
Generate a styled PDF from docs/dataverse-mcp-server-testing.md.
Reads the Markdown file and renders it — edit the MD, regenerate the PDF.

Usage: python scripts/generate-dv-testing-pdf.py
Output: docs/pdf/dataverse-mcp-server-testing.pdf
"""

from fpdf import FPDF
import os
import re


def sanitize_text(text):
    """Replace Unicode characters that Helvetica cannot render."""
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
        .replace("\u00a0", " ")
    )


# -- Color palette -----------------------------------------------------------
NAVY = (22, 48, 82)
ACCENT = (41, 98, 163)
DARK = (40, 40, 40)
MED = (90, 90, 90)
LIGHT = (130, 130, 130)
WHITE = (255, 255, 255)
ROW_ALT = (241, 245, 249)
ROW_WHT = (255, 255, 255)
TABLE_HEADER_BG = (22, 48, 82)
TABLE_HEADER_FG = (255, 255, 255)
DIVIDER = (200, 210, 220)
CODE_BG = (245, 245, 248)
CODE_BORDER = (210, 215, 225)
CALLOUT_BG = (255, 248, 235)
CALLOUT_BORDER = (230, 170, 50)


class DVTestingPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT)
        self.cell(0, 6, sanitize_text(
            "Dataverse MCP Server Testing -- Technical Reference"), align="L")
        self.cell(0, 6, f"Page {self.page_no()}", align="R",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*DIVIDER)
        self.line(self.l_margin, self.get_y(),
                  self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-18)
        self.set_draw_color(*DIVIDER)
        self.line(self.l_margin, self.get_y(),
                  self.w - self.r_margin, self.get_y())
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*LIGHT)
        self.ln(3)
        self.cell(0, 4, sanitize_text("March 2026 | Internal Technical Reference"),
                  align="C")


def parse_md(md_path):
    """Parse markdown into a list of blocks."""
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Horizontal rule
        if line.strip() in ("---", "***", "___"):
            blocks.append(("hr",))
            i += 1
            continue

        # Code block
        if line.strip().startswith("```"):
            lang = line.strip()[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i].rstrip("\n"))
                i += 1
            i += 1  # skip closing ```
            blocks.append(("code", "\n".join(code_lines), lang))
            continue

        # Table (pipe-delimited)
        if "|" in line and line.strip().startswith("|"):
            table_lines = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].rstrip("\n"))
                i += 1
            # Parse table
            rows = []
            for tl in table_lines:
                cells = [c.strip() for c in tl.strip().strip("|").split("|")]
                rows.append(cells)
            # Remove separator row (contains only dashes/colons)
            rows = [r for r in rows
                    if not all(re.match(r'^[\-:]+$', c) for c in r)]
            if rows:
                blocks.append(("table", rows))
            continue

        # Heading
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            blocks.append(("heading", level, text))
            i += 1
            continue

        # Bullet list
        if line.strip().startswith("- "):
            bullets = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                bullets.append(lines[i].strip()[2:])
                i += 1
            blocks.append(("bullets", bullets))
            continue

        # Numbered list
        m_num = re.match(r'^\d+\.\s+(.*)', line.strip())
        if m_num:
            items = []
            while i < len(lines):
                m2 = re.match(r'^\d+\.\s+(.*)', lines[i].strip())
                if m2:
                    items.append(m2.group(1))
                    i += 1
                else:
                    break
            blocks.append(("numbered", items))
            continue

        # Regular paragraph (collect contiguous non-empty, non-special lines)
        para_lines = []
        while i < len(lines):
            l = lines[i].rstrip("\n")
            if not l.strip():
                break
            if l.strip().startswith("#") or l.strip().startswith("```"):
                break
            if l.strip().startswith("- ") and not para_lines:
                break
            if l.strip().startswith("|") and "|" in l:
                break
            if l.strip() in ("---", "***", "___"):
                break
            m_num2 = re.match(r'^\d+\.\s+', l.strip())
            if m_num2 and not para_lines:
                break
            para_lines.append(l.strip())
            i += 1
        if para_lines:
            blocks.append(("para", " ".join(para_lines)))

    return blocks


def render_inline(pdf, text, base_size=9.5, base_color=DARK):
    """Render text with inline **bold** and `code` formatting."""
    text = sanitize_text(text)
    # Split on **bold** and `code` markers
    parts = re.split(r'(\*\*.*?\*\*|`[^`]+`)', text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            pdf.set_font("Helvetica", "B", base_size)
            pdf.set_text_color(*base_color)
            pdf.write(5.5, part[2:-2])
        elif part.startswith("`") and part.endswith("`"):
            pdf.set_font("Courier", "", base_size - 1)
            pdf.set_text_color(120, 50, 50)
            pdf.write(5.5, part[1:-1])
        else:
            pdf.set_font("Helvetica", "", base_size)
            pdf.set_text_color(*base_color)
            pdf.write(5.5, part)


def build_pdf(md_path, out_path):
    blocks = parse_md(md_path)

    pdf = DVTestingPDF()
    pdf.set_margins(20, 20, 20)

    # ── Cover page ──
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 100, "F")

    pdf.set_y(25)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 12, "Dataverse MCP Server Testing",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(180, 200, 220)
    pdf.cell(0, 10, "Technical Reference",
             align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(60)
    pdf.set_draw_color(80, 140, 200)
    pdf.set_line_width(0.4)
    pdf.line(pdf.w * 0.3, pdf.get_y(), pdf.w * 0.7, pdf.get_y())
    pdf.set_line_width(0.2)

    pdf.set_y(68)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 7, "Copilot Studio + Dataverse MCP Connector",
             align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(115)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MED)
    pdf.multi_cell(0, 6, sanitize_text(
        "Comprehensive test log capturing actual SQL queries generated, "
        "errors returned, and results across four models (GPT-4o, GPT-4.1, "
        "GPT-5 Auto, Sonnet 4.6) and two environments (GCC, Commercial). "
        "Purpose: help the product team diagnose MCP SQL generation issues."
    ), align="C")

    pdf.set_y(145)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 7, sanitize_text(
        "4 models  |  2 environments  |  11 prompts  |  4 rounds (GCC)"),
        align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 6, sanitize_text(
        "March 2026 | Internal Technical Reference"
    ), align="C")
    pdf.ln(2)
    pdf.multi_cell(0, 6, "Patrick O'Gorman  |  Microsoft", align="C")

    # ── Content pages ──
    pdf.add_page()

    for block in blocks:
        btype = block[0]

        if btype == "heading":
            level = block[1]
            text = sanitize_text(block[2])

            if level == 1:
                # Skip H1 — it's the title, already on cover
                continue
            elif level == 2:
                # Check page space
                if pdf.get_y() > pdf.h - 50:
                    pdf.add_page()
                pdf.ln(4)
                pdf.set_font("Helvetica", "B", 15)
                pdf.set_text_color(*NAVY)
                pdf.cell(0, 9, text, new_x="LMARGIN", new_y="NEXT")
                pdf.set_draw_color(*ACCENT)
                pdf.set_line_width(0.6)
                pdf.line(pdf.l_margin, pdf.get_y(),
                         pdf.l_margin + 50, pdf.get_y())
                pdf.set_line_width(0.2)
                pdf.ln(5)
            elif level == 3:
                if pdf.get_y() > pdf.h - 40:
                    pdf.add_page()
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(*ACCENT)
                pdf.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(2)
            elif level == 4:
                if pdf.get_y() > pdf.h - 35:
                    pdf.add_page()
                pdf.ln(2)
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(*DARK)
                pdf.cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)

        elif btype == "para":
            text = block[1]
            # Check for callout-style paragraphs (bold observation/conclusion)
            if text.startswith("**Observation:") or text.startswith("**Conclusion:") or text.startswith("**Result:"):
                # Callout box
                clean = sanitize_text(text.replace("**", ""))
                pdf.set_font("Helvetica", "", 9)
                h = pdf.multi_cell(
                    pdf.w - pdf.l_margin - pdf.r_margin - 16, 5, clean,
                    dry_run=True, output="HEIGHT")
                box_h = h + 10
                if pdf.get_y() + box_h > pdf.h - 25:
                    pdf.add_page()
                y = pdf.get_y()
                pdf.set_fill_color(*CALLOUT_BG)
                pdf.set_draw_color(*CALLOUT_BORDER)
                pdf.rect(pdf.l_margin, y,
                         pdf.w - pdf.l_margin - pdf.r_margin, box_h, "FD")
                pdf.set_xy(pdf.l_margin + 5, y + 5)
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(*DARK)
                pdf.multi_cell(
                    pdf.w - pdf.l_margin - pdf.r_margin - 16, 5, clean)
                pdf.set_y(y + box_h + 3)
            else:
                render_inline(pdf, text)
                pdf.ln(7)

        elif btype == "bullets":
            for bullet in block[1]:
                x = pdf.l_margin + 6
                pdf.set_x(x)
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(*MED)
                pdf.write(5.5, "- ")
                render_inline(pdf, bullet, 9.5, DARK)
                pdf.ln(6)

        elif btype == "numbered":
            for idx, item in enumerate(block[1], 1):
                x = pdf.l_margin + 6
                pdf.set_x(x)
                pdf.set_font("Helvetica", "B", 9.5)
                pdf.set_text_color(*ACCENT)
                pdf.write(5.5, f"{idx}. ")
                render_inline(pdf, item, 9.5, DARK)
                pdf.ln(6)

        elif btype == "code":
            code_text = block[1]
            code_lines = code_text.split("\n")
            # Measure height
            line_h = 4.2
            block_h = len(code_lines) * line_h + 8
            if pdf.get_y() + block_h > pdf.h - 25:
                pdf.add_page()
            y = pdf.get_y()
            code_w = pdf.w - pdf.l_margin - pdf.r_margin - 8
            pdf.set_fill_color(*CODE_BG)
            pdf.set_draw_color(*CODE_BORDER)
            pdf.rect(pdf.l_margin + 4, y, code_w, block_h, "FD")
            pdf.set_xy(pdf.l_margin + 8, y + 4)
            pdf.set_font("Courier", "", 7.5)
            pdf.set_text_color(60, 60, 60)
            for cl in code_lines:
                pdf.cell(0, line_h, sanitize_text(cl),
                         new_x="LMARGIN", new_y="NEXT")
                pdf.set_x(pdf.l_margin + 8)
            pdf.set_y(y + block_h + 3)

        elif btype == "table":
            rows = block[1]
            if not rows:
                continue
            num_cols = len(rows[0])
            usable_w = pdf.w - pdf.l_margin - pdf.r_margin

            # Auto-calculate column widths based on content
            col_maxes = [0] * num_cols
            pdf.set_font("Helvetica", "", 7.5)
            for row in rows:
                for ci, cell in enumerate(row):
                    if ci < num_cols:
                        w = pdf.get_string_width(sanitize_text(cell)) + 4
                        col_maxes[ci] = max(col_maxes[ci], w)

            total = sum(col_maxes)
            if total > 0:
                col_widths = [max(c / total * usable_w, 12) for c in col_maxes]
                # Normalize to fit
                scale = usable_w / sum(col_widths)
                col_widths = [w * scale for w in col_widths]
            else:
                col_widths = [usable_w / num_cols] * num_cols

            row_h = 6

            # Check if table fits
            table_h = len(rows) * (row_h + 0.5) + 4
            if pdf.get_y() + table_h > pdf.h - 25 and len(rows) < 15:
                pdf.add_page()

            # Header row
            if rows:
                pdf.set_font("Helvetica", "B", 7.5)
                pdf.set_fill_color(*TABLE_HEADER_BG)
                pdf.set_text_color(*TABLE_HEADER_FG)
                for ci, cell in enumerate(rows[0]):
                    if ci < num_cols:
                        pdf.cell(col_widths[ci], row_h + 1,
                                 sanitize_text(cell), border=0,
                                 align="C", fill=True)
                pdf.ln()

                # Data rows
                pdf.set_font("Helvetica", "", 7.5)
                for ri, row in enumerate(rows[1:]):
                    bg = ROW_ALT if ri % 2 == 0 else ROW_WHT
                    pdf.set_fill_color(*bg)
                    pdf.set_text_color(*DARK)

                    # Check for page break mid-table
                    if pdf.get_y() + row_h > pdf.h - 25:
                        pdf.add_page()

                    for ci, cell in enumerate(row):
                        if ci < num_cols:
                            pdf.cell(col_widths[ci], row_h,
                                     sanitize_text(cell), border=0,
                                     align="C" if ci > 0 else "L",
                                     fill=True)
                    pdf.ln()

            pdf.ln(3)

        elif btype == "hr":
            pdf.ln(2)
            pdf.set_draw_color(*DIVIDER)
            pdf.line(pdf.l_margin, pdf.get_y(),
                     pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(4)

    # Save
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    md_path = os.path.join(script_dir, "..", "docs",
                           "dataverse-mcp-server-testing.md")
    out_path = os.path.join(script_dir, "..", "docs", "pdf",
                            "dataverse-mcp-server-testing.pdf")
    build_pdf(md_path, out_path)
