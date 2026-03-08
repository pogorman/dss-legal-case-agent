# FAQs

Clarification questions and answers from development sessions.

## General

**Q: Is this real case data?**
A: No. All names, dates, case numbers, and details are entirely fictional and synthetic. No real DSS case data is used.

**Q: Is this a production system?**
A: No. This is a sales demo / proof of concept. It demonstrates the value of structured data for AI agents. Production deployment would require additional security, compliance, and scale considerations.

**Q: Where did the case data come from? Is any of it real?**
A: SC DSS OGC provided real legal pleading templates and attorney feedback as reference material. These were used to understand the case lifecycle structure (complaint → removal → permanency planning → TPR → dismissal) and the attorneys' desired prompt patterns. All PII (names, case numbers, dates, specific facts) was replaced with entirely synthetic data. No real case data was ever loaded into Azure SQL or committed to the repository. Source documents are kept locally but excluded from git. See `docs/architecture.md` → "Data Provenance" for full details.

## Architecture

**Q: Why not call the Azure Functions directly from the Container App?**
A: APIM sits between them to: (1) provide a consistent API surface, (2) handle function key injection via policy, (3) enable rate limiting / monitoring, and (4) match the pattern established in the philly-profiteering project.

**Q: Why is the /mcp endpoint unauthenticated?**
A: For POC simplicity — same approach used in the philly-profiteering demo. The data is read-only and synthetic. Production would require API key or OAuth. This is noted in the code.

**Q: Why embedded data in the Case Browser instead of API calls?**
A: The Case Browser is a read-only view for the demo audience. Embedding the data eliminates a runtime dependency and ensures the browser panel loads instantly even if the backend is cold-starting.

**Q: Why can't I use the Azure Portal Query Editor?**
A: Public network access is disabled on the SQL server (`philly-stats-sql-01`). The Portal Query Editor requires public access. Use Azure Data Studio from a VNet-connected machine, or temporarily enable public access to run ad-hoc queries. See the User Guide "Database Access" section for details.

**Q: Why is public network access disabled on the SQL server?**
A: Security best practice. All application traffic flows through a private endpoint (`pe-sql-philly`) on the VNet. The Function App reaches SQL via VNet integration → private endpoint → private DNS resolution. No SQL traffic goes over the public internet.

**Q: Will disabling public access break anything?**
A: No — all runtime application traffic (Function App → SQL, Function App → Storage) uses private endpoints. The only things that require public access are the Portal Query Editor and running `deploy-sql.js` from a local machine. For those, temporarily enable public access on the SQL server and disable it when done. Storage never needs public access — deployments go through Kudu, which runs in the Function App's VNet context.

**Q: Why does the Function App storage account have private endpoints?**
A: The storage account `dssdemofuncsa` has `publicNetworkAccess: Disabled` (enforced by Azure policy). Without private endpoints, the Function App runtime can't read its deployment package and Kudu can't write new deployments — resulting in 503 errors. The private endpoints (`pe-blob-dss`, `pe-queue-dss`, `pe-table-dss`) on `snet-private-endpoints` let both the Function App and Kudu reach storage over the VNet. This is a permanent fix — no need to toggle public access for deployments.

**Q: Why did the Function App suddenly start returning 503?**
A: Flex Consumption Function Apps store their deployment package in a blob on the storage account. If the storage account's public access is disabled and there are no private endpoints, the Function App can't read the package and returns 503 even though Azure reports it as "Running". Adding private endpoints for blob, queue, and table services resolved this permanently.

## Demo

**Q: What's the "money prompt" for the demo?**
A: See the User Guide. It's a 4-part legal analysis request matching what a DSS attorney actually tested. The agent should call all four relevant tools and return structured, citable results.

**Q: How does this prove the MCP approach is better than SharePoint?**
A: Two key proof points: (1) **Completeness** — every statement, timeline event, and discrepancy is returned because the data is structured, not extracted from PDFs. (2) **Consistency** — running the same prompt twice returns identical results because the agent queries SQL, not chunks from a document index.

## SharePoint Comparison

