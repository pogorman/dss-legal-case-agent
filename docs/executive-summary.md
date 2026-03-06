# DSS Legal Case Agent — Executive Summary

## MCP-Backed Agents vs. Document-Backed Agents for Legal Case Analysis

### The Question

When attorneys need answers from case files, which approach delivers more reliable results: an AI agent backed by **structured data** (SQL database via MCP tools) or one backed by **unstructured documents** (PDFs and Word files in SharePoint or uploaded to Copilot Studio)?

### What We Tested

We built the same legal case data in two forms — a normalized SQL database with 50 cases, 275 people, 325 timeline events, 338 statements, and 150 documented discrepancies, and a set of 11 narrative legal documents (investigation reports, medical records, court orders, sheriff reports) covering 2 primary cases. We then tested **11 agent configurations** across **11 prompts** designed to simulate real attorney questions: timeline reconstruction, witness statement comparison, contradiction detection, filtering by event type, aggregate case queries, and arithmetic reasoning from case data.

### Key Findings

**1. Structured data agents are consistently precise; document agents are inconsistently rich.**

MCP-backed agents (Web SPA, Copilot Studio MCP) return complete, accurate answers on every prompt where the data exists in SQL. On timeline enumeration, all 3 MCP agents scored 12/12 events with zero fabrication. Document agents ranged from 12/12 (best case) to 4/12 with data from the wrong case mixed in.

**2. Every agent has a failure mode — there is no unconditional winner.**

| Failure Type | Severity | Example | Which Agents |
|---|---|---|---|
| Cross-case contamination | Critical | Case 2 (Crystal Price) data injected into Case 1 timeline | SP/PDF - GCC |
| Misleading source faithfully reproduced | Critical | 7/8 doc agents repeated Sheriff Report's incorrect "no fractures" claim | All doc agents except SP/PDF - Com |
| False negative on retrieved data | Critical | GPT-4.1 agents never call `get_discrepancies` — conclude "no evidence" when contradiction data exists | Web SPA, MCP - Com |
| Misattribution | High | 4/8 doc agents attribute Dena Holloway's statement to Marcus Webb | SP/DOCX-Com, KB/DOCX-Com, SP/PDF-GCC, KB/DOCX-GCC |
| Hallucinated fact with confidence | High | MCP-GCC fabricated "2:00 AM" ER time (actual: 3:15 AM) | MCP - GCC |
| Timeline collapse | Medium | Investigation phase (5 events) compressed into 1 vague paragraph | KB/PDF - Com |
| Silent failure | Medium | Hallucinated a case number, returned no results, gave no warning | Web SPA on Case 2 |

**3. The model matters as much as the architecture.**

GCC Copilot Studio is locked to GPT-4o; Commercial uses GPT-4.1. Neither can be changed. This creates a measurable split:

- **GPT-4o (GCC):** Better tool selection (always calls `get_discrepancies`), uses precise legal phrasing ("materially changes her account"), gets bedtime time correct (10 PM). Worse fact faithfulness — fabricates when uncertain.
- **GPT-4.1 (Commercial):** Better fact faithfulness, fewer hallucinations. Worse tool selection — never calls the discrepancy detection tool, leading to false negatives on contradiction questions.

**4. Document format and retrieval method affect results more than expected.**

| Format | Avg Score (Prompt 5) | Notes |
|---|---|---|
| MCP / SQL | 12/12 | Deterministic, complete |
| SharePoint PDF (Com) | 12/12 | Strongest doc agent overall |
| SharePoint DOCX (Com) | 12/12 | 8 PM error + fabricated event |
| SharePoint DOCX (GCC) | 9/12 | Correct facts, limited sources |
| KB PDF (GCC) | 10/12 | Best KB agent |
| KB DOCX (Com) | 9/12 | Good investigation, no post-removal |
| KB DOCX (GCC) | 8/12 | Single source doc |
| KB PDF (Com) | 6/12 | Collapsed timeline |
| SharePoint PDF (GCC) | ~4/12 | Cross-case contamination |

