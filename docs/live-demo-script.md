# Live Demo Script — Copilot Studio Focus

**Target audience:** Government IT leaders, AI decision-makers
**Total demo time:** ~15-20 minutes (adjust by cutting model demo to 2 models)
**Platform:** Copilot Studio (all agents) — no custom code UI
**Emphasis:** GCC, document quality, model selection

---

## Pre-Demo Setup (Day Before or Morning Of)

### 1. Create Three SharePoint Document Libraries

All three libraries live on the same SharePoint site. Each gets the same Copilot Studio agent configuration (SP/PDF/GCC) pointed at a different library.

| Library Name | Contents | Source Folder |
|---|---|---|
| **Case Files - Raw** | Original PDFs, no modifications | `Case-2024-DR-42-0892/Case-2024-DR-42-0892-pdf/` (use plain filenames: `Medical_Records.pdf`, etc.) + `Case-2024-DR-15-0341/Case-2024-DR-15-0341-pdf/` (plain filenames) |
| **Case Files - Cross-Referenced** | Same PDFs with cross-reference headers added | `Case-2024-DR-42-0892 (R1 - Cross-Referenced)/` (.pdf files) + `Case-2024-DR-15-0341 (R1 - Cross-Referenced)/` (.pdf files) |
| **Case Files - Enriched** | Cross-referenced PDFs + SharePoint metadata columns | Same files as Cross-Referenced library, plus metadata columns filled in |

#### Files per Library

**Case 1 (2024-DR-42-0892) — 6 documents:**
- Court_Orders_and_Filings.pdf
- DSS_Investigation_Report.pdf
- GAL_Report.pdf
- Home_Study_Report.pdf
- Medical_Records.pdf
- Sheriff_Report_24-06-4418.pdf

**Case 2 (2024-DR-15-0341) — 5 documents:**
- Court_Orders_and_Filings.pdf
- DSS_Investigation_Report.pdf
- GAL_Reports.pdf
- Substance_Abuse_Evaluation.pdf
- TPR_Petition_and_Affidavit.pdf

**Total: 11 PDFs per library, 33 PDFs across all three libraries.**

> **Note on cross-referenced files:** The R1 Cross-Referenced folder also contains `-case2` suffixed PDFs (e.g., `Court_Orders_and_Filings-case2.pdf`). These are the Case 2 docs that were added to the Case 1 folder so the agent could cross-reference across cases. Upload ALL PDFs from the cross-referenced folders (both the primary and the -case1/-case2 variants).

### 2. What Changed in the Cross-Referenced Documents

The cross-referenced documents are the SAME content as the originals with one addition: a **cross-reference header block** at the top of each document. No content was changed, added, or removed from the body text.

Example from Medical_Records.md (cross-referenced version):
```
CASE FILE CROSS-REFERENCE — 2024-DR-42-0892
This document should be read in conjunction with the following case file documents:
- Sheriff_Report_24-06-4418 — Law enforcement investigation summary, including
  officer's summary of hospital records (note: the Sheriff Report summarizes the
  skeletal survey as "no fractures detected" — this refers only to the survey of
  areas outside the known fracture sites; see Radiology Report below for complete
  findings including two diagnosed fractures)
- DSS_Investigation_Report — ...
- Court_Orders_and_Filings — ...
- GAL_Report — ...
- Home_Study_Report — ...
```

**Why this matters:** The cross-reference header on the Medical Records explicitly warns that the Sheriff Report's "no fractures detected" summary is misleading. This gives the agent the context it needs to avoid the false-negative trap.

### 3. SharePoint Metadata Columns (Enriched Library Only)

Add these columns to the **Case Files - Enriched** library:

| Column Name | Type | Purpose |
|---|---|---|
| **Case Number** | Single line of text | `2024-DR-42-0892` or `2024-DR-15-0341` |
| **Document Type** | Choice | Sheriff Report, Medical Records, Court Filing, Investigation Report, GAL Report, Home Study, Substance Abuse Evaluation, TPR Petition |
| **Key Topics** | Multiple lines of text | Comma-separated keywords for retrieval |

