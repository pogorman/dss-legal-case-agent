# AI Agent Accuracy Spectrum -- Presenter Guide

## The Framework

This demo is built around a five-level accuracy spectrum that helps government leaders decide where AI agents are safe to deploy aggressively, where they need guardrails, and where human review is non-negotiable.

| Level | Name | Stakes | Key Question |
|---|---|---|---|
| 1 | Information Discovery | Minor inconvenience | "Help me find the right document" |
| 2 | Summarization | Wasted time | "Summarize this report for my briefing" |
| 3 | Operational Support | Misallocated resources | "Show me the portfolio-level picture" |
| 4 | Investigative | Missed evidence | "Cross-reference these records" |
| 5 | Legal/Adjudicative | Wrong legal outcome | "Prepare the facts for this hearing" |

**The story arc:** Start where AI is easy and reliable. Escalate to where engineering decisions determine success or failure. End with the trust-but-verify moment that makes you credible.

---

## Demo URLs

- **DSS Web App:** https://happy-wave-016cd330f.1.azurestaticapps.net
- **MCP Endpoint:** https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/mcp
- **Primary Case:** 2024-DR-42-0892 (CPS, Webb/Holloway)
- **Secondary Case:** 2024-DR-15-0341 (TPR, Price)

---

## Pre-Demo Checklist

- [ ] Sign into SWA URL 10 minutes before
- [ ] Click "Warm Up" button to prime the cold-start chain
- [ ] Have SharePoint agent open in a separate browser tab (for Level 2 comparison)
- [ ] Have `sharepoint-docs/Demo_Comparison_Prompts.md` open for reference
- [ ] Know the case numbers: 2024-DR-42-0892 (CPS) and 2024-DR-15-0341 (TPR)
- [ ] Have the slide deck open for the framework overview
- [ ] Test that the chat widget responds before the audience arrives

---

## Key Stats to Memorize

| Stat | Value |
|---|---|
| Total test runs | 305 across 19 agent configurations |
| Document agents (Levels 1-2) | 8/10 with zero engineering |
| GPT-4.1 agents (Levels 3-5) | 9.5/10 average |
| GPT-4o agents (GCC model gap) | 4/10 average |
| One fuzzy search tool | 13% to 100% accuracy |
| Document agents on skeletal survey | 7 of 8 reproduced a misleading finding |

---

## Demo Flow

### Opening: The Hook (3-4 minutes, no product)

> "Some of you may remember me from such demos as the delegation demo, or the [insert another landmark demo here]. And there's one thing those demos have in common with this one: I like to build test harnesses that demonstrate the different capabilities of our technology in real-world use cases that my customers care about. And what's funny is -- both this demo and the delegation demo deal with the same fundamental topic: **accuracy**."

> "Before we dive in, let me tell you what this demo is and what it isn't. **It's a way to show you a process and methods -- with real-world examples -- for making your agents better.** It is not a demo on data extraction, other than to provide ideas on tools and process for getting that done when extraction is necessary."

> "I have a feeling that when we're all said and done, you'll have more questions than answers. But let's get into it."

**Show the five-level spectrum slide.**

> "We developed this framework after running 305 test evaluations across two government use cases and 19 different agent configurations. Not all AI use cases need the same level of accuracy, and not all agent architectures deliver it."

> "Level 1: finding a policy document. Level 5: preparing facts for a legal hearing where a family's future depends on accuracy. Most agencies jump straight to Copilot without asking 'where does my use case fall on this spectrum?' Today I'll show you why that question matters."

---

### Act 1: Level 2 -- Summarization Works Out of the Box (2 minutes)

> "Let's start at Level 2 -- summarization. This is where most agencies start, and the good news is: it works."

**If SharePoint agent is available, show it:**

> "Here's a Copilot Studio agent pointed at a SharePoint document library. No custom code. I'll ask it to summarize a case."

```
Summarize the investigation report for the Webb/Holloway case. What are the key findings?
```

> "Solid summary. It found the main themes, identified the parties, got the narrative right. For a policy analyst preparing a briefing, this is perfectly useful. Score: 8 out of 10 in our testing. No engineering required."

> "But watch what happens when we ask harder questions."

---

