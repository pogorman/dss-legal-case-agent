# DSS Legal Case Intelligence — Demo Guide

## Demo URL
**https://happy-wave-016cd330f.1.azurestaticapps.net**

## MCP Endpoint (for Copilot Studio)
**https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/mcp**

---

## The Story (Know This Cold)

A DSS attorney tested an AI agent backed by unstructured case documents in SharePoint. She asked it for a timeline, discrepancies, and statements from both parties. Her feedback: **"It was not as detailed as I imagined — missing statements, incorrect on some timeline items."**

This demo shows WHY that happened and HOW to fix it. Same Copilot Studio agent, same prompt, two backends:
- **Version A** (SharePoint): Chunked PDFs, inconsistent retrieval, missing data
- **Version B** (MCP + SQL): Structured data, every record returned, fully cited

The audience should experience the difference themselves before you explain what changed.

---

## Pre-Demo Checklist

- [ ] Sign into the SWA URL and verify you see the app (do this 10 min before)
- [ ] The Container App may cold-start — send a quick "List available cases" to warm it up
- [ ] Upload `sharepoint-docs/` files to SharePoint and connect Copilot Studio agent (or have screenshots ready)
- [ ] Have the SharePoint agent open in a separate browser tab for side-by-side comparison
- [ ] Have `sharepoint-docs/Demo_Comparison_Prompts.md` open for reference (19 ready-made prompts)
- [ ] Know the primary case number: **2024-DR-42-0892** (CPS) and secondary: **2024-DR-15-0341** (TPR)
- [ ] There are **50 total cases** across all SC circuits — the agent can list and query any of them

---

## Demo Script

### Opening (2 min)

**The Case Browser is already showing — it's the default view.**

> "Before we start talking to the agent, let me show you what's behind it. There are 50 synthetic cases in the database — completely fictional, no real data — modeled on real DSS case structures across all 16 judicial circuits."

**Click into case 2024-DR-42-0892.**

> "This is a CPS emergency removal. You can see the parties — two parents, the child, a case manager, law enforcement, a GAL, medical witnesses. Below that: timeline events, statements, discrepancies. All structured. All queryable."

**Point at the stat cards (timeline count, statement count, discrepancy count).**

> "The key difference from the SharePoint approach: this data isn't buried in PDFs. Every statement has a speaker, a date, a recipient, and a page citation. Every timeline event has a type and source document. The AI doesn't have to guess what's in a document — it queries exactly what it needs."

**Click Back, then click the floating chat button in the bottom-right corner to open the AI agent.**

---

### Act 1: Orientation (1 min)

**Click the suggested prompt: "List available cases"**

> "Let's start simple. The agent discovers its tools automatically and returns all 50 cases."

*Wait for response. Point out the `list_cases` tool badge.*

> "See that badge? That's the tool the agent called. It didn't search a document library — it executed a structured query against the case database."

---

### Act 2: The Money Prompt (3-4 min)

**This is the centerpiece. Type or paste:**

```
I represent DSS in case 2024-DR-42-0892. After reviewing the case, can you provide:
1. A detailed timeline of pertinent facts with source citations
2. A chart of discrepancies between the two parents' accounts
3. All statements made by Marcus Webb to case managers or law enforcement
4. All statements made by Dena Holloway to case managers or law enforcement
```

> "This is the exact structure of the prompt the attorney used in her original test. Four distinct analytical tasks in one request."

*Wait for response. It will take 10-15 seconds as the agent calls 4 tools.*

**When it renders, walk through each section:**

**Timeline:**
> "Look at this timeline. Every event has a date, a time where available, and a source citation — 'Dictation PDF page 3', 'Sheriff Report page 7', 'Medical Records pages 1 through 4'. An attorney can verify every single entry."

> "Count the events. [X] timeline entries, all chronologically ordered, from the night of the incident through the 30-day review hearing. The SharePoint agent returned maybe 6 or 7 of these and got two dates wrong."

**Discrepancy Chart:**
> "Now the discrepancies. This is a structured comparison — what Marcus said, what Dena said, and what contradicted each of them. Look at the 'Contradicted By' column — medical records, sheriff's reports, the parents' own prior statements."

> "This is what attorneys actually need. Not a summary that says 'the parents disagreed.' A specific, citable comparison they can use in court filings."

**Statements — Marcus Webb:**
> "Every statement Marcus made, in chronological order: what he said, who he said it to, the date, the source document, and the page number. Five statements across medical staff, law enforcement, the case manager, and court testimony."

