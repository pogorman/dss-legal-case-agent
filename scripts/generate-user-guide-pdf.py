"""
Generate user-guide.pdf with hardcoded content (no markdown file dependency).
Uses fpdf2 -- same self-contained pattern as generate-executive-pdf.py.

Usage: python scripts/generate-user-guide-pdf.py
Output: docs/pdf/user-guide.pdf
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
CODE_BG = (245, 245, 245)
CODE_BORDER = (220, 220, 220)
QUOTE_BG = (248, 249, 252)
QUOTE_BORDER = (41, 98, 163)


class UserGuidePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT)
        self.cell(0, 6, sanitize_text("Agent Accuracy Spectrum for Copilot Studio -- User Guide"), align="L")
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

    def numbered_item(self, number, text, bold_lead=None, indent=8):
        """Render a numbered step with bold number, then text."""
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*ACCENT)
        self.write(5.5, f"{number}. ")
        if bold_lead:
            self.set_text_color(*DARK)
            self.write(5.5, sanitize_text(bold_lead) + "  ")
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*DARK)
        self.multi_cell(self.w - self.r_margin - self.get_x(), 5.5, sanitize_text(text))
        self.ln(1)

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

    def horizontal_rule(self):
        """Draw a horizontal divider line."""
        self.ln(2)
        self.set_draw_color(*DIVIDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)


def build_pdf():
    pdf = UserGuidePDF()
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
    pdf.cell(0, 12, "Agent Accuracy Spectrum for Copilot Studio", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(180, 200, 220)
    pdf.cell(0, 10, "User Guide", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(70)
    pdf.set_draw_color(80, 140, 200)
    pdf.set_line_width(0.4)
    pdf.line(pdf.w * 0.3, pdf.get_y(), pdf.w * 0.7, pdf.get_y())
    pdf.set_line_width(0.2)

    pdf.set_y(78)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 7, "March 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(110)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MED)
    pdf.multi_cell(0, 6.5, sanitize_text(
        "How to use the DSS Legal Case Agent demo application, including the web "
        "interface, agent chat, SharePoint comparison, and Copilot Studio integration."
    ), align="C")

    # ====================================================================
    # ACCESSING THE APPLICATION
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Accessing the Application")

    pdf.numbered_item(1, "Navigate to the Static Web App URL (provided after deployment)")
    pdf.numbered_item(2, "Sign in with your Azure AD credentials")
    pdf.numbered_item(3, "You'll land on the Case Browser -- the main portal page")

    # ====================================================================
    # WARM-UP (BEFORE DEMOS)
    # ====================================================================
    pdf.section_title("Warm-Up (Before Demos)")

    pdf.body_text(
        "Before starting a demo, click the Warm Up button in the header bar. This "
        "primes the entire backend pipeline so the first real query responds quickly."
    )

    pdf.body_text("A popup appears showing three stages:")

    pdf.numbered_item(1, "Wakes the Container App from cold start",
                      bold_lead="Container App --")
    pdf.numbered_item(2, "Establishes the SQL connection pool",
                      bold_lead="Database Connection --")
    pdf.numbered_item(3, "Loads the OpenAI model context",
                      bold_lead="AI Model --")

    pdf.ln(1)
    pdf.body_text(
        "Each stage shows a spinner that transitions to a checkmark with timing. "
        "The popup auto-closes after 4 seconds. No typing required -- one click and wait."
    )

    pdf.callout_box(
        "Tip",
        "Run this 30-60 seconds before your audience arrives. If the Container App "
        "has been idle, the full warm-up takes 10-20 seconds.",
        height=22
    )

    # ====================================================================
    # STATE-GENERIC BRANDING
    # ====================================================================
    pdf.section_title("State-Generic Branding")

    pdf.body_text(
        'The site uses generic "Department of Social Services" and "Office of Legal '
        'Services" branding with no state-specific references. County names, links, '
        "addresses, and legal citations are all genericized. This makes the demo "
        "reusable for any state DSS audience."
    )

    # ====================================================================
    # AGENT CHAT
    # ====================================================================
    pdf.section_title("Agent Chat")

    pdf.body_text(
        "The AI Case Agent is accessed via the floating chat button in the bottom-right "
        "corner of the screen. Click the navy circle with the chat icon to open the "
        "agent widget."
    )

    # -- Suggested Prompts --
    pdf.subsection_title("Suggested Prompts")

    pdf.body_text("On first load, three starter prompts are displayed:")

    pdf.bullet("Returns all cases with IDs, good starting point",
               bold_lead='"List available cases" --')
    pdf.bullet("Chronological events",
               bold_lead='"Give me a detailed timeline for case 2024-DR-42-0892" --')
    pdf.bullet("Conflicting accounts",
               bold_lead='"Show me the discrepancies between the parents\' accounts in case 2024-DR-42-0892" --')

    pdf.ln(1)
    pdf.body_text(
        "Click any prompt chip to send it, or type your own in the text box."
    )

    # -- The Demo Prompt --
    pdf.subsection_title("The Demo Prompt")

    pdf.body_text(
        "For the full demo, use this prompt (replacing names as needed):"
    )

    pdf.blockquote(
        "I represent DSS in case 2024-DR-42-0892. After reviewing the case, can you provide:\n"
        "1. A detailed timeline of pertinent facts with source citations\n"
        "2. A chart of discrepancies between the two parents' accounts\n"
        "3. All statements made by Marcus Webb to case managers or law enforcement\n"
        "4. All statements made by Dena Holloway to case managers or law enforcement"
    )

    pdf.body_text("The agent will call multiple tools and return a structured response with:")

    pdf.bullet(
        "A chronological timeline with dates, times, and source document references"
    )
    pdf.bullet(
        "A comparison table of discrepancies between the parents"
    )
    pdf.bullet(
        "Statements organized by person with dates, recipients, and page citations"
    )

    # -- Tool Badges --
    pdf.subsection_title("Tool Badges")

    pdf.body_text(
        "Below each assistant response, small badges show which tools were called "
        "(e.g., get_timeline, get_discrepancies). This is for transparency -- the "
        "audience can see exactly what data the agent queried."
    )

    # -- Follow-Up Questions --
    pdf.subsection_title("Follow-Up Questions")

    pdf.body_text("You can ask follow-ups in the same conversation:")

    pdf.bullet(
        '"Can you make the timeline more detailed -- include specific times where available?"'
    )
    pdf.bullet(
        '"What did the medical records say about the injuries?"'
    )
    pdf.bullet(
        '"Summarize the GAL\'s recommendation"'
    )

    pdf.ln(1)
    pdf.body_text(
        "The key demo point: follow-up questions return consistent results because "
        "the agent queries the same structured data every time.",
        bold_lead="Consistency:"
    )

    # -- Clearing the Conversation --
    pdf.subsection_title("Clearing the Conversation")

    pdf.body_text(
        "Click the New Chat button in the widget header to reset the conversation. "
        "This clears all messages and returns to the welcome screen with suggested prompts."
    )

    # ====================================================================
    # CASE BROWSER
    # ====================================================================
    pdf.section_title("Case Browser")

    pdf.body_text(
        "The Case Browser is the main content area, always visible behind the chat widget."
    )

    pdf.bullet(
        "The table shows all cases with ID, title, type, county, filed date, and status"
    )
    pdf.bullet(
        "Click a case ID to see details: parties, stat counts (timeline events, "
        "statements, discrepancies)"
    )
    pdf.bullet(
        "This panel is read-only -- it exists to show the demo audience the data structure"
    )

    # ====================================================================
    # TIPS FOR PRESENTERS
    # ====================================================================
    pdf.section_title("Tips for Presenters")

    pdf.numbered_item(1, "in the header to prime the backend (do this before the audience arrives)",
                      bold_lead='Click "Warm Up"')
    pdf.numbered_item(2, "(it's the default view) to establish that structured data exists",
                      bold_lead="Start with Case Browser")
    pdf.numbered_item(3, "in the bottom-right corner to open the agent",
                      bold_lead="Click the chat button")
    pdf.numbered_item(4, "and point out tool badges showing which queries ran",
                      bold_lead="Run the demo prompt")
    pdf.numbered_item(5, "-- prove consistency by asking for the same data in a different way",
                      bold_lead="Run a follow-up")
    pdf.numbered_item(6, "to reset between demo scenarios",
                      bold_lead='Click "New Chat"')
    pdf.numbered_item(7, "(shown separately) -- the contrast sells itself",
                      bold_lead="Compare with SharePoint results")

    # ====================================================================
    # SHAREPOINT COMPARISON DEMO
    # ====================================================================
    pdf.add_page()
    pdf.section_title("SharePoint Comparison Demo")

    # -- Use Case 1 --
    pdf.subsection_title("Use Case 1: DSS Legal Case Analysis")

    pdf.body_text(
        "The sharepoint-docs/ folder contains 11 realistic legal documents for Cases 1 "
        "and 2, ready to upload to SharePoint. These contain the same facts as the SQL "
        "database but in unstructured narrative prose."
    )

    # -- Setting Up the SharePoint Agent --
    pdf.subsection_title("Setting Up the SharePoint Agent")

    pdf.numbered_item(
        1, "Upload all files from sharepoint-docs/Case-2024-DR-42-0892/ and "
           "sharepoint-docs/Case-2024-DR-15-0341/ to a SharePoint document library"
    )
    pdf.numbered_item(
        2, "Create a new Copilot Studio agent grounded in that SharePoint library"
    )
    pdf.numbered_item(
        3, "Use the same prompts on both agents to compare results"
    )

    # -- Comparison Prompts --
    pdf.subsection_title("Comparison Prompts")

    pdf.body_text(
        "See sharepoint-docs/Demo_Comparison_Prompts.md for 19 ready-made prompts "
        "across 6 categories:"
    )

    pdf.numbered_item(1, "-- timelines, dates, names",
                      bold_lead="Factual Retrieval")
    pdf.numbered_item(2, "-- comparing what different people said",
                      bold_lead="Cross-Referencing Statements")
    pdf.numbered_item(3, "-- finding contradictions",
                      bold_lead="Discrepancy Identification")
    pdf.numbered_item(4, "-- medical-only events, law-enforcement-only statements",
                      bold_lead="Filtering and Precision")
    pdf.numbered_item(5, "-- counts, circuit filtering (MCP-only, 50 cases)",
                      bold_lead="Multi-Case / Aggregate Queries")
    pdf.numbered_item(6, "-- page numbers, session counts, time gap calculations",
                      bold_lead="Precision Stress Tests")

    pdf.ln(1)
    pdf.body_text(
        "Each prompt includes expected MCP vs. SharePoint responses and why MCP wins."
    )

    # -- Document Inventory --
    pdf.subsection_title("Document Inventory")

    pdf.body_text("Case 2024-DR-42-0892 (CPS Emergency Removal) -- 6 documents:",
                  bold_lead="")

    doc_headers_1 = ["Document", "Content"]
    doc_widths_1 = [65, 105]
    doc_rows_1 = [
        ["DSS_Investigation_Report.md", "Case manager notes, interviews, recommendations"],
        ["Medical_Records.md", "Hospital admission, radiology, Dr. Chowdhury's assessment, nursing notes"],
        ["Sheriff_Report_24-06-4418.md", "Lt. Odom investigation, parent interviews"],
        ["Court_Orders_and_Filings.md", "Emergency order, probable cause hearing, 30-day review"],
        ["Home_Study_Report.md", "Kinship placement assessment for Theresa Holloway"],
        ["GAL_Report.md", "Karen Milford's Guardian ad Litem report"],
    ]
    pdf.styled_table(doc_headers_1, doc_rows_1, doc_widths_1, font_size=7.5)

    pdf.ln(4)
    pdf.body_text("Case 2024-DR-15-0341 (TPR) -- 5 documents:",
                  bold_lead="")

    doc_rows_2 = [
        ["DSS_Investigation_Report.md", "Full investigation from referral through TPR filing"],
        ["Substance_Abuse_Evaluation.md", "Dr. Ellis clinical eval, OUD diagnosis"],
        ["Court_Orders_and_Filings.md", "All 6 court events including voluntary relinquishment"],
        ["TPR_Petition_and_Affidavit.md", "Formal petition with statutory grounds + sworn affidavit"],
        ["GAL_Reports.md", "Thomas Reed's initial and updated reports"],
    ]
    pdf.styled_table(doc_headers_1, doc_rows_2, doc_widths_1, font_size=7.5)

    # -- Use Case 2 --
    pdf.ln(4)
    pdf.subsection_title("Use Case 2: Philly Poverty Profiteering")

    pdf.body_text(
        "A second document set in sharepoint-docs/Philly-GEENA-LLC/, "
        "sharepoint-docs/Philly-2400-Bryn-Mawr/, and sharepoint-docs/ covers the "
        "Philly use case. These are investigator-style PDF reports about GEENA LLC "
        "and two of its properties, containing data that also lives in the Philly MCP "
        "server's 34M-row SQL database."
    )

    pdf.body_text("Documents (5 PDFs):", bold_lead="")

    pdf.bullet("Entity Investigation Report (GEENA LLC portfolio overview)")
    pdf.bullet("Property Enforcement File: 4763 Griscom Street (violations, demolition)")
    pdf.bullet("Transfer Chain Analysis: 4763 Griscom Street (6-owner chain, two sheriff sales)")
    pdf.bullet("Property Case File: 2400 Bryn Mawr Avenue (stone colonial, condition decline)")
    pdf.bullet("Ownership and Financial History: 2400 Bryn Mawr Avenue (mortgage crisis, foreclosure)")

    pdf.ln(1)
    pdf.body_text(
        "Comparison Prompts: Philly_Comparison_Prompts.pdf has 10 prompts with ground "
        "truth. Prompts 6 and 9 are designed to be impossible for document agents "
        "(require city-wide aggregation). Prompt 7 favors document agents (narrative "
        "about institutional failures).",
        bold_lead=""
    )

    pdf.body_text(
        "Upload the 5 investigation PDFs to SharePoint for the document-backed agent. "
        "Use the same prompts against both the MCP agent and the SharePoint agent."
    )

    # ====================================================================
    # DATABASE ACCESS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Database Access")

    pdf.body_text(
        "The SQL server (philly-stats-sql-01) has public network access disabled. All "
        "application traffic flows through a private endpoint on the VNet."
    )

    # -- Portal Query Editor --
    pdf.subsection_title("Portal Query Editor")

    pdf.body_text(
        "The Azure Portal Query Editor will not work -- it requires public network "
        "access. You'll see this error:"
    )

    pdf.blockquote(
        "An instance-specific error occurred while establishing a connection to SQL "
        "Server. Connection was denied because Deny Public Network Access is set to Yes."
    )

    # -- Running Ad-Hoc Queries --
    pdf.subsection_title("Running Ad-Hoc Queries")

    pdf.body_text("Options for running queries against the database:")

    pdf.numbered_item(1, "from a VNet-connected machine (VM or VPN)",
                      bold_lead="Azure Data Studio / SSMS")
    pdf.numbered_item(2, "on the SQL server, run your query, then disable it again",
                      bold_lead="Temporarily enable public access")
    pdf.numbered_item(3, "with VNet integration (if configured)",
                      bold_lead="Cloud Shell")

    # -- Redeploying Seed Data --
    pdf.subsection_title("Redeploying Seed Data")

    pdf.body_text(
        "The deploy-sql.js script runs from your local machine, so it requires "
        "temporarily enabling public access:"
    )

    pdf.numbered_item(1, "Azure Portal -> SQL Server -> Networking -> Public network "
                         "access -> Selected networks")
    pdf.numbered_item(2, "Add your client IP to the firewall rules")
    pdf.numbered_item(3, "Run node database/deploy-sql.js")
    pdf.numbered_item(4, "Set Public network access back to Disabled")

    # ====================================================================
    # AVAILABLE CASES
    # ====================================================================
    pdf.section_title("Available Cases")

    pdf.body_text(
        "The system contains 50 synthetic cases across multiple judicial circuits."
    )

    # -- Primary Demo Cases --
    pdf.subsection_title("Primary Demo Cases (rich detail)")

    case_headers = ["Case ID", "Description"]
    case_widths = [42, 128]
    case_rows = [
        ["2024-DR-42-0892", "CPS emergency removal -- Webb/Holloway (Spartanburg) -- "
         "14 timeline events, 15 statements, 7 discrepancies"],
        ["2024-DR-15-0341", "Termination of Parental Rights -- Price (Richland) -- "
         "16 timeline events, 12 statements, 4 discrepancies"],
    ]
    pdf.styled_table(case_headers, case_rows, case_widths, font_size=7.5)

    # -- Additional Cases --
    pdf.ln(4)
    pdf.subsection_title("Additional Cases (48 generated)")

    pdf.body_text(
        "Browse all 50 cases in the Case Browser tab. Case types include:"
    )

    pdf.bullet("Child Protective Services")
    pdf.bullet("Termination of Parental Rights")
    pdf.bullet("Child Neglect")
    pdf.bullet("Physical Abuse")
    pdf.bullet("Guardianship")
    pdf.bullet("Kinship Placement")

    pdf.ln(1)
    pdf.body_text("Cases span multiple regions and counties.")

    pdf.horizontal_rule()

    # ====================================================================
    # CONNECTING COPILOT STUDIO TO THE MCP ENDPOINT
    # ====================================================================
    pdf.section_title("Connecting Copilot Studio to the MCP Endpoint")

    pdf.body_text("The MCP endpoint is ready for Copilot Studio at:")

    pdf.code_block([
        "https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/mcp"
    ])

    pdf.ln(2)

    # -- Prerequisites --
    pdf.subsection_title("Prerequisites")

    pdf.bullet("Access to Copilot Studio (https://copilotstudio.microsoft.com)")
    pdf.bullet("An agent created (or create a new one)")
    pdf.bullet("Generative Orchestration must be enabled on the agent (this is required "
               "for MCP tools)",
               bold_lead="Required:")

    # -- Step-by-Step Setup --
    pdf.subsection_title("Step-by-Step Setup")

    pdf.numbered_item(1, "Open your agent in Copilot Studio")
    pdf.numbered_item(2, "Go to the Tools page")
    pdf.numbered_item(3, "Select Add a tool -> New tool -> Model Context Protocol")
    pdf.numbered_item(4, "Fill in the MCP onboarding wizard:")

    pdf.ln(1)
    pdf.bullet("DSS Case Intelligence", bold_lead="Server name:", indent=16)
    pdf.bullet(
        "Queries structured DSS legal case data including timelines, statements, "
        "discrepancies, and party information across 50 synthetic cases. Returns "
        "cited results with source documents and page references.",
        bold_lead="Server description:", indent=16
    )
    pdf.bullet(
        "https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/mcp",
        bold_lead="Server URL:", indent=16
    )
    pdf.bullet("Select None (the endpoint is unauthenticated for this POC)",
               bold_lead="Authentication:", indent=16)

    pdf.ln(1)
    pdf.numbered_item(5, "Select Create")
    pdf.numbered_item(6, "On the Add tool dialog, select Create a new connection")
    pdf.numbered_item(7, "Select Add to agent")

    # -- Verify It Works --
    pdf.subsection_title("Verify It Works")

    pdf.body_text("Once connected, the agent auto-discovers 5 tools:")

    tool_headers = ["Tool", "Description"]
    tool_widths = [52, 118]
    tool_rows = [
        ["list_cases", "Returns all available cases"],
        ["get_case_summary", "Case overview + parties for a specific case"],
        ["get_timeline", "Chronological events with optional type filter"],
        ["get_statements_by_person", "Statements filtered by person name and/or audience"],
        ["get_discrepancies", "Conflicting accounts between parties"],
    ]
    pdf.styled_table(tool_headers, tool_rows, tool_widths, font_size=7.5)

    pdf.ln(3)
    pdf.body_text(
        'Test with: "List available cases" -- the agent should call list_cases and '
        "return all 50 cases."
    )

    pdf.body_text(
        "Then try the money prompt from the demo guide to verify all tools work end-to-end."
    )

    # -- Troubleshooting --
    pdf.subsection_title("Troubleshooting")

    pdf.bullet(
        "Ensure Generative Orchestration is enabled in agent settings",
        bold_lead="Tools not appearing:"
    )
    pdf.bullet(
        "The Container App may need to warm up -- send a quick health check first",
        bold_lead="Connection errors:"
    )
    pdf.bullet(
        "Copilot Studio no longer supports SSE transport (deprecated August 2025). "
        "The DSS endpoint uses Streamable HTTP which is the current supported transport",
        bold_lead="SSE errors:"
    )
    pdf.bullet(
        "Make sure the server description is filled in -- the orchestrator uses it to "
        "decide when to invoke the MCP server",
        bold_lead="Agent not calling tools:"
    )

    # -- Alternative: Custom Connector --
    pdf.subsection_title("Alternative: Custom Connector (Power Apps)")

    pdf.body_text(
        "If the MCP onboarding wizard isn't available in your environment, you can "
        "create a custom connector in Power Apps using the OpenAPI schema provided "
        "in the user guide. Import the YAML and complete the setup."
    )

    # ====================================================================
    # OUTPUT
    # ====================================================================
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "pdf")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "user-guide.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    build_pdf()