### Act 2: Level 3 -- Aggregate Queries (2 minutes)

**Switch to the DSS Web App. Open the Case Browser.**

> "Now I'm switching to our structured data agent. There are 50 synthetic cases in this database -- completely fictional, no real data -- modeled on real case structures."

**Click the chat widget. Ask:**

```
How many active cases does DSS currently have? Break them down by case type.
```

> "Aggregate questions -- 'how many', 'what's the breakdown' -- these work reliably across every agent type we tested. Even the weakest performers got these right. This is Level 3: operational decision support."

> "But here's where it gets interesting. What happens when we move from 'show me the big picture' to 'show me the details for this specific case'?"

---

### Act 3: Level 4 -- The Inflection Point (5-7 minutes)

**This is the centerpiece of the demo.**

> "Now, there's no way to have this conversation without getting a little technical. But I'll do my best."

> "Level 4 is investigative work. Cross-referencing records, building timelines, finding discrepancies between accounts. This is where agent architecture starts to matter -- a lot."

**Type the money prompt:**

```
I represent DSS in case 2024-DR-42-0892. After reviewing the case, can you provide:
1. A detailed timeline of pertinent facts with source citations
2. A chart of discrepancies between the two parents' accounts
3. All statements made by Marcus Webb to case managers or law enforcement
4. All statements made by Dena Holloway to case managers or law enforcement
```

> "This is the exact prompt structure a DSS attorney used when she tested an earlier version. Four analytical tasks in one request."

*Wait for response (10-15 seconds).*

**Walk through each section:**

**Timeline:**

> "Every event has a date, a time where available, and a source citation -- page number in the original document. An attorney can verify every entry. Count them: [X] timeline entries, all chronologically ordered. The SharePoint agent returned maybe 6 or 7 and got two dates wrong."

**Discrepancy Chart:**

> "Structured comparison -- what Marcus said versus what Dena said, with the evidence that contradicts each. Not 'the parents disagreed.' Specific, citable contradictions an attorney can use in court filings."

**Statements (Marcus Webb):**

> "Every statement Marcus made, in chronological order: what he said, who he said it to, the date, the source document, and the page number."

**Statements (Dena Holloway):**

> "Same for Dena. And notice her story changes -- the hospital statement on June 12th says one thing, but the sheriff interview the next afternoon reveals the 9:30 PM thump she didn't mention before. That evolution is captured because each statement is its own record."

**The data point:**

> "This agent scored 10 out of 10 in our evaluation. The same prompt sent to the SharePoint document agent? It scored 3. It missed statements, got dates wrong, and couldn't produce the discrepancy chart at all."

**If time allows, show the model gap:**

> "Here's the number that should keep you up at night. Same tools, same data, same backend: GPT-4.1 agents averaged 9.5 out of 10. GPT-4o -- which is what Government Cloud Copilot Studio uses today -- scored 4 out of 10. The model is the bottleneck."

---

### Act 4: Level 5 -- Trust But Verify (3-4 minutes)

> "Now here's the slide I want you to remember after everything else fades."

**Type:**

```
Did the sheriff's investigation find fractures in Jaylen Webb's skeletal survey?
```

*Wait for response.*

> "The agent returns the medical records showing bilateral long bone fractures, with the radiology findings and page numbers. That's the right answer."

> "But here's what happened when we asked a document-based agent the same question. Seven out of eight document agents quoted the Sheriff's Report -- which says 'no fractures detected on skeletal survey.' The medical records in the same case clearly document fractures. The Sheriff's Report was wrong. The AI faithfully reproduced the error."

> "This is Level 5. The agent was not wrong about what the document said. It was wrong about what was true. The citation was real. The confidence was justified. The conclusion was dangerous."

> "In a child welfare case, an attorney who trusts 'no fractures detected' because an AI said so is making a worse decision than an attorney with no AI at all."

**Pause. Let it land.**

**The human review thread -- connect it to their daily experience:**

> "Think about how you already use AI today. Copilot helps you draft an email -- you review it before you hit send. Copilot helps you write code -- you better be reviewing that before it goes to production. So why would we skip human review for any of these five levels? Especially at Level 5, where the stakes are a family's future?"

