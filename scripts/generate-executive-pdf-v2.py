"""
Generate the Improving Agents whitepaper v2 PDF — three use cases.
Incorporates Use Case 3 (Policy Compliance / Medicaid chatbot) alongside
the original UC1 (Legal Case Analysis) and UC2 (Investigative Analytics).

Uses fpdf2 for layout and matplotlib for data visualizations (rendered as PNGs).

Usage: python scripts/generate-executive-pdf-v2.py
Output: docs/pdf/phase-2/improving-agents-whitepaper-v2.pdf
"""

from fpdf import FPDF
import os
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np


def sanitize_text(text):
    """Replace Unicode characters that Helvetica cannot render."""
    return (
        text
        .replace("\u2014", " - ")   # em dash (avoid -- which triggers fpdf2 strikethrough)
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

# UC3 accent
TEAL = (0, 137, 123)


class ExecutivePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT)
        self.cell(0, 6, sanitize_text("Agent Fidelity Spectrum for Government AI  |  Whitepaper"), align="L")
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
        self.cell(0, 4, sanitize_text("March 2026  |  v2.0"), align="C")

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

    def sub_subsection_title(self, text):
        self.ln(1)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*DARK)
        self.cell(0, 6, sanitize_text(text), new_x="LMARGIN", new_y="NEXT")
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
                      col_aligns=None, wrap=False):
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
            if wrap:
                cell_heights = []
                for i, val in enumerate(row):
                    h = self.multi_cell(col_widths[i], row_height, sanitize_text(val),
                                        dry_run=True, output="HEIGHT")
                    cell_heights.append(h)
                max_h = max(cell_heights)
                if self.get_y() + max_h > self.h - self.b_margin:
                    self.add_page()
                row_top = self.get_y()
                self.set_fill_color(*bg)
                self.rect(self.l_margin, row_top, sum(col_widths), max_h, "F")
                x = self.l_margin
                for i, val in enumerate(row):
                    self.set_xy(x, row_top)
                    self.set_text_color(*DARK)
                    self.multi_cell(col_widths[i], row_height, sanitize_text(val),
                                    align=col_aligns[i])
                    x += col_widths[i]
                self.set_xy(self.l_margin, row_top + max_h)
            else:
                self.set_fill_color(*bg)
                for i, val in enumerate(row):
                    self.set_text_color(*DARK)
                    self.cell(col_widths[i], row_height, sanitize_text(val), border=0,
                              align=col_aligns[i], fill=True)
                self.ln()

    def level_badge(self, level_num, color, name, y_offset=0):
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

    def numbered_step(self, num, title, text):
        text = sanitize_text(text)
        title = sanitize_text(title)
        circle_r = 4
        circle_d = circle_r * 2
        gap = 3
        indent = self.l_margin + 4
        content_x = indent + circle_d + gap
        content_w = self.w - self.r_margin - content_x
        self.set_font("Helvetica", "B", 9.5)
        title_h = 5.5
        self.set_font("Helvetica", "", 9.5)
        body_h = self.multi_cell(content_w, 5, text, dry_run=True, output="HEIGHT")
        total_h = max(circle_d, title_h + body_h) + 3
        if self.get_y() + total_h > self.h - self.b_margin:
            self.add_page()
        top_y = self.get_y()
        cx = indent + circle_r
        cy = top_y + circle_r
        self.set_fill_color(*ACCENT)
        self.ellipse(cx - circle_r, cy - circle_r, circle_d, circle_d, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*WHITE)
        self.set_xy(indent, top_y)
        self.cell(circle_d, circle_d, str(num), align="C")
        self.set_xy(content_x, top_y + 0.5)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*NAVY)
        self.cell(content_w, title_h, title)
        self.set_xy(content_x, top_y + title_h + 1)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*DARK)
        old_l_margin = self.l_margin
        self.l_margin = content_x
        self.multi_cell(content_w, 5, text)
        self.l_margin = old_l_margin
        self.ln(1)

    def callout_box(self, title, text, height=None):
        pad = 5
        box_w = self.w - self.l_margin - self.r_margin
        inner_w = box_w - pad * 2
        self.set_font("Helvetica", "B", 11)
        title_h = 7
        self.set_font("Helvetica", "", 10)
        body_h = self.multi_cell(inner_w, 6, sanitize_text(text), dry_run=True, output="HEIGHT")
        total_h = height or (pad + title_h + 2 + body_h + pad)
        if self.get_y() + total_h > self.h - self.b_margin:
            self.add_page()
        self.set_fill_color(*GRAY_BG)
        self.set_draw_color(*ACCENT)
        box_y = self.get_y()
        self.rect(self.l_margin, box_y, box_w, total_h, "FD")
        self.set_xy(self.l_margin + pad, box_y + pad)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*NAVY)
        self.cell(0, title_h, sanitize_text(title))
        self.set_xy(self.l_margin + pad, box_y + pad + title_h + 2)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        self.multi_cell(inner_w, 6, sanitize_text(text))
        self.set_y(box_y + total_h + 4)


# ========================================================================
# Chart generation (matplotlib -> PNG -> embedded in PDF)
# ========================================================================

CHART_NAVY = "#163052"
CHART_ACCENT = "#2962A3"
CHART_DARK = "#282828"
CHART_MED = "#5A5A5A"
CHART_LIGHT = "#828282"
CHART_GREEN = "#22A652"
CHART_RED = "#B92D2D"
CHART_AMBER = "#D4A017"
CHART_TEAL = "#00897B"


def _apply_chart_style(ax, title=None):
    """Apply consistent whitepaper styling to a matplotlib axis."""
    ax.set_facecolor("#f8f9fa")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(colors="#666666", labelsize=8)
    ax.grid(axis="y", alpha=0.2, linewidth=0.5)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", color=CHART_NAVY, pad=12)


def generate_uc3_bubble_chart(out_path):
    """UC3 retrieval method vs accuracy bubble chart."""
    agents = [
        ("DHHS KB\nBaseline*", "Knowledge\nBase Upload", "Adjusted", 57),
        ("GCC KB\nBaseline", "Knowledge\nBase Upload", "Original", 39),
        ("GCC KB\nxRef", "Knowledge\nBase Upload", "Enriched", 91),
        ("GCC SP\nBaseline", "SharePoint\nSearch", "Original", 39),
        ("GCC SP\nXRef", "SharePoint\nSearch", "Enriched", 52),
        ("GCC SP\nXRef+Meta", "SharePoint\nSearch", "Enriched", 61),
        ("GCC SP\nXRef PDF", "SharePoint\nSearch", "Enriched", 39),
        ("COM SP\nGPT-4.1", "SharePoint\nSearch", "Original", 39),
        ("GCC\nWeb", "Website\nKB", "Original", 39),
        ("AI Search\nBaseline", "Azure AI\nSearch", "Original", 70),
        ("AI Search\nEnriched", "Azure AI\nSearch", "Enriched", 91),
        ("CPS + AI\nSearch", "Azure AI\nSearch", "Enriched", 91),
    ]

    retrieval_order = [
        "SharePoint\nSearch",
        "Website\nKB",
        "Knowledge\nBase Upload",
        "Azure AI\nSearch",
    ]
    retrieval_x = {r: i for i, r in enumerate(retrieval_order)}

    doc_colors = {
        "Original": "#e74c3c",
        "Enriched": "#2ecc71",
        "Adjusted": "#f39c12",
    }

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    fig.patch.set_facecolor("white")
    _apply_chart_style(ax, "Agent Accuracy by Retrieval Method & Document Quality")

    # Vertical bands
    for i in range(len(retrieval_order)):
        color = "#eef1f5" if i % 2 == 0 else "#f8f9fa"
        ax.axvspan(i - 0.48, i + 0.48, color=color, zorder=0)

    for label, retrieval, doc_type, pct in agents:
        x_base = retrieval_x[retrieval]
        color = doc_colors[doc_type]

        same_group = [a for a in agents if a[1] == retrieval]
        idx_in_group = next(j for j, a in enumerate(same_group) if a[0] == label)
        n_in_group = len(same_group)
        spread = min(0.36, 0.12 * n_in_group)
        x_off = np.linspace(-spread, spread, n_in_group)[idx_in_group] if n_in_group > 1 else 0
        x_pos = x_base + x_off

        bubble_size = 650 if pct >= 70 else 420
        ax.scatter(x_pos, pct, s=bubble_size, c=color, alpha=0.85,
                   edgecolors="white", linewidth=2, zorder=3)
        ax.text(x_pos, pct, f"{pct}%", ha="center", va="center",
                fontsize=8, fontweight="bold", color="white", zorder=4)

        y_off = -6 if pct >= 70 else 5.5
        va = "top" if pct >= 70 else "bottom"
        ax.annotate(label, (x_pos, pct),
                    textcoords="offset points", xytext=(0, y_off),
                    ha="center", va=va, fontsize=6, color="#444444", linespacing=0.85)

    # Reference lines
    ax.axhline(y=91, color="#27ae60", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.text(len(retrieval_order) - 0.45, 92.5, "91% target", fontsize=7,
            color="#27ae60", ha="right", style="italic")
    ax.axhline(y=70, color="#f39c12", linestyle="--", linewidth=0.8, alpha=0.4)
    ax.text(len(retrieval_order) - 0.45, 71.5, "70% baseline", fontsize=7,
            color="#d4a017", ha="right", style="italic")

    ax.set_xticks(range(len(retrieval_order)))
    ax.set_xticklabels(retrieval_order, fontsize=9, fontweight="bold",
                       color="#333333", linespacing=0.85)
    ax.set_ylabel("Accuracy (%)", fontsize=10, fontweight="bold", color="#333333")
    ax.set_ylim(25, 102)
    ax.set_xlim(-0.6, len(retrieval_order) - 0.4)

    legend_patches = [
        mpatches.Patch(color="#e74c3c", alpha=0.85, label="Original Documents"),
        mpatches.Patch(color="#2ecc71", alpha=0.85, label="Enriched Documents"),
        mpatches.Patch(color="#f39c12", alpha=0.85, label="Adjusted (independent review)"),
    ]
    ax.legend(handles=legend_patches, loc="upper left", fontsize=8,
              framealpha=0.95, edgecolor="#dddddd", fancybox=True)

    plt.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close()


def generate_heatmap(out_path):
    """Iterative improvement heatmap: agents x rounds."""
    agents = [
        "Case Analyst (MCP)",
        "CS MCP/Com",
        "CS SP/PDF/Com",
        "Investigative (SDK)",
        "Triage (SK)",
        "Foundry Agent",
        "CS SP/PDF/GCC",
        "CS MCP/GCC",
        "CS DV MCP/GCC",
    ]
    # Scores: Round 0, Round 1, Round 2 (out of 10)
    scores = np.array([
        [10,  10,  10],
        [ 8,  10,  10],
        [ 8,  10,  10],
        [ 1,   8,  10],
        [ 0,   1,  10],
        [ 4,   8,   9],
        [ 3,   7,   9],
        [ 2,   4,   4],
        [ 1,   1, 3.2],
    ])
    rounds = ["Round 0\nBaseline", "Round 1\nFix Foundations", "Round 2\nRefine & Optimize"]

    fig, ax = plt.subplots(figsize=(7, 5))
    fig.patch.set_facecolor("white")

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "fidelity", ["#d32f2f", "#ff9800", "#fdd835", "#66bb6a", "#2e7d32"], N=256
    )
    norm = plt.Normalize(vmin=0, vmax=10)

    # Draw cells
    for i in range(len(agents)):
        for j in range(len(rounds)):
            val = scores[i, j]
            color = cmap(norm(val))
            rect = plt.Rectangle((j, len(agents) - 1 - i), 1, 1,
                                  facecolor=color, edgecolor="white", linewidth=2)
            ax.add_patch(rect)
            # Text: dark on light cells, white on dark cells
            text_color = "white" if val <= 4 else "#1a1a1a"
            display_val = f"{val:.1f}" if val != int(val) else f"{int(val)}"
            ax.text(j + 0.5, len(agents) - 1 - i + 0.5, f"{display_val}/10",
                    ha="center", va="center", fontsize=10, fontweight="bold",
                    color=text_color)

    ax.set_xlim(0, len(rounds))
    ax.set_ylim(0, len(agents))
    ax.set_xticks([j + 0.5 for j in range(len(rounds))])
    ax.set_xticklabels(rounds, fontsize=9, fontweight="bold", color="#333333",
                       linespacing=0.85)
    ax.set_yticks([i + 0.5 for i in range(len(agents))])
    ax.set_yticklabels(list(reversed(agents)), fontsize=8.5, color="#333333")
    ax.tick_params(length=0)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title("Score Progression Across Testing Rounds (UC1 & UC2)",
                 fontsize=12, fontweight="bold", color=CHART_NAVY, pad=14)

    # Arrows showing improvement direction
    ax.annotate("", xy=(2.85, len(agents) + 0.1), xytext=(0.15, len(agents) + 0.1),
                arrowprops=dict(arrowstyle="->", color=CHART_ACCENT, lw=1.5))
    ax.text(1.5, len(agents) + 0.35, "Iterative Improvement",
            ha="center", fontsize=8, color=CHART_ACCENT, style="italic")

    plt.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close()


