"""
Generate architecture.pdf from hardcoded content.
Uses fpdf2 -- no external dependencies beyond what's already installed.

Usage: python scripts/generate-architecture-pdf.py
Output: docs/pdf/architecture.pdf
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
CODE_BG = (243, 244, 246)


class ArchitecturePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT)
        self.cell(0, 6, sanitize_text("AI Agent Accuracy Spectrum -- Architecture"), align="L")
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

    def numbered_item(self, number, text, indent=8):
        text = sanitize_text(text)
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*MED)
        self.write(5.5, f"{number}. ")
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

    def code_block(self, text):
        """Render a code/ASCII block with monospace font on gray background."""
        text = sanitize_text(text)
        lines = text.split("\n")
        line_h = 3.8
        padding = 4
        block_w = self.w - self.l_margin - self.r_margin
        # Calculate height needed
        block_h = len(lines) * line_h + padding * 2
        # Check if we need a page break
        if self.get_y() + block_h > self.h - 25:
            self.add_page()
        y_start = self.get_y()
        self.set_fill_color(*CODE_BG)
        self.set_draw_color(*DIVIDER)
        self.rect(self.l_margin, y_start, block_w, block_h, "FD")
        self.set_font("Courier", "", 7)
        self.set_text_color(*DARK)
        self.set_xy(self.l_margin + padding, y_start + padding)
        for line in lines:
            self.set_x(self.l_margin + padding)
            self.cell(block_w - padding * 2, line_h, line)
            self.ln(line_h)
        self.set_y(y_start + block_h + 3)


def build_pdf():
    pdf = ArchitecturePDF()
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
    pdf.cell(0, 10, "Architecture", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(65)
    pdf.set_draw_color(80, 140, 200)
    pdf.set_line_width(0.4)
    pdf.line(pdf.w * 0.3, pdf.get_y(), pdf.w * 0.7, pdf.get_y())
    pdf.set_line_width(0.2)

    pdf.set_y(75)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 7, "System Design | March 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(140)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MED)
    pdf.multi_cell(0, 6.5, sanitize_text(
        "Four-tier architecture: SWA, Container App (MCP/Chat), APIM, Azure Functions, "
        "Azure SQL. Nine agent configurations across three data paths."
    ), align="C")

    # ====================================================================
    # OVERVIEW
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Overview")

    pdf.body_text(
        "Four-tier architecture following the same pattern as the philly-profiteering "
        "project. All tiers communicate over HTTPS with managed identity or subscription "
        "key auth."
    )

    pdf.code_block(
        "Copilot Studio Agent (or Web SPA via /chat endpoint)\n"
        "  | Streamable HTTP (MCP), POST /mcp (JSON-RPC 2.0), POST /chat (OpenAI-style)\n"
        "  v\n"
        "Container App: dss-case-agent (Express + TypeScript + Node 20)\n"
        "  Routes: /mcp, /chat, /healthz | Auth: Managed identity (AOAI)\n"
        "  Secrets: APIM subscription key\n"
        "  | HTTPS + Ocp-Apim-Subscription-Key\n"
        "  v\n"
        "Azure API Management (shared)\n"
        "  Product: dss-demo | API: dss-case-api (5 operations)\n"
        "  Policy: inject function key via query param from named value\n"
        "  | HTTPS + ?code= query param\n"
        "  v\n"
        "Azure Functions: dss-demo-func (5 HTTP-triggered functions)\n"
        "  Auth: Managed identity -> SQL | Runtime: Node 20, TypeScript\n"
        "  | Azure AD token\n"
        "  v\n"
        "Azure SQL: dss-demo (5 tables, synthetic data, Private endpoint (VNet))\n"
        "\n"
        "Static Web App: swa-dss-legal-case\n"
        "  Vanilla HTML/CSS/JS | AAD built-in auth\n"
        "  Calls Container App /chat endpoint"
    )

    # ====================================================================
    # COMPONENT DETAILS
    # ====================================================================
    pdf.section_title("Component Details")

    # -- Azure SQL Database --
    pdf.subsection_title("Azure SQL Database (dss-demo)")
    pdf.bullet("Hosted on existing SQL Server (shared with philly-profiteering)")
    pdf.bullet("5 tables: cases, people, timeline_events, statements, discrepancies")
    pdf.bullet("50 synthetic cases: 2 hand-crafted (rich detail) + 48 procedurally generated")
    pdf.bullet("Total: 277 people, 333 timeline events, 338 statements, 151 discrepancies")
    pdf.bullet("Basic tier (5 DTU) -- sufficient for demo")
    pdf.bullet("Accessed via managed identity only (no passwords)")
    pdf.bullet("Public network access: Disabled -- all SQL traffic flows over private endpoint")
    pdf.bullet("Private endpoint pe-sql-philly on subnet snet-private-endpoints (10.0.2.0/24)")
    pdf.bullet("Private DNS zone privatelink.database.windows.net resolves the server FQDN to the private IP")
    pdf.bullet("Portal Query Editor does not work (requires public access) -- use Azure Data Studio or temporarily re-enable public access for ad-hoc queries")

    # -- Azure Functions --
    pdf.subsection_title("Azure Functions (dss-demo-func)")
    pdf.bullet("Node 20, TypeScript, Azure Functions v4")
    pdf.bullet("5 HTTP-triggered functions with function auth level (getStatements supports optional made_to filter)")
    pdf.bullet("System-assigned managed identity with db_datareader on dss-demo")
    pdf.bullet("Flex Consumption plan")
    pdf.bullet("VNet integrated via snet-dss-functions (10.0.3.0/24) -- all outbound traffic routes through the VNet")
    pdf.bullet("vnetRouteAllEnabled: true -- ensures DNS resolution uses the private DNS zones")
    pdf.bullet("SQL connection via @azure/identity DefaultAzureCredential + access token -> private endpoint")
    pdf.bullet("Storage account dssdemofuncsa -- public network access disabled, accessed via private endpoints:")
    pdf.bullet("pe-blob-dss (10.0.2.8), pe-queue-dss (10.0.2.9), pe-table-dss (10.0.2.10)", indent=16)
    pdf.bullet("DNS records in privatelink.blob/queue/table.core.windows.net zones", indent=16)
    pdf.bullet("Identity-based auth (managed identity with Storage Blob Data Owner, Storage Account Contributor, Storage Queue/Table Data Contributor roles)", indent=16)
    pdf.bullet("Deployment via func azure functionapp publish works because Kudu uploads through the VNet -> private endpoint path", indent=16)

    # -- Container App --
    pdf.subsection_title("Container App (dss-case-agent)")
    pdf.bullet("Node 20, TypeScript, Express")
    pdf.bullet("POST /mcp: MCP streamable HTTP transport (JSON-RPC 2.0)")
    pdf.bullet("POST /chat: OpenAI chat completions with tool-calling loop (GPT-4.1)")
    pdf.bullet("GET /healthz: Health check")
    pdf.bullet("System-assigned managed identity with Cognitive Services OpenAI User role")
    pdf.bullet("APIM subscription key stored as Container App secret")

    # -- API Management --
    pdf.subsection_title("API Management (shared instance)")
    pdf.bullet("New product: dss-demo with subscription key requirement")
    pdf.bullet("New API: dss-case-api with 5 GET operations")
    pdf.bullet("Inbound policy injects function key as ?code= query parameter from named value dss-func-key")
    pdf.bullet("Routes: /dss/cases, /dss/cases/{caseId}, etc.")

    # -- Static Web App --
    pdf.subsection_title("Static Web App (swa-dss-legal-case)")
    pdf.bullet("Vanilla HTML/CSS/JS (no framework, no build step)")
    pdf.bullet("AAD built-in authentication")
    pdf.bullet("Modern government-application UI: classification banner, DSS branding, scales of justice logo")
    pdf.bullet("Two panels: Agent Chat (with welcome hero, prompt chips, tool badges) and Case Browser (sortable table, detail views)")
    pdf.bullet("Calls Container App /chat endpoint for agent interaction")
    pdf.bullet("Case Browser uses embedded data (no API dependency)")
    pdf.bullet("AI disclaimer footer, responsive design")

    # ====================================================================
    # AUTHENTICATION FLOW
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Authentication Flow")

    pdf.numbered_item(1, "User -> SWA: AAD built-in auth (/.auth/login/aad)")
    pdf.numbered_item(2, "SWA -> Container App /chat: Direct HTTPS call (CORS enabled)")
    pdf.numbered_item(3, "Container App -> APIM: HTTPS + Ocp-Apim-Subscription-Key header")
    pdf.numbered_item(4, "APIM -> Functions: HTTPS + ?code= query parameter (injected by policy from named value)")
    pdf.numbered_item(5, "Functions -> SQL: Azure AD token via DefaultAzureCredential")
    pdf.numbered_item(6, "Container App -> Azure OpenAI: Azure AD token via DefaultAzureCredential")

    # ====================================================================
    # NETWORK ARCHITECTURE
    # ====================================================================
    pdf.section_title("Network Architecture")

    pdf.body_text(
        "All SQL traffic is private -- the SQL server has public network access disabled."
    )

    pdf.code_block(
        "VNet: vnet-philly-profiteering (10.0.0.0/16)\n"
        "\n"
        "  snet-dss-functions (10.0.3.0/24)         snet-private-endpoints (10.0.2.0/24)\n"
        "  Function App (outbound)                  pe-sql-philly -> SQL Server\n"
        "  dss-demo-func (VNet integration)         pe-blob-philly -> phillyfuncsa\n"
        "                                           pe-queue-philly -> phillyfuncsa\n"
        "                                           pe-table-philly -> phillyfuncsa\n"
        "                                           pe-blob-dss -> dssdemofuncsa\n"
        "                                           pe-queue-dss -> dssdemofuncsa\n"
        "                                           pe-table-dss -> dssdemofuncsa\n"
        "\n"
        "  snet-functions (10.0.1.0/24)            Private DNS Zones:\n"
        "  (philly-profiteering)                    privatelink.database.windows.net\n"
        "                                           privatelink.blob.core.windows.net\n"
        "                                           privatelink.queue.core.windows.net\n"
        "                                           privatelink.table.core.windows.net"
    )

    pdf.subsection_title("How it works")
    pdf.numbered_item(1, "Function App outbound traffic routes through snet-dss-functions (VNet integration + vnetRouteAllEnabled)")
    pdf.numbered_item(2, "DNS for philly-stats-sql-01.database.windows.net resolves via the private DNS zone to the private endpoint IP")
    pdf.numbered_item(3, "DNS for dssdemofuncsa.blob.core.windows.net (and queue/table) resolves via private DNS zones to private endpoint IPs")
    pdf.numbered_item(4, "Traffic flows entirely within the Azure backbone -- never touches the public internet")
    pdf.numbered_item(5, "Both databases on the server (dss-demo and PhillyStats) benefit from the same SQL private endpoint")
    pdf.numbered_item(6, "Both storage accounts (phillyfuncsa and dssdemofuncsa) have their own private endpoints on the same subnet")

    pdf.subsection_title("Implications")
    pdf.bullet("Azure Portal Query Editor does not work (requires public network access on SQL)")
    pdf.bullet("deploy-sql.js requires temporarily enabling public access on the SQL server")
    pdf.bullet("Function App deployments (func azure functionapp publish) work because Kudu runs within the Function App's VNet context, reaching storage via private endpoints")
    pdf.bullet("Any new app that needs SQL or storage access must be VNet-integrated or use a private endpoint")

    # ====================================================================
    # AGENT ARCHITECTURE PATHS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Agent Architecture Paths")

    pdf.body_text(
        "Not all agents reach the data the same way. There are two distinct paths through "
        "the stack, and understanding which agents use which path is critical for the demo narrative."
    )

    # Agent table -- wide, use 7pt
    agent_headers = ["Agent", "UC", "Data Path", "LLM Orchestration", "Our Code", "Model"]
    agent_widths = [34, 10, 40, 32, 27, 27]
    agent_rows = [
        ["Custom Web SPA", "UC1", "MCP -> APIM -> Func -> SQL", "MCP Server /chat", "Full stack (TS)", "GPT-4.1"],
        ["CS MCP (GCC)", "1, 2", "MCP -> APIM -> Func -> SQL", "Copilot Studio", "Zero", "GPT-4o"],
        ["CS MCP (Com)", "1, 2", "MCP -> APIM -> Func -> SQL", "Copilot Studio", "Zero", "GPT-4.1"],
        ["M365 Copilot", "UC2", "MCP -> APIM -> Func -> SQL", "M365 Copilot", "Zero (3 JSON)", "Platform"],
        ["CS SP/PDF (GCC)", "1, 2", "SharePoint doc library", "CS built-in RAG", "Zero", "GPT-4o"],
        ["CS SP/PDF (Com)", "1, 2", "SharePoint doc library", "CS built-in RAG", "Zero", "GPT-4.1"],
        ["Foundry Agent", "UC2", "MCP -> APIM -> Func -> SQL", "AI Agent Service", "Minimal", "GPT-4.1"],
        ["Investigative", "UC2", "Direct APIM -> Func -> SQL", "OpenAI SDK (TS)", "Full", "GPT-4.1"],
        ["Triage Agent", "UC2", "Direct APIM -> Func -> SQL", "Semantic Kernel", "Full", "GPT-4.1"],
    ]
    pdf.styled_table(agent_headers, agent_rows, agent_widths, font_size=7, row_height=6)

    # Path 1
    pdf.ln(4)
    pdf.subsection_title("Path 1: Via MCP Server /mcp (tool discovery)")

    pdf.body_text(
        "The MCP server Container App exposes tools via /mcp (JSON-RPC 2.0). Multiple "
        "clients auto-discover and call these tools -- each brings its own LLM orchestration:"
    )

    pdf.code_block(
        "Copilot Studio ----> /mcp --\\\n"
        "M365 Copilot ------> /mcp ---+---> Container App (MCP Server)\n"
        "Foundry Agent -----> /mcp --/        ---> APIM ---> Functions ---> SQL"
    )

    # Path 2
    pdf.subsection_title("Path 2: Via MCP Server /chat (full orchestration)")

    pdf.body_text(
        "The Web SPA uses /chat, where the MCP server runs the full agentic loop "
        "(chat completions + tool calling + Azure OpenAI):"
    )

    pdf.code_block(
        "Web SPA -----------> /chat ---> Container App (MCP Server)\n"
        "                                  ---> APIM ---> Functions ---> SQL\n"
        "                                  |\n"
        "                                  +--> Azure OpenAI"
    )

    # Path 3
    pdf.subsection_title("Path 3: Direct APIM (custom agentic loops)")

    pdf.body_text(
        "These agents bypass the MCP server entirely. Our code runs the agentic loop "
        "and calls APIM endpoints directly:"
    )

    pdf.code_block(
        "Investigative Agent (TypeScript, OpenAI SDK) ---\\\n"
        "                                                +----> APIM ----> Functions ----> SQL\n"
        "Triage Agent (C#, Semantic Kernel) -------------/"
    )

    # Why This Matters
    pdf.subsection_title("Why This Matters for the Demo")

    pdf.body_text(
        "The MCP server is a \"build once, serve many\" investment -- one Container App "
        "serves Copilot Studio, M365 Copilot, Foundry Agent, and the Web SPA. The spectrum "
        "of \"our code\" ranges from zero (M365 Copilot: 3 JSON manifests) to full "
        "(Investigative Agent: we write the entire agentic loop). This is the build vs buy "
        "trade-off in action:"
    )

    pdf.bullet("M365 Copilot (3 manifests), Copilot Studio (low-code config) -- auto-discover MCP tools, platform runs the loop",
               bold_lead="Zero code:")
    pdf.bullet("Foundry Agent -- create agent + point at /mcp, Agent Service runs the loop",
               bold_lead="Minimal code:")
    pdf.bullet("Investigative Agent (TypeScript), Triage Agent (C#) -- we run the loop, call APIM direct, control everything",
               bold_lead="Full code:")

    pdf.ln(2)
    pdf.body_text(
        "UC2 COM MCP originally tested with GPT-5 Auto (Copilot Studio Commercial default). "
        "Retested with GPT-4.1: identical 10/10."
    )

    pdf.callout_box(
        "Key Demo Talking Point",
        "All agents hit the same APIM gateway and the same data -- the only difference "
        "is who does the LLM orchestration and which model reasons over the results.",
        height=24
    )

    # ====================================================================
    # SHAREPOINT COMPARISON LAYER
    # ====================================================================
    pdf.add_page()
    pdf.section_title("SharePoint Comparison Layer")

    pdf.body_text(
        "In addition to the MCP-backed agent, the demo includes unstructured legal documents "
        "in sharepoint-docs/ for creating a second Copilot Studio agent grounded in SharePoint. "
        "This enables a side-by-side comparison:"
    )

    pdf.code_block(
        "Copilot Studio Agent (MCP)              Copilot Studio Agent (SharePoint)\n"
        "Queries structured SQL via              Searches uploaded documents via\n"
        "MCP tools -- precise, complete          semantic search -- approximate\n"
        "  |                                       |\n"
        "  v                                       v\n"
        "Container App -> APIM ->                SharePoint Document Library\n"
        "Functions -> Azure SQL                  11 Markdown files (Cases 1-2)\n"
        "50 cases, fully structured              Same facts, narrative prose"
    )

    # Use Case 1 SharePoint Docs
    pdf.subsection_title("Use Case 1: SharePoint Documents (11 files)")

    pdf.body_text(
        "Case 2024-DR-42-0892 (CPS): DSS Investigation Report, Medical Records, Sheriff "
        "Report #24-06-4418, Court Orders and Filings (3 orders), Home Study Report, GAL Report"
    )

    pdf.body_text(
        "Case 2024-DR-15-0341 (TPR): DSS Investigation Report, Substance Abuse Evaluation, "
        "Court Orders and Filings (6 orders), TPR Petition and Affidavit, GAL Reports "
        "(initial + updated)"
    )

    pdf.body_text(
        "All documents use page markers matching the page_reference values in the SQL seed "
        "data. Key statements are embedded verbatim in narrative prose. Some information is "
        "intentionally spread across multiple documents to test cross-document synthesis."
    )

    # Use Case 2 SharePoint Docs
    pdf.subsection_title("Use Case 2: Philly Investigation Documents (5 files + comparison prompts)")

    pdf.body_text(
        "A second set of documents covering the Philly Poverty Profiteering use case. These "
        "are written as investigator reports from the \"Office of Property & Code Enforcement "
        "Analytics\" and contain the same data available via the Philly MCP server's 34M-row "
        "SQL database. Documents are authored to look like the source from which structured "
        "data was extracted (not the reverse)."
    )

    pdf.body_text(
        "GEENA LLC / 4763 Griscom Street (3 files):",
        bold_lead=""
    )
    pdf.bullet("Entity_Investigation_Report.pdf -- GEENA LLC portfolio overview: 194 properties, 178 vacant (91.8%), $8.6M assessed value, acquisition patterns, 1,411 violations, related entities")
    pdf.bullet("Property_Enforcement_File_4763_Griscom.pdf -- 64 violations, 45 failed (70.3%), assessment decline $56,900->$24,800, city demolition June 2019")
    pdf.bullet("Transfer_Chain_Analysis_4763_Griscom.pdf -- 6-owner chain (1999-2019), two sheriff sales, $146K purchase at 275% of fair market value, 26-day flip")

    pdf.body_text(
        "2400 Bryn Mawr Avenue (2 files):",
        bold_lead=""
    )
    pdf.bullet("Property_Case_File_2400_Bryn_Mawr.pdf -- 4,141 sq ft stone colonial, quality grade B, condition 7 (poor), 34 violations, assessment decline $357,100->$265,600")
    pdf.bullet("Ownership_Financial_History_2400_Bryn_Mawr.pdf -- Anderson family 14+ year ownership, WaMu/IndyMac/Financial Freedom collapse, reverse mortgage foreclosure, GEENA LLC acquisition at 36.2% below FMV")

    pdf.body_text(
        "Comparison Prompts:",
        bold_lead=""
    )
    pdf.bullet("Philly_Comparison_Prompts.pdf -- 10 test prompts with ground truth, expected winners, and design rationale")

    # Source info
    pdf.subsection_title("Source File Locations")
    pdf.body_text(
        "Source markdown files are in sharepoint-docs/Philly-GEENA-LLC/, "
        "sharepoint-docs/Philly-2400-Bryn-Mawr/, and sharepoint-docs/. PDFs generated "
        "via scripts/convert-philly-docs.py using fpdf2."
    )

    # ====================================================================
    # WEB FRONT END
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Web Front End")

    pdf.body_text(
        "The Static Web App features a modern government-application design:"
    )

    pdf.bullet("Gold \"FOR OFFICIAL USE ONLY -- SC DSS INTERNAL SYSTEM\" bar",
               bold_lead="Classification banner:")
    pdf.bullet("Scales of justice icon, \"Legal Case Intelligence\" title, Office of General Counsel subtitle, PRODUCTION badge, user email display",
               bold_lead="Header:")
    pdf.bullet("Welcome hero with branding, icon-labeled prompt chips, animated message bubbles, tool badges, AI disclaimer footer",
               bold_lead="Agent Chat:")
    pdf.bullet("Searchable case table with status badges, detail views with stat cards",
               bold_lead="Case Browser:")
    pdf.bullet("Dark navy with DSS branding and \"Internal Use Only\" notice",
               bold_lead="Footer:")

    # ====================================================================
    # DATA PROVENANCE
    # ====================================================================
    pdf.section_title("Data Provenance")

    pdf.body_text(
        "All data in this system is synthetic. No real PII or case data was ever loaded "
        "into Azure SQL or committed to the repository."
    )

    # Source Material
    pdf.subsection_title("Source Material")
    pdf.body_text(
        "DSS Office of Legal Services provided reference materials in January-February 2026:"
    )
    pdf.numbered_item(1,
        "6 legal pleading templates from an active case -- complaint for ex parte removal, "
        "summons/notice documents, permanency planning orders (reunification and TPR paths), "
        "TPR summons/complaint, and order of dismissal. These are heavily templated documents "
        "with [CHOOSE ONE] placeholders and boilerplate statutory language. They established "
        "the case lifecycle structure (complaint -> removal -> permanency planning -> TPR -> "
        "dismissal)."
    )
    pdf.numbered_item(2,
        "Attorney feedback from two DSS attorneys who tested an early Copilot prototype. "
        "One provided screenshots; the other provided a detailed example prompt requesting: "
        "(1) timeline of pertinent facts with citations, (2) chart of discrepancies between "
        "parents' accounts, (3) statements by each parent to case managers/law enforcement. "
        "The feedback noted the AI output \"was not as detailed as I imagined\" and had some "
        "incorrect timeline items -- this set the accuracy bar for the demo."
    )

    # What Was Synthesized
    pdf.subsection_title("What Was Synthesized")
    synth_headers = ["Real Data Element", "Synthetic Replacement"]
    synth_widths = [85, 85]
    synth_rows = [
        ["Real case numbers", "2024-DR-42-0892"],
        ["Real defendant names", "Webb / Holloway (Case 1), Price (Case 2)"],
        ["Child names", "Synthetic children"],
        ["Attorney / caseworker names", "Synthetic names"],
        ["Specific dates and facts", "Invented timeline events, statements, discrepancies"],
        ["Thompson/Legette case details", "Not used -- only the prompt structure was adopted"],
    ]
    pdf.styled_table(synth_headers, synth_rows, synth_widths, font_size=8)

    # What Was Kept
    pdf.ln(3)
    pdf.subsection_title("What Was Kept (public, non-PII)")
    pdf.bullet("General case type structure (CPS, TPR, etc.)")
    pdf.bullet("Court procedural flow (hearings, orders, filings)")
    pdf.bullet("Statutory references (public law)")

    # The Money Prompt
    pdf.subsection_title("The \"Money Prompt\"")
    pdf.body_text(
        "The attorney's 4-part prompt structure became the primary demo prompt:"
    )
    pdf.numbered_item(1, "Timeline of pertinent facts with source citations")
    pdf.numbered_item(2, "Chart of discrepancies between parents' accounts")
    pdf.numbered_item(3, "Statements by Parent A to case managers/law enforcement")
    pdf.numbered_item(4, "Statements by Parent B to case managers/law enforcement")
    pdf.ln(1)
    pdf.body_text(
        "This directly shaped the 5 MCP tools (list_cases, get_case_summary, get_timeline, "
        "get_statements_by_person, get_discrepancies) and the SQL schema design."
    )

    # Source Document Sanitization
    pdf.subsection_title("Source Document Sanitization")
    pdf.body_text(
        "The original Word documents contained real case data. These were sanitized using "
        "scripts/sanitize-docs.py, which replaced all real names, case numbers, dates, and "
        "addresses with synthetic equivalents. The mapping is stored locally only (not in the "
        "committed version of the script). Sanitization verified: zero real names remain in "
        "any document."
    )

    # Source Document Handling
    pdf.subsection_title("Source Document Handling")
    pdf.bullet("Sanitized Word documents (.docx) are stored in docs/ but excluded from git via .gitignore")
    pdf.bullet("The .msg email file still contains real names and screenshots -- kept locally only, excluded from git")
    pdf.bullet("scripts/sanitize-docs.py can be re-run if documents are re-obtained from DSS")
    pdf.bullet("No real PII was ever loaded into Azure SQL -- only synthetic data from seed.sql / seed-expanded.sql")
    pdf.bullet("The sharepoint-docs/ folder contains entirely synthetic documents written from scratch")

    # ====================================================================
    # WARM-UP FEATURE
    # ====================================================================
    pdf.section_title("Warm-Up Feature")

    pdf.body_text(
        "The web UI includes a \"Warm Up\" button in the header that primes the entire "
        "cold-start chain before a demo. It runs two sequential requests:"
    )

    pdf.numbered_item(1, "GET /healthz -- Wakes the Container App (which may be scaled to zero)")
    pdf.numbered_item(2, "POST /chat -- Sends a lightweight chat request that traverses the full pipeline: Container App -> APIM -> Functions -> Azure SQL (warms DB connection pool) -> Azure OpenAI (loads model context)")

    pdf.ln(2)
    pdf.body_text(
        "The UI shows a three-stage progress popup (Container App, Database Connection, "
        "AI Model) with spinners, checkmarks, and per-stage timing. Auto-closes after "
        "4 seconds on success."
    )

    # ====================================================================
    # DESIGN DECISIONS
    # ====================================================================
    pdf.add_page()
    pdf.section_title("Design Decisions")

    pdf.bullet("The Case Browser panel uses JS-embedded data matching seed-expanded.sql (50 cases). This eliminates an API dependency for the read-only browser view and ensures the demo works even if the backend is slow to start.",
               bold_lead="Embedded case data in SWA:")
    pdf.bullet("database/generate-seed.js produces 50 cases with seeded PRNG (seed=42) for reproducibility. Keeps 2 hand-crafted demo cases and generates 48 with randomized SC counties, circuits, case types, names, and dates.",
               bold_lead="Procedural seed generation:")
    pdf.bullet("The /mcp endpoint is unauthenticated for the POC. Production would require API key or OAuth. Noted in code comments.",
               bold_lead="Unauthenticated MCP endpoint:")
    pdf.bullet("Reuses the existing APIM to avoid additional cost and provisioning time. Isolated via separate product and API.",
               bold_lead="Same APIM instance:")
    pdf.bullet("Using a CDN-hosted markdown renderer for the chat panel to keep the SWA simple (no build step).",
               bold_lead="marked.js CDN:")
    pdf.bullet("Switched from Standard to Free tier for built-in AAD login support without custom provider config.",
               bold_lead="Free tier SWA:")
    pdf.bullet("Azure policy prevents shared key access on storage accounts; using system-assigned identity with RBAC roles instead of connection strings.",
               bold_lead="Identity-based Function App storage:")
    pdf.bullet("Storage account dssdemofuncsa has public network access disabled. Private endpoints for blob, queue, and table services on snet-private-endpoints ensure the Function App (and Kudu deployments) can access storage entirely over the VNet. This eliminates the need to toggle public access for deployments.",
               bold_lead="Private endpoints for Function App storage:")
    pdf.bullet("Created snet-dss-functions (10.0.3.0/24) since existing snet-functions was delegated to Container App environments.",
               bold_lead="Dedicated VNet subnet:")

    # ====================================================================
    # DEPLOYED RESOURCE URLS
    # ====================================================================
    pdf.section_title("Deployed Resource URLs")

    url_headers = ["Resource", "URL"]
    url_widths = [40, 130]
    url_rows = [
        ["Web App (SWA)", "https://happy-wave-016cd330f.1.azurestaticapps.net"],
        ["MCP Endpoint", "https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/mcp"],
        ["Chat Endpoint", "https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/chat"],
        ["Health Check", "https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/healthz"],
        ["APIM Gateway", "https://philly-profiteering-apim.azure-api.net/dss/cases"],
        ["Functions", "https://dss-demo-func.azurewebsites.net/api/cases"],
    ]
    pdf.styled_table(url_headers, url_rows, url_widths, font_size=7, row_height=6)

    # ====================================================================
    # OUTPUT
    # ====================================================================
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "pdf")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "architecture.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    build_pdf()
