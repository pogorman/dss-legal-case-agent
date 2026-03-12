"""
Generate a styled PDF from docs/live-demo-script.md.
Reads the Markdown file and renders it -- edit the MD, regenerate the PDF.

Usage: python scripts/generate-demo-script-pdf.py
Output: docs/pdf/live-demo-script.pdf
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
TIP_BG = (235, 248, 240)
TIP_BORDER = (60, 160, 80)


class DemoScriptPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT)
        self.cell(0, 6, sanitize_text(
            "Live Demo Script -- Copilot Studio Focus"), align="L")
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
        self.cell(0, 4, sanitize_text("March 2026 | Demo Script"),
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

        # Blockquote
        if line.strip().startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            blocks.append(("blockquote", " ".join(quote_lines)))
            continue

        # Table (pipe-delimited)
        if "|" in line and line.strip().startswith("|"):
            table_lines = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].rstrip("\n"))
                i += 1
            rows = []
            for tl in table_lines:
                cells = [c.strip() for c in tl.strip().strip("|").split("|")]
                rows.append(cells)
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

        # Regular paragraph
        para_lines = []
        while i < len(lines):
            l = lines[i].rstrip("\n")
            if not l.strip():
                break
            if l.strip().startswith("#") or l.strip().startswith("```"):
                break
            if l.strip().startswith("- ") and not para_lines:
                break
            if l.strip().startswith("> ") and not para_lines:
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

    pdf = DemoScriptPDF()
    pdf.set_margins(18, 18, 18)

    # -- Cover page --
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 95, "F")

    pdf.set_y(22)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 12, "Live Demo Script",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(180, 200, 220)
    pdf.cell(0, 10, "Copilot Studio Focus",
             align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(55)
    pdf.set_draw_color(80, 140, 200)
    pdf.set_line_width(0.4)
    pdf.line(pdf.w * 0.3, pdf.get_y(), pdf.w * 0.7, pdf.get_y())
    pdf.set_line_width(0.2)

    pdf.set_y(63)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 7, "GCC Emphasis | Document Quality + Model Selection",
             align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(110)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MED)
    pdf.multi_cell(0, 6, sanitize_text(
        "Complete setup and execution guide for a Copilot Studio-only demo. "
        "Part 1 demonstrates document quality improvements across three "
        "SharePoint libraries. Part 2 demonstrates model selection impact "
        "with live model swaps on a Dataverse MCP agent."
    ), align="C")

    pdf.set_y(138)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 7, sanitize_text(
        "~18 min  |  3 doc prompts  |  3 model prompts  |  All Copilot Studio"),
        align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 6, "March 2026", align="C")

    # -- Content pages --
    pdf.add_page()
    usable_w = pdf.w - pdf.l_margin - pdf.r_margin

    for block in blocks:
        btype = block[0]

        if btype == "heading":
            level = block[1]
            text = sanitize_text(block[2])

            if level == 1:
                continue  # skip H1, on cover
            elif level == 2:
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
            # Talking point / what to say callouts
            if text.startswith("**Talking point:") or text.startswith("**Narrative:") or text.startswith("**Why this prompt:"):
                clean = sanitize_text(text.replace("**", ""))
                pdf.set_font("Helvetica", "", 9)
                h = pdf.multi_cell(usable_w - 16, 5, clean,
                                   dry_run=True, output="HEIGHT")
                box_h = h + 10
                if pdf.get_y() + box_h > pdf.h - 25:
                    pdf.add_page()
                y = pdf.get_y()
                pdf.set_fill_color(*TIP_BG)
                pdf.set_draw_color(*TIP_BORDER)
                pdf.rect(pdf.l_margin, y, usable_w, box_h, "FD")
                pdf.set_xy(pdf.l_margin + 5, y + 5)
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(*DARK)
                pdf.multi_cell(usable_w - 16, 5, clean)
                pdf.set_y(y + box_h + 3)
            elif text.startswith("**"):
                # Bold-lead paragraph
                render_inline(pdf, text)
                pdf.ln(7)
            else:
                render_inline(pdf, text)
                pdf.ln(7)

        elif btype == "blockquote":
            text = sanitize_text(block[1])
            pdf.set_font("Helvetica", "", 9)
            h = pdf.multi_cell(usable_w - 16, 5, text,
                               dry_run=True, output="HEIGHT")
            box_h = h + 10
            if pdf.get_y() + box_h > pdf.h - 25:
                pdf.add_page()
            y = pdf.get_y()
            pdf.set_fill_color(*CALLOUT_BG)
            pdf.set_draw_color(*CALLOUT_BORDER)
            pdf.rect(pdf.l_margin, y, usable_w, box_h, "FD")
            pdf.set_xy(pdf.l_margin + 5, y + 5)
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(*MED)
            pdf.multi_cell(usable_w - 16, 5, text)
            pdf.set_y(y + box_h + 3)

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
            line_h = 4.2
            block_h = len(code_lines) * line_h + 8
            if pdf.get_y() + block_h > pdf.h - 25:
                pdf.add_page()
            y = pdf.get_y()
            code_w = usable_w - 8
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

            n_cols = len(rows[0])
            col_w = (usable_w - 4) / n_cols

            # Measure max height for each row
            pdf.set_font("Helvetica", "", 8)
            row_heights = []
            for row in rows:
                max_h = 6
                for cell_text in row:
                    clean = sanitize_text(cell_text.replace("**", ""))
                    h = pdf.multi_cell(col_w - 4, 4.5, clean,
                                       dry_run=True, output="HEIGHT")
                    max_h = max(max_h, h + 4)
                row_heights.append(max_h)

            # Check if table fits
            total_h = sum(row_heights)
            if pdf.get_y() + total_h > pdf.h - 25:
                pdf.add_page()

            header = rows[0]
            data_rows = rows[1:] if len(rows) > 1 else []

            # Header row
            y = pdf.get_y()
            rh = row_heights[0]
            for ci, cell_text in enumerate(header):
                x = pdf.l_margin + 2 + ci * col_w
                pdf.set_fill_color(*TABLE_HEADER_BG)
                pdf.rect(x, y, col_w, rh, "F")
                pdf.set_xy(x + 2, y + 2)
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_text_color(*TABLE_HEADER_FG)
                pdf.multi_cell(col_w - 4, 4.5,
                               sanitize_text(cell_text.replace("**", "")))
            pdf.set_y(y + rh)

            # Data rows
            for ri, row in enumerate(data_rows):
                rh = row_heights[ri + 1]
                y = pdf.get_y()
                if y + rh > pdf.h - 25:
                    pdf.add_page()
                    y = pdf.get_y()
                bg = ROW_ALT if ri % 2 == 0 else ROW_WHT
                for ci, cell_text in enumerate(row):
                    x = pdf.l_margin + 2 + ci * col_w
                    pdf.set_fill_color(*bg)
                    pdf.rect(x, y, col_w, rh, "F")
                    pdf.set_xy(x + 2, y + 2)
                    pdf.set_font("Helvetica", "", 8)
                    pdf.set_text_color(*DARK)
                    clean = sanitize_text(cell_text.replace("**", ""))
                    pdf.multi_cell(col_w - 4, 4.5, clean)
                pdf.set_y(y + rh)

            pdf.ln(3)

        elif btype == "hr":
            pdf.ln(2)
            pdf.set_draw_color(*DIVIDER)
            pdf.line(pdf.l_margin + 20, pdf.get_y(),
                     pdf.w - pdf.r_margin - 20, pdf.get_y())
            pdf.ln(4)

    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, "..")
    md_path = os.path.join(project_root, "docs", "live-demo-script.md")
    out_path = os.path.join(project_root, "docs", "pdf", "live-demo-script.pdf")
    build_pdf(md_path, out_path)