def generate_model_gap_chart(out_path):
    """Bar chart comparing model performance at Level 4."""
    categories = [
        "Data Agents\n(Structured)",
        "Document Agents\n(SharePoint)",
        "Dataverse MCP\n(Native Connector)",
    ]
    gpt41_scores = [9.5, 10, 6]       # GPT-4.1 / Sonnet on DV
    gpt4o_scores = [4, 8, 3.2]        # GPT-4o
    bar_labels_41 = ["9.5/10", "10/10", "6/11*"]
    bar_labels_4o = ["4/10", "8/10", "3.2/11*"]

    x = np.arange(len(categories))
    width = 0.32

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    fig.patch.set_facecolor("white")
    _apply_chart_style(ax, "The Model Gap: GPT-4.1 vs GPT-4o at Level 4")

    bars1 = ax.bar(x - width/2, gpt41_scores, width, label="GPT-4.1 (Commercial)",
                   color=CHART_ACCENT, alpha=0.9, edgecolor="white", linewidth=1)
    bars2 = ax.bar(x + width/2, gpt4o_scores, width, label="GPT-4o (GCC)",
                   color="#e57373", alpha=0.9, edgecolor="white", linewidth=1)

    # Score labels on bars
    for bar, label in zip(bars1, bar_labels_41):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                label, ha="center", va="bottom", fontsize=9, fontweight="bold",
                color=CHART_NAVY)
    for bar, label in zip(bars2, bar_labels_4o):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                label, ha="center", va="bottom", fontsize=9, fontweight="bold",
                color="#c62828")

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9, fontweight="bold", color="#333333",
                       linespacing=0.85)
    ax.set_ylabel("Score", fontsize=10, fontweight="bold", color="#333333")
    ax.set_ylim(0, 12)
    ax.legend(fontsize=9, framealpha=0.95, edgecolor="#dddddd", fancybox=True,
              loc="upper right")

    # Annotation
    ax.annotate("Same tools, same data\nDifferent model = different result",
                xy=(0, 4), xytext=(0.6, 2),
                fontsize=8, color=CHART_MED, style="italic",
                arrowprops=dict(arrowstyle="->", color="#aaaaaa", lw=1),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff8e1",
                          edgecolor="#f0e0a0", alpha=0.9))

    # Footnote
    ax.text(0.5, -0.12, "* Dataverse MCP scored on 11 prompts; Sonnet 4.6 achieved 11/11 (not shown)",
            transform=ax.transAxes, fontsize=7, color="#999999", ha="center", style="italic")

    plt.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close()


