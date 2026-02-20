# FAQs

Clarification questions and answers from development sessions.

## General

**Q: Is this real case data?**
A: No. All names, dates, case numbers, and details are entirely fictional and synthetic. No real DSS case data is used.

**Q: Is this a production system?**
A: No. This is a sales demo / proof of concept. It demonstrates the value of structured data for AI agents. Production deployment would require additional security, compliance, and scale considerations.

## Architecture

**Q: Why not call the Azure Functions directly from the Container App?**
A: APIM sits between them to: (1) provide a consistent API surface, (2) handle function key injection via policy, (3) enable rate limiting / monitoring, and (4) match the pattern established in the philly-profiteering project.

**Q: Why is the /mcp endpoint unauthenticated?**
A: For POC simplicity — same approach used in the philly-profiteering demo. The data is read-only and synthetic. Production would require API key or OAuth. This is noted in the code.

**Q: Why embedded data in the Case Browser instead of API calls?**
A: The Case Browser is a read-only view for the demo audience. Embedding the data eliminates a runtime dependency and ensures the browser panel loads instantly even if the backend is cold-starting.

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
A: Yes. All key statements are embedded verbatim, page references match the `page_reference` values in the seed data, dates and names are consistent, and the same facts appear in both sources. Some information is intentionally spread across multiple documents to test cross-document synthesis.

**Q: Where are the comparison prompts?**
A: `sharepoint-docs/Demo_Comparison_Prompts.md` has 19 prompts across 6 categories, each with expected MCP vs. SharePoint responses and a "why MCP wins" explanation.

## Web UI

**Q: What does the web app look like?**
A: A modern government internal application with a gold classification banner ("FOR OFFICIAL USE ONLY"), navy header with scales of justice branding, Office of General Counsel subtitle, Agent Chat with welcome hero and icon-labeled prompt chips, Case Browser with styled tables, and a dark footer. Designed to look like a production internal tool, not a demo prototype.

---

*This file is updated when clarification questions arise during development sessions.*
