"""
Generate an elegant executive-summary PDF from the testing results.
Uses fpdf2 — no external dependencies beyond what's already installed.

Usage: python scripts/generate-executive-pdf.py
Output: docs/executive-summary.pdf
"""

from fpdf import FPDF
import os

# ── Color palette ──────────────────────────────────────────────────
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


class ExecutivePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return  # cover page — no header
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT)
        self.cell(0, 6, "DSS Office of Legal Services  |  Copilot Studio Evaluation", align="L")
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
        self.cell(0, 4, "Confidential  |  March 2026  |  Testing conducted March 5-6, 2026", align="C")

    # ── Helpers ─────────────────────────────────────────────────────
    def section_title(self, text):
        self.ln(4)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*NAVY)
        self.cell(0, 9, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.l_margin + 50, self.get_y())
        self.set_line_width(0.2)
        self.ln(5)

    def subsection_title(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*ACCENT)
        self.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text, bold_lead=None):
        if bold_lead:
            self.set_font("Helvetica", "B", 9.5)
            self.set_text_color(*DARK)
            self.write(5.5, bold_lead + " ")
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text, bold_lead=None, indent=8):
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*MED)
        self.write(5.5, "- ")
        if bold_lead:
            self.set_font("Helvetica", "B", 9.5)
            self.set_text_color(*DARK)
            self.write(5.5, bold_lead + "  ")
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*DARK)
        self.multi_cell(self.w - self.r_margin - self.get_x(), 5.5, text)
        self.ln(1)

    def grade_color(self, grade):
        g = grade.strip().upper()
        if g.startswith("PASS") or g.startswith("P ") or g == "P":
            return GREEN
        elif g.startswith("PARTIAL") or g.startswith("PA") or g == "PA":
            return AMBER
        elif g.startswith("FAIL") or g.startswith("F ") or g == "F":
            return RED
        elif g.startswith("N/A"):
            return LIGHT
        return DARK

    def styled_table(self, headers, rows, col_widths, row_height=6, font_size=7.5):
        """Draw a professional table with header row and alternating stripes."""
        # Header
        self.set_font("Helvetica", "B", font_size)
        self.set_fill_color(*TABLE_HEADER_BG)
        self.set_text_color(*TABLE_HEADER_FG)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], row_height + 1, h, border=0, align="C", fill=True)
        self.ln()

        # Rows
        self.set_font("Helvetica", "", font_size)
        for r_idx, row in enumerate(rows):
            bg = ROW_ALT if r_idx % 2 == 0 else ROW_WHT
            self.set_fill_color(*bg)
            max_h = row_height
            for i, val in enumerate(row):
                self.set_text_color(*DARK)
                self.cell(col_widths[i], max_h, val, border=0, align="C" if i > 0 else "L", fill=True)
            self.ln()

    def colored_score_table(self, headers, rows, col_widths, row_height=5.5, font_size=7):
        """Table where cells are color-coded by Pass/Partial/Fail."""
        # Header
        self.set_font("Helvetica", "B", font_size)
        self.set_fill_color(*TABLE_HEADER_BG)
        self.set_text_color(*TABLE_HEADER_FG)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], row_height + 2, h, border=0, align="C", fill=True)
        self.ln()

        # Rows
        for r_idx, row in enumerate(rows):
            bg = ROW_ALT if r_idx % 2 == 0 else ROW_WHT
            self.set_fill_color(*bg)
            for i, val in enumerate(row):
                if i <= 1:
                    self.set_text_color(*DARK)
                    self.set_font("Helvetica", "B" if i == 0 else "", font_size)
                else:
                    color = self.grade_color(val)
                    self.set_text_color(*color)
                    self.set_font("Helvetica", "B", font_size)
                align = "L" if i == 0 else "C"
                self.cell(col_widths[i], row_height, val, border=0, align=align, fill=True)
            self.ln()


