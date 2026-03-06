# Demo Notes — Data Design Decision

## "How did the data get from documents into the database?"

### The Short Answer

The data was never extracted from documents. It went the other direction: structured SQL data was designed first, then realistic legal documents were written from that data to populate SharePoint.

### The Design

1. **Structured data came first.** The SQL schema (`cases`, `people`, `timeline_events`, `statements`, `discrepancies`) was designed as the source of truth. Cases 1-2 were hand-crafted with rich detail; Cases 3-50 were procedurally generated for volume.

2. **SharePoint documents were written from the structured data.** The 11 files in `sharepoint-docs/` are realistic legal documents (investigation reports, medical records, sheriff reports, court orders, GAL reports) that embed the same facts into narrative prose. They deliberately:
   - Scatter facts across multiple documents (e.g., the same injury appears in medical records, the sheriff report, and the court filing)
   - Use the same `page_reference` values that appear in the SQL data
   - Embed verbatim quotes from the `statements` table into narrative paragraphs

3. **Two agents query the same facts through different lenses.** MCP agent hits structured SQL; SharePoint agent searches unstructured documents. Same ground truth, different retrieval methods.

### How to Frame It for the Audience

**"This is what digitization looks like."**

> "In the real world, DSS already has this information — it's in Word documents, PDFs, case files scattered across SharePoint. What we did is model that same information as structured data: timelines, statements, people, discrepancies. Think of it as the difference between a filing cabinet and a database. The MCP agent queries the database; the SharePoint agent searches the filing cabinet. Same facts, dramatically different precision."

You do not need to explain which came first. The audience cares about the outcome: structured data enables precise queries, cross-referencing, and aggregation that document search cannot match.

### Key Demo Sections (from Demo_Comparison_Prompts.md)

| Section | What It Proves | Best "Wow" Prompt |
|---|---|---|
| 1. Factual Retrieval | MCP returns complete, ordered data | "Complete timeline for case 2024-DR-42-0892" |
| 2. Cross-Referencing | MCP compares statements side by side | "What did Marcus Webb tell medical staff vs. law enforcement?" |
| 3. Discrepancies | MCP surfaces all contradictions | "Key discrepancies between Webb's and Holloway's accounts" |
| 4. Filtering | SQL WHERE clauses vs. semantic search | "Show me only the medical events in the Webb case" |
| 5. Multi-Case Queries | Scalability — 50 cases, imagine 5,000 | "How many active cases does DSS currently have?" |
| 6. Precision Stress Tests | Page numbers, session counts, time gaps | "What page of the medical records contains Dr. Chowdhury's assessment?" |

### Recommended Flow

1. Start with Section 1 to establish that MCP returns complete, structured data
2. Move to Section 3 for the "wow" moment on discrepancy detection
3. Use Section 5 for the scalability argument
4. Close with Section 6 to drive home precision (page numbers, session counts)

### The Punchline

> "Would you rather have your attorneys search through PDFs, or query a database that already has the answers organized?"

## 5 Discrepancy Questions to Ask the Agent

These questions are grounded in the actual seed data and SharePoint documents. Questions 1 and 5 expose cross-document conflicts that the SharePoint agent is likely to mishandle, while the MCP agent returns one consistent answer.

### Question 1: "What time was Jaylen Webb brought to the emergency room, and who was the admitting nurse?"

**What it exposes:** A cross-document conflict in the SharePoint docs.

- Medical Records say arrival at **03:15 AM**, nurse **Rebecca Torres**
- Sheriff Report says arrival at **approximately 0047 hours** (12:47 AM), nurse **Charge Nurse Patricia Daniels**

**MCP agent:** Returns one consistent answer from structured data.
**SharePoint agent:** May surface both conflicting versions — or pick one without flagging the contradiction.

### Question 2: "What did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement?"

**What it exposes:** A subtle two-hour discrepancy between statements.

- Nursing notes (Medical Records p. 8): Marcus told hospital staff he put Jaylen to bed "**around ten**"
- Sheriff Report (p. 3): Marcus told Lt. Odom he put the child to bed at approximately **8:00 PM**

**MCP agent:** Pulls both statements side-by-side from the `statements` table filtered by `made_to`.
**SharePoint agent:** Has to find these in two different documents and may not catch the discrepancy.

### Question 3: "Crystal Price told the court she was 'clean now' at the November 2023 hearing. What do the drug test results show?"

**What it exposes:** A direct contradiction between Crystal's testimony and lab results.

- Crystal's statement to court (Nov 14, 2023): "I am clean now"
- Drug screen results: Two positive fentanyl screens on **October 8** and **October 22** — just three weeks earlier
- Also: Missed screens on December 5, January 15, and March 3

**MCP agent:** Returns the contradiction with dates and sources from the `discrepancies` table.
**SharePoint agent:** Has to cross-reference the court transcript with the DSS investigation report — drug test dates are in one document, Crystal's statement is in another.

### Question 4: "Crystal Price said she couldn't comply with the treatment plan because she lacked transportation. What support did DSS actually provide?"

**What it exposes:** Crystal's stated barrier is contradicted by DSS records.

- Crystal claims: Lack of transportation and support
- DSS records show: Monthly bus passes issued, three housing referrals provided, IOP transportation assistance **offered and declined by Crystal**

**MCP agent:** Has this as a structured discrepancy record with both sides and the contradicting evidence.
**SharePoint agent:** Would need to connect Crystal's court statement (in Court Orders) with DSS case management notes (in Investigation Report, p. 7) — the detail about declining transportation is easy to miss in prose.

### Question 5: "Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey?"

**What it exposes:** A direct factual conflict between two documents about the same hospital visit.

- Sheriff Report (p. 2): "Radiology report indicated **no fractures detected** on skeletal survey"
- Medical Records (pp. 3-4): Bilateral long bone fractures with extensive radiological findings — transverse femur fracture (3-5 days old) and spiral humerus fracture (24-48 hours old)

**MCP agent:** Returns the medical findings from structured data — fractures confirmed.
**SharePoint agent:** Might surface the Sheriff Report's incorrect statement, the Medical Records' correct findings, or both. This is exactly the kind of inconsistency attorneys need to catch.

### Recommended Order for Demo

1. Start with **Question 3** (Crystal's sobriety) — easy to understand, clear contradiction
2. Follow with **Question 4** (transportation excuse) — builds the pattern of Crystal's credibility issues
3. Ask **Question 2** (Marcus bedtime discrepancy) — shifts to the Webb case, shows subtle cross-referencing
4. Ask **Question 5** (fractures in skeletal survey) — the cross-document bombshell
5. Close with **Question 1** (ER arrival time and nurse) — reinforces that document-based search can't be trusted for precise facts

---

### What NOT to Say

- Do not bash SharePoint. The message is "different tools for different jobs."
- SharePoint is great for unstructured narratives, policy documents, and memos.
- When case data is structured, MCP gives precision that document search cannot match.