**5. Structured data fails responsibly; documents fail dangerously.**

When MCP agents lack data (e.g., the skeletal survey question), they say "this information is not in the structured data" — an honest absence. When document agents encounter a misleading source, they reproduce it faithfully with a citation. The citation makes the wrong answer *look* authoritative. An attorney reading "no fractures detected [Sheriff Report, p. 3]" has no reason to doubt it — but the medical records show two fractures that the sheriff report's summary omitted.

### The Recommendation

Neither approach alone is sufficient. The strongest architecture **layers both**:

- **Structured data (MCP/SQL)** for precision queries: timelines, people rosters, statement comparisons, discrepancy detection, aggregate counts, filtering by event type or audience. These are the questions attorneys ask most and where wrong answers are most dangerous.
- **Document grounding (SharePoint/KB)** for narrative detail the schema doesn't capture: nursing notes, page-level citations, clinical observations, GAL home visit narratives. These enrich the structured answers with context.
- **Human review remains essential.** No agent configuration — structured or unstructured — was correct on every prompt. The value of AI is speed and coverage, not infallibility. The right question is not "can I trust the agent?" but "does the agent surface enough for me to make a better decision, faster?"

### Results at a Glance

Each prompt tests a different attorney question type. The table below shows how the three architecture groups performed and the key takeaway.

| # | Prompt | MCP (3 agents) | Best Doc Agent | Worst Doc Agent | Key Takeaway |
|---|--------|---------------|----------------|-----------------|-------------|
| 1 | ER time + nurse | 2/3 correct time; 0/3 found nurse | KB/PDF-Com: time + nurse + employee ID | SP/DOCX-GCC: found nothing | Nurse only in documents, not SQL — need both layers |
| 2 | Marcus Webb statements | Web SPA: full quotes, cross-doc analysis | KB/PDF-Com: 10 PM correct, detailed | SP/PDF-GCC: missed hospital stmt + 8 PM error | 4/8 doc agents misattribute Dena's words to Marcus |
| 3 | Crystal Price "clean now" | GCC: best (used discrepancies tool); GPT-4.1: false negative | SP/PDF-Com: 3-doc synthesis, dates, missed screens | Web SPA: hallucinated case # then missed contradiction | GPT-4.1 never calls `get_discrepancies` — misses contradictions |
| 4 | Skeletal survey fractures | Honest absence — "not in data" | SP/PDF-Com: **only agent** to catch cross-doc conflict | 7/8 doc agents: repeated Sheriff's incorrect "no fractures" | Most dangerous prompt — misleading source faithfully reproduced |
| 5 | Full timeline (12 events) | All 3: 12/12 | SP/PDF-Com: 12/12, richer medical detail | SP/PDF-GCC: ~4/12, **Case 2 contamination** | Structured data makes enumeration trivial; doc agents range 4–12 |
| 6 | People roster (8 people) | All 3: 8/8 | SP/PDF-Com: 8/8 + 4 doc-only extras | SP/PDF-GCC & SP/DOCX-GCC: 5/8 | Doc agents found 4 real people not in SQL — genuine value-add |
| 7 | Statement evolution (3 changes) | Web: 3/3; GCC: 3/3; Com: **2/3** | SP/PDF-Com: 3/3 + fear motive + summary table | MCP-Com: 2/3 (missed rough handling) | Strongest consensus — 10/11 found all changes |
| 8 | LE statements filter (4 stmts) | **All 3 MCP agents failed** (tool lacks audience filter) | SP/DOCX-Com: 4/4, identified intermediate interview | SP/PDF-GCC: 0/4, returned court testimony | First prompt where doc agents strictly outperform MCP |
| 9 | TPR cases (9 in DB) | All 3: **9/9** | SP/DOCX-Com: 1/9 + statutory citations | All doc agents: 1/9 (expected) | Aggregate queries are MCP's strongest advantage — doc agents can't search across cases |
| 10 | Time gap (thump → ER) | Com: **gold standard** (all 3 times, both gaps); GCC: ~4h (imprecise) | SP/DOCX-Com: 5h45m exact | SP/PDF-GCC: fabricated 7:30 AM → 10h | Arithmetic reasoning exposes every agent's weaknesses — even correct retrieval ≠ correct calculation |

