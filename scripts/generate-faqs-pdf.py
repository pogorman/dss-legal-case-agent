"""
Generate a FAQs PDF using the same pattern as the executive summary.
Uses fpdf2 -- no external dependencies beyond what's already installed.

Usage: python scripts/generate-faqs-pdf.py
Output: docs/pdf/faqs.pdf
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


class FaqsPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT)
        self.cell(0, 6, sanitize_text("Agent Accuracy Spectrum for Copilot Studio  |  FAQs"), align="L")
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

    def qa_pair(self, question, answer):
        """Render a Q&A pair with bold Q: and A: leads."""
        self.body_text(question, bold_lead="Q:")
        self.body_text(answer, bold_lead="A:")
        self.ln(1)


def build_pdf():
    pdf = FaqsPDF()
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
    pdf.cell(0, 10, "Frequently Asked Questions", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(65)
    pdf.set_draw_color(80, 140, 200)
    pdf.set_line_width(0.4)
    pdf.line(pdf.w * 0.3, pdf.get_y(), pdf.w * 0.7, pdf.get_y())
    pdf.set_line_width(0.2)

    pdf.set_y(75)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 185, 210)
    pdf.cell(0, 7, "March 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(130)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MED)
    pdf.multi_cell(0, 6.5, sanitize_text(
        "Clarification questions and answers from development sessions covering "
        "data provenance, architecture, demo setup, testing methodology, and "
        "improvement rounds."
    ), align="C")

    # ====================================================================
    # GENERAL
    # ====================================================================
    pdf.add_page()
    pdf.section_title("General")

    pdf.qa_pair(
        "Is this real case data?",
        "No. All names, dates, case numbers, and details are entirely fictional "
        "and synthetic. No real DSS case data is used."
    )

    pdf.qa_pair(
        "Is this a production system?",
        "No. This is a sales demo / proof of concept. It demonstrates the value "
        "of structured data for AI agents. Production deployment would require "
        "additional security, compliance, and scale considerations."
    )

    pdf.qa_pair(
        "Where did the case data come from? Is any of it real?",
        "SC DSS OGC provided real legal pleading templates and attorney feedback "
        "as reference material. These were used to understand the case lifecycle "
        "structure (complaint to removal to permanency planning to TPR to dismissal) "
        "and the attorneys' desired prompt patterns. All PII (names, case numbers, "
        "dates, specific facts) was replaced with entirely synthetic data. No real "
        "case data was ever loaded into Azure SQL or committed to the repository. "
        "Source documents are kept locally but excluded from git."
    )

    # ====================================================================
    # ARCHITECTURE
    # ====================================================================
    pdf.section_title("Architecture")

    pdf.qa_pair(
        "Why not call the Azure Functions directly from the Container App?",
        "APIM sits between them to: (1) provide a consistent API surface, "
        "(2) handle function key injection via policy, (3) enable rate limiting / "
        "monitoring, and (4) match the pattern established in the philly-profiteering project."
    )

    pdf.qa_pair(
        "Why is the /mcp endpoint unauthenticated?",
        "For POC simplicity -- same approach used in the philly-profiteering demo. "
        "The data is read-only and synthetic. Production would require API key or OAuth. "
        "This is noted in the code."
    )

    pdf.qa_pair(
        "Why embedded data in the Case Browser instead of API calls?",
        "The Case Browser is a read-only view for the demo audience. Embedding the "
        "data eliminates a runtime dependency and ensures the browser panel loads "
        "instantly even if the backend is cold-starting."
    )

    pdf.qa_pair(
        "Why can't I use the Azure Portal Query Editor?",
        "Public network access is disabled on the SQL server (philly-stats-sql-01). "
        "The Portal Query Editor requires public access. Use Azure Data Studio from "
        "a VNet-connected machine, or temporarily enable public access to run ad-hoc queries."
    )

    pdf.qa_pair(
        "Why is public network access disabled on the SQL server?",
        "Security best practice. All application traffic flows through a private "
        "endpoint (pe-sql-philly) on the VNet. The Function App reaches SQL via VNet "
        "integration to private endpoint to private DNS resolution. No SQL traffic "
        "goes over the public internet."
    )

    pdf.qa_pair(
        "Will disabling public access break anything?",
        "No -- all runtime application traffic (Function App to SQL, Function App to "
        "Storage) uses private endpoints. The only things that require public access "
        "are the Portal Query Editor and running deploy-sql.js from a local machine. "
        "For those, temporarily enable public access on the SQL server and disable it "
        "when done. Storage never needs public access -- deployments go through Kudu, "
        "which runs in the Function App's VNet context."
    )

    pdf.qa_pair(
        "Why does the Function App storage account have private endpoints?",
        "The storage account dssdemofuncsa has publicNetworkAccess: Disabled (enforced "
        "by Azure policy). Without private endpoints, the Function App runtime can't "
        "read its deployment package and Kudu can't write new deployments -- resulting "
        "in 503 errors. The private endpoints (pe-blob-dss, pe-queue-dss, pe-table-dss) "
        "on snet-private-endpoints let both the Function App and Kudu reach storage "
        "over the VNet."
    )

    pdf.qa_pair(
        "Why did the Function App suddenly start returning 503?",
        "Flex Consumption Function Apps store their deployment package in a blob on "
        "the storage account. If the storage account's public access is disabled and "
        "there are no private endpoints, the Function App can't read the package and "
        "returns 503 even though Azure reports it as \"Running\". Adding private endpoints "
        "for blob, queue, and table services resolved this permanently."
    )

    # ====================================================================
    # DEMO
    # ====================================================================
    pdf.section_title("Demo")

    pdf.qa_pair(
        "What's the \"money prompt\" for the demo?",
        "See the User Guide. It's a 4-part legal analysis request matching what a "
        "DSS attorney actually tested. The agent should call all four relevant tools "
        "and return structured, citable results."
    )

    pdf.qa_pair(
        "How does this prove the MCP approach is better than SharePoint?",
        "Two key proof points: (1) Completeness -- every statement, timeline event, "
        "and discrepancy is returned because the data is structured, not extracted "
        "from PDFs. (2) Consistency -- running the same prompt twice returns identical "
        "results because the agent queries SQL, not chunks from a document index."
    )

    # ====================================================================
    # SHAREPOINT COMPARISON
    # ====================================================================
    pdf.section_title("SharePoint Comparison")

    pdf.qa_pair(
        "What are the SharePoint documents?",
        "11 realistic legal documents (Markdown format) in sharepoint-docs/ for Cases "
        "1 and 2. They contain the same facts as the SQL database but written as "
        "narrative prose -- DSS investigation reports, medical records, sheriff reports, "
        "court orders, home study reports, GAL reports, substance abuse evaluations, "
        "and a TPR petition with affidavit."
    )

    pdf.qa_pair(
        "Why Markdown instead of PDF/Word?",
        "Markdown is easy to create, version-control, and upload. Copilot Studio "
        "indexes Markdown from SharePoint the same way it indexes PDFs or Word docs. "
        "For the demo, the format doesn't matter -- the comparison is about structured "
        "(SQL) vs. unstructured (documents) retrieval."
    )

    pdf.qa_pair(
        "Do the documents match the SQL data exactly?",
        "Mostly yes -- key statements are embedded verbatim and page references match "
        "the seed data. However, the SharePoint documents contain deliberate "
        "cross-document inconsistencies (e.g., the Sheriff Report lists different ER "
        "arrival times, nurse names, and fracture findings than the Medical Records). "
        "These inconsistencies are realistic -- in real cases, different agencies often "
        "record conflicting details."
    )

    pdf.qa_pair(
        "How did the data get from Word documents into the SQL database?",
        "It didn't -- the data flow went the other direction. The SQL schema and seed "
        "data were designed first as the structured source of truth. The SharePoint "
        "documents were then written from that data as realistic narrative prose. This "
        "mirrors what \"digitization\" looks like."
    )

    pdf.qa_pair(
        "Where are the comparison prompts?",
        "sharepoint-docs/Demo_Comparison_Prompts.md has 19 prompts across 6 categories, "
        "each with expected MCP vs. SharePoint responses."
    )

    # ====================================================================
    # WEB UI
    # ====================================================================
    pdf.section_title("Web UI")

    pdf.qa_pair(
        "What does the web app look like?",
        "A full internal government portal with: gold classification banner (\"FOR "
        "OFFICIAL USE ONLY\"), navy header with scales of justice branding, global "
        "navigation with dropdown menus (Legal Resources, Forms and Templates, Training "
        "and CLE), left sidebar with quick links/alerts/deadlines/circuit contacts, "
        "Case Browser as the main content area, and a multi-column dark footer. The AI "
        "Case Agent is a floating chat widget in the bottom-right corner."
    )

    # ====================================================================
    # BRANDING
    # ====================================================================
    pdf.section_title("Branding")

    pdf.qa_pair(
        "Why was South Carolina branding removed?",
        "The site was genericized to \"Department of Social Services\" / \"Office of Legal "
        "Services\" so the demo is reusable for any state DSS audience. County names, "
        "sidebar links, footer address, and legal citations were all replaced with "
        "generic equivalents."
    )

    # ====================================================================
    # WARM-UP
    # ====================================================================
    pdf.section_title("Warm-Up")

    pdf.qa_pair(
        "How does the warm-up button work?",
        "Clicking \"Warm Up\" in the header fires two real requests behind the scenes: "
        "(1) a GET to /healthz which wakes the Container App from cold start, then "
        "(2) a POST to /chat with a lightweight prompt that traverses the full pipeline "
        "-- Container App, APIM, Functions, SQL, and OpenAI. A popup shows three stages "
        "with spinners, checkmarks, and per-stage timing. It auto-closes after 4 seconds."
    )

    pdf.qa_pair(
        "When should I use the warm-up button?",
        "Before every demo, ideally 30-60 seconds before the audience arrives. If the "
        "Container App has been idle, cold start can take 10-20 seconds. Warming up "
        "ensures the first real query responds quickly."
    )

    pdf.qa_pair(
        "Does the warm-up button send real data?",
        "Yes -- it sends a real (minimal) chat request so the entire chain is primed, "
        "including the SQL connection pool and OpenAI model context. The warm-up prompt "
        "is lightweight and the response is discarded."
    )

    # ====================================================================
    # DATA IMPROVEMENTS
    # ====================================================================
    pdf.section_title("Data Improvements")

    pdf.qa_pair(
        "How were data gaps identified?",
        "After 190 baseline test runs across 19 agent configurations and 10 prompts each, specific "
        "failures were traced to missing data or tool limitations. Each proposed fix "
        "was validated against the source PDF documents -- no data was fabricated."
    )

    pdf.qa_pair(
        "What was added in Improvements Round 1?",
        "Five changes: (1) made_to filter on the statements tool (fixes P8 failures), "
        "(2) skeletal survey findings + discrepancy in SQL (fixes P4), (3) 9:30 PM "
        "thump as standalone timeline event (fixes P10), (4) individual drug test events "
        "as discrete timeline rows (fixes P3), (5) nurses added to people table (fixes P1). "
        "Total: 11 new SQL rows + 1 tool/function change."
    )

    pdf.qa_pair(
        "What was changed in Improvements Round 2?",
        "Four changes, zero data modifications: (1) new search_properties fuzzy address "
        "lookup tool (fixes 87% address resolution failure rate), (2) entity network "
        "summary mode with ?summary=true (fixes GCC token overflow), (3) improved tool "
        "descriptions emphasizing people roster and address workflow, (4) system prompt "
        "additions with explicit tool selection guidance."
    )

    pdf.qa_pair(
        "Why did the Triage Agent barely improve (0/10 to 1/10) in Round 2 when other "
        "agents jumped dramatically?",
        "The Triage Agent's team-of-agents architecture (triage router to specialized "
        "sub-agents) initially prevented it from using the new search_properties tool. "
        "The sub-agents had their own system prompts that didn't include the address "
        "resolution workflow. However, after five iterative rounds of prompt and routing "
        "fixes, the Triage Agent ultimately reached a perfect 10 out of 10 -- the most "
        "rounds of any agent, but proof that architectural complexity can be overcome "
        "with persistent iteration."
    )

    pdf.qa_pair(
        "How does data get from PDFs into the database?",
        "In production, tools like Azure Document Intelligence or Power Automate AI "
        "Builder extract entities from PDFs."
    )

    pdf.qa_pair(
        "Why weren't these data points in the original load?",
        "The original data load focused on the attorney's 4-part prompt pattern. "
        "Details like individual drug test dates, skeletal survey findings, and nursing "
        "staff were in the source documents but weren't prioritized for extraction. "
        "This is a realistic scenario -- initial data modeling always misses details "
        "that surface during testing."
    )

    # ====================================================================
    # PII AND DATA PROVENANCE
    # ====================================================================
    pdf.section_title("PII and Data Provenance")

    pdf.qa_pair(
        "Are there any real names in the codebase?",
        "No. All real names from the original case were scrubbed. The sanitize script "
        "no longer contains the real-to-synthetic mapping."
    )

    pdf.qa_pair(
        "Are real names in the git history?",
        "Yes -- commits prior to the scrub still contain the mapping table. The repo "
        "is private. A full purge would require BFG Repo Cleaner or git filter-branch "
        "with a force push."
    )

    # ====================================================================
    # WHITEPAPER
    # ====================================================================
    pdf.section_title("Whitepaper")

    pdf.qa_pair(
        "Why is the whitepaper called \"Improving Copilot Studio Agents\" and not \"AI Agent Evaluation\"?",
        "The evaluation is specifically testing Copilot Studio agent configurations. "
        "The whitepaper is framed as a practical guide for improving Copilot Studio agents "
        "across multiple government use cases."
    )

    pdf.qa_pair(
        "What are the two use cases in the PDF?",
        "Use Case 1 is Legal Case Analysis (DSS, 50 synthetic cases, 11 agents, "
        "10 prompts). Use Case 2 is Investigative Analytics (Philly, 34M rows, same "
        "agent configs)."
    )

    pdf.qa_pair(
        "Why one PDF instead of separate reports per use case?",
        "A single authoritative document makes it easier to compare findings across "
        "use cases."
    )

    pdf.qa_pair(
        "Why does the PDF say \"Uploaded PDF\" instead of \"Knowledge Base PDF\"?",
        "\"Knowledge base\" is a technical term. \"Uploaded files\" is plain English. "
        "The PDF avoids all abbreviations for C-suite readability."
    )

    # ====================================================================
    # USE CASE 2: PHILLY POVERTY PROFITEERING
    # ====================================================================
    pdf.section_title("Use Case 2: Philly Poverty Profiteering")

    pdf.qa_pair(
        "What is Use Case 2?",
        "An investigative analytics use case using real Philadelphia public records "
        "(34M rows across 11 tables). Five PDF investigation reports about GEENA LLC "
        "and two properties are compared against the Philly MCP server backed by live "
        "SQL data."
    )

    pdf.qa_pair(
        "What documents are in the Philly corpus?",
        "Five investigator-style PDF reports: Entity Investigation Report (GEENA LLC "
        "portfolio), Property Enforcement File (4763 Griscom violations/demolition), "
        "Transfer Chain Analysis (4763 Griscom ownership history), Property Case File "
        "(2400 Bryn Mawr profile), and Ownership and Financial History (2400 Bryn Mawr "
        "mortgage crisis/foreclosure). Plus a comparison prompts document."
    )

    pdf.qa_pair(
        "Is the Philly data real or synthetic?",
        "Real public data from the City of Philadelphia -- property assessments, code "
        "violations, real estate transfers, demolition permits. Every number is "
        "verifiable against official city records."
    )

    pdf.qa_pair(
        "How were the Philly documents created?",
        "Written as investigator reports from the \"Office of Property and Code "
        "Enforcement Analytics.\" They are authored to read as if the structured "
        "database was extracted FROM them (source-first framing), even though the data "
        "already existed in SQL."
    )

    pdf.qa_pair(
        "Which prompts are impossible for document agents?",
        "Prompts 6 (top 5 private violators citywide) and 9 (zip code vacancy "
        "comparison) require aggregation across 584K properties. The documents only "
        "cover 2 properties and 1 entity."
    )

    pdf.qa_pair(
        "How do I convert the markdown documents to PDF?",
        "Run python scripts/convert-philly-docs.py. Uses fpdf2 to parse markdown and "
        "render styled PDFs."
    )

    # ====================================================================
    # USE CASE 2 TESTING
    # ====================================================================
    pdf.section_title("Use Case 2 Testing")

    pdf.qa_pair(
        "Why are there different property counts for GEENA LLC across agents?",
        "The investigation report says 194 properties. The MCP database returns 631 "
        "rows (including duplicates) or 330 distinct parcels. The \"correct\" answer "
        "depends on how \"ownership\" is defined. This is inherent ambiguity in "
        "real-world data."
    )

    pdf.qa_pair(
        "Why did the GCC MCP agent fail on Prompt 1?",
        "The MCP tool returned all 631 property records as raw JSON, exceeding the "
        "token limit. The data was retrieved but the model couldn't process it. This "
        "is a tool design issue -- return pre-aggregated statistics for large result sets."
    )

    pdf.qa_pair(
        "Why is Use Case 2 scoring different from Use Case 1?",
        "Use Case 1 used synthetic data with known ground truth. Use Case 2 uses real "
        "public data where \"correct\" answers can be ambiguous. Scoring shifted from "
        "\"matched ground truth\" to \"gave a defensible, sourced answer.\""
    )

    pdf.qa_pair(
        "What are the Investigative Agent, Foundry Agent, and Triage Agent?",
        "Pro-code agents from the Philly Profiteering web SPA. The Investigative Agent "
        "uses OpenAI's chat interface; the Foundry Agent uses Azure AI Foundry Agent Service; the "
        "Triage Agent uses Semantic Kernel with a team-of-agents routing pattern. All "
        "query the same MCP backend. They're supplemental to the Copilot Studio comparison."
    )

    pdf.qa_pair(
        "Where are the Use Case 2 test response files?",
        "docs/test-responses/use-case-2-poverty/. Use Case 1 responses are in "
        "docs/test-responses/use-case-1-dss-legal/."
    )

    pdf.qa_pair(
        "What was the biggest finding from Use Case 2 testing?",
        "Address resolution is broken. MCP agents can't reliably map a street address "
        "to the correct parcel number. The mapping is non-deterministic -- the same "
        "agent gets different parcels for the same address across prompts."
    )

    pdf.qa_pair(
        "Why does GPT-4.1 outperform GPT-4o so dramatically for MCP agents but not "
        "document agents?",
        "MCP agents require multi-step reasoning. GPT-4.1's improved tool selection "
        "produces 80% pass rates vs GPT-4o's 20%. Document agents just retrieve and "
        "summarize text -- a simpler task where both models achieve 80%."
    )

    pdf.qa_pair(
        "Why did the Triage Agent start at 0/10?",
        "The team-of-agents pattern introduces hand-off failures. Initial failures "
        "included false negatives, answering the wrong prompt, refusing to filter, and "
        "infrastructure crashes. After five rounds of iterative improvement (the most "
        "of any agent), the Triage Agent reached a perfect 10 out of 10. The lesson: "
        "complexity is not disqualifying, but it demands more testing investment."
    )

    pdf.qa_pair(
        "How many agents were tested in Use Case 2?",
        "Eight agents total (seven in the initial round, M365 Copilot added in a later "
        "round). 80+ total responses scored across 10 prompts."
    )

    # ====================================================================
    # M365 COPILOT
    # ====================================================================
    pdf.section_title("M365 Copilot (Commercial)")

    pdf.qa_pair(
        "How did M365 Copilot Commercial perform?",
        "2 Pass, 3 Partial, 5 Fail (20% pass rate) on Use Case 2. It scored worst "
        "among all MCP-connected agents. Prompts 4 (ownership chain) and 6 (top 5 "
        "violators) produced excellent answers -- among the best in the entire evaluation. "
        "But tool reliability was inconsistent: the same parcel that worked for Prompt 4 "
        "returned no data for Prompt 5."
    )

    pdf.qa_pair(
        "Why does M365 Copilot Commercial perform worse than Copilot Studio?",
        "Three factors: (1) the platform-assigned model cannot be changed by the user, "
        "(2) tool execution is non-deterministic -- tools return no data with correct "
        "parcel IDs, (3) the model makes incorrect assumptions about data availability "
        "(e.g., claiming mortgage data is in the system when it is not). Copilot Studio "
        "gives you model choice and more predictable tool execution."
    )

    pdf.qa_pair(
        "Is M365 Copilot useful for anything?",
        "Yes -- it is excellent for Levels 1-2 (discovery and summarization) where you "
        "point it at SharePoint documents. The confirmation UX (showing each tool call "
        "for user approval) is also a strong demo asset for enterprise security. It "
        "struggles at Level 4+ where multi-step tool orchestration is required."
    )

    # ====================================================================
    # ITERATIVE IMPROVEMENT
    # ====================================================================
    pdf.section_title("Iterative Improvement")

    pdf.qa_pair(
        "How many rounds of testing and improvement were there?",
        "Seven testing rounds and four improvement rounds. Round 0 was the baseline. "
        "Round 1 added missing data (11 SQL rows, 1 tool filter). Round 2 added new "
        "tools (search_properties, summary mode) and improved prompts. Round 3 validated "
        "across models (GPT-4.1 vs GPT-5 Auto). Subsequent rounds focused on specific "
        "agents (Triage took 5 rounds alone). Total: 313 test runs across 19 agent "
        "configurations."
    )

    pdf.qa_pair(
        "What is the pattern organizations should follow?",
        "Start with ground truth (what the correct answers are). Test against it. Fix "
        "data gaps first, then tool gaps, then validate across models. Budget 3+ rounds "
        "for Level 4 use cases. The investment is real but the improvement arc is "
        "dramatic -- agents went from 0-1 out of 10 to perfect scores."
    )

    # ====================================================================
    # OUTPUT
    # ====================================================================
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "pdf")
    out_path = os.path.join(out_dir, "faqs.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    build_pdf()