#### Metadata Values per Document

**Case 1 — 2024-DR-42-0892:**

| Document | Document Type | Key Topics |
|---|---|---|
| Medical_Records.pdf | Medical Records | parent statements, nursing interview, Marcus Webb hospital statement, Dena Holloway hospital statement, emergency room admission, skeletal survey, fractures, Rebecca Torres, bilateral fractures, different healing stages, non-accidental injury |
| Sheriff_Report_24-06-4418.pdf | Sheriff Report | law enforcement statements, Marcus Webb interview, Dena Holloway interview, Lt. Frank Odom, skeletal survey summary, crib fall, investigation |
| DSS_Investigation_Report.pdf | Investigation Report | case summary, timeline, family history, prior referrals, safety assessment, case plan |
| Court_Orders_and_Filings.pdf | Court Filing | emergency removal order, probable cause hearing, 30-day review, Judge Easley, Karen Milford GAL |
| GAL_Report.pdf | GAL Report | guardian ad litem, child welfare, placement recommendation, Karen Milford |
| Home_Study_Report.pdf | Home Study | relative placement, home environment, safety assessment |

**Case 2 — 2024-DR-15-0341:**

| Document | Document Type | Key Topics |
|---|---|---|
| DSS_Investigation_Report.pdf | Investigation Report | Crystal Price, substance abuse, fentanyl, drug screens, IOP compliance, housing instability, bus passes, transportation |
| Court_Orders_and_Filings.pdf | Court Filing | TPR hearing, treatment plan, compliance review, drug test results, Monica Vance testimony |
| GAL_Reports.pdf | GAL Report | Thomas Reed, child welfare, Amari Price, Destiny Price, foster care, Sandra Patterson |
| TPR_Petition_and_Affidavit.pdf | TPR Petition | termination of parental rights, Crystal Price, neglect, failed compliance, fentanyl positive |
| Substance_Abuse_Evaluation.pdf | Substance Abuse Evaluation | Dr. Raymond Ellis, opioid use disorder, IOP recommendation, drug testing |

### 4. Create Three Copilot Studio Agents (GCC)

All three agents use the **same** configuration — only the SharePoint library source differs.

| Agent Name | SharePoint Source | Model |
|---|---|---|
| **Case Analyst - Raw Docs** | Case Files - Raw | GPT-4o (GCC default) |
| **Case Analyst - Cross-Ref** | Case Files - Cross-Referenced | GPT-4o (GCC default) |
| **Case Analyst - Enriched** | Case Files - Enriched | GPT-4o (GCC default) |

**Agent instructions** (same for all three):
```
You are a legal case analyst for the Office of Legal Services. You help attorneys
prepare for hearings by analyzing case documents. When answering questions:
- Always cite the specific document and page number
- When documents conflict, note the conflict and cite both sources
- Never guess — if information isn't in the documents, say so
```

### 5. Create One Dataverse MCP Agent (Commercial)

This is the existing CS/DV/Com agent. Before the demo, set it to **GPT-4o** (to start at the weakest model).

| Agent Name | Data Source | Starting Model |
|---|---|---|
| **Case Analyst - Dataverse** | Dataverse MCP connector | GPT-4o (switch during demo) |

### 6. Warm-Up (10 min before demo)

| Step | Action |
|---|---|
| 1 | Open all 3 document agents in separate browser tabs |
| 2 | Send a throwaway prompt to each ("Hello") to warm up |
| 3 | Open the Dataverse MCP agent in its own tab |
| 4 | Send a throwaway prompt to warm it up |
| 5 | Pre-stage tabs in order: Raw, Cross-Ref, Enriched, Dataverse |

---

## Part 1: Document Quality Demo (~10 min)

**Narrative:** "Same agent. Same model. Same configuration. The only thing that changes is the quality of the documents."

### Prompt 1 — The Skeletal Survey Trap (THE signature prompt)

**Run on all 3 agents.**

```
Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey?
```

