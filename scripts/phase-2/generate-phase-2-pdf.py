"""
Generate Phase 2 documentation PDF.
Uses fpdf2 -- no external dependencies beyond what's already installed.

Usage: python scripts/phase-2/generate-phase-2-pdf.py
Output: docs/pdf/phase-2/phase-2-custom-connector.pdf
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
CODE_BG = (243, 244, 246)
CALLOUT_BG = (235, 245, 255)
CALLOUT_BORDER = (41, 98, 163)


class Phase2PDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT)
        self.cell(0, 6, sanitize_text("Phase 2 -- Custom Connector Setup"), align="L")
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
        self.cell(0, 4, sanitize_text("Phase 2 | March 2026"), align="C")

    # -- Helpers --------------------------------------------------------------
    def section_title(self, text):
        self.ln(4)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*NAVY)
        self.cell(0, 9, sanitize_text(text), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.l_margin + 55, self.get_y())
        self.set_line_width(0.2)
        self.ln(4)

    def subsection_title(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*ACCENT)
        self.cell(0, 7, sanitize_text(text), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, sanitize_text(text), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        indent = self.l_margin + 5
        self.set_x(indent)
        self.cell(4, 5.5, "-")
        old_lm = self.l_margin
        self.l_margin = indent + 4
        self.multi_cell(0, 5.5, sanitize_text(text), new_x="LMARGIN", new_y="NEXT")
        self.l_margin = old_lm
        self.ln(0.5)

    def bold_bullet(self, label, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        indent = self.l_margin + 5
        self.set_x(indent)
        self.cell(4, 5.5, "-")
        old_lm = self.l_margin
        self.l_margin = indent + 4
        self.multi_cell(0, 5.5, sanitize_text(f"**{label}:** {text}"),
                        markdown=True, new_x="LMARGIN", new_y="NEXT")
        self.l_margin = old_lm
        self.ln(0.5)

    def code_block(self, text):
        self.ln(1)
        self.set_fill_color(*CODE_BG)
        self.set_font("Courier", "", 8.5)
        self.set_text_color(*DARK)
        x = self.l_margin + 3
        w = self.w - self.l_margin - self.r_margin - 6
        h = self.multi_cell(w, 4.5, sanitize_text(text), dry_run=True, output="HEIGHT")
        self.set_x(x)
        self.rect(x - 2, self.get_y(), w + 4, h + 4, "F")
        self.set_x(x)
        self.ln(2)
        self.set_x(x)
        self.multi_cell(w, 4.5, sanitize_text(text), new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def callout_box(self, text):
        self.ln(2)
        x = self.l_margin
        w = self.w - self.l_margin - self.r_margin
        self.set_font("Helvetica", "", 10)
        h = self.multi_cell(w - 10, 5.5, sanitize_text(text), dry_run=True, output="HEIGHT")
        self.set_fill_color(*CALLOUT_BG)
        self.rect(x, self.get_y(), w, h + 8, "F")
        self.set_draw_color(*CALLOUT_BORDER)
        self.set_line_width(0.8)
        self.line(x, self.get_y(), x, self.get_y() + h + 8)
        self.set_line_width(0.2)
        self.set_text_color(*DARK)
        self.set_xy(x + 5, self.get_y() + 4)
        self.multi_cell(w - 10, 5.5, sanitize_text(text), new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def table_row(self, cells, widths, is_header=False, alt=False):
        if is_header:
            self.set_fill_color(*TABLE_HEADER_BG)
            self.set_text_color(*TABLE_HEADER_FG)
            self.set_font("Helvetica", "B", 9)
        else:
            bg = ROW_ALT if alt else ROW_WHT
            self.set_fill_color(*bg)
            self.set_text_color(*DARK)
            self.set_font("Helvetica", "", 9)
        row_h = 7
        x_start = self.l_margin
        for i, (cell_text, w) in enumerate(zip(cells, widths)):
            self.set_x(x_start + sum(widths[:i]))
            self.cell(w, row_h, sanitize_text(cell_text), fill=True)
        self.ln(row_h)


def build_pdf():
    pdf = Phase2PDF()
    pdf.set_margins(20, 20, 20)

    # -- Cover page ----------------------------------------------------------
    pdf.add_page()
    pdf.ln(55)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 14, "Phase 2", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 10, "Custom Connector Setup", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.8)
    cx = pdf.w / 2
    pdf.line(cx - 40, pdf.get_y(), cx + 40, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*MED)
    pdf.cell(0, 7, "Giving GCC Copilot Studio Agents Structured API Access",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Without MCP Infrastructure",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(25)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*LIGHT)
    pdf.cell(0, 6, "Office of Legal Services", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "March 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    # -- Section 1: Context --------------------------------------------------
    pdf.add_page()
    pdf.section_title("1. Context")

    pdf.body_text(
        "Phase 1 of the Agent Fidelity Spectrum project demonstrated that tool access "
        "(MCP) and model selection are the two primary drivers of response fidelity in "
        "Copilot Studio agents. MCP-backed agents scored 9-10/10 at investigative "
        "prompts where SharePoint-grounded agents scored 2-4/10."
    )

    pdf.body_text(
        "However, MCP requires Container Apps, custom TypeScript code, and APIM "
        "configuration. Many state government teams want the fidelity gains without "
        "the infrastructure investment. Phase 2 tests whether a Power Platform custom "
        "connector -- which requires zero code and deploys in minutes -- can deliver "
        "similar fidelity by giving Copilot Studio the same structured API access."
    )

    pdf.subsection_title("Phase 2 Hypothesis")
    pdf.callout_box(
        "GCC state government customers can improve Copilot Studio agent fidelity by "
        "adding structured API tools via custom connectors, without needing MCP "
        "infrastructure. A Swagger file and a single CLI command is all it takes."
    )

    pdf.subsection_title("Comparison Matrix")
    pdf.body_text("Phase 2 tests three rows against the same prompts and rubric:")

    widths = [25, 55, 50, 42]
    pdf.table_row(["Row", "Data Path", "Fidelity Driver", "Cost"], widths, is_header=True)
    pdf.table_row(["1 (P1)", "SP native grounding", "Document search", "Included"], widths, alt=False)
    pdf.table_row(["2 (P2a)", "Custom Connector -> APIM", "Structured API tools", "$0 incremental"], widths, alt=True)
    pdf.table_row(["3 (P2b)", "AI Search retrieval", "Semantic reranking", "$75/mo (Basic)"], widths, alt=False)
    pdf.ln(2)

    pdf.body_text(
        "Row 1 is the Phase 1 baseline. Row 2 is the primary Phase 2 deliverable. "
        "Row 3 (AI Search) is parked due to a cross-tenant blocker and may become Phase 2b."
    )

    # -- Section 2: Architecture ---------------------------------------------
    pdf.section_title("2. Architecture")

    pdf.body_text("The custom connector creates a new data path for Copilot Studio:")

    pdf.body_text(
        "Copilot Studio Agent -> Custom Connector -> APIM -> Azure Functions -> Azure SQL"
    )

    pdf.body_text(
        "This reuses the exact same APIM endpoints and Azure Functions that the "
        "Phase 1 MCP server calls. No new backend code was written. The only new "
        "artifact is a Swagger 2.0 specification file that describes the existing API "
        "in a format Power Platform can consume."
    )

    pdf.subsection_title("Key Design Decisions")
    pdf.bold_bullet("Same backend", "The connector calls the same 5 APIM operations the MCP server uses. Any fidelity difference is attributable to the orchestration layer, not the data")
    pdf.bold_bullet("API key auth", "APIM subscription key is injected via the Ocp-Apim-Subscription-Key header, matching the existing auth pattern")
    pdf.bold_bullet("GCC target", "Connector deployed to GCC Power Platform environment (og-ai), proving the pattern works in government cloud")
    pdf.bold_bullet("Zero code", "No Power Automate flows, no custom code -- just the Swagger spec and pac CLI")

    # -- Section 3: What We Built -------------------------------------------
    pdf.section_title("3. What We Built")

    pdf.subsection_title("Step 1: Export APIM Swagger Spec")
    pdf.body_text(
        "APIM already had a Swagger 2.0 definition for the DSS Case API. We exported "
        "it using the Azure CLI:"
    )
    pdf.code_block(
        "az apim api export \\\n"
        "  --resource-group rg-philly-profiteering \\\n"
        "  --service-name philly-profiteering-apim \\\n"
        "  --api-id dss-case-api \\\n"
        "  --export-format SwaggerUrl"
    )
    pdf.body_text(
        "The exported spec had the correct host, base path, and auth definitions, "
        "but was missing query parameters, response schemas, and operation descriptions."
    )

    pdf.subsection_title("Step 2: Enrich the Swagger Spec")
    pdf.body_text(
        "Copilot Studio uses the operation descriptions and parameter metadata to decide "
        "when and how to call each tool. A bare spec with no descriptions produces an agent "
        "that doesn't know what the tools do. We enriched the spec with:"
    )

    pdf.bullet("Detailed operation descriptions explaining what each endpoint returns and when to use it")
    pdf.bullet("Parameter descriptions with example values (e.g., 'The case identifier, e.g. 2024-DR-42-0892')")
    pdf.bullet("Missing query parameters: 'type' filter on GetTimeline, 'person' and 'made_to' filters on GetStatements")
    pdf.bullet("Full response schemas with all fields defined (CaseSummary, CaseDetail, Person, TimelineEvent, Statement, Discrepancy)")

    pdf.subsection_title("The 5 Operations")
    widths2 = [42, 52, 78]
    pdf.table_row(["Operation", "Route", "Description"], widths2, is_header=True)
    pdf.table_row(["ListCases", "GET /dss/cases", "All cases with metadata"], widths2, alt=False)
    pdf.table_row(["GetCaseSummary", "GET /dss/cases/{caseId}", "Case detail + people involved"], widths2, alt=True)
    pdf.table_row(["GetTimeline", "GET /dss/cases/{id}/timeline", "Chronological events, optional type filter"], widths2, alt=False)
    pdf.table_row(["GetStatements", "GET /dss/cases/{id}/statements", "Witness statements, person/made_to filter"], widths2, alt=True)
    pdf.table_row(["GetDiscrepancies", "GET /dss/cases/{id}/discrepancies", "Contradictions between accounts"], widths2, alt=False)
    pdf.ln(2)

    pdf.subsection_title("Step 3: Generate API Properties File")
    pdf.body_text(
        "Power Platform custom connectors require an API properties file alongside "
        "the Swagger spec. We generated the template using pac CLI:"
    )
    pdf.code_block("pac connector init --connection-template ApiKey")
    pdf.body_text(
        "Then customized it with the APIM-specific display name, description, "
        "and branding color."
    )

    pdf.subsection_title("Step 4: Deploy to GCC")
    pdf.body_text(
        "With the enriched Swagger spec and API properties file ready, deployment "
        "was a single command:"
    )
    pdf.code_block(
        "# Switch to GCC auth profile\n"
        "pac auth select --index 4\n\n"
        "# Create the connector\n"
        "pac connector create \\\n"
        "  --api-definition-file dss-case-api-swagger.json \\\n"
        "  --api-properties-file apiProperties.json \\\n"
        "  --environment https://og-ai.crm9.dynamics.com/"
    )
    pdf.body_text(
        "The connector was created in the GCC environment in under 30 seconds. "
        "Verification:"
    )
    pdf.code_block(
        "pac connector list\n"
        "# Output:\n"
        "# 540e456d-...  DSS Case API  CustomConnector"
    )

    pdf.subsection_title("Step 5: Wire to Copilot Studio")
    pdf.body_text(
        "In the Copilot Studio maker portal:"
    )
    pdf.bullet("Open (or create) the target agent")
    pdf.bullet("Navigate to Tools (formerly Actions)")
    pdf.bullet("Search connectors for 'DSS' -- all 5 operations appear as individual tools")
    pdf.bullet("Add all 5 tools to the agent")
    pdf.bullet("Create a connection using the APIM subscription key")
    pdf.bullet("Test with the same prompts used in Phase 1")

    # -- Section 4: File Inventory ------------------------------------------
    pdf.section_title("4. Artifacts")

    pdf.subsection_title("New Files (Phase 2)")
    pdf.bold_bullet("connectors/dss-case-api-swagger.json", "Enriched Swagger 2.0 spec with descriptions, query params, and response schemas")
    pdf.bold_bullet("connectors/apiProperties.json", "Power Platform connector properties (API key auth, branding)")
    pdf.bold_bullet("scripts/phase-2/generate-phase-2-pdf.py", "This document's generator")
    pdf.bold_bullet("docs/pdf/phase-2/phase-2-custom-connector.pdf", "This document")

    pdf.subsection_title("Unchanged from Phase 1")
    pdf.bullet("All 5 Azure Functions (functions/src/functions/*.ts)")
    pdf.bullet("APIM configuration and endpoints")
    pdf.bullet("Azure SQL schema and seed data")
    pdf.bullet("Phase 1 whitepaper, slide deck, and all Phase 1 PDFs")

    # -- Section 5: What's Different ----------------------------------------
    pdf.section_title("5. Custom Connector vs. MCP")

    pdf.body_text("Both paths hit the same backend. The differences are in the orchestration:")

    widths3 = [52, 60, 60]
    pdf.table_row(["Dimension", "MCP Server", "Custom Connector"], widths3, is_header=True)
    pdf.table_row(["Code required", "TypeScript MCP server", "None (Swagger file only)"], widths3, alt=False)
    pdf.table_row(["Infrastructure", "Container App + ACR", "None"], widths3, alt=True)
    pdf.table_row(["Deployment", "Docker build + deploy", "pac connector create"], widths3, alt=False)
    pdf.table_row(["Tool discovery", "MCP protocol", "Swagger operation IDs"], widths3, alt=True)
    pdf.table_row(["Orchestration", "Server-side (MCP loop)", "Copilot Studio (platform)"], widths3, alt=False)
    pdf.table_row(["Model control", "Choose any model", "Platform-assigned (GPT-4o in GCC)"], widths3, alt=True)
    pdf.table_row(["Auth", "APIM sub key (code)", "APIM sub key (connection)"], widths3, alt=False)
    pdf.table_row(["GCC available", "Yes (custom infra)", "Yes (native)"], widths3, alt=True)
    pdf.ln(2)

    pdf.callout_box(
        "The key question Phase 2 answers: Does Copilot Studio's built-in orchestration, "
        "combined with structured API tools, produce fidelity comparable to a custom MCP "
        "orchestration loop? If yes, many government teams can skip the MCP infrastructure "
        "entirely."
    )

    # -- Section 6: Test Results ---------------------------------------------
    pdf.section_title("6. Test Results")

    pdf.body_text(
        "We ran all 19 Phase 1 evaluation prompts against the Custom Connector agent "
        "via Direct Line API on March 12, 2026. The agent was published in GCC Copilot "
        "Studio with no authentication, shared connection (agent author authenticates), "
        "and all 5 connector tools enabled."
    )

    pdf.subsection_title("Scoring Method")
    pdf.body_text(
        "Each prompt is scored 0-10 against the expected MCP agent response defined in "
        "Phase 1. Section averages are the arithmetic mean of the prompt scores in that "
        "section (e.g., 3 prompts scoring 10, 10, 0 = 20/3 = 6.7). The overall average "
        "is the arithmetic mean of all 19 individual prompt scores, not a mean of section "
        "averages. This produces decimal values like 9.3 or 6.7 when section sizes don't "
        "divide evenly."
    )
    pdf.bullet("10/10: All expected details present and accurate, with source citations")
    pdf.bullet("7-9/10: Most details correct, minor omissions (missing cross-references, no editorial analysis)")
    pdf.bullet("4-6/10: Partially correct, missing notable details or has inaccuracies")
    pdf.bullet("1-3/10: Responded but with wrong data or wrong case")
    pdf.bullet("0/10: No usable response (agent refused, asked for input, or returned error)")

    pdf.subsection_title("Results by Section")

    widths4 = [55, 25, 92]
    pdf.table_row(["Section", "Average", "Notes"], widths4, is_header=True)
    pdf.table_row(["1. Factual Retrieval (4)", "10.0/10",
                    "All 4 prompts perfect. 14 timeline events, all 8 people, all 3 hearings."], widths4, alt=False)
    pdf.table_row(["2. Cross-Referencing (3)", "9.3/10",
                    "Exact quotes, side-by-side comparisons. Minor: didn't highlight key analytical shift in 2.1."], widths4, alt=True)
    pdf.table_row(["3. Discrepancies (3)", "6.7/10",
                    "Two perfect (7 discrepancies found, 4 contradictions). One failure: couldn't resolve implicit case reference."], widths4, alt=False)
    pdf.table_row(["4. Filtering (3)", "7.0/10",
                    "Two perfect. One failure: resolved 'Webb case' to wrong Webb case (2 Webb cases in DB)."], widths4, alt=True)
    pdf.table_row(["5. Aggregate (4)", "9.3/10",
                    "Counted 25 active cases, listed all TPR cases (9), all Seventh Circuit cases (5). Minor: imprecise language on 5.4."], widths4, alt=False)
    pdf.table_row(["6. Stress Tests (2)", "7.5/10",
                    "Correct page ref and IOP counts, but missed cross-references and net calculations."], widths4, alt=True)
    pdf.ln(2)

    pdf.subsection_title("Individual Scores")

    widths5 = [15, 60, 15, 82]
    pdf.table_row(["#", "Prompt (abbreviated)", "Score", "Key Observation"], widths5, is_header=True)
    pdf.table_row(["1.1", "Complete timeline for 2024-DR-42-0892", "10", "14 events, all dates/times/sources"], widths5, alt=False)
    pdf.table_row(["1.2", "Jaylen Webb hospital admission", "10", "3:15 AM, both fractures, different healing stages"], widths5, alt=True)
    pdf.table_row(["1.3", "People in Price TPR case", "10", "All 8 people with roles"], widths5, alt=False)
    pdf.table_row(["1.4", "Court hearings in Webb case", "10", "3 hearings with outcomes"], widths5, alt=True)
    pdf.table_row(["2.1", "Webb: medical staff vs law enforcement", "8", "Exact quotes but no analytical highlight"], widths5, alt=False)
    pdf.table_row(["2.2", "Holloway: hospital vs Lt. Odom", "10", "All 3 changes identified"], widths5, alt=True)
    pdf.table_row(["2.3", "Price: sobriety claims vs drug tests", "10", "Exceeded expectations, added compliance/housing"], widths5, alt=False)
    pdf.table_row(["3.1", "Webb/Holloway discrepancies", "10", "7 discrepancies (expected 6)"], widths5, alt=True)
    pdf.table_row(["3.2", "Price compliance contradictions", "10", "4 contradictions with sources"], widths5, alt=False)
    pdf.table_row(["3.3", "Evidence vs crib fall claim", "0", "Asked for case ID -- couldn't resolve"], widths5, alt=True)
    pdf.table_row(["4.1", "Medical events in Webb timeline", "1", "Wrong Webb case (Bryce, not Jaylen)"], widths5, alt=False)
    pdf.table_row(["4.2", "Statements to law enforcement", "10", "All 4 statements with page refs"], widths5, alt=True)
    pdf.table_row(["4.3", "Price court orders chronologically", "10", "5 events in correct order"], widths5, alt=False)
    pdf.table_row(["5.1", "Active case count", "9", "Said 25 (previous run said 24)"], widths5, alt=True)
    pdf.table_row(["5.2", "Seventh Judicial Circuit cases", "10", "5 cases, all Spartanburg"], widths5, alt=False)
    pdf.table_row(["5.3", "TPR cases", "10", "9 cases listed"], widths5, alt=True)
    pdf.table_row(["5.4", "Richland County besides Price", "8", "Correct but used 'for example' language"], widths5, alt=False)
    pdf.table_row(["6.1", "Dr. Chowdhury page reference", "7", "Page 5 correct, missing quote/cross-ref"], widths5, alt=True)
    pdf.table_row(["6.2", "IOP sessions Nov vs Apr", "8", "3/12 and 5/12 correct, no net calc"], widths5, alt=False)
    pdf.ln(2)

    pdf.callout_box(
        "Overall: 161/190 = 8.5/10. A zero-code custom connector delivers 85% of MCP "
        "fidelity using the same data, same endpoints, and the same 19 evaluation prompts."
    )

    pdf.subsection_title("Failure Analysis")
    pdf.body_text(
        "The 2 hard failures (3.3 and 4.1) are both orchestration issues, not data "
        "access issues. The connector delivered the data correctly in every other prompt. "
        "The failures occurred when GPT-4o could not resolve an ambiguous case reference:"
    )
    pdf.bold_bullet("Prompt 3.3 (0/10)", "Says 'Jaylen' and 'the parents' with no case ID or last names. GPT-4o did not attempt a ListCases lookup to resolve the implicit reference. The MCP agent handles this because its orchestration loop is more sophisticated.")
    pdf.bold_bullet("Prompt 4.1 (1/10)", "Says 'the Webb case' but there are two Webb cases in the database (2024-DR-42-0892 and 2024-DR-10-0261). GPT-4o resolved to the wrong one. When the prompt includes an explicit case ID, the connector agent performs at MCP-level fidelity.")

    pdf.body_text(
        "Pattern: When prompts include explicit identifiers (case ID, full names), "
        "the custom connector agent scores 10/10 consistently. The gap appears only "
        "when the agent must reason about which case the user means."
    )

    # -- Section 7: What's Next ---------------------------------------------
    pdf.section_title("7. What's Next")

    pdf.bold_bullet("Prompt engineering", "Add system instructions to the Copilot Studio agent telling it to always resolve case IDs via ListCases before calling other tools. May close the orchestration gap.")
    pdf.bold_bullet("Model variation", "If GCC adds GPT-4.1 or GPT-5, retest to isolate model vs. tool effects on the 2 failed prompts")
    pdf.bold_bullet("AI Search (Phase 2b)", "Resolve cross-tenant blocker for SharePoint indexer, or pivot to Power Automate sync. Test BM25 (Free) and semantic ranking (Basic) as retrieval layers")
    pdf.bold_bullet("Score comparison", "Add Custom Connector scores to the fidelity spectrum alongside SP-grounded and MCP agents in the Phase 1 whitepaper (after peer review concludes)")

    # -- Output --------------------------------------------------------------
    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "pdf", "phase-2")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "phase-2-custom-connector.pdf")
    pdf.output(out_path)
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    build_pdf()
