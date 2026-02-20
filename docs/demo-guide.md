# DSS Legal Case Intelligence — Demo Guide

## Demo URL
**https://happy-wave-016cd330f.1.azurestaticapps.net**

## MCP Endpoint (for Copilot Studio)
**https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/mcp**

---

## The Story (Know This Cold)

A DSS attorney named Laurel tested an AI agent backed by unstructured case documents in SharePoint. She asked it for a timeline, discrepancies, and statements from both parties. Her feedback: **"It was not as detailed as I imagined — missing statements, incorrect on some timeline items."**

This demo shows WHY that happened and HOW to fix it. Same Copilot Studio agent, same prompt, two backends:
- **Version A** (SharePoint): Chunked PDFs, inconsistent retrieval, missing data
- **Version B** (MCP + SQL): Structured data, every record returned, fully cited

The audience should experience the difference themselves before you explain what changed.

---

## Pre-Demo Checklist

- [ ] Sign into the SWA URL and verify you see the app (do this 10 min before)
- [ ] The Container App may cold-start — send a quick "List available cases" to warm it up
- [ ] Have the SharePoint agent results ready for side-by-side comparison (screenshots or live)
- [ ] Know the primary case number: **2024-DR-42-0892** (CPS) and secondary: **2024-DR-15-0341** (TPR)
- [ ] There are **50 total cases** across all SC circuits — the agent can list and query any of them

---

## Demo Script

### Opening (2 min)

**Click the Case Browser tab.**

> "Before we start talking to the agent, let me show you what's behind it. There are 50 synthetic cases in the database — completely fictional, no real data — modeled on real DSS case structures across all 16 judicial circuits."

**Click into case 2024-DR-42-0892.**

> "This is a CPS emergency removal. You can see the parties — two parents, the child, a case manager, law enforcement, a GAL, medical witnesses. Below that: timeline events, statements, discrepancies. All structured. All queryable."

**Point at the stat cards (timeline count, statement count, discrepancy count).**

> "The key difference from the SharePoint approach: this data isn't buried in PDFs. Every statement has a speaker, a date, a recipient, and a page citation. Every timeline event has a type and source document. The AI doesn't have to guess what's in a document — it queries exactly what it needs."

**Click Back, then switch to Agent Chat tab.**

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

> "This is the exact structure of the prompt Laurel used in her original test. Four distinct analytical tasks in one request."

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
| Q&A | 5-10 min | ~20 min |

**Total: ~20 minutes** including Q&A. Can compress to 10 if needed by skipping Acts 4 and shortening the walkthrough.