> "This is why Level 5 requires a different operating model. The AI is a research assistant -- it drafts, it retrieves, it organizes. The human decides. Trust but verify is not a suggestion at this level. It is the only responsible way to operate."

---

### Act 5: What This Means for Your Agency (3 minutes, no typing)

> "Let me bring it back to your decisions."

> "**Levels 1 and 2:** Deploy now. Point Copilot at your SharePoint libraries. You'll get 80 percent accuracy with zero custom engineering. That's a real productivity gain."

> "**Level 3:** Connect to your structured data. Case management systems, property databases, HR records. Model Context Protocol makes this straightforward -- the AI auto-discovers what data is available."

> "**Level 4:** This is where you need an engineering partner. Purpose-built tools, fuzzy matching, entity resolution, iterative testing against ground truth. One missing tool caused 87 percent of our failures. Adding it back produced the single largest improvement in the entire evaluation."

> "**Level 5:** Everything from Level 4, plus governance. Audit logging. Citation linking. Human review workflows. The AI accelerates the attorney -- it does not replace the attorney."

**The "So what?" close:**

> "So what do we do? Do we just give up on using agents?"

> "No. You continue to test them and make them better. And you always adhere to trust but verify."

> "In my world, I have agents building apps for me right now. I'm not building production enterprise applications anymore, but if I were, I would have a team of human developers involved in the process -- checking the work my agents are producing with my guidance, helping to test, reviewing agentic test results. That's the operating model. The AI accelerates the team. The team validates the AI."

> "The question isn't 'should we deploy AI?' The question is 'which level are we operating at, and have we invested accordingly?'"

---

## Timing Guide (50-60 Minutes)

| Section | Duration | Running Total |
|---------|----------|---------------|
| Opening: Hook + Framework | 4-5 min | 5 min |
| Act 1: Level 2 Summarization | 3-4 min | 8 min |
| Act 2: Level 3 Aggregation (DSS + Philly) | 4-5 min | 13 min |
| Act 3: Level 4 Investigation (Money Prompt) | 8-10 min | 23 min |
| Act 3b: Side-by-Side Comparison | 5-7 min | 30 min |
| Act 3c: Use Case 2 (Philly Properties) | 5-7 min | 37 min |
| Act 4: Level 5 Trust But Verify | 5-6 min | 43 min |
| Act 5: Code Spectrum + GCC Guidance | 5-7 min | 50 min |
| Q&A | 10-15 min | 60-65 min |

### Expanded Sections for 50-60 Minutes

**Act 2 (expanded):** Show aggregate queries on BOTH use cases. After "How many active cases?", switch to Philly: "How many properties does GEENA LLC own?" Shows Level 3 works across domains with live structured data.

**Act 3b: Side-by-Side Comparison (new section):**
Run the money prompt on the SharePoint agent in a separate tab. Walk through what's missing, what's wrong, and what's different. Use 2-3 of the discrepancy questions from Appendix C. This is where the "structured data vs documents" argument becomes visceral.

**Act 3c: Use Case 2 (new section):**
Switch to Philly property investigation. Show address resolution in action:
```
Tell me about the property at 4763 Griscom Street. Who owns it, what violations does it have, and what's the ownership history?
```
Then show the aggregate power:
```
What are the top 5 addresses by code violation count, excluding government-owned properties?
```
Talking point: "Same architecture, completely different domain. The tools are different but the pattern is identical."

**M365 Copilot (optional, time permitting):**
If you show M365 Copilot, lean into the orchestration UX -- the confirmation dialog shows every tool call before it executes. This is actually a great demo asset for enterprise security conversations:
> "Notice it's showing you exactly what it's about to do and asking for permission. This is the kind of transparency enterprise customers want. You can see the orchestration happening in real time."
Note: Confirmation can be disabled via admin pre-approval or `x-openai-isConsequential: false` in the manifest.

**Act 5 (expanded):** Walk through the code spectrum slide (zero code to full code) and the GCC-specific guidance. This is where you land the services conversation: "Levels 1-3 are Copilot licenses you already own. Levels 4-5 are where we help."

**Compressed (20 min):** Skip Acts 1, 3b, 3c. Shorten Act 3 to just the money prompt result. Skip Act 5 code spectrum.

