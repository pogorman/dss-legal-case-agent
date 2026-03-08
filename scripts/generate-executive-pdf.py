"""
Generate an executive-summary PDF using the five-level accuracy framework.
Uses fpdf2 -- no external dependencies beyond what's already installed.

Usage: python scripts/generate-executive-pdf.py
Output: docs/executive-summary.pdf
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
        self.cell(0, 6, sanitize_text("AI Agent Accuracy Spectrum  |  Executive Summary"), align="L")
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
        self.cell(0, 4, sanitize_text("Confidential  |  March 2026  |  304 test runs across 19 agent configurations"), align="C")

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

    def callout_box(self, title, text, height=32):
        self.set_fill_color(*GRAY_BG)
        self.set_draw_color(*ACCENT)
        box_y = self.get_y()
        self.rect(self.l_margin, box_y, self.w - self.l_margin - self.r_margin, height, "FD")
        self.set_xy(self.l_margin + 6, box_y + 5)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*NAVY)
        self.cell(0, 7, sanitize_text(title))
        self.set_xy(self.l_margin + 6, box_y + 14)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 12, 6, sanitize_text(text))
        self.set_y(box_y + height + 4)


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
    pdf.cell(0, 14, "AI Agent Accuracy Spectrum", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(180, 200, 220)
    pdf.cell(0, 10, "A Five-Level Framework for Government", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(65)
    pdf.set_draw_color(80, 140, 200)
    pdf.set_line_width(0.4)
    pdf.line(pdf.w * 0.3, pdf.get_y(), pdf.w * 0.7, pdf.get_y())
    pdf.set_line_width(0.2)

    pdf.set_y(75)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 7, "Executive Summary", align="C", new_x="LMARGIN", new_y="NEXT")
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
        "304 empirical test runs across 19 agent configurations and two government use cases."
    ), align="C")

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 7, sanitize_text("304 test runs  |  19 agents  |  20 prompts  |  2 use cases  |  6 testing rounds"),
             align="C", new_x="LMARGIN", new_y="NEXT")

    # ====================================================================
    # THE FIVE LEVELS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("The Five Levels")

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
    pdf.styled_table(lvl_headers, lvl_rows, lvl_widths, font_size=8)

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
        "where Model Context Protocol agents begin to outperform document agents -- live "
        "structured data delivers answers that static documents cannot.",
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
        "GPT-4.1 agents averaged 9.5 out of 10. The GPT-4o agent scored 4 out of 10. "
        "Same tools, same data, same backend. Government Cloud Copilot Studio is locked "
        "to GPT-4o. No amount of tool or prompt engineering closed this gap."
    )

    model_headers = ["Model", "Average Score", "Platform"]
    model_widths = [50, 40, 80]
    model_rows = [
        ["GPT-4.1", "9.5 / 10", "Commercial Copilot Studio, Azure OpenAI"],
        ["GPT-5 Auto", "10 / 10", "Commercial Copilot Studio (identical to 4.1)"],
        ["GPT-4o", "4 / 10", "Government Cloud Copilot Studio"],
        ["Platform-assigned", "2 / 10", "M365 Copilot (no user control)"],
    ]
    pdf.styled_table(model_headers, model_rows, model_widths, font_size=7.5)

    pdf.ln(4)
    pdf.subsection_title("The Tool Gap")
    pdf.body_text(
        "Address resolution (converting '4763 Griscom Street' to a database identifier) "
        "failed 87 percent of the time before we added a dedicated fuzzy-search tool. "
        "After adding that one tool, address failures dropped to zero. The Investigative "
        "Agent went from 1 out of 10 to a perfect 10 out of 10."
    )
    pdf.body_text(
        "Purpose-built tools with fuzzy matching and entity resolution. GPT-4.1 minimum. "
        "Explicit workflow guidance in system prompts. Ground truth test suites with known "
        "answers. Budget for iterative testing.",
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
        "Even our highest-scoring agent (10 out of 10 on factual accuracy) produced a "
        "dangerous result: it faithfully reproduced a sheriff's report statement that "
        "'no fractures detected on skeletal survey' while the medical records documented "
        "bilateral long bone fractures in a child abuse investigation. The citation was "
        "real. The confidence was justified. The conclusion was dangerous.",
        bold_lead="What we found:"
    )

    # ====================================================================
    # DANGER TAXONOMY
    # ====================================================================
    pdf.add_page()
    pdf.section_title("The Danger Taxonomy")

    pdf.body_text(
        "Testing revealed five categories of AI failure, ranked by severity. These are "
        "not hypothetical -- each was documented across 304 test runs."
    )

    danger_headers = ["Severity", "Failure Mode", "Description"]
    danger_widths = [22, 48, 100]
    danger_rows = [
        ["Critical", "False negative",
         "Data retrieved but not recognized as the answer"],
        ["Critical", "Faithfully reproduced\nmisinformation",
         "Agent accurately quoted a source document\nthat itself contained an error"],
        ["High", "Misattribution",
         "Correct fact assigned to the wrong person\n(e.g., mother's statement attributed to father)"],
        ["High", "Hallucinated fact\nwith confidence",
         "Invented specific detail with no source\n(dates, case numbers, statistics)"],
        ["Medium", "Silent failure",
         "No results returned without indicating\nanything went wrong"],
    ]

    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(*TABLE_HEADER_BG)
    pdf.set_text_color(*TABLE_HEADER_FG)
    for i, h in enumerate(danger_headers):
        pdf.cell(danger_widths[i], 7, sanitize_text(h), border=0, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 7.5)
    for r_idx, row in enumerate(danger_rows):
        bg = ROW_ALT if r_idx % 2 == 0 else ROW_WHT
        pdf.set_fill_color(*bg)
        y_start = pdf.get_y()
        x_start = pdf.get_x()
        row_h = 12
        for i, val in enumerate(row):
            pdf.set_xy(x_start + sum(danger_widths[:i]), y_start)
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
            pdf.multi_cell(danger_widths[i], 4, sanitize_text(val), border=0,
                           align="C" if i == 0 else "L", fill=True)
        pdf.set_y(y_start + row_h)
    pdf.ln(4)

    pdf.callout_box(
        "Level 5: Trust But Verify",
        "The agent accelerates the human; it does not replace them. "
        "Mandatory human review, citation linking, audit logging, and "
        "organizational culture that treats AI output as a draft -- never "
        "a decision. This is the only responsible operating model.",
        height=30
    )

    # ====================================================================
    # THE EVIDENCE
    # ====================================================================
    pdf.add_page()
    pdf.section_title("The Evidence")

    pdf.body_text(
        "This framework is grounded in 304 empirical test runs across two government "
        "use cases, 19 agent configurations, and six testing rounds."
    )

    pdf.subsection_title("Use Case 1: Legal Case Analysis")
    pdf.bullet("50 synthetic legal cases with 277 people, 333 timeline events, "
               "338 statements, and 151 discrepancies",
               bold_lead="Data:")
    pdf.bullet("11 configurations across 3 structured database agents and 8 "
               "document-based agents",
               bold_lead="Agents:")
    pdf.bullet("Custom web application scored a perfect 10 out of 10. Document agents "
               "scored 3 to 8 out of 10. 7 of 8 faithfully reproduced a misleading "
               "medical finding.",
               bold_lead="Result:")

    pdf.ln(2)
    pdf.subsection_title("Use Case 2: Investigative Analytics")
    pdf.bullet("34 million rows of real Philadelphia public records (584,000 properties, "
               "1.6 million code violations)",
               bold_lead="Data:")
    pdf.bullet("8 configurations including 3 pro-code agents with custom orchestration",
               bold_lead="Agents:")
    pdf.bullet("Two agents achieved perfect 10 out of 10 after iterative improvement. "
               "The GPT-4o agent plateaued at 4 out of 10 despite identical improvements.",
               bold_lead="Result:")

    # Cross-use-case results table
    pdf.ln(4)
    pdf.subsection_title("Cross-Use-Case Results")
    result_headers = ["Agent Configuration", "Use Case 1", "Use Case 2", "Model"]
    result_widths = [58, 24, 24, 64]
    result_rows = [
        ["Custom Web Application", "10/10", "--", "GPT-4.1"],
        ["Investigative Agent", "--", "10/10", "GPT-4.1"],
        ["Copilot Studio MCP (Commercial)", "8/10", "10/10", "GPT-4.1"],
        ["Foundry Agent", "--", "9/10", "GPT-4.1"],
        ["Triage Agent", "--", "9/10", "GPT-4.1"],
        ["Copilot Studio MCP (Gov Cloud)", "9/10", "4/10", "GPT-4o"],
        ["SharePoint/PDF (Commercial)", "8/10", "8/10", "GPT-4.1"],
        ["SharePoint/PDF (Gov Cloud)", "3-8/10", "8/10", "GPT-4o"],
        ["M365 Copilot", "--", "2/10", "Platform-assigned"],
    ]
    pdf.styled_table(result_headers, result_rows, result_widths, font_size=7.5)

    # ====================================================================
    # ITERATIVE IMPROVEMENT
    # ====================================================================
    pdf.add_page()
    pdf.section_title("The Iterative Process")

    pdf.body_text(
        "Deploying an AI agent is not a one-time event. Each round of testing reveals "
        "a different category of failure requiring a different type of fix. Organizations "
        "that skip this process will encounter every failure mode documented here."
    )

    pdf.subsection_title("Round 0: Baseline Testing")
    pdf.body_text(
        "Deploy the agent, test against known prompts with known answers, document every "
        "failure. This project tested 11 + 7 agent configurations across 10 prompts each "
        "(180 baseline test runs)."
    )

    pdf.subsection_title("Round 1: Fix the Data")
    pdf.body_text(
        "Drug test results buried in narrative text were invisible to the model. A skeletal "
        "survey finding missing from the database meant agents could not answer the most "
        "dangerous prompt. Fix: 11 new SQL rows and 1 tool filter. Result: 2 Pass / 8 Fail "
        "became 12 Pass / 1 Fail across affected prompts."
    )

    pdf.subsection_title("Round 2: Fix the Tools")
    pdf.body_text(
        "No tool existed to convert a street address into a database identifier (87% failure "
        "rate). Tool descriptions did not mention they contained medical staff data. Fix: "
        "1 new fuzzy address tool, improved descriptions, system prompt guidance. Zero data "
        "changes."
    )

    imp_headers = ["Agent", "Round 1", "Final", "Change"]
    imp_widths = [56, 28, 28, 58]
    imp_rows = [
        ["Commercial MCP", "8/10", "10/10", "PERFECT"],
        ["Investigative Agent", "1/10", "10/10", "PERFECT (+9)"],
        ["Foundry Agent", "4/10", "9/10", "+5, zero failures"],
        ["Triage Agent (SK)", "0/10", "9/10", "+9 across 4 rounds"],
        ["Gov Cloud MCP", "2/10", "4/10", "+2 (model-limited)"],
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
    pdf.section_title("What Government Cloud Customers Should Do")

    pdf.subsection_title("The Model Gap")
    pdf.body_text(
        "Government Community Cloud is currently locked to GPT-4o for Copilot Studio. "
        "This model scored 4 out of 10 on investigative queries where GPT-4.1 scored "
        "9.5 out of 10. No amount of tool or prompt engineering closed this gap."
    )

    pdf.bullet("Use Copilot Studio document agents for Levels 1 through 3 (GPT-4o is "
               "adequate for retrieval and summarization)",
               bold_lead="Option 1:")
    pdf.bullet("Deploy pro-code agents using Azure OpenAI GPT-4.1 directly for Level 4 "
               "and 5 workloads",
               bold_lead="Option 2:")
    pdf.bullet("Monitor Government Cloud model updates -- when GPT-4.1 becomes available, "
               "Copilot Studio agents will benefit immediately",
               bold_lead="Option 3:")

    pdf.ln(4)
    pdf.subsection_title("The Code Investment Spectrum")
    pdf.body_text(
        "The engineering investment changes what you can customize, not whether the agent "
        "works at Level 4 and above."
    )

    code_headers = ["Approach", "Code Required", "Best For"]
    code_widths = [56, 44, 70]
    code_rows = [
        ["M365 Copilot", "Zero (3 JSON manifests)", "Levels 1-2"],
        ["Copilot Studio", "Zero to low", "Levels 1-3 (Com), 1-2 (GCC)"],
        ["AI Foundry Agent", "Minimal", "Levels 3-4"],
        ["Custom SDK", "Full (TypeScript, C#)", "Levels 4-5"],
    ]
    pdf.styled_table(code_headers, code_rows, code_widths, font_size=8)

    pdf.ln(4)
    pdf.body_text(
        "Every architecture scored 9 to 10 out of 10 with GPT-4.1. The investment buys "
        "customization, governance controls, and audit capabilities -- all of which matter "
        "most at Levels 4 and 5."
    )

    pdf.ln(4)
    pdf.subsection_title("Why Copilot Studio")
    pdf.body_text(
        "Copilot Studio is the platform that ties the spectrum together. It hosts both "
        "zero-code SharePoint agents (Levels 1-2) and MCP-connected structured data agents "
        "(Levels 3-4) under a single governance boundary. Model flexibility is the headline: "
        "the same Copilot Studio agent configuration scored 4 out of 10 with GPT-4o and "
        "10 out of 10 with GPT-4.1 -- no configuration changes required. When Government "
        "Cloud gains access to more capable models, every Copilot Studio agent improves "
        "overnight. Enterprise governance (data loss prevention, audit logging, admin "
        "pre-approval for tool calls) and M365 distribution (agents appear in Teams and "
        "Copilot chat) are built into the platform, not bolted on after the fact."
    )

    # ====================================================================
    # FIVE SURPRISING FINDINGS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Five Findings That Surprised Us")

    pdf.subsection_title("1. The most dangerous agent was the most accurate quoting its source")
    pdf.body_text(
        "Seven of eight document agents faithfully reproduced a sheriff's report statement "
        "about fracture findings while the medical records told a different story. The agents "
        "were not wrong about what the document said. They were wrong about what was true."
    )

    pdf.subsection_title("2. A single missing tool caused an 87% failure rate -- and one day of engineering fixed it")
    pdf.body_text(
        "No tool existed to convert a street address into a database identifier. Adding one "
        "fuzzy-match lookup tool produced zero failures in retesting. One agent went from "
        "1 out of 10 to a perfect 10 out of 10. The cost of not having the tool was enormous; "
        "the cost of building it was trivial."
    )

    pdf.subsection_title("3. The most complex agent needed four rounds of iteration")
    pdf.body_text(
        "The Semantic Kernel team-of-agents pattern started at 0 out of 10 and reached "
        "9 out of 10, but only after four rounds of sub-agent prompt engineering. A simpler "
        "Copilot Studio agent scored 8 out of 10 with no customization at all."
    )

    pdf.subsection_title("4. The model retrieved the answer and did not recognize it")
    pdf.body_text(
        "The agent called the right tools, received data containing 'two positive drug "
        "screens (fentanyl) in October,' and concluded: 'no drug test results exist.' "
        "This false negative is invisible to users because the tool calls look correct."
    )

    pdf.subsection_title("5. A pro-code agent challenged its own premise -- and was right")
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
    pdf.section_title("Conclusion")

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
        "-- it is the only responsible operating model.",
        height=28
    )

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 5, sanitize_text(
        "Based on 304 test runs across 2 government use cases, 19 agent configurations, "
        "6 testing rounds, and 3 rounds of iterative improvement."
    ), align="C")

    # ====================================================================
    # OUTPUT
    # ====================================================================
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    out_path = os.path.join(out_dir, "executive-summary.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    build_pdf()
