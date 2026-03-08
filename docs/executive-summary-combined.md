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

## Use Case 2: Investigative Analytics

**Domain:** City of Philadelphia property and code enforcement investigation
**Data:** 34 million rows of real public records (584,000 properties, 1.6 million code violations)
**Agents tested:** 7 configurations (2 Copilot Studio structured database agents, 2 Copilot Studio document agents, 3 pro-code agents)
**Prompts tested:** 10 of 10 completed across 7 agents (70 total test runs)

### Results

The Commercial MCP agent (GPT-4.1) was the strongest overall performer, going 4 for 4 on the final stretch of prompts after initially struggling with address resolution. The Government Cloud document agent (SharePoint PDFs, GPT-4o) matched it on overall pass rate by leveraging pre-computed summaries in the investigation reports. The Government Cloud MCP agent (GPT-4o) was crippled by two issues: token overflow on large entities and the model gap vs GPT-4.1.

**Final standings (after Round 2 improvements):**

| Agent | Pass | Partial | Fail | Change from Round 1 |
|---|---|---|---|---|
| Philly MCP - Com (structured database, GPT-4.1) | **10** | 0 | 0 | +2P (was 8/0/2) — **PERFECT** |
| Philly SP/PDF - GCC (SharePoint docs) | 8 | 2 | 0 | unchanged |
| Philly SP/PDF - Com (SharePoint docs) | 8 | 2 | 0 | unchanged |
| Investigative Agent (OpenAI chat) | 8 | 1 | 1 | +7P (was 1/0/9) |
| Foundry Agent (Azure AI Foundry) | 8 | 1 | 1 | +4P (was 4/0/6) |
| Philly MCP - GCC (structured database, GPT-4o) | 4 | 3 | 3 | +2P (was 2/0/8) |
| Triage Agent (Semantic Kernel) | 1 | 1 | 8 | +1P, +1Pa (was 0/0/10) |

**Critical finding:** Address resolution was the #1 failure mode. Across Prompts 2-4, agents attempted 15 address-to-parcel lookups and succeeded only twice (13% success rate). Every SQL-backed agent resolved "4763 Griscom St" to a different wrong parcel number on different attempts — producing non-deterministic, unreliable answers. This led directly to the Round 2 improvement: a dedicated fuzzy address search tool.

**Finding #2:** GPT-4.1 vs GPT-4o produced an 80% vs 20% pass rate gap for MCP agents — the largest model-driven difference in either use case.

**Finding #3:** Aggregate queries (citywide stats, zip code comparisons) worked reliably for all MCP agents. Address-based queries failed reliably. The failure pattern was predictable and fixable.

## What's Next: Round 3 Candidates

Round 2 retesting is complete. Three issues remain that could be addressed in a Round 3:

1. **GCC MCP token overflow on P1** — the entity network summary mode was built but the Copilot Studio GCC action may not be passing `summary=true`. Configuration fix, not a code change.
2. **P6 top private violators** — 3 of 4 agents return government entities instead of private owners. The `get_top_violators` tool needs an `exclude_government` filter parameter.
3. **MCP-Com nurse lookup (UC1)** — the nurse is stored with role="Witness" in the people table. Changing to role="Medical Staff" or "Nurse" might help the model recognize it as relevant to a nurse question.

## Pro-Code Agent Architectures

Use Case 2 introduced two agents not available in Use Case 1: an Investigative Agent built with Semantic Kernel and OpenAI, and a Foundry Agent built with Azure AI Foundry. Both query the same structured database as the Copilot Studio agents but through custom-built agent loops rather than a low-code platform.

Results across 10 prompts show these agents share the same data access as Copilot Studio but differ in how they process results. The Foundry Agent produced the best analytical moment in the entire evaluation (challenging a premise against source data on Prompt 10). The Investigative Agent had the most dramatic improvement — from 1/10 to 8/10 after Round 2 tool changes. The Triage Agent (Semantic Kernel team-of-agents) scored 0/10 in Round 1 and only 1/10 after Round 2 — proving that architectural complexity does not guarantee quality and can prevent agents from benefiting from improvements that lift simpler architectures.

This is the question every technology leader faces: **build or buy?** The structured database versus document comparison answers "what data architecture do I need." The Copilot Studio versus pro-code comparison answers "what agent architecture do I need." Together, they form a complete decision framework for government AI adoption.

## The Iterative Improvement Process

