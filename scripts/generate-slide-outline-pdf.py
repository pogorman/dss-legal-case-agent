"""
Generate a slide-outline PDF from the 21-slide presentation outline.
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
        self.cell(0, 6, sanitize_text("Agent Accuracy Spectrum for Copilot Studio -- Slide Outline"), align="L")
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
        y_start = self.get_y()
        bar_x = x + 4
        text_x = x + 8
        text_w = self.w - self.r_margin - text_x

        # Render the text first to determine height
        self.set_xy(text_x, y_start)
        self.set_font("Helvetica", "I", 8.5)
        self.set_text_color(*MED)

        # Use multi_cell to render and capture the end Y
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
    pdf.cell(0, 14, "Agent Accuracy Spectrum", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 14, "for Copilot Studio", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(180, 200, 220)
    pdf.cell(0, 10, "Slide Outline", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(65)
    pdf.set_draw_color(80, 140, 200)
    pdf.set_line_width(0.4)
    pdf.line(pdf.w * 0.3, pdf.get_y(), pdf.w * 0.7, pdf.get_y())
    pdf.set_line_width(0.2)

    pdf.set_y(75)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 7, "21 Slides  |  March 2026", align="C", new_x="LMARGIN", new_y="NEXT")

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
        "Target: 21 slides, 50-60 minutes (40-45 min presentation + live demo + 10-15 min Q&A)"
    ), align="C")

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 7, sanitize_text("313 test runs  |  19 agents  |  21 slides  |  2 use cases"),
             align="C", new_x="LMARGIN", new_y="NEXT")

    # ====================================================================
    # SLIDE 1: Title
    # ====================================================================
    pdf.add_page()
    pdf.slide_heading(1, "Title")

    pdf.headline("AI Agent Accuracy for Government: A Five-Level Framework")

    pdf.body_text(
        "Subtitle: Findings from 313 Test Runs Across 19 Agent Configurations"
    )

    pdf.visual_note("Clean title slide with agency-appropriate branding")

    pdf.speaker_note(
        "Some of you may remember me from such demos as the delegation demo, or "
        "[insert another]. Those demos and this one have something in common: I like "
        "to build test harnesses for real-world use cases my customers care about. "
        "And both this demo and the delegation demo deal with the same fundamental "
        "topic: accuracy."
    )

    # ====================================================================
    # SLIDE 2: The Question
    # ====================================================================
    pdf.slide_heading(2, "The Question")

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
        "What this demo is: a process and methods -- with real-world examples -- for "
        "making your agents better. What it isn't: a data extraction demo, other than "
        "to show ideas on tools and process when extraction is necessary. You'll "
        "probably have more questions than answers when we're done. Let's get into it."
    )

    # ====================================================================
    # SLIDE 3: The Five Levels (Overview)
    # ====================================================================
    pdf.slide_heading(3, "The Five Levels (Overview)")

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
    pdf.slide_heading(4, "Levels 1-2 -- The Quick Win")

    pdf.headline("Document agents score 8 out of 10 with zero engineering")

    pdf.bullet("Point Copilot at your SharePoint library")
    pdf.bullet("No custom code, no databases, no tool design")
    pdf.bullet("Model choice barely matters at this level")
    pdf.bullet("Good enough for policy lookup, report summarization, meeting notes")

    pdf.visual_note("Simple diagram: Copilot -> SharePoint -> Answer")

    pdf.talking_point("This is where most agencies should start. It works today.")

    # ====================================================================
    # SLIDE 5: Level 3 -- Structured Data Starts Winning
    # ====================================================================
    pdf.slide_heading(5, "Level 3 -- Structured Data Starts Winning")

    pdf.headline("Aggregate queries work across all agent types")

    pdf.bullet(
        '"How many active cases?" "What\'s the breakdown by county?" "Top 5 violators?"'
    )
    pdf.bullet(
        "Document agents cannot answer these -- they only have individual files"
    )
    pdf.bullet(
        "Model Context Protocol connects AI to live databases and APIs"
    )

    pdf.visual_note(
        'Side-by-side comparison. Document agent: "I don\'t have that information." '
        "MCP agent: table with counts."
    )

    pdf.talking_point("This is where you start investing in data structure.")

    # ====================================================================
    # SLIDE 6: Level 4 -- The Inflection Point
    # ====================================================================
    pdf.slide_heading(6, "Level 4 -- The Inflection Point")

    pdf.headline("This is where engineering decisions determine success or failure")

    pdf.body_text("Three gaps emerged in testing:")

    pdf.bullet("GPT-4.1 scores 9.5/10 vs GPT-4o at 4/10", bold_lead="The model gap:")
    pdf.bullet("One missing tool caused 87% failure rate", bold_lead="The tool gap:")
    pdf.bullet(
        "Facts buried in narrative text were invisible to agents",
        bold_lead="The data gap:"
    )

    pdf.visual_note("Three gap icons with before/after numbers")

    pdf.talking_point("Level 4 is where the investment pays off -- or doesn't.")

    # ====================================================================
    # SLIDE 7: The Model Gap (Detail)
    # ====================================================================
    pdf.slide_heading(7, "The Model Gap (Detail)")

    pdf.headline("GPT-4.1 vs GPT-4o: Same tools, same data, same backend")

    model_headers = ["Model", "Average Score"]
    model_widths = [85, 85]
    model_rows = [
        ["GPT-4.1", "9.5 out of 10"],
        ["GPT-4o (Government Cloud)", "4 out of 10"],
        ["Platform-assigned (M365 Copilot)", "2 out of 10"],
    ]
    pdf.styled_table(model_headers, model_rows, model_widths, font_size=8)

    pdf.ln(2)
    pdf.bullet("Government Cloud Copilot Studio is locked to GPT-4o today")
    pdf.bullet("No amount of prompt engineering closed this gap")
    pdf.bullet(
        "Pro-code agents can use GPT-4.1 in Government Cloud via Azure OpenAI directly"
    )

    pdf.visual_note("Bar chart with three bars showing dramatic gap")

    pdf.talking_point("The model is the single biggest variable at Level 4.")

    # ====================================================================
    # SLIDE 8: The Tool Gap (Detail)
    # ====================================================================
    pdf.slide_heading(8, "The Tool Gap (Detail)")

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
    pdf.slide_heading(9, "Level 5 -- Trust But Verify")

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

    pdf.ln(2)
    pdf.bullet(
        "Added cross-reference headers to each document (zero content changes)",
        bold_lead="Document improvement:"
    )
    pdf.bullet(
        "Commercial agent: 0/2 to 2/2 -- pulled Medical Records as primary source"
    )
    pdf.bullet(
        "GCC agent: vague single-source answer became detailed multi-source analysis"
    )
    pdf.bullet(
        "Zero code, zero engineering -- document hygiene that any paralegal can implement"
    )

    pdf.talking_point(
        "The good news: document structure improvements can fix retrieval failures "
        "without any custom engineering."
    )

    pdf.speaker_note(
        "Connect to daily experience: Copilot helps you draft an email -- you review it. "
        "Copilot helps you write code -- you review it. Why would we skip human review at "
        "any of these five levels, especially Level 5 where the stakes are a family's future?"
    )

    # ====================================================================
    # SLIDE 10: The Danger Taxonomy
    # ====================================================================
    pdf.slide_heading(10, "The Danger Taxonomy")

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
        "These are not hypothetical. We documented each one across 313 test runs."
    )

    # ====================================================================
    # SLIDE 11: The Iterative Process
    # ====================================================================
    pdf.slide_heading(11, "The Iterative Process")

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
    pdf.slide_heading(12, "Results After Iteration")

    pdf.headline(
        "Four agents reached 9-10 out of 10 after iterative improvement "
        "(three at perfect 10)"
    )

    iter_headers = ["Agent", "Round 1", "Final", "Rounds"]
    iter_widths = [60, 28, 28, 54]
    iter_rows = [
        ["Commercial MCP (Copilot Studio)", "8/10", "10/10", "2"],
        ["Investigative Agent (OpenAI SDK)", "1/10", "10/10", "2"],
        ["Foundry Agent", "4/10", "9/10", "2"],
        ["Triage Agent (Semantic Kernel)", "0/10", "10/10", "5"],
    ]
    pdf.styled_table(iter_headers, iter_rows, iter_widths, font_size=8)

    pdf.ln(2)
    pdf.visual_note("Improvement arc showing Round 1 baseline to final score")

    pdf.talking_point(
        "The Triage Agent took five rounds to reach a perfect score. "
        "The investment is real -- but so are the results."
    )

    # ====================================================================
    # SLIDE 13: The Code Spectrum
    # ====================================================================
    pdf.slide_heading(13, "The Code Spectrum")

    pdf.headline("Zero code to full code -- same accuracy with GPT-4.1")

    code_headers = ["Approach", "Code", "Best For"]
    code_widths = [60, 52, 58]
    code_rows = [
        ["M365 Copilot", "Zero (3 JSON manifests)", "Levels 1-2"],
        ["Copilot Studio", "Zero to low code", "Levels 1-3"],
        ["Foundry Agent", "Minimal code", "Levels 3-4"],
        ["Custom SDK (OpenAI, SK)", "Full code", "Levels 4-5"],
    ]
    pdf.styled_table(code_headers, code_rows, code_widths, font_size=8)

    pdf.ln(2)
    pdf.visual_note(
        "Horizontal spectrum from zero to full code with accuracy bars all at 9-10"
    )

    pdf.talking_point(
        "The investment buys governance and customization, not accuracy. "
        "Accuracy comes from the model and the data."
    )

    # ====================================================================
    # SLIDE 14: Why Copilot Studio (Tech Series)
    # ====================================================================
    pdf.slide_heading(14, "Why Copilot Studio (Tech Series)")

    pdf.headline("One platform, declarative to pro-code")

    pdf.bullet(
        "Same environment hosts zero-code SharePoint agents AND MCP-connected "
        "structured data agents"
    )
    pdf.bullet(
        "Model flexibility: swap GPT-4o for GPT-4.1, accuracy goes from 4/10 to "
        "10/10 -- no config changes"
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
        "Commercial Copilot Studio MCP scored a perfect 10 out of 10. The architecture "
        "is sound. The limiting factor is model availability in GCC."
    )

    pdf.speaker_note(
        "This slide is critical for the tech series. MUST articulate the platform value, "
        "not just the results."
    )

    # ====================================================================
    # SLIDE 15: What to Do at Each Level
    # ====================================================================
    pdf.slide_heading(15, "What to Do at Each Level")

    action_headers = ["Level", "Action"]
    action_widths = [20, 150]
    action_rows = [
        ["1-2", "Deploy Copilot with SharePoint. Clean up document metadata. Done."],
        ["3", "Connect to structured data via MCP. Clear tool descriptions. Summary modes."],
        ["4", "Purpose-built tools. GPT-4.1 minimum. Ground truth test suite. Budget 3+ rounds."],
        ["5", "Level 4 + human review workflows + audit logging + citation linking."],
    ]
    pdf.styled_table(action_headers, action_rows, action_widths, font_size=8)

    pdf.ln(2)
    pdf.visual_note(
        "Checklist format, one row per level, with investment increasing rightward"
    )

    pdf.talking_point("Match your investment to your accuracy requirement.")

    # ====================================================================
    # SLIDE 16: Government Cloud Customers
    # ====================================================================
    pdf.slide_heading(16, "Government Cloud Customers")

    pdf.headline("The GCC reality today")

    pdf.bullet("Copilot Studio locked to GPT-4o (adequate for Levels 1-3)")
    pdf.bullet("Pro-code agents can use GPT-4.1 via Azure OpenAI (Levels 4-5)")
    pdf.bullet("Monitor model updates -- GCC parity will improve over time")

    pdf.ln(2)
    pdf.body_text("Decision tree:", bold_lead=None)

    pdf.bullet(
        "Use Copilot Studio today.",
        bold_lead="Is your use case Level 1-3?"
    )
    pdf.bullet(
        "Deploy a pro-code agent with GPT-4.1.",
        bold_lead="Is your use case Level 4-5?"
    )
    pdf.bullet(
        "Start building ground truth test suites now.",
        bold_lead="Are you planning for Level 4-5 in the future?"
    )

    pdf.visual_note("Decision tree flowchart")

    pdf.talking_point("Know what works today. Plan for what's coming.")

    # ====================================================================
    # SLIDE 17: Live Demo Title Card
    # ====================================================================
    pdf.slide_heading(17, "Live Demo Title Card")

    pdf.headline('"Let me show you the difference between Level 2 and Level 4."')

    pdf.body_text("[Switch to live demo -- follow the presenter guide]")

    pdf.bullet("Level 2: SharePoint document summarization (2 min)")
    pdf.bullet('Level 3: "How many cases by type?" aggregate query (2 min)')
    pdf.bullet(
        "Level 4: The money prompt -- timeline, discrepancies, statements (5 min)"
    )
    pdf.bullet("Level 5: The skeletal survey question (3 min)")

    pdf.visual_note("Demo URL and case number reference")

    # ====================================================================
    # SLIDE 18: Surprising Finding -- Agent Challenged Its Own Premise
    # ====================================================================
    pdf.slide_heading(18, "Surprising Finding -- Agent Challenged Its Own Premise")

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
    pdf.slide_heading(19, "Surprising Finding -- False Negative")

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
    pdf.slide_heading(20, "The Bottom Line")

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
    # SLIDE 21: Next Steps
    # ====================================================================
    pdf.slide_heading(21, "Next Steps")

    pdf.headline("Start the conversation")

    pdf.bullet("Where do your use cases fall on the spectrum?")
    pdf.bullet("What data do you already have in structured form?")
    pdf.bullet("What's your risk tolerance for AI-generated output?")
    pdf.bullet(
        "Ready for a deeper dive? We have the architecture, the test data, and "
        "the framework."
    )

    pdf.visual_note("Contact information, QR code to summary PDF")

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
