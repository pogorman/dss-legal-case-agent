"""
Generate O'G's single-page presenter guide PDF.
Uses fpdf2 — same dependency as the executive summary.

Usage: python scripts/generate-presenter-guide.py
Output: docs/ogs-presenter-guide.pdf
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
GREEN   = (34, 120, 69)
AMBER   = (180, 130, 20)
RED     = (185, 45, 45)
DIVIDER = (200, 210, 220)


class PresenterPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=False)


def build_pdf():
    pdf = PresenterPDF()
    page_margin = 12
    pdf.set_margins(page_margin, 10, page_margin)
    pdf.add_page()

    page_w = pdf.w - page_margin * 2

    # ── TITLE BAR ──────────────────────────────────────────────────
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 16, "F")
    pdf.set_y(4)
    pdf.set_x(page_margin)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*WHITE)
    pdf.cell(page_w / 2, 8, "O'G's Presenter Guide")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(180, 200, 220)
    pdf.cell(page_w / 2, 8, "DSS Legal Case Agent  |  Copilot Studio Evaluation", align="R")

    # ── COLUMN GEOMETRY ────────────────────────────────────────────
    gutter = 6
    col_w = (page_w - gutter) / 2
    left_x = page_margin
    right_x = page_margin + col_w + gutter
    col_top = 20

    # ── MARGIN HELPERS ─────────────────────────────────────────────
    # Set l_margin and r_margin to constrain all write()/multi_cell()
    # calls to the active column. This is the key to preventing bleed.

    def set_col_margins(cx, cw):
        """Set page margins to match a column so write/multi_cell respect its bounds."""
        pdf.l_margin = cx
        pdf.r_margin = pdf.w - (cx + cw)

    def restore_page_margins():
        pdf.l_margin = page_margin
        pdf.r_margin = page_margin

    # ── COLUMN-AWARE HELPERS ───────────────────────────────────────

    def section_header(title):
        cx = pdf.l_margin
        pdf.set_x(cx)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 6, title.upper())
        y = pdf.get_y() + 6
        pdf.set_draw_color(*ACCENT)
        pdf.set_line_width(0.4)
        pdf.line(cx, y, cx + 42, y)
        pdf.set_line_width(0.2)
        pdf.set_xy(cx, y + 2.5)

    def bullet(text, bold_lead=None):
        cx = pdf.l_margin
        indent = 4
        pdf.set_x(cx + indent)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*MED)
        pdf.write(4.2, "- ")
        if bold_lead:
            pdf.set_font("Helvetica", "B", 7.5)
            pdf.set_text_color(*DARK)
            pdf.write(4.2, bold_lead + " ")
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*DARK)
        pdf.write(4.2, text)
        pdf.ln(5)

    def body_text(text, indent=4, font_size=7.5, line_h=4.2, style="", color=DARK):
        pdf.set_x(pdf.l_margin + indent)
        pdf.set_font("Helvetica", style, font_size)
        pdf.set_text_color(*color)
        pdf.multi_cell(0, line_h, text)

    # ================================================================
    # LEFT COLUMN
    # ================================================================
    set_col_margins(left_x, col_w)
    pdf.set_xy(left_x, col_top)

    # ── YOUR 3 MESSAGES ────────────────────────────────────────────
    section_header("Your 3 Messages")

    pdf.set_x(left_x + 3)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*ACCENT)
    pdf.multi_cell(0, 4.5, "1. Why some GCC Copilot Studio agents struggle in production")
    body_text(
        "GCC is locked to GPT-4o. It hallucinates facts (2:00 AM vs 3:15 AM), "
        "fabricates citations, and you can't change the model. Show the consistency "
        "retest: same wrong answer both times.",
        indent=7
    )
    pdf.ln(2.5)

    pdf.set_x(left_x + 3)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*ACCENT)
    pdf.multi_cell(0, 4.5, "2. What you feed your agent matters as much as your prompt")
    body_text(
        "Same docs, different format = different results. PDF > DOCX > MD. "
        "Structured data is deterministic: same query, same answer, every time. "
        "Skeletal survey: 7/8 doc agents repeated \"no fractures\" when two fractures existed.",
        indent=7
    )
    pdf.ln(2.5)

    pdf.set_x(left_x + 3)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*ACCENT)
    pdf.multi_cell(0, 4.5, "3. Connect Copilot Studio to a real backend -- no custom connectors")
    body_text(
        "Copilot Studio is the interface, Azure is the engine. MCP plugin = one URL, "
        "no connector code. SWA -> Container App -> APIM -> Functions -> SQL.",
        indent=7
    )
    pdf.ln(3.5)

    # ── DEMO FLOW ──────────────────────────────────────────────────
    section_header("Demo Flow")

    steps = [
        ("Before audience:", "Click Warm Up. Wait for 3 green checks (10-20s)."),
        ("1. Case Browser:", "Show 50 cases: 277 people, 333 events, 151 discrepancies."),
        ("2. Open chat:", "Run 4-part attorney prompt. Point out tool badges."),
        ("3. Skeletal survey:", "\"Did the Sheriff find fractures?\" MCP finds both + conflict."),
        ("4. Aggregate (P9):", "\"Which cases are TPR?\" MCP finds all 9. Doc agents: 1."),
        ("5. Time gap (P10):", "\"Thump to hospital?\" MCP: 4h30m correct. Doc agent: 10h."),
        ("6. Side-by-side:", "Same prompt, Copilot Studio: structured vs. document agent."),
        ("7. Architecture:", "Four-tier diagram. Managed identity, private endpoints, zero secrets."),
    ]
    for bold_lead, text in steps:
        bullet(text, bold_lead=bold_lead)

    pdf.ln(2)

    # ── KILLER STAT ────────────────────────────────────────────────
    section_header("The Number That Sells It")
    body_text(
        "7 of 8 document agents told an attorney \"no fractures detected\" "
        "when two fractures existed in the medical records.",
        font_size=9, style="B", color=RED, line_h=4.8
    )
    pdf.ln(1)
    body_text(
        "The citation made it look authoritative. Only 1 doc agent caught it. "
        "All 3 structured agents found both fractures after improvements."
    )
    pdf.ln(3)

    # ── RANKINGS ───────────────────────────────────────────────────
    section_header("Final Rankings")

    rank_data = [
        ("#1", "Web App", "10P / 0F", GREEN),
        ("#2", "Structured (GCC)", "9P / 1F", GREEN),
        ("#3", "Structured (Com)", "8P / 0F", GREEN),
        ("#4", "SP/PDF (Com)", "8P / 0F", ACCENT),
        ("#5", "KB/DOCX (Com)", "6P / 2F", AMBER),
        ("#11", "SP/PDF (GCC)", "2P / 6F", RED),
    ]
    for rank, name, score, color in rank_data:
        pdf.set_x(left_x + 4)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(*color)
        pdf.cell(10, 4.2, rank)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*DARK)
        pdf.cell(38, 4.2, name)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(*color)
        pdf.cell(30, 4.2, score)
        pdf.ln()

    left_bottom = pdf.get_y()

    # ================================================================
    # RIGHT COLUMN
    # ================================================================
    set_col_margins(right_x, col_w)
    pdf.set_xy(right_x, col_top)

    # ── 5 KEY FINDINGS ─────────────────────────────────────────────
    section_header("5 Findings (Your Talking Points)")

    findings = [
        ("1. Structured agents are consistently precise.",
         "Same query = same answer every time. 12/12 timeline events, zero fabrication. "
         "Doc agents ranged 4-12/12 with wrong-case contamination."),
        ("2. Every agent has a failure mode.",
         "No config was correct on all 10 prompts. Structured agents fail safely "
         "(\"not in the data\"). Doc agents fail dangerously (wrong answer + citation)."),
        ("3. The AI model matters as much as architecture.",
         "GPT-4o (GCC): better tool selection, more hallucinations. "
         "GPT-4.1 (Com): fewer hallucinations, skips the discrepancy tool entirely."),
        ("4. Document format affects results.",
         "PDF > DOCX > MD. SharePoint > Uploaded. Same files, different indexing = different answers."),
        ("5. Structured data fails safely; documents fail dangerously.",
         "Structured agents say \"not in the data.\" Doc agents reproduce a misleading "
         "source with a citation -- the wrong answer looks authoritative."),
    ]
    for heading, text in findings:
        pdf.set_x(right_x)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(*NAVY)
        pdf.multi_cell(0, 4, heading)
        body_text(text, line_h=4)
        pdf.ln(1)

    pdf.ln(1)

    # ── DANGER STORIES ─────────────────────────────────────────────
    section_header("Danger Stories (for Q&A)")

    dangers = [
        ("Skeletal survey (P4):",
         "Sheriff Report: \"no fractures.\" Medical Records: 2 fractures (femur + humerus). "
         "7/8 doc agents repeated the Sheriff's version. Attorney misses abuse evidence."),
        ("Misattribution (P2):",
         "4/8 doc agents attributed Dena's \"8 PM\" to Marcus. Real fact, wrong person. "
         "Marcus said \"around ten\" -- a 2-hour gap that changes everything."),
        ("GCC hallucination (P1):",
         "GCC reported \"2:00 AM\" ER arrival. Actual: 3:15 AM. Same wrong answer on "
         "retest -- systematic, not random variance."),
        ("Silent failure (P3/P9):",
         "Web SPA hallucinated a case number. Doc agents found 1/9 TPR cases, never "
         "acknowledged 8 were invisible to them."),
    ]
    for bold_lead, text in dangers:
        bullet(text, bold_lead=bold_lead)

    pdf.ln(1.5)

    # ── FEEDBACK LOOP ──────────────────────────────────────────────
    section_header("The Feedback Loop Story")
    body_text(
        "Before improvements: 2P / 5Pa / 8F. After: 12P / 2Pa / 1F. "
        "5 fixes traced to exact pages in source documents."
    )
    pdf.ln(1)
    body_text(
        "\"When a structured agent fails, you find the missing row, add it, "
        "and verify deterministically. Document agents have no equivalent feedback loop.\"",
        style="I", color=ACCENT
    )

    pdf.ln(2)

    # ── YOUR CLOSE ─────────────────────────────────────────────────
    section_header("Your Close")
    body_text(
        "Neither approach alone is sufficient. Layer both: structured data for precision, "
        "documents for narrative detail. Copilot Studio is the interface, Azure is the engine.",
        font_size=8, style="B", color=NAVY, line_h=4.5
    )
    pdf.ln(1.5)
    body_text(
        "\"The right question isn't 'can I trust the agent?' It's 'does it surface enough "
        "for me to make a better decision, faster?'\"",
        style="I", color=MED
    )

    pdf.ln(2)

    # ── DOCUMENT INDEX ─────────────────────────────────────────────
    section_header("Quick Reference (docs/)")

    refs = [
        ("executive-summary.pdf", "10-page C-suite handoff"),
        ("copilot-studio-testing.md", "Full 110-run results + ground truth"),
        ("architecture.md", "4-tier diagram, networking, auth"),
        ("user-guide.md", "Demo walkthrough, warm-up, prompts"),
        ("improvements-round-1.md", "5 data fixes with before/after"),
    ]
    for filename, desc in refs:
        pdf.set_x(right_x + 4)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(*ACCENT)
        pdf.write(3.8, filename)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(*MED)
        pdf.write(3.8, "  " + desc)
        pdf.ln(4.2)

    right_bottom = pdf.get_y()

    # ── FOOTER ─────────────────────────────────────────────────────
    restore_page_margins()
    footer_y = pdf.h - 14
    pdf.set_y(footer_y)
    pdf.set_draw_color(*DIVIDER)
    pdf.line(page_margin, pdf.get_y(), pdf.w - page_margin, pdf.get_y())
    pdf.ln(2.5)
    pdf.set_font("Helvetica", "I", 6.5)
    pdf.set_text_color(*LIGHT)
    pdf.set_x(page_margin)
    pdf.cell(page_w, 3.5, "125 test runs  |  11 agents  |  10 prompts  |  5 data improvements  |  50 synthetic cases  |  All data is fictional", align="C")
    pdf.ln()
    pdf.set_x(page_margin)
    pdf.cell(page_w, 3.5, "Confidential  |  March 2026  |  Generated from dss-legal-case-agent repo", align="C")

    # ── GUTTER LINE ────────────────────────────────────────────────
    # Draw a subtle vertical divider between columns
    gutter_x = left_x + col_w + gutter / 2
    pdf.set_draw_color(*DIVIDER)
    pdf.set_line_width(0.15)
    pdf.line(gutter_x, col_top, gutter_x, footer_y - 2)
    pdf.set_line_width(0.2)

    # ── SAVE ───────────────────────────────────────────────────────
    restore_page_margins()
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ogs-presenter-guide.pdf")
    pdf.output(out_path)
    print(f"Generated: {out_path}")
    print(f"Left col ends: {left_bottom:.1f}mm  |  Right col ends: {right_bottom:.1f}mm  |  Footer: {footer_y:.1f}mm  |  Page: {pdf.h:.1f}mm")


if __name__ == "__main__":
    build_pdf()