Deploying an AI agent is not a one-time event. It is an iterative engineering process where each round of testing reveals a different category of failure, each requiring a different type of fix. Organizations that skip this process — deploying a Copilot Studio agent, pointing it at a SharePoint library, and expecting production-quality results — will encounter every failure mode documented in this report.

This evaluation went through three distinct phases:

### Round 0: Baseline Testing

Deploy the agent, test it against known prompts with known answers, and document every failure. This project tested 11 agent configurations across 10 prompts (110 test runs for Use Case 1) and 7 agent configurations across 10 prompts (70 test runs for Use Case 2). Failures were categorized into a danger taxonomy ranging from silent failures (medium severity) to faithfully reproduced misinformation (critical severity).

**Key insight:** You cannot evaluate an agent without ground truth. For Use Case 1, synthetic data with known answers made scoring binary (right or wrong). For Use Case 2, real data introduced ambiguity — but even ambiguous prompts revealed clear agent failures (wrong parcel numbers, token overflows, hallucinated facts).

### Round 1: Data Layer Improvements

Testing revealed that structured database agents failed specific prompts because the data wasn't granular enough for the model to extract. Drug test results buried in a narrative court event description were invisible to the model. A skeletal survey finding missing from the database meant agents couldn't answer the most dangerous prompt in the suite.

**Changes made:** 11 new SQL rows (discrete drug test events, skeletal survey findings, nurse records) and 1 tool filter addition (`made_to` parameter on the statements tool). Zero changes to the documents or agent configuration.

**Results:** Retesting the 5 affected prompts across 3 MCP agents showed improvement from 2 Pass / 5 Partial / 8 Fail to 12 Pass / 2 Partial / 1 Fail. The remaining failures shifted from "missing data" to "model behavior" — a fundamentally different problem requiring a different fix.

### Round 2: Tool Architecture and Prompt Engineering

With the data layer corrected, Round 2 addressed how models interact with tools. Use Case 2 revealed an 87% failure rate on address-based queries — not because the data was wrong, but because no tool existed to convert a street address into a database identifier. Use Case 1 revealed that agents had nurse data available but never called the tool that returns it, because the tool description didn't mention it contained medical staff.

**Changes made:** 1 new tool (fuzzy address-to-parcel lookup with USPS normalization), 1 tool enhancement (entity network summary mode to prevent token overflow), improved tool descriptions across both use cases, and system prompt additions with explicit workflow guidance. Zero data changes.

**Results (43 retests):**

| Agent | Round 1 | Round 2 | Change |
|-------|---------|---------|--------|
| COM MCP (GPT-4.1) | 8P / 0Pa / 2F | **10P / 0Pa / 0F** | Perfect score |
| Investigative Agent | 1P / 0Pa / 9F | **8P / 1Pa / 1F** | +7 Pass |
| Foundry Agent | 4P / 0Pa / 6F | **8P / 1Pa / 1F** | +4 Pass |
| GCC MCP (GPT-4o) | 2P / 0Pa / 8F | **4P / 3Pa / 3F** | +2 Pass |
| Triage Agent (SK) | 0P / 0Pa / 10F | **1P / 1Pa / 8F** | +1 Pass (still last) |

The single highest-impact change was the address resolution tool: zero address lookup failures in Round 2 for agents that used it, compared to 87% failure in Round 1. The Triage Agent — the only agent that did not use `search_properties` — continued to resolve addresses to wrong parcels, confirming that the tool was the fix, not the prompts.

### The Pattern for Organizations

Every organization deploying AI agents will go through these same rounds, in this order:

1. **Test with known answers.** Without ground truth, you cannot measure improvement. Build a test suite before you build the agent.
2. **Fix the data first.** If the answer isn't in the data, no model or prompt will find it. Make facts discrete and queryable, not buried in narrative text.
3. **Fix the tools second.** If the model can't reach the data through the available tools, add tools. If the model doesn't know which tool to use, improve descriptions and add system prompt guidance.
4. **Retest after every change.** Each fix can introduce new failure modes. The only way to know is to run the full test suite again.

This is not optional engineering overhead — it is the difference between a demo that impresses and a deployment that misleads. The danger taxonomy from this evaluation (false negatives, faithfully reproduced misinformation, misattribution, confident hallucination) represents real risks to real decisions. An attorney who trusts "no fractures detected" because an AI agent said so is making a worse decision than an attorney with no AI at all.