**Standard (35 min):** Skip Act 3c (Philly). Shorten side-by-side to one comparison prompt.

---

## Handling Q&A

**"Is this real data?"**
> No. All 50 DSS cases are completely synthetic. The Philadelphia property data is real public records (34 million rows) but contains no personally identifiable information. We tested on both synthetic and real data -- real data is harder.

**"How long did this take to build?"**
> The structured database, API layer, MCP server, and web interface were built in a single session. The iterative testing and tool improvements took 6 rounds. The key insight: structuring the data is the hard part. Once it's structured, the AI layer is straightforward.

**"Can this work with our case management system?"**
> Yes. Same pattern regardless of where data lives. If your system has an API or database, we connect MCP tools to that instead of this demo database. The agent auto-discovers whatever tools are available.

**"What about security?"**
> Azure AD authentication, managed identity for all service-to-service auth, AI model hosted in your Azure tenant, no data leaves your tenant. At Level 5, add audit logging of every tool call and human review gates.

**"Can the agent make mistakes?"**
> Yes -- and we documented exactly how. [Show the danger taxonomy.] The structured data agent won't hallucinate facts that aren't in the database, but it can miss data it retrieves (false negative), attribute facts to the wrong person (misattribution), or faithfully reproduce errors from source documents.

**"What about Government Cloud?"**
> Government Cloud Copilot Studio is currently locked to GPT-4o, which scored 4 out of 10 on investigative queries in our testing. For Levels 1 through 3, GPT-4o is adequate. For Levels 4 and 5, deploy pro-code agents using Azure OpenAI GPT-4.1 directly. When Government Cloud upgrades to a more capable model, Copilot Studio agents will benefit immediately.

---

## Appendix A: Data Design Decision

### "How did the data get from documents into the database?"

**The short answer:** The data was never extracted from documents. Structured SQL data was designed first, then realistic legal documents were written from that data for the SharePoint comparison.

**How to frame it:**

> "This is what digitization looks like. Your agency already has this information -- it's in Word documents, PDFs, case files scattered across SharePoint. What we did is model that same information as structured data: timelines, statements, people, discrepancies. The MCP agent queries the database; the SharePoint agent searches the filing cabinet. Same facts, dramatically different precision."

You do not need to explain which came first. The audience cares about the outcome: structured data enables precise queries, cross-referencing, and aggregation that document search cannot match.

### The data engineering story (if asked about the process)

> "I took a very first cut at chunking up the data -- deciding what a 'timeline event' is, what a 'statement' is, what a 'discrepancy' looks like as structured fields. Then I used an AI coding agent to generate additional cases and refine the schema. Two hand-crafted cases became 50, with increasing detail at every round."

> "This is the part people underestimate. The AI layer on top is straightforward once you've done the data engineering. Deciding what to extract, how to schema it, what granularity matters -- that's the investment that separates Level 3-4 from Level 1-2."

---

## Appendix B: Agent Architecture Matrix

Every agent hits the same backend (APIM to Functions to SQL). The only variables are who runs the orchestration, how much code you write, and which model reasons over the results.

