# Agent Evaluation — Combined Executive Summary

## Purpose

This document summarizes the findings from evaluating AI agent configurations across two government use cases. The evaluation compares structured database agents against document-based agents to determine which approach delivers more accurate, consistent, and trustworthy answers for government analysts.

## Use Case 1: Legal Case Analysis

**Domain:** Department of Social Services, Office of Legal Services
**Data:** 50 synthetic legal cases with 277 people, 333 timeline events, 338 statements, and 151 discrepancies
**Agents tested:** 11 configurations (3 structured database agents, 8 document-based agents)
**Prompts tested:** 10 legal analysis questions covering fact extraction, cross-document reasoning, contradiction detection, statement comparison, aggregate queries, and arithmetic

### Results

The custom web application agent scored a perfect 10/10. Structured database agents consistently returned accurate, citable answers but missed details not modeled in the database (e.g., the admitting nurse's name). Document-based agents found those missing details but suffered from misattribution, hallucination, and inability to cross-reference across documents.

**Top 3 agents:**
1. Custom Web Application (structured database) — 10 Pass, 0 Partial, 0 Fail
2. Copilot Studio with structured database (Government Cloud, GPT-4o) — 9 Pass, 0 Partial, 1 Fail
3. Copilot Studio with structured database (Commercial, GPT-4.1) — 8 Pass, 2 Partial, 0 Fail

**Bottom 2 agents:**
- Copilot Studio with SharePoint documents (Government Cloud) — 3 Pass, 1 Partial, 6 Fail
- Copilot Studio with SharePoint PDFs (Government Cloud) — 3 Pass, 1 Partial, 6 Fail

**Critical finding:** 7 of 8 document-based agents repeated a misleading statement from one source document without checking it against the medical records — the AI equivalent of an analyst copying an error from one report into their own without verification.

### Danger Taxonomy

Testing revealed five categories of AI failure, ranked by severity:

1. **False negative (Critical):** The agent retrieved the correct data but failed to recognize the answer within it
2. **Misleading source faithfully reproduced (Critical):** The agent accurately quoted a source document that itself contained an error, presenting the error as fact
3. **Misattribution (High):** The agent reported a real fact but attributed it to the wrong person — e.g., attributing a mother's statement about bedtime to the father
4. **Hallucinated fact with confidence (High):** The agent invented a specific time, case number, or detail that does not exist in any source
5. **Silent failure (Medium):** The agent returned no results or a hallucinated case number without indicating anything went wrong

## Use Case 2: Investigative Analytics (In Progress)

**Domain:** City of Philadelphia property and code enforcement investigation
**Data:** 34 million rows of real public records (584,000 properties, 1.6 million code violations)
**Agents tested:** 5 configurations (2 Copilot Studio structured database agents, 1 Copilot Studio document agent, 2 pro-code agents from the investigation web application)
**Prompts tested:** 1 of 10 completed (testing started 2026-03-07)

### Early Findings (Prompt 1)

The first prompt — "How many properties does GEENA LLC own, and what percentage are vacant?" — immediately revealed a challenge absent from Use Case 1: **there is no single correct answer.**

Five agents returned three different property counts:

| Agent Type | Properties | Vacancy Rate | Methodology |
|---|---|---|---|
| Copilot Studio + structured database (Commercial) | 330 distinct parcels | 86.67% | Deduplicated by parcel number, explained methodology |
| Copilot Studio + SharePoint documents (Government Cloud) | 194 | 91.8% | Quoted the investigation report directly |
| Investigation web application (OpenAI) | 631 | ~60% | Used raw row count, estimated vacancy by sampling |
| Investigation web application (Foundry) | 631 | 45.3% | Used raw row count, filtered by category code |
| Copilot Studio + structured database (Government Cloud) | Error | Error | Token limit exceeded — data retrieved but too large to process |

The investigation report says 194 properties. The database returns 631 rows (including duplicates from multiple data sources) or 330 distinct parcels (depending on deduplication). The "correct" answer depends on how "ownership" is defined across entity networks — a question the human evaluator could not resolve either.

**Key observations:**
- The document-based agent gave the cleanest answer by quoting the pre-computed summary in the report
- The Commercial structured database agent gave the most analytically defensible answer — deduplicating, explaining methodology, and offering alternative calculations
- Both pro-code agents used raw row counts without deduplication, inflating the property count
- The Government Cloud structured database agent failed due to the tool returning all 631 property records instead of a summary — a tool design issue, not a model issue

### Remaining Prompts

9 prompts remain, testing cross-document synthesis, numeric extraction, ownership chain reconstruction, contradiction detection, city-wide aggregation (impossible for document agents), narrative extraction (designed to favor document agents), filtering precision, area statistics, and multi-step arithmetic.

## What's Next: Pro-Code Agent Architectures

Use Case 2 introduced two agents not available in Use Case 1: an Investigative Agent built with Semantic Kernel and OpenAI, and a Foundry Agent built with Azure AI Foundry. Both query the same structured database as the Copilot Studio agents but through custom-built agent loops rather than a low-code platform.

Early results (1 prompt) show these agents share the same data access as Copilot Studio but differ in how they process results. After all 10 prompts are complete, this section will evaluate whether the additional engineering investment of building custom agents produces meaningfully better answers than Copilot Studio — and for which types of questions.

This is the question every technology leader faces: **build or buy?** The structured database versus document comparison answers "what data architecture do I need." The Copilot Studio versus pro-code comparison answers "what agent architecture do I need." Together, they form a complete decision framework for government AI adoption.

## Cross-Use-Case Conclusions (Preliminary)

1. **Structured data wins on consistency and precision.** Across both use cases, structured database agents return the same answer every time for the same question. Document agents' answers vary based on which chunks the retrieval engine surfaces.

2. **Documents win on narrative context.** Details like institutional histories, investigator observations, and contextual explanations live in documents, not databases. Both approaches are needed.

3. **Real data is harder than synthetic data.** Use Case 1's synthetic data had clean ground truth. Use Case 2's real data introduced ambiguity on the very first prompt. Government AI deployments will face Use Case 2's complexity, not Use Case 1's clarity.

4. **Government Cloud model constraints matter.** Government Cloud Copilot Studio is locked to GPT-4o while Commercial uses GPT-4.1. This model gap consistently affected accuracy across both use cases.

5. **Tool design is as important as model selection.** The Government Cloud structured database agent failed Prompt 1 not because the model was weak, but because the tool returned 631 raw records instead of a summary. The best model in the world can't help if the tool overwhelms its context window.

---

*Use Case 1: Complete (110 test runs). Use Case 2: In progress (1 of 10 prompts). This document will be updated as Use Case 2 testing continues.*

*Detailed results: `use-case-1-testing.md` | `use-case-2-testing.md`*