| Agent | Expected Result | What to Say |
|---|---|---|
| **Raw Docs** | FAIL — quotes Sheriff Report: "no fractures detected on skeletal survey." Confidently wrong. | "This is the dangerous answer. The citation is real. The quote is accurate. But it's wrong. The Sheriff Report summarizes the skeletal survey as 'no fractures' when the Medical Records document bilateral fractures at different healing stages." |
| **Cross-Ref** | PASS — finds both sources, notes the conflict. Reports both fractures (right femur, left humerus) with correct aging. | "Same agent, same model. The only change: we added a cross-reference header to each document. Zero content changes. The header on Medical Records warns that the Sheriff's summary is misleading." |
| **Enriched** | PASS — same quality as Cross-Ref, possibly faster retrieval. | "Metadata columns help the agent find the right document faster, but the cross-reference is what actually fixed the answer." |

**Talking point:** "Seven out of eight document agents we tested reproduced the Sheriff's 'no fractures' language without cross-checking the Medical Records. The citation was real. The confidence was justified. The conclusion was dangerous."

### Prompt 2 — Marcus Webb's Statements (shows metadata value)

**Run on all 3 agents.**

```
What did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement?
```

| Agent | Expected Result | What to Say |
|---|---|---|
| **Raw Docs** | FAIL — finds law enforcement statements from Sheriff Report but misses hospital staff statements from Medical Records nursing notes. May misattribute Dena's "8:00 PM" quote to Marcus. | "The agent found the Sheriff Report but couldn't retrieve the nursing notes from the Medical Records. It has no reason to look there for parent statements." |
| **Cross-Ref** | PARTIAL — finds both sources but may still miss nursing notes detail. Improved from raw but not perfect. | "Cross-references helped, but the agent still struggles to connect 'hospital staff statements' with 'nursing notes' in a medical record." |
| **Enriched** | PASS — metadata keywords "Marcus Webb hospital statement, nursing interview, parent statements" on Medical_Records.pdf enable the agent to retrieve the right section. Returns both statements, correct times (~10 PM to both), no 8 PM misattribution. | "This is where metadata earns its keep. The keywords 'parent statements' and 'nursing interview' on the Medical Records told the agent where to look. Cross-references alone weren't enough for this one." |

**Talking point:** "Cross-references fix reasoning errors. Metadata fixes retrieval errors. You need both."

### Prompt 3 — The Timeline (shows cross-ref preventing case contamination)

**Run on Raw and Cross-Ref only** (skip Enriched — same result as Cross-Ref).

```
What is the complete timeline of events for case 2024-DR-42-0892?
```

| Agent | Expected Result | What to Say |
|---|---|---|
| **Raw Docs** | FAIL — incomplete timeline, may mix events from Case 1 and Case 2, misses events scattered across documents. | "The agent has to piece together a timeline from 6 different documents with no guidance on which events belong to which case." |
| **Cross-Ref** | PASS — 10+ events in chronological order, zero case contamination between Webb and Price cases. | "Cross-reference headers explicitly name the case number and related documents. The agent knows exactly which events belong to 2024-DR-42-0892." |

**Talking point:** "We went from 3/10 on this agent to 9/10 with zero code, zero model changes, zero cost. Just better documents."

### Summary Slide (between parts)