def build_pdf():
    pdf = ExecutivePDF()
    pdf.set_margins(20, 20, 20)

    # Generate chart PNGs in a temp directory
    chart_dir = tempfile.mkdtemp(prefix="wp_charts_")
    chart_bubble = os.path.join(chart_dir, "uc3_bubble.png")
    chart_heatmap = os.path.join(chart_dir, "heatmap.png")
    chart_model = os.path.join(chart_dir, "model_gap.png")
    generate_uc3_bubble_chart(chart_bubble)
    generate_heatmap(chart_heatmap)
    generate_model_gap_chart(chart_model)

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
    pdf.cell(0, 14, "for Government AI", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(180, 200, 220)
    pdf.cell(0, 9, "A five-level framework for measuring AI agent response fidelity", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 12)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 8, "across Copilot Studio, Foundry, and pro-code architectures", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(95)
    pdf.set_draw_color(80, 140, 200)
    pdf.set_line_width(0.4)
    pdf.line(pdf.w * 0.3, pdf.get_y(), pdf.w * 0.7, pdf.get_y())
    pdf.set_line_width(0.2)

    pdf.set_y(103)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 7, "Whitepaper  |  v2.0", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "March 2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Patrick O'Gorman  |  Microsoft", align="C", new_x="LMARGIN", new_y="NEXT")

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
        "Not all AI use cases require the same level of response fidelity, and not all agent "
        "architectures deliver it. This report presents a five-level framework based on "
        "757 empirical test runs across 34 agent configurations and three government use cases."
    ), align="C")

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 7, sanitize_text(
        "757 test runs  |  34 agents  |  6 models  |  45 prompts  |  3 use cases"
    ), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 6, sanitize_text(
        "The agent accelerates the human; it does not replace them. "
        "Mandatory human review, citation linking, audit logging, and "
        "organizational culture that treats AI output as a draft, never "
        "a decision. Aligned with the NIST AI Risk Management Framework. "
        "This is the only responsible operating model."
    ), align="C")

    # ====================================================================
    # TABLE OF CONTENTS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Contents")
    pdf.ln(4)

    toc_entries = [
        "At a Glance",
        "How This Was Built",
        "The Five Levels",
        "The Iterative Process",
        "Phase 2: Structured API Without MCP",
        "Use Case 3: Policy Compliance",
        "Government Cloud (GCC) Options",
        "Six Findings That Surprised Us",
        "Risk Management and Responsible AI",
        "Conclusion",
        "Appendix: Meet Your Agents",
        "Appendix: Test Prompts",
    ]
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
    # AT A GLANCE
    # ====================================================================
    pdf.add_page()
    pdf.section_title("At a Glance", link=toc_links["At a Glance"])

    total_w = pdf.w - pdf.l_margin - pdf.r_margin

    # -- Summary tile (full width) --
    sum_pad = 5
    sum_stripe = 3
    sum_text_w = total_w - sum_stripe - sum_pad * 2

    intro_text = sanitize_text(
        "This framework is grounded in 757 test runs across 34 agent configurations and 6 models, "
        "3 government use cases, and multiple testing rounds. Four gaps emerged: "
        "model, data, tool, and retrieval. Every gap was fixable, and none required AI expertise. "
        "Better tools, cleaner data, cross-referenced documents, and the right retrieval "
        "infrastructure. Here is what the data says."
    )

    sum_label_h = 5
    pdf.set_font("Helvetica", "", 9)
    text_h = pdf.multi_cell(sum_text_w, 5, intro_text, dry_run=True, output="HEIGHT")
    sum_h = sum_pad * 2 + sum_label_h + text_h
    sum_y = pdf.get_y()

    bg = tuple(int(c * 0.08 + 255 * 0.92) for c in NAVY)
    pdf.set_fill_color(*bg)
    pdf.rect(pdf.l_margin, sum_y, total_w, sum_h, "F")
    pdf.set_fill_color(*NAVY)
    pdf.rect(pdf.l_margin, sum_y, sum_stripe, sum_h, "F")

    content_x = pdf.l_margin + sum_stripe + sum_pad
    pdf.set_xy(content_x, sum_y + sum_pad)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, sum_label_h, "Summary")
    pdf.set_xy(content_x, sum_y + sum_pad + sum_label_h)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(sum_text_w, 5, intro_text)
    pdf.set_y(sum_y + sum_h + 4)

    # -- 4 level tiles (2x2, ~75%) + legend (right ~25%) --
    lvl_grid = [
        [(LVL2_COLOR, "Levels 1 - 2", "Just Works",
          "8/10 with zero customization. Model choice irrelevant."),
         (LVL3_COLOR, "Level 3", "Data Over Documents",
          "MCP outperformed document search on every aggregate query.")],
        [(LVL4_COLOR, "Level 4", "The Inflection Point",
          "Four gaps emerged: model, data, tool, and retrieval. All fixable."),
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

    # Legend tile
    legend_x = pdf.l_margin + tiles_zone_w + legend_gap
    legend_pad = 5
    legend_badge = 5.5
    legend_label_h = 5
    lbg = tuple(int(c * 0.06 + 255 * 0.94) for c in NAVY)
    pdf.set_fill_color(*lbg)
    pdf.rect(legend_x, grid_y, legend_zone_w, grid_total_h, "F")
    pdf.set_fill_color(*NAVY)
    pdf.rect(legend_x, grid_y, 2, grid_total_h, "F")
    lx = legend_x + 2 + legend_pad
    pdf.set_xy(lx, grid_y + legend_pad - 2)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, legend_label_h, "The Five Levels")
    badges_h = len(legend_items) * (legend_badge + 3)
    remaining_h = grid_total_h - legend_pad - legend_label_h - legend_pad
    badge_y_start = grid_y + legend_pad + legend_label_h + (remaining_h - badges_h) / 2
    if badge_y_start < grid_y + legend_pad + legend_label_h:
        badge_y_start = grid_y + legend_pad + legend_label_h
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

    # -- Three UC tiles + Meet Your Agents sidebar --
    uc_tiles = [
        (ACCENT, "Use Case 1", "Legal Case Analysis",
         "A child welfare legal office prepares for hearings by "
         "reconstructing timelines, identifying conflicting witness "
         "statements, and flagging discrepancies across case files.",
         [("50", "cases"), ("277", "people"), ("333", "events"), ("151", "discrepancies")],
         "17 agent configurations"),
        (ACCENT, "Use Case 2", "Investigative Analytics",
         "A municipal investigative unit cross-references property "
         "ownership, code violations, and business registrations to "
         "identify patterns of landlord negligence.",
         [("34M", "rows"), ("584K", "properties"), ("1.6M", "violations")],
         "8 agent configurations"),
        (TEAL, "Use Case 3", "Policy Compliance",
         "A state Medicaid agency tests chatbot accuracy for "
         "caseworker policy lookups across eligibility rules, "
         "resource limits, and procedural guidance.",
         [("37", "chapters"), ("25", "questions"), ("12", "agents")],
         "12 agent configurations"),
    ]
    agent_categories = [
        ((140, 170, 210), "M365 Copilot", "Zero code, platform model"),
        ((80, 130, 185),  "Copilot Studio", "Highly configurable"),
        ((45, 85, 140),   "Foundry", "Agent Service, managed"),
        (NAVY,            "Pro-code", "Full control, custom SDK"),
    ]

    # Force a new page for UC tiles since we now have 3
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 7, "Three Use Cases", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    uc_pad = 4
    uc_stripe = 3
    uc_row_gap = 3
    agents_gap = 4
    agents_zone_w = total_w * 0.22 - agents_gap / 2
    tiles_zone_w2 = total_w - agents_zone_w - agents_gap
    uc_inner_w = tiles_zone_w2 - uc_stripe - uc_pad * 2

    uc_row_heights = []
    for _, label, title, desc, stats, agents_line in uc_tiles:
        pdf.set_font("Helvetica", "B", 7)
        lh = pdf.multi_cell(uc_inner_w, 4, sanitize_text(label), dry_run=True, output="HEIGHT")
        pdf.set_font("Helvetica", "B", 10)
        th = pdf.multi_cell(uc_inner_w, 5.5, sanitize_text(title), dry_run=True, output="HEIGHT")
        pdf.set_font("Helvetica", "", 8)
        dh = pdf.multi_cell(uc_inner_w, 4.5, sanitize_text(desc), dry_run=True, output="HEIGHT")
        uc_row_heights.append(uc_pad + lh + 1 + th + 2 + dh + 2 + 10 + 5 + 3)

    uc_grid_h = sum(uc_row_heights) + uc_row_gap * (len(uc_tiles) - 1)
    uc_grid_y = pdf.get_y()

    tiles_x = pdf.l_margin + agents_zone_w + agents_gap
    cur_y = uc_grid_y
    for idx, (color, label, title, desc, stats, agents_line) in enumerate(uc_tiles):
        rh = uc_row_heights[idx]
        tbg = tuple(int(c * 0.10 + 255 * 0.90) for c in color)
        pdf.set_fill_color(*tbg)
        pdf.rect(tiles_x, cur_y, tiles_zone_w2, rh, "F")
        pdf.set_fill_color(*color)
        pdf.rect(tiles_x, cur_y, uc_stripe, rh, "F")
        cx = tiles_x + uc_stripe + uc_pad
        pdf.set_xy(cx, cur_y + uc_pad)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*color)
        pdf.multi_cell(uc_inner_w, 4, sanitize_text(label))
        pdf.set_x(cx)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(uc_inner_w, 5.5, sanitize_text(title))
        pdf.set_xy(cx, pdf.get_y() + 1)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*MED)
        pdf.multi_cell(uc_inner_w, 4.5, sanitize_text(desc))
        stat_y = pdf.get_y() + 2
        chip_x = cx
        for num, lbl in stats:
            pdf.set_xy(chip_x, stat_y)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(*ACCENT if color == ACCENT else TEAL)
            num_w = pdf.get_string_width(num) + 1
            pdf.cell(num_w, 6, num)
            pdf.set_font("Helvetica", "", 6.5)
            pdf.set_text_color(*MED)
            lbl_w = pdf.get_string_width(sanitize_text(lbl)) + 3
            pdf.cell(lbl_w, 6, sanitize_text(lbl))
            chip_x += num_w + lbl_w
        pdf.set_xy(cx, stat_y + 10)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*DARK)
        pdf.cell(uc_inner_w, 5, sanitize_text(agents_line))
        cur_y += rh + uc_row_gap

    # Meet Your Agents sidebar
    ma_pad = 5
    ma_x = pdf.l_margin
    ma_bg = tuple(int(c * 0.06 + 255 * 0.94) for c in ACCENT)
    pdf.set_fill_color(*ma_bg)
    pdf.rect(ma_x, uc_grid_y, agents_zone_w, uc_grid_h, "F")
    pdf.set_fill_color(*ACCENT)
    pdf.rect(ma_x + agents_zone_w - 2, uc_grid_y, 2, uc_grid_h, "F")
    mx = ma_x + ma_pad
    pdf.set_xy(mx, uc_grid_y + ma_pad - 2)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*ACCENT)
    ma_label_h = 5
    pdf.cell(0, ma_label_h, "Meet Your Agents")
    badge_w = agents_zone_w - ma_pad * 2 - 2
    badge_h = 10
    badge_gap = 3
    items_total_h = len(agent_categories) * badge_h + (len(agent_categories) - 1) * badge_gap
    remaining_h = uc_grid_h - ma_pad - ma_label_h - ma_pad
    item_y_start = uc_grid_y + ma_pad + ma_label_h + (remaining_h - items_total_h) / 2
    if item_y_start < uc_grid_y + ma_pad + ma_label_h:
        item_y_start = uc_grid_y + ma_pad + ma_label_h
    ay = item_y_start
    for color, name, desc in agent_categories:
        pdf.set_fill_color(*color)
        pdf.rect(mx, ay, badge_w, badge_h, "F")
        pdf.set_xy(mx + 2.5, ay + 1)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(badge_w - 5, 4, sanitize_text(name))
        pdf.set_xy(mx + 2.5, ay + 5)
        pdf.set_font("Helvetica", "", 5.5)
        pdf.set_text_color(220, 230, 240)
        pdf.cell(badge_w - 5, 3.5, sanitize_text(desc))
        ay += badge_h + badge_gap
    pdf.set_xy(mx, uc_grid_y + uc_grid_h - ma_pad - 3)
    pdf.set_font("Helvetica", "I", 5.5)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(badge_w, 3, sanitize_text("Full agent reference in Appendix."), align="L")
    pdf.set_y(uc_grid_y + uc_grid_h + 4)

    # ====================================================================
    # HOW THIS WAS BUILT
    # ====================================================================
    pdf.add_page()
    pdf.section_title("How This Was Built", link=toc_links["How This Was Built"])

    pdf.body_text(
        "This project - the code, the data, and the documentation you are reading - "
        "was AI-accelerated. One solution engineer. One AI coding assistant. Three "
        "agency engagements. Six weeks."
    )

    pdf.body_text(
        "Architecture decisions, Azure service selection, schema design, security posture, "
        "and the five-level fidelity framework came from domain expertise and customer conversations.",
        bold_lead="Human-directed."
    )
    pdf.body_text(
        "TypeScript Functions, MCP server, SQL schema, 50 synthetic cases (277 people, "
        "333 timeline events), web UI, eight PDF generators, a 26-slide deck, and "
        "37 enriched policy documents were generated by AI and reviewed by a human.",
        bold_lead="AI-accelerated."
    )
    pdf.body_text(
        "757 test runs across 34 agent configurations and 6 models, scored by hand. Every dangerous "
        "response - hallucinated facts, missed fractures, invented timelines, fabricated policy "
        "procedures - was caught through manual review. That is exactly the point of Level 5.",
        bold_lead="Human-verified."
    )

    # ====================================================================
    # THE FIVE LEVELS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("The Five Levels", link=toc_links["The Five Levels"])

    pdf.body_text(
        "Government agencies deploy AI agents across a spectrum of use cases. "
        "Each level has different fidelity requirements, different failure consequences, "
        "and different engineering investments. This framework helps leaders match their "
        "investment to their risk."
    )

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

    # -- Level 1-2 --
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
        "10 on both use cases with zero customization. **GPT-4o (Government Cloud) and GPT-4.1 (Commercial) performed "
        "identically at this level.** Model choice had no measurable impact at these levels. "
        "Invest in document hygiene (cross-reference headers that point "
        "reviewers to related documents, consistent formatting, meaningful "
        "filenames, metadata tags) rather than custom engineering.",
        bold_lead="What we found:"
    )
    pdf.body_text(
        "Use Case 3 reinforced this dramatically: the same enriched Medicaid policy "
        "documents scored 39% through SharePoint search but 91% through knowledge base "
        "upload. Document quality is necessary but not sufficient - "
        "**retrieval infrastructure determines whether good documents produce good answers.** "
        "See the Use Case 3 section for the full retrieval gap analysis.",
        bold_lead="Use Case 3 confirmed:"
    )
    pdf.body_text(
        "Deploy a Copilot Studio agent with SharePoint or a knowledge base. "
        "This is where most agencies should start. Test retrieval accuracy before "
        "investing in custom engineering.",
        bold_lead="Recommendation:"
    )

    # -- Level 3 --
    pdf.ln(6)
    pdf.level_badge(3, LVL3_COLOR, "Operational Decision Support")
    pdf.ln(2)
    pdf.body_text(
        "Multi-source data aggregation, dashboards-via-conversation, workload triage. "
        "Wrong answers misallocate resources but are verifiable against existing reports."
    )
    pdf.body_text(
        "Aggregate queries (portfolio summaries, citywide statistics, workload counts) "
        "worked reliably across all agent types, including the weakest performers. "
        "**This is where agents with structured data access begin to outperform "
        "document agents,** including both Copilot Studio and pro-code "
        "agents. Live structured data delivers answers "
        "that static documents cannot.",
        bold_lead="What we found:"
    )
    pdf.body_text(
        "Connect agents to structured data sources via Model Context Protocol. "
        "If your operational data already lives in Dataverse, the built-in "
        "Dataverse MCP connector provides this path with zero custom code. "
        "Write clear tool descriptions. Add summary modes for large result sets.",
        bold_lead="Recommendation:"
    )

    # -- Level 4 --
    pdf.add_page()
    pdf.level_badge(4, LVL4_COLOR, "Investigative and Analytical")
    pdf.ln(2)
    pdf.body_text(
        "Timeline reconstruction, discrepancy detection, entity resolution across multiple "
        "data sources. Wrong answers mean missed evidence, false leads, and misdirected "
        "investigations. This is where response fidelity diverges dramatically."
    )

    pdf.subsection_title("The Model Gap")
    pdf.body_text(
        "Among agents with structured data access, GPT-4.1 agents averaged 9.5 out of 10. "
        "The GPT-4o agent scored 4 out of 10. Same tools, same data, same backend. "
        "Tool and prompt engineering alone did not close this gap at Level 4."
        "Document agents showed no model gap (8 out of 10 on both GPT-4o and GPT-4.1)."
    )

    model_headers = ["Model", "Average Score", "Platform"]
    model_widths = [50, 40, 80]
    model_rows = [
        ["GPT-4.1", "9.5 / 10", "Commercial Copilot Studio, Pro-code agents"],
        ["GPT-5 Auto", "9.5 / 10", "Commercial Copilot Studio (identical to 4.1)"],
        ["GPT-4o", "4 / 10", "Government Cloud Copilot Studio"],
        ["Platform-assigned", "2 / 10", "M365 Copilot Commercial (no user control)"],
    ]
    pdf.styled_table(model_headers, model_rows, model_widths, font_size=7.5,
                      col_aligns=["L", "C", "L"])
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.cell(0, 4, "* Ranked by score", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.cell(0, 4, sanitize_text(
        "Dataverse MCP multi-model test (5 models): GPT-4o 3.2/11, GPT-5 Auto 4/11, GPT-4.1 6/11, "
        "GPT-5 Reasoning 10/11, Sonnet 4.6 11/11."
    ), new_x="LMARGIN", new_y="NEXT")

    # -- Model Gap Chart --
    pdf.ln(4)
    img_w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.image(chart_model, x=pdf.l_margin, w=img_w)
    pdf.ln(4)

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
        "fixed it with simple engineering."
    )

    tg_headers = ["Issue", "User Input", "In Database", "Agent Result"]
    tg_widths = [30, 42, 42, 56]
    tg_rows = [
        ["Street address", "\"4763 Griscom Street\"", "\"4763 GRISCOM ST\"", "Wrong property 87% of the time"],
    ]
    pdf.styled_table(tg_headers, tg_rows, tg_widths, font_size=7.5,
                      col_aligns=["L", "L", "L", "L"])

    pdf.ln(2)
    pdf.body_text(
        "Purpose-built tools for entity resolution. Models with strong multi-step reasoning (GPT-4.1 in our testing)."
        "Explicit workflow guidance in system prompts. Ground truth test suites with "
        "known answers.",
        bold_lead="Recommendation:"
    )

    # -- The Retrieval Gap (NEW in v2) --
    pdf.ln(1)
    pdf.subsection_title("The Retrieval Gap")
    pdf.body_text(
        "Use Case 3 revealed a fourth gap: even when documents contain the right answer, "
        "the retrieval infrastructure determines whether the agent finds it. The same "
        "enriched Medicaid policy documents produced dramatically different accuracy "
        "depending on how they were indexed and searched."
    )

    rg_headers = ["Retrieval Method", "Accuracy", "Notes"]
    rg_widths = [56, 26, 88]
    rg_rows = [
        ["SharePoint search (baseline)", "39%", "Search index surfaced wrong chapters consistently"],
        ["SharePoint + cross-references", "52%", "Document enrichment improved but did not solve retrieval"],
        ["SharePoint + cross-refs + metadata", "61%", "Six custom metadata columns boosted search relevance"],
        ["Knowledge base upload + cross-refs", "91%", "Bypassed SharePoint search entirely; top performer"],
        ["Azure AI Search + enriched docs", "91%", "Purpose-built retrieval; tied KB upload"],
        ["CPS + AI Search (production agent)", "91%", "Copilot Studio front end with AI Search backend"],
    ]
    pdf.styled_table(rg_headers, rg_rows, rg_widths, font_size=7.5,
                      col_aligns=["L", "C", "L"])

    pdf.ln(2)
    pdf.body_text(
        "Before investing in model upgrades or prompt engineering, verify that "
        "your retrieval infrastructure surfaces the right documents. If it does not, "
        "no model will produce the right answer. Knowledge base upload and Azure AI "
        "Search both solved the retrieval problem in our testing.",
        bold_lead="Recommendation:"
    )

    # -- Level 5 --
    pdf.add_page()
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
        ["Fabricated procedure",
         "Invented a 4-step COLA disregard process\nwith specific dollar amounts not in\nthe policy manual",
         "Caseworker applies non-existent\npolicy to eligibility decision"],
    ]

    line_h = 4
    pad = 2
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(*TABLE_HEADER_BG)
    pdf.set_text_color(*TABLE_HEADER_FG)
    for i, h in enumerate(l5_headers):
        pdf.cell(l5_widths[i], 7, sanitize_text(h), border=0, align="C", fill=True)
    pdf.ln()
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
        total_w_row = sum(l5_widths)
        if y_start + row_h > pdf.h - pdf.b_margin:
            pdf.add_page()
            y_start = pdf.get_y()
            x_start = pdf.get_x()
        pdf.set_fill_color(*bg)
        pdf.rect(x_start, y_start, total_w_row, row_h, "F")
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

    # ====================================================================
    # THE ITERATIVE PROCESS (UC1 & UC2)
    # ====================================================================
    pdf.add_page()
    pdf.section_title("The Iterative Process", link=toc_links["The Iterative Process"])

    pdf.body_text(
        "Deploying an AI agent is not a one-time event. Each round of testing reveals "
        "a different category of failure requiring a different type of fix. Organizations "
        "that skip this process will encounter every failure mode documented here. "
        "This section covers Use Cases 1 and 2. Use Case 3 follows in a dedicated section."
    )

    # -- Round 0 --
    pdf.subsection_title("Round 0: Test Everything")
    pdf.body_text(
        "Without ground truth, you cannot measure improvement. We tested 21 agent "
        "configurations across 20 prompts before making any changes."
    )

    pdf.sub_subsection_title("Document Agents")
    pdf.body_text(
        "12 document agent configurations tested across 10 prompts each "
        "(120 test runs). Scores ranged from 3 out of 10 to 8 out of 10. "
        "Seven of eight missed the skeletal survey discrepancy because the "
        "platform retrieved only one of two conflicting documents."
    )

    pdf.sub_subsection_title("Data Agents")
    pdf.body_text(
        "7 structured data agent configurations tested across 10 prompts each "
        "(70 test runs). Scores ranged from 0 out of 10 to 8 out of 10. The best agent "
        "still missed 2 prompts due to missing data. Address resolution failed "
        "87% of the time with no tool to bridge user input to database identifiers."
    )

    # -- Danger Taxonomy --
    pdf.sub_subsection_title("What We Found")
    pdf.body_text(
        "Testing revealed five categories of AI failure, ranked by severity. These are "
        "not hypothetical. Each was documented across 462 test runs. **Every failure "
        "below occurred in agents that ultimately scored 9 or 10 out of 10** - which "
        "is why human review remains essential regardless of final scores."
    )

    danger_headers = ["Severity", "Failure Mode", "Description", "Example", "Agent(s)"]
    danger_widths = [16, 28, 50, 50, 26]
    danger_rows = [
        ["Critical", "False negative",
         "Data retrieved but not\nrecognized as the answer",
         "Found fentanyl screens,\nthen concluded no drug\ntest results existed",
         "Data Agent"],
        ["Critical", "Reproduced\nmisinformation",
         "Quoted a source whose\ncharacterization was\nmisleading in isolation",
         "Sheriff: 'no fractures';\nmedical records showed\nbilateral fractures",
         "Document Agent"],
        ["High", "Misattribution",
         "Correct fact assigned\nto the wrong person",
         "Mother's '8 PM' attributed\nto father (who said\n'around ten')",
         "Document Agent"],
        ["High", "Hallucinated fact",
         "Invented specific detail\nwith no source",
         "ER arrival at '2:00 AM';\nactual time was 3:15 AM",
         "Data Agent"],
        ["Medium", "Silent failure",
         "No results returned\nwithout warning",
         "Hallucinated case number;\nreturned 1 of 9 results",
         "Both"],
    ]

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(*TABLE_HEADER_BG)
    pdf.set_text_color(*TABLE_HEADER_FG)
    for i, h in enumerate(danger_headers):
        pdf.cell(danger_widths[i], 6, sanitize_text(h), border=0, align="C", fill=True)
    pdf.ln()

    line_h = 3.5
    pad = 1
    pdf.set_font("Helvetica", "", 7)
    for r_idx, row in enumerate(danger_rows):
        bg = ROW_ALT if r_idx % 2 == 0 else ROW_WHT
        y_start = pdf.get_y()
        x_start = pdf.get_x()
        cell_heights = []
        for i, val in enumerate(row):
            pdf.set_font("Helvetica", "B" if i <= 1 else "", 7)
            h = pdf.multi_cell(danger_widths[i], line_h, sanitize_text(val),
                               dry_run=True, output="HEIGHT")
            cell_heights.append(h)
        row_h = max(cell_heights) + pad * 2
        total_w_row = sum(danger_widths)
        if y_start + row_h > pdf.h - pdf.b_margin:
            pdf.add_page()
            y_start = pdf.get_y()
            x_start = pdf.get_x()
        pdf.set_fill_color(*bg)
        pdf.rect(x_start, y_start, total_w_row, row_h, "F")
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
                pdf.set_font("Helvetica", "B", 7)
            else:
                pdf.set_text_color(*DARK)
                pdf.set_font("Helvetica", "B" if i == 1 else "", 7)
            pdf.multi_cell(danger_widths[i], line_h, sanitize_text(val), border=0,
                           align="C" if i <= 1 or i == 4 else "L")
        pdf.set_y(y_start + row_h)

    # -- Baseline Scores --
    pdf.ln(4)
    pdf.sub_subsection_title("Baseline Scores")

    r0_headers = ["Agent", "Score"]
    r0_widths = [130, 40]
    r0_rows = [
        ["Case Analyst Agent (pro-code / MCP Chat)", "10/10"],
        ["Copilot Studio MCP (Commercial)", "8/10"],
        ["Copilot Studio SharePoint/PDF (Commercial)", "8/10"],
        ["Foundry Agent (Foundry Agent Service)", "4/10"],
        ["Copilot Studio SharePoint/PDF (Gov Cloud)", "3/10"],
        ["Copilot Studio MCP (Gov Cloud)", "2/10"],
        ["Investigative Agent (pro-code / OpenAI SDK)", "1/10"],
        ["Copilot Studio Dataverse MCP (Gov Cloud)", "1/10"],
        ["Triage Agent (pro-code / Semantic Kernel)", "0/10"],
    ]
    pdf.styled_table(r0_headers, r0_rows, r0_widths, font_size=7.5)
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 4, sanitize_text(
        "* Ranked by score. Data agents scored on Use Case 2 (investigative analytics). "
        "Document agents scored on Use Case 1 (legal case analysis). "
        "Both document agents also scored 8/10 on UC2 (stable across all rounds)."
    ))

    # -- Round 1 --
    pdf.ln(4)
    pdf.subsection_title("Round 1: Fix the Foundations")

    pdf.body_text(
        "Round 1 targeted two categories: missing data in the database and missing "
        "cross-references in documents."
    )

    pdf.sub_subsection_title("Data Agents")
    pdf.body_text(
        "Narrative facts (drug screens, skeletal survey) were not in the database. "
        "A new address normalization tool eliminated the 87% address resolution "
        "failure rate. Fix: 11 new SQL rows, 1 tool filter, 1 new tool.",
        bold_lead="What changed:"
    )

    pdf.sub_subsection_title("Document Agents")
    pdf.body_text(
        "Cross-reference headers added to all documents listing related documents "
        "and their key findings. No content was altered. Zero code.",
        bold_lead="What changed:"
    )

    r1_headers = ["Agent", "Round 0", "Round 1"]
    r1_widths = [110, 30, 30]
    r1_rows = [
        ["Case Analyst Agent (pro-code / MCP Chat)", "10/10", "10/10"],
        ["Copilot Studio MCP (Commercial)", "8/10", "10/10"],
        ["Copilot Studio SharePoint/PDF (Commercial)", "8/10", "10/10"],
        ["Investigative Agent (pro-code / OpenAI SDK)", "1/10", "8/10"],
        ["Foundry Agent (Foundry Agent Service)", "4/10", "8/10"],
        ["Copilot Studio SharePoint/PDF (Gov Cloud)", "3/10", "7/10"],
        ["Copilot Studio MCP (Gov Cloud)", "2/10", "4/10"],
        ["Copilot Studio Dataverse MCP (Gov Cloud)", "1/10", "1/10"],
        ["Triage Agent (pro-code / Semantic Kernel)", "0/10", "1/10"],
        ["M365 Copilot MCP (Commercial)", "--", "2/10"],
    ]
    pdf.sub_subsection_title("Round 1 Scores")
    pdf.styled_table(r1_headers, r1_rows, r1_widths, font_size=7.5)
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.cell(0, 4, sanitize_text(
        "* Ranked by Round 1 score. M365 Copilot first tested in Round 1. "
        "UC2 scores for data agents; UC1 scores for document agents."
    ), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.body_text(
        "M365 Copilot scored 2/10. Its platform-assigned model, limited tool customization, "
        "and lack of system prompt control made iterative improvement impractical. "
        "Organizations with existing M365 Copilot licenses should use it for Level 1 "
        "tasks (document discovery) and deploy Copilot Studio for anything higher.",
        bold_lead="Why M365 Copilot scored lowest:"
    )

    # -- Round 2 --
    pdf.subsection_title("Round 2: Refine and Optimize")
    pdf.body_text(
        "Round 2 refined MCP tool descriptions, agent system prompts, and SharePoint metadata tags."
    )

    pdf.sub_subsection_title("Data Agents")
    pdf.body_text(
        "Triage Agent underwent five sub-rounds of system prompt and tool description "
        "refinement, climbing from 1/10 to 10/10. Investigative Agent reached 10/10 "
        "with minor tool description adjustments. Foundry Agent improved to 9/10 but its managed orchestration "
        "layer limited tool sequencing on the hardest prompt. GCC MCP remained at 4/10 - the same improvements "
        "that lifted other agents had no effect with GPT-4o at this level, confirming a model-level ceiling for Level 4 workloads.",
        bold_lead="What changed:"
    )

    pdf.sub_subsection_title("Document Agents")
    pdf.body_text(
        "SharePoint metadata tags (document topics, keywords) boosted retrieval "
        "for queries the platform previously missed. Cross-reference headers on "
        "a second case file fixed a missing-document retrieval gap. Still zero code.",
        bold_lead="What changed:"
    )

    pdf.body_text(
        "All other document agents also benefited from "
        "cross-referenced documents: KB/DOCX/Com improved from 6/10 to a perfect "
        "10/10, SP/DOCX/Com from 7/10 to 9/10, "
        "KB/PDF/GCC from 5/10 to 9/10, KB/PDF/Com from 5/10 to 8/10, "
        "KB/DOCX/GCC from 4/10 to 8/10, and SP/DOCX/GCC from 5/10 to 7/10. "
        "The same document hygiene improvements delivered gains across "
        "upload method, file format, and cloud environment.",
        bold_lead="Additional agents retested:"
    )

    r2_headers = ["Agent", "Round 0", "Round 1", "Round 2"]
    r2_widths = [96, 24, 24, 26]
    r2_rows = [
        ["Case Analyst Agent (pro-code / MCP Chat)", "10/10", "10/10", "10/10"],
        ["Copilot Studio MCP (Commercial)", "8/10", "10/10", "10/10"],
        ["Investigative Agent (pro-code / OpenAI SDK)", "1/10", "8/10", "10/10"],
        ["Triage Agent (pro-code / Semantic Kernel)", "0/10", "1/10", "10/10"],
        ["Copilot Studio SharePoint/PDF (Commercial)", "8/10", "10/10", "10/10"],
        ["Copilot Studio DV MCP / Sonnet 4.6 (Commercial)", "--", "--", "10/10"],
        ["Copilot Studio DV MCP / GPT-5 Reasoning (Commercial)", "--", "--", "10/10"],
        ["Copilot Studio SharePoint/PDF (Gov Cloud)", "3/10", "7/10", "9/10"],
        ["Foundry Agent (Foundry Agent Service)", "4/10", "8/10", "9/10"],
        ["Copilot Studio Dataverse MCP / GPT-4.1 (Commercial)", "--", "--", "6/10"],
        ["Copilot Studio MCP (Gov Cloud)", "2/10", "4/10", "4/10"],
        ["Copilot Studio DV MCP / GPT-5 Auto (Commercial)", "--", "--", "4/10"],
        ["Copilot Studio Dataverse MCP (Gov Cloud)", "1/10", "1/10", "3.2/10"],
        ["M365 Copilot MCP (Commercial)", "--", "2/10", "--"],
    ]
    pdf.sub_subsection_title("Round 2 Scores")
    pdf.styled_table(r2_headers, r2_rows, r2_widths, font_size=7.5)
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.cell(0, 4, sanitize_text(
        "* Ranked by Round 2 score. M365 Copilot not retested (platform constraints "
        "prevent iterative improvement). Dataverse MCP agents scored on UC1 prompts against "
        "structured Dataverse data; Sonnet 4.6 achieved 11/11 (perfect), GPT-5 Reasoning 10/11."
    ), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.body_text(
        "Six agents reached 10/10 (including KB/DOCX/Com, which jumped from 6/10 to "
        "a perfect score). Copilot Studio SP/PDF/GCC improved from 3/10 to "
        "9/10 with zero code changes. Every retested document agent improved. "
        "The Triage Agent climbed from 0/10 to 10/10 "
        "across five sub-rounds of prompt and tool refinement. Copilot Studio MCP/GCC "
        "plateaued at 4/10 despite receiving every improvement the other agents received, "
        "confirming a model-level ceiling for these workloads with GPT-4o. "
        "A multi-model test of the native Dataverse MCP connector proved the model is everything: "
        "GPT-4o scored 3.2/11 (best after 6 rounds of optimization), GPT-5 Auto 4/11, GPT-4.1 6/11, GPT-5 Reasoning 10/11, and Sonnet 4.6 achieved a perfect "
        "11/11 on identical schema and data across 5 models. GPT-5 Reasoning nearly matches Sonnet, losing only on a "
        "connector-level abbreviation bug. GPT-5 Auto still performed worse than GPT-4.1.",
        bold_lead="Combined result:"
    )

    # -- Improvement Heatmap --
    pdf.add_page()
    pdf.subsection_title("The Visual Story")
    pdf.body_text(
        "The heatmap below shows how scores progressed across testing rounds. "
        "Green cells represent high fidelity; red cells represent low fidelity. "
        "Every agent above the diagonal improved. The pattern is clear: iterative "
        "testing and targeted fixes work."
    )
    pdf.image(chart_heatmap, x=pdf.l_margin + 10, w=img_w - 20)
    pdf.ln(4)

    # -- The Improvement Playbook --
    pdf.subsection_title("The Improvement Playbook")
    pdf.body_text(
        "Every organization that deploys AI agents should follow this sequence. "
        "Skipping steps does not save time - it hides failures until production."
    )
    pdf.numbered_step(1, "Test with known answers",
        "Without ground truth, you cannot measure improvement. Build a test suite "
        "before you build the agent.")
    pdf.numbered_step(2, "Fix the data",
        "If the answer is not in the data, no model will find it. Make facts "
        "discrete and queryable.")
    pdf.numbered_step(3, "Fix the tools",
        "If the model cannot reach the data, add tools. If it does not know "
        "which tool to use, improve descriptions.")
    pdf.numbered_step(4, "Fix the documents",
        "Invest in document hygiene before custom engineering. Cross-reference "
        "headers, metadata tags, and consistent formatting compound across every "
        "document agent.")
    pdf.numbered_step(5, "Fix the retrieval",
        "Verify that the right documents are being surfaced. If SharePoint search "
        "is the bottleneck, test knowledge base upload or Azure AI Search as "
        "alternative retrieval paths.")
    pdf.numbered_step(6, "Retest after every change",
        "Each fix can introduce new failure modes. Run the full test suite after "
        "every change.")

    # ====================================================================
    # PHASE 2: STRUCTURED API WITHOUT MCP (NEW IN V2)
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Phase 2: Structured API Without MCP",
                      link=toc_links["Phase 2: Structured API Without MCP"])

    pdf.body_text(
        "Phase 1 proved that MCP-backed agents with structured data access dramatically "
        "outperform document-grounded agents at Level 4. But MCP requires a Container App, "
        "custom TypeScript code, and APIM configuration. Many government teams want the "
        "fidelity gains without the infrastructure investment."
    )
    pdf.body_text(
        "Phase 2 tests whether a Power Platform custom connector - which requires zero "
        "code and deploys in under 30 seconds - can deliver comparable fidelity by giving "
        "Copilot Studio the same structured API access through a different path."
    )

    pdf.callout_box(
        "Phase 2 Hypothesis",
        "GCC customers can improve Copilot Studio agent fidelity by adding structured API "
        "tools via custom connectors, without needing MCP infrastructure. A Swagger file and "
        "a single CLI command is all it takes."
    )

    # -- Architecture --
    pdf.subsection_title("What We Built")
    pdf.body_text(
        "The custom connector creates a new data path that reuses the existing backend:"
    )
    pdf.body_text(
        "Copilot Studio Agent -> Custom Connector -> APIM -> Azure Functions -> Azure SQL"
    )
    pdf.body_text(
        "No new backend code was written. The connector calls the same 5 APIM operations "
        "the MCP server uses. Any fidelity difference is attributable to the orchestration "
        "layer, not the data. The entire process took four steps:"
    )

    pdf.numbered_step(1, "Export the APIM Swagger spec",
        "APIM already had a Swagger 2.0 definition. One Azure CLI command exported it.")
    pdf.numbered_step(2, "Enrich the Swagger spec",
        "Added detailed operation descriptions, parameter metadata, example values, and "
        "full response schemas. Copilot Studio uses this metadata to decide when and how "
        "to call each tool.")
    pdf.numbered_step(3, "Generate the API properties file",
        "Power Platform requires a properties file alongside the Swagger spec. One pac "
        "CLI command generated the template.")
    pdf.numbered_step(4, "Deploy to GCC",
        "A single command: pac connector create. The connector appeared in the GCC "
        "environment in under 30 seconds. All 5 operations were immediately available "
        "as tools in Copilot Studio.")

    # -- The 5 operations --
    pdf.ln(2)
    ops_headers = ["Operation", "Route", "Description"]
    ops_widths = [40, 56, 74]
    ops_rows = [
        ["ListCases", "GET /dss/cases", "All cases with metadata"],
        ["GetCaseSummary", "GET /dss/cases/{caseId}", "Case detail + people involved"],
        ["GetTimeline", "GET /dss/cases/{id}/timeline", "Events, optional type filter"],
        ["GetStatements", "GET /dss/cases/{id}/statements", "Witness statements, person filter"],
        ["GetDiscrepancies", "GET /dss/cases/{id}/discrepancies", "Contradictions between accounts"],
    ]
    pdf.styled_table(ops_headers, ops_rows, ops_widths, font_size=7.5,
                      col_aligns=["L", "L", "L"])

    # -- Results --
    pdf.ln(4)
    pdf.subsection_title("Results: 8.5 / 10")
    pdf.body_text(
        "We ran all 19 Phase 1 evaluation prompts against the custom connector agent. "
        "The zero-code agent scored 161/190 (8.5/10), achieving 85% of MCP fidelity "
        "with no custom infrastructure."
    )

    results_headers = ["Section", "Score", "Notes"]
    results_widths = [44, 22, 104]
    results_rows = [
        ["Factual Retrieval (4)", "10.0/10",
         "All 4 prompts perfect. 14 timeline events, all 8 people, all hearings."],
        ["Cross-Referencing (3)", "9.3/10",
         "Exact quotes, side-by-side comparisons. Minor: missed one analytical shift."],
        ["Discrepancies (3)", "6.7/10",
         "Two perfect. One failure: could not resolve ambiguous case reference."],
        ["Filtering (3)", "7.0/10",
         "Two perfect. One failure: resolved 'Webb case' to wrong Webb case."],
        ["Aggregate (4)", "9.3/10",
         "Counted 25 active cases, listed all TPR cases (9). Minor omission on one."],
        ["Stress Tests (2)", "7.5/10",
         "Correct references but missed cross-references and net calculations."],
    ]
    pdf.styled_table(results_headers, results_rows, results_widths, font_size=7.5,
                      col_aligns=["L", "C", "L"], wrap=True)

    # -- Failure analysis --
    pdf.ln(4)
    pdf.subsection_title("Failure Analysis")
    pdf.body_text(
        "The 2 hard failures (0/10 and 1/10) were both orchestration issues, not data "
        "access issues. The connector delivered data correctly on every other prompt. "
        "The failures occurred when GPT-4o could not resolve ambiguous case references:"
    )
    pdf.bullet(
        "Says 'Jaylen' and 'the parents' with no case ID. GPT-4o did not attempt a "
        "ListCases lookup to resolve the implicit reference. The MCP agent handles this "
        "because its orchestration loop is more aggressive about disambiguation.",
        bold_lead="Prompt 3.3 (0/10):"
    )
    pdf.bullet(
        "Says 'the Webb case' but there are two Webb cases in the database. GPT-4o "
        "resolved to the wrong one. When the prompt includes an explicit case ID, the "
        "connector agent performs at MCP-level fidelity.",
        bold_lead="Prompt 4.1 (1/10):"
    )
    pdf.body_text(
        "When prompts include explicit identifiers (case ID, full names), the "
        "custom connector agent scores 10/10 consistently. The gap appears only when "
        "the agent must reason about which entity the user means - an orchestration "
        "problem, not a data access problem. System prompt instructions telling the agent "
        "to always resolve case IDs via ListCases before calling other tools may close "
        "this gap entirely.",
        bold_lead="Pattern:"
    )

    # -- Comparison table --
    pdf.ln(2)
    pdf.subsection_title("Custom Connector vs. MCP")

    cmp_headers = ["Dimension", "MCP Server", "Custom Connector"]
    cmp_widths = [40, 65, 65]
    cmp_rows = [
        ["Code required", "TypeScript MCP server", "None (Swagger file only)"],
        ["Infrastructure", "Container App + ACR", "None"],
        ["Deployment", "Docker build + deploy", "pac connector create"],
        ["Tool discovery", "MCP protocol", "Swagger operation IDs"],
        ["Orchestration", "Server-side (MCP loop)", "Copilot Studio (platform)"],
        ["Model control", "Choose any model", "Platform-assigned (GPT-4o GCC)"],
        ["GCC available", "Yes (custom infra)", "Yes (native)"],
        ["Fidelity (UC1)", "10/10", "8.5/10"],
    ]
    pdf.styled_table(cmp_headers, cmp_rows, cmp_widths, font_size=7.5,
                      col_aligns=["L", "L", "L"])

    pdf.ln(4)
    pdf.callout_box(
        "The Takeaway",
        "A zero-code custom connector delivers 85% of MCP fidelity using the same data, "
        "same endpoints, and the same evaluation prompts. For many government use cases, "
        "this is enough. For the hardest prompts requiring multi-step disambiguation, "
        "MCP's server-side orchestration or a stronger model still wins."
    )

    # ====================================================================
    # USE CASE 3: POLICY COMPLIANCE (NEW IN V2)
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Use Case 3: Policy Compliance",
                      link=toc_links["Use Case 3: Policy Compliance"])

    pdf.body_text(
        "A state Medicaid agency uses a chatbot to help caseworkers look up eligibility "
        "rules, resource limits, and procedural guidance from the Medicaid Policy and "
        "Procedures Manual (MPPM). The existing chatbot had been deployed for several "
        "months. The agency wanted to know: how accurate is it, and can we make it better?"
    )
    pdf.body_text(
        "We tested 12 agent configurations against 25 test questions developed by policy "
        "experts. Questions ranged from simple lookups ('What is the burial fund resource "
        "limit for a couple?') to nuanced policy interpretation ('If a member applying for "
        "ABD reports life insurance with face value $5,000 and cash surrender value $3,000, "
        "is that resource counted under the liberalized policy?')."
    )

    # -- Auditing the Baseline --
    pdf.subsection_title("Auditing the Baseline")
    pdf.body_text(
        "The existing chatbot (GCC Knowledge Base with original documents) was graded at "
        "70% accuracy (16/23) by the customer. When we independently reviewed each response "
        "against the actual policy text, three answers marked 'correct' were factually wrong. "
        "The adjusted accuracy was 57% (13/23)."
    )

    audit_headers = ["Question", "Customer Grade", "Independent Review", "Issue"]
    audit_widths = [30, 28, 28, 84]
    audit_rows = [
        ["COLA disregard", "Correct", "Incorrect",
         "Fabricated a 4-step procedure with invented dollar amounts not in the policy"],
        ["E-signatures\non Form 1282", "Correct", "Incorrect",
         "Stated documents do not mention e-signatures; policy explicitly allows them"],
        ["Life insurance\nfor ABD", "Correct", "Incorrect",
         "Applied $1,500 SSI threshold instead of $10,000 liberalized ABD threshold"],
    ]

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(*TABLE_HEADER_BG)
    pdf.set_text_color(*TABLE_HEADER_FG)
    for i, h in enumerate(audit_headers):
        pdf.cell(audit_widths[i], 7, sanitize_text(h), border=0, align="C", fill=True)
    pdf.ln()
    line_h = 3.5
    pad = 1.5
    pdf.set_font("Helvetica", "", 7)
    for r_idx, row in enumerate(audit_rows):
        bg = ROW_ALT if r_idx % 2 == 0 else ROW_WHT
        y_start = pdf.get_y()
        x_start = pdf.get_x()
        cell_heights = []
        for i, val in enumerate(row):
            pdf.set_font("Helvetica", "B" if i <= 0 else "", 7)
            h = pdf.multi_cell(audit_widths[i], line_h, sanitize_text(val),
                               dry_run=True, output="HEIGHT")
            cell_heights.append(h)
        row_h = max(cell_heights) + pad * 2
        total_w_row = sum(audit_widths)
        if y_start + row_h > pdf.h - pdf.b_margin:
            pdf.add_page()
            y_start = pdf.get_y()
            x_start = pdf.get_x()
        pdf.set_fill_color(*bg)
        pdf.rect(x_start, y_start, total_w_row, row_h, "F")
        for i, val in enumerate(row):
            cell_x = x_start + sum(audit_widths[:i])
            cell_y = y_start + pad + (max(cell_heights) - cell_heights[i]) / 2
            pdf.set_xy(cell_x, cell_y)
            pdf.set_text_color(*DARK)
            pdf.set_font("Helvetica", "B" if i == 0 else "", 7)
            pdf.multi_cell(audit_widths[i], line_h, sanitize_text(val), border=0,
                           align="C" if i in (1, 2) else "L")
        pdf.set_y(y_start + row_h)

    pdf.ln(2)
    pdf.body_text(
        "Five additional responses marked correct or left ungraded contained significant "
        "omissions or inaccuracies. Self-reported accuracy is not ground truth. "
        "Independent review against source policy documents is essential.",
        bold_lead="Key takeaway:"
    )

    # -- The Retrieval Problem --
    pdf.subsection_title("The Retrieval Problem")
    pdf.body_text(
        "The primary driver of incorrect answers was document retrieval failure. "
        "The chatbot consistently retrieved the wrong policy chapters and based its "
        "answers on irrelevant content. Section 300 (Non-MAGI resource and income policy) "
        "was the largest blind spot: 7 of 11 failures involved questions that expected "
        "Section 300 content, but the chatbot retrieved Chapter 403 (Optional State "
        "Supplementation), Chapter 601 (Presumptive Eligibility), or Chapter 703 "
        "(Disability Determination) instead."
    )
    pdf.body_text(
        "The content existed in the enriched documents. The search index failed to "
        "surface it."
    )

    # -- What We Changed --
    pdf.subsection_title("What We Changed")

    pdf.sub_subsection_title("Step 1: Document Enrichment")
    pdf.body_text(
        "The original 20 source documents were processed through an automated enrichment "
        "pipeline that produced 37 individual chapter files. Each enriched document "
        "included metadata headers, inline cross-reference expansions, and a "
        "cross-reference guide listing all related sections. "
        "Result: SharePoint accuracy improved from 39% to 52%."
    )

    pdf.sub_subsection_title("Step 2: SharePoint Metadata")
    pdf.body_text(
        "Six custom metadata columns were added to the SharePoint document library: "
        "Program Type, Key Thresholds, FAQ (natural-language questions), MPPM Section, "
        "and Chapter Number. "
        "Result: SharePoint accuracy improved from 52% to 61%."
    )

    pdf.sub_subsection_title("Step 3: Alternative Retrieval")
    pdf.body_text(
        "The enriched documents were tested through three alternative retrieval paths: "
        "knowledge base upload (bypassing SharePoint search entirely), "
        "Azure AI Search (purpose-built retrieval infrastructure), and "
        "Copilot Studio connected to Azure AI Search via Power Automate. "
        "All three achieved 91% accuracy (21/23) - a 52 percentage point improvement "
        "over the SharePoint baseline with the same documents."
    )

    # -- Content Gaps --
    pdf.subsection_title("Content Gaps")
    pdf.body_text(
        "Three questions remained unanswered across all 12 agents because the source "
        "policy documents do not contain the answer. No amount of engineering can fix "
        "missing source content."
    )

    gap_headers = ["Gap", "Issue", "Recommendation"]
    gap_widths = [34, 68, 68]
    gap_rows = [
        ["1099-R verification",
         "Only 1 mention in entire 37-document corpus. No guidance on pension income verification.",
         "Add 1099-R section to income policy chapters"],
        ["Veterans/VA in\nMAGI context",
         "35 references in Non-MAGI chapters, 0 in MAGI chapters. Chatbot cannot find relevant policy.",
         "Add VA benefits cross-reference to MAGI income chapter"],
        ["Deemed eligible\nnewborn",
         "Only covers adoption scenarios, not general newborn deeming rule.",
         "Expand eligibility chapter to cover all newborn deeming scenarios"],
    ]
    pdf.styled_table(gap_headers, gap_rows, gap_widths, font_size=7.5,
                      col_aligns=["L", "L", "L"], wrap=True)

    # -- UC3 Scores --
    pdf.ln(4)
    pdf.subsection_title("Use Case 3 Scores")

    uc3_headers = ["Agent Configuration", "Score", "Accuracy"]
    uc3_widths = [100, 30, 40]
    uc3_rows = [
        ["GCC KB + Cross-Referenced Docs", "21/23", "91%"],
        ["Azure AI Search + Enriched Docs", "21/23", "91%"],
        ["CPS + AI Search + Enriched Docs (production agent)", "21/23", "91%"],
        ["Azure AI Search + Original Docs", "16/23", "70%"],
        ["GCC SP + Cross-Refs + Metadata", "14/23", "61%"],
        ["GCC SP + Cross-Referenced Docs", "12/23", "52%"],
        ["DHHS GCC KB Baseline (customer-reported)", "16/23", "70%"],
        ["DHHS GCC KB Baseline (adjusted)", "13/23", "57%"],
        ["GCC SP Baseline", "9/23", "39%"],
        ["Commercial SP Baseline (GPT-4.1)", "9/23", "39%"],
        ["GCC Web (Direct Line API)", "9/23", "39%"],
        ["GCC KB + Original Docs", "9/23", "39%"],
        ["GCC SP + Cross-Refs as PDF", "9/23", "39%"],
    ]
    pdf.styled_table(uc3_headers, uc3_rows, uc3_widths, font_size=7.5,
                      col_aligns=["L", "C", "C"])
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 4, sanitize_text(
        "* Ranked by accuracy. Questions 12 and 16 excluded from scoring (not tested across all agents). "
        "SP XRef PDF = 39% confirms SharePoint search is the bottleneck, not file format. "
        "Commercial SP Baseline (GPT-4.1) = 39% confirms the model does not matter when retrieval fails."
    ))

    # -- UC3 Bubble Chart --
    pdf.add_page()
    pdf.subsection_title("The Retrieval Gap, Visualized")
    pdf.body_text(
        "Same enriched documents, four retrieval methods, dramatically different results. "
        "Bubble size reflects accuracy threshold. Green = enriched documents, "
        "red = original documents, orange = adjusted after independent review."
    )
    pdf.image(chart_bubble, x=pdf.l_margin, w=img_w)
    pdf.ln(4)

    pdf.callout_box(
        "The Retrieval Gap in One Line",
        "SharePoint search: 39-61%. Knowledge base upload: 91%. Azure AI Search: 91%. "
        "The retrieval infrastructure is as important as document quality."
    )

    # ====================================================================
    # WHAT GCC CUSTOMERS SHOULD DO
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Government Cloud (GCC) Options",
                      link=toc_links["Government Cloud (GCC) Options"])

    pdf.subsection_title("The Model Gap")
    pdf.body_text(
        "Government Community Cloud currently defaults to GPT-4o for Copilot Studio. "
        "For agents with structured data access, this model scored 4 out of 10 on "
        "Level 4 investigative queries where GPT-4.1 scored 9.5 out of 10. Document agents "
        "were unaffected (8 out of 10 on both models). Tool and prompt "
        "engineering alone did not close the structured data gap at Level 4."
    )

    pdf.body_text(
        "Organizations on Government Cloud have seven practical paths forward today:"
    )

    pdf.numbered_step(1, "Improve document quality",
        "Cross-reference headers and SharePoint metadata tags improved the Government "
        "Cloud document agent from 3 out of 10 to 9 out of 10, surpassing the Commercial "
        "agent. Zero code, zero model dependency.")
    pdf.numbered_step(2, "Fix the retrieval path",
        "Use Case 3 proved that GCC Knowledge Base upload with enriched documents "
        "achieved 91% accuracy where SharePoint search peaked at 61%. "
        "If SharePoint search is the bottleneck, switch to KB upload or Azure AI Search.")
    pdf.numbered_step(3, "Use Copilot Studio document agents for Levels 1-3",
        "GPT-4o is adequate for retrieval and summarization.")
    pdf.numbered_step(4, "Deploy a Foundry Agent",
        "Zero to low code (portal or SDK) using Azure OpenAI GPT-4.1 for Level 4 "
        "and 5 workloads.")
    pdf.numbered_step(5, "Build a fully custom agent",
        "Use Azure OpenAI GPT-4.1 directly for maximum control over orchestration, "
        "tools, and evaluation.")
    pdf.numbered_step(6, "Use the Dataverse MCP connector",
        "If case data lives in Dataverse, give Copilot Studio agents structured data "
        "access without building custom APIs.")
    pdf.numbered_step(7, "Monitor GCC model updates",
        "When GPT-4.1 becomes available in Government Cloud, Copilot Studio agents "
        "will benefit immediately.")

    pdf.ln(2)
    pdf.body_text(
        "These options are not mutually exclusive. Most organizations will combine "
        "document agents for everyday queries with a structured data agent for "
        "investigative workloads. The table below shows how engineering investment "
        "scales across these approaches."
    )

    pdf.subsection_title("The Code Investment Spectrum")
    pdf.body_text(
        "This table shows the agent-side investment. MCP-connected agents need an MCP "
        "server. If your data lives in Dataverse, the built-in Dataverse MCP connector "
        "eliminates that step. For any other data source, building a custom MCP server "
        "and backing APIs is a separate pro-code investment. Once that foundation is in "
        "place, the agent-side engineering changes what you can customize, not whether "
        "the agent works."
    )

    code_headers = ["Approach", "Code Required", "Best For"]
    code_widths = [56, 44, 70]
    code_rows = [
        ["M365 Copilot + MCP (Com)", "Config only", "Levels 1-2"],
        ["Copilot Studio + SharePoint", "Config only", "Levels 1-3"],
        ["Copilot Studio + KB Upload", "Config only", "Levels 1-3 (improved retrieval)"],
        ["Copilot Studio + Custom Connector", "Config only", "Levels 1-4 (8.5/10, zero code)"],
        ["Copilot Studio + MCP", "Config only", "Levels 1-4 (Com), 1-3 (GCC)"],
        ["CPS + AI Search + Power Automate", "Low", "Levels 1-3 (best retrieval)"],
        ["Foundry Agent", "Low", "Levels 3-4"],
        ["OpenAI SDK / Semantic Kernel", "Full", "Levels 4-5"],
    ]
    pdf.styled_table(code_headers, code_rows, code_widths, font_size=8)

    pdf.ln(2)
    pdf.body_text(
        "Every architecture scored 9 to 10 out of 10 with GPT-4.1. The investment buys "
        "customization, governance controls, and audit capabilities, all of which matter "
        "most at Levels 4 and 5."
    )

    pdf.ln(2)
    pdf.subsection_title("Why Copilot Studio")
    pdf.body_text(
        "Copilot Studio is the platform that ties the spectrum together. It hosts both "
        "zero-code SharePoint agents (Levels 1-2) and MCP-connected structured data agents "
        "(Levels 3-4) under a single governance boundary. For agencies with data in "
        "Dataverse, the built-in MCP connector means zero custom code for structured "
        "data access. Model flexibility is the headline: "
        "the same Copilot Studio agent configuration scored 4 out of 10 with GPT-4o and "
        "10 out of 10 with GPT-4.1 with no configuration changes required. **When Government "
        "Cloud gains access to models with stronger multi-step reasoning, every Copilot Studio agent improves "
        "overnight.** Enterprise governance (data loss prevention, audit logging, admin "
        "pre-approval for tool calls) and M365 distribution (agents appear in Teams and "
        "Copilot chat) are built into the platform, not bolted on after the fact."
    )

    # ====================================================================
    # SIX SURPRISING FINDINGS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Six Findings That Surprised Us",
                      link=toc_links["Six Findings That Surprised Us"])

    pdf.subsection_title("1. The most dangerous agent was the most faithful to its source")
    pdf.body_text(
        "Seven of eight document agents faithfully reproduced a sheriff's report statement "
        "about fracture findings while the medical records told a different story. The agents "
        "were not wrong about what the document said. They were wrong about what was true."
    )

    pdf.subsection_title("2. A single missing tool caused an 87% failure rate, and simple engineering fixed it")
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

    pdf.subsection_title("5. An advanced agent challenged its own premise, and was right")
    pdf.body_text(
        "The Foundry Agent was asked about a purchase price versus assessment ratio. "
        "Instead of calculating the answer, it checked the source data, found the premise "
        "was wrong, and recalculated using verified numbers. No other agent questioned "
        "the input."
    )

    pdf.subsection_title("6. The customer's own accuracy grading was inflated by 13 percentage points")
    pdf.body_text(
        "When we independently reviewed the existing Medicaid policy chatbot's responses "
        "against the actual policy documents, three answers marked 'correct' by the "
        "customer were factually wrong - fabricated procedures, wrong thresholds, and "
        "misapplied policy frameworks. The true baseline was 57%, not 70%. You cannot "
        "improve what you cannot accurately measure, and self-reported accuracy is not "
        "reliable ground truth."
    )

    # ====================================================================
    # RISK MANAGEMENT AND RESPONSIBLE AI
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Risk Management and Responsible AI",
                      link=toc_links["Risk Management and Responsible AI"])

    pdf.body_text(
        "The fidelity framework presented in this report is not just a testing methodology "
        "- it is a risk-tiering system. Each level maps increasing consequence of failure "
        "to increasing investment in tools, data, models, and human oversight. This aligns "
        "directly with NIST's AI Risk Management Framework (AI 100-1), which provides "
        "the most widely recognized standard for managing AI risk in government."
    )

    pdf.ln(2)
    pdf.subsection_title("Mapping to NIST AI RMF")
    pdf.body_text(
        "The four core functions of NIST AI RMF each have a direct counterpart in this "
        "framework's methodology and findings."
    )

    rmf_headers = ["NIST AI RMF Function", "What This Framework Provides"]
    rmf_widths = [50, 120]
    rmf_rows = [
        ["GOVERN\nEstablish policies and roles\nfor AI risk",
         "Five fidelity levels as a risk-tiering policy.\n"
         "Human-in-the-loop operating model at Level 5.\n"
         "Agent is research assistant, never the decision-maker."],
        ["MAP\nIdentify and contextualize\nAI risks",
         "Danger taxonomy: five failure modes documented\n"
         "across 757 test runs, ranked by severity.\n"
         "Each failure mode traced to specific agent types."],
        ["MEASURE\nQuantify risks with metrics\nand testing",
         "Ground-truth test suites with verified answers.\n"
         "Scoring rubrics applied consistently across 3 use cases.\n"
         "Iterative retesting after every change."],
        ["MANAGE\nAct on risks and monitor\nover time",
         "Improvement Playbook: six-step cycle.\n"
         "Round-over-round regression testing.\n"
         "Model comparison across 6 configurations."],
    ]
    pdf.styled_table(rmf_headers, rmf_rows, rmf_widths, row_height=5, font_size=7.5,
                      col_aligns=["L", "L"])

    pdf.ln(4)
    pdf.subsection_title("Trust but Verify as an Operating Model")
    pdf.body_text(
        "At every level where consequences are material (Level 3 and above), this framework "
        "treats AI output as a draft, never a decision. The agent surfaces evidence, timelines, "
        "and discrepancies. A human reviewer evaluates that output against source records before "
        "any action is taken. This is not a guardrail bolted on after deployment - it is the "
        "design premise of every agent tested in this report."
    )

    pdf.body_text(
        "This framework is complementary to, not a replacement for, an organization's broader "
        "responsible AI governance. The fidelity levels, danger taxonomy, and improvement playbook "
        "are designed to slot into an existing NIST AI RMF process - providing the MEASURE and "
        "MAP functions with empirical data while reinforcing the GOVERN and MANAGE functions "
        "with concrete operating procedures."
    )

    # ====================================================================
    # CONCLUSION
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Conclusion", link=toc_links["Conclusion"])

    pdf.body_text(
        "Not all AI use cases require the same investment. Levels 1 and 2 work with "
        "existing Copilot and Copilot Studio licenses, plus SharePoint document libraries "
        "or knowledge base uploads. From Level 3 onward, structured data connections via MCP "
        "dramatically improve fidelity - whether through Dataverse's built-in MCP connector, "
        "a custom MCP server, or both. The higher the level, the more you also need models "
        "with strong multi-step reasoning (GPT-4.1 in our testing), iterative testing, and "
        "human review workflows."
    )

    pdf.body_text(
        "Use Case 3 added a critical dimension: **retrieval infrastructure matters as "
        "much as document quality.** The same enriched documents scored 39% through "
        "SharePoint search and 91% through knowledge base upload or Azure AI Search. "
        "Organizations should test their retrieval path before investing in model upgrades "
        "or custom engineering."
    )

    pdf.body_text(
        "Copilot Studio agents are included with existing Microsoft 365 and Power Platform "
        "licenses. Foundry and pro-code agents use consumption-based Azure OpenAI pricing. "
        "The licensing cost scales with the level of investment, not the number of agents."
    )

    pdf.ln(6)
    pdf.callout_box(
        "The Bottom Line",
        "The agent is a research assistant, never the decision-maker. At Level 5, "
        "where legal outcomes depend on response fidelity, trust but verify is not a suggestion "
        "- it is the only responsible operating model."
    )
    pdf.ln(2)

    # -- Next Steps --
    pdf.subsection_title("Next Steps")
    pdf.numbered_step(1, "Start simple",
        "Deploy a Copilot Studio agent with SharePoint grounding or knowledge base "
        "upload on a real document library. Measure it against known answers before "
        "customizing anything.")
    pdf.numbered_step(2, "Build your ground truth",
        "Build a 10-prompt test suite with verified answers for your use case. "
        "Independently verify the existing baseline - do not trust self-reported accuracy. "
        "You cannot improve what you cannot measure.")
    pdf.numbered_step(3, "Test the retrieval path",
        "Before investing in model upgrades or custom engineering, verify that your "
        "retrieval infrastructure surfaces the right documents. If it does not, "
        "no model will produce the right answer.")
    pdf.numbered_step(4, "Scale when ready",
        "If your fidelity target exceeds what document agents deliver, connect "
        "structured data via MCP and follow the Improvement Playbook.")
    pdf.numbered_step(5, "Get started",
        "Contact your Microsoft account team to scope a pilot.")

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 5, sanitize_text(
        "Based on 757 test runs across 3 government use cases, 34 agent configurations, "
        "6 models, 45 test prompts, and multiple rounds of iterative improvement."
    ), align="C")

    # ====================================================================
    # APPENDIX: MEET YOUR AGENTS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Appendix: Meet Your Agents", link=toc_links["Appendix: Meet Your Agents"])

    pdf.body_text(
        "Every score in this report comes from one of these agents. "
        "Here is who was tested and how they are built."
    )

    # -- UC1 Table --
    pdf.subsection_title("Use Case 1: Legal Case Analysis (17 Agents)")

    uc1a_headers = ["Agent", "Data Source", "Model", "Final Score"]
    uc1a_widths = [62, 42, 28, 38]
    uc1a_rows = [
        ["Case Analyst Agent (pro-code)", "MCP / SQL", "GPT-4.1", "10/10"],
        ["Copilot Studio MCP/Com", "MCP / SQL", "GPT-4.1", "10/10"],
        ["Copilot Studio SP/PDF/Com", "SharePoint PDFs", "GPT-4.1", "10/10"],
        ["Copilot Studio KB/DOCX/Com", "Uploaded DOCXs", "GPT-4.1", "10/10"],
        ["Copilot Studio DV/Com (Sonnet)", "Dataverse MCP", "Sonnet 4.6", "10/10"],
        ["Copilot Studio DV/Com (5 Reasoning)", "Dataverse MCP", "GPT-5 Reasoning", "10/10"],
        ["Copilot Studio SP/DOCX/Com", "SharePoint DOCXs", "GPT-4.1", "9/10"],
        ["Copilot Studio MCP/GCC", "MCP / SQL", "GPT-4o", "9/10"],
        ["Copilot Studio SP/PDF/GCC", "SharePoint PDFs", "GPT-4o", "9/10"],
        ["Copilot Studio KB/PDF/GCC", "Uploaded PDFs", "GPT-4o", "9/10"],
        ["CS Custom Connector/GCC", "APIM / SQL", "GPT-4o", "8.5/10"],
        ["Copilot Studio KB/PDF/Com", "Uploaded PDFs", "GPT-4.1", "8/10"],
        ["Copilot Studio KB/DOCX/GCC", "Uploaded DOCXs", "GPT-4o", "8/10"],
        ["Copilot Studio SP/DOCX/GCC", "SharePoint DOCXs", "GPT-4o", "7/10"],
        ["Copilot Studio DV/Com (4.1)", "Dataverse MCP", "GPT-4.1", "6/10"],
        ["Copilot Studio DV/Com (5 Auto)", "Dataverse MCP", "GPT-5 Auto", "4/10"],
        ["Copilot Studio DV/GCC", "Dataverse MCP", "GPT-4o", "3.2/10"],
    ]
    pdf.styled_table(uc1a_headers, uc1a_rows, uc1a_widths, font_size=7)
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 4, sanitize_text(
        "Ranked by final score. All agents retested with cross-referenced "
        "documents. PDF outperformed DOCX in 3 of 4 matchups; KB/DOCX/Com "
        "was the exception (10/10). Dataverse MCP tested across 5 models: "
        "Sonnet 4.6 achieved 10/10 (perfect); GPT-5 Reasoning 10/10; GPT-4o/GCC reached 3.2/10 after 6 rounds of optimization."
    ))

    # -- UC2 Table --
    pdf.ln(4)
    pdf.subsection_title("Use Case 2: Investigative Analytics (8 Agents)")

    uc2a_headers = ["Agent", "Platform", "Model", "Final Score"]
    uc2a_widths = [62, 42, 28, 38]
    uc2a_rows = [
        ["Copilot Studio MCP/Com", "Copilot Studio", "GPT-4.1", "10/10"],
        ["Investigative Agent", "OpenAI SDK", "GPT-4.1", "10/10"],
        ["Triage Agent", "Semantic Kernel", "GPT-4.1", "10/10"],
        ["Foundry Agent", "Foundry Agent Service", "GPT-4.1", "9/10"],
        ["Copilot Studio SP/PDF/GCC", "Copilot Studio", "GPT-4o", "9/10"],
        ["Copilot Studio SP/PDF/Com", "Copilot Studio", "GPT-4.1", "8/10"],
        ["Copilot Studio MCP/GCC", "Copilot Studio", "GPT-4o", "4/10"],
        ["M365 Copilot MCP/Com", "M365 Platform", "Platform-assigned", "2/10"],
    ]
    pdf.styled_table(uc2a_headers, uc2a_rows, uc2a_widths, font_size=7)
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 4, sanitize_text(
        "Ranked by final score. Case Analyst Agent tested on UC1 only."
    ))

    # -- UC3 Table --
    pdf.ln(4)
    pdf.subsection_title("Use Case 3: Policy Compliance (12 Agents)")

    uc3a_headers = ["Agent", "Retrieval Method", "Model", "Accuracy"]
    uc3a_widths = [56, 48, 28, 38]
    uc3a_rows = [
        ["GCC KB xRef", "KB Upload", "GPT-4o", "91% (21/23)"],
        ["Azure AI Search Enriched", "AI Search", "GPT-4.1", "91% (21/23)"],
        ["CPS AI Search Enriched", "AI Search + PA", "GPT-4o", "91% (21/23)"],
        ["Azure AI Search Baseline", "AI Search", "GPT-4.1", "70% (16/23)"],
        ["GCC SP XRef + Meta", "SharePoint", "GPT-4o", "61% (14/23)"],
        ["GCC SP XRef", "SharePoint", "GPT-4o", "52% (12/23)"],
        ["DHHS GCC KB Baseline", "KB Upload", "GPT-4o", "57% (13/23)*"],
        ["GCC SP Baseline", "SharePoint", "GPT-4o", "39% (9/23)"],
        ["COM SP Baseline", "SharePoint", "GPT-4.1", "39% (9/23)"],
        ["GCC Web", "Web KB", "GPT-4o", "39% (9/23)"],
        ["GCC KB Baseline", "KB Upload", "GPT-4o", "39% (9/23)"],
        ["GCC SP XRef PDF", "SharePoint", "GPT-4o", "39% (9/23)"],
    ]
    pdf.styled_table(uc3a_headers, uc3a_rows, uc3a_widths, font_size=7)
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 4, sanitize_text(
        "* DHHS baseline adjusted from customer-reported 70% (16/23) to 57% (13/23) after "
        "independent grading review. Ranked by accuracy. PA = Power Automate. "
        "COM SP Baseline (GPT-4.1) = 39% confirms the model is not the bottleneck when retrieval fails."
    ))

    # ====================================================================
    # APPENDIX: TEST PROMPTS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Appendix: Test Prompts", link=toc_links["Appendix: Test Prompts"])

    pdf.body_text(
        "Every agent was tested against the same prompts per use case "
        "to ensure consistent, comparable scoring. Prompts progress from simple "
        "retrieval to multi-step investigative reasoning."
    )

    # -- UC1 Prompts --
    pdf.subsection_title("Use Case 1: DSS Legal (Document Agents)")

    uc1_prompts = [
        ["1", "What was the ER admission time for Jaylen Webb, and who was the nurse?",
         "Simple factual retrieval"],
        ["2", "What did Marcus Webb say to hospital staff vs. law enforcement about the night Jaylen was injured?",
         "Cross-document statement comparison"],
        ["3", "Crystal Price told the court she was 'clean now' at the November 2023 hearing. What do the drug test results show?",
         "Contradiction detection"],
        ["4", "Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey?",
         "Cross-document conflict resolution"],
        ["5", "What is the complete timeline of events for case 2024-DR-42-0892?",
         "Full case narrative assembly"],
        ["6", "List all people involved in the Price TPR case and their roles.",
         "Complete roster extraction"],
        ["7", "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?",
         "Statement evolution tracking"],
        ["8", "What statements were made to law enforcement in case 2024-DR-42-0892?",
         "Filtered statement retrieval"],
        ["9", "Which cases involve Termination of Parental Rights?",
         "Multi-case aggregate query"],
        ["10", "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?",
         "Precision time calculation"],
    ]

    uc1_headers = ["#", "Prompt", "Tests"]
    uc1_widths = [8, 120, 42]
    uc1_aligns = ["C", "L", "L"]
    pdf.styled_table(uc1_headers, uc1_prompts, uc1_widths, font_size=7.5,
                      col_aligns=uc1_aligns, wrap=True)

    # -- UC2 Prompts --
    pdf.subsection_title("Use Case 2: Investigative Analytics (Data Agents)")

    uc2_prompts = [
        ["1", "How many properties does GEENA LLC own, and what percentage are vacant?",
         "Simple fact extraction"],
        ["2", "What happened to 4763 Griscom Street between when GEENA LLC bought it and today?",
         "Cross-source synthesis"],
        ["3", "What was the assessment value of 4763 Griscom Street in 2017, and what is it now? What happened?",
         "Numeric extraction + causation"],
        ["4", "Trace the complete ownership history of 4763 Griscom Street. How many times was it sold at sheriff sale?",
         "Chain reconstruction"],
        ["5", "The transfer records show 4763 Griscom was sold for $146,000 in 2004. What was the fair market value at the time?",
         "Contradiction detection"],
        ["6", "Who are the top 5 private property owners in Philadelphia by code violation count? Exclude government entities.",
         "Citywide aggregate query"],
        ["7", "What financial institutions were involved in the mortgage history of 2400 Bryn Mawr Avenue?",
         "Narrative context extraction"],
        ["8", "How many code violations at 4763 Griscom Street resulted in FAILED inspections, and what type of investigator handles them?",
         "Filtering precision"],
        ["9", "Compare the vacancy rates and violation rates between zip codes 19104 and 19132. Which is worse?",
         "Cross-area aggregate"],
        ["10", "GEENA LLC bought 2400 Bryn Mawr Ave for $230,000 at sheriff sale. The assessed value was $357,100. What percentage discount was that?",
         "Multi-step arithmetic"],
    ]

    uc2_headers = ["#", "Prompt", "Tests"]
    uc2_widths = [8, 120, 42]
    uc2_aligns = ["C", "L", "L"]
    pdf.styled_table(uc2_headers, uc2_prompts, uc2_widths, font_size=7.5,
                      col_aligns=uc2_aligns, wrap=True)

    # -- UC3 Prompts --
    pdf.add_page()
    pdf.subsection_title("Use Case 3: Policy Compliance (Document Agents)")

    uc3_prompts = [
        ["1", "If a person applied for pregnancy coverage and reported 2 months later that pregnancy ended, will they get postpartum coverage?",
         "Policy interpretation"],
        ["1.1", "Is the postpartum period applicable for PW in Emergency coverage?",
         "Follow-up specificity"],
        ["1.2", "Can we assumptively approve Pregnancy women coverage for emergency services?",
         "Policy boundary testing"],
        ["2", "If I transfer $10,000 to my brother, is there a penalty?",
         "Asset transfer rules"],
        ["2.1", "How long is the penalty period?",
         "Calculation methodology"],
        ["3", "Can we re-open an IS application within 30 days if the case was closed due to over resources?",
         "Procedural rule lookup"],
        ["4", "What is the burial fund resource limit for a couple?",
         "Simple threshold lookup"],
        ["5", "Tell me about COLA disregard",
         "Open-ended policy explanation"],
        ["6", "Tell me about AVS",
         "Broad topic retrieval"],
        ["7", "When should an AVS Geo search be requested for a new application?",
         "Procedural specificity"],
        ["8", "When should an AVS FI search be requested for a new application?",
         "Trigger condition identification"],
        ["9", "What process should be followed if an AVS FI search is not returned from the bank?",
         "Fallback procedure"],
        ["10", "When is the cash value of Life insurance counted?",
         "Conditional policy rule"],
        ["10a", "If a member applying for ABD reports Life insurance with FV $5000 and CSV $3000, will that resource be counted?",
         "Scenario-based application"],
        ["10b", "Same question, per liberalized policy?",
         "Policy framework selection"],
        ["13", "Tell me about Income trust",
         "Topic retrieval"],
        ["14", "Can we accept electronic signatures on a 1282?",
         "Specific form policy"],
        ["15", "Can a 1099R Form be used for verification of retirement income?",
         "Document verification rules"],
        ["19", "Do we count Veterans benefits towards MAGI budgeting/PHC?",
         "Cross-program income rules"],
        ["20", "Do we count child's SSA towards MAGI?",
         "Income counting rules"],
        ["21", "Is a child's SSA counted for MAGI categories?",
         "Rephrased consistency test"],
        ["22", "Is a child's SSA counted for MAGI categories? (same question, different user)",
         "Cross-user consistency"],
    ]

    uc3_headers = ["#", "Prompt", "Tests"]
    uc3_widths = [10, 118, 42]
    uc3_aligns = ["C", "L", "L"]
    pdf.styled_table(uc3_headers, uc3_prompts, uc3_widths, font_size=7.5,
                      col_aligns=uc3_aligns, wrap=True)

    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 4, sanitize_text(
        "UC3 prompts developed by state Medicaid policy experts. Questions 12 and 16 excluded from "
        "scoring (not tested across all agents). 23 of 25 questions scored. "
        "All 34 agents across 3 use cases were scored against these prompts."
    ))

    # ====================================================================
    # OUTPUT
    # ====================================================================
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "pdf", "phase-2")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "improving-agents-whitepaper-v2.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")

    # Cleanup temp chart files
    import shutil
    shutil.rmtree(chart_dir, ignore_errors=True)
    print("Chart temp files cleaned up.")


if __name__ == "__main__":
    build_pdf()
