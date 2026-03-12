"""
Generate a one-page demo cheat sheet PDF from docs/demo-cheat-sheet.md.
Designed to be compact and printable on a single sheet.

Usage: python scripts/generate-cheat-sheet-pdf.py
Output: docs/pdf/demo-cheat-sheet.pdf
"""

from fpdf import FPDF
import os


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


# -- Colors ------------------------------------------------------------------
NAVY = (22, 48, 82)
ACCENT = (41, 98, 163)
DARK = (40, 40, 40)
MED = (90, 90, 90)
LIGHT = (140, 140, 140)
WHITE = (255, 255, 255)
TABLE_HEADER_BG = (22, 48, 82)
TABLE_HEADER_FG = (255, 255, 255)
ROW_ALT = (243, 246, 250)
ROW_WHT = (255, 255, 255)

# Level colors
L2_COLOR = (139, 195, 74)
L3_COLOR = (255, 193, 7)
L4_COLOR = (255, 87, 34)
L5_COLOR = (211, 47, 47)

WARN_BG = (255, 248, 235)
WARN_BORDER = (230, 170, 50)
GREEN_BG = (232, 245, 233)
GREEN_BORDER = (76, 175, 80)


class CheatSheetPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=False)


def build_pdf():
    pdf = CheatSheetPDF()
    pdf.set_margins(12, 10, 12)
    pdf.add_page()

    usable_w = pdf.w - pdf.l_margin - pdf.r_margin
    col_gap = 6
    col_w = (usable_w - col_gap) / 2

    # ── Title bar ──
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 14, "F")
    pdf.set_xy(pdf.l_margin, 3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*WHITE)
    pdf.cell(usable_w, 8, sanitize_text("Demo Cheat Sheet -- Agent Fidelity Spectrum"),
             align="C")

    # ── Left column ──
    lx = pdf.l_margin
    y = 18

    # Pre-Demo section
    pdf.set_xy(lx, y)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(col_w, 5, "PRE-DEMO (10 min before)")
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.4)
    pdf.line(lx, y + 5, lx + col_w, y + 5)
    pdf.set_line_width(0.2)
    y += 7

    pre_demo = [
        ("1.", "Open SWA: happy-wave-016cd330f.1.azurestaticapps.net"),
        ("2.", "Click Warm Up -- wait for green checkmarks"),
        ("3.", "Open CS SP/PDF/Com agent -- send throwaway prompt"),
        ("4.", "Open CS MCP/Com agent -- send throwaway prompt"),
        ("5.", "Pre-stage browser tabs: SWA, both CS agents, deck"),
    ]
    pdf.set_font("Helvetica", "", 7)
    for num, text in pre_demo:
        pdf.set_xy(lx, y)
        pdf.set_text_color(*ACCENT)
        pdf.set_font("Helvetica", "B", 7)
        pdf.cell(5, 3.8, num)
        pdf.set_text_color(*DARK)
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(col_w - 5, 3.8, sanitize_text(text))
        y += 4.2

    y += 3

    # Demo Flow section
    pdf.set_xy(lx, y)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(col_w, 5, "DEMO FLOW (S21 -- ~12 min)")
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.4)
    pdf.line(lx, y + 5, lx + col_w, y + 5)
    pdf.set_line_width(0.2)
    y += 8

    # Level cards
    levels = [
        (L2_COLOR, "L2", "SharePoint Summarization", "2 min", "CS SP/PDF/Com",
         "Summarize the medical records for case 2024-DR-42-0892",
         "This is where most agencies should start."),
        (L3_COLOR, "L3", "Aggregate Query", "2 min", "Web UI (Case Analyst)",
         "How many active cases does DSS have by case type?",
         "The moment you need to count across cases, you need structured data."),
        (L4_COLOR, "L4", "The Money Prompt", "5 min", "Web UI (Case Analyst)",
         "Build a complete timeline for case 2024-DR-42-0892. Include all discrepancies between Marcus Webb's and Dena Holloway's accounts.",
         "This is what a paralegal spends hours doing."),
        (L5_COLOR, "L5", "Skeletal Survey Trap", "3 min", "Talk through / screenshot",
         "What did the skeletal survey show for Jaylen Webb?",
         "The citation was real. The conclusion was dangerous."),
    ]

    for color, label, title, time, agent, prompt, talking_pt in levels:
        # Measure prompt height
        pdf.set_font("Helvetica", "I", 6.5)
        prompt_h = pdf.multi_cell(col_w - 14, 3.2, sanitize_text(prompt),
                                  dry_run=True, output="HEIGHT")
        card_h = max(21, 10 + prompt_h + 6)

        # Card background
        tint = tuple(int(c * 0.12 + 255 * 0.88) for c in color)
        pdf.set_fill_color(*tint)
        pdf.rect(lx, y, col_w, card_h, "F")
        # Color stripe
        pdf.set_fill_color(*color)
        pdf.rect(lx, y, 2.5, card_h, "F")

        # Label + title + time
        pdf.set_xy(lx + 4, y + 1)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(*color)
        pdf.cell(8, 4, label)
        pdf.set_text_color(*DARK)
        pdf.cell(col_w - 30, 4, sanitize_text(title))
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(*MED)
        pdf.cell(16, 4, sanitize_text(time + " | " + agent), align="R")

        # Prompt
        pdf.set_xy(lx + 4, y + 6)
        pdf.set_font("Helvetica", "I", 6.5)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(col_w - 6, 3.2, sanitize_text(prompt))

        # Talking point
        tp_y = y + card_h - 5
        pdf.set_xy(lx + 4, tp_y)
        pdf.set_font("Helvetica", "B", 6)
        pdf.set_text_color(*color)
        pdf.cell(col_w - 6, 3.5, sanitize_text(talking_pt))

        y += card_h + 2

    # ── Right column ──
    rx = pdf.l_margin + col_w + col_gap
    y_r = 18

    # Fallback Plan
    pdf.set_xy(rx, y_r)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(col_w, 5, "FALLBACK PLAN")
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.4)
    pdf.line(rx, y_r + 5, rx + col_w, y_r + 5)
    pdf.set_line_width(0.2)
    y_r += 8

    fallbacks = [
        ("SWA won't load", "Show architecture slide and talk through it"),
        ("Container App times out", "Re-click Warm Up, fill with skeletal survey story"),
        ("CS agent is slow", '"Cold start -- in production you\'d pin these"'),
        ("Agent gives wrong answer", '"Exactly the point -- here\'s what it should say"'),
    ]

    fb_col1 = 28
    fb_col2 = col_w - fb_col1
    # Header
    pdf.set_xy(rx, y_r)
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_fill_color(*TABLE_HEADER_BG)
    pdf.set_text_color(*TABLE_HEADER_FG)
    pdf.cell(fb_col1, 5, "  If...", fill=True)
    pdf.cell(fb_col2, 5, "  Then...", fill=True)
    y_r += 5.5

    pdf.set_font("Helvetica", "", 6.5)
    for i, (cond, action) in enumerate(fallbacks):
        bg = ROW_ALT if i % 2 == 0 else ROW_WHT
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*DARK)

        # Measure heights
        pdf.set_font("Helvetica", "B", 6.5)
        h1 = pdf.multi_cell(fb_col1 - 2, 3.5, sanitize_text(cond),
                             dry_run=True, output="HEIGHT")
        pdf.set_font("Helvetica", "", 6.5)
        h2 = pdf.multi_cell(fb_col2 - 2, 3.5, sanitize_text(action),
                             dry_run=True, output="HEIGHT")
        row_h = max(h1, h2) + 2

        # Background
        pdf.set_fill_color(*bg)
        pdf.rect(rx, y_r, fb_col1, row_h, "F")
        pdf.rect(rx + fb_col1, y_r, fb_col2, row_h, "F")

        # Text
        pdf.set_xy(rx + 1, y_r + 1)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(fb_col1 - 2, 3.5, sanitize_text(cond))

        pdf.set_xy(rx + fb_col1 + 1, y_r + 1)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(*MED)
        pdf.multi_cell(fb_col2 - 2, 3.5, sanitize_text(action))

        y_r += row_h

    y_r += 5

    # Key Numbers
    pdf.set_xy(rx, y_r)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(col_w, 5, "KEY NUMBERS")
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.4)
    pdf.line(rx, y_r + 5, rx + col_w, y_r + 5)
    pdf.set_line_width(0.2)
    y_r += 8

    stats = [
        ("Test runs", "462"),
        ("Agent configs", "21"),
        ("Cases in DB", "50"),
        ("Primary demo case", "2024-DR-42-0892"),
        ("Secondary demo case", "2024-DR-15-0341"),
        ("Best zero-code", "10/10 (SP/PDF/Com)"),
        ("Best pro-code", "10/10 (Case Analyst, IA, Triage)"),
        ("Worst-to-best", "Triage: 0/10 -> 10/10 in 5 rounds"),
        ("Models tested", "5 (GPT-4o, 4.1, 5 Auto, 5 Reasoning, Sonnet)"),
        ("Model gap", "Sonnet 11/11, GPT-5 Reasoning 10/11, GPT-4o 3.2/11"),
    ]

    stat_col1 = 30
    stat_col2 = col_w - stat_col1

    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_fill_color(*TABLE_HEADER_BG)
    pdf.set_text_color(*TABLE_HEADER_FG)
    pdf.set_xy(rx, y_r)
    pdf.cell(stat_col1, 5, "  Stat", fill=True)
    pdf.cell(stat_col2, 5, "  Value", fill=True)
    y_r += 5.5

    for i, (stat, val) in enumerate(stats):
        bg = ROW_ALT if i % 2 == 0 else ROW_WHT
        pdf.set_fill_color(*bg)
        pdf.set_xy(rx, y_r)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(*DARK)
        pdf.cell(stat_col1, 4.5, sanitize_text("  " + stat), fill=True)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(*MED)
        pdf.cell(stat_col2, 4.5, sanitize_text("  " + val), fill=True)
        y_r += 4.5

    y_r += 5

    # Three Numbers callout
    pdf.set_fill_color(*GREEN_BG)
    pdf.set_draw_color(*GREEN_BORDER)
    box_h = 20
    pdf.rect(rx, y_r, col_w, box_h, "FD")
    pdf.set_xy(rx + 3, y_r + 2)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*NAVY)
    pdf.cell(col_w - 6, 4, "THE BOTTOM LINE")
    pdf.set_xy(rx + 3, y_r + 6.5)
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(*DARK)
    pdf.cell(10, 3.5, "8/10")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(*MED)
    pdf.cell(col_w - 16, 3.5, sanitize_text("-- zero engineering (Levels 1-2)"))
    pdf.set_xy(rx + 3, y_r + 10.5)
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(*DARK)
    pdf.cell(10, 3.5, "9.5/10")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(*MED)
    pdf.cell(col_w - 16, 3.5, sanitize_text("-- purpose-built tools + GPT-4.1 (Levels 3-4)"))
    pdf.set_xy(rx + 3, y_r + 14.5)
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(*DARK)
    pdf.cell(18, 3.5, "Trust but verify")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(*MED)
    pdf.cell(col_w - 24, 3.5, sanitize_text("-- no score skips human review (Level 5)"))

    y_r += box_h + 4

    # URLs callout
    pdf.set_fill_color(*WARN_BG)
    pdf.set_draw_color(*WARN_BORDER)
    url_h = 14
    pdf.rect(rx, y_r, col_w, url_h, "FD")
    pdf.set_xy(rx + 3, y_r + 2)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*NAVY)
    pdf.cell(col_w - 6, 4, "URLS")
    pdf.set_xy(rx + 3, y_r + 6.5)
    pdf.set_font("Courier", "", 5.5)
    pdf.set_text_color(*DARK)
    pdf.cell(col_w - 6, 3.5, "SWA: happy-wave-016cd330f.1.azurestaticapps.net")
    pdf.set_xy(rx + 3, y_r + 10)
    pdf.cell(col_w - 6, 3.5, "API: dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io")

    # Footer (page 1)
    pdf.set_xy(pdf.l_margin, pdf.h - 8)
    pdf.set_font("Helvetica", "I", 6)
    pdf.set_text_color(*LIGHT)
    pdf.cell(usable_w, 4, sanitize_text("Agent Fidelity Spectrum for Copilot Studio | March 2026 | Confidential"),
             align="C")

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 2 — Use Case Stories
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()

    # Title bar
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 14, "F")
    pdf.set_xy(pdf.l_margin, 3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*WHITE)
    pdf.cell(usable_w, 8, "The Two Use Cases", align="C")

    # ── Intro blurb ──
    y2 = 18
    pdf.set_xy(pdf.l_margin, y2)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(usable_w, 4, sanitize_text(
        "Both use cases follow the same pattern: a government worker protecting "
        "vulnerable people needs to cross-reference records, spot contradictions, "
        "and build a case that holds up. The difference is where the data lives -- "
        "one in documents, the other in databases. The question is the same: can an "
        "AI agent do this work reliably enough to trust?"
    ))
    y2 = pdf.get_y() + 4

    # ── Helper: story card ──
    def draw_story_card(pdf, x, y, w, color, uc_label, title, subtitle,
                        setting, complication, stakes, data_note, connection):
        """Draw a use-case story card. Returns bottom y."""
        pad = 4
        inner_w = w - 2 * pad

        # Measure all text blocks to compute card height
        pdf.set_font("Helvetica", "", 7.5)
        setting_h = pdf.multi_cell(inner_w, 3.8, sanitize_text(setting),
                                   dry_run=True, output="HEIGHT")
        complication_h = pdf.multi_cell(inner_w, 3.8, sanitize_text(complication),
                                        dry_run=True, output="HEIGHT")
        stakes_h = pdf.multi_cell(inner_w, 3.8, sanitize_text(stakes),
                                   dry_run=True, output="HEIGHT")
        pdf.set_font("Helvetica", "I", 7)
        data_h = pdf.multi_cell(inner_w, 3.5, sanitize_text(data_note),
                                 dry_run=True, output="HEIGHT")
        pdf.set_font("Helvetica", "B", 7)
        conn_h = pdf.multi_cell(inner_w, 3.5, sanitize_text(connection),
                                 dry_run=True, output="HEIGHT")

        # header(8) + subtitle(5) + 3 labeled sections + data + connection + padding
        card_h = (8 + 5 + (5 + setting_h) + (5 + complication_h) +
                  (5 + stakes_h) + 3 + data_h + 3 + conn_h + 6)

        # Card background
        tint = tuple(int(c * 0.08 + 255 * 0.92) for c in color)
        pdf.set_fill_color(*tint)
        pdf.rect(x, y, w, card_h, "F")
        # Color stripe
        pdf.set_fill_color(*color)
        pdf.rect(x, y, 3, card_h, "F")

        cy = y + 2

        # UC label + title
        pdf.set_xy(x + pad + 1, cy)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*color)
        pdf.cell(14, 5, uc_label)
        pdf.set_text_color(*NAVY)
        pdf.cell(inner_w - 14, 5, sanitize_text(title))
        cy += 7

        # Subtitle
        pdf.set_xy(x + pad + 1, cy)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*MED)
        pdf.cell(inner_w, 4, sanitize_text(subtitle))
        cy += 6

        # Section helper
        def draw_section(label, text, font_style=""):
            nonlocal cy
            pdf.set_xy(x + pad + 1, cy)
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_text_color(*ACCENT)
            pdf.cell(inner_w, 4, label)
            cy += 4.5
            pdf.set_xy(x + pad + 1, cy)
            pdf.set_font("Helvetica", font_style, 7.5)
            pdf.set_text_color(*DARK)
            pdf.multi_cell(inner_w, 3.8, sanitize_text(text))
            cy = pdf.get_y() + 1

        draw_section("THE SETTING", setting)
        draw_section("THE COMPLICATION", complication)
        draw_section("THE STAKES", stakes)

        cy += 1
        # Data note (italic)
        pdf.set_xy(x + pad + 1, cy)
        pdf.set_font("Helvetica", "I", 7)
        pdf.set_text_color(*MED)
        pdf.multi_cell(inner_w, 3.5, sanitize_text(data_note))
        cy = pdf.get_y() + 2

        # Connection callout
        pdf.set_fill_color(*color)
        pdf.rect(x + pad + 1, cy, 1.5, conn_h + 2, "F")
        pdf.set_xy(x + pad + 4, cy + 1)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*color)
        pdf.multi_cell(inner_w - 4, 3.5, sanitize_text(connection))

        return y + card_h

    # ── UC1 Card ──
    UC1_COLOR = (41, 98, 163)   # blue
    UC2_COLOR = (183, 110, 30)  # amber

    y2 = draw_story_card(
        pdf, pdf.l_margin, y2, usable_w, UC1_COLOR,
        "UC1", "Document Fidelity",
        "Can an AI agent prepare a child welfare case from legal documents?",

        setting=(
            "An attorney in the Department of Social Services is preparing for "
            "a probable cause hearing on Thursday. A two-year-old named Jaylen "
            "was admitted to the ER at 3 AM with bilateral fractures. Both parents "
            "say he fell from his crib. The attorney has 11 documents -- dictation "
            "notes, medical records, a sheriff's report, court filings -- scattered "
            "across SharePoint."
        ),
        complication=(
            "The mother's story changed between the hospital and the sheriff's "
            "interview. At the ER, she said she heard crying at 2 AM. The next day, "
            "she told the detective she heard a loud thump at 9:30 PM -- four and a "
            "half hours earlier -- and that the father had a temper and had grabbed "
            "the child roughly before. Meanwhile, the radiologist found fractures at "
            "different stages of healing, meaning two separate injury events days "
            "apart. A single crib fall cannot explain that."
        ),
        stakes=(
            "The attorney needs every discrepancy, every contradiction, every "
            "timeline gap surfaced before the hearing. Miss one, and a judge may "
            "not find probable cause. But one of the documents -- the sheriff's "
            "report -- says the skeletal survey showed 'no fractures.' The medical "
            "records say the opposite. Seven of eight document agents quoted the "
            "sheriff without cross-checking. The citation was real. The confidence "
            "was justified. The conclusion was dangerous."
        ),
        data_note=(
            "50 synthetic cases, 277 people, 333 timeline events, 338 statements, "
            "151 discrepancies. All data modeled after real DSS legal pleadings, "
            "all PII replaced with fictional names."
        ),
        connection=(
            "This is why fidelity matters: the answer looked right, cited a real "
            "source, and was dead wrong. Level 5 requires human review -- always."
        ),
    )

    y2 += 5

    # ── UC2 Card ──
    y2 = draw_story_card(
        pdf, pdf.l_margin, y2, usable_w, UC2_COLOR,
        "UC2", "Investigative Analytics",
        "Can an AI agent investigate a slumlord from a 34-million-row property database?",

        setting=(
            "A city investigator notices a pattern: one LLC owns 194 properties "
            "across Philadelphia. 178 are vacant lots. They buy at sheriff's sales "
            "for pennies on the dollar -- a $357,000 stone colonial for $230,000, "
            "a $629,000 multi-family building for $46,000. No rental licenses. No "
            "business licenses. The entity's mailing address is a house 1.2 miles "
            "from its most valuable property."
        ),
        complication=(
            "The properties accumulate 1,411 code violations. 823 failed inspections. "
            "Lots fill with debris while assessed values climb in gentrifying "
            "neighborhoods. One property -- 2400 Bryn Mawr, a 4,100 sq ft stone "
            "colonial -- has 34 violations and a condition rating of 7 out of 7 "
            "(near-uninhabitable). The investigator needs to trace the ownership "
            "chain, calculate acquisition discounts, map violation patterns across "
            "zip codes. The data spans 34 million rows."
        ),
        stakes=(
            "Every MCP-backed agent can count the properties, pull the violations, "
            "and trace the ownership chain -- but only with the right model. GPT-4o "
            "scores 3.2/11 on the same Dataverse MCP infrastructure where Sonnet 4.6 "
            "scores 11/11 and GPT-5 Reasoning scores 10/11. Same data, same tools, same "
            "agent -- different model, completely different outcome. And every SQL-backed agent struggles with "
            "address resolution: 15 attempts across three prompts, only 2 correct "
            "parcel matches."
        ),
        data_note=(
            "Real public data from the City of Philadelphia. 584K properties, "
            "1.6M violations, 34M total rows. Five investigation PDFs written from "
            "the data for document agent comparison."
        ),
        connection=(
            "This is why model choice matters: infrastructure is necessary but not "
            "sufficient. The gap between models is larger than the gap between tools."
        ),
    )

    # Footer (page 2)
    pdf.set_xy(pdf.l_margin, pdf.h - 8)
    pdf.set_font("Helvetica", "I", 6)
    pdf.set_text_color(*LIGHT)
    pdf.cell(usable_w, 4, sanitize_text("Agent Fidelity Spectrum for Copilot Studio | March 2026 | Confidential"),
             align="C")

    # Save
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "pdf")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "demo-cheat-sheet.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    build_pdf()