**Q: What are the SharePoint documents?**
A: 11 realistic legal documents (Markdown format) in `sharepoint-docs/` for Cases 1 and 2. They contain the same facts as the SQL database but written as narrative prose — DSS investigation reports, medical records, sheriff reports, court orders, home study reports, GAL reports, substance abuse evaluations, and a TPR petition with affidavit.

**Q: Why Markdown instead of PDF/Word?**
A: Markdown is easy to create, version-control, and upload. Copilot Studio indexes Markdown from SharePoint the same way it indexes PDFs or Word docs. For the demo, the format doesn't matter — the comparison is about structured (SQL) vs. unstructured (documents) retrieval.

**Q: Do the documents match the SQL data exactly?**
A: Mostly yes — key statements are embedded verbatim and page references match the seed data. However, the SharePoint documents contain deliberate cross-document inconsistencies (e.g., the Sheriff Report lists different ER arrival times, nurse names, and fracture findings than the Medical Records). These inconsistencies are realistic — in real cases, different agencies often record conflicting details. They also strengthen the demo by showing that document search can surface contradictory information without flagging it, while the MCP agent returns one authoritative answer from structured data.

**Q: How did the data get from Word documents into the SQL database?**
A: It didn't — the data flow went the other direction. The SQL schema and seed data were designed first as the structured source of truth. The SharePoint documents were then written from that data as realistic narrative prose. This mirrors what "digitization" looks like: taking information that exists in unstructured documents and modeling it as structured, queryable data.

**Q: Where are the comparison prompts?**
A: `sharepoint-docs/Demo_Comparison_Prompts.md` has 19 prompts across 6 categories, each with expected MCP vs. SharePoint responses and a "why MCP wins" explanation.

## Web UI

**Q: What does the web app look like?**
A: A full internal government portal with: gold classification banner ("FOR OFFICIAL USE ONLY"), navy header with scales of justice branding, global navigation with dropdown menus (Legal Resources, Forms & Templates, Training & CLE), left sidebar with quick links/alerts/deadlines/circuit contacts, Case Browser as the main content area, and a multi-column dark footer. The AI Case Agent is a floating chat widget in the bottom-right corner, accessible via a FAB button with open/close animation and a "New Chat" reset button. Designed to look like a production internal tool, not a demo prototype.

## Branding

**Q: Why was South Carolina branding removed?**
A: The site was genericized to "Department of Social Services" / "Office of Legal Services" so the demo is reusable for any state DSS audience. County names, sidebar links (SC Code of Laws, SCCIS, etc.), footer address, and legal citations were all replaced with generic equivalents. The underlying data and demo flow are unchanged.

## Warm-Up

**Q: How does the warm-up button work?**
A: Clicking "Warm Up" in the header fires two real requests behind the scenes: (1) a GET to `/healthz` which wakes the Container App from cold start, then (2) a POST to `/chat` with a lightweight prompt that traverses the full pipeline — Container App, APIM, Functions, SQL, and OpenAI. A popup shows three stages (Container App, Database Connection, AI Model) with spinners, checkmarks, and per-stage timing. It auto-closes after 4 seconds.

**Q: When should I use the warm-up button?**
A: Before every demo, ideally 30-60 seconds before the audience arrives. If the Container App has been idle, cold start can take 10-20 seconds. Warming up ensures the first real query in front of the audience responds quickly.

**Q: Does the warm-up button send real data?**
A: Yes — it sends a real (minimal) chat request so the entire chain is primed, including the SQL connection pool and OpenAI model context. The warm-up prompt is lightweight and the response is discarded.

## Data Improvements

**Q: How were data gaps identified?**
A: After 110 test runs across 11 agent configurations and 10 prompts, specific failures were traced to missing data or tool limitations. Each proposed fix was validated against the source PDF documents — no data was fabricated. Details in `docs/improvements/improvements-round-1.md`.

**Q: What was added in Improvements Round 1?**
A: Five changes: (1) `made_to` filter on the statements tool (fixes P8 failures), (2) skeletal survey findings + discrepancy in SQL (fixes P4), (3) 9:30 PM thump as standalone timeline event (fixes P10), (4) individual drug test events as discrete timeline rows (fixes P3), (5) nurses added to people table (fixes P1). Total: 11 new SQL rows + 1 tool/function change.

