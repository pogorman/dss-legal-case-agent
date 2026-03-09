"""
Generate PowerPoint deck from slide outline.
Output: decks/agent-accuracy-spectrum.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

# ── Colors ──────────────────────────────────────────────────────────────
DARK_NAVY = RGBColor(0x1B, 0x2A, 0x4A)
MEDIUM_BLUE = RGBColor(0x2C, 0x5F, 0x8A)
ACCENT_BLUE = RGBColor(0x35, 0x7A, 0xBD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF2)
DARK_TEXT = RGBColor(0x2D, 0x2D, 0x2D)
MEDIUM_TEXT = RGBColor(0x55, 0x55, 0x55)
TABLE_HEADER_BG = RGBColor(0x2C, 0x5F, 0x8A)
TABLE_ALT_BG = RGBColor(0xE8, 0xF0, 0xF8)

# Level colors (green to red spectrum)
L1_GREEN = RGBColor(0x4C, 0xAF, 0x50)
L2_LIME = RGBColor(0x8B, 0xC3, 0x4A)
L3_ORANGE = RGBColor(0xFF, 0x98, 0x00)
L4_DEEP_ORANGE = RGBColor(0xF4, 0x51, 0x1E)
L5_RED = RGBColor(0xE5, 0x39, 0x35)
LEVEL_COLORS = [L1_GREEN, L2_LIME, L3_ORANGE, L4_DEEP_ORANGE, L5_RED]

# Severity colors
SEV_CRITICAL = RGBColor(0xC6, 0x28, 0x28)
SEV_HIGH = RGBColor(0xE6, 0x5C, 0x00)
SEV_MEDIUM = RGBColor(0xF9, 0xA8, 0x25)


def new_prs():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def add_blank_slide(prs):
    layout = prs.slide_layouts[6]  # Blank
    return prs.slides.add_slide(layout)


def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_textbox(slide, left, top, width, height, text, font_size=18,
                bold=False, color=DARK_TEXT, alignment=PP_ALIGN.LEFT,
                font_name="Calibri"):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top),
                                     Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    return txBox


def add_bullet_list(slide, left, top, width, height, items, font_size=16,
                    color=DARK_TEXT, bold_leads=False, spacing=Pt(6)):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top),
                                     Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True

    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()

        p.space_after = spacing

        if bold_leads and ":" in item:
            # Split on first colon for bold lead
            lead, rest = item.split(":", 1)
            run1 = p.add_run()
            run1.text = lead + ":"
            run1.font.size = Pt(font_size)
            run1.font.bold = True
            run1.font.color.rgb = color
            run1.font.name = "Calibri"
            run2 = p.add_run()
            run2.text = rest
            run2.font.size = Pt(font_size)
            run2.font.bold = False
            run2.font.color.rgb = color
            run2.font.name = "Calibri"
        else:
            run = p.add_run()
            run.text = item
            run.font.size = Pt(font_size)
            run.font.color.rgb = color
            run.font.name = "Calibri"

        p.level = 0
    return txBox


def add_level_bar(slide, top=6.6):
    """Add the 5-level color bar at the bottom of a slide."""
    labels = ["L1: Discovery", "L2: Summarization", "L3: Operational",
              "L4: Investigative", "L5: Adjudicative"]
    bar_width = 2.2
    gap = 0.15
    total = 5 * bar_width + 4 * gap
    start_x = (13.333 - total) / 2

    for i in range(5):
        x = start_x + i * (bar_width + gap)
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x), Inches(top), Inches(bar_width), Inches(0.45)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = LEVEL_COLORS[i]
        shape.line.fill.background()
        tf = shape.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.text = labels[i]
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.CENTER


def add_table(slide, left, top, width, col_widths, headers, rows,
              font_size=14):
    """Add a styled table to the slide."""
    num_rows = len(rows) + 1
    num_cols = len(headers)
    table_shape = slide.shapes.add_table(
        num_rows, num_cols, Inches(left), Inches(top),
        Inches(width), Inches(0.45 * num_rows)
    )
    table = table_shape.table

    # Set column widths
    for i, w in enumerate(col_widths):
        table.columns[i].width = Inches(w)

    # Header row
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = TABLE_HEADER_BG
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(font_size)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.font.name = "Calibri"
            p.alignment = PP_ALIGN.CENTER
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    # Data rows
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.cell(r + 1, c)
            cell.text = str(val)
            if r % 2 == 1:
                cell.fill.solid()
                cell.fill.fore_color.rgb = TABLE_ALT_BG
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(font_size)
                p.font.color.rgb = DARK_TEXT
                p.font.name = "Calibri"
                p.alignment = PP_ALIGN.CENTER
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    return table_shape


def add_speaker_notes(slide, text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = text


def add_rect(slide, left, top, width, height, color):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_rounded_rect(slide, left, top, width, height, color):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_confidential_footer(slide):
    add_textbox(slide, 0.5, 7.05, 3, 0.35, "Confidential  |  March 2026",
                font_size=10, color=MEDIUM_TEXT)


# ── SLIDE BUILDERS ──────────────────────────────────────────────────────

def slide_01_title(prs):
    slide = add_blank_slide(prs)
    # Navy top half
    add_rect(slide, 0, 0, 13.333, 4.5, DARK_NAVY)
    # Title
    add_textbox(slide, 1.5, 0.8, 10.3, 1.5,
                "AI Agent Accuracy\nfor Government",
                font_size=44, bold=True, color=WHITE,
                alignment=PP_ALIGN.CENTER)
    # Subtitle line
    add_textbox(slide, 2.5, 2.6, 8.3, 0.6,
                "A Five-Level Framework",
                font_size=28, color=RGBColor(0xA0, 0xC4, 0xE8),
                alignment=PP_ALIGN.CENTER)
    # Findings line
    add_textbox(slide, 2, 3.3, 9.3, 0.5,
                "Findings from 313 Test Runs Across 19 Agent Configurations",
                font_size=16, color=RGBColor(0x88, 0xAA, 0xCC),
                alignment=PP_ALIGN.CENTER)
    # Slide count + date
    add_textbox(slide, 4, 4.8, 5.3, 0.5,
                "21 Slides  |  March 2026",
                font_size=16, color=MEDIUM_TEXT,
                alignment=PP_ALIGN.CENTER)
    # Level bar
    add_level_bar(slide, top=5.6)
    # Stats line
    add_textbox(slide, 2, 6.3, 9.3, 0.4,
                "313 test runs  |  19 agents  |  21 slides  |  2 use cases",
                font_size=14, bold=True, color=ACCENT_BLUE,
                alignment=PP_ALIGN.CENTER)
    add_speaker_notes(slide,
        "Some of you may remember me from such demos as the delegation demo. "
        "Those demos and this one have something in common: I like to build test "
        "harnesses for real-world use cases my customers care about. And both this "
        "demo and the delegation demo deal with the same fundamental topic: accuracy.")


def slide_02_the_question(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "The Question",
                font_size=32, bold=True, color=DARK_NAVY)
    # Accent bar
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    # Big quote
    add_textbox(slide, 1.5, 1.6, 10.3, 1.0,
                '"Not all AI use cases are created equal."',
                font_size=28, bold=True, color=DARK_NAVY,
                alignment=PP_ALIGN.CENTER)

    add_bullet_list(slide, 1.5, 2.8, 10.3, 2.5, [
        "Your policy lookup chatbot and your legal case preparation tool have "
        "fundamentally different accuracy requirements",
        "This framework helps you decide where to deploy aggressively, where to "
        "add guardrails, and where human review is non-negotiable",
    ], font_size=18, color=DARK_TEXT)

    # Arrow visual: Low Stakes -> High Stakes
    add_rect(slide, 1.5, 5.0, 10.3, 0.08, RGBColor(0xDD, 0xDD, 0xDD))
    # Gradient dots
    for i, c in enumerate(LEVEL_COLORS):
        x = 1.5 + i * 2.58
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(x + 0.95), Inches(4.75), Inches(0.5), Inches(0.5))
        dot.fill.solid()
        dot.fill.fore_color.rgb = c
        dot.line.fill.background()
    add_textbox(slide, 1.5, 5.2, 3, 0.4, "Low Stakes",
                font_size=14, color=L1_GREEN, alignment=PP_ALIGN.LEFT)
    add_textbox(slide, 8.8, 5.2, 3, 0.4, "High Stakes",
                font_size=14, color=L5_RED, alignment=PP_ALIGN.RIGHT)

    add_level_bar(slide)
    add_confidential_footer(slide)
    add_speaker_notes(slide,
        "What this demo is: a process and methods -- with real-world examples -- for "
        "making your agents better. What it isn't: a data extraction demo, other than "
        "to show ideas on tools and process when extraction is necessary. You'll "
        "probably have more questions than answers when we're done. Let's get into it.")


def slide_03_five_levels(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "The Five Levels",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    headers = ["Level", "Name", "Stakes", "Example"]
    rows = [
        ["1", "Discovery", "Inconvenience", '"Find our leave policy"'],
        ["2", "Summarization", "Wasted time", '"Summarize this audit report"'],
        ["3", "Operational", "Misallocated resources", '"How many open cases by type?"'],
        ["4", "Investigative", "Missed evidence", '"Build a timeline from these records"'],
        ["5", "Adjudicative", "Wrong legal outcome", '"Prepare facts for this hearing"'],
    ]
    tbl = add_table(slide, 1.2, 1.6, 10.9, [1.0, 2.2, 3.0, 4.7], headers, rows, font_size=15)

    # Color the level number cells
    table = tbl.table
    for r in range(5):
        cell = table.cell(r + 1, 0)
        cell.fill.solid()
        cell.fill.fore_color.rgb = LEVEL_COLORS[r]
        for p in cell.text_frame.paragraphs:
            p.font.color.rgb = WHITE
            p.font.bold = True

    add_textbox(slide, 1.2, 5.3, 10.9, 0.5,
                'Where does your highest-priority use case fall?',
                font_size=18, bold=True, color=ACCENT_BLUE,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)


def slide_04_quick_win(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "Levels 1-2: The Quick Win",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.7,
                "Document agents score 8 out of 10 with zero engineering",
                font_size=24, bold=True, color=DARK_TEXT)

    add_bullet_list(slide, 1.2, 2.4, 10.9, 3.0, [
        "Point Copilot at your SharePoint library",
        "No custom code, no databases, no tool design",
        "Model choice barely matters at this level",
        "Good enough for policy lookup, report summarization, meeting notes",
    ], font_size=18)

    # Simple flow diagram: Copilot -> SharePoint -> Answer
    boxes = [("Copilot", 3.0), ("SharePoint", 5.8), ("Answer", 8.6)]
    for label, x in boxes:
        shape = add_rounded_rect(slide, x, 4.6, 2.0, 0.8, ACCENT_BLUE)
        tf = shape.text_frame
        p = tf.paragraphs[0]
        p.text = label
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.CENTER
    # Arrows between boxes
    for x in [5.05, 7.85]:
        add_textbox(slide, x, 4.65, 0.7, 0.8, ">",
                    font_size=28, bold=True, color=ACCENT_BLUE,
                    alignment=PP_ALIGN.CENTER)

    add_textbox(slide, 1.2, 5.8, 10.9, 0.5,
                "This is where most agencies should start. It works today.",
                font_size=16, bold=True, color=MEDIUM_TEXT,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)


def slide_05_level3(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "Level 3: Structured Data Starts Winning",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.7,
                "Aggregate queries work across all agent types",
                font_size=24, bold=True, color=DARK_TEXT)

    add_bullet_list(slide, 1.2, 2.4, 10.9, 1.8, [
        '"How many active cases?" "What\'s the breakdown by county?" "Top 5 violators?"',
        "Document agents cannot answer these -- they only have individual files",
        "Agents with structured data access start outperforming document agents here",
    ], font_size=18)

    # Side-by-side comparison boxes
    # Doc agent box
    box_l = add_rounded_rect(slide, 1.5, 4.2, 4.8, 1.8, RGBColor(0xFF, 0xEB, 0xEE))
    add_textbox(slide, 1.7, 4.25, 4.4, 0.4, "Document Agent", font_size=14,
                bold=True, color=L5_RED)
    add_textbox(slide, 1.7, 4.7, 4.4, 1.0,
                '"I don\'t have that information."',
                font_size=16, color=MEDIUM_TEXT, alignment=PP_ALIGN.CENTER)

    # MCP agent box
    box_r = add_rounded_rect(slide, 7.0, 4.2, 4.8, 1.8, RGBColor(0xE8, 0xF5, 0xE9))
    add_textbox(slide, 7.2, 4.25, 4.4, 0.4, "MCP Agent", font_size=14,
                bold=True, color=L1_GREEN)
    # Mini table text
    add_textbox(slide, 7.2, 4.7, 4.4, 1.0,
                "CPS: 18 cases\nTPR: 12 cases\nGuardianship: 8 cases",
                font_size=14, color=DARK_TEXT, alignment=PP_ALIGN.CENTER)

    add_textbox(slide, 1.2, 6.2, 10.9, 0.4,
                "This is where you start investing in data structure.",
                font_size=16, bold=True, color=MEDIUM_TEXT,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)


def slide_06_inflection(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "Level 4: The Inflection Point",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.7,
                "This is where engineering decisions determine success or failure",
                font_size=22, bold=True, color=DARK_TEXT)

    add_textbox(slide, 1.2, 2.3, 10.9, 0.5,
                "Three gaps emerged in testing:",
                font_size=18, color=DARK_TEXT)

    # Three gap cards
    gaps = [
        ("The Model Gap", "GPT-4.1 scores 9.5/10\nvs GPT-4o at 4/10", L4_DEEP_ORANGE),
        ("The Tool Gap", "One missing tool caused\n87% failure rate", L3_ORANGE),
        ("The Data Gap", "Facts buried in narrative\ntext were invisible", MEDIUM_BLUE),
    ]
    for i, (title, desc, color) in enumerate(gaps):
        x = 1.5 + i * 3.8
        box = add_rounded_rect(slide, x, 3.0, 3.3, 2.5, color)
        add_textbox(slide, x + 0.2, 3.1, 2.9, 0.6, title,
                    font_size=20, bold=True, color=WHITE,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, x + 0.2, 3.8, 2.9, 1.5, desc,
                    font_size=16, color=WHITE,
                    alignment=PP_ALIGN.CENTER)

    add_textbox(slide, 1.2, 5.8, 10.9, 0.4,
                "Level 4 is where the investment pays off -- or doesn't.",
                font_size=16, bold=True, color=MEDIUM_TEXT,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)


def slide_07_model_gap(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "The Model Gap",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.5,
                "GPT-4.1 vs GPT-4o: Same tools, same data, same backend",
                font_size=20, bold=True, color=DARK_TEXT)

    # Bar chart visual (horizontal bars)
    models = [
        ("GPT-4.1", 9.5, L1_GREEN),
        ("GPT-4o (Government Cloud)", 4.0, L3_ORANGE),
        ("Platform-assigned (M365)", 2.0, L5_RED),
    ]
    for i, (label, score, color) in enumerate(models):
        y = 2.3 + i * 1.2
        # Label
        add_textbox(slide, 1.5, y, 4.5, 0.4, label, font_size=16,
                    color=DARK_TEXT, alignment=PP_ALIGN.RIGHT)
        # Bar
        bar_max_w = 5.5
        bar_w = bar_max_w * (score / 10.0)
        add_rounded_rect(slide, 6.2, y + 0.05, bar_w, 0.45, color)
        # Score label
        add_textbox(slide, 6.2 + bar_w + 0.1, y, 1.5, 0.5,
                    f"{score}/10", font_size=18, bold=True, color=color)

    add_bullet_list(slide, 1.5, 5.2, 10.3, 1.5, [
        "Government Cloud Copilot Studio is locked to GPT-4o today",
        "No amount of prompt engineering closed this gap",
        "Pro-code agents can use GPT-4.1 in Government Cloud via Azure OpenAI directly",
    ], font_size=16)

    add_level_bar(slide)
    add_confidential_footer(slide)
    add_speaker_notes(slide,
        "The model is the single biggest variable at Level 4.")


def slide_08_tool_gap(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "The Tool Gap",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.7,
                "87% failure rate from one missing tool",
                font_size=24, bold=True, color=DARK_TEXT)

    add_bullet_list(slide, 1.2, 2.4, 10.9, 2.0, [
        'Agents could not convert "4763 Griscom St" to a database parcel ID',
        "15 address lookups across 5 agents, only 2 succeeded",
        "One fuzzy-match tool added: zero failures in retesting",
        "Investigative Agent: 1 out of 10 to a perfect 10 out of 10",
    ], font_size=18)

    # Before/After visual
    # Before box
    add_rounded_rect(slide, 2.0, 4.6, 4.2, 1.6, RGBColor(0xFF, 0xEB, 0xEE))
    add_textbox(slide, 2.2, 4.65, 3.8, 0.4, "BEFORE", font_size=14,
                bold=True, color=L5_RED, alignment=PP_ALIGN.CENTER)
    add_textbox(slide, 2.2, 5.1, 3.8, 0.9,
                "13 of 15 lookups failed\n1/10 accuracy",
                font_size=18, color=L5_RED, alignment=PP_ALIGN.CENTER)

    # Arrow
    add_textbox(slide, 6.2, 4.9, 0.9, 0.8, ">",
                font_size=36, bold=True, color=ACCENT_BLUE,
                alignment=PP_ALIGN.CENTER)

    # After box
    add_rounded_rect(slide, 7.1, 4.6, 4.2, 1.6, RGBColor(0xE8, 0xF5, 0xE9))
    add_textbox(slide, 7.3, 4.65, 3.8, 0.4, "AFTER", font_size=14,
                bold=True, color=L1_GREEN, alignment=PP_ALIGN.CENTER)
    add_textbox(slide, 7.3, 5.1, 3.8, 0.9,
                "0 failures\n10/10 accuracy",
                font_size=18, color=L1_GREEN, alignment=PP_ALIGN.CENTER)

    # Highlight the change
    add_textbox(slide, 2.0, 6.3, 9.3, 0.4,
                "The change: one search_properties fuzzy-match tool",
                font_size=14, bold=True, color=ACCENT_BLUE,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)
    add_speaker_notes(slide,
        "Tool design is as important as model selection. Maybe more.")


def slide_09_level5(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "Level 5: Trust But Verify",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.5,
                "Even our best agent reproduced a dangerous error",
                font_size=22, bold=True, color=DARK_TEXT)

    # Split screen: Sheriff Report vs Medical Records
    # Left box
    add_rounded_rect(slide, 1.2, 2.3, 5.2, 2.0, RGBColor(0xFF, 0xEB, 0xEE))
    add_textbox(slide, 1.4, 2.35, 4.8, 0.35, "Sheriff's Report",
                font_size=14, bold=True, color=L5_RED, alignment=PP_ALIGN.CENTER)
    add_textbox(slide, 1.4, 2.8, 4.8, 1.2,
                '"no fractures detected\non skeletal survey"',
                font_size=18, color=DARK_TEXT, alignment=PP_ALIGN.CENTER)

    # Right box
    add_rounded_rect(slide, 6.9, 2.3, 5.2, 2.0, RGBColor(0xE8, 0xF5, 0xE9))
    add_textbox(slide, 7.1, 2.35, 4.8, 0.35, "Medical Records",
                font_size=14, bold=True, color=L1_GREEN, alignment=PP_ALIGN.CENTER)
    add_textbox(slide, 7.1, 2.8, 4.8, 1.2,
                "Bilateral long bone\nfractures documented",
                font_size=18, color=DARK_TEXT, alignment=PP_ALIGN.CENTER)

    add_textbox(slide, 1.2, 4.45, 10.9, 0.4,
                "7 of 8 document agents quoted the sheriff's report without cross-checking",
                font_size=16, bold=True, color=SEV_CRITICAL,
                alignment=PP_ALIGN.CENTER)

    # Document improvement section
    add_textbox(slide, 1.2, 5.0, 10.9, 0.4,
                "The fix: document structure improvements",
                font_size=18, bold=True, color=DARK_NAVY)
    add_bullet_list(slide, 1.2, 5.4, 10.9, 1.5, [
        "Added cross-reference headers to each document (zero content changes)",
        "Commercial agent: 0/2 to 2/2 -- pulled Medical Records as primary source",
        "GCC agent: 3/10 to 9/10 -- same model, same platform, just better documents",
        "Zero code, zero engineering -- document hygiene any paralegal can implement",
    ], font_size=14)

    add_level_bar(slide)
    add_confidential_footer(slide)
    add_speaker_notes(slide,
        "Connect to daily experience: Copilot helps you draft an email -- you review it. "
        "Copilot helps you write code -- you review it. Why would we skip human review at "
        "any of these five levels, especially Level 5 where the stakes are a family's future?")


def slide_10_danger_taxonomy(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "The Danger Taxonomy",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.5,
                "Five categories of AI failure, ranked by severity",
                font_size=20, bold=True, color=DARK_TEXT)

    dangers = [
        ("1", "CRITICAL", "False Negative",
         "Data retrieved, answer not recognized", SEV_CRITICAL),
        ("2", "CRITICAL", "Faithfully Reproduced Misinformation",
         "Source document had an error, agent quoted it accurately", SEV_CRITICAL),
        ("3", "HIGH", "Misattribution",
         "Real fact, wrong person", SEV_HIGH),
        ("4", "HIGH", "Hallucinated Fact with Confidence",
         "Invented detail with no source", SEV_HIGH),
        ("5", "MEDIUM", "Silent Failure",
         "No results, no indication anything went wrong", SEV_MEDIUM),
    ]

    for i, (num, severity, name, desc, color) in enumerate(dangers):
        y = 2.2 + i * 0.9
        # Severity pill
        pill = add_rounded_rect(slide, 1.5, y + 0.05, 1.5, 0.5, color)
        tf = pill.text_frame
        p = tf.paragraphs[0]
        p.text = severity
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.CENTER

        # Name + desc
        add_textbox(slide, 3.2, y, 3.5, 0.6, f"{num}. {name}",
                    font_size=16, bold=True, color=DARK_TEXT)
        add_textbox(slide, 6.8, y + 0.05, 5.5, 0.6, desc,
                    font_size=15, color=MEDIUM_TEXT)

    add_textbox(slide, 1.2, 6.0, 10.9, 0.4,
                "These are not hypothetical. We documented each one across 313 test runs.",
                font_size=16, bold=True, color=ACCENT_BLUE,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)


def slide_11_iterative_process(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "The Iterative Process",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.5,
                "Deploying an agent is not a one-time event",
                font_size=22, bold=True, color=DARK_TEXT)

    # Four round boxes in a cycle
    rounds = [
        ("Round 0", "Baseline Testing", "Measure failures\nagainst ground truth",
         RGBColor(0x78, 0x90, 0x9C)),
        ("Round 1", "Fix the Data", "Make facts discrete\nand queryable",
         MEDIUM_BLUE),
        ("Round 2", "Fix the Tools", "Help the model\nreach the data",
         ACCENT_BLUE),
        ("Round 3", "Validate Models", "Confirm what works\nwhere",
         RGBColor(0x42, 0x95, 0x88)),
    ]

    for i, (rnd, title, desc, color) in enumerate(rounds):
        x = 1.2 + i * 3.1
        box = add_rounded_rect(slide, x, 2.5, 2.7, 3.0, color)
        add_textbox(slide, x + 0.1, 2.55, 2.5, 0.45, rnd,
                    font_size=14, bold=True, color=WHITE,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, x + 0.1, 3.1, 2.5, 0.5, title,
                    font_size=18, bold=True, color=WHITE,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, x + 0.1, 3.7, 2.5, 1.2, desc,
                    font_size=14, color=RGBColor(0xDD, 0xEE, 0xFF),
                    alignment=PP_ALIGN.CENTER)

    # Arrows between
    for i in range(3):
        x = 1.2 + (i + 1) * 3.1 - 0.4
        add_textbox(slide, x, 3.3, 0.5, 0.6, ">",
                    font_size=28, bold=True, color=ACCENT_BLUE,
                    alignment=PP_ALIGN.CENTER)

    add_textbox(slide, 1.2, 5.8, 10.9, 0.4,
                "Every organization will go through these rounds, in this order.",
                font_size=16, bold=True, color=MEDIUM_TEXT,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)


def slide_12_results(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "Results After Iteration",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.5,
                "Four agents reached 9-10 out of 10 (three at perfect 10)",
                font_size=20, bold=True, color=DARK_TEXT)

    headers = ["Agent", "Round 1", "Final", "Rounds"]
    rows = [
        ["Commercial MCP (Copilot Studio)", "8/10", "10/10", "2"],
        ["Investigative Agent (OpenAI SDK)", "1/10", "10/10", "2"],
        ["Foundry Agent", "4/10", "9/10", "2"],
        ["Triage Agent (Semantic Kernel)", "0/10", "10/10", "5"],
    ]
    add_table(slide, 1.5, 2.3, 10.3, [4.5, 1.8, 1.8, 1.5], headers, rows,
              font_size=16)

    add_textbox(slide, 1.2, 5.0, 10.9, 0.7,
                "The Triage Agent took five rounds to reach a perfect score.\n"
                "The investment is real -- but so are the results.",
                font_size=16, bold=True, color=MEDIUM_TEXT,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)


def slide_13_code_spectrum(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "The Code Spectrum",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.5,
                "Zero code to full code -- same accuracy with GPT-4.1",
                font_size=20, bold=True, color=DARK_TEXT)

    headers = ["Approach", "Code", "Best For"]
    rows = [
        ["M365 Copilot (Com)", "Zero (3 JSON manifests)", "Levels 1-2"],
        ["Copilot Studio", "Zero to low code", "Levels 1-3"],
        ["Foundry Agent", "Minimal code", "Levels 3-4"],
        ["Custom SDK (OpenAI, SK)", "Full code", "Levels 4-5"],
    ]
    add_table(slide, 1.5, 2.3, 10.3, [3.5, 3.5, 3.0], headers, rows,
              font_size=16)

    add_textbox(slide, 1.2, 5.0, 10.9, 0.7,
                "The investment buys governance and customization, not accuracy.\n"
                "Accuracy comes from the model and the data.",
                font_size=18, bold=True, color=ACCENT_BLUE,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)


def slide_14_why_copilot_studio(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "Why Copilot Studio",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.5,
                "One platform, declarative to pro-code",
                font_size=22, bold=True, color=DARK_TEXT)

    add_bullet_list(slide, 1.2, 2.3, 10.9, 3.5, [
        "Same environment hosts zero-code SharePoint agents AND MCP-connected structured data agents",
        "Model flexibility: swap GPT-4o for GPT-4.1, accuracy goes from 4/10 to 10/10 -- no config changes",
        "Enterprise governance built in: DLP, audit logging, admin pre-approval for tool calls",
        "M365 distribution: agents show up in Teams and Copilot chat -- no separate app to deploy",
        "Our test data proves the platform works -- the model is the variable, not the architecture",
    ], font_size=17)

    add_textbox(slide, 1.2, 5.5, 10.9, 0.7,
                "Commercial Copilot Studio MCP scored a perfect 10 out of 10.\n"
                "The architecture is sound. The limiting factor is model availability in GCC.",
                font_size=16, bold=True, color=ACCENT_BLUE,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)
    add_speaker_notes(slide,
        "This slide is critical for the tech series. MUST articulate the platform value, "
        "not just the results.")


def slide_15_what_to_do(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "What to Do at Each Level",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    headers = ["Level", "Action"]
    rows = [
        ["1-2", "Deploy Copilot with SharePoint. Clean up document metadata. Done."],
        ["3", "Connect to structured data via MCP. Clear tool descriptions. Summary modes."],
        ["4", "Purpose-built tools. GPT-4.1 minimum. Ground truth test suite. Budget 3+ rounds."],
        ["5", "Level 4 + human review workflows + audit logging + citation linking."],
    ]
    tbl = add_table(slide, 1.2, 1.6, 10.9, [1.5, 9.0], headers, rows, font_size=16)

    # Color the level cells
    table = tbl.table
    level_colors_map = [L1_GREEN, L3_ORANGE, L4_DEEP_ORANGE, L5_RED]
    for r in range(4):
        cell = table.cell(r + 1, 0)
        cell.fill.solid()
        cell.fill.fore_color.rgb = level_colors_map[r]
        for p in cell.text_frame.paragraphs:
            p.font.color.rgb = WHITE
            p.font.bold = True

    add_textbox(slide, 1.2, 5.2, 10.9, 0.5,
                "Match your investment to your accuracy requirement.",
                font_size=20, bold=True, color=ACCENT_BLUE,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)


def slide_16_gcc(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "Government Cloud Customers",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.5,
                "The GCC reality today",
                font_size=22, bold=True, color=DARK_TEXT)

    add_bullet_list(slide, 1.2, 2.2, 10.9, 1.5, [
        "Copilot Studio locked to GPT-4o (adequate for Levels 1-3)",
        "Pro-code agents can use GPT-4.1 via Azure OpenAI (Levels 4-5)",
        "Monitor model updates -- GCC parity will improve over time",
    ], font_size=17)

    # Decision tree boxes
    decisions = [
        ("Is your use case Level 1-3?", "Use Copilot Studio today.", L1_GREEN),
        ("Is your use case Level 4-5?", "Deploy a pro-code agent\nwith GPT-4.1.", L4_DEEP_ORANGE),
        ("Planning for Level 4-5\nin the future?", "Start building ground truth\ntest suites now.", MEDIUM_BLUE),
    ]

    for i, (question, answer, color) in enumerate(decisions):
        x = 1.2 + i * 3.9
        # Question box
        q_box = add_rounded_rect(slide, x, 4.0, 3.5, 1.0, LIGHT_GRAY)
        add_textbox(slide, x + 0.15, 4.0, 3.2, 1.0, question,
                    font_size=14, bold=True, color=DARK_TEXT,
                    alignment=PP_ALIGN.CENTER)
        # Answer box
        a_box = add_rounded_rect(slide, x, 5.2, 3.5, 1.0, color)
        add_textbox(slide, x + 0.15, 5.2, 3.2, 1.0, answer,
                    font_size=14, bold=True, color=WHITE,
                    alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)
    add_speaker_notes(slide,
        "Know what works today. Plan for what's coming.")


def slide_17_demo(prs):
    slide = add_blank_slide(prs)
    # Full navy background
    set_slide_bg(slide, DARK_NAVY)

    add_textbox(slide, 1.5, 1.0, 10.3, 1.0,
                "Live Demo",
                font_size=44, bold=True, color=WHITE,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, 1.5, 2.2, 10.3, 0.8,
                '"Let me show you the difference\nbetween Level 2 and Level 4."',
                font_size=24, color=RGBColor(0xA0, 0xC4, 0xE8),
                alignment=PP_ALIGN.CENTER)

    demos = [
        ("Level 2:", "SharePoint document summarization", "2 min"),
        ("Level 3:", '"How many cases by type?" aggregate query', "2 min"),
        ("Level 4:", "The money prompt -- timeline, discrepancies, statements", "5 min"),
        ("Level 5:", "The skeletal survey question", "3 min"),
    ]

    for i, (level, desc, time) in enumerate(demos):
        y = 3.5 + i * 0.7
        add_textbox(slide, 2.5, y, 1.5, 0.5, level,
                    font_size=16, bold=True, color=LEVEL_COLORS[i + 1],
                    alignment=PP_ALIGN.RIGHT)
        add_textbox(slide, 4.2, y, 5.5, 0.5, desc,
                    font_size=16, color=WHITE)
        add_textbox(slide, 10.0, y, 1.5, 0.5, time,
                    font_size=14, color=RGBColor(0x88, 0xAA, 0xCC),
                    alignment=PP_ALIGN.RIGHT)


def slide_18_challenged_premise(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "Surprising Finding: Agent Challenged Its Own Premise",
                font_size=28, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.5,
                "A pro-code agent questioned the question -- and was right",
                font_size=20, bold=True, color=DARK_TEXT)

    add_bullet_list(slide, 1.2, 2.3, 10.9, 2.5, [
        "Asked about a $146,000 purchase vs a $357,100 assessment",
        "Agent checked the source data: actual assessment was $53,155",
        "Recalculated using verified numbers instead of the prompt's numbers",
        "No other agent questioned the input",
    ], font_size=18)

    # Quote box
    quote_box = add_rounded_rect(slide, 2.0, 4.6, 9.3, 1.2,
                                  RGBColor(0xE3, 0xF2, 0xFD))
    add_textbox(slide, 2.2, 4.65, 8.9, 1.1,
                '"The assessment value in our records is $53,155, not $357,100 as stated '
                'in the question. Using the verified assessment value..."',
                font_size=15, color=MEDIUM_BLUE, alignment=PP_ALIGN.CENTER)

    add_textbox(slide, 1.2, 6.0, 10.9, 0.4,
                "This is what custom orchestration enables -- but only with iterative testing.",
                font_size=16, bold=True, color=MEDIUM_TEXT,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)


def slide_19_false_negative(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "Surprising Finding: False Negative",
                font_size=28, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.5,
                "The model retrieved the answer and didn't recognize it",
                font_size=20, bold=True, color=DARK_TEXT)

    add_bullet_list(slide, 1.2, 2.3, 10.9, 2.0, [
        "Agent called the right tools",
        'Received data containing "two positive drug screens (fentanyl)"',
        'Concluded: "no drug test results exist in the available data"',
        "Invisible to users: tool calls look correct, answer sounds confident",
    ], font_size=18)

    # Tool output vs Agent conclusion
    add_rounded_rect(slide, 1.5, 4.5, 5.0, 1.5, RGBColor(0xE8, 0xF5, 0xE9))
    add_textbox(slide, 1.7, 4.55, 4.6, 0.35, "Tool Output (correct)",
                font_size=13, bold=True, color=L1_GREEN, alignment=PP_ALIGN.CENTER)
    add_textbox(slide, 1.7, 5.0, 4.6, 0.8,
                '"two positive drug screens\n(fentanyl)"',
                font_size=16, color=DARK_TEXT, alignment=PP_ALIGN.CENTER)

    add_rounded_rect(slide, 6.8, 4.5, 5.0, 1.5, RGBColor(0xFF, 0xEB, 0xEE))
    add_textbox(slide, 7.0, 4.55, 4.6, 0.35, "Agent Conclusion (wrong)",
                font_size=13, bold=True, color=L5_RED, alignment=PP_ALIGN.CENTER)
    add_textbox(slide, 7.0, 5.0, 4.6, 0.8,
                '"no drug test results exist\nin the available data"',
                font_size=16, color=DARK_TEXT, alignment=PP_ALIGN.CENTER)

    add_textbox(slide, 1.2, 6.2, 10.9, 0.4,
                "This is why you need ground truth testing. You cannot catch this in production.",
                font_size=16, bold=True, color=SEV_CRITICAL,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)


def slide_20_bottom_line(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, WHITE)
    add_textbox(slide, 0.8, 0.4, 11.7, 0.7,
                "The Bottom Line",
                font_size=32, bold=True, color=DARK_NAVY)
    add_rect(slide, 0.8, 1.1, 2, 0.06, ACCENT_BLUE)

    add_textbox(slide, 1.2, 1.5, 10.9, 0.5,
                "Three numbers to remember",
                font_size=22, bold=True, color=DARK_TEXT)

    # Three big number cards
    cards = [
        ("8/10", "What you get with\nzero engineering", "Levels 1-2",
         L1_GREEN),
        ("9.5/10", "What you get with\npurpose-built tools + GPT-4.1", "Levels 3-4",
         ACCENT_BLUE),
        ("Trust\nBut Verify", "No score is high enough\nto skip human review", "Level 5",
         L5_RED),
    ]

    for i, (number, desc, levels, color) in enumerate(cards):
        x = 1.2 + i * 3.9
        box = add_rounded_rect(slide, x, 2.3, 3.5, 3.5, color)
        add_textbox(slide, x + 0.1, 2.5, 3.3, 1.2, number,
                    font_size=40, bold=True, color=WHITE,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, x + 0.1, 3.8, 3.3, 1.0, desc,
                    font_size=15, color=WHITE,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, x + 0.1, 5.0, 3.3, 0.5, levels,
                    font_size=13, color=RGBColor(0xDD, 0xEE, 0xFF),
                    alignment=PP_ALIGN.CENTER)

    add_textbox(slide, 1.2, 6.0, 10.9, 0.5,
                '"The question is not \'should we deploy AI?\' The question is '
                '\'which level are we operating at, and have we invested accordingly?\'"',
                font_size=15, bold=True, color=MEDIUM_TEXT,
                alignment=PP_ALIGN.CENTER)

    add_level_bar(slide)
    add_confidential_footer(slide)
    add_speaker_notes(slide,
        "So what do we do? Do we just give up on agents? No -- you continue to test "
        "them and make them better, and you always adhere to trust but verify. I have "
        "agents building apps for me right now. If I were building production enterprise "
        "apps, I'd have a team of human developers checking the work, helping test, "
        "reviewing agentic results. The AI accelerates the team. The team validates the AI.")


def slide_21_next_steps(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, DARK_NAVY)

    add_textbox(slide, 1.5, 0.8, 10.3, 1.0,
                "Next Steps",
                font_size=44, bold=True, color=WHITE,
                alignment=PP_ALIGN.CENTER)

    add_textbox(slide, 1.5, 2.0, 10.3, 0.6,
                "Start the conversation",
                font_size=24, color=RGBColor(0xA0, 0xC4, 0xE8),
                alignment=PP_ALIGN.CENTER)

    questions = [
        "Where do your use cases fall on the spectrum?",
        "What data do you already have in structured form?",
        "What's your risk tolerance for AI-generated output?",
        "Ready for a deeper dive? We have the architecture, the test data, and the framework.",
    ]

    for i, q in enumerate(questions):
        y = 3.2 + i * 0.8
        add_textbox(slide, 3.0, y, 7.3, 0.6, q,
                    font_size=18, color=WHITE)
        # bullet dot
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(2.5), Inches(y + 0.15), Inches(0.2), Inches(0.2))
        dot.fill.solid()
        dot.fill.fore_color.rgb = ACCENT_BLUE
        dot.line.fill.background()

    add_textbox(slide, 1.5, 6.2, 10.3, 0.6,
                "I'm not here to sell you a product. I'm here to help you make "
                "the right investment for your mission.",
                font_size=16, bold=True, color=RGBColor(0xA0, 0xC4, 0xE8),
                alignment=PP_ALIGN.CENTER)


def main():
    prs = new_prs()

    slide_01_title(prs)
    slide_02_the_question(prs)
    slide_03_five_levels(prs)
    slide_04_quick_win(prs)
    slide_05_level3(prs)
    slide_06_inflection(prs)
    slide_07_model_gap(prs)
    slide_08_tool_gap(prs)
    slide_09_level5(prs)
    slide_10_danger_taxonomy(prs)
    slide_11_iterative_process(prs)
    slide_12_results(prs)
    slide_13_code_spectrum(prs)
    slide_14_why_copilot_studio(prs)
    slide_15_what_to_do(prs)
    slide_16_gcc(prs)
    slide_17_demo(prs)
    slide_18_challenged_premise(prs)
    slide_19_false_negative(prs)
    slide_20_bottom_line(prs)
    slide_21_next_steps(prs)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "decks")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "agent-accuracy-spectrum.pptx")
    prs.save(out_path)
    print(f"Saved: {out_path}")
    print(f"Slides: {len(prs.slides)}")


if __name__ == "__main__":
    main()
