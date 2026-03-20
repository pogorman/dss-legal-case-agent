"""
Generate a briefing PDF: Copilot Studio Knowledge Architecture
Talking points for David Smith / Rod Davis meeting.

Usage: python scripts/generate-doc-hygiene-brief-pdf.py
Output: docs/pdf/document-hygiene-brief.pdf
"""

from fpdf import FPDF
import os


def s(text):
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

RED_BG = (253, 237, 237)
RED_BORDER = (211, 47, 47)
RED_TEXT = (183, 28, 28)

GREEN_BG = (232, 245, 233)
GREEN_BORDER = (76, 175, 80)
GREEN_TEXT = (27, 94, 32)

AMBER_BG = (255, 248, 235)
AMBER_BORDER = (230, 170, 50)
AMBER_TEXT = (183, 110, 30)

ROW_ALT = (241, 245, 249)

BLUE_BG = (232, 240, 254)
BLUE_BORDER = (41, 98, 163)


class BriefPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=False)


def section_header(pdf, x, y, w, num, title):
    """Draw a numbered section header within a column. Returns new y."""
    pdf.set_xy(x, y)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*ACCENT)
    pdf.cell(5, 4, num)
    pdf.set_text_color(*NAVY)
    pdf.cell(w - 5, 4, s(title))
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.3)
    pdf.line(x, y + 4.5, x + w, y + 4.5)
    pdf.set_line_width(0.2)
    return y + 6.5


def bullet(pdf, x, y, w, text, bold_prefix=""):
    """Draw a bullet point within a column. Returns new y."""
    indent = 2.5
    pdf.set_xy(x, y)
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(*MED)
    pdf.cell(indent, 2.8, ">")
    if bold_prefix:
        pdf.set_font("Helvetica", "B", 6)
        pdf.set_text_color(*DARK)
        bw = pdf.get_string_width(s(bold_prefix)) + 0.8
        pdf.cell(bw, 2.8, s(bold_prefix))
        pdf.set_font("Helvetica", "", 6)
        pdf.set_text_color(*DARK)
        remaining_w = w - indent - bw
    else:
        pdf.set_text_color(*DARK)
        remaining_w = w - indent
    pdf.multi_cell(remaining_w, 2.8, s(text))
    return pdf.get_y() + 0.3


