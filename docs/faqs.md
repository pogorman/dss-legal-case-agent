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
A: See the User Guide. It's a 4-part legal analysis request matching what a DSS attorney (Laurel) actually tested. The agent should call all four relevant tools and return structured, citable results.

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

---

*This file is updated when clarification questions arise during development sessions.*