**Q: How does data get from PDFs into the database?**
A: See `docs/improvements/document-to-database-mapping.md` for a detailed walkthrough. In production, tools like Azure Document Intelligence or Power Automate AI Builder extract entities from PDFs. The mapping guide shows the exact PDF text and the SQL row it produces for each table.

**Q: Why weren't these data points in the original load?**
A: The original data load focused on the attorney's 4-part prompt pattern (timeline, discrepancies, statements by each parent). Details like individual drug test dates, skeletal survey findings, and nursing staff were in the source documents but weren't prioritized for extraction. This is a realistic scenario — initial data modeling always misses details that surface during testing.

## PII and Data Provenance

**Q: Are there any real names in the codebase?**
A: No. All real names from the original case were scrubbed in Session 15. The sanitize script (`scripts/sanitize-docs.py`) no longer contains the real→synthetic mapping — it must be populated from a local-only reference file before running. The architecture doc describes the mapping generically without revealing real names.

**Q: Are real names in the git history?**
A: Yes — commits prior to the scrub still contain the mapping table. The repo is private. A full purge would require BFG Repo Cleaner or `git filter-branch` with a force push.

## Executive Summary PDF

**Q: Why is the PDF called "Copilot Studio Evaluation" and not "AI Agent Evaluation"?**
A: The evaluation is specifically testing Copilot Studio agent configurations — MCP-backed, SharePoint-backed, and knowledge-base-backed. The PDF is framed as a Copilot Studio evaluation across multiple government use cases, not a generic AI comparison.

**Q: What are the two use cases in the PDF?**
A: Use Case 1 is Legal Case Analysis (DSS Office of Legal Services, 50 synthetic cases, 11 agents, 10 prompts — complete). Use Case 2 is Investigative Analytics (Philly Poverty Profiteering, 34M rows of public records, same agent configurations — testing planned).

**Q: Why one PDF instead of separate reports per use case?**
A: A single authoritative document makes it easier to compare findings across use cases. As Use Case 2 results come in, they'll be added to the same PDF, strengthening (or challenging) Use Case 1's conclusions.

**Q: Why does the PDF say "Uploaded PDF" instead of "Knowledge Base PDF"?**
A: "Knowledge base" is a technical term. "Uploaded files" is plain English that any executive understands. The PDF avoids all abbreviations (no MCP, GCC, SP, KB, Com, Pa, ER, DB, DOCX) for C-suite readability.

## Use Case 2: Philly Poverty Profiteering

**Q: What is Use Case 2?**
A: An investigative analytics use case using real Philadelphia public records (34M rows across 11 tables). Five PDF investigation reports about GEENA LLC and two properties are compared against the Philly MCP server backed by live SQL data. Same agent comparison methodology as Use Case 1.

**Q: What documents are in the Philly corpus?**
A: Five investigator-style PDF reports: Entity Investigation Report (GEENA LLC portfolio), Property Enforcement File (4763 Griscom violations/demolition), Transfer Chain Analysis (4763 Griscom ownership history), Property Case File (2400 Bryn Mawr profile), and Ownership & Financial History (2400 Bryn Mawr mortgage crisis/foreclosure). Plus a comparison prompts document with 10 test prompts.

**Q: Is the Philly data real or synthetic?**
A: Unlike Use Case 1 (entirely synthetic), Use Case 2 uses real public data from the City of Philadelphia — property assessments, code violations, real estate transfers, demolition permits. Every number is verifiable against official city records.

**Q: How were the Philly documents created?**
A: The documents were written as investigator reports from the "Office of Property & Code Enforcement Analytics." They are authored to read as if the structured database was extracted FROM them (source-first framing), even though the data already existed in SQL. This mirrors a realistic digitization workflow.

**Q: Which prompts are impossible for document agents?**
A: Prompts 6 (top 5 private violators citywide) and 9 (zip code vacancy comparison) require aggregation across 584K properties. The documents only cover 2 properties and 1 entity, so document agents can only partially answer or must acknowledge the limitation.

