"""
Generate the summary PDF using the five-level accuracy framework.
Uses fpdf2 -- no external dependencies beyond what's already installed.

Usage: python scripts/generate-executive-pdf.py
Output: docs/summary.pdf
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


class ExecutivePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT)
        self.cell(0, 6, sanitize_text("Agent Accuracy Spectrum for Copilot Studio  |  Summary"), align="L")
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
        self.cell(0, 4, sanitize_text("Confidential  |  March 2026  |  313 test runs across 19 agent configurations"), align="C")

    # -- Helpers --------------------------------------------------------------
    def section_title(self, text, link=None):
        if link is not None:
            self.set_link(link)
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
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*DARK)
        if bold_lead:
            combined = f"**{sanitize_text(bold_lead)}** {text}"
            self.multi_cell(0, 5.5, combined, markdown=True)
        else:
            self.multi_cell(0, 5.5, text, markdown=True)
        self.ln(2)

    def bullet(self, text, bold_lead=None, indent=8, label_width=None):
        text = sanitize_text(text)
        x = self.get_x()
        bullet_x = x + indent
        self.set_font("Helvetica", "", 9.5)
        dash_w = self.get_string_width("- ")
        if bold_lead and label_width:
            # Fixed-width label column: "- Label:" in col 1, text in col 2
            self.set_x(bullet_x)
            self.set_text_color(*MED)
            self.write(5.5, "- ")
            self.set_font("Helvetica", "B", 9.5)
            self.set_text_color(*DARK)
            self.write(5.5, sanitize_text(bold_lead) + " ")
            content_x = bullet_x + dash_w + label_width
            content_w = self.w - self.r_margin - content_x
            self.set_xy(content_x, self.get_y())
            old_l_margin = self.l_margin
            self.l_margin = content_x
            self.set_font("Helvetica", "", 9.5)
            self.multi_cell(content_w, 5.5, text)
            self.l_margin = old_l_margin
        elif bold_lead:
            self.set_x(bullet_x)
            self.set_text_color(*MED)
            self.write(5.5, "- ")
            content_x = bullet_x + dash_w
            content_w = self.w - self.r_margin - content_x
            old_l_margin = self.l_margin
            self.l_margin = content_x
            self.set_text_color(*DARK)
            combined = f"**{sanitize_text(bold_lead)}** {text}"
            self.multi_cell(content_w, 5.5, combined, markdown=True)
            self.l_margin = old_l_margin
        else:
            self.set_x(bullet_x)
            self.set_text_color(*MED)
            self.write(5.5, "- ")
            content_x = bullet_x + dash_w
            content_w = self.w - self.r_margin - content_x
            old_l_margin = self.l_margin
            self.l_margin = content_x
            self.set_text_color(*DARK)
            self.multi_cell(content_w, 5.5, text)
            self.l_margin = old_l_margin
        self.ln(1)

    def styled_table(self, headers, rows, col_widths, row_height=6, font_size=7.5,
                      col_aligns=None):
        if col_aligns is None:
            col_aligns = ["L"] + ["C"] * (len(headers) - 1)
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
                          align=col_aligns[i], fill=True)
            self.ln()

    def level_badge(self, level_num, color, name, y_offset=0):
        """Draw a colored level badge."""
        x = self.get_x()
        y = self.get_y() + y_offset
        self.set_fill_color(*color)
        self.set_draw_color(*color)
        badge_w = 8
        badge_h = 6
        self.rect(x, y, badge_w, badge_h, "F")
        self.set_xy(x, y)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*WHITE)
        self.cell(badge_w, badge_h, str(level_num), align="C")
        self.set_xy(x + badge_w + 2, y)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*DARK)
        self.cell(0, badge_h, sanitize_text(name))
        self.set_xy(x, y + badge_h + 2)

    def callout_box(self, title, text, height=None):
        pad = 5
        box_w = self.w - self.l_margin - self.r_margin
        inner_w = box_w - pad * 2
        # Measure title height
        self.set_font("Helvetica", "B", 11)
        title_h = 7
        # Measure body height
        self.set_font("Helvetica", "", 10)
        body_h = self.multi_cell(inner_w, 6, sanitize_text(text), dry_run=True, output="HEIGHT")
        total_h = height or (pad + title_h + 2 + body_h + pad)
        # Draw box
        self.set_fill_color(*GRAY_BG)
        self.set_draw_color(*ACCENT)
        box_y = self.get_y()
        self.rect(self.l_margin, box_y, box_w, total_h, "FD")
        # Title
        self.set_xy(self.l_margin + pad, box_y + pad)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*NAVY)
        self.cell(0, title_h, sanitize_text(title))
        # Body
        self.set_xy(self.l_margin + pad, box_y + pad + title_h + 2)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        self.multi_cell(inner_w, 6, sanitize_text(text))
        self.set_y(box_y + total_h + 4)


def build_pdf():
    pdf = ExecutivePDF()
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
    pdf.cell(0, 14, "Agent Accuracy Spectrum", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 14, "for Copilot Studio", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(180, 200, 220)
    pdf.cell(0, 9, "A five-level framework for measuring AI agent accuracy", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 12)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 8, "with a comparative look at pro-code agent architectures", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(95)
    pdf.set_draw_color(80, 140, 200)
    pdf.set_line_width(0.4)
    pdf.line(pdf.w * 0.3, pdf.get_y(), pdf.w * 0.7, pdf.get_y())
    pdf.set_line_width(0.2)

    pdf.set_y(103)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 7, "Summary", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "March 2026", align="C", new_x="LMARGIN", new_y="NEXT")

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
        "Not all AI use cases require the same level of accuracy, and not all agent "
        "architectures deliver it. This report presents a five-level framework based on "
        "313 empirical test runs across 19 agent configurations and two government use cases."
    ), align="C")

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 7, sanitize_text("313 test runs  |  19 agents  |  20 prompts  |  2 use cases  |  7 testing rounds"),
             align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 6, sanitize_text(
        "The agent accelerates the human; it does not replace them. "
        "Mandatory human review, citation linking, audit logging, and "
        "organizational culture that treats AI output as a draft -- never "
        "a decision. This is the only responsible operating model."
    ), align="C")

    # ====================================================================
    # TABLE OF CONTENTS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Contents")
    pdf.ln(4)

    toc_entries = [
        "The Five Levels",
        "The Danger Taxonomy",
        "The Evidence",
        "The Iterative Process",
        "What Government Cloud Customers Should Do",
        "Five Findings That Surprised Us",
        "Conclusion",
        "Appendix: Agent Configurations",
    ]
    # Create link targets for each TOC entry
    toc_links = {entry: pdf.add_link() for entry in toc_entries}
    for entry in toc_entries:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*ACCENT)
        pdf.cell(0, 9, sanitize_text(entry), new_x="LMARGIN", new_y="NEXT",
                 link=toc_links[entry])
        pdf.set_draw_color(*DIVIDER)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(1)

    # ====================================================================
    # THE FIVE LEVELS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("The Five Levels", link=toc_links["The Five Levels"])

    pdf.body_text(
        "Government agencies deploy AI agents across a spectrum of use cases. "
        "Each level has different accuracy requirements, different failure consequences, "
        "and different engineering investments. This framework helps leaders match their "
        "investment to their risk."
    )

    # Level overview table
    lvl_headers = ["Level", "Name", "Stakes", "Example"]
    lvl_widths = [14, 34, 48, 74]
    lvl_rows = [
        ["1", "Discovery", "Minor inconvenience", "Find our leave policy"],
        ["2", "Summarization", "Wasted time", "Summarize this audit report"],
        ["3", "Operational", "Misallocated resources", "How many open cases by type?"],
        ["4", "Investigative", "Missed evidence", "Build a timeline from these records"],
        ["5", "Adjudicative", "Wrong legal outcome", "Prepare facts for this hearing"],
    ]
    pdf.styled_table(lvl_headers, lvl_rows, lvl_widths, font_size=8,
                      col_aligns=["C", "L", "L", "L"])

    # ── Level 1-2 ──
    pdf.ln(6)
    pdf.level_badge(1, LVL1_COLOR, "Discovery")
    pdf.level_badge(2, LVL2_COLOR, "Summarization and Synthesis")
    pdf.ln(2)
    pdf.body_text(
        "The simplest AI use cases: finding documents, summarizing reports, condensing "
        "meeting transcripts. Wrong answers are inconvenient but not dangerous. Users can "
        "easily verify results against the original source."
    )
    pdf.body_text(
        "Document-based agents (Copilot Studio with SharePoint grounding) scored 8 out of "
        "10 on both use cases with zero customization. GPT-4o and GPT-4.1 performed "
        "identically at this level. Model choice does not matter here.",
        bold_lead="What we found:"
    )
    pdf.body_text(
        "Deploy Copilot with SharePoint. Invest in document hygiene (consistent "
        "formatting, meaningful filenames, metadata tags) rather than custom engineering. "
        "This is where most agencies should start.",
        bold_lead="Recommendation:"
    )

    # ── Level 3 ──
    pdf.ln(2)
    pdf.level_badge(3, LVL3_COLOR, "Operational Decision Support")
    pdf.ln(2)
    pdf.body_text(
        "Multi-source data aggregation, dashboards-via-conversation, workload triage. "
        "Wrong answers misallocate resources but are verifiable against existing reports."
    )
    pdf.body_text(
        "Aggregate queries (portfolio summaries, citywide statistics, workload counts) "
        "worked reliably across all agent types, including the weakest performers. This is "
        "where agents with structured data access begin to outperform document agents, "
        "including both Copilot Studio MCP agents and pro-code agents. Live structured "
        "data delivers answers that static documents cannot.",
        bold_lead="What we found:"
    )
    pdf.body_text(
        "Connect agents to structured data sources via Model Context Protocol. "
        "Write clear tool descriptions. Add summary modes for large result sets.",
        bold_lead="Recommendation:"
    )

    # ── Level 4 ──
    pdf.add_page()
    pdf.level_badge(4, LVL4_COLOR, "Investigative and Analytical")
    pdf.ln(2)
    pdf.body_text(
        "Timeline reconstruction, discrepancy detection, entity resolution across multiple "
        "data sources. Wrong answers mean missed evidence, false leads, and misdirected "
        "investigations. This is where accuracy diverges dramatically."
    )

    pdf.subsection_title("The Model Gap")
    pdf.body_text(
        "Among agents with structured data access, GPT-4.1 agents averaged 9.5 out of 10. "
        "The GPT-4o agent scored 4 out of 10. Same tools, same data, same backend. "
        "Document agents showed no model gap (8 out of 10 on both GPT-4o and GPT-4.1). "
        "Government Cloud Copilot Studio is locked to GPT-4o. No amount of tool or prompt "
        "engineering closed this gap."
    )

    model_headers = ["Model", "Average Score", "Platform"]
    model_widths = [50, 40, 80]
    model_rows = [
        ["GPT-4.1", "9.5 / 10", "Commercial Copilot Studio, Pro-code agents"],
        ["GPT-5 Auto", "10 / 10", "Commercial Copilot Studio (identical to 4.1)"],
        ["GPT-4o", "4 / 10", "Government Cloud Copilot Studio"],
        ["Platform-assigned", "2 / 10", "M365 Copilot (no user control)"],
    ]
    pdf.styled_table(model_headers, model_rows, model_widths, font_size=7.5,
                      col_aligns=["L", "C", "L"])
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.cell(0, 4, "* Ranked by score", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.subsection_title("The Data Gap")
    pdf.body_text(
        "The agent correctly queried the database, found no results, and concluded no "
        "drug tests existed. The answer was wrong because the data was incomplete, not "
        "because the agent failed."
    )

    dg_headers = ["Issue", "In Source Documents", "In Database", "Agent Result"]
    dg_widths = [30, 42, 34, 64]
    dg_rows = [
        ["Fentanyl screens", "Yes (narrative text)", "Not extracted", "\"No drug tests exist\""],
        ["Skeletal survey", "Yes (medical records)", "Not extracted", "Could not answer prompt"],
    ]
    pdf.styled_table(dg_headers, dg_rows, dg_widths, font_size=7.5,
                      col_aligns=["L", "L", "L", "L"])

    pdf.ln(2)
    pdf.body_text(
        "Audit your data before auditing your agent. If critical facts live only in "
        "unstructured reports, they must be extracted and loaded before an agent can "
        "query them.",
        bold_lead="Recommendation:"
    )

    pdf.ln(1)
    pdf.subsection_title("The Tool Gap")
    pdf.body_text(
        "Users type '4763 Griscom Street.' The database stores '4763 GRISCOM ST.' Without "
        "a tool to bridge that gap, agents resolved the wrong property 87% of the time. "
        "Every downstream answer was confidently wrong. One address normalization tool "
        "fixed it in 30 minutes of engineering."
    )

    tg_headers = ["Metric", "Before Tool", "After Tool"]
    tg_widths = [70, 50, 50]
    tg_rows = [
        ["Address failure rate", "87%", "0%"],
        ["Copilot Studio MCP (Commercial)", "8 / 10", "10 / 10"],
        ["Copilot Studio MCP (Gov Cloud)", "2 / 10", "4 / 10"],
        ["Investigative Agent (OpenAI SDK)", "1 / 10", "10 / 10"],
        ["Foundry Agent (Agent Service)", "4 / 10", "9 / 10"],
        ["Triage Agent (Semantic Kernel)", "0 / 10", "10 / 10"],
    ]
    pdf.styled_table(tg_headers, tg_rows, tg_widths, font_size=7.5,
                      col_aligns=["L", "C", "C"])
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.cell(0, 4, "* Ranked by score", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.body_text(
        "Purpose-built tools for entity resolution. GPT-4.1 minimum. "
        "Explicit workflow guidance in system prompts. Ground truth test suites with "
        "known answers.",
        bold_lead="Recommendation:"
    )

    # ── Level 5 ──
    pdf.ln(2)
    pdf.level_badge(5, LVL5_COLOR, "Legal and Adjudicative")
    pdf.ln(2)
    pdf.body_text(
        "Case preparation, evidence compilation, hearing summaries, regulatory "
        "determinations. Wrong answers can produce incorrect legal outcomes, due process "
        "violations, or direct harm to vulnerable populations."
    )
    pdf.body_text(
        "Even our highest-scoring agents produced dangerous results. Each example below "
        "was documented during testing:",
        bold_lead="What we found:"
    )

    l5_headers = ["Failure Type", "What Happened", "Legal Risk"]
    l5_widths = [32, 78, 60]
    l5_rows = [
        ["Reproduced\nmisinformation",
         "Quoted 'no fractures detected' from sheriff\nreport; medical records showed bilateral\nlong bone fractures",
         "Wrong medical conclusion\nin child abuse investigation"],
        ["False negative",
         "Found two positive fentanyl screens,\nthen concluded no drug tests existed",
         "Missed evidence contradicting\nsworn testimony"],
        ["Misattribution",
         "Attributed mother's '8 PM bedtime'\nstatement to father (who consistently\nsaid 'around ten')",
         "Undermined witness\ncredibility at hearing"],
    ]

    line_h = 4
    pad = 2
    # Header
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(*TABLE_HEADER_BG)
    pdf.set_text_color(*TABLE_HEADER_FG)
    for i, h in enumerate(l5_headers):
        pdf.cell(l5_widths[i], 7, sanitize_text(h), border=0, align="C", fill=True)
    pdf.ln()
    # Rows
    pdf.set_font("Helvetica", "", 7.5)
    for r_idx, row in enumerate(l5_rows):
        bg = ROW_ALT if r_idx % 2 == 0 else ROW_WHT
        y_start = pdf.get_y()
        x_start = pdf.get_x()
        cell_heights = []
        for i, val in enumerate(row):
            pdf.set_font("Helvetica", "B" if i == 0 else "", 7.5)
            h = pdf.multi_cell(l5_widths[i], line_h, sanitize_text(val),
                               dry_run=True, output="HEIGHT")
            cell_heights.append(h)
        row_h = max(cell_heights) + pad * 2
        total_w = sum(l5_widths)
        pdf.set_fill_color(*bg)
        pdf.rect(x_start, y_start, total_w, row_h, "F")
        for i, val in enumerate(row):
            cell_x = x_start + sum(l5_widths[:i])
            cell_y = y_start + pad + (max(cell_heights) - cell_heights[i]) / 2
            pdf.set_xy(cell_x, cell_y)
            pdf.set_text_color(*DARK)
            pdf.set_font("Helvetica", "B" if i == 0 else "", 7.5)
            pdf.multi_cell(l5_widths[i], line_h, sanitize_text(val), border=0,
                           align="C" if i == 0 else "L")
        pdf.set_y(y_start + row_h)
    pdf.ln(2)
    pdf.body_text(
        "Mandatory human review by a qualified professional before any legal action. "
        "Citation linking so reviewers can verify every claim. Audit logging for "
        "accountability. Treat every agent output as a draft, never a decision.",
        bold_lead="Recommendation:"
    )

    pdf.ln(2)
    pdf.callout_box(
        "*  Reminder",
        "The agent accelerates the human; it does not replace them. Mandatory human "
        "review, citation linking, audit logging, and organizational culture that treats "
        "AI output as a draft -- never a decision. This is the only responsible operating model."
    )

    # ====================================================================
    # DANGER TAXONOMY
    # ====================================================================
    pdf.add_page()
    pdf.section_title("The Danger Taxonomy", link=toc_links["The Danger Taxonomy"])

    pdf.body_text(
        "Testing revealed five categories of AI failure, ranked by severity. These are "
        "not hypothetical -- each was documented across 305 test runs."
    )

    danger_headers = ["Severity", "Failure Mode", "Description", "Example from Testing"]
    danger_widths = [18, 32, 60, 60]
    danger_rows = [
        ["Critical", "False negative",
         "Data retrieved but not recognized\nas the answer",
         "Agent found two positive fentanyl\nscreens, then concluded no drug\ntest results existed"],
        ["Critical", "Faithfully reproduced\nmisinformation",
         "Agent accurately quoted a source\nwhose characterization was\nmisleading in isolation",
         "Sheriff report: 'no fractures\ndetected' -- medical records\nshowed bilateral fractures"],
        ["High", "Misattribution",
         "Correct fact assigned to the\nwrong person",
         "Mother's '8 PM bedtime' statement\nattributed to father, who\nconsistently said 'around ten'"],
        ["High", "Hallucinated fact\nwith confidence",
         "Invented specific detail with\nno source",
         "Agent reported ER arrival at\n'2:00 AM' -- actual time was\n3:15 AM (no source for 2:00)"],
        ["Medium", "Silent failure",
         "No results returned without\nindicating anything went wrong",
         "Web SPA hallucinated a case\nnumber; doc agent returned 1 of 9\nresults with no warning"],
    ]

    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(*TABLE_HEADER_BG)
    pdf.set_text_color(*TABLE_HEADER_FG)
    for i, h in enumerate(danger_headers):
        pdf.cell(danger_widths[i], 7, sanitize_text(h), border=0, align="C", fill=True)
    pdf.ln()

    line_h = 4
    pad = 2
    pdf.set_font("Helvetica", "", 7.5)
    for r_idx, row in enumerate(danger_rows):
        bg = ROW_ALT if r_idx % 2 == 0 else ROW_WHT
        y_start = pdf.get_y()
        x_start = pdf.get_x()
        # Measure tallest cell
        cell_heights = []
        for i, val in enumerate(row):
            pdf.set_font("Helvetica", "B" if i <= 1 else "", 7.5)
            h = pdf.multi_cell(danger_widths[i], line_h, sanitize_text(val),
                               dry_run=True, output="HEIGHT")
            cell_heights.append(h)
        row_h = max(cell_heights) + pad * 2
        # Draw full-width background
        total_w = sum(danger_widths)
        pdf.set_fill_color(*bg)
        pdf.rect(x_start, y_start, total_w, row_h, "F")
        # Render each cell vertically centered
        for i, val in enumerate(row):
            cell_x = x_start + sum(danger_widths[:i])
            cell_y = y_start + pad + (max(cell_heights) - cell_heights[i]) / 2
            pdf.set_xy(cell_x, cell_y)
            if i == 0:
                sev = val.strip()
                if sev == "Critical":
                    pdf.set_text_color(*RED)
                elif sev == "High":
                    pdf.set_text_color(200, 120, 20)
                else:
                    pdf.set_text_color(*AMBER)
                pdf.set_font("Helvetica", "B", 7.5)
            else:
                pdf.set_text_color(*DARK)
                pdf.set_font("Helvetica", "B" if i == 1 else "", 7.5)
            pdf.multi_cell(danger_widths[i], line_h, sanitize_text(val), border=0,
                           align="C" if i <= 1 else "L")
        pdf.set_y(y_start + row_h)
    pdf.ln(4)

    # ====================================================================
    # THE EVIDENCE
    # ====================================================================
    pdf.add_page()
    pdf.section_title("The Evidence", link=toc_links["The Evidence"])

    pdf.body_text(
        "This framework is grounded in 313 empirical test runs across two government "
        "use cases, 19 agent configurations, and six testing rounds."
    )

    ev_lw = 18  # fixed label column width for Data/Agents/Result alignment
    pdf.subsection_title("Use Case 1: Legal Case Analysis")
    pdf.bullet("50 synthetic legal cases with 277 people, 333 timeline events, "
               "338 statements, and 151 discrepancies",
               bold_lead="Data:", label_width=ev_lw)
    pdf.bullet("11 configurations across 3 structured database agents (including "
               "1 pro-code custom web app) and 8 document-based agents",
               bold_lead="Agents:", label_width=ev_lw)
    pdf.bullet("The pro-code web app scored a perfect 10 out of 10, using the same "
               "MCP tools as Copilot Studio (8 out of 10) but with full control over orchestration. "
               "Document agents scored 3 to 8 out of 10. 7 of 8 faithfully reproduced "
               "a misleading medical finding.",
               bold_lead="Result:", label_width=ev_lw)

    pdf.ln(2)
    pdf.subsection_title("Use Case 2: Investigative Analytics")
    pdf.bullet("34 million rows of real Philadelphia public records (584,000 properties, "
               "1.6 million code violations)",
               bold_lead="Data:", label_width=ev_lw)
    pdf.bullet("8 configurations including 3 pro-code agents with custom orchestration",
               bold_lead="Agents:", label_width=ev_lw)
    pdf.bullet("Two agents achieved perfect 10 out of 10 after iterative improvement. "
               "The GPT-4o agent plateaued at 4 out of 10 despite identical improvements.",
               bold_lead="Result:", label_width=ev_lw)

    # Cross-use-case results table
    pdf.ln(4)
    pdf.subsection_title("Cross-Use-Case Results")
    result_headers = ["Agent Configuration", "Use Case 1", "Use Case 2", "Model"]
    result_widths = [58, 24, 24, 64]
    result_rows = [
        ["Custom Web App (pro-code / MCP Chat)", "10/10", "--", "GPT-4.1"],
        ["Investigative Agent (pro-code / OpenAI SDK)", "--", "10/10", "GPT-4.1"],
        ["Copilot Studio MCP (Commercial)", "8/10", "10/10", "GPT-4.1 / GPT-5 Auto"],
        ["Foundry Agent (pro-code / Agent Service)", "--", "9/10", "GPT-4.1"],
        ["Triage Agent (pro-code / Semantic Kernel)", "--", "10/10", "GPT-4.1"],
        ["Copilot Studio MCP (Gov Cloud)", "9/10", "4/10", "GPT-4o"],
        ["SharePoint/PDF (Commercial)", "8/10", "8/10", "GPT-4.1 / GPT-5 Auto"],
        ["SharePoint/PDF (Gov Cloud)", "3-8/10", "8/10", "GPT-4o"],
        ["M365 Copilot MCP", "--", "2/10", "Platform-assigned"],
    ]
    pdf.styled_table(result_headers, result_rows, result_widths, font_size=7.5)
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.cell(0, 4, "* Ranked by score. M365 Copilot MCP uses a platform-assigned model with no user control.", new_x="LMARGIN", new_y="NEXT")

    # ====================================================================
    # ITERATIVE IMPROVEMENT
    # ====================================================================
    pdf.add_page()
    pdf.section_title("The Iterative Process", link=toc_links["The Iterative Process"])

    pdf.body_text(
        "Deploying an AI agent is not a one-time event. Each round of testing reveals "
        "a different category of failure requiring a different type of fix. Organizations "
        "that skip this process will encounter every failure mode documented here."
    )

    pdf.subsection_title("Round 0: Baseline Testing")
    pdf.body_text(
        "Deploy the agent, test against known prompts with known answers, document every "
        "failure. This project tested 11 + 8 agent configurations across 10 prompts each "
        "(190 baseline test runs). This step applies to both document and structured data "
        "agents -- without a baseline, you cannot measure improvement."
    )

    pdf.subsection_title("Improving Document Agents")
    pdf.body_text(
        "Document agents cannot be improved through tool engineering. Their accuracy "
        "depends on document quality and platform retrieval. Seven of eight missed the "
        "skeletal survey discrepancy because the platform retrieved only one of two "
        "conflicting documents."
    )
    pdf.body_text(
        "We added cross-reference headers listing related documents "
        "and their key findings. No content was altered. Zero code.",
        bold_lead="Round 1: Fix the documents."
    )

    doc_headers = ["Agent", "Before", "After", "Change"]
    doc_widths = [62, 28, 28, 52]
    doc_rows = [
        ["Commercial doc agent", "0 / 2", "2 / 2", "Retrieved 4 sources"],
        ["Gov Cloud doc agent", "Vague", "Detailed", "Multi-source analysis"],
    ]
    pdf.styled_table(doc_headers, doc_rows, doc_widths, font_size=7.5,
                      col_aligns=["L", "C", "C", "L"])

    pdf.ln(2)
    pdf.body_text(
        "Invest in document hygiene before custom engineering. Cross-reference "
        "headers, consistent formatting, meaningful filenames, and metadata tags. "
        "Zero-code improvements that compound across every document agent.",
        bold_lead="Recommendation:"
    )

    pdf.body_text(
        "Copilot Studio topics, SharePoint metadata tags, and Power Automate "
        "cloud flows for cross-validation. These are platform configuration, not "
        "custom code -- testing whether they can push document agents past 8 out "
        "of 10 on both Government Cloud and Commercial.",
        bold_lead="Round 2: Configure the agent (planned)."
    )

    pdf.ln(2)
    pdf.subsection_title("Improving Structured Data Agents")

    pdf.body_text(
        "Structured data agents improved dramatically through iterative engineering."
    )

    pdf.body_text(
        "Narrative facts (drug screens, skeletal survey) were not in the database. "
        "Fix: 11 new rows + 1 tool filter. Result: 2 Pass / 8 Fail became 12 Pass / 1 Fail.",
        bold_lead="Round 1: Fix the data."
    )

    pdf.body_text(
        "No tool to convert street addresses to database identifiers (87% failure rate). "
        "Fix: 1 address normalization tool + improved descriptions. Zero data changes.",
        bold_lead="Round 2: Fix the tools."
    )

    imp_headers = ["Agent", "Round 1", "Final", "Change"]
    imp_widths = [56, 28, 28, 58]
    imp_rows = [
        ["Copilot Studio MCP (Commercial)", "8/10", "10/10", "PERFECT"],
        ["Investigative Agent (pro-code / OpenAI SDK)", "1/10", "10/10", "PERFECT (+9)"],
        ["Foundry Agent (pro-code / Agent Service)", "4/10", "9/10", "+5, zero failures"],
        ["Triage Agent (pro-code / Semantic Kernel)", "0/10", "10/10", "+10 across 5 rounds"],
        ["Copilot Studio MCP (Gov Cloud)", "2/10", "4/10", "+2 (model-limited)"],
        ["M365 Copilot MCP", "--", "2/10", "Not tested in Round 1"],
    ]
    pdf.styled_table(imp_headers, imp_rows, imp_widths, font_size=8)

    pdf.ln(4)
    pdf.subsection_title("The Pattern for Organizations")
    pdf.bullet("Without ground truth, you cannot measure improvement. Build a test suite "
               "before you build the agent.",
               bold_lead="1. Test with known answers.")
    pdf.bullet("If the answer is not in the data, no model will find it. Make facts "
               "discrete and queryable.",
               bold_lead="2. Fix the data first.")
    pdf.bullet("If the model cannot reach the data, add tools. If it does not know "
               "which tool to use, improve descriptions.",
               bold_lead="3. Fix the tools second.")
    pdf.bullet("Each fix can introduce new failure modes. Run the full test suite after "
               "every change.",
               bold_lead="4. Retest after every change.")

    # ====================================================================
    # WHAT GCC CUSTOMERS SHOULD DO
    # ====================================================================
    pdf.add_page()
    pdf.section_title("What Government Cloud Customers Should Do", link=toc_links["What Government Cloud Customers Should Do"])

    pdf.subsection_title("The Model Gap")
    pdf.body_text(
        "Government Community Cloud is currently locked to GPT-4o for Copilot Studio. "
        "For agents with structured data access, this model scored 4 out of 10 on "
        "investigative queries where GPT-4.1 scored 9.5 out of 10. Document agents "
        "were unaffected (8 out of 10 on both models). No amount of tool or prompt "
        "engineering closed the structured data gap."
    )

    pdf.bullet("Improve document quality now. Cross-reference headers, consistent "
               "formatting, and metadata tags improved retrieval from 0/2 to 2/2 on the "
               "hardest prompts -- zero code, zero model dependency",
               bold_lead="Option 1:")
    pdf.bullet("Use Copilot Studio document agents for Levels 1 through 3 (GPT-4o is "
               "adequate for retrieval and summarization)",
               bold_lead="Option 2:")
    pdf.bullet("Deploy a Foundry Agent (zero to low code, portal or SDK) or a fully custom "
               "agent using Azure OpenAI GPT-4.1 directly for Level 4 and 5 workloads",
               bold_lead="Option 3:")
    pdf.bullet("Monitor Government Cloud model updates -- when GPT-4.1 becomes available, "
               "Copilot Studio agents will benefit immediately",
               bold_lead="Option 4:")

    pdf.ln(4)
    pdf.subsection_title("The Code Investment Spectrum")
    pdf.body_text(
        "The engineering investment changes what you can customize, not whether the agent "
        "works at Level 4 and above."
    )

    code_headers = ["Approach", "Code Required", "Best For"]
    code_widths = [56, 44, 70]
    code_rows = [
        ["M365 Copilot + MCP", "Zero (3 JSON manifests)", "Levels 1-2"],
        ["Copilot Studio + SharePoint", "Zero (platform configuration)", "Levels 1-3"],
        ["Copilot Studio + MCP", "Zero (platform configuration)", "Levels 1-4 (Com), 1-3 (GCC)"],
        ["Foundry Agent", "Zero to low (portal or SDK)", "Levels 3-4"],
        ["OpenAI SDK / Semantic Kernel", "Full (TypeScript, C#)", "Levels 4-5"],
    ]
    pdf.styled_table(code_headers, code_rows, code_widths, font_size=8)

    pdf.ln(2)
    pdf.body_text(
        "Every architecture scored 9 to 10 out of 10 with GPT-4.1. The investment buys "
        "customization, governance controls, and audit capabilities -- all of which matter "
        "most at Levels 4 and 5."
    )

    pdf.ln(2)
    pdf.subsection_title("Why Copilot Studio")
    pdf.body_text(
        "Copilot Studio is the platform that ties the spectrum together. It hosts both "
        "zero-code SharePoint agents (Levels 1-2) and MCP-connected structured data agents "
        "(Levels 3-4) under a single governance boundary. Model flexibility is the headline: "
        "the same Copilot Studio agent configuration scored 4 out of 10 with GPT-4o and "
        "10 out of 10 with GPT-4.1 with no configuration changes required. **When Government "
        "Cloud gains access to more capable models, every Copilot Studio agent improves "
        "overnight.** Enterprise governance (data loss prevention, audit logging, admin "
        "pre-approval for tool calls) and M365 distribution (agents appear in Teams and "
        "Copilot chat) are built into the platform, not bolted on after the fact."
    )

    # ====================================================================
    # FIVE SURPRISING FINDINGS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Five Findings That Surprised Us", link=toc_links["Five Findings That Surprised Us"])

    pdf.subsection_title("1. The most dangerous agent was the most accurate quoting its source")
    pdf.body_text(
        "Seven of eight document agents faithfully reproduced a sheriff's report statement "
        "about fracture findings while the medical records told a different story. The agents "
        "were not wrong about what the document said. They were wrong about what was true."
    )

    pdf.subsection_title("2. A single missing tool caused an 87% failure rate -- and 30 minutes of engineering fixed it")
    pdf.body_text(
        "No tool existed to convert a street address into a database identifier. Adding one "
        "address lookup tool produced zero failures in retesting. One agent went from "
        "1 out of 10 to a perfect 10 out of 10. The cost of not having the tool was enormous; "
        "the cost of building it was trivial."
    )

    pdf.subsection_title("3. The most complex agent needed five rounds to reach perfection")
    pdf.body_text(
        "The Semantic Kernel team-of-agents pattern started at 0 out of 10 and reached "
        "a perfect 10 out of 10, but only after five rounds of sub-agent prompt engineering. "
        "A simpler Copilot Studio agent scored 8 out of 10 with no customization at all."
    )

    pdf.subsection_title("4. The model retrieved the answer and did not recognize it")
    pdf.body_text(
        "The agent called the right tools, received data containing 'two positive drug "
        "screens (fentanyl) in October,' and concluded: 'no drug test results exist.' "
        "This false negative is invisible to users because the tool calls look correct."
    )

    pdf.subsection_title("5. An advanced agent challenged its own premise -- and was right")
    pdf.body_text(
        "The Foundry Agent was asked about a purchase price versus assessment ratio. "
        "Instead of calculating the answer, it checked the source data, found the premise "
        "was wrong, and recalculated using verified numbers. No other agent questioned "
        "the input."
    )

    # ====================================================================
    # CONCLUSION
    # ====================================================================
    pdf.ln(4)
    pdf.section_title("Conclusion", link=toc_links["Conclusion"])

    pdf.body_text(
        "Not all AI use cases require the same investment. Levels 1 and 2 work with "
        "existing Copilot licenses and SharePoint document libraries. Level 3 benefits "
        "from structured data connections via Model Context Protocol. Levels 4 and 5 "
        "require purpose-built tools, capable models (GPT-4.1 minimum), iterative "
        "testing, and human review workflows."
    )

    pdf.callout_box(
        "The Bottom Line",
        "The agent is a research assistant, never the decision-maker. At Level 5, "
        "where legal outcomes depend on accuracy, trust but verify is not a suggestion "
        "-- it is the only responsible operating model."
    )

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 5, sanitize_text(
        "Based on 313 test runs across 2 government use cases, 19 agent configurations, "
        "7 testing rounds, and 4 rounds of iterative improvement."
    ), align="C")

    # ====================================================================
    # APPENDIX: AGENT CONFIGURATIONS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Appendix: Agent Configurations", link=toc_links["Appendix: Agent Configurations"])

    pdf.body_text(
        "All 19 agent configurations tested across both use cases. Use Case 1 tested "
        "legal case analysis (synthetic data, 50 cases). Use Case 2 tested investigative "
        "analytics (real Philadelphia public records, 34 million rows)."
    )

    pdf.subsection_title("Use Case 1: Legal Case Analysis (11 Agents)")

    uc1_headers = ["Agent", "Data Source", "Model", "Score"]
    uc1_widths = [62, 42, 28, 38]
    uc1_rows = [
        ["Custom Web App (pro-code)", "MCP / SQL", "GPT-4.1", "10/10"],
        ["Copilot Studio MCP (GCC)", "MCP / SQL", "GPT-4o", "9/10"],
        ["Copilot Studio MCP (Com)", "MCP / SQL", "GPT-4.1", "8/10"],
        ["Copilot Studio SP/PDF (Com)", "SharePoint PDFs", "GPT-4.1", "8/10"],
        ["Copilot Studio SP/DOCX (Com)", "SharePoint DOCXs", "GPT-4.1", "7/10"],
        ["Copilot Studio KB/DOCX (Com)", "Uploaded DOCXs", "GPT-4.1", "6/10"],
        ["Copilot Studio KB/PDF (Com)", "Uploaded PDFs", "GPT-4.1", "5/10"],
        ["Copilot Studio SP/DOCX (GCC)", "SharePoint DOCXs", "GPT-4o", "5/10"],
        ["Copilot Studio KB/PDF (GCC)", "Uploaded PDFs", "GPT-4o", "5/10"],
        ["Copilot Studio KB/DOCX (GCC)", "Uploaded DOCXs", "GPT-4o", "4/10"],
        ["Copilot Studio SP/PDF (GCC)", "SharePoint PDFs", "GPT-4o", "3/10"],
    ]
    pdf.styled_table(uc1_headers, uc1_rows, uc1_widths, font_size=7)
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 4, sanitize_text(
        "* Ranked by score. Document agent scores (rows 5-11) are approximate totals "
        "across 10 prompts. PDF consistently outperformed DOCX; Commercial consistently "
        "outperformed Government Cloud."
    ))

    pdf.ln(6)
    pdf.subsection_title("Use Case 2: Investigative Analytics (8 Agents)")

    uc2_headers = ["Agent", "Platform", "Model", "Score"]
    uc2_widths = [62, 42, 28, 38]
    uc2_rows = [
        ["Copilot Studio MCP (Com)", "Copilot Studio", "GPT-4.1", "10/10"],
        ["Investigative Agent", "OpenAI SDK", "GPT-4.1", "10/10"],
        ["Triage Agent", "Semantic Kernel", "GPT-4.1", "10/10"],
        ["Foundry Agent", "AI Agent Service", "GPT-4.1", "9/10"],
        ["Copilot Studio SP/PDF (GCC)", "Copilot Studio", "GPT-4o", "8/10"],
        ["Copilot Studio SP/PDF (Com)", "Copilot Studio", "GPT-4.1", "8/10"],
        ["Copilot Studio MCP (GCC)", "Copilot Studio", "GPT-4o", "4/10"],
        ["M365 Copilot MCP", "M365 Platform", "Platform-assigned", "2/10"],
    ]
    pdf.styled_table(uc2_headers, uc2_rows, uc2_widths, font_size=7)
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 4, sanitize_text(
        "* Ranked by score. Custom Web App is pro-code, tested on Use Case 1 only. "
        "Investigative, Foundry, and Triage are pro-code, tested on Use Case 2 only. "
        "M365 Copilot MCP uses a platform-assigned model with no user control."
    ))

    pdf.ln(6)
    pdf.subsection_title("Key: Platform Descriptions")
    pdf.bullet("Copilot Studio: Low-code agent builder with SharePoint grounding or MCP "
               "tool connections. Hosted in Power Platform.",
               bold_lead="Copilot Studio:")
    pdf.bullet("M365 Copilot: Zero-code agent deployed via 3 JSON manifest files. "
               "Appears in Teams, Outlook, and Edge. Platform assigns the model.",
               bold_lead="M365 Copilot:")
    pdf.bullet("Azure AI Foundry managed agent with "
               "MCPTool for automatic tool discovery. Stateful threads.",
               bold_lead="Foundry Agent:")
    pdf.bullet("OpenAI SDK: Custom TypeScript agent using Azure OpenAI "
               "chat completions with tool calling. Full developer control.",
               bold_lead="Investigative Agent:")
    pdf.bullet("Semantic Kernel: C# team-of-agents pattern with a triage agent "
               "dispatching to specialized sub-agents (ownership, violations, transfers).",
               bold_lead="Triage Agent:")

    # ====================================================================
    # OUTPUT
    # ====================================================================
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "pdf")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "summary.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    build_pdf()
