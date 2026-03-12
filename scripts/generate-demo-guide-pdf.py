"""
Generate demo-guide.pdf with hardcoded content (no markdown file dependency).
Uses fpdf2 -- same self-contained pattern as generate-executive-pdf.py.

Usage: python scripts/generate-demo-guide-pdf.py
Output: docs/pdf/demo-guide.pdf
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
CHECK_COLOR = (41, 98, 163)
CODE_BG = (245, 245, 245)
CODE_BORDER = (220, 220, 220)
QUOTE_BG = (248, 249, 252)
QUOTE_BORDER = (41, 98, 163)

# Level colors
LVL1_COLOR = (76, 175, 80)    # green
LVL2_COLOR = (139, 195, 74)   # light green
LVL3_COLOR = (255, 193, 7)    # amber
LVL4_COLOR = (255, 87, 34)    # deep orange
LVL5_COLOR = (211, 47, 47)    # red


class DemoGuidePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT)
        self.cell(0, 6, sanitize_text("Agent Fidelity Spectrum for Copilot Studio -- Demo Guide"), align="L")
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
        self.cell(0, 4, sanitize_text("Confidential | March 2026"), align="C")

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

    def checkbox(self, text, checked=False, indent=8):
        """Render a checkbox list item with [ ] or [x] marker."""
        text = sanitize_text(text)
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font("Helvetica", "", 9.5)
        marker = "[x]" if checked else "[ ]"
        self.set_text_color(*CHECK_COLOR if not checked else MED)
        self.write(5.5, marker + "  ")
        self.set_text_color(*DARK)
        self.set_font("Helvetica", "", 9.5)
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

    def blockquote(self, text):
        """Render a blockquote with italic text and a left accent bar."""
        text = sanitize_text(text)
        y_start = self.get_y()
        self.set_x(self.l_margin + 6)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(*MED)
        cell_w = self.w - self.l_margin - self.r_margin - 12
        self.multi_cell(cell_w, 5, text)
        y_end = self.get_y()
        # Draw accent bar
        self.set_draw_color(*QUOTE_BORDER)
        self.set_line_width(0.8)
        self.line(self.l_margin + 3, y_start, self.l_margin + 3, y_end)
        self.set_line_width(0.2)
        self.ln(2)

    def code_block(self, lines):
        """Render a code block with gray background."""
        y_start = self.get_y()
        block_h = len(lines) * 4.5 + 6
        if y_start + block_h > self.h - 25:
            self.add_page()
            y_start = self.get_y()
        self.set_fill_color(*CODE_BG)
        self.set_draw_color(*CODE_BORDER)
        self.rect(self.l_margin + 4, y_start,
                  self.w - self.l_margin - self.r_margin - 8,
                  block_h, "FD")
        self.set_xy(self.l_margin + 8, y_start + 3)
        self.set_font("Courier", "", 8)
        self.set_text_color(*DARK)
        for cl in lines:
            self.cell(0, 4.5, sanitize_text(cl), new_x="LMARGIN", new_y="NEXT")
            self.set_x(self.l_margin + 8)
        self.set_y(y_start + block_h + 2)

    def horizontal_rule(self):
        """Draw a horizontal divider line."""
        self.ln(2)
        self.set_draw_color(*DIVIDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)


def build_pdf():
    pdf = DemoGuidePDF()
    pdf.set_margins(20, 20, 20)

    # ====================================================================
    # COVER PAGE
    # ====================================================================
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 100, "F")

    pdf.set_y(30)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 12, "Agent Fidelity Spectrum for Copilot Studio", align="C",
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
    pdf.cell(0, 7, "Presenter Guide | March 2026", align="C",
             new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(115)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MED)
    pdf.multi_cell(0, 6, sanitize_text(
        "A five-level framework for demonstrating AI agent accuracy "
        "across government use cases. Includes demo script, talking points, "
        "timing guide, Q&A handling, and reference appendices."
    ), align="C")

    pdf.set_y(145)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 7, "50-60 minutes  |  5 levels  |  2 use cases  |  6 models  |  462 test runs",
             align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 6, sanitize_text(
        "The agent accelerates the human; it does not replace them. "
        "Mandatory human review, citation linking, audit logging, and "
        "organizational culture that treats AI output as a draft -- never "
        "a decision."
    ), align="C")

    # ====================================================================
    # AT A GLANCE
    # ====================================================================
    pdf.add_page()
    pdf.section_title("At a Glance")

    pdf.body_text(
        "462 test runs across 21 agent configurations and 6 models. Here is what the data says."
    )

    # ── Colored tiles for levels 1-2, 3, 4 ──
    tiles = [
        (LVL2_COLOR, "Levels 1-2", "Just works",
         "8/10 with zero customization. Model choice irrelevant."),
        (LVL3_COLOR, "Level 3", "Data over documents",
         "MCP agents outperformed document search on every aggregate query."),
        (LVL4_COLOR, "Level 4", "The inflection point",
         "Three gaps emerged: tools, data, and model. All fixable."),
    ]
    tile_gap = 4
    tile_count = len(tiles)
    total_w = pdf.w - pdf.l_margin - pdf.r_margin
    tile_w = (total_w - tile_gap * (tile_count - 1)) / tile_count
    pad = 5
    stripe_w = 3
    inner_w = tile_w - stripe_w - pad * 2

    tile_heights = []
    for _, label, title, body in tiles:
        pdf.set_font("Helvetica", "B", 8)
        lh = pdf.multi_cell(inner_w, 4.5, sanitize_text(label), dry_run=True, output="HEIGHT")
        pdf.set_font("Helvetica", "B", 11)
        th = pdf.multi_cell(inner_w, 6, sanitize_text(title), dry_run=True, output="HEIGHT")
        pdf.set_font("Helvetica", "", 9)
        bh = pdf.multi_cell(inner_w, 5, sanitize_text(body), dry_run=True, output="HEIGHT")
        tile_heights.append(pad + lh + 1 + th + 2 + bh + pad)
    row_h = max(tile_heights)

    y_start = pdf.get_y()
    for i, (color, label, title, body) in enumerate(tiles):
        x = pdf.l_margin + i * (tile_w + tile_gap)
        bg = tuple(int(c * 0.12 + 255 * 0.88) for c in color)
        pdf.set_fill_color(*bg)
        pdf.rect(x, y_start, tile_w, row_h, "F")
        pdf.set_fill_color(*color)
        pdf.rect(x, y_start, stripe_w, row_h, "F")
        pdf.set_xy(x + stripe_w + pad, y_start + pad)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*color)
        pdf.multi_cell(inner_w, 4.5, sanitize_text(label))
        label_bottom = pdf.get_y()
        pdf.set_xy(x + stripe_w + pad, label_bottom + 1)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(inner_w, 6, sanitize_text(title))
        title_bottom = pdf.get_y()
        pdf.set_xy(x + stripe_w + pad, title_bottom + 2)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*MED)
        pdf.multi_cell(inner_w, 5, sanitize_text(body))

    pdf.set_y(y_start + row_h + 6)

    pdf.bullet(
        "One new tool, cleaner data, and cross-referenced documents.",
        bold_lead="Every gap was fixable, and none required AI expertise."
    )

    pdf.horizontal_rule()

    # ====================================================================
    # THE FRAMEWORK
    # ====================================================================
    pdf.section_title("The Framework")

    pdf.body_text(
        "This demo is built around a five-level fidelity spectrum that helps "
        "government leaders decide where AI agents are safe to deploy aggressively, "
        "where they need guardrails, and where human review is non-negotiable."
    )

    fw_headers = ["Level", "Name", "Stakes", "Key Question"]
    fw_widths = [16, 34, 42, 78]
    fw_rows = [
        ["1", "Information Discovery", "Minor inconvenience",
         '"Help me find the right document"'],
        ["2", "Summarization", "Wasted time",
         '"Summarize this report for my briefing"'],
        ["3", "Operational Support", "Misallocated resources",
         '"Show me the portfolio-level picture"'],
        ["4", "Investigative", "Missed evidence",
         '"Cross-reference these records"'],
        ["5", "Legal/Adjudicative", "Wrong legal outcome",
         '"Prepare the facts for this hearing"'],
    ]
    pdf.styled_table(fw_headers, fw_rows, fw_widths, font_size=8)

    pdf.ln(4)
    pdf.body_text(
        "The story arc: Start where AI is easy and reliable. Escalate to where "
        "engineering decisions determine success or failure. End with the "
        "trust-but-verify moment that makes you credible.",
        bold_lead="The story arc:"
    )

    pdf.horizontal_rule()

    # ====================================================================
    # DEMO URLS
    # ====================================================================
    pdf.section_title("Demo URLs")

    pdf.bullet("https://happy-wave-016cd330f.1.azurestaticapps.net",
               bold_lead="DSS Web App:")
    pdf.bullet("https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/mcp",
               bold_lead="MCP Endpoint:")
    pdf.bullet("2024-DR-42-0892 (CPS, Webb/Holloway)",
               bold_lead="Primary Case:")
    pdf.bullet("2024-DR-15-0341 (TPR, Price)",
               bold_lead="Secondary Case:")

    pdf.horizontal_rule()

    # ====================================================================
    # PRE-DEMO CHECKLIST
    # ====================================================================
    pdf.section_title("Pre-Demo Checklist")

    pdf.checkbox("Sign into SWA URL 10 minutes before")
    pdf.checkbox('Click "Warm Up" button to prime the cold-start chain')
    pdf.checkbox("Have SharePoint agent open in a separate browser tab (for Level 2 comparison)")
    pdf.checkbox("Have sharepoint-docs/Demo_Comparison_Prompts.md open for reference")
    pdf.checkbox("Know the case numbers: 2024-DR-42-0892 (CPS) and 2024-DR-15-0341 (TPR)")
    pdf.checkbox("Have the slide deck open for the framework overview")
    pdf.checkbox("Test that the chat widget responds before the audience arrives")

    pdf.horizontal_rule()

    # ====================================================================
    # KEY STATS TO MEMORIZE
    # ====================================================================
    pdf.section_title("Key Stats to Memorize")

    stats_headers = ["Stat", "Value"]
    stats_widths = [100, 70]
    stats_rows = [
        ["Total test runs", "462 across 21 agents, 6 models, 7 rounds"],
        ["Document agents (Levels 1-2)", "8/10 with zero engineering"],
        ["GPT-4.1 agents (structured data)", "9.5/10 average"],
        ["GPT-4o agents (GCC model gap)", "4/10 average"],
        ["M365 Copilot Com (platform model)", "2/10 (20% pass rate)"],
        ["One fuzzy search tool", "13% to 100% accuracy"],
        ["Document agents on skeletal survey", "7 of 8 reproduced a misleading finding"],
        ["Document hygiene (zero code)", "GCC: 3/10 to 9/10; Com: 8/10 to 10/10"],
        ["Iterative improvement", "0-1/10 to perfect 10/10 (3-5 rounds)"],
    ]
    pdf.styled_table(stats_headers, stats_rows, stats_widths, font_size=8)

    # ====================================================================
    # DEMO FLOW
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Demo Flow")

    # -- Opening: The Hook --
    pdf.subsection_title("Opening: The Hook (3-4 minutes, no product)")

    pdf.blockquote(
        '"Some of you may remember me from such demos as the delegation demo, '
        "or the [insert another landmark demo here]. And there's one thing those "
        "demos have in common with this one: I like to build test harnesses that "
        "demonstrate the different capabilities of our technology in real-world "
        "use cases that my customers care about. And what's funny is -- both this "
        "demo and the delegation demo deal with the same fundamental topic: "
        'accuracy."'
    )

    pdf.blockquote(
        '"Before we dive in, let me tell you what this demo is and what it '
        "isn't. It's a way to show you a process and methods -- with real-world "
        "examples -- for making your agents better. It is not a demo on data "
        "extraction, other than to provide ideas on tools and process for getting "
        'that done when extraction is necessary."'
    )

    pdf.blockquote(
        '"I have a feeling that when we\'re all said and done, you\'ll have more '
        'questions than answers. But let\'s get into it."'
    )

    pdf.body_text("Show the five-level spectrum slide.", bold_lead="Show the five-level spectrum slide.")

    pdf.blockquote(
        '"We developed this framework after running 462 test evaluations across '
        "two government use cases and 21 different agent configurations. Not all "
        "AI use cases need the same level of accuracy, and not all agent "
        'architectures deliver it."'
    )

    pdf.blockquote(
        '"Level 1: finding a policy document. Level 5: preparing facts for a '
        "legal hearing where a family's future depends on accuracy. Most agencies "
        "jump straight to Copilot without asking 'where does my use case fall on "
        "this spectrum?' Today I'll show you why that question matters.\""
    )

    # -- Act 1: Level 2 --
    pdf.add_page()
    pdf.subsection_title("Act 1: Level 2 -- Summarization Works Out of the Box (2 minutes)")

    pdf.blockquote(
        "\"Let's start at Level 2 -- summarization. This is where most agencies "
        'start, and the good news is: it works."'
    )

    pdf.body_text("If SharePoint agent is available, show it:",
                  bold_lead="If SharePoint agent is available, show it:")

    pdf.blockquote(
        "\"Here's a Copilot Studio agent pointed at a SharePoint document library. "
        "No custom code. I'll ask it to summarize a case.\""
    )

    pdf.code_block([
        "Summarize the investigation report for the Webb/Holloway case.",
        "What are the key findings?"
    ])

    pdf.blockquote(
        '"Solid summary. It found the main themes, identified the parties, got '
        "the narrative right. For a policy analyst preparing a briefing, this is "
        "perfectly useful. Score: 8 out of 10 in our testing. No engineering "
        'required."'
    )

    pdf.blockquote(
        '"But watch what happens when we ask harder questions."'
    )

    # -- Act 2: Level 3 --
    pdf.add_page()
    pdf.subsection_title("Act 2: Level 3 -- Aggregate Queries (2 minutes)")

    pdf.body_text("Switch to the DSS Web App. Open the Case Browser.",
                  bold_lead="Switch to the DSS Web App. Open the Case Browser.")

    pdf.blockquote(
        '"Now I\'m switching to our structured data agent. There are 50 synthetic '
        "cases in this database -- completely fictional, no real data -- modeled "
        'on real case structures."'
    )

    pdf.body_text("Click the chat widget. Ask:",
                  bold_lead="Click the chat widget. Ask:")

    pdf.code_block([
        "How many active cases does DSS currently have?",
        "Break them down by case type."
    ])

    pdf.blockquote(
        '"Aggregate questions -- \'how many\', \'what\'s the breakdown\' -- these '
        "work reliably across every agent type with structured data access, "
        "including both Copilot Studio MCP agents and pro-code agents. Even the "
        "weakest performers got these right. This is Level 3: operational decision "
        'support."'
    )

    pdf.blockquote(
        '"But here\'s where it gets interesting. What happens when we move from '
        "'show me the big picture' to 'show me the details for this specific "
        "case'?\""
    )

    # -- Act 3: Level 4 --
    pdf.add_page()
    pdf.subsection_title("Act 3: Level 4 -- The Inflection Point (5-7 minutes)")

    pdf.body_text("This is the centerpiece of the demo.",
                  bold_lead="This is the centerpiece of the demo.")

    pdf.blockquote(
        '"Now, there\'s no way to have this conversation without getting a little '
        'technical. But I\'ll do my best."'
    )

    pdf.blockquote(
        '"Level 4 is investigative work. Cross-referencing records, building '
        "timelines, finding discrepancies between accounts. This is where agent "
        'architecture starts to matter -- a lot."'
    )

    pdf.body_text("Type the money prompt:", bold_lead="Type the money prompt:")

    pdf.code_block([
        "I represent DSS in case 2024-DR-42-0892. After reviewing the case,",
        "can you provide:",
        "1. A detailed timeline of pertinent facts with source citations",
        "2. A chart of discrepancies between the two parents' accounts",
        "3. All statements made by Marcus Webb to case managers or law enforcement",
        "4. All statements made by Dena Holloway to case managers or law enforcement"
    ])

    pdf.blockquote(
        '"This is the exact prompt structure a DSS attorney used when she tested '
        'an earlier version. Four analytical tasks in one request."'
    )

    pdf.body_text("Wait for response (10-15 seconds).", bold_lead="Wait for response (10-15 seconds).")

    pdf.body_text("Walk through each section:", bold_lead="Walk through each section:")

    pdf.subsection_title("Timeline:")

    pdf.blockquote(
        '"Every event has a date, a time where available, and a source citation '
        "-- page number in the original document. An attorney can verify every "
        "entry. Count them: [X] timeline entries, all chronologically ordered. "
        "The SharePoint agent returned maybe 6 or 7 and got two dates wrong.\""
    )

    pdf.subsection_title("Discrepancy Chart:")

    pdf.blockquote(
        '"Structured comparison -- what Marcus said versus what Dena said, with '
        "the evidence that contradicts each. Not 'the parents disagreed.' "
        "Specific, citable contradictions an attorney can use in court filings.\""
    )

    pdf.subsection_title("Statements (Marcus Webb):")

    pdf.blockquote(
        '"Every statement Marcus made, in chronological order: what he said, who '
        "he said it to, the date, the source document, and the page number.\""
    )

    pdf.subsection_title("Statements (Dena Holloway):")

    pdf.blockquote(
        '"Same for Dena. And notice her story changes -- the hospital statement '
        "on June 12th says one thing, but the sheriff interview the next "
        "afternoon reveals the 9:30 PM thump she didn't mention before. That "
        'evolution is captured because each statement is its own record."'
    )

    pdf.subsection_title("The data point:")

    pdf.blockquote(
        '"This agent scored 10 out of 10 in our evaluation. The same prompt sent '
        "to the SharePoint document agent? It scored 3. It missed statements, got "
        "dates wrong, and couldn't produce the discrepancy chart at all.\""
    )

    pdf.body_text("If time allows, show the model gap:",
                  bold_lead="If time allows, show the model gap:")

    pdf.blockquote(
        '"Here\'s the number that should keep you up at night. Among agents with '
        "structured data access -- both Copilot Studio MCP agents and pro-code "
        "agents -- GPT-4.1 averaged 9.5 out of 10. GPT-4o, which is what "
        "Government Cloud Copilot Studio uses today, scored 4 out of 10. Same "
        "tools, same data, same backend. The model is the bottleneck.\""
    )

    # -- Act 4: Level 5 --
    pdf.add_page()
    pdf.subsection_title("Act 4: Level 5 -- Trust But Verify (3-4 minutes)")

    pdf.blockquote(
        '"Now here\'s the slide I want you to remember after everything else fades."'
    )

    pdf.body_text("Type:", bold_lead="Type:")

    pdf.code_block([
        "Did the sheriff's investigation find fractures in Jaylen Webb's",
        "skeletal survey?"
    ])

    pdf.body_text("Wait for response.", bold_lead="Wait for response.")

    pdf.blockquote(
        '"The agent returns the medical records showing bilateral long bone '
        "fractures, with the radiology findings and page numbers. That's the "
        'right answer."'
    )

    pdf.blockquote(
        '"But here\'s what happened when we asked a document-based agent the same '
        "question. Seven out of eight document agents quoted the Sheriff's Report "
        "-- which says 'no fractures detected on skeletal survey.' The medical "
        "records in the same case clearly document fractures. The Sheriff's Report "
        "was wrong. The AI faithfully reproduced the error.\""
    )

    pdf.blockquote(
        '"This is Level 5. The agent was not wrong about what the document said. '
        "It was wrong about what was true. The citation was real. The confidence "
        'was justified. The conclusion was dangerous."'
    )

    pdf.blockquote(
        '"In a child welfare case, an attorney who trusts \'no fractures detected\' '
        "because an AI said so is making a worse decision than an attorney with "
        'no AI at all."'
    )

    pdf.body_text("Pause. Let it land.", bold_lead="Pause. Let it land.")

    pdf.body_text(
        "Transition into the walkthrough:",
        bold_lead="Transition into the walkthrough:"
    )

    pdf.blockquote(
        '"But here is the good news. We found a way to fix this. And it did not '
        "require a single line of code, a model upgrade, or a platform configuration "
        "change. Let me show you.\""
    )

    pdf.body_text(
        "Go directly into Act 4b: Document Improvement Walkthrough (next section).",
        bold_lead="[Go to Act 4b]"
    )

    pdf.body_text("After the walkthrough, return here for the human review thread.",
                  bold_lead="After the walkthrough:")

    pdf.body_text("The human review thread -- connect it to their daily experience:",
                  bold_lead="The human review thread -- connect it to their daily experience:")

    pdf.blockquote(
        '"Think about how you already use AI today. Copilot helps you draft an '
        "email -- you review it before you hit send. Copilot helps you write code "
        "-- you better be reviewing that before it goes to production. So why "
        "would we skip human review for any of these five levels? Especially at "
        "Level 5, where the stakes are a family's future?\""
    )

    pdf.blockquote(
        '"This is why Level 5 requires a different operating model. The AI is a '
        "research assistant -- it drafts, it retrieves, it organizes. The human "
        "decides. Trust but verify is not a suggestion at this level. It is the "
        'only responsible way to operate."'
    )

    # -- Act 4b: Document Improvement Walkthrough --
    pdf.add_page()
    pdf.subsection_title("Act 4b: Document Improvement Walkthrough (5-7 minutes)")

    pdf.body_text(
        "This is the audience's favorite section. You are walking them through "
        "a real improvement journey, step by step, with live results at each stage. "
        "Three steps, zero code.",
        bold_lead="Why this matters:"
    )

    pdf.callout_box(
        "The Story Arc",
        "Step 1: Baseline (3/10) -> Step 2: Cross-reference headers (7/10) -> "
        "Step 3: Metadata tags (8/10) -> Step 4: Cross-ref Case 2 docs (9/10). "
        "Same model, same platform. GCC went from worst in the test set to surpassing Commercial.",
        height=22
    )

    # -- Step 1 --
    pdf.ln(2)
    pdf.subsection_title("Step 1: The Baseline (show the problem)")

    pdf.body_text(
        "Open the original SharePoint document library. Show the audience: "
        "six PDFs, standard case file. No special formatting.",
        bold_lead="On screen:"
    )

    pdf.blockquote(
        '"This is what a typical case file looks like in SharePoint. Six documents: '
        "investigation report, medical records, sheriff report, court orders, GAL "
        "report, home study. Uploaded as PDFs, no modifications. A Copilot Studio "
        'agent pointed at this library. Let me show you how it does."'
    )

    pdf.body_text("Run the skeletal survey prompt:", bold_lead="Prompt 1:")

    pdf.code_block([
        "Did the Sheriff's Office investigation find fractures in Jaylen",
        "Webb's skeletal survey?"
    ])

    pdf.blockquote(
        '"Watch what comes back. The agent quotes the Sheriff Report: \'no fractures '
        "detected on skeletal survey.' Sounds definitive, right? But the Medical "
        "Records in the same case file document bilateral long bone fractures. The "
        "Sheriff Report was summarizing incorrectly. The agent faithfully reproduced "
        'the error."'
    )

    pdf.body_text("Run the Marcus Webb prompt:", bold_lead="Prompt 2:")

    pdf.code_block([
        "What did Marcus Webb tell hospital staff about when he put Jaylen",
        "to bed, and did he give the same answer to law enforcement?"
    ])

    pdf.blockquote(
        '"This one fails differently. The agent cannot even find Marcus Webb\'s '
        "statements to hospital staff. The nursing notes are in the Medical Records, "
        "but the agent never retrieves that document for this question. It only "
        'searches the documents it thinks are relevant."'
    )

    pdf.body_text(
        "Score: 3 out of 10 across our full 10-prompt test battery. "
        "Six outright failures, one partial pass. This was the worst-performing "
        "agent in our entire evaluation of 21 agents.",
        bold_lead="Result:"
    )

    # -- Step 2 --
    pdf.add_page()
    pdf.subsection_title("Step 2: Cross-Reference Headers (3/10 to 7/10)")

    pdf.body_text(
        "Open the cross-referenced document library side by side with the original. "
        "Pull up the Sheriff Report. Scroll to the top.",
        bold_lead="On screen:"
    )

    pdf.blockquote(
        '"Same documents, same content. The only change: each document now has a '
        "cross-reference header at the top. It lists every other document in the case "
        "file and describes what each one contains. This is standard legal case file "
        "practice. Nothing exotic.\""
    )

    pdf.body_text(
        "Show the Sheriff Report header. Read the Medical Records entry aloud:",
        bold_lead="Highlight:"
    )

    pdf.blockquote(
        '"Look at this entry: \'Medical Records contains the complete radiology report '
        "with skeletal survey findings, fracture diagnoses, fracture age estimates, "
        "physician assessment of non-accidental trauma, and ER nursing interview notes "
        "from both parents.' Now the agent knows where to look.\""
    )

    pdf.body_text(
        "Now open the Medical Records cross-reference header. Show the Sheriff Report "
        "entry:",
        bold_lead="Key annotation:"
    )

    pdf.blockquote(
        '"And here is the key: the Medical Records header says \'the Sheriff Report '
        "summarizes the skeletal survey as no fractures detected. This refers only to "
        "areas outside the known fracture sites. See Radiology Report below for "
        "complete findings including two diagnosed fractures.' We told the agent "
        'exactly where the conflict is."'
    )

    pdf.body_text(
        "Upload the cross-referenced documents to the agent. "
        "Run the same skeletal survey prompt:",
        bold_lead="Run the test:"
    )

    pdf.code_block([
        "Did the Sheriff's Office investigation find fractures in Jaylen",
        "Webb's skeletal survey?"
    ])

    pdf.blockquote(
        '"Now watch. The agent pulls the Medical Records as its primary source. '
        "Bilateral long bone fractures: right femur transverse fracture, left "
        "humerus spiral fracture, different stages of healing indicating two "
        'separate trauma events. This is the correct answer."'
    )

    pdf.body_text(
        "Full retest results: 3 out of 10 to 7 out of 10. "
        "Six failures became five passes and two partials. "
        "Zero code, same model, same platform.",
        bold_lead="Result:"
    )

    pdf.body_text("Show the improvement table:", bold_lead="Show the improvement table:")

    step2_headers = ["Prompt", "Before", "After"]
    step2_widths = [100, 35, 35]
    step2_rows = [
        ["P1: ER arrival time + admitting nurse", "Pass", "Pass"],
        ["P2: Marcus Webb statements to hospital staff", "Fail", "Partial"],
        ["P3: Crystal Price drug test results", "Partial", "Pass"],
        ["P4: Skeletal survey findings", "Fail", "Pass"],
        ["P5: Complete case timeline", "Fail", "Pass"],
        ["P6: People involved in Price case", "Fail", "Partial"],
        ["P7: Dena Holloway statement changes", "Pass", "Pass"],
        ["P8: Statements to law enforcement", "Fail", "Pass"],
        ["P9: TPR cases in the system", "Partial", "Partial"],
        ["P10: Time gap between thump and ER", "Fail", "Pass"],
    ]
    pdf.styled_table(step2_headers, step2_rows, step2_widths, font_size=7.5)

    pdf.ln(4)
    pdf.blockquote(
        '"Five failures flipped to passes. Just by telling each document what the '
        "other documents contain. A paralegal could do this in an afternoon.\""
    )

    # -- Step 3 --
    pdf.add_page()
    pdf.subsection_title("Step 3: SharePoint Metadata Tags (7/10 to 8/10)")

    pdf.body_text(
        "Open the SharePoint document library settings. Show the Topics and Keywords "
        "columns on Medical_Records.pdf.",
        bold_lead="On screen:"
    )

    pdf.blockquote(
        '"We still have one prompt stuck at Partial. The agent cannot find Marcus '
        "Webb's statements to hospital staff. Why? The agent's retrieval engine "
        "never pulls the Medical Records for a question about parent statements. "
        "It searches for 'Marcus Webb hospital statements' and only finds the "
        'Sheriff Report and DSS Investigation Report."'
    )

    pdf.blockquote(
        '"The fix: SharePoint metadata tags. We added Topics and Keywords to the '
        "Medical Records PDF: 'nursing interviews, parent statements to nursing "
        "staff, skeletal survey, fracture analysis, ER admission.' Now when the "
        "agent searches for parent statements, the Medical Records document shows "
        'up in the retrieval results."'
    )

    pdf.body_text("Run the Marcus Webb prompt again:", bold_lead="Run the test:")

    pdf.code_block([
        "What did Marcus Webb tell hospital staff about when he put Jaylen",
        "to bed, and did he give the same answer to law enforcement?"
    ])

    pdf.blockquote(
        '"Now the agent retrieves the Medical Records nursing notes. Marcus told '
        "hospital staff 'around ten' for bedtime. But the Sheriff Report says he told "
        "Lt. Odom approximately 8:00 PM. The agent surfaces the two-hour discrepancy "
        'across documents. That is the correct answer."'
    )

    pdf.body_text(
        "Score: 7 out of 10 to 8 out of 10. Same model (GPT-4o), same "
        "platform, same Copilot Studio configuration.",
        bold_lead="Result:"
    )

    # -- Step 4 --
    pdf.ln(2)
    pdf.subsection_title("Step 4: Cross-Reference the Second Case (8/10 to 9/10)")

    pdf.body_text(
        "The document library has two cases. We applied cross-reference headers "
        "to the Webb case (Case 1) in Step 2. Now apply the same treatment to "
        "the Price case (Case 2) documents.",
        bold_lead="On screen:"
    )

    pdf.blockquote(
        '"Same pattern. Each Price case document now lists the other documents '
        "in the case file and what they contain. The GAL Report is written by "
        "Thomas Reed, the court-appointed Guardian ad Litem. Before cross-references, "
        "the agent never surfaced his name when asked who was involved in the case. "
        'Now it does."'
    )

    pdf.body_text("Run the people roster prompt:", bold_lead="Run the test:")

    pdf.code_block([
        "Who are all the people involved in the Crystal Price TPR case,",
        "and what are their roles?"
    ])

    pdf.blockquote(
        '"Thomas Reed now appears as Guardian ad Litem. The agent pulls from '
        "the GAL Report and the DSS Investigation Report together. Before "
        "cross-references, it only cited the TPR Petition and missed him "
        'entirely."'
    )

    pdf.body_text(
        "Score: 8 out of 10 to 9 out of 10. The GCC agent now surpasses "
        "the Commercial SP/PDF agent (8/10). Same model (GPT-4o), same "
        "platform.",
        bold_lead="Result:"
    )

    # -- The Punchline --
    pdf.ln(2)
    pdf.subsection_title("The Punchline")

    pdf.blockquote(
        '"Let me recap what just happened. The Government Cloud document agent '
        "started at 3 out of 10. The worst performer in our entire evaluation "
        "of 21 agents. Worse than M365 Copilot. Four steps later, it is at 9 "
        "out of 10, surpassing the Commercial agent that has access to a better "
        'model."'
    )

    pdf.blockquote(
        '"Cross-reference headers on both cases. Metadata tags on one document. '
        "That is the entire engineering investment. A paralegal could do this in "
        'an afternoon."'
    )

    pdf.blockquote(
        '"Zero code. Zero model changes. Zero Copilot Studio configuration changes. '
        "These improvements compound across every document agent in the organization "
        'that uses the same library."'
    )

    pdf.body_text(
        "Let this land. Then transition back to Act 4 (human review thread) "
        "or skip directly to Act 5.",
        bold_lead="Pause."
    )

    summary_headers = ["Step", "Change", "Score", "Effort"]
    summary_widths = [12, 70, 48, 40]
    summary_rows = [
        ["1", "Original documents (baseline)", "3/10", "n/a"],
        ["2", "Cross-reference headers on Case 1 documents", "3/10 to 7/10", "1-2 hours"],
        ["3", "SharePoint metadata tags on Medical Records", "7/10 to 8/10", "10 minutes"],
        ["4", "Cross-reference headers on Case 2 documents", "8/10 to 9/10", "1 hour"],
    ]
    pdf.styled_table(summary_headers, summary_rows, summary_widths, font_size=8)

    pdf.ln(4)
    pdf.callout_box(
        "Key Takeaway for GCC Customers",
        "Document hygiene is the highest-ROI investment for Government Cloud "
        "document agents. Cross-reference headers and metadata tags require no "
        "code, no model upgrade, and no platform configuration. The GCC agent "
        "surpassed Commercial with document improvements alone.",
        height=26
    )

    # -- Act 5: What This Means --
    pdf.add_page()
    pdf.subsection_title("Act 5: What This Means for Your Agency (3 minutes, no typing)")

    pdf.blockquote('"Let me bring it back to your decisions."')

    pdf.blockquote(
        '"Levels 1 and 2: Deploy now. Point Copilot at your SharePoint libraries. '
        "You'll get 80 percent accuracy with zero custom engineering. That's a "
        'real productivity gain."'
    )

    pdf.blockquote(
        '"Level 3: Connect to your structured data. Case management systems, '
        "property databases, HR records. Model Context Protocol makes this "
        "straightforward -- the AI auto-discovers what data is available.\""
    )

    pdf.blockquote(
        '"Level 4: This is where you need an engineering partner. Purpose-built '
        "tools, fuzzy matching, entity resolution, iterative testing against "
        "ground truth. One missing tool caused 87 percent of our failures. "
        "Adding it back produced the single largest improvement in the entire "
        'evaluation."'
    )

    pdf.blockquote(
        '"Level 5: Everything from Level 4, plus governance. Audit logging. '
        "Citation linking. Human review workflows. The AI accelerates the "
        'attorney -- it does not replace the attorney."'
    )

    pdf.body_text('The "So what?" close:', bold_lead='The "So what?" close:')

    pdf.blockquote(
        '"So what do we do? Do we just give up on using agents?"'
    )

    pdf.blockquote(
        '"No. You continue to test them and make them better. And you always '
        'adhere to trust but verify."'
    )

    pdf.blockquote(
        '"In my world, I have agents building apps for me right now. I\'m not '
        "building production enterprise applications anymore, but if I were, I "
        "would have a team of human developers involved in the process -- checking "
        "the work my agents are producing with my guidance, helping to test, "
        "reviewing agentic test results. That's the operating model. The AI "
        'accelerates the team. The team validates the AI."'
    )

    pdf.blockquote(
        '"The question isn\'t \'should we deploy AI?\' The question is \'which level '
        "are we operating at, and have we invested accordingly?'\""
    )

    # ====================================================================
    # THE ITERATIVE PROCESS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("The Iterative Process")

    pdf.body_text(
        "A key narrative thread: deploying an agent is not a one-time event. "
        "Our evaluation went through seven testing rounds and four improvement "
        "rounds. This section gives you the talking points for that journey."
    )

    pdf.subsection_title("The Four Rounds")

    pdf.bullet(
        "Baseline testing -- measure failures against ground truth. "
        "Measure failures against ground truth. This project tested 11 + 8 "
        "agent configurations across 10 prompts each (190 baseline test runs). "
        "Most agents scored 3-8 out of 10.",
        bold_lead="Round 0:"
    )
    pdf.bullet(
        "Fix the data -- make facts discrete and queryable. Added 11 SQL rows "
        "and 1 tool filter. Biggest change: individual drug test results as "
        "separate timeline events instead of buried in a paragraph.",
        bold_lead="Round 1:"
    )
    pdf.bullet(
        "Fix the tools -- help the model reach the data. Added a fuzzy "
        "address search tool (fixed 87% failure rate), entity network summary "
        "mode, improved tool descriptions and system prompt.",
        bold_lead="Round 2:"
    )
    pdf.bullet(
        "Validate across models -- confirmed GPT-4.1 and GPT-5 Auto produce "
        "identical results. The gap is GPT-4o versus everything above it.",
        bold_lead="Round 3:"
    )

    pdf.subsection_title("Improvement Results")

    iter_headers = ["Agent", "Round 1", "Final", "Rounds"]
    iter_widths = [60, 28, 28, 54]
    iter_rows = [
        ["Commercial MCP (Copilot Studio)", "8/10", "10/10", "2"],
        ["Investigative Agent (OpenAI SDK)", "1/10", "10/10", "2"],
        ["Foundry Agent (AI Foundry)", "4/10", "9/10", "2"],
        ["Triage Agent (Semantic Kernel)", "0/10", "10/10", "5"],
    ]
    pdf.styled_table(iter_headers, iter_rows, iter_widths, font_size=8)

    pdf.ln(4)
    pdf.subsection_title("Document Agent Improvement (Zero Code)")

    pdf.body_text(
        "Added cross-reference headers to each document -- standard legal case "
        "file practice. Each document now lists the other case file documents and "
        "what they contain. Same words, same facts. Just better organized."
    )

    doc_imp_headers = ["Agent", "Before", "After", "Change"]
    doc_imp_widths = [60, 28, 28, 54]
    doc_imp_rows = [
        ["Commercial doc agent", "8/10", "10/10", "Cross-ref headers"],
        ["GCC SP/PDF agent", "3/10", "9/10", "Cross-ref headers + metadata tags"],
    ]
    pdf.styled_table(doc_imp_headers, doc_imp_rows, doc_imp_widths, font_size=8)

    pdf.ln(4)
    pdf.body_text(
        "The pattern for organizations: ground truth first, then data, then tools, "
        "then documents, then model validation. Budget 3+ rounds for Level 4 use cases.",
        bold_lead="The pattern:"
    )

    # ====================================================================
    # TIMING GUIDE
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Timing Guide (50-60 Minutes)")

    timing_headers = ["Section", "Duration", "Running Total"]
    timing_widths = [100, 35, 35]
    timing_rows = [
        ["Opening: Hook + Framework", "4-5 min", "5 min"],
        ["Act 1: Level 2 Summarization", "3-4 min", "8 min"],
        ["Act 2: Level 3 Aggregation (DSS + Philly)", "4-5 min", "13 min"],
        ["Act 3: Level 4 Investigation (Money Prompt)", "8-10 min", "23 min"],
        ["Act 3b: Side-by-Side Comparison", "5-7 min", "30 min"],
        ["Act 3c: Use Case 2 (Philly Properties)", "5-7 min", "37 min"],
        ["Act 4: Level 5 Trust But Verify", "3-4 min", "41 min"],
        ["Act 4b: Document Improvement Walkthrough", "5-7 min", "48 min"],
        ["Act 5: Code Spectrum + GCC Guidance", "5-7 min", "55 min"],
        ["Q&A", "10-15 min", "65-70 min"],
    ]
    pdf.styled_table(timing_headers, timing_rows, timing_widths, font_size=8)

    pdf.ln(4)
    pdf.subsection_title("Expanded Sections for 50-60 Minutes")

    pdf.body_text(
        'Show aggregate queries on BOTH use cases. After "How many active cases?", '
        'switch to Philly: "How many properties does GEENA LLC own?" Shows Level 3 '
        "works across domains with live structured data.",
        bold_lead="Act 2 (expanded):"
    )

    pdf.body_text(
        "Run the money prompt on the SharePoint agent in a separate tab. Walk "
        "through what's missing, what's wrong, and what's different. Use 2-3 of "
        "the discrepancy questions from Appendix C. This is where the "
        '"structured data vs documents" argument becomes visceral.',
        bold_lead="Act 3b: Side-by-Side Comparison (new section):"
    )

    pdf.body_text(
        "Switch to Philly property investigation. Show address resolution in action:",
        bold_lead="Act 3c: Use Case 2 (new section):"
    )

    pdf.code_block([
        "Tell me about the property at 4763 Griscom Street. Who owns it,",
        "what violations does it have, and what's the ownership history?"
    ])

    pdf.body_text("Then show the aggregate power:")

    pdf.code_block([
        "What are the top 5 addresses by code violation count,",
        "excluding government-owned properties?"
    ])

    pdf.body_text(
        'Talking point: "Same architecture, completely different domain. The tools '
        'are different but the pattern is identical."'
    )

    pdf.body_text(
        "If you show M365 Copilot, lean into the orchestration UX -- the confirmation "
        "dialog shows every tool call before it executes. This is actually a great "
        "demo asset for enterprise security conversations:",
        bold_lead="M365 Copilot (optional, time permitting):"
    )

    pdf.blockquote(
        '"Notice it\'s showing you exactly what it\'s about to do and asking for '
        "permission. This is the kind of transparency enterprise customers want. "
        'You can see the orchestration happening in real time."'
    )

    pdf.body_text(
        "Note: Confirmation can be disabled via admin pre-approval or "
        "x-openai-isConsequential: false in the manifest."
    )

    pdf.body_text(
        "Walk through the code spectrum slide (zero code to full code) and the "
        'GCC-specific guidance. This is where you land the services conversation: '
        '"Levels 1-3 are Copilot licenses you already own. Levels 4-5 are where '
        'we help."',
        bold_lead="Act 5 (expanded):"
    )

    pdf.body_text(
        "Skip Acts 1, 3b, 3c. Shorten Act 3 to just the money prompt result. "
        "Keep Act 4b (document improvement walkthrough). Skip Act 5 code spectrum.",
        bold_lead="Compressed (25 min):"
    )

    pdf.body_text(
        "Skip Act 3c (Philly). Shorten side-by-side to one comparison prompt. "
        "Keep full Act 4b walkthrough.",
        bold_lead="Standard (40 min):"
    )

    # ====================================================================
    # HANDLING Q&A
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Handling Q&A")

    pdf.body_text('"Is this real data?"', bold_lead='"Is this real data?"')
    pdf.blockquote(
        "No. All 50 DSS cases are completely synthetic. The Philadelphia property "
        "data is real public records (34 million rows) but contains no personally "
        "identifiable information. We tested on both synthetic and real data -- "
        "real data is harder."
    )

    pdf.body_text('"How long did this take to build?"', bold_lead='"How long did this take to build?"')
    pdf.blockquote(
        "The structured database, API layer, MCP server, and web interface were "
        "built in a single session. The iterative testing and tool improvements "
        "took 7 rounds. The key insight: structuring the data is the hard part. "
        "Once it's structured, the AI layer is straightforward."
    )

    pdf.body_text('"Can this work with our case management system?"',
                  bold_lead='"Can this work with our case management system?"')
    pdf.blockquote(
        "Yes. Same pattern regardless of where data lives. If your system has an "
        "API or database, we connect MCP tools to that instead of this demo "
        "database. The agent auto-discovers whatever tools are available."
    )

    pdf.body_text('"What about security?"', bold_lead='"What about security?"')
    pdf.blockquote(
        "Azure AD authentication, managed identity for all service-to-service auth, "
        "AI model hosted in your Azure tenant, no data leaves your tenant. At "
        "Level 5, add audit logging of every tool call and human review gates."
    )

    pdf.body_text('"Can the agent make mistakes?"', bold_lead='"Can the agent make mistakes?"')
    pdf.blockquote(
        "Yes -- and we documented exactly how. [Show the danger taxonomy.] The "
        "structured data agent won't hallucinate facts that aren't in the database, "
        "but it can miss data it retrieves (false negative), attribute facts to the "
        "wrong person (misattribution), or faithfully reproduce errors from source "
        "documents."
    )

    pdf.body_text('"What about Government Cloud?"', bold_lead='"What about Government Cloud?"')
    pdf.blockquote(
        "Government Cloud Copilot Studio currently defaults to GPT-4o, which "
        "scored 4 out of 10 on investigative queries in our testing. For Levels 1 "
        "through 3, GPT-4o is adequate. For Levels 4 and 5, deploy pro-code agents "
        "using Azure OpenAI GPT-4.1 directly. When Government Cloud upgrades to a "
        "a model with stronger multi-step reasoning, Copilot Studio agents will benefit immediately."
    )

    # ====================================================================
    # APPENDIX A: DATA DESIGN DECISION
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Appendix A: Data Design Decision")

    pdf.subsection_title('"How did the data get from documents into the database?"')

    pdf.body_text(
        "The data was never extracted from documents. Structured SQL data was "
        "designed first, then realistic legal documents were written from that "
        "data for the SharePoint comparison.",
        bold_lead="The short answer:"
    )

    pdf.body_text("How to frame it:", bold_lead="How to frame it:")

    pdf.blockquote(
        '"This is what digitization looks like. Your agency already has this '
        "information -- it's in Word documents, PDFs, case files scattered across "
        "SharePoint. What we did is model that same information as structured data: "
        "timelines, statements, people, discrepancies. The MCP agent queries the "
        "database; the SharePoint agent searches the filing cabinet. Same facts, "
        'dramatically different precision."'
    )

    pdf.body_text(
        "You do not need to explain which came first. The audience cares about "
        "the outcome: structured data enables precise queries, cross-referencing, "
        "and aggregation that document search cannot match."
    )

    pdf.subsection_title("The data engineering story (if asked about the process)")

    pdf.blockquote(
        '"I took a very first cut at chunking up the data -- deciding what a '
        "'timeline event' is, what a 'statement' is, what a 'discrepancy' looks "
        "like as structured fields. Then I used an AI coding agent to generate "
        "additional cases and refine the schema. Two hand-crafted cases became 50, "
        'with increasing detail at every round."'
    )

    pdf.blockquote(
        '"This is the part people underestimate. The AI layer on top is '
        "straightforward once you've done the data engineering. Deciding what to "
        "extract, how to schema it, what granularity matters -- that's the "
        'investment that separates Level 3-4 from Level 1-2."'
    )

    # ====================================================================
    # APPENDIX B: AGENT ARCHITECTURE MATRIX
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Appendix B: Agent Architecture Matrix")

    pdf.body_text(
        "Every agent hits the same backend (APIM to Functions to SQL). The only "
        "variables are who runs the orchestration, how much code you write, and "
        "which model reasons over the results."
    )

    arch_headers = ["Agent", "Orchestration", "Code Required", "Data Path", "Model"]
    arch_widths = [32, 26, 26, 50, 36]
    arch_rows = [
        ["Custom Web SPA", "MCP Server /chat", "Full (TypeScript)",
         "MCP to APIM to Functions to SQL", "GPT-4.1"],
        ["Copilot Studio MCP", "Copilot Studio", "Zero",
         "MCP to APIM to Functions to SQL", "GPT-4o (GCC) / GPT-4.1 (Com)"],
        ["M365 Copilot (Com)", "M365 platform", "Zero (3 JSON files)",
         "MCP to APIM to Functions to SQL", "Platform-assigned"],
        ["Foundry Agent", "AI Agent Service", "Minimal",
         "MCP to APIM to Functions to SQL", "GPT-4.1"],
        ["Investigative Agent", "OpenAI SDK", "Full (TypeScript)",
         "Direct to APIM to Func to SQL", "GPT-4.1"],
        ["Triage Agent", "Semantic Kernel", "Full (C#)",
         "Direct to APIM to Func to SQL", "GPT-4.1"],
        ["Copilot Studio SP/PDF", "Built-in RAG", "Zero",
         "SharePoint docs", "GPT-4o (GCC) / GPT-4.1 (Com)"],
    ]
    pdf.styled_table(arch_headers, arch_rows, arch_widths, font_size=6.5, row_height=7)

    pdf.ln(4)
    pdf.body_text(
        "Every architecture scored 9 to 10 out of 10 with GPT-4.1. The engineering "
        "investment buys customization and governance, not accuracy, which comes "
        "from the model and data. Exception: M365 Copilot Commercial (platform-assigned "
        "model) scored 2 out of 10 -- model selection matters as much as architecture.",
        bold_lead="Key insight:"
    )

    # ====================================================================
    # APPENDIX C: FIVE DISCREPANCY QUESTIONS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Appendix C: Five Discrepancy Questions")

    pdf.body_text(
        "These questions are grounded in the actual seed data and SharePoint "
        "documents. They expose cross-document conflicts that document agents "
        "are likely to mishandle."
    )

    pdf.body_text("Recommended demo order:", bold_lead="Recommended demo order:")

    # Question 1
    pdf.subsection_title("1. Crystal's sobriety (easy to understand, clear contradiction)")

    pdf.code_block([
        'Crystal Price told the court she was "clean now" at the November',
        "2023 hearing. What do the drug test results show?"
    ])

    pdf.body_text(
        'Crystal\'s statement: "I am clean now" (November 14, 2023). Drug screens: '
        "two positive fentanyl screens on October 8 and October 22 -- three weeks "
        "earlier. Also missed screens on December 5, January 15, and March 3."
    )

    # Question 2
    pdf.subsection_title("2. Transportation excuse (builds the credibility pattern)")

    pdf.code_block([
        "Crystal Price said she couldn't comply with the treatment plan",
        "because she lacked transportation. What support did DSS actually provide?"
    ])

    pdf.body_text(
        "Crystal claims: lack of transportation and support. DSS records show: "
        "monthly bus passes issued, three housing referrals provided, IOP "
        "transportation assistance offered and declined by Crystal."
    )

    # Question 3
    pdf.subsection_title("3. Marcus bedtime discrepancy (subtle cross-referencing)")

    pdf.code_block([
        "What did Marcus Webb tell hospital staff about when he put Jaylen",
        "to bed, and did he give the same answer to law enforcement?"
    ])

    pdf.body_text(
        'Nursing notes (Medical Records p. 8): Marcus told hospital staff "around '
        'ten." Sheriff Report (p. 3): Marcus told Lt. Odom approximately 8:00 PM. '
        "Two-hour discrepancy."
    )

    # Question 4
    pdf.subsection_title("4. Skeletal survey (the cross-document bombshell)")

    pdf.code_block([
        "Did the Sheriff's Office investigation find fractures in Jaylen Webb's",
        "skeletal survey?"
    ])

    pdf.body_text(
        'Sheriff Report (p. 2): "no fractures detected on skeletal survey." '
        "Medical Records (pp. 3-4): bilateral long bone fractures with extensive "
        "radiological findings. Direct factual conflict between two documents "
        "about the same hospital visit."
    )

    pdf.body_text(
        "With original documents, the Commercial agent failed completely (retrieved "
        "the wrong case on one prompt, returned 'no information found' on the "
        "targeted skeletal survey prompt despite five attempts). With cross-referenced "
        "documents (same content, added case file cross-reference headers), the agent "
        "pulled Medical Records as the primary source and delivered detailed fracture "
        "findings with healing timelines. The Government Cloud agent improved even "
        "more dramatically: from 3 out of 10 to 9 out of 10 across all 10 prompts "
        "using cross-reference headers and metadata tags. Zero code, same model, "
        "same platform.",
        bold_lead="Document improvement A/B result:"
    )

    # Question 5
    pdf.subsection_title("5. ER arrival time and nurse (reinforces document unreliability)")

    pdf.code_block([
        "What time was Jaylen Webb brought to the emergency room, and who",
        "was the admitting nurse?"
    ])

    pdf.body_text(
        "Medical Records: arrival at 03:15 AM, nurse Rebecca Torres. Sheriff "
        "Report: arrival at approximately 0047 hours (12:47 AM), nurse Charge "
        "Nurse Patricia Daniels. Two conflicting versions of the same event."
    )

    # ====================================================================
    # APPENDIX D: COPILOT STUDIO VALUE PROP
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Appendix D: Copilot Studio Value Prop (Tech Series)")

    pdf.body_text(
        "When presenting to a technical audience, you MUST articulate why Copilot "
        "Studio matters in this story. This is not a \"pick your own adventure\" -- "
        "Copilot Studio is the platform that ties it together."
    )

    pdf.body_text("Key points to land:", bold_lead="Key points to land:")

    pdf.bullet(
        "The same Copilot Studio environment hosts the zero-code SharePoint agent "
        "(Level 1-2) and the MCP-connected structured data agent (Level 3-4). One "
        "governance boundary, one admin console, one DLP policy set.",
        bold_lead="1. Single platform for declarative AND pro-code agents."
    )

    pdf.bullet(
        "Same Copilot Studio agent, swap GPT-4o for GPT-4.1, and accuracy goes "
        "from 4/10 to 10/10 without changing a single line of configuration. "
        "That's a platform story, not a coding story. When GCC gets a better "
        "model, every Copilot Studio agent improves overnight.",
        bold_lead="2. Model flexibility is the headline."
    )

    pdf.bullet(
        "DLP policies, audit logging, admin pre-approval for tool calls, the M365 "
        "Copilot confirmation UX. These are not things you bolt on later -- they "
        "come with the platform.",
        bold_lead="3. Enterprise governance is built in."
    )

    pdf.bullet(
        "Agents show up where users already work: Teams, Copilot chat, SharePoint. "
        "No separate app to deploy or URL to bookmark. For Level 1-3 use cases, "
        "this is the fastest path to adoption.",
        bold_lead="4. M365 distribution."
    )

    pdf.bullet(
        "Our evaluation shows the platform works -- the limiting factor is the "
        "model, not the platform. Commercial Copilot Studio MCP scored a perfect "
        "10/10 with GPT-4.1. The architecture is sound.",
        bold_lead="5. The test data proves it."
    )

    pdf.ln(2)
    pdf.body_text("The services hook:", bold_lead="The services hook:")

    pdf.blockquote(
        '"Levels 1-3 are Copilot licenses you already own. Levels 4-5 are where '
        "purpose-built tools and iterative testing come in -- and where we can "
        'help."'
    )

    # ====================================================================
    # APPENDIX E: WHAT NOT TO SAY
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Appendix E: What Not to Say")

    pdf.bullet(
        'The message is "different tools for different jobs."',
        bold_lead="Do not bash SharePoint."
    )
    pdf.bullet(
        "SharePoint is great for unstructured narratives, policy documents, and "
        "memos (Levels 1-2)."
    )
    pdf.bullet(
        "When case data needs cross-referencing and precision (Levels 4-5), "
        "structured data with MCP delivers what document search cannot."
    )
    pdf.bullet(
        "Do not promise Government Cloud will get GPT-4.1 on a specific date."
    )
    pdf.bullet(
        "Do not suggest the AI replaces human judgment at Level 5. The agent "
        "accelerates the human."
    )

    # ====================================================================
    # OUTPUT
    # ====================================================================
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "pdf")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "demo-guide.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()