**Q: How do I convert the markdown documents to PDF?**
A: Run `python scripts/convert-philly-docs.py`. This uses fpdf2 to parse markdown structure and render styled PDFs with navy headers, alternating-row tables, and professional footers. The script handles Unicode character replacement for Helvetica font compatibility.

## Use Case 2 Testing

**Q: Why are there different property counts for GEENA LLC across agents?**
A: The investigation report says 194 properties. The MCP database returns 631 rows (including duplicates from permits, violations, tax records, and related entities) or 330 distinct parcels (deduplicated by parcel number). The "correct" answer depends on how "ownership" is defined — OPA-registered ownership (194), distinct parcels in the entity network (330), or all property touchpoints (631). This is inherent ambiguity in real-world data, not an agent error.

**Q: Why did the GCC MCP agent fail on Prompt 1?**
A: The MCP tool returned all 631 property records as raw JSON, exceeding Copilot Studio's `OpenAIModelTokenLimit`. The data was retrieved successfully (visible in the tool activity log) but the model couldn't process it to generate a summary. This is a tool design issue — the MCP server should return pre-aggregated statistics for large result sets instead of raw rows.

**Q: Why is Use Case 2 scoring different from Use Case 1?**
A: Use Case 1 used synthetic data with known ground truth — every answer was designed by the team. Use Case 2 uses real public data where "correct" answers can be ambiguous (e.g., property counts depend on deduplication logic). Scoring shifted from "matched ground truth" to "gave a defensible, sourced answer with sound methodology."

**Q: What are the Investigative Agent, Foundry Agent, and Triage Agent?**
A: Pro-code agents from the Philly Profiteering web SPA (mcp-apim project). The Investigative Agent uses OpenAI's chat interface; the Foundry Agent uses Azure AI Foundry; the Triage Agent uses Semantic Kernel with a team-of-agents routing pattern (dispatches to OwnerAnalyst, ViolationAnalyst, AreaAnalyst sub-agents). All query the same MCP backend as the Copilot Studio agents. They're "sprinkles on top" — supplemental to the Copilot Studio comparison, Use Case 2 only.

**Q: Where are the Use Case 2 test response files?**
A: `docs/test-responses/use-case-2-poverty/`. Use Case 1 responses are in `docs/test-responses/use-case-1-dss-legal/`.

**Q: What was the biggest finding from Use Case 2 testing?**
A: Address resolution is broken. MCP agents can't reliably map a street address (e.g., "4763 Griscom Street") to the correct parcel number. Across prompts 2-8, agents produced 10+ different wrong parcel numbers for 2 addresses. The mapping is non-deterministic — the same agent gets different parcels for the same address across prompts. The Foundry Agent found 45 failed inspections in Prompt 2 (correct parcel) and 0 in Prompt 8 (wrong parcel), contradicting itself.

**Q: Why does GPT-4.1 outperform GPT-4o so dramatically for MCP agents but not document agents?**
A: MCP agents require multi-step reasoning: resolve an address, select the right tool, interpret results, and compose an answer. GPT-4.1's improved tool selection and reasoning produces 80% pass rates vs GPT-4o's 20%. Document agents just retrieve and summarize text from PDFs — a simpler task where both models achieve 80%. The model upgrade matters most when the task requires complex tool orchestration.

**Q: Why did the Triage Agent score 0/10?**
A: The Semantic Kernel team-of-agents pattern introduces hand-off failures that single-agent architectures avoid. Failures included: false negatives (ViolationAnalyst found 0 violations where 45 exist), answering the wrong prompt (responded to P6 when asked P7), refusing to filter (asked for clarification instead of excluding government entities), and infrastructure crashes (tool_call_id mismatch causing 500 errors). The routing layer adds complexity without improving answer quality.

**Q: How many agents were tested in Use Case 2?**
A: Seven: GCC MCP, COM MCP, GCC SP/PDF, COM SP/PDF (all Copilot Studio), plus Investigative Agent (OpenAI), Foundry Agent (AI Foundry), and Triage Agent (Semantic Kernel). 70 total responses scored across 10 prompts.

---

*This file is updated when clarification questions arise during development sessions.*