def build_pdf():
    pdf = BriefPDF()
    pdf.set_margins(10, 8, 10)
    pdf.add_page()

    uw = pdf.w - pdf.l_margin - pdf.r_margin
    col_gap = 5
    col_w = (uw - col_gap) / 2
    lx = pdf.l_margin
    rx = pdf.l_margin + col_w + col_gap

    # ── Title bar ──
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 13, "F")
    pdf.set_xy(pdf.l_margin, 1.5)
    pdf.set_font("Helvetica", "B", 11.5)
    pdf.set_text_color(*WHITE)
    pdf.cell(uw, 5, "Copilot Studio Knowledge Architecture", align="C")
    pdf.set_xy(pdf.l_margin, 7)
    pdf.set_font("Helvetica", "", 7)
    pdf.cell(uw, 3.5, s("Medicaid Eligibility Policy Agent -- Technical Briefing"),
             align="C")

    # ════════════════════════════════════════════════════════════════════════
    # LEFT COLUMN
    # ════════════════════════════════════════════════════════════════════════
    y = 16

    # ── Questions to Ask ──
    q_items = [
        ("When the agent gives a bad answer, what does 'bad' look like?",
         "Missing key details? Hallucinating facts? Citing the wrong document? "
         "Blending outdated policy versions? Each failure mode points to a "
         "different root cause."),
        ("Have you looked at any sort of document hygiene?",
         "Cross-references between related docs, consistent headings, "
         "metadata tags, meaningful filenames. We saw a 3/10 to 9/10 jump "
         "from document prep alone, zero code."),
    ]

    # Header
    pdf.set_fill_color(*NAVY)
    q_hdr_h = 5
    pdf.rect(lx, y, col_w, q_hdr_h, "F")
    pdf.set_xy(lx + 2, y + 1)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*WHITE)
    pdf.cell(col_w - 4, 3, "QUESTIONS TO ASK")
    y += q_hdr_h

    # Question cards
    for question, subtext in q_items:
        pdf.set_fill_color(*BLUE_BG)
        pdf.set_draw_color(*BLUE_BORDER)
        # Measure heights
        pdf.set_font("Helvetica", "B", 6.5)
        q_h = pdf.multi_cell(col_w - 6, 3, s(question),
                             dry_run=True, output="HEIGHT")
        pdf.set_font("Helvetica", "I", 5.5)
        s_h = pdf.multi_cell(col_w - 6, 2.6, s(subtext),
                             dry_run=True, output="HEIGHT")
        card_h = q_h + s_h + 4
        pdf.rect(lx, y, col_w, card_h, "FD")

        # Question text
        pdf.set_xy(lx + 3, y + 1.5)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(*ACCENT)
        pdf.multi_cell(col_w - 6, 3, s(question))

        # Subtext
        pdf.set_xy(lx + 3, pdf.get_y() + 0.5)
        pdf.set_font("Helvetica", "I", 5.5)
        pdf.set_text_color(*MED)
        pdf.multi_cell(col_w - 6, 2.6, s(subtext))

        y += card_h + 0.5

    y += 2

    # ── 1. How Copilot Studio Retrieves Answers ──
    y = section_header(pdf, lx, y, col_w, "1", "How Copilot Studio Retrieves Answers")

    pdf.set_xy(lx, y)
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(col_w, 2.8, s(
        "Copilot doesn't search your document. It searches a library of "
        "chunks created from your document. The ingestion pipeline:"
    ))
    y = pdf.get_y() + 0.5

    y = bullet(pdf, lx, y, col_w,
               "Breaks each document into smaller passages so they can be "
               "indexed and retrieved. One 40-page PDF becomes ~120 chunks. "
               "Chunk quality determines what's retrievable.",
               "Chunking: ")
    y = bullet(pdf, lx, y, col_w,
               "Each chunk is converted into a numeric vector capturing its "
               "meaning. This enables semantic matching: 'two-factor' matches "
               "'MFA' even though the words differ.",
               "Embeddings: ")
    y = bullet(pdf, lx, y, col_w,
               "User query is vectorized, matched against chunk embeddings, "
               "top results are passed to the model as grounding evidence, "
               "then the model generates a cited answer.",
               "At runtime: ")

    # Key mental model callout
    bh = 5
    pdf.set_fill_color(*BLUE_BG)
    pdf.set_draw_color(*BLUE_BORDER)
    pdf.rect(lx, y, col_w, bh, "FD")
    pdf.set_xy(lx + 2, y + 1)
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_text_color(*ACCENT)
    pdf.cell(col_w - 4, 2.8, s(
        "Chunking = what's retrievable. Embeddings = how it's matched by meaning."
    ))
    y += bh + 2.5

    # ── 2. What You Can (and Can't) Control ──
    y = section_header(pdf, lx, y, col_w, "2", "What You Can (and Can't) Control")

    pdf.set_xy(lx, y)
    pdf.set_font("Helvetica", "B", 5.5)
    pdf.set_text_color(*RED_TEXT)
    pdf.cell(col_w, 2.8, s("You can't control:"))
    y = pdf.get_y() + 3
    y = bullet(pdf, lx, y, col_w,
               "Exact chunk size, overlap, embedding model, indexing algorithm. "
               "Copilot Studio abstracts the entire pipeline.", "")

    pdf.set_xy(lx, y + 0.5)
    pdf.set_font("Helvetica", "B", 5.5)
    pdf.set_text_color(*GREEN_TEXT)
    pdf.cell(col_w, 2.8, s("You CAN control:"))
    y = pdf.get_y() + 3
    y = bullet(pdf, lx, y, col_w,
               "Headings and short sections influence chunk boundaries. "
               "Better structure = more coherent chunks.",
               "Document structure: ")
    y = bullet(pdf, lx, y, col_w,
               "A doc with 12 topics produces blurry embeddings. Split it "
               "into 12 focused docs and retrieval becomes precise.",
               "One topic per doc: ")
    y = bullet(pdf, lx, y, col_w,
               "Scanned/image-only PDFs won't index. Text-based PDF and "
               "DOCX work best. Clean text in, clean chunks out.",
               "File format: ")

    # Symptoms box
    y += 1
    y = section_header(pdf, lx, y, col_w, "", "How to Spot the Problem")
    y = bullet(pdf, lx, y, col_w,
               "Right doc, wrong section. Citations to irrelevant passages. "
               "Cross-section questions fail.",
               "Chunking issues: ")
    y = bullet(pdf, lx, y, col_w,
               "Retrieves content that sounds similar but is semantically off. "
               "Generic policy language instead of the specific answer.",
               "Embedding issues: ")

    # Amber note
    bh = 5
    pdf.set_fill_color(*AMBER_BG)
    pdf.set_draw_color(*AMBER_BORDER)
    pdf.rect(lx, y, col_w, bh, "FD")
    pdf.set_xy(lx + 2, y + 1)
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_text_color(*AMBER_TEXT)
    pdf.cell(col_w - 4, 2.8, s(
        "You usually see chunking issues first. Fix structure before blaming the model."
    ))
    y += bh + 2.5

    # ── Quick Comparison Table ──
    tbl_y = y
    row_h = 2.8
    hdr_h = 3.5
    c1 = 28  # aspect column
    c2 = (col_w - c1) / 2  # direct upload column
    c3 = c2  # SharePoint column

    # Header row
    pdf.set_fill_color(*NAVY)
    pdf.set_font("Helvetica", "B", 5.5)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(lx, tbl_y)
    pdf.cell(c1, hdr_h, "", fill=True)
    pdf.cell(c2, hdr_h, "Direct Upload", align="C", fill=True)
    pdf.cell(c3, hdr_h, "SharePoint Site", align="C", fill=True)
    tbl_y += hdr_h

    tbl_rows = [
        ("Retrieval", "Dataverse vector index", "Graph search (top 3)"),
        ("File cap", "500 files", "No cap"),
        ("Chunking", "Platform-controlled", "None (Graph snippets)"),
        ("Auth required", "None (built-in)", "Entra app reg + consent"),
        ("GCC ready", "Yes", "Partial"),
        ("Governance", "Power Platform DLP", "M365 DLP"),
    ]
    for i, (aspect, upload, sp) in enumerate(tbl_rows):
        bg = ROW_ALT if i % 2 == 0 else WHITE
        pdf.set_fill_color(*bg)
        pdf.set_xy(lx, tbl_y)
        pdf.set_font("Helvetica", "B", 5.5)
        pdf.set_text_color(*DARK)
        pdf.cell(c1, row_h, s(aspect), fill=True)
        pdf.set_font("Helvetica", "", 5.5)
        pdf.cell(c2, row_h, s(upload), align="C", fill=True)
        pdf.cell(c3, row_h, s(sp), align="C", fill=True)
        tbl_y += row_h

    y = tbl_y + 1.5

    # ════════════════════════════════════════════════════════════════════════
    # RIGHT COLUMN
    # ════════════════════════════════════════════════════════════════════════
    y_r = 16

    # ── 3. Document Hygiene ──
    y_r = section_header(pdf, rx, y_r, col_w, "3", "Document Hygiene: The Hidden Variable")

    pdf.set_xy(rx, y_r)
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(col_w, 2.8, s(
        "Direct upload wins on retrieval, but garbage in, garbage out still "
        "applies. These principles determine good answers vs. confidently wrong ones."
    ))
    y_r = pdf.get_y() + 0.5

    y_r = bullet(pdf, rx, y_r, col_w,
                 "Add a header to each document listing related documents "
                 "and their key findings. This was our biggest lever: every "
                 "retested agent improved, average +3 points. The platform "
                 "retrieves one doc; the cross-ref tells the model what else exists.",
                 "Cross-references: ")
    y_r = bullet(pdf, rx, y_r, col_w,
                 "A 40-page policy doc with 12 topics produces worse chunk "
                 "retrieval than 12 focused single-topic docs. Tighter scope = "
                 "better semantic match.",
                 "Single-topic docs: ")
    y_r = bullet(pdf, rx, y_r, col_w,
                 "The file name becomes metadata. 'final_v3_REVISED.docx' "
                 "makes citation and retrieval worse.",
                 "File naming matters: ")
    y_r = bullet(pdf, rx, y_r, col_w,
                 "Scanned/image-only PDFs won't index. Text-based PDF, DOCX, "
                 "TXT work best.",
                 "Format matters: ")
    y_r = bullet(pdf, rx, y_r, col_w,
                 "Sensitivity labels and IRM protection block indexing. "
                 "Files show as 'Ready' but return no answers.",
                 "Labels block indexing: ")

    # ── 4. Split the Work ──
    y_r = section_header(pdf, rx, y_r, col_w, "4", "Split the Work Across Agents")

    pdf.set_xy(rx, y_r)
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(col_w, 2.8, s(
        "One agent with 500 docs retrieves worse than three agents with "
        "150 each. Narrower knowledge scope = better retrieval."
    ))
    y_r = pdf.get_y() + 0.5

    y_r = bullet(pdf, rx, y_r, col_w,
                 "Group docs by topic (eligibility, appeals, provider rules). "
                 "Each agent becomes an expert in its domain.",
                 "Topic agents: ")
    y_r = bullet(pdf, rx, y_r, col_w,
                 "A parent agent routes the question to the right child. "
                 "Copilot Studio supports this natively with agent routing.",
                 "Parent-child pattern: ")
    y_r = bullet(pdf, rx, y_r, col_w,
                 "Each child agent stays under file limits with tighter "
                 "retrieval. The parent never searches documents directly.",
                 "Why it works: ")
    y_r += 1.5

    # ── 5. Model Matters ──
    y_r = section_header(pdf, rx, y_r, col_w, "5", "Model Makes a Difference")

    pdf.set_xy(rx, y_r)
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(col_w, 2.8, s(
        "GCC Copilot Studio currently runs GPT-4o. Our testing showed massive "
        "quality gaps between models on identical infrastructure:"
    ))
    y_r = pdf.get_y() + 0.5

    y_r = bullet(pdf, rx, y_r, col_w,
                 "on same MCP tools + data",
                 "GPT-4o: 3.2/11 ")
    y_r = bullet(pdf, rx, y_r, col_w,
                 "on same MCP tools + data",
                 "GPT-5 Reasoning: 10/11 ")
    y_r = bullet(pdf, rx, y_r, col_w,
                 "on same MCP tools + data",
                 "Claude Sonnet 4.6: 11/11 ")

    # Amber callout
    bh = 8
    pdf.set_fill_color(*AMBER_BG)
    pdf.set_draw_color(*AMBER_BORDER)
    pdf.rect(rx, y_r, col_w, bh, "FD")
    pdf.set_xy(rx + 2, y_r + 1)
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_text_color(*AMBER_TEXT)
    pdf.cell(col_w - 4, 2.8, s("New models are coming to GCC Copilot Studio."))
    pdf.set_xy(rx + 2, y_r + 4)
    pdf.set_font("Helvetica", "", 5.5)
    pdf.set_text_color(*DARK)
    pdf.cell(col_w - 4, 2.8, s(
        "When GPT-4.1 or GPT-5 lands in GCC, answer quality will improve independent of any architecture changes."
    ))
    y_r += bh

    # ════════════════════════════════════════════════════════════════════════
    # BOTTOM — full width
    # ════════════════════════════════════════════════════════════════════════
    y_bottom = max(y, y_r) + 2
    if y_bottom > pdf.h - 24:
        y_bottom = pdf.h - 24

    box_h = 16
    pdf.set_fill_color(*GREEN_BG)
    pdf.set_draw_color(*GREEN_BORDER)
    pdf.rect(pdf.l_margin, y_bottom, uw, box_h, "FD")
    pdf.set_xy(pdf.l_margin + 3, y_bottom + 1.5)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*GREEN_TEXT)
    pdf.cell(uw - 6, 3.5, s("Recommended Sequence"))

    steps = [
        ("1.", "Apply document hygiene to 5-10 representative policy docs (days, not weeks)."),
        ("2.", "Test with direct upload to validate answer quality against known questions."),
        ("3.", "If using SharePoint, fix permissions and site-level URLs, then retest."),
        ("4.", "Only build Power Automate sync after validating quality. Never automate bad answers."),
    ]
    step_y = y_bottom + 5.5
    for num, text in steps:
        pdf.set_xy(pdf.l_margin + 3, step_y)
        pdf.set_font("Helvetica", "B", 6)
        pdf.set_text_color(*GREEN_TEXT)
        pdf.cell(4, 2.6, num)
        pdf.set_font("Helvetica", "", 6)
        pdf.set_text_color(*DARK)
        pdf.cell(uw - 10, 2.6, s(text))
        step_y += 2.8

    # ── Footer ──
    pdf.set_xy(pdf.l_margin, pdf.h - 7)
    pdf.set_font("Helvetica", "I", 5.5)
    pdf.set_text_color(*LIGHT)
    pdf.cell(uw, 3.5, s(
        "Patrick O'Gorman | Microsoft | March 2026"
    ), align="C")

    # Save
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "pdf")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "document-hygiene-brief.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    build_pdf()