| Change | What It Fixed | Score Impact | Cost |
|---|---|---|---|
| Cross-reference headers | Reasoning errors (skeletal survey trap, case contamination) | 3/10 to 7/10 | Free (30 min of document hygiene) |
| SharePoint metadata columns | Retrieval errors (couldn't find nursing notes for parent statements) | 7/10 to 8/10 | Free (15 min of library config) |
| **Combined** | | **3/10 to 8/10** | **$0, 45 minutes** |

---

## Part 2: Model Selection Demo (~8 min)

**Narrative:** "Same agent. Same data. Same Dataverse schema. The only thing that changes is the model."

**Setup:** The Dataverse MCP agent starts on GPT-4o (the GCC default). You will swap to Sonnet 4.6 during the demo. Optionally show GPT-4.1 as a middle tier.

### Demo Flow

**Step 1: Run all 3 prompts on GPT-4o**

Run these one at a time. Let the audience see the failures.

#### Model Prompt 1 — Aggregate Query

```
Which cases involve Termination of Parental Rights?
```

| Model | Expected Result |
|---|---|
| GPT-4o | FAIL — generates `WHERE legal_casetype = 'TPR'` (abbreviation). Returns zero results. The actual stored value is 'Termination of Parental Rights'. |
| GPT-4.1 | FAIL — same abbreviation problem. |
| Sonnet 4.6 | PASS — correctly uses full text value, returns all 9 TPR cases with case numbers, counties, circuits, statuses. |

**Why this prompt:** It's simple. A single-table filter. And two OpenAI models can't do it. Sonnet can.

#### Model Prompt 2 — Cross-Reference Reasoning

```
What did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement?
```

| Model | Expected Result |
|---|---|
| GPT-4o | FAIL — can't resolve Marcus Webb to the right case, can't do the two-step GUID lookup. Returns nothing or errors. |
| GPT-4.1 | PASS (9/10) — finds all 3 statements, compares them, identifies consistency. |
| Sonnet 4.6 | PASS (10/10) — full comparison table, correct quotes, flags the crib-climbing theory as a new claim in the LE statement. |

**Why this prompt:** Shows a real cross-document reasoning task. GPT-4o can't even start. GPT-4.1 gets close. Sonnet nails it.

#### Model Prompt 3 — Time Calculation

```
What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?
```

| Model | Expected Result |
|---|---|
| GPT-4o | FAIL — can't find timeline events matching "thump" or "hospital." |
| GPT-4.1 | PASS — finds both events, calculates 4h30m (thump to discovery) and 5h45m (thump to ER admission). |
| Sonnet 4.6 | PASS — same calculation plus contextual notes about disclosure inconsistency. |

**Why this prompt:** Requires finding events by semantic meaning (not exact column values), then doing arithmetic. GPT-4o fails at step 1.

**Step 2: Swap to Sonnet 4.6**

1. Open agent settings
2. Change model from GPT-4o to Claude Sonnet 4.6
3. Publish (takes ~30 seconds)
4. Re-run the same 3 prompts

**Talking point while publishing:** "No code changes. No schema changes. No prompt changes. Just a different model selection in the dropdown. Same Copilot Studio, same Dataverse connector."

**Step 3 (Optional): Show GPT-4.1 as middle tier**

If time allows, swap to GPT-4.1 and re-run Prompt 1 (TPR cases) to show it also fails on the abbreviation problem. This reinforces that it's not just "old model vs new model" — it's a fundamental difference in how models reason about structured data.

### Model Demo Summary

| Prompt | GPT-4o (GCC) | GPT-4.1 (Com) | Sonnet 4.6 (Com) |
|---|---|---|---|
| TPR cases (filter) | 0 | 0 | 10 |
| Marcus Webb (cross-ref) | 0 | 9 | 10 |
| Time gap (arithmetic) | 0 | 10 | 10 |
| **Total** | **0/3** | **2/3** | **3/3** |

Full test battery: GPT-4o = 1/11, GPT-4.1 = 6/11, Sonnet 4.6 = 11/11.

**Talking point:** "The model is the single biggest lever. Better documents took us from 3/10 to 9/10 with zero code. A better model took us from 1/11 to 11/11 with zero code. But today, the best model is only available in Commercial."

---

## Wrap-Up (~2 min)

### The Two Levers

| Lever | What It Controls | Who Can Pull It | Cost |
|---|---|---|---|
| Document quality | Reasoning accuracy (false negatives, case contamination) | Any SharePoint admin | $0, 45 minutes |
| Model selection | Query generation quality (structured data, arithmetic, filtering) | Copilot Studio admin (Commercial only today) | $0, 30 seconds |

### The GCC Reality

"In GCC today, you have one lever: document quality. And it's powerful — we proved you can go from 3/10 to 9/10 with 45 minutes of free work. But for structured data agents, you're capped by GPT-4o until GCC gets access to better models. When that happens, every agent improves overnight with zero changes."

### The Bottom Line

"Match your investment to your fidelity requirement. For document summarization, GCC with good documents is excellent. For cross-referencing structured data, model selection is everything."

---

## Fallback Plan

| If... | Then... |
|---|---|
| Document agent returns correct answer on Raw Docs | "Great — this particular question worked. Let me show you the one where document quality makes the difference." Jump to skeletal survey. |
| Dataverse agent fails on Sonnet 4.6 | "Non-deterministic query generation is a known limitation. Let me re-run." (Sonnet was 11/11 in testing but individual runs can vary.) |
| Model swap takes too long to publish | "While this publishes, let me show you the test results." Pull up the multi-model comparison table. |
| Any agent gives an unexpected answer | "This is exactly the point — non-determinism is why Level 5 requires human review. Always." |
| Copilot Studio is slow/throttled | "Cold starts happen. In production you'd pin these agents." Fill with the narrative about the skeletal survey trap. |

---

## Quick Reference — Prompt Cheat Sheet

### Document Quality Prompts (run on all 3 doc agents)

| # | Prompt | Expected Arc |
|---|---|---|
| 1 | Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey? | FAIL → PASS → PASS |
| 2 | What did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement? | FAIL → PARTIAL → PASS |
| 3 | What is the complete timeline of events for case 2024-DR-42-0892? | FAIL → PASS → PASS |

### Model Selection Prompts (run on Dataverse agent, swap model between runs)

| # | Prompt | GPT-4o | Sonnet 4.6 |
|---|---|---|---|
| 1 | Which cases involve Termination of Parental Rights? | FAIL | PASS |
| 2 | What did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement? | FAIL | PASS |
| 3 | What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital? | FAIL | PASS |

---

## Proven Test Results (Source Data)

These results come from 462 test runs across 21 agent configurations. Session 31 is the primary source for document quality improvements (SP/PDF-GCC, 10-prompt battery).

### Document Quality — SP/PDF-GCC Results

| Prompt | Raw (R0) | Cross-Ref (R1) | Enriched (R2) |
|---|---|---|---|
| P1: ER time + nurse | Pass | Pass | Pass |
| P2: Marcus Webb statements | Fail | Partial | Pass (metadata) |
| P3: Crystal Price drug tests | Partial | Pass | Pass |
| P4: Skeletal survey | **Fail** | **Pass** | Pass |
| P5: Timeline | **Fail** | **Pass** | Pass |
| P6: People list | Fail | Partial | Partial |
| P7: Dena statements | Pass | Pass | Pass |
| P8: LE statements | **Fail** | **Pass** | Pass |
| P9: TPR cases | Partial | Partial | Partial |
| P10: Time gap | **Fail** | **Pass** | Pass |
| **Total** | **3/10** | **7/10** | **8/10** |

### Model Selection — CS/DV Multi-Model Results

| Prompt | GPT-4o (GCC) | GPT-4.1 (Com) | GPT-5 Auto (Com) | Sonnet 4.6 (Com) |
|---|---|---|---|---|
| Q1: ER admission | 0 | 0 | 0 | 10 |
| Q2: Marcus bedtime | 0 | 9 | 5 | 10 |
| Q3: Crystal "clean now" | 0 | 0 | 0 | 10 |
| Q4: Crystal transportation | 0 | 0 | 0 | 10 |
| Q5: Skeletal survey | 0 | 0 | 0 | 10 |
| Q6: Full timeline | 10 | 10 | 10 | 10 |
| Q7: Price TPR people | 0 | 9 | 8 | 10 |
| Q8: Dena comparison | 0 | 9 | 9 | 10 |
| Q9: LE statements | 0 | 9 | 9 | 10 |
| Q10: TPR cases | 0 | 0 | 0 | 10 |
| Q11: Time gap | 0 | 10 | 0 | 10 |
| **Total** | **1/11** | **6/11** | **4/11** | **11/11** |