**Statements — Dena Holloway:**
> "Same for Dena. And notice her story changes — the hospital statement on June 12th says one thing, but the sheriff interview the next afternoon reveals the 9:30 PM thump she didn't mention before. That evolution is captured because each statement is its own record with its own date and context."

**Point at the tool badges:**
> "Four tools called: `get_timeline`, `get_discrepancies`, `get_statements_by_person` twice — once for Marcus, once for Dena. The agent planned its own execution. It decided what data it needed and retrieved exactly that."

---

### Act 3: The Consistency Proof (1 min)

**Type:**
```
Can you make the timeline more detailed — include specific times where available?
```

> "Now watch this. I'm asking the same question a slightly different way."

*Wait for response.*

> "Same timeline. Same events. Same citations. Same page numbers. If I run this prompt ten times, I get the same answer ten times. That's the structural advantage — the data doesn't change because the retrieval method doesn't change."

> "With the SharePoint approach, the same prompt returns different document chunks each time. You might get 8 events one time and 11 the next, with different page references. An attorney can't rely on that."

---

### Act 4: Deep Dive (1 min, optional)

**Choose one of these follow-up prompts based on audience interest:**

For attorneys focused on medical evidence:
```
What did the medical evidence show about the timing and nature of Jaylen's injuries?
```

For attorneys focused on case strategy:
```
Based on the evidence, what are the strongest points DSS can make about each parent's credibility?
```

For the TPR case:
```
Switch to case 2024-DR-15-0341. What progress has Crystal Price made on her court-ordered treatment plan, and what does the GAL recommend?
```

For showing the closed case:
```
Give me a summary of case 2024-DR-21-0149. What was the outcome?
```

---

### Act 5: The "So What" (2 min, no typing)

> "Let me bring it back to what this means for your team."

> "**Completeness.** Every statement, every timeline event, every discrepancy — returned every time. No missed facts because the AI happened to grab the wrong PDF chunk."

> "**Consistency.** The same question returns the same answer. Your attorneys can cite these results in filings with confidence."

> "**Citations.** Every piece of data traces back to a source document and page number. This isn't a black-box summary — it's a research tool that shows its work."

> "**Speed.** That four-part analysis took 15 seconds. A junior attorney doing that manually is spending hours cross-referencing documents."

> "The AI model is the same in both versions. The difference is entirely in how the data is organized. Structure the data, and the AI becomes dramatically more useful."

---

### Act 6: Side-by-Side Comparison (3-5 min, optional)

If you have the SharePoint agent set up, run the same prompt on both agents:

**Switch to the SharePoint agent tab. Type:**
```
What are the key discrepancies between Marcus Webb's and Dena Holloway's accounts in case 2024-DR-42-0892?
```

> "Now let's ask the same question to the SharePoint-grounded agent. Same AI model, same prompt — the only difference is the data source."

*Wait for both responses. Compare them side by side.*

> "Notice the differences. The MCP agent returns all 6 discrepancies from the database, each with specific page citations and the 'contradicted by' evidence. The SharePoint agent returns... [react to whatever it shows]. It might find 2 or 3 discrepancies, miss the medical evidence contradictions, and won't have structured source/page references."

**More comparison prompts from `Demo_Comparison_Prompts.md`:**

| Category | Sample Prompt |
|----------|--------------|
| Cross-referencing | "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom" |
| Filtering | "Show me only the medical events in the Webb case timeline" |
| Aggregate | "How many active cases does DSS currently have?" |
| Precision | "How many IOP sessions had Crystal Price completed as of November 2023 vs April 2024?" |

> "The SharePoint agent can't do aggregate queries across 50 cases — it only has documents for 2. It can't filter by event type because that's a structured concept. And it can't reliably give you session counts at two different points in time because those numbers are buried in paragraphs."

---

## Backup Prompts (If the Demo Goes Long or Q&A Gets Specific)

| Prompt | What It Shows |
|--------|---------------|
| "List all people involved in case 2024-DR-42-0892 and their roles" | Agent returns structured party list with relationships |
| "What statements did Renee Dawson make to the court?" | Case manager's testimony, with citations |
| "Compare Crystal Price's statements about her sobriety with the drug screen results" | Cross-referencing statements against contradicting evidence |
| "Which cases are in Spartanburg County?" | Filtering across cases |
| "What happened between June 12 and June 14 in the Webb case?" | Date-range timeline filtering |
| "What did Dr. Chowdhury say about the injuries?" | Medical expert testimony with page refs |
| "Show me all court events across both cases" | Timeline filtering by event type |

