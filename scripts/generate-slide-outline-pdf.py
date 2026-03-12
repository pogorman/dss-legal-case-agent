"""
Generate a slide-outline PDF from the 27-slide presentation outline.
Uses fpdf2 -- no external dependencies beyond what's already installed.

Usage: python scripts/generate-slide-outline-pdf.py
Output: docs/pdf/slide-outline.pdf
"""

from fpdf import FPDF
import os


def sanitize_text(text):
    """Replace Unicode characters that Helvetica cannot render."""
    return (
        text
        .replace("\u2014", "--")    # em dash
        .replace("\u2013", "-")     # en dash
        .replace("\u2018", "'")     # left single quote
        .replace("\u2019", "'")     # right single quote
        .replace("\u201c", '"')     # left double quote
        .replace("\u201d", '"')     # right double quote
        .replace("\u2026", "...")   # ellipsis
        .replace("\u2192", "->")   # right arrow
        .replace("\u2022", "-")    # bullet
        .replace("\u2003", " ")    # em space
    )


# -- Color palette -----------------------------------------------------------
NAVY    = (22, 48, 82)
ACCENT  = (41, 98, 163)
DARK    = (40, 40, 40)
MED     = (90, 90, 90)
LIGHT   = (130, 130, 130)
WHITE   = (255, 255, 255)
ROW_ALT = (241, 245, 249)
ROW_WHT = (255, 255, 255)
TABLE_HEADER_BG = (22, 48, 82)
TABLE_HEADER_FG = (255, 255, 255)
DIVIDER = (200, 210, 220)
GREEN   = (34, 120, 69)
AMBER   = (180, 130, 20)
RED     = (185, 45, 45)
GRAY_BG = (248, 249, 250)

# Level colors
LVL1_COLOR = (76, 175, 80)    # green
LVL2_COLOR = (139, 195, 74)   # light green
LVL3_COLOR = (255, 193, 7)    # amber
LVL4_COLOR = (255, 87, 34)    # deep orange
LVL5_COLOR = (211, 47, 47)    # red


class SlideOutlinePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT)
        self.cell(0, 6, sanitize_text("Agent Fidelity Spectrum for Copilot Studio -- Slide Outline"), align="L")
        self.cell(0, 6, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*DIVIDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-18)
        self.set_draw_color(*DIVIDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*LIGHT)
        self.ln(3)
        self.cell(0, 4, sanitize_text("Confidential  |  March 2026"), align="C")

    # -- Helpers --------------------------------------------------------------
    def section_title(self, text):
        self.ln(4)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*NAVY)
        self.cell(0, 9, sanitize_text(text), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.l_margin + 50, self.get_y())
        self.set_line_width(0.2)
        self.ln(5)

    def subsection_title(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*ACCENT)
        self.cell(0, 7, sanitize_text(text), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text, bold_lead=None):
        text = sanitize_text(text)
        if bold_lead:
            self.set_font("Helvetica", "B", 9.5)
            self.set_text_color(*DARK)
            self.write(5.5, sanitize_text(bold_lead) + " ")
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text, bold_lead=None, indent=8):
        text = sanitize_text(text)
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*MED)
        self.write(5.5, "- ")
        if bold_lead:
            self.set_font("Helvetica", "B", 9.5)
            self.set_text_color(*DARK)
            self.write(5.5, sanitize_text(bold_lead) + "  ")
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*DARK)
        self.multi_cell(self.w - self.r_margin - self.get_x(), 5.5, text)
        self.ln(1)

    def styled_table(self, headers, rows, col_widths, row_height=6, font_size=7.5):
        self.set_font("Helvetica", "B", font_size)
        self.set_fill_color(*TABLE_HEADER_BG)
        self.set_text_color(*TABLE_HEADER_FG)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], row_height + 1, sanitize_text(h), border=0, align="C", fill=True)
        self.ln()
        self.set_font("Helvetica", "", font_size)
        for r_idx, row in enumerate(rows):
            bg = ROW_ALT if r_idx % 2 == 0 else ROW_WHT
            self.set_fill_color(*bg)
            for i, val in enumerate(row):
                self.set_text_color(*DARK)
                self.cell(col_widths[i], row_height, sanitize_text(val), border=0,
                          align="C" if i > 0 else "L", fill=True)
            self.ln()

    def visual_note(self, text):
        """Render visual suggestions in italic gray text."""
        self.set_font("Helvetica", "I", 8.5)
        self.set_text_color(*LIGHT)
        self.multi_cell(0, 5, sanitize_text("Visual: " + text))
        self.ln(1)

    def talking_point(self, text):
        """Render talking points in italic with quotes."""
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(*MED)
        self.multi_cell(0, 5.5, sanitize_text('Talking point: "' + text + '"'))
        self.ln(1)

    def speaker_note(self, text):
        """Render speaker notes in italic with a left accent bar (blockquote style)."""
        x = self.l_margin
        bar_x = x + 4
        text_x = x + 8
        text_w = self.w - self.r_margin - text_x

        # Measure height first to avoid orphaning across page break
        self.set_font("Helvetica", "I", 8.5)
        note_h = self.multi_cell(
            text_w, 5, sanitize_text("Speaker notes: " + text),
            dry_run=True, output="HEIGHT"
        )
        usable = self.h - self.b_margin - self.get_y()
        if note_h + 4 > usable:
            self.add_page()

        y_start = self.get_y()

        # Render the text
        self.set_xy(text_x, y_start)
        self.set_text_color(*MED)
        self.multi_cell(text_w, 5, sanitize_text("Speaker notes: " + text))
        y_end = self.get_y()

        # Draw the accent bar
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.8)
        self.line(bar_x, y_start, bar_x, y_end)
        self.set_line_width(0.2)

        self.ln(2)

    def slide_heading(self, slide_num, title):
        """Render a slide as a subsection with number and title."""
        self.subsection_title(f"Slide {slide_num}: {title}")

    def headline(self, text):
        """Render a bold headline for a slide."""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*NAVY)
        self.multi_cell(0, 6, sanitize_text(text))
        self.ln(2)