| Agent | Orchestration | Code Required | Data Path | Model |
|---|---|---|---|---|
| Custom Web SPA | MCP Server `/chat` | Full (TypeScript) | MCP to APIM to Functions to SQL | GPT-4.1 |
| Copilot Studio MCP | Copilot Studio | Zero | MCP to APIM to Functions to SQL | GPT-4o (GCC) / GPT-4.1 (Com) |
| M365 Copilot | M365 platform | Zero (3 JSON files) | MCP to APIM to Functions to SQL | Platform-assigned |
| Foundry Agent | AI Agent Service | Minimal | MCP to APIM to Functions to SQL | GPT-4.1 |
| Investigative Agent | OpenAI SDK | Full (TypeScript) | Direct to APIM to Functions to SQL | GPT-4.1 |
| Triage Agent | Semantic Kernel | Full (C#) | Direct to APIM to Functions to SQL | GPT-4.1 |
| Copilot Studio SP/PDF | Built-in RAG | Zero | SharePoint docs | GPT-4o (GCC) / GPT-4.1 (Com) |

**Key insight:** Every architecture scored 9 to 10 out of 10 with GPT-4.1. The engineering investment buys customization and governance, not accuracy, which comes from the model and data. Exception: M365 Copilot (platform-assigned model) scored 2 out of 10 -- model selection matters as much as architecture.

---

## Appendix C: Five Discrepancy Questions

These questions are grounded in the actual seed data and SharePoint documents. They expose cross-document conflicts that document agents are likely to mishandle.

**Recommended demo order:**

**1. Crystal's sobriety (easy to understand, clear contradiction)**

```
Crystal Price told the court she was "clean now" at the November 2023 hearing. What do the drug test results show?
```

Crystal's statement: "I am clean now" (November 14, 2023). Drug screens: two positive fentanyl screens on October 8 and October 22 -- three weeks earlier. Also missed screens on December 5, January 15, and March 3.

**2. Transportation excuse (builds the credibility pattern)**

```
Crystal Price said she couldn't comply with the treatment plan because she lacked transportation. What support did DSS actually provide?
```

Crystal claims: lack of transportation and support. DSS records show: monthly bus passes issued, three housing referrals provided, IOP transportation assistance offered and declined by Crystal.

**3. Marcus bedtime discrepancy (subtle cross-referencing)**

```
What did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement?
```

Nursing notes (Medical Records p. 8): Marcus told hospital staff "around ten." Sheriff Report (p. 3): Marcus told Lt. Odom approximately 8:00 PM. Two-hour discrepancy.

**4. Skeletal survey (the cross-document bombshell)**

```
Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey?
```

Sheriff Report (p. 2): "no fractures detected on skeletal survey." Medical Records (pp. 3-4): bilateral long bone fractures with extensive radiological findings. Direct factual conflict between two documents about the same hospital visit.

**5. ER arrival time and nurse (reinforces document unreliability)**

```
What time was Jaylen Webb brought to the emergency room, and who was the admitting nurse?
```

Medical Records: arrival at 03:15 AM, nurse Rebecca Torres. Sheriff Report: arrival at approximately 0047 hours (12:47 AM), nurse Charge Nurse Patricia Daniels. Two conflicting versions of the same event.

---

## Appendix D: Copilot Studio Value Prop (Tech Series)

When presenting to a technical audience, you MUST articulate why Copilot Studio matters in this story. This is not a "pick your own adventure" -- Copilot Studio is the platform that ties it together.

**Key points to land:**

1. **Single platform for declarative AND pro-code agents.** The same Copilot Studio environment hosts the zero-code SharePoint agent (Level 1-2) and the MCP-connected structured data agent (Level 3-4). One governance boundary, one admin console, one DLP policy set.

2. **Model flexibility is the headline.** Same Copilot Studio agent, swap GPT-4o for GPT-4.1, and accuracy goes from 4/10 to 10/10 without changing a single line of configuration. That's a platform story, not a coding story. When GCC gets a better model, every Copilot Studio agent improves overnight.

3. **Enterprise governance is built in.** DLP policies, audit logging, admin pre-approval for tool calls, the M365 Copilot confirmation UX. These are not things you bolt on later -- they come with the platform.

4. **M365 distribution.** Agents show up where users already work: Teams, Copilot chat, SharePoint. No separate app to deploy or URL to bookmark. For Level 1-3 use cases, this is the fastest path to adoption.

5. **The test data proves it.** Our evaluation shows the platform works -- the limiting factor is the model, not the platform. Commercial Copilot Studio MCP scored a perfect 10/10 with GPT-4.1. The architecture is sound.

**The services hook:**
> "Levels 1-3 are Copilot licenses you already own. Levels 4-5 are where purpose-built tools and iterative testing come in -- and where we can help."

---

## Appendix E: What Not to Say

- Do not bash SharePoint. The message is "different tools for different jobs."
- SharePoint is great for unstructured narratives, policy documents, and memos (Levels 1-2).
- When case data needs cross-referencing and precision (Levels 4-5), structured data with MCP delivers what document search cannot.
- Do not promise Government Cloud will get GPT-4.1 on a specific date.
- Do not suggest the AI replaces human judgment at Level 5. The agent accelerates the human.