### Agent Scorecard

Grades: **Pass** = accurate and useful. **Partial** = correct core facts but shallow, minor errors, or missing depth. **Fail** = wrong answer, dangerous error, or critical omission. **N/A** = data not in source; agent was honest about it.

| Agent | Model | P1: ER Time | P2: Marcus Webb | P3: Crystal Price | P4: Skeletal Survey | P5: Timeline | P6: People | P7: Stmt Evolution | P8: LE Filter | P9: TPR Cases | P10: Time Gap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Web SPA** | GPT-4.1 | Pass (no nurse) | **Pass** — best quotes | **Fail** — hallucinated case #, then missed fentanyl | Partial — fractures from SQL, no doc conflict | **Pass** 12/12 | **Pass** 8/8 | **Pass** 3/3, discrepancy ref | **Fail** — tool lacks audience filter | **Pass** 9/9 | **Fail** — conflated thump w/ discovery, said 1h15m |
| **MCP - Com** | GPT-4.1 | Pass (no nurse) | Partial — needed case # | Partial — found it, no dates | N/A — honest absence | **Pass** 12/12 | **Pass** 8/8 | Partial — **2/3**, missed rough handling | **Fail** — 3 tries, all failed | **Pass** 9/9 | **Pass** — gold standard, all 3 times + both gaps |
| **MCP - GCC** | GPT-4o | **Fail** — hallucinated 2:00 AM | **Pass** — consistent ×3 | **Pass** — used discrepancies tool | N/A — honest absence (w/ case #) | **Pass** 12/12 | **Pass** 8/8 | **Pass** 3/3 + 6 discrepancies | Partial — pivoted to timeline, 2/4 | **Pass** 9/9 | Partial — ~4h (should be 4.5h) |
| **SP/PDF - Com** | GPT-4.1 | **Pass** + nurse | Partial — no quotes | **Pass** — 3-doc gold standard | **Pass** — caught cross-doc conflict | **Pass** 12/12 | **Pass** 8/8 + 4 extras | **Pass** 3/3 + fear motive + table | **Pass** 4/4, 3 sources | Partial — 1/9 + flagged CPS as potential TPR | **Pass** — 4.5h, distinguished 2 AM vs 3:15 AM |
| **SP/DOCX - Com** | GPT-4.1 | **Pass** + nurse | **Fail** — 8 PM misattribution | Partial — contradiction, no dates | **Fail** — repeated "no fractures" | Partial 12/12 — 8 PM error + fabrication | **Pass** 8/8 + 4 extras | **Pass** 3/3 + "material" framing | **Pass** 4/4, intermediate interview | Partial — 1/9 + statutory citations | **Pass** — 5h45m exact |
| **KB/DOCX - Com** | GPT-4.1 | **Pass** + nurse | **Fail** — 8 PM + missed hospital | **Pass** — specific dates | **Fail** — repeated "no fractures" | Partial 9/12 | **Pass** 8/8 + 2 extras | **Pass** 3/3, 3 sources | **Pass** 4/4, unique Marcus quote | Partial — 1/9 | **Pass** — 4.5h |
| **KB/PDF - Com** | GPT-4.1 | **Pass** + nurse + ID | **Pass** — 10 PM, detailed | **Pass** — dates + missed screens | **Fail** — repeated "no fractures" | **Fail** 6/12 — collapsed timeline | **Pass** 8/8 + 2 extras | **Pass** 3/3 + grandmother detail | **Pass** 4/4, DSS follow-ups | Partial — 1/9 | Partial — honest absence of ER time, 2.5h only |
| **SP/PDF - GCC** | GPT-4o | Pass (no nurse) | **Fail** — missed hospital + 8 PM | Partial — shallow | **Fail** — repeated "no fractures" | **Fail** ~4/12 — Case 2 contamination | **Fail** 5/8 | **Pass** 3/3 | **Fail** — returned court testimony | Partial — 1/9, generic framing | **Fail** — fabricated 7:30 AM, said 10h |
| **SP/DOCX - GCC** | GPT-4o | **Fail** — nothing found | Partial — correct, shallow | Partial — shallow | **Fail** — repeated "no fractures" | Partial 9/12 | **Fail** 5/8 | **Pass** 3/3 | **Fail** — returned hospital versions | Partial — 1/9 | **Pass** — 4.5h correct |
| **KB/PDF - GCC** | GPT-4o | Partial — 12:47 AM (real doc time) | Partial — correct, thin | **Pass** — specific dates | **Fail** — repeated "no fractures" | **Pass** 10/12 | **Pass** 8/8 + 3 extras | **Pass** 3/3 | **Pass** 4/4, best GCC | Partial — 1/9, GAL detail | Partial — 3h17m (used Sheriff Report 12:47 AM) |
| **KB/DOCX - GCC** | GPT-4o | Partial — 12:47 AM (real doc time) | **Fail** — 8 PM misattribution | **Pass** — specific dates | **Fail** — repeated "no fractures" | Partial 8/12 | Partial 7/8 | **Pass** 3/3, best demeanor analysis | **Pass** 4/4, no 8 PM error | Partial — 1/9, procedural detail | Partial — 2.5h (thump→discovery, not hospital) |

### Win/Loss Summary

| Agent | Pass | Partial | Fail | N/A |
|---|---|---|---|---|
| **SP/PDF - Com** | **8** | 2 | 0 | 0 |
| **KB/DOCX - Com** | 6 | 2 | 2 | 0 |
| **MCP - GCC** | 6 | 2 | 1 | 1 |
| **KB/PDF - Com** | 6 | 2 | 2 | 0 |
| **Web SPA** | 6 | 1 | 3 | 0 |
| **SP/DOCX - Com** | 5 | 3 | 2 | 0 |
| **MCP - Com** | 5 | 3 | 1 | 1 |
| **KB/PDF - GCC** | 5 | 4 | 1 | 0 |
| **KB/DOCX - GCC** | 3 | 5 | 2 | 0 |
| **SP/DOCX - GCC** | 2 | 4 | 4 | 0 |
| **SP/PDF - GCC** | 2 | 2 | 6 | 0 |

**SP/PDF - Com is the clear winner** with 8 Passes and zero Fails across all 10 prompts — the only agent with no dangerous errors on any question type. MCP-Com redeemed itself on Prompt 10 with the gold standard response (all three time milestones, both gap calculations), while the Web SPA failed its third prompt by conflating the thump with the discovery event. SP/PDF-GCC remains the weakest agent with 6 Fails including a fabricated 7:30 AM hospital time on Prompt 10.

**Final verdict:** The layered approach holds — MCP/SQL for precision (timelines, aggregates, completeness) and document grounding for narrative richness (nurse names, statutory citations, clinical observations). Neither alone is sufficient.

### Testing Status

| Prompt | Category | Status |
|---|---|---|
| 1. ER time + nurse | Fact extraction | Complete (11 agents) |
| 2. Marcus Webb statements | Cross-doc reasoning | Complete (11 agents) |
| 3. Crystal Price "clean now" | Contradiction detection | Complete (11 agents) |
| 3.2. Transportation barrier | Contradiction detection | Complete (MCP only) |
| 4. Skeletal survey | Cross-doc conflict | Complete (11 agents) |
| 5. Full timeline | Completeness | Complete (11 agents) |
| 6. People roster | Completeness | Complete (11 agents) |
| 7. Statement evolution | Change detection | Complete (11 agents) |
| 8. LE statements filter | Filtering precision | Complete (11 agents) |
| 9. TPR cases | Aggregate query | Complete (11 agents) |
| 10. Time gap calculation | Arithmetic | Complete (11 agents) |

---

*Testing conducted March 5-6, 2026. Full results: `docs/copilot-studio-testing.md`*