def build_pdf():
    pdf = SlideOutlinePDF()
    pdf.set_margins(20, 20, 20)

    # ====================================================================
    # COVER PAGE
    # ====================================================================
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 120, "F")

    pdf.set_y(30)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 14, "Agent Fidelity Spectrum", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 14, "for Copilot Studio", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(180, 200, 220)
    pdf.cell(0, 10, "Slide Outline", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_draw_color(80, 140, 200)
    pdf.set_line_width(0.4)
    line_y = 71.5  # centered between "Slide Outline" (bottom ~68) and "27 Slides" (top 75)
    pdf.line(pdf.w * 0.3, line_y, pdf.w * 0.7, line_y)
    pdf.set_line_width(0.2)

    pdf.set_y(75)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 7, "27 Slides  |  March 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    # Five colored level indicators on cover
    pdf.set_y(130)
    levels = [
        (LVL1_COLOR, "Discovery"),
        (LVL2_COLOR, "Summarization"),
        (LVL3_COLOR, "Operational"),
        (LVL4_COLOR, "Investigative"),
        (LVL5_COLOR, "Adjudicative"),
    ]
    bar_w = (pdf.w - 40) / 5
    for i, (color, name) in enumerate(levels):
        x = 20 + i * bar_w
        pdf.set_fill_color(*color)
        pdf.rect(x, pdf.get_y(), bar_w - 2, 8, "F")
        pdf.set_xy(x, pdf.get_y())
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*WHITE)
        pdf.cell(bar_w - 2, 8, sanitize_text(f"L{i+1}: {name}"), align="C")
    pdf.set_y(pdf.get_y() + 14)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MED)
    pdf.multi_cell(0, 6.5, sanitize_text(
        "Target: 27 slides, 50-60 minutes (40-45 min presentation + live demo + 10-15 min Q&A)"
    ), align="C")

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 7, sanitize_text("462 test runs  |  21 agents  |  6 models  |  27 slides  |  2 use cases"),
             align="C", new_x="LMARGIN", new_y="NEXT")

    # ====================================================================
    # SLIDE 1: Title
    # ====================================================================
    pdf.add_page()
    pdf.slide_heading(1, "Title")

    pdf.headline("AI Agent Fidelity for Government: A Five-Level Framework")

    pdf.body_text(
        "Subtitle: Findings from 462 Test Runs Across 21 Agent Configurations"
    )

    pdf.visual_note("Clean title slide with agency-appropriate branding")

    pdf.speaker_note(
        "Some of you may remember me from such demos as the delegation demo, "
        "or one of my many ALM demos. Those demos and this one have something "
        "in common: I like to build test harnesses for real-world use cases my "
        "customers care about. And they all deal with the same fundamental "
        "topic: accuracy."
    )

    # ====================================================================
    # SLIDE 2: At a Glance
    # ====================================================================
    pdf.slide_heading(2, "At a Glance")

    pdf.body_text(
        "462 test runs across 21 agent configurations and 6 models, 2 government use cases, "
        "and 7 testing rounds. Three gaps emerged at the higher levels: tools, "
        "data, and model. Every gap was fixable, and none required AI expertise."
    )

    # ── 4 level tiles (2x2, ~75% width) + legend (right ~25%) ──
    total_w = pdf.w - pdf.l_margin - pdf.r_margin
    lvl_grid = [
        [(LVL2_COLOR, "Levels 1 - 2", "Just Works",
          "8/10 with zero customization. Model choice irrelevant."),
         (LVL3_COLOR, "Level 3", "Data Over Documents",
          "MCP outperformed document search on every aggregate query.")],
        [(LVL4_COLOR, "Level 4", "The Inflection Point",
          "Three gaps emerged: tools, data, and model. All fixable."),
         (LVL5_COLOR, "Level 5", "Human in the Loop",
          "High fidelity at L4 means humans review conclusions, not raw data.")],
    ]
    legend_items = [
        (LVL1_COLOR, "L1", "Discovery"),
        (LVL2_COLOR, "L2", "Summarization"),
        (LVL3_COLOR, "L3", "Operational"),
        (LVL4_COLOR, "L4", "Investigative"),
        (LVL5_COLOR, "L5", "Adjudicative"),
    ]

    lvl_pad = 4
    lvl_stripe = 3
    lvl_col_gap = 3
    lvl_row_gap = 3
    legend_gap = 4

    tiles_zone_w = total_w * 0.75 - legend_gap / 2
    legend_zone_w = total_w - tiles_zone_w - legend_gap
    tile_w = (tiles_zone_w - lvl_col_gap) / 2
    lvl_inner_w = tile_w - lvl_stripe - lvl_pad * 2

    # Measure row heights
    row_heights = []
    for row in lvl_grid:
        cell_heights = []
        for _, label, title, body in row:
            pdf.set_font("Helvetica", "B", 7)
            lh = pdf.multi_cell(lvl_inner_w, 4, sanitize_text(label), dry_run=True, output="HEIGHT")
            pdf.set_font("Helvetica", "B", 10)
            th = pdf.multi_cell(lvl_inner_w, 5, sanitize_text(title), dry_run=True, output="HEIGHT")
            pdf.set_font("Helvetica", "", 8)
            bh = pdf.multi_cell(lvl_inner_w, 4, sanitize_text(body), dry_run=True, output="HEIGHT")
            cell_heights.append(lvl_pad + lh + th + 1 + bh + lvl_pad)
        row_heights.append(max(cell_heights))

    grid_total_h = sum(row_heights) + lvl_row_gap
    grid_y = pdf.get_y()

    # Render level tiles
    cur_y = grid_y
    for ri, row in enumerate(lvl_grid):
        rh = row_heights[ri]
        for ci, (color, label, title, body) in enumerate(row):
            tx = pdf.l_margin + ci * (tile_w + lvl_col_gap)
            tbg = tuple(int(c * 0.12 + 255 * 0.88) for c in color)
            pdf.set_fill_color(*tbg)
            pdf.rect(tx, cur_y, tile_w, rh, "F")
            pdf.set_fill_color(*color)
            pdf.rect(tx, cur_y, lvl_stripe, rh, "F")
            cx = tx + lvl_stripe + lvl_pad
            pdf.set_xy(cx, cur_y + lvl_pad)
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_text_color(*color)
            pdf.multi_cell(lvl_inner_w, 4, sanitize_text(label))
            pdf.set_x(cx)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*DARK)
            pdf.multi_cell(lvl_inner_w, 5, sanitize_text(title))
            pdf.set_xy(cx, pdf.get_y() + 1)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*MED)
            pdf.multi_cell(lvl_inner_w, 4, sanitize_text(body))
        cur_y += rh + lvl_row_gap

    # ── Legend tile (right side, spans both rows) ──
    legend_x = pdf.l_margin + tiles_zone_w + legend_gap
    legend_pad_inner = 5
    legend_badge = 5.5
    legend_label_h = 5

    lbg = tuple(int(c * 0.06 + 255 * 0.94) for c in NAVY)
    pdf.set_fill_color(*lbg)
    pdf.rect(legend_x, grid_y, legend_zone_w, grid_total_h, "F")
    pdf.set_fill_color(*NAVY)
    pdf.rect(legend_x, grid_y, 2, grid_total_h, "F")

    lx = legend_x + 2 + legend_pad_inner
    pdf.set_xy(lx, grid_y + legend_pad_inner - 2)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, legend_label_h, "The Five Levels")

    badges_h = len(legend_items) * (legend_badge + 3)
    remaining_h = grid_total_h - legend_pad_inner - legend_label_h - legend_pad_inner
    badge_y_start = grid_y + legend_pad_inner + legend_label_h + (remaining_h - badges_h) / 2
    if badge_y_start < grid_y + legend_pad_inner + legend_label_h:
        badge_y_start = grid_y + legend_pad_inner + legend_label_h

    ly = badge_y_start
    for color, num, name in legend_items:
        pdf.set_fill_color(*color)
        pdf.rect(lx, ly, legend_badge, legend_badge, "F")
        pdf.set_xy(lx, ly)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(legend_badge, legend_badge, num, align="C")
        pdf.set_xy(lx + legend_badge + 2, ly)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*DARK)
        pdf.cell(0, legend_badge, sanitize_text(name))
        ly += legend_badge + 3

    pdf.set_y(grid_y + grid_total_h + 4)

    # ── Use case tiles ──
    pdf.ln(2)
    uc_data = [
        (ACCENT, "Use Case 1", "Legal Case Analysis",
         "50 cases, 277 people, 333 events, 151 discrepancies",
         "15 agent configurations"),
        (ACCENT, "Use Case 2", "Investigative Analytics",
         "34M rows, 584K properties, 1.6M violations",
         "8 agent configurations"),
    ]
    uc_tile_w = (total_w - lvl_col_gap) / 2
    uc_pad = 4
    uc_stripe = 3
    uc_inner = uc_tile_w - uc_stripe - uc_pad * 2

    # Measure
    uc_heights = []
    for _, label, title, stats, agents in uc_data:
        pdf.set_font("Helvetica", "B", 7)
        lh = pdf.multi_cell(uc_inner, 4, sanitize_text(label), dry_run=True, output="HEIGHT")
        pdf.set_font("Helvetica", "B", 10)
        th = pdf.multi_cell(uc_inner, 5.5, sanitize_text(title), dry_run=True, output="HEIGHT")
        pdf.set_font("Helvetica", "", 8)
        sh = pdf.multi_cell(uc_inner, 4, sanitize_text(stats), dry_run=True, output="HEIGHT")
        uc_heights.append(uc_pad + lh + 1 + th + 1 + sh + 2 + 5 + uc_pad)
    uc_h = max(uc_heights)
    uc_y = pdf.get_y()

    for i, (color, label, title, stats, agents) in enumerate(uc_data):
        x = pdf.l_margin + i * (uc_tile_w + lvl_col_gap)
        bg = tuple(int(c * 0.10 + 255 * 0.90) for c in color)
        pdf.set_fill_color(*bg)
        pdf.rect(x, uc_y, uc_tile_w, uc_h, "F")
        pdf.set_fill_color(*color)
        pdf.rect(x, uc_y, uc_stripe, uc_h, "F")
        cx = x + uc_stripe + uc_pad
        pdf.set_xy(cx, uc_y + uc_pad)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*color)
        pdf.multi_cell(uc_inner, 4, sanitize_text(label))
        pdf.set_xy(cx, pdf.get_y() + 1)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(uc_inner, 5.5, sanitize_text(title))
        pdf.set_xy(cx, pdf.get_y() + 1)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*MED)
        pdf.multi_cell(uc_inner, 4, sanitize_text(stats))
        pdf.set_xy(cx, pdf.get_y() + 2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*DARK)
        pdf.cell(uc_inner, 5, sanitize_text(agents))

    pdf.set_y(uc_y + uc_h + 4)

    # Closing summary
    pdf.body_text(
        "Every gap was fixable, and none required AI expertise. "
        "One new tool, cleaner data, and cross-referenced documents."
    )

    pdf.talking_point(
        "This is the whole story on one slide. Everything that follows is how we got here."
    )

    # ====================================================================
    # SLIDE 3: The Two Use Cases
    # ====================================================================
    pdf.slide_heading(3, "The Two Use Cases")

    pdf.headline("Two real government scenarios, twenty-one agent configurations")

    pdf.bullet(
        "50 synthetic legal cases with 277 people, 333 timeline events, "
        "338 statements, and 151 discrepancies. Can an AI agent prepare "
        "a case for an attorney as well as a paralegal?",
        bold_lead="Legal Case Analysis."
    )
    pdf.bullet(
        "34 million rows of property, violation, and licensing data across "
        "584K properties and 1.6M violations. Can an AI agent surface patterns "
        "an investigator would otherwise miss?",
        bold_lead="Investigative Analytics."
    )

    pdf.visual_note(
        "Two-column layout: UC1 (case files, structured DB) on left, "
        "UC2 (large-scale analytics) on right"
    )

    pdf.talking_point(
        "Both use cases came from real customer conversations. "
        "The data is synthetic but the structure mirrors production systems."
    )

    # ====================================================================
    # SLIDE 4: How This Was Built
    # ====================================================================
    pdf.slide_heading(4, "How This Was Built")

    pdf.headline("One solution engineer. One AI coding assistant. Four weeks.")

    pdf.bullet(
        "Architecture decisions, Azure service selection, schema design, security "
        "posture, and the five-level fidelity framework came from domain expertise "
        "and customer conversations.",
        bold_lead="Human-directed."
    )
    pdf.bullet(
        "TypeScript Functions, MCP server, SQL schema, 50 synthetic cases (277 "
        "people, 333 timeline events), web UI, six PDF generators, and this deck "
        "were generated by AI and reviewed by a human.",
        bold_lead="AI-accelerated."
    )
    pdf.bullet(
        "462 test runs across 21 agent configurations and 6 models, scored by hand. Every "
        "dangerous response was caught through manual review. That is exactly "
        "the point of Level 5.",
        bold_lead="Human-verified."
    )

    pdf.visual_note("Three-column layout: Human-directed | AI-accelerated | Human-verified")

    pdf.talking_point(
        "We practiced what we preach. This entire project is Level 5: "
        "AI-accelerated, human-verified."
    )

    # ====================================================================
    # SLIDE 5: Meet the Agents
    # ====================================================================
    pdf.slide_heading(5, "Meet the Agents")

    pdf.headline("21 configurations, 3 approaches, 1 set of test prompts")

    pdf.bullet(
        "M365 Copilot -- three JSON manifest files pointing at the MCP server, "
        "zero code, platform picks the model.",
        bold_lead="Zero Code."
    )
    pdf.bullet(
        "Copilot Studio -- SharePoint docs, knowledge base, MCP server, or Dataverse. "
        "Same platform, different data sources. 12 configurations across Commercial and GCC.",
        bold_lead="Configure It."
    )
    pdf.bullet(
        "Case Analyst (TypeScript), Investigative Agent (OpenAI SDK), "
        "Triage Agent (Semantic Kernel), Foundry Agent (Agent Service). "
        "Full control over orchestration, tools, and model selection. 8 configurations.",
        bold_lead="Build It Yourself."
    )

    pdf.visual_note(
        "Three-column layout: green (Zero Code), amber (Configure It), "
        "blue (Build It Yourself) with agent names and config counts"
    )

    pdf.talking_point(
        "Same prompts. Same ground truth. The only variable is how you build it."
    )

    pdf.speaker_note(
        "You'll see these names on every chart going forward. The important thing "
        "is the spectrum: on the left, you're up and running in an afternoon. On the "
        "right, you have full control. The question is which level of fidelity "
        "you need -- and that's what the rest of this talk is about."
    )

    # ====================================================================
    # SLIDE 6: The Question
    # ====================================================================
    pdf.slide_heading(6, "The Question")

    pdf.headline('"Not all AI use cases are created equal."')

    pdf.bullet(
        "Your policy lookup chatbot and your legal case preparation tool have "
        "fundamentally different accuracy requirements"
    )
    pdf.bullet(
        "This framework helps you decide where to deploy aggressively, where to "
        "add guardrails, and where human review is non-negotiable"
    )

    pdf.visual_note('Spectrum arrow from "Low Stakes" to "High Stakes"')

    pdf.speaker_note(
        "A policy lookup chatbot that hallucinates a deadline is annoying. A legal case "
        "prep tool that misses a discrepancy can change an outcome. The framework we're "
        "about to walk through helps you match your engineering investment to the stakes "
        "of the use case -- so you know when 'good enough' really is good enough, and "
        "when it isn't."
    )

    # ====================================================================
    # SLIDE 3: The Five Levels (Overview)
    # ====================================================================
    pdf.slide_heading(7, "The Five Levels (Overview)")

    lvl_headers = ["Level", "Name", "Stakes", "Example"]
    lvl_widths = [14, 34, 48, 74]
    lvl_rows = [
        ["1", "Discovery", "Inconvenience", '"Find our leave policy"'],
        ["2", "Summarization", "Wasted time", '"Summarize this audit report"'],
        ["3", "Operational", "Misallocated resources", '"How many open cases by type?"'],
        ["4", "Investigative", "Missed evidence", '"Build a timeline from these records"'],
        ["5", "Adjudicative", "Wrong legal outcome", '"Prepare facts for this hearing"'],
    ]
    pdf.styled_table(lvl_headers, lvl_rows, lvl_widths, font_size=8)

    pdf.ln(2)
    pdf.visual_note("Stacked bar or pyramid with color-coded levels (green to red)")

    pdf.talking_point("Where does your highest-priority use case fall?")

    # ====================================================================
    # SLIDE 4: Levels 1-2 -- The Quick Win
    # ====================================================================
    pdf.slide_heading(8, "Levels 1-2 -- The Quick Win")

    pdf.headline("Document agents start strong and improve quickly")

    pdf.bullet("Point Copilot at your SharePoint library — Commercial agents scored 8/10 out of the gate")
    pdf.bullet("GCC agents started lower (3/10) but reached 7-9/10 after cross-referencing documents")
    pdf.bullet("No custom code, no databases, no tool design")
    pdf.bullet("Good enough for policy lookup, report summarization, meeting notes")

    pdf.visual_note("Simple diagram: Copilot -> SharePoint -> Answer")

    pdf.talking_point("This is where most agencies should start. It works today, and the improvements are straightforward.")

    # ====================================================================
    # SLIDE 5: Level 3 -- Structured Data Starts Winning
    # ====================================================================
    pdf.slide_heading(9, "Level 3 -- Structured Data Starts Winning")

    pdf.headline("Structured data agents outperform documents on every aggregate query")

    pdf.bullet(
        "Document agents excel at single-case analysis (10/10) but struggle to answer "
        "cross-case aggregate queries -- they can't count, sum, or filter across a full dataset"
    )
    pdf.bullet(
        '"How many active cases?" "What\'s the breakdown by county?" "Top 5 violators?" '
        "-- these require structured data"
    )
    pdf.bullet(
        "Agents with structured data access -- both Copilot Studio MCP and pro-code -- "
        "answer every aggregate query correctly when paired with a capable model"
    )

    pdf.visual_note(
        'Side-by-side comparison. Document agent: "I don\'t have that information." '
        "MCP agent: table with counts."
    )

    pdf.talking_point("This is where you start investing in data structure. "
        "Document agents are perfect for single-case work, but the moment you need "
        "to query across cases, you need structured data.")

    # ====================================================================
    # SLIDE 6: Level 4 -- The Inflection Point
    # ====================================================================
    pdf.slide_heading(10, "Level 4 -- The Inflection Point")

    pdf.headline("This is where engineering decisions determine success or failure")

    pdf.body_text("Three gaps emerged in testing:")

    pdf.bullet("GPT-4.1 scores 9.5/10 vs GPT-4o at 4/10", bold_lead="The model gap:")
    pdf.bullet("One missing tool caused 87% failure rate in a pro-code agent", bold_lead="The tool gap:")
    pdf.bullet(
        "Facts buried in narrative text were invisible to agents",
        bold_lead="The data gap:"
    )

    pdf.visual_note("Three gap icons with before/after numbers")

    pdf.talking_point(
        "Level 4 is where the investment pays off -- or doesn't. "
        "Every one of these gaps was invisible until we tested against ground truth. "
        "You will not find these in production without a test harness."
    )

    # ====================================================================
    # SLIDE 7: The Model Gap (Detail)
    # ====================================================================
    pdf.slide_heading(11, "The Model Gap (Detail)")

    pdf.headline("Same tools, same data, same backend -- only the model changed")

    model_headers = ["Model", "Infrastructure", "Score"]
    model_widths = [56, 60, 54]
    model_rows = [
        ["Sonnet 4.6 (Anthropic)", "Copilot Studio + Dataverse MCP", "11/11"],
        ["GPT-5 Reasoning", "Copilot Studio + Dataverse MCP", "10/11"],
        ["GPT-4.1", "Pro-code + custom MCP", "9.5/10"],
        ["GPT-4.1", "Copilot Studio + Dataverse MCP", "6/11"],
        ["GPT-5 Auto", "Copilot Studio + Dataverse MCP", "4/11"],
        ["GPT-4o (GCC default)", "Pro-code + custom MCP", "4/10"],
        ["GPT-4o (GCC default)", "Copilot Studio + Dataverse MCP", "3.2/11"],
        ["Platform-assigned", "M365 Copilot", "2/10"],
    ]
    pdf.styled_table(model_headers, model_rows, model_widths, font_size=8)

    pdf.ln(2)
    pdf.bullet("Newer is not always better: GPT-5 Auto scored worse than GPT-4.1")
    pdf.bullet("Anthropic models now available in Commercial Copilot Studio model picker")
    pdf.bullet("GCC defaults to GPT-4o -- pro-code agents can use GPT-4.1 via Azure OpenAI")

    pdf.visual_note("Bar chart with dramatic gap between models, color-coded by score")

    pdf.talking_point("The model is the single biggest variable at Level 4.")

    # ====================================================================
    # SLIDE 8: The Tool Gap (Detail)
    # ====================================================================
    pdf.slide_heading(12, "The Tool Gap (Detail)")

    pdf.headline("87% failure rate from one missing tool")

    pdf.bullet(
        'Agents could not convert "4763 Griscom St" to a database parcel ID'
    )
    pdf.bullet("15 address lookups across 5 agents, only 2 succeeded")
    pdf.bullet("One fuzzy-match tool added: zero failures in retesting")
    pdf.bullet("Investigative Agent: 1 out of 10 to a perfect 10 out of 10")

    pdf.visual_note("Before/after with the single tool highlighted as the change")

    pdf.talking_point("Tool design is as important as model selection. Maybe more.")

    # ====================================================================
    # SLIDE 9: Level 5 -- Trust But Verify
    # ====================================================================
    pdf.add_page()
    pdf.slide_heading(13, "Level 5 -- Trust But Verify")

    pdf.headline("Even our best agent reproduced a dangerous error")

    pdf.bullet(
        'Sheriff\'s Report: "no fractures detected on skeletal survey"'
    )
    pdf.bullet("Medical Records: bilateral long bone fractures documented")
    pdf.bullet(
        "7 of 8 document agents quoted the sheriff's report without cross-checking"
    )
    pdf.bullet(
        "The citation was real. The confidence was justified. The conclusion was dangerous."
    )

    pdf.visual_note(
        "Split screen -- Sheriff Report quote on left, Medical Records finding on right"
    )

    pdf.talking_point("This is why Level 5 requires human review. Always.")

    pdf.speaker_note(
        "Connect to daily experience: Copilot helps you draft an email -- you review it. "
        "Copilot helps you write code -- you review it. Why would we skip human review at "
        "any of these five levels, especially Level 5 where the stakes are a family's future?"
    )

    pdf.ln(2)
    pdf.bullet(
        "Added cross-reference headers to each document (zero content changes)",
        bold_lead="Document improvement:"
    )
    pdf.bullet(
        "Commercial agent: 8/10 to 10/10 -- pulled Medical Records as primary source"
    )
    pdf.bullet(
        "GCC agent: 3/10 to 9/10 across all 10 prompts with document hygiene alone"
    )
    pdf.bullet(
        "Zero code, zero engineering -- document hygiene that any paralegal can implement"
    )

    pdf.talking_point(
        "The good news: document structure improvements can fix retrieval failures "
        "without any custom engineering."
    )

    # ====================================================================
    # SLIDE 10: The Danger Taxonomy
    # ====================================================================
    pdf.slide_heading(14, "The Danger Taxonomy")

    pdf.headline("Five categories of AI failure, ranked by severity")

    pdf.bullet(
        "Data retrieved, answer not recognized",
        bold_lead="1. False negative (Critical) --"
    )
    pdf.bullet(
        "Source document had an error, agent quoted it accurately",
        bold_lead="2. Faithfully reproduced misinformation (Critical) --"
    )
    pdf.bullet(
        "Real fact, wrong person",
        bold_lead="3. Misattribution (High) --"
    )
    pdf.bullet(
        "Invented detail with no source",
        bold_lead="4. Hallucinated fact with confidence (High) --"
    )
    pdf.bullet(
        "No results, no indication anything went wrong",
        bold_lead="5. Silent failure (Medium) --"
    )

    pdf.visual_note("Severity ladder or risk matrix, color-coded red to yellow")

    pdf.talking_point(
        "These are not hypothetical. We documented each one across 462 test runs."
    )

    # ====================================================================
    # SLIDE 11: The Iterative Process
    # ====================================================================
    pdf.slide_heading(15, "The Iterative Process")

    pdf.headline("Deploying an agent is not a one-time event")

    pdf.bullet(
        "Baseline testing -- measure failures against ground truth",
        bold_lead="Round 0:"
    )
    pdf.bullet(
        "Fix the data -- make facts discrete and queryable",
        bold_lead="Round 1:"
    )
    pdf.bullet(
        "Fix the tools -- help the model reach the data",
        bold_lead="Round 2:"
    )
    pdf.bullet(
        "Validate across models -- confirm what works where",
        bold_lead="Round 3:"
    )

    pdf.visual_note(
        "Circular improvement diagram with 4 stages, arrows showing iteration"
    )

    pdf.talking_point("Every organization will go through these rounds, in this order.")

    # ====================================================================
    # SLIDE 12: Results After Iteration
    # ====================================================================
    pdf.slide_heading(16, "Results After Iteration")

    pdf.headline(
        "Six agents reached 9-10 out of 10 after iterative improvement"
    )

    iter_headers = ["Agent", "Round 0", "Final", "Fix"]
    iter_widths = [60, 22, 22, 66]
    iter_rows = [
        ["SP/PDF/GCC (Copilot Studio)", "3/10", "9/10", "Cross-referenced documents (zero code)"],
        ["KB/DOCX/Com (Copilot Studio)", "6/10", "10/10", "Cross-referenced documents (zero code)"],
        ["Commercial MCP (Copilot Studio)", "8/10", "10/10", "Tool descriptions + data cleanup"],
        ["Investigative Agent (OpenAI SDK)", "1/10", "10/10", "One fuzzy-match tool added"],
        ["Foundry Agent", "4/10", "9/10", "Tool descriptions + data cleanup"],
        ["Triage Agent (Semantic Kernel)", "0/10", "10/10", "5 rounds: tools, data, model"],
    ]
    pdf.styled_table(iter_headers, iter_rows, iter_widths, font_size=7.5)

    pdf.ln(2)
    pdf.visual_note("Improvement arc showing Round 0 baseline to final score")

    pdf.talking_point(
        "The first two rows required zero engineering -- just document hygiene "
        "that any paralegal can implement. The rest required iterative tool and data work."
    )

    # ====================================================================
    # SLIDE 13: The Code Spectrum
    # ====================================================================
    pdf.slide_heading(17, "The Code Spectrum")

    pdf.headline("Zero code to full code -- same fidelity when you control the model")

    code_headers = ["Approach", "Code", "Best For"]
    code_widths = [60, 52, 58]
    code_rows = [
        ["M365 Copilot (Com)", "Zero (3 JSON manifests)", "Levels 1-2"],
        ["Copilot Studio", "Zero to low code", "Levels 1-3"],
        ["Foundry Agent", "Minimal code", "Levels 3-4"],
        ["Custom SDK (OpenAI, SK)", "Full code", "Levels 4-5"],
    ]
    pdf.styled_table(code_headers, code_rows, code_widths, font_size=8)

    pdf.ln(2)
    pdf.visual_note(
        "Horizontal spectrum from zero to full code with fidelity bars all at 9-10"
    )

    pdf.talking_point(
        "The investment buys governance and customization, not fidelity. "
        "Fidelity comes from the model and the data."
    )

    # ====================================================================
    # SLIDE 14: Why Copilot Studio (Tech Series)
    # ====================================================================
    pdf.slide_heading(18, "Why Copilot Studio (Tech Series)")

    pdf.headline("One platform, declarative to pro-code")

    pdf.bullet(
        "Same environment hosts zero-code SharePoint agents AND MCP-connected "
        "structured data agents"
    )
    pdf.bullet(
        "Model flexibility: swap GPT-4o for GPT-4.1, fidelity goes from 4/10 to "
        "10/10 -- no code changes"
    )
    pdf.bullet(
        "Commercial model picker now includes Anthropic (Sonnet 4.6): "
        "perfect 11/11 on Dataverse MCP"
    )
    pdf.bullet(
        "Enterprise governance built in: DLP, audit logging, admin pre-approval "
        "for tool calls"
    )
    pdf.bullet(
        "M365 distribution: agents show up in Teams and Copilot chat -- no separate "
        "app to deploy"
    )
    pdf.bullet(
        "Our test data proves the platform works -- the model is the variable, not "
        "the architecture"
    )

    pdf.visual_note(
        "Copilot Studio logo with radiating connections to SharePoint, MCP, Teams, Foundry"
    )

    pdf.talking_point(
        "Commercial Copilot Studio scored a perfect 10 out of 10 across multiple "
        "data sources. The architecture is sound. The limiting factor is model "
        "availability in GCC."
    )

    pdf.speaker_note(
        "This slide is critical for the tech series. MUST articulate the platform value, "
        "not just the results."
    )

    # ====================================================================
    # SLIDE 15: What to Do at Each Level
    # ====================================================================
    pdf.slide_heading(19, "What to Do at Each Level")

    action_headers = ["Level", "Action"]
    action_widths = [20, 150]
    action_rows = [
        ["1-2", "Deploy Copilot with SharePoint. Clean up document metadata. Done."],
        ["3", "Connect to structured data via MCP. Clear tool descriptions. Summary modes."],
        ["4", "Purpose-built tools. Models with strong multi-step reasoning (GPT-4.1 in our testing). Ground truth test suite. Budget 3+ rounds."],
        ["5", "Level 4 + human review workflows + audit logging + citation linking."],
    ]
    pdf.styled_table(action_headers, action_rows, action_widths, font_size=8)

    pdf.ln(2)
    pdf.visual_note(
        "Checklist format, one row per level, with investment increasing rightward"
    )

    pdf.talking_point("Match your investment to your fidelity requirement.")

    # ====================================================================
    # SLIDE 16: Government Cloud Customers
    # ====================================================================
    pdf.slide_heading(20, "Government Cloud Customers")

    pdf.headline("Copilot Studio works at every level -- the levers differ")

    pdf.ln(1)
    pdf.body_text("What to use at each level:", bold_lead=None)

    pdf.bullet(
        "Copilot Studio, any configuration.",
        bold_lead="Levels 1-3:"
    )
    pdf.bullet(
        "Copilot Studio with good document hygiene (9/10 proven in GCC with GPT-4o).",
        bold_lead="Levels 4-5 (documents):"
    )
    pdf.bullet(
        "Model selection matters for structured data queries. Sonnet 4.6 scored 11/11, "
        "GPT-5 Reasoning scored 10/11 (both Commercial). "
        "In GCC today, pro-code agents with GPT-4.1 via Azure OpenAI.",
        bold_lead="Structured data gap:"
    )

    pdf.ln(2)
    pdf.body_text("The GCC gap:", bold_lead=None)

    pdf.bullet("Model selection not yet available in GCC Copilot Studio -- document quality is your lever today")
    pdf.bullet("When expanded model availability arrives in GCC, every agent improves overnight with zero changes")
    pdf.bullet("Start building ground truth test suites now so you are ready to measure the improvement")

    pdf.visual_note("Three-tier layout with level colors, GCC gap callout at bottom")

    pdf.talking_point("Know what works today. Plan for what's coming.")

    # ====================================================================
    # SLIDE 16b: How We Score
    # ====================================================================
    pdf.slide_heading(21, "How We Score: Ground Truth Grading")

    pdf.headline("Every grade is verifiable -- we wrote the data")

    pdf.body_text(
        "All 50 cases are synthetic. We control the ground truth for every prompt. "
        "Grading is not subjective -- a correct answer is provably correct, and a wrong "
        "answer is provably wrong."
    )

    pdf.ln(1)
    pdf.styled_table(
        ["Score", "Meaning", "Example"],
        [
            ["10", "Fully correct, complete, properly sourced", "All facts match ground truth, sources cited"],
            ["8-9", "Correct on key facts, one minor detail missing", "Found all statements but missed one source page"],
            ["5", "Partially correct or incomplete", "Found one of two data sources, or wrong time"],
            ["1-4", "Meaningful attempt but significant gaps", "Found the right case but missed key facts"],
            ["0", "Wrong, hallucinated, or dangerously confident", "Quoted real citation, drew wrong conclusion"],
        ],
        col_widths=[16, 70, 84],
        row_height=7,
        font_size=7.5,
    )

    pdf.ln(3)
    pdf.body_text("How scores become totals:", bold_lead=None)
    pdf.bullet("Each prompt scored 0-10 against known ground truth (one run per agent)")
    pdf.bullet("Per-prompt scores averaged across all prompts for that agent")
    pdf.bullet("462 test runs across 21 agent configurations and 6 models")
    pdf.bullet("Graded by Claude against ground truth during live demo")

    pdf.visual_note("Left: 0-10 scale table with anchors. Right: process steps. Bottom callout box.")

    pdf.speaker_note(
        "We grade against data we wrote. Every correct answer is verifiable. "
        "Every wrong answer is provably wrong -- not a matter of interpretation. "
        "The 0-10 scale lets us distinguish between an agent that found the right "
        "case but missed a key detail (8) versus one that got half the answer (5) "
        "versus one that confidently gave the wrong answer (0). "
        "During the live demo, I'll paste agent responses into Claude Code and it will "
        "grade them against the ground truth in real time."
    )

    # ====================================================================
    # SLIDE 17: Live Demo Title Card
    # ====================================================================
    pdf.slide_heading(22, "Live Demo Title Card")

    pdf.headline('"Same agent. Change one variable. Watch the result change."')

    pdf.body_text("[Switch to Copilot Studio -- all demos run in the platform]")

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 6, "Part 1: Document Quality (~10 min)", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.bullet("3 agents, same model (GPT-4o/GCC), 3 SharePoint libraries: Raw, Cross-Referenced, Enriched")
    pdf.bullet('Prompt 1: "Did the Sheriff\'s Office find fractures in the skeletal survey?" (FAIL -> PASS -> PASS)')
    pdf.bullet('Prompt 2: "What did Marcus Webb tell hospital staff?" (FAIL -> PARTIAL -> PASS)')
    pdf.bullet('Prompt 3: "Complete timeline for case 2024-DR-42-0892" (FAIL -> PASS -> PASS)')
    pdf.bullet("Score arc: 3/10 -> 7/10 -> 8/10 for $0 and 45 minutes")

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 6, "Part 2: Model Selection (~8 min)", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.bullet("1 Dataverse MCP agent, swap model live: GPT-4o -> Sonnet 4.6")
    pdf.bullet('Prompt 1: "Which cases involve Termination of Parental Rights?" (0 -> 10)')
    pdf.bullet('Prompt 2: "What did Marcus Webb tell hospital staff?" (0 -> 10)')
    pdf.bullet('Prompt 3: "Time gap between thump and hospital?" (0 -> 10)')
    pdf.bullet("Full battery (5 models): GPT-4o = 3.2/11, GPT-5 Auto = 4/11, GPT-4.1 = 6/11, GPT-5 Reasoning = 10/11, Sonnet 4.6 = 11/11")

    pdf.visual_note("Two-part layout: document quality levers on left, model selection on right")

    # ====================================================================
    # SLIDE 18: Surprising Finding -- Agent Challenged Its Own Premise
    # ====================================================================
    pdf.slide_heading(23, "Surprising Finding -- Agent Challenged Its Own Premise")

    pdf.headline("A pro-code agent questioned the question -- and was right")

    pdf.bullet(
        "Asked about a $146,000 purchase vs a $357,100 assessment"
    )
    pdf.bullet(
        "Agent checked the source data: actual assessment was $53,155"
    )
    pdf.bullet(
        "Recalculated using verified numbers instead of the prompt's numbers"
    )
    pdf.bullet("No other agent questioned the input")

    pdf.visual_note("Quote from agent response showing the correction")

    pdf.talking_point(
        "This is what custom orchestration enables -- but only with iterative testing."
    )

    # ====================================================================
    # SLIDE 19: Surprising Finding -- False Negative
    # ====================================================================
    pdf.slide_heading(24, "Surprising Finding -- False Negative")

    pdf.headline("The model retrieved the answer and didn't recognize it")

    pdf.bullet("Agent called the right tools")
    pdf.bullet(
        'Received data containing "two positive drug screens (fentanyl)"'
    )
    pdf.bullet(
        'Concluded: "no drug test results exist in the available data"'
    )
    pdf.bullet(
        "Invisible to users: tool calls look correct, answer sounds confident"
    )

    pdf.visual_note(
        "Screenshot of tool output alongside agent's incorrect conclusion"
    )

    pdf.talking_point(
        "This is why you need ground truth testing. You cannot catch this in production."
    )

    # ====================================================================
    # SLIDE 20: The Bottom Line
    # ====================================================================
    pdf.slide_heading(25, "The Bottom Line")

    pdf.headline("Three numbers to remember")

    pdf.bullet(
        "What you get with zero engineering (Levels 1-2)",
        bold_lead="8/10 --"
    )
    pdf.bullet(
        "What you get with purpose-built tools and GPT-4.1 (Levels 3-4)",
        bold_lead="9.5/10 --"
    )
    pdf.bullet(
        "No score is high enough to skip human review (Level 5)",
        bold_lead="Trust but verify --"
    )

    pdf.visual_note("Three large numbers with icons (document, tools, human)")

    pdf.talking_point(
        "The question is not 'should we deploy AI?' The question is 'which level are "
        "we operating at, and have we invested accordingly?'"
    )

    pdf.speaker_note(
        "So what do we do? Do we just give up on agents? No -- you continue to test "
        "them and make them better, and you always adhere to trust but verify. I have "
        "agents building apps for me right now. If I were building production enterprise "
        "apps, I'd have a team of human developers checking the work, helping test, "
        "reviewing agentic results. The AI accelerates the team. The team validates the AI."
    )

    # ====================================================================
    # SLIDE 21: Full Scorecard
    # ====================================================================
    pdf.slide_heading(26, "Full Scorecard")

    pdf.headline("462 test runs, 21 agent configurations, 6 models, 2 use cases")

    pdf.body_text("Use Case 1: Legal Case Analysis (16 agents)")

    sc1_headers = ["Agent", "Model", "Final"]
    sc1_widths = [92, 40, 38]
    sc1_rows = [
        ["Case Analyst Agent (pro-code)", "GPT-4.1", "10/10"],
        ["Copilot Studio MCP/Com", "GPT-4.1", "10/10"],
        ["Copilot Studio SP/PDF/Com", "GPT-4.1", "10/10"],
        ["Copilot Studio KB/DOCX/Com", "GPT-4.1", "10/10"],
        ["Copilot Studio DV/Com", "Sonnet 4.6", "10/10"],
        ["Copilot Studio DV/Com", "GPT-5 Reasoning", "10/10"],
        ["Copilot Studio SP/DOCX/Com", "GPT-4.1", "9/10"],
        ["Copilot Studio MCP/GCC", "GPT-4o", "9/10"],
        ["Copilot Studio SP/PDF/GCC", "GPT-4o", "9/10"],
        ["Copilot Studio KB/PDF/GCC", "GPT-4o", "9/10"],
        ["Copilot Studio KB/PDF/Com", "GPT-4.1", "8/10"],
        ["Copilot Studio KB/DOCX/GCC", "GPT-4o", "8/10"],
        ["Copilot Studio SP/DOCX/GCC", "GPT-4o", "7/10"],
        ["Copilot Studio DV/Com", "GPT-4.1", "6/10"],
        ["Copilot Studio DV/Com", "GPT-5 Auto", "4/10"],
        ["Copilot Studio DV/GCC", "GPT-4o", "3.2/10"],
    ]
    pdf.styled_table(sc1_headers, sc1_rows, sc1_widths, font_size=7)

    pdf.add_page()
    pdf.body_text("Use Case 2: Investigative Analytics (8 agents)")

    sc2_headers = ["Agent", "Model", "Final"]
    sc2_widths = [92, 40, 38]
    sc2_rows = [
        ["Copilot Studio MCP/Com", "GPT-4.1", "10/10"],
        ["Investigative Agent (OpenAI SDK)", "GPT-4.1", "10/10"],
        ["Triage Agent (Semantic Kernel)", "GPT-4.1", "10/10"],
        ["Foundry Agent", "GPT-4.1", "9/10"],
        ["Copilot Studio SP/PDF/GCC", "GPT-4o", "9/10"],
        ["Copilot Studio SP/PDF/Com", "GPT-4.1", "8/10"],
        ["Copilot Studio MCP/GCC", "GPT-4o", "4/10"],
        ["M365 Copilot MCP/Com", "Platform", "2/10"],
    ]
    pdf.styled_table(sc2_headers, sc2_rows, sc2_widths, font_size=7)

    pdf.ln(3)
    pdf.body_text(
        "Ranked by final score. Dataverse MCP tested across 5 models on identical "
        "infrastructure: Sonnet 4.6 (10/10), GPT-5 Reasoning (10/10), GPT-4.1 (6/10), "
        "GPT-5 Auto (4/10), GPT-4o (3.2/10). Newer models are not always better."
    )

    pdf.talking_point(
        "This is 462 data points. The pattern is clear: "
        "the model and the data matter more than the platform."
    )

    # ====================================================================
    # SLIDE 22: Next Steps
    # ====================================================================
    pdf.slide_heading(27, "Next Steps")

    pdf.headline("Start the conversation")

    pdf.bullet("Where do your use cases fall on the spectrum?")
    pdf.bullet("What data do you already have in structured form?")
    pdf.bullet("What's your risk tolerance for AI-generated output?")
    pdf.bullet(
        "Ready for a deeper dive? We have the architecture, the test data, and "
        "the framework."
    )

    pdf.visual_note("Contact information, QR code to whitepaper")

    pdf.talking_point(
        "I'm not here to sell you a product. I'm here to help you make the right "
        "investment for your mission."
    )

    # ====================================================================
    # OUTPUT
    # ====================================================================
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "pdf")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "slide-outline.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    build_pdf()