## Five Findings That Surprised Us

1. **The most dangerous agent was also the most accurate quoting its source.** Seven of eight document-based agents faithfully reproduced a Sheriff Report statement that "no fractures detected on skeletal survey" — while the Medical Records in the same case clearly documented two fractures in a child abuse investigation. The agents weren't wrong about what the document said. They were wrong about what was true. This is the hardest failure mode to detect because the citation is real and the confidence is justified — but the conclusion is dangerous.

2. **The most sophisticated agent architecture scored 1 out of 10 — even after improvements that lifted simpler agents to 8.** The Triage Agent — a Semantic Kernel team-of-agents pattern with a routing agent dispatching to specialized sub-agents (OwnerAnalyst, ViolationAnalyst, AreaAnalyst) — produced the worst results of any configuration tested across both rounds. In Round 1 it scored 0/10 (crashes, wrong prompts, 500 errors). After Round 2 tool improvements that lifted the Investigative Agent from 1/10 to 8/10, the Triage Agent improved to only 1/10. It still resolved addresses to wrong parcels because its sub-agents never called the new address lookup tool. Meanwhile, a simple Copilot Studio agent pointed at SharePoint PDFs scored 8 out of 10 without any improvements at all. Architectural complexity is not a proxy for quality — and can actively prevent agents from benefiting from tool improvements.

3. **The model retrieved the answer and didn't recognize it.** On Use Case 1, Prompt 3, the custom web application agent called the right tools, received data containing "two positive drug screens (fentanyl) in October," and concluded: "no drug test results exist in the available data." The answer was in the tool output. The model read past it. This "false negative" failure — data retrieved but not recognized — is invisible to users because the agent sounds confident and the tool calls look correct.

4. **A single missing tool caused an 87% failure rate — and adding it back produced the largest improvement.** Use Case 2 had no way to convert a street address ("4763 Griscom St") into a database identifier (parcel number 232452100). Six of ten prompts mentioned street addresses. Across those six prompts and five SQL-backed agents, only 2 of 15 address lookups succeeded. Every agent resolved the same address to a different wrong parcel on different attempts — producing non-deterministic, unreliable answers to the same question. Adding one fuzzy-match lookup tool produced zero address resolution failures in Round 2 retesting. The Investigative Agent went from 1/10 to 8/10. The COM MCP agent achieved a perfect 10/10. Same data, same models, same code — one new tool.

5. **A pro-code agent challenged its own premise — and was right.** On Prompt 10, the Foundry Agent (Azure AI Foundry) was asked about a purchase price of $146,000 versus a $357,100 assessment. Instead of calculating the percentage, it checked the OPA assessment data and found the actual assessed value was $53,155 — not the $357,100 stated in the prompt. It flagged the discrepancy and recalculated using the verified number. No other agent questioned the premise. This is the kind of analytical rigor that justifies the engineering investment in custom agents — but only when paired with the iterative testing process that makes them reliable.

## Cross-Use-Case Conclusions (Preliminary)

1. **Structured data wins on consistency and precision.** Across both use cases, structured database agents return the same answer every time for the same question. Document agents' answers vary based on which chunks the retrieval engine surfaces.

2. **Documents win on narrative context.** Details like institutional histories, investigator observations, and contextual explanations live in documents, not databases. Both approaches are needed.

3. **Real data is harder than synthetic data.** Use Case 1's synthetic data had clean ground truth. Use Case 2's real data introduced ambiguity on the very first prompt. Government AI deployments will face Use Case 2's complexity, not Use Case 1's clarity.

4. **Government Cloud model constraints matter.** Government Cloud Copilot Studio is locked to GPT-4o while Commercial uses GPT-4.1. This model gap consistently affected accuracy across both use cases.

5. **Tool design is as important as model selection.** The Government Cloud structured database agent failed Prompt 1 not because the model was weak, but because the tool returned 631 raw records instead of a summary. The best model in the world can't help if the tool overwhelms its context window.

---

*Use Case 1: Complete (110 test runs + 15 Round 1 retests + 3 Round 2 retests). Use Case 2: Complete (70 Round 1 runs + 50 Round 2 retests). Total: 248 test runs across 2 improvement rounds.*

*Detailed results: `use-case-1-testing.md` | `use-case-2-testing.md` | `improvements/improvements-round-1.md` | `improvements/improvements-round-2.md`*