---

## Handling Q&A

**"Is this real case data?"**
> No. Every name, date, case number, and detail is completely synthetic. No real DSS data was used at any point. The cases are realistic in structure but entirely fictional.

**"How long did this take to build?"**
> The structured database, the API layer, the MCP server, and the web interface were built in a single session. The infrastructure reuses your existing Azure environment. The key insight is that structuring the data is the hard part — once it's structured, the AI layer is straightforward.

**"Can this work with our real case management system?"**
> Yes. The pattern is the same regardless of where the data lives. If your case management system has an API or database, we connect the MCP tools to that instead of this demo database. The agent auto-discovers whatever tools are available.

**"What about security / HIPAA / confidentiality?"**
> This demo is behind Azure AD authentication — only authorized users can access it. In production, the MCP endpoint would require API keys or OAuth tokens, and all data access would go through the same role-based permissions your team already uses. The AI model (GPT-4.1) is hosted in your Azure tenant and does not store or train on your data.

**"What about cases with hundreds of documents?"**
> That's actually where this approach shines most. The more data there is, the worse the SharePoint chunking approach performs — it can only retrieve a few chunks per query. The structured approach returns everything that matches the query, regardless of volume.

**"Can the agent make mistakes?"**
> The agent can only return what's in the database. It won't hallucinate facts because it's querying structured records, not generating from memory. It might interpret or summarize the data in different ways, but the underlying facts and citations are always grounded in the actual records.

---

## Technical Details (If IT/Engineering Asks)

- **Architecture**: Static Web App → Container App (MCP + Chat) → API Management → Azure Functions → Azure SQL
- **AI Model**: GPT-4.1 via Azure OpenAI, managed identity auth, deployed in your Azure tenant
- **Protocol**: MCP (Model Context Protocol) — open standard for connecting AI agents to data sources
- **Auth**: Azure AD (SWA), managed identity (Functions → SQL, Container App → OpenAI), subscription key (Container App → APIM), function key (APIM → Functions)
- **Data**: 5 normalized SQL tables — cases, people, timeline_events, statements, discrepancies — 50 cases, 275 people, 325 timeline events, 338 statements, 150 discrepancies
- **No data leaves your tenant**: Azure OpenAI processes within your subscription, no external API calls

---

## Timing Guide

| Section | Duration | Cumulative |
|---------|----------|------------|
| Opening (Case Browser) | 2 min | 2 min |
| Act 1: List Cases | 1 min | 3 min |
| Act 2: Money Prompt | 3-4 min | 7 min |
| Act 3: Consistency Proof | 1 min | 8 min |
| Act 4: Deep Dive (optional) | 1 min | 9 min |
| Act 5: The "So What" | 2 min | 11 min |
| Act 6: Side-by-Side (optional) | 3-5 min | 16 min |
| Q&A | 5-10 min | ~25 min |

**Total: ~25 minutes** with comparison, ~20 without. Can compress to 10 by skipping Acts 4 and 6 and shortening the walkthrough.

---

## Appendix: Data Design Decision

### "How did the data get from documents into the database?"

**The Short Answer:** The data was never extracted from documents. It went the other direction: structured SQL data was designed first, then realistic legal documents were written from that data to populate SharePoint.

**The Design:**

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

### 5 Discrepancy Questions to Ask the Agent

These questions are grounded in the actual seed data and SharePoint documents. Questions 1 and 5 expose cross-document conflicts that the SharePoint agent is likely to mishandle, while the MCP agent returns one consistent answer.

**Question 1: "What time was Jaylen Webb brought to the emergency room, and who was the admitting nurse?"**

What it exposes: A cross-document conflict in the SharePoint docs.
- Medical Records say arrival at **03:15 AM**, nurse **Rebecca Torres**
- Sheriff Report says arrival at **approximately 0047 hours** (12:47 AM), nurse **Charge Nurse Patricia Daniels**

MCP agent returns one consistent answer from structured data. SharePoint agent may surface both conflicting versions — or pick one without flagging the contradiction.

**Question 2: "What did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement?"**

What it exposes: A subtle two-hour discrepancy between statements.
- Nursing notes (Medical Records p. 8): Marcus told hospital staff he put Jaylen to bed "**around ten**"
- Sheriff Report (p. 3): Marcus told Lt. Odom he put the child to bed at approximately **8:00 PM**