def build_pdf():
    pdf = ExecutivePDF()
    pdf.set_margins(20, 20, 20)

    # ══════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════════
    pdf.add_page()

    # Background band
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 120, "F")

    # Title
    pdf.set_y(35)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 14, "Copilot Studio Evaluation", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(180, 200, 220)
    pdf.cell(0, 10, "Structured Data vs. Document-Backed Agents", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Across Government Use Cases", align="C", new_x="LMARGIN", new_y="NEXT")

    # Divider line
    pdf.set_y(82)
    pdf.set_draw_color(80, 140, 200)
    pdf.set_line_width(0.4)
    pdf.line(pdf.w * 0.3, pdf.get_y(), pdf.w * 0.7, pdf.get_y())
    pdf.set_line_width(0.2)

    pdf.set_y(90)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 7, "DSS Office of Legal Services", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "March 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    # Below the band
    pdf.set_y(140)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MED)
    pdf.multi_cell(0, 6.5,
        "This report presents findings from a structured evaluation of Copilot Studio agents "
        "across multiple government use cases. Each use case tests the same core question: do agents "
        "backed by structured databases or unstructured documents deliver more reliable answers? "
        "Use Case 1 (Legal Case Analysis) is complete. Use Case 2 (Investigative Analytics) is planned.",
        align="C"
    )

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 7, "110 total test runs  |  11 Copilot Studio agents  |  10 prompt categories", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 5.5,
        "Use Case 1: Legal Case Analysis  |  Use Case 2: Investigative Analytics (planned)",
        align="C"
    )

    # ══════════════════════════════════════════════════════════════════
    # THE QUESTION
    # ══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("The Question")

    pdf.body_text(
        "When government workers need answers from case data, which Copilot Studio approach "
        "delivers more reliable results?"
    )
    pdf.bullet(
        "A structured-data agent that queries a normalized database through purpose-built tools "
        "(MCP/SQL approach)",
        bold_lead="Structured Data:"
    )
    pdf.bullet(
        "A document-backed agent that retrieves answers from PDFs and Word files stored in "
        "SharePoint or uploaded as a knowledge base",
        bold_lead="Unstructured Documents:"
    )
    pdf.ln(2)
    pdf.body_text(
        "We are testing both approaches side-by-side across two government use cases, scoring "
        "every response on accuracy, completeness, and safety."
    )

    pdf.subsection_title("Use Cases")
    pdf.bullet(
        "11 Copilot Studio agents tested across 10 attorney-style prompts (110 test runs). "
        "50 synthetic child welfare cases, 275 people, 325 timeline events, 338 witness statements, "
        "150 discrepancies. All data is fictional.",
        bold_lead="Use Case 1 - Legal Case Analysis (complete):"
    )
    pdf.bullet(
        "Investigative analytics over 34 million rows of Philadelphia public records -- property "
        "ownership, code violations, demolitions, tax assessments, and real estate transfers. "
        "Same MCP/SQL architecture, same Copilot Studio agent configurations. Testing planned.",
        bold_lead="Use Case 2 - Investigative Analytics (planned):"
    )

    # ══════════════════════════════════════════════════════════════════
    # USE CASE 1: LEGAL CASE ANALYSIS
    # ══════════════════════════════════════════════════════════════════
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 11, "Use Case 1: Legal Case Analysis", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 9.5)
    pdf.set_text_color(*MED)
    pdf.cell(0, 6, "DSS Office of Legal Services  |  11 agents  |  10 prompts  |  110 test runs", new_x="LMARGIN", new_y="NEXT")

    pdf.section_title("Key Findings")

    # Finding 1
    pdf.subsection_title("1. Structured data agents are consistently precise")
    pdf.body_text(
        "Agents backed by structured data returned complete, accurate answers on every prompt "
        "where the information existed in the database. For timeline enumeration, all three "
        "structured agents scored 12 out of 12 events with zero fabrication. Document-backed "
        "agents ranged from 12 out of 12 (best case) down to 4 out of 12 with data from the "
        "wrong case mixed in."
    )

    # Finding 2
    pdf.subsection_title("2. Every agent has a failure mode")
    pdf.body_text(
        "No single Copilot Studio configuration was correct on every question. Each approach has blind "
        "spots that could mislead an attorney if used without review:"
    )

    failure_headers = ["Risk", "Severity", "What Happened", "Affected Agents"]
    failure_widths = [32, 18, 72, 48]
    failure_rows = [
        ["Cross-case\ncontamination", "Critical", "Case 2 data injected into\nCase 1 timeline", "1 document agent\n(SharePoint PDF, GCC)"],
        ["Misleading source\nreproduced", "Critical", "7 of 8 document agents repeated\nan incorrect 'no fractures' claim", "All document agents\nexcept SP/PDF Commercial"],
        ["Missed contradiction", "Critical", "Agent concluded 'no evidence'\nwhen contradiction data existed", "2 structured agents\n(GPT-4.1 based)"],
        ["Misattribution", "High", "4 of 8 document agents attributed\none person's statement to another", "4 document agents\n(mixed platforms)"],
        ["Fabricated fact", "High", "Agent confidently stated\n'2:00 AM' (actual: 3:15 AM)", "1 structured agent\n(MCP, GCC)"],
        ["Silent failure", "Medium", "Hallucinated a case number,\nreturned no results, no warning", "1 structured agent\n(Web application)"],
    ]

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(*TABLE_HEADER_BG)
    pdf.set_text_color(*TABLE_HEADER_FG)
    for i, h in enumerate(failure_headers):
        pdf.cell(failure_widths[i], 7, h, border=0, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 7)
    for r_idx, row in enumerate(failure_rows):
        bg = ROW_ALT if r_idx % 2 == 0 else ROW_WHT
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*DARK)
        y_start = pdf.get_y()
        x_start = pdf.get_x()
        row_h = 10
        for i, val in enumerate(row):
            pdf.set_xy(x_start + sum(failure_widths[:i]), y_start)
            if i == 1:
                sev = val.strip()
                if sev == "Critical":
                    pdf.set_text_color(*RED)
                elif sev == "High":
                    pdf.set_text_color(200, 120, 20)
                else:
                    pdf.set_text_color(*AMBER)
                pdf.set_font("Helvetica", "B", 7)
            else:
                pdf.set_text_color(*DARK)
                pdf.set_font("Helvetica", "", 7)
            pdf.multi_cell(failure_widths[i], 5, val, border=0, align="C" if i == 1 else "L", fill=True)
        pdf.set_y(y_start + row_h)
    pdf.ln(3)

    # Finding 3
    pdf.subsection_title("3. The AI model matters as much as the architecture")
    pdf.body_text(
        "The evaluation revealed a significant split between the two underlying models used by Copilot Studio. "
        "Government Cloud (GCC) environments use GPT-4o, while Commercial environments use GPT-4.1. "
        "Neither can be changed by the agency."
    )
    pdf.bullet(
        "Better at selecting the right tools (always checks for contradictions), uses precise "
        "legal phrasing, gets specific facts like bedtime correct. However, more likely to "
        "fabricate details when uncertain.",
        bold_lead="GPT-4o (GCC):"
    )
    pdf.bullet(
        "More factually faithful with fewer fabricated details. However, consistently fails to "
        "check for contradictions, leading to missed issues that exist in the data.",
        bold_lead="GPT-4.1 (Commercial):"
    )

    # Finding 4
    pdf.subsection_title("4. Document format affects results more than expected")
    pdf.body_text(
        "PDF files indexed via SharePoint in a Commercial environment produced the strongest "
        "document-backed results. The same documents in Word format, or accessed through GCC, "
        "scored measurably lower. Knowledge-base uploads (flat file uploads) performed unevenly, "
        "with PDF generally outperforming Word."
    )

    fmt_headers = ["Source & Format", "Avg Accuracy", "Notes"]
    fmt_widths = [55, 28, 87]
    fmt_rows = [
        ["Structured Database (MCP/SQL)", "12 / 12", "Deterministic and complete"],
        ["SharePoint PDF (Commercial)", "12 / 12", "Strongest document agent overall"],
        ["SharePoint Word (Commercial)", "12 / 12", "Minor time errors and one fabricated event"],
        ["Knowledge Base PDF (GCC)", "10 / 12", "Best knowledge-base agent"],
        ["SharePoint Word (GCC)", "9 / 12", "Correct facts but limited source coverage"],
        ["Knowledge Base Word (Commercial)", "9 / 12", "Good detail but gaps in later events"],
        ["Knowledge Base Word (GCC)", "8 / 12", "Relied on single source document"],
        ["Knowledge Base PDF (Commercial)", "6 / 12", "Collapsed multiple events into one"],
        ["SharePoint PDF (GCC)", "~4 / 12", "Mixed in data from a different case"],
    ]
    pdf.styled_table(fmt_headers, fmt_rows, fmt_widths, font_size=7.5)
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*LIGHT)
    pdf.cell(0, 5, "Accuracy scores shown for the timeline enumeration prompt (12 events expected).", new_x="LMARGIN", new_y="NEXT")

    # Finding 5
    pdf.ln(2)
    pdf.subsection_title("5. Structured data fails safely; documents fail dangerously")
    pdf.body_text(
        "When structured-data agents lack information, they say so explicitly: \"This information "
        "is not in the available data.\" This is an honest absence that signals the attorney to "
        "look elsewhere."
    )
    pdf.body_text(
        "When document-backed agents encounter a misleading source, they reproduce it faithfully "
        "with a citation. The citation makes the wrong answer appear authoritative. For example, "
        "an attorney reading \"no fractures detected [Sheriff Report, p. 3]\" has no reason to "
        "doubt it, but the medical records show two fractures that the summary omitted. Seven of "
        "eight document agents made this error."
    )

    # ══════════════════════════════════════════════════════════════════
    # RESULTS AT A GLANCE
    # ══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("Results at a Glance")

    pdf.body_text(
        "Each of the 10 prompts tests a different type of question attorneys commonly ask. "
        "The table below summarizes how Copilot Studio's two architecture groups performed and "
        "the practical takeaway for each question type."
    )

    glance_headers = ["#", "Question Type", "Structured\nAgents", "Best Doc\nAgent", "Worst Doc\nAgent", "Key Takeaway"]
    glance_widths = [7, 26, 22, 22, 22, 71]
    glance_rows = [
        ["1", "ER arrival time\n& nurse name", "Time correct;\nnurse not in DB", "Time + nurse\n+ employee ID", "Found\nnothing", "Nurse name only exists in\ndocuments -- need both layers"],
        ["2", "Witness\nstatements", "Full quotes,\ncross-doc analysis", "Correct time,\nrich detail", "Missed key\nstatement", "4 of 8 doc agents attributed\none person's words to another"],
        ["3", "Contradiction\ndetection", "GCC: found it;\nGPT-4.1: missed", "3-document\nsynthesis", "Hallucinated\ncase number", "GPT-4.1 agents consistently\nmiss contradictions in data"],
        ["4", "Cross-document\nconflict", "Honest: 'not\nin our data'", "Only agent to\ncatch conflict", "Repeated\nincorrect claim", "Most dangerous prompt --\nmisleading source reproduced"],
        ["5", "Full timeline\n(12 events)", "All 3:\n12 / 12", "12 / 12 with\nricher detail", "4 / 12 with\nwrong-case data", "Structured data makes\nenumeration trivial"],
        ["6", "People roster\n(8 people)", "All 3:\n8 / 8", "8 / 8 plus\n4 extras", "5 / 8\nincomplete", "Doc agents found 4 people\nnot in the database"],
        ["7", "Statement\nevolution", "10 of 11 agents\nfound all changes", "All changes +\nmotive analysis", "Missed 1 of 3\nchanges", "Strongest consensus across\nall agent types"],
        ["8", "Filter by\naudience", "All 3 agents\nfailed", "4 / 4 with\nsource detail", "Returned wrong\nstatement type", "Only prompt where doc agents\nstrictly outperform structured"],
        ["9", "Aggregate\ncount (9 cases)", "All 3:\n9 / 9", "1 / 9\n(expected)", "1 / 9\n(expected)", "Cross-case queries are\nstructured data's top strength"],
        ["10", "Time gap\ncalculation", "Gold standard:\nall milestones", "Correct gap\ncalculation", "Fabricated time,\nsaid 10 hours", "Arithmetic reasoning exposes\nweaknesses in every agent"],
    ]

    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_fill_color(*TABLE_HEADER_BG)
    pdf.set_text_color(*TABLE_HEADER_FG)
    for i, h in enumerate(glance_headers):
        pdf.cell(glance_widths[i], 10, h, border=0, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 6.5)
    for r_idx, row in enumerate(glance_rows):
        bg = ROW_ALT if r_idx % 2 == 0 else ROW_WHT
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*DARK)
        y_start = pdf.get_y()
        x_start = pdf.get_x()
        cell_h = 13
        for i, val in enumerate(row):
            pdf.set_xy(x_start + sum(glance_widths[:i]), y_start)
            pdf.set_text_color(*DARK)
            pdf.set_font("Helvetica", "B" if i == 0 else "", 6.5)
            pdf.multi_cell(glance_widths[i], 4.3, val, border=0, align="C" if i <= 0 else "L", fill=True)
        pdf.set_y(y_start + cell_h)
    pdf.ln(3)

    # ══════════════════════════════════════════════════════════════════
    # AGENT SCORECARD
    # ══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("Agent Scorecard")

    pdf.body_text(
        "Each Copilot Studio agent was graded on every prompt: Pass (accurate and useful), "
        "Partial (correct core facts but incomplete or minor errors), "
        "Fail (wrong answer, dangerous error, or critical omission), or "
        "N/A (data not available and agent was transparent about it)."
    )

    sc_headers = ["Agent", "Model", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"]
    sc_widths = [36, 16] + [11.8] * 10
    sc_rows = [
        ["Web Application", "4.1", "Pass", "Pass", "Fail", "Pa", "Pass", "Pass", "Pass", "Fail", "Pass", "Fail"],
        ["MCP - Commercial", "4.1", "Pass", "Pa", "Pa", "N/A", "Pass", "Pass", "Pa", "Fail", "Pass", "Pass"],
        ["MCP - GCC", "4o", "Fail", "Pass", "Pass", "N/A", "Pass", "Pass", "Pass", "Pa", "Pass", "Pa"],
        ["SP/PDF - Com", "4.1", "Pass", "Pa", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pa", "Pass"],
        ["SP/DOCX - Com", "4.1", "Pass", "Fail", "Pa", "Fail", "Pa", "Pass", "Pass", "Pass", "Pa", "Pass"],
        ["KB/DOCX - Com", "4.1", "Pass", "Fail", "Pass", "Fail", "Pa", "Pass", "Pass", "Pass", "Pa", "Pass"],
        ["KB/PDF - Com", "4.1", "Pass", "Pass", "Pass", "Fail", "Fail", "Pass", "Pass", "Pass", "Pa", "Pa"],
        ["SP/PDF - GCC", "4o", "Pass", "Fail", "Pa", "Fail", "Fail", "Fail", "Pass", "Fail", "Pa", "Fail"],
        ["SP/DOCX - GCC", "4o", "Fail", "Pa", "Pa", "Fail", "Pa", "Fail", "Pass", "Fail", "Pa", "Pass"],
        ["KB/PDF - GCC", "4o", "Pa", "Pa", "Pass", "Fail", "Pass", "Pass", "Pass", "Pass", "Pa", "Pa"],
        ["KB/DOCX - GCC", "4o", "Pa", "Fail", "Pass", "Fail", "Pa", "Pa", "Pass", "Pass", "Pa", "Pa"],
    ]
    pdf.colored_score_table(sc_headers, sc_rows, sc_widths)

    pdf.ln(4)
    # Legend
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*MED)
    legend_x = pdf.get_x()
    pdf.set_x(legend_x)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*GREEN)
    pdf.write(5, "Pass")
    pdf.set_text_color(*MED)
    pdf.set_font("Helvetica", "", 8)
    pdf.write(5, " = Accurate & useful    ")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*AMBER)
    pdf.write(5, "Pa")
    pdf.set_text_color(*MED)
    pdf.set_font("Helvetica", "", 8)
    pdf.write(5, " = Partial (minor gaps)    ")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*RED)
    pdf.write(5, "Fail")
    pdf.set_text_color(*MED)
    pdf.set_font("Helvetica", "", 8)
    pdf.write(5, " = Wrong or dangerous    ")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*LIGHT)
    pdf.write(5, "N/A")
    pdf.set_text_color(*MED)
    pdf.set_font("Helvetica", "", 8)
    pdf.write(5, " = Data unavailable (honest)")
    pdf.ln(8)

    # Prompt legend
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(*MED)
    prompts = [
        "P1: ER arrival time", "P2: Witness statements", "P3: Contradiction detection",
        "P4: Cross-document conflict", "P5: Full timeline", "P6: People roster",
        "P7: Statement evolution", "P8: Audience filter", "P9: Aggregate count",
        "P10: Time gap calculation"
    ]
    pdf.multi_cell(0, 4.5, "   |   ".join(prompts), align="C")

    # ══════════════════════════════════════════════════════════════════
    # WIN/LOSS SUMMARY
    # ══════════════════════════════════════════════════════════════════
    pdf.ln(6)
    pdf.section_title("Overall Rankings")

    rank_headers = ["Rank", "Agent", "Pass", "Partial", "Fail", "N/A"]
    rank_widths = [12, 50, 24, 24, 24, 24]
    rank_rows = [
        ["1", "SP/PDF - Commercial", "8", "2", "0", "0"],
        ["2", "MCP - GCC", "6", "2", "1", "1"],
        ["3", "KB/DOCX - Commercial", "6", "2", "2", "0"],
        ["4", "KB/PDF - Commercial", "6", "2", "2", "0"],
        ["5", "Web Application", "6", "1", "3", "0"],
        ["6", "SP/DOCX - Commercial", "5", "3", "2", "0"],
        ["7", "MCP - Commercial", "5", "3", "1", "1"],
        ["8", "KB/PDF - GCC", "5", "4", "1", "0"],
        ["9", "KB/DOCX - GCC", "3", "5", "2", "0"],
        ["10", "SP/DOCX - GCC", "2", "4", "4", "0"],
        ["11", "SP/PDF - GCC", "2", "2", "6", "0"],
    ]
    pdf.styled_table(rank_headers, rank_rows, rank_widths, font_size=8)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 5.5,
        "SharePoint PDF (Commercial) is the only agent with zero failures across all 10 prompts."
    )

    # ══════════════════════════════════════════════════════════════════
    # USE CASE 2: INVESTIGATIVE ANALYTICS
    # ══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 11, "Use Case 2: Investigative Analytics", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 9.5)
    pdf.set_text_color(*MED)
    pdf.cell(0, 6, "Philly Poverty Profiteering  |  Testing Planned", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)
    pdf.body_text(
        "The second use case evaluates the same Copilot Studio agent configurations against a "
        "large-scale investigative analytics workload: 34 million rows of Philadelphia public "
        "records spanning property ownership, code violations, demolitions, business licenses, "
        "tax assessments, and real estate transfers."
    )
    pdf.body_text(
        "The underlying system uses the same architecture pattern -- MCP server backed by Azure "
        "Functions and Azure SQL -- with 14 investigative tools. Copilot Studio agents will be "
        "tested using the same methodology: structured data (MCP/SQL) vs. document-backed "
        "(SharePoint and knowledge base), scored on accuracy, completeness, and safety."
    )
    pdf.body_text(
        "This use case will stress-test Copilot Studio's ability to handle aggregate queries "
        "across millions of records, cross-dataset pattern detection, and complex multi-step "
        "investigative reasoning -- capabilities that go well beyond single-case retrieval."
    )

    pdf.ln(4)
    pdf.set_fill_color(*GRAY_BG)
    pdf.set_draw_color(*ACCENT)
    box_y = pdf.get_y()
    pdf.rect(pdf.l_margin, box_y, pdf.w - pdf.l_margin - pdf.r_margin, 18, "FD")
    pdf.set_xy(pdf.l_margin + 6, box_y + 5)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 7, "Results will be added to this report after testing is complete.")
    pdf.set_y(box_y + 24)

    # ══════════════════════════════════════════════════════════════════
    # RECOMMENDATION
    # ══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("Recommendation")

    pdf.body_text(
        "Based on Use Case 1 results, neither Copilot Studio approach alone is sufficient for "
        "production-grade reliability. The strongest configuration layers both:"
    )

    pdf.bullet(
        "For precision queries: timelines, people rosters, statement comparisons, "
        "contradiction detection, aggregate counts, and filtering by event type. These are the "
        "questions attorneys ask most often, and where wrong answers carry the greatest risk.",
        bold_lead="Structured data (database-backed):"
    )
    pdf.ln(1)
    pdf.bullet(
        "For narrative detail the database does not capture: nursing notes, "
        "page-level citations, clinical observations, home visit narratives. These enrich "
        "structured answers with the context attorneys need for legal filings.",
        bold_lead="Document grounding (SharePoint/knowledge base):"
    )
    pdf.ln(1)
    pdf.bullet(
        "No Copilot Studio configuration was correct on every prompt. The value of Copilot Studio "
        "is speed and coverage, not infallibility. The right question is not \"can I trust the agent?\" "
        "but \"does it surface enough for me to make a better decision, faster?\"",
        bold_lead="Human review remains essential."
    )

    pdf.ln(6)

    # Callout box
    pdf.set_fill_color(*GRAY_BG)
    pdf.set_draw_color(*ACCENT)
    box_y = pdf.get_y()
    pdf.rect(pdf.l_margin, box_y, pdf.w - pdf.l_margin - pdf.r_margin, 32, "FD")
    pdf.set_xy(pdf.l_margin + 6, box_y + 5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 7, "Bottom Line")
    pdf.set_xy(pdf.l_margin + 6, box_y + 14)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 12, 6,
        "Structured data delivers precision for day-to-day queries. "
        "Document grounding adds narrative richness for complex analysis. "
        "Together, they cover each other's blind spots. Neither alone is safe enough. "
        "Use Case 2 will test whether this finding holds at scale."
    )

    # ══════════════════════════════════════════════════════════════════
    # OUTPUT
    # ══════════════════════════════════════════════════════════════════
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    out_path = os.path.join(out_dir, "executive-summary.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    build_pdf()