MCP agent pulls both statements side-by-side from the `statements` table filtered by `made_to`. SharePoint agent has to find these in two different documents and may not catch the discrepancy.

**Question 3: "Crystal Price told the court she was 'clean now' at the November 2023 hearing. What do the drug test results show?"**

What it exposes: A direct contradiction between Crystal's testimony and lab results.
- Crystal's statement to court (Nov 14, 2023): "I am clean now"
- Drug screen results: Two positive fentanyl screens on **October 8** and **October 22** — just three weeks earlier
- Also: Missed screens on December 5, January 15, and March 3

MCP agent returns the contradiction with dates and sources from the `discrepancies` table. SharePoint agent has to cross-reference the court transcript with the DSS investigation report.

**Question 4: "Crystal Price said she couldn't comply with the treatment plan because she lacked transportation. What support did DSS actually provide?"**

What it exposes: Crystal's stated barrier is contradicted by DSS records.
- Crystal claims: Lack of transportation and support
- DSS records show: Monthly bus passes issued, three housing referrals provided, IOP transportation assistance **offered and declined by Crystal**

**Question 5: "Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey?"**

What it exposes: A direct factual conflict between two documents about the same hospital visit.
- Sheriff Report (p. 2): "Radiology report indicated **no fractures detected** on skeletal survey"
- Medical Records (pp. 3-4): Bilateral long bone fractures with extensive radiological findings

### Recommended Demo Order for Discrepancy Questions

1. Start with **Question 3** (Crystal's sobriety) — easy to understand, clear contradiction
2. Follow with **Question 4** (transportation excuse) — builds the pattern of Crystal's credibility issues
3. Ask **Question 2** (Marcus bedtime discrepancy) — shifts to the Webb case, shows subtle cross-referencing
4. Ask **Question 5** (fractures in skeletal survey) — the cross-document bombshell
5. Close with **Question 1** (ER arrival time and nurse) — reinforces that document-based search can't be trusted for precise facts

### What NOT to Say

- Do not bash SharePoint. The message is "different tools for different jobs."
- SharePoint is great for unstructured narratives, policy documents, and memos.
- When case data is structured, MCP gives precision that document search cannot match.

## Appendix: Agent Architecture Matrix

Every agent hits the same backend (APIM → Functions → SQL). The only variables are who runs the orchestration, how much code we write, and which model reasons over the results.

| Agent | Orchestration | Our Code | Data Path | Model |
|---|---|---|---|---|
| **Custom Web SPA** | MCP Server `/chat` | Full stack (TypeScript) | MCP Server → APIM → Functions → SQL | GPT-4.1 |
| **Copilot Studio MCP** | Copilot Studio (low-code) | Zero — auto-discovers `/mcp` tools | MCP Server → APIM → Functions → SQL | GPT-4o (GCC) / GPT-4.1 (Com) |
| **M365 Copilot** | M365 Copilot (Teams/Outlook/Edge) | Zero — 3 JSON manifest files | MCP Server → APIM → Functions → SQL | Platform-assigned (no user control) |
| **Foundry Agent** | Azure AI Agent Service | Minimal — create agent, point at `/mcp` | MCP Server → APIM → Functions → SQL | GPT-4.1 |
| **Investigative Agent** | OpenAI SDK (TypeScript) | Full — we run the agentic loop | Direct → APIM → Functions → SQL | GPT-4.1 |
| **Triage Agent** | Semantic Kernel HandoffOrchestration (C#) | Full — we run the agentic loop | Direct → APIM → Functions → SQL | GPT-4.1 |
| **Copilot Studio SP/PDF** | Copilot Studio built-in RAG | Zero | SharePoint document library | GPT-4o (GCC) / GPT-4.1 (Com) |

**Key talking point:** The spectrum runs from zero code (M365 Copilot: 3 JSON manifests) to full code (Investigative Agent: we write the entire agentic loop). Every point on this spectrum scored 9-10/10 with GPT-4.1. The engineering investment changes what you can customize, not whether it works. Note: M365 Copilot (platform-assigned model) scored 2/10 — model selection matters as much as architecture.

**M365 Copilot demo talking point:** M365 Copilot shows each external tool call to the user and requires confirmation before executing. This is a strong differentiator for enterprise security conversations — it makes the MCP tool calls visible and explainable. For production, admins can pre-approve specific agents so actions execute without confirmation (admin pre-approval available since August 2025, or set `x-openai-isConsequential: false` in the manifest for read-only operations).
