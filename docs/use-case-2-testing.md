# Use Case 2 Testing: Philly Poverty Profiteering

## Executive Summary

**Use Case 2: Investigative Analytics — Philly Poverty Profiteering**

Real public data from the City of Philadelphia (34M rows, 584K properties, 1.6M violations). Five investigation PDF reports about GEENA LLC and two properties. Testing started 2026-03-07. **All 10 prompts complete across 8 agents (176 total responses). Round 2 retesting complete (53 runs). Round 2 Take 2 Triage Agent retest complete (10 runs). Round 2 Take 3 (13 runs). Round 3 model validation (20 runs). M365 Copilot testing (10 runs).**

**Key early findings:**
- Prompt 1 produced 3 different property counts (194, 330, 631) — scoring shifts from "correct vs incorrect" to "defensible, sourced answer"
- Prompt 2: Both MCP Copilot Studio agents blocked by token limits; Foundry Agent is the standout; two pro-code agents failed dangerously (wrong parcel, false negative on violations)
- Prompt 3: **Address resolution is broken** — every SQL-backed agent resolved 4763 Griscom to a different wrong parcel. Only the document agent passed.
- Prompt 4: COM MCP finally resolved the correct parcel and produced a perfect ownership chain. 15 address resolution attempts across P2-P4, only 2 successes.
- Prompt 5: FMV ($53,155) was in the deed record, not assessment table — 4 agents searched the wrong table. COM MCP found it. SP/PDF-GCC is 5 for 5.
- Prompt 6: "MCP dominates" by design (citywide aggregate) — COM MCP and Foundry Agent both delivered complete top-5 lists. COM MCP's was the most accurate (included individuals + LLCs).
- Prompt 7: Designed as "Document dominates" but COM MCP matched the doc agent by combining SQL transfer records with general knowledge about bank failures (WaMu, IndyMac). COM MCP is 4 for 4 since P4.
- Prompt 8: Foundry Agent contradicts itself (45 failed in P2, 0 in P8 — same property, different parcel resolution). COM MCP and SP/PDF-GCC both got 45. Four agents report 0 failures for a 45-failure property.
- Prompt 9: No address resolution needed (zip codes) = all MCP agents pass. GCC MCP's first pass since P1. All 4 MCP agents agree on raw numbers. Triage answered P8 instead of P9.
- Prompt 10: COM MCP, SP/PDF, and Foundry all got 35.6% discount. GCC MCP and Investigative answered P9 instead. Triage crashed (500 error). Foundry challenged the $357,100 premise against OPA data — best analytical moment.

---

## Overview

Multiple agent configurations tested against 10 prompts comparing structured SQL (MCP) agents against document-backed (SharePoint PDF) agents. Unlike Use Case 1 (synthetic data, 50 cases), Use Case 2 uses real public data and the Philly Profiteering MCP server backed by a 34M-row SQL database.

---

## Agent Matrix

| Agent Name | Backend | Model | Project | Status |
|---|---|---|---|---|
| Philly MCP - GCC | Copilot Studio - Philly MCP/SQL | GPT-4o | Philly Profiteering | Active |
| Philly MCP - Com | Copilot Studio - Philly MCP/SQL | GPT-4.1† | Philly Profiteering | Active |
| Philly SP/PDF - GCC | Copilot Studio - SharePoint PDFs | GPT-4o | Philly Profiteering | Active |
| Philly SP/PDF - Com | Copilot Studio - SharePoint PDFs | GPT-4.1 | Philly Profiteering | Active |
| Investigative Agent | OpenAI (Web SPA) | GPT-4.1 | Philly Profiteering | Active |
| Foundry Agent | Azure AI Foundry (Web SPA) | GPT-4.1 | Philly Profiteering | Active |
| Triage Agent | Semantic Kernel team-of-agents (Web SPA) | GPT-4.1 | Philly Profiteering | Active |
| M365 Copilot | M365 Copilot (Teams/Outlook/Edge) - Philly MCP | Platform-assigned | Philly Profiteering | Active |

**Notes:**
- GCC Copilot Studio locked to GPT-4o; Commercial uses GPT-4.1 (see † below)
- † COM MCP Round 1-2 testing used GPT-5 Auto (Copilot Studio Commercial default). Discovered during Round 3 preparation. Agent reconfigured to GPT-4.1 and retested: identical 10/10. See "Round 3: Model Validation."
- M365 Copilot uses the same `/mcp` endpoint as Copilot Studio — zero code, 3 JSON manifest files. Model is platform-assigned (no user control).
- Investigative Agent, Foundry Agent, and Triage Agent are from the Philly Profiteering web SPA (mcp-apim project), not DSS
- These three agents represent pro-code agent architectures (OpenAI chat, Azure AI Foundry, Semantic Kernel team-of-agents) vs Copilot Studio's low-code approach
- Triage Agent uses a routing pattern: a triage agent dispatches to specialized sub-agents (OwnerAnalyst, ViolationAnalyst, etc.)

---

## Scoring Rubric

Unlike Use Case 1 where ground truth was fully known (synthetic data designed by the team), Use Case 2 uses real data where "correct" answers may be ambiguous. Property counts depend on deduplication logic, network traversal depth, and how "ownership" is defined across entity networks.

**Scoring criteria:**
- **Pass**: Gave a defensible, sourced answer. Methodology is sound even if numbers differ from the investigation report.
- **Partial**: Answered but with significant gaps, unsourced claims, or clearly wrong methodology.
- **Fail**: Did not answer (error/crash), hallucinated with no basis, or gave a fundamentally misleading response.

**Additional dimensions evaluated:**
- Did it answer the question?
- Did it explain its methodology?
- Is it consistent with its data source?
- Did it acknowledge ambiguity where appropriate?

---

## Test Prompts

| # | Prompt | What It Tests | Expected Winner |
|---|--------|--------------|----------------|
| 1 | GEENA LLC property count + vacancy % | Simple fact extraction | Tie |
| 2 | What happened to 4763 Griscom since purchase | Cross-document synthesis | Slight doc advantage |
| 3 | Assessment 2017 vs 2025 + explanation | Numeric extraction + causation | Tie |
| 4 | Complete ownership chain of 4763 Griscom | Chain reconstruction | Tie |
| 5 | $146K purchase vs $53K fair market value | Contradiction / discrepancy detection | Document advantage |
| 6 | Top 5 private violators citywide | Aggregate across 584K properties | MCP dominates |
| 7 | Financial institutions + what happened to them | Narrative context extraction | Document dominates |
| 8 | Failed violations count + investigator type | Filtering precision | Tie |
| 9 | Zip code comparison (19104 vs 19132) | Cross-area aggregate | MCP dominates |
| 10 | Purchase discount % + assessment change | Multi-step arithmetic | Tie |

**Design notes:**
- Prompts 6 and 9 are impossible for document agents (docs cover 2 properties; DB covers 584K)
- Prompt 7 is designed to favor document agents (institutional failure narrative not in SQL)
- Unlike Use Case 1 (synthetic), this is real public data — every number is verifiable

---

## Ground Truth

### Prompt 1: GEENA LLC Property Count and Vacancy Rate

Unlike Use Case 1 where ground truth was designed into the synthetic data, Prompt 1 immediately revealed that "ground truth" is ambiguous when querying real-world entity networks:

- The investigation report states **194 properties, 178 vacant (91.8%)**
- The MCP database returns **631 rows** for GEENA LLC's entity network, which includes properties linked through related entities, duplicate rows from multiple data sources (permits, violations, tax records), and properties where GEENA LLC appears in permit/contractor records but isn't the OPA-registered owner
- **330 distinct parcels** is a third answer — deduplicating by parcel number but still including network-linked properties

The "correct" answer depends on what "own" means: OPA-registered ownership (194), distinct parcels in the entity network (330), or all property touchpoints (631). None of these is wrong — they reflect different definitions.

---

## Round 1 — Prompt 1 (2026-03-07)

### Prompt

> How many properties does GEENA LLC own, and what percentage are vacant?

### Results

#### Philly MCP - GCC (Copilot Studio)

**Result: FAIL**

Error in chat window:

> Error Message: The request is resulting in too much data to handle, please evaluate the amount of data being returned by your actions. Error Code: OpenAIModelTokenLimit

The MCP tool successfully retrieved all 631 property rows as raw JSON, but the payload exceeded Copilot Studio's token limit. The data was in the MCP tool activity log but the model couldn't process it to generate a summary.

**Analysis:** This is a tool design issue, not a model issue. The MCP server returned every property row instead of a pre-aggregated count. For large entity networks, the tool needs to return summary statistics rather than full property lists. Same class of problem as returning all 50 cases in Use Case 1 — works for small datasets, breaks at scale.

#### Philly MCP - Com (Copilot Studio)

**Result: Pass**

> GEENA LLC owns 330 distinct Philadelphia parcels. Of those, 286 are coded by OPA as "Vacant..." (e.g., Vacant Land, Vacant Land - Non-Residential), which is **86.67%** of the portfolio.
>
> Notes: Counts are by distinct parcel number tied to GEENA LLC's master entity record. "Vacant" here reflects OPA use-category labels, not whether a building is unoccupied.

**Analysis:** Defensible answer. Deduped to distinct parcels (330 vs 631 raw rows), explained methodology, and clarified the definition of "vacant." The 86.67% vacancy rate is close to the report's 91.8% — the gap is explainable by the larger denominator (330 vs 194 parcels). Offered to calculate vacancy using L&I data instead if needed.

#### Philly SP/PDF - GCC (Copilot Studio)

**Result: Pass**

> GEENA LLC owns a total of **194 properties**, and **91.8%** of these properties are vacant.
> *1 reference: Entity_Investigation_Report.pdf*

**Analysis:** Matched the investigation report exactly (194 / 91.8%). Clean, cited answer. This is a prompt that favors document agents — the answer is stated explicitly in the report. No methodology explanation needed because it's a direct quote.

#### Investigative Agent (Philly Web SPA)

**Result: Partial**

> GEENA LLC owns **631 properties** in Philadelphia. Based on a scan of their portfolio, the majority of entries listed as "VACANT LAND" in the property category indicate vacant status. A conservative estimate (sampling the data) shows they have approximately **376** properties classified as vacant or vacant land.
>
> Percentage vacant: (376 / 631) x 100 = ~60%

**Analysis:** Used the raw row count (631) without deduplication, then estimated vacancy by "sampling" — suggesting it didn't systematically categorize all rows. The ~60% vacancy rate is significantly below both the report (91.8%) and COM MCP (86.67%). Called it a "conservative estimate" which is honest but not precise. Tools used: search_entities, get_entity_network, run_query.

#### Foundry Agent (Philly Web SPA)

**Result: Partial**

> GEENA LLC owns **631 properties** in Philadelphia. Of those, **286** are classified as "vacant" (by "category code description" such as "VACANT LAND" or "VACANT" types).
>
> Percentage vacant: 286 / 631 = **45.3%**

**Analysis:** Same 631 raw count as the Investigative Agent, but got 286 vacant (matching COM MCP's vacant count exactly). The 45.3% is mathematically correct for 286/631 but misleading because the denominator is inflated by duplicate rows. Interestingly, if you use 286/330 (COM MCP's denominator), you get 86.67% — matching COM MCP exactly. The vacant count is right; the total property count is wrong.

### Prompt 1 Comparison Matrix

| Dimension | MCP - GCC | MCP - Com | SP/PDF - GCC | Investigative Agent | Foundry Agent | Triage Agent |
|---|---|---|---|---|---|---|
| **Property count** | Error (token limit) | 330 (distinct parcels) | 194 (from report) | 631 (raw rows) | 631 (raw rows) | Not tested |
| **Vacancy %** | Error | 86.67% | 91.8% | ~60% (estimated) | 45.3% | Not tested |
| **Vacant count** | Error | 286 | 178 | ~376 (estimated) | 286 | Not tested |
| **Methodology stated** | N/A | Yes (distinct parcels, OPA labels) | No (direct quote from doc) | Partial ("sampling") | Yes (category code filter) | Not tested |
| **Ambiguity acknowledged** | N/A | Yes (offered alternative calc) | No | No | No | Not tested |
| **Source cited** | N/A | No | Yes (PDF reference) | No | No | Not tested |
| **Grade** | Fail | Pass | Pass | Partial | Partial | Not tested |

### Prompt 1 Analysis

#### The property count problem

Five agents, three different property counts (194, 330, 631), and no definitive ground truth. This is the first prompt and it already reveals a fundamental difference from Use Case 1: when the underlying data is real and complex, "correct" becomes a matter of definition.

#### Token limit is a tool design problem

GCC MCP's failure isn't about the model — it's about the MCP server returning 631 raw property rows as JSON instead of pre-aggregated statistics. This is solvable by adding a summary/count mode to the entity network tool. The data was retrieved correctly; it just overwhelmed Copilot Studio's context window.

#### Document agents excel when the answer is pre-computed

SP/PDF-GCC nailed it because the investigation report already contains "194 properties, 178 vacant (91.8%)." The agent just quoted the document. This is Prompt 1's design — it was expected to be a tie, but the MCP agents' struggle with deduplication and token limits gave documents the edge.

#### Pro-code agents (Investigative + Foundry) share the same flaw

Both used 631 as the denominator, meaning they didn't deduplicate the entity network results. They're querying the same MCP backend as COM MCP but processing the results differently. COM MCP (Copilot Studio + GPT-4.1) deduped to distinct parcels; the web SPA agents did not. This could be a prompt engineering or post-processing difference in the SPA's agent loop.

#### COM MCP showed the best analytical behavior

Despite not matching the report's numbers, COM MCP gave the most defensible answer: deduped by parcel, explained the methodology, defined what "vacant" means in context, and offered an alternative calculation. In a real investigation, this is the answer you'd want from an analyst.

---

## Round 1 — Prompt 2 (2026-03-07)

### Prompt

> What happened to 4763 Griscom Street between when GEENA LLC bought it and today? Have they done anything with the property?

### Ground Truth

Key facts from the database and investigation reports:

- GEENA LLC acquired via sheriff's deed on 2019-12-24 for $6,500
- Prior owner: Ricky H. Martinez (sheriff sale likely from unpaid taxes/liens)
- City demolished the building in June 2019 — before GEENA LLC purchased (contractor: Pedro Palmer Construction Inc.)
- Property classified as "VACANT LAND," no building since demolition
- 2025 assessed market value: $24,800
- 64 code violation cases, 45 failed inspections (mostly vacant lot maintenance — overgrown vegetation, debris, dumping)
- Cyclical pattern: fail inspection → notice of violation → clean up → pass → fall back into disrepair
- No building permits, development applications, business licenses, or rental licenses filed since acquisition
- No transfers or ownership changes since the sheriff sale
- Pattern consistent with speculative land-banking / absentee neglect

### Results

#### Philly MCP - GCC (Copilot Studio)

**Result: FAIL**

> Error Message: The request is resulting in too much data to handle, please evaluate the amount of data being returned by your actions. Error Code: OpenAIModelTokenLimit

Same token limit failure as Prompt 1. The entity network tool returns too much raw data for Copilot Studio to process.

#### Philly MCP - Com (Copilot Studio)

**Result: FAIL**

> Error Message: The request is resulting in too much data to handle, please evaluate the amount of data being returned by your actions. Error Code: OpenAIModelTokenLimit

**Analysis:** New failure — COM MCP passed Prompt 1 but fails here. The property-level query likely triggers network traversal that returns even more data than the entity-level query in P1. Both Copilot Studio MCP agents are now blocked by the same tool design issue: raw row dumps instead of pre-aggregated summaries.

#### Philly SP/PDF - GCC (Copilot Studio)

**Result: PASS**

> Since GEENA LLC acquired the property at 4763 Griscom Street in December 2019, the property has remained a vacant lot. No building permits, development applications, or license applications have been filed for this parcel since the acquisition. The property has accumulated numerous code enforcement investigations, primarily for lot maintenance issues such as overgrown vegetation, debris, and dumping. The violation pattern is cyclical, with the property failing inspections, receiving notices of violation, being cleaned to pass follow-up inspections, and then falling back into disrepair.
>
> The building that previously occupied the lot was demolished by the city before GEENA LLC acquired the property. The property is located in a mixed-use area in Frankford, Philadelphia, and GEENA LLC owns several other vacant properties in the same zip code, contributing to visual blight and safety concerns for residents.
>
> *1 reference: Property_Enforcement_File_4763_Griscom.pdf*

**Analysis:** Strong narrative answer. Hit every key point: vacant lot since acquisition, no permits or development, cyclical violation pattern, city demolished before purchase, broader context of GEENA's portfolio. Cited the source document. This is exactly the kind of prompt where document agents shine — the investigation report tells the story directly.

#### Foundry Agent (Philly Web SPA)

**Result: PASS**

> GEENA LLC acquired the property via sheriff's deed on 2019-12-24 for $6,500. The prior owner was Ricky H. Martinez, and the sheriff sale likely stemmed from unpaid taxes or liens.
>
> It is currently classified as "VACANT LAND," and has no building (demolished). The market value is $24,800 (2025 assessment). No building has been constructed or occupied since GEENA LLC purchased it.
>
> The lot is vacant because the City of Philadelphia demolished a structure on this parcel. The demolition was city-initiated (taxpayer-funded), not owner-initiated. Was completed in June 2019, before GEENA LLC purchased the lot. Contractor: Pedro Palmer Construction Inc.
>
> There is heavy code enforcement on this lot: 64 total code violation cases in the last decade. 45 failed inspections (most recent in June and July 2024). GEENA LLC has been cited repeatedly since taking possession.
>
> There are NO: Business licenses, Permit or zoning appeals, New construction or use permits, Signs of any development or sanctioned use since GEENA LLC acquired the parcel.
>
> Pattern: GEENA LLC exhibits a pattern of speculative holding or neglect on this property, paying virtually nothing at auction, letting maintenance lapse, and failing to put the land back into productive/revenue-generating use. This aligns with classic land-banking or absentee speculator behavior.

**Analysis:** The best answer across all agents. Specific dates, dollar amounts, violation counts, contractor name, and assessment value — all pulled from live SQL data. Also provided investigative analysis (land-banking pattern) without being asked. This is what a good analyst would produce. Tools used: search_entities, get_entity_network, run_query.

#### Investigative Agent (OpenAI Web SPA)

**Result: FAIL**

> There is no record of GEENA LLC ever owning 4763 Griscom Street (parcel 332326800, which is 4111 K Street). As of the most recent data (2024), the current owner is "Rosa Francisco Isaam."

**Analysis:** Catastrophic failure — looked up the **wrong parcel** entirely. Parcel 332326800 is 4111 K Street, not 4763 Griscom Street (which is parcel 232452100). The agent confidently reported on a completely different property. This is a new danger category: **tool misuse — geocoding/search error leading to wrong-entity analysis**. More dangerous than hallucination because the data is real, just for the wrong property. An investigator trusting this answer would draw conclusions about the wrong address.

#### Triage Agent (Semantic Kernel Web SPA)

**Result: FAIL**

> GEENA LLC purchased 4763 Griscom Street, and since their acquisition, the property has been monitored for activity and changes. Owner-related investigations show GEENA LLC as the current owner, but there is no evidence of a sale or transfer since their purchase. Violation and enforcement records indicate that there have been no recent code violations, demolitions, or L&I enforcement actions associated with the address since GEENA LLC took ownership. Overall, since GEENA LLC acquired 4763 Griscom Street, there is no substantial record of changes, developments, or compliance actions taken at the property.
>
> *Routing: Triage → OwnerAnalyst → ViolationAnalyst*

**Analysis:** Found the right owner but then claimed **"no recent code violations, demolitions, or L&I enforcement actions"** — flatly contradicted by 64 violations and 45 failed inspections in the database. This is **Danger Taxonomy #1: False negative — data exists but was not recognized**. The triage routing pattern (OwnerAnalyst → ViolationAnalyst) suggests the ViolationAnalyst sub-agent failed to retrieve or interpret the violation records. This is more dangerous than not answering at all — it gives false assurance that the property is clean.

### Prompt 2 Comparison Matrix

| Dimension | MCP - GCC | MCP - Com | SP/PDF - GCC | Foundry Agent | Investigative Agent | Triage Agent |
|---|---|---|---|---|---|---|
| **Answered the question** | No (error) | No (error) | Yes | Yes | No (wrong property) | Partially |
| **Acquisition details** | N/A | N/A | Dec 2019, no price | $6,500, sheriff's deed, 12/24/2019 | N/A (wrong property) | Yes (no details) |
| **Demolition mentioned** | N/A | N/A | Yes (city, pre-purchase) | Yes (June 2019, contractor named) | N/A | No |
| **Violation count** | N/A | N/A | "Numerous" (no count) | 64 cases, 45 failed | N/A (wrong property) | "None" (false negative) |
| **Development activity** | N/A | N/A | None (correct) | None (correct) | N/A | "None" (correct but incomplete) |
| **Source cited** | N/A | N/A | Yes (PDF) | No | No | No |
| **Dangerous error** | No | No | No | No | Yes (wrong parcel) | Yes (false negative) |
| **Grade** | Fail | Fail | Pass | Pass | Fail | Fail |

### Prompt 2 Analysis

#### Both MCP Copilot Studio agents are now blocked

COM MCP passed Prompt 1 but fails Prompt 2. The entity network tool's raw-dump design is a systemic problem — every prompt that touches GEENA LLC's property network will exceed Copilot Studio's token limit. This confirms the need for a summary/count mode before MCP agents can be competitive in Use Case 2.

#### Document agent holds steady

SP/PDF-GCC delivered another clean, cited answer. For prompts where the investigation report covers the topic, the document agent is reliable and consistent. The limitation will show on prompts 6 and 9 (citywide aggregates) where the documents can't help.

#### Foundry Agent is the standout

Two prompts in, the Foundry Agent has produced the most detailed, analytically rich answers. It's pulling specific data points from SQL (dates, dollars, violation counts, contractor names) and synthesizing them into investigative narratives. This is the "what good looks like" benchmark for the demo.

#### Two pro-code agents failed dangerously

The Investigative Agent and Triage Agent both failed, but in different and instructive ways:

- **Investigative Agent:** Tool misuse — searched for 4763 Griscom but resolved to the wrong parcel number. The data it returned was real and accurate, just for a completely different property. An investigator would draw conclusions about the wrong address.
- **Triage Agent:** False negative — found the right property and owner but reported zero violations where 64 exist. The team-of-agents routing (Triage → OwnerAnalyst → ViolationAnalyst) suggests a hand-off failure between sub-agents.

Both failures are more dangerous than "I don't know" because they present confidently wrong information. This reinforces the danger taxonomy from Use Case 1: **false negatives and wrong-entity analysis are the most dangerous failure modes for investigative AI**.

#### New danger category: wrong-entity analysis

The Investigative Agent's parcel lookup error introduces a failure mode not seen in Use Case 1: the agent queries a real database, gets real data, but for the **wrong entity**. Everything in the response is factually accurate — just not about the property that was asked about. This is arguably worse than hallucination because the data passes a "does this look real?" sniff test.

---

## Round 1 — Prompt 3 (2026-03-07)

### Prompt

> What was the assessment value of 4763 Griscom Street in 2017, and what is it now? What happened?

### Ground Truth

From the investigation report (Property_Enforcement_File_4763_Griscom.pdf):

- 2017: $56,900 ($42,390 building + $14,510 land)
- 2025: $24,800 (all land — property is now a vacant lot)
- The building was demolished by the city in 2019, causing the value to drop from $56,900 → $37,200 (2019) → $17,500 (2020)
- The current $24,800 reflects land value appreciation in the surrounding area, not any improvement to the property
- The correct parcel number for 4763 Griscom Street is 232452100

### Results

#### Philly MCP - GCC (Copilot Studio)

**Result: FAIL**

> The assessment value of 4763 Griscom Street in 2017 was $87,800. The current assessment value for 2025 is $206,800.
>
> Address: 1423 E Lycoming St. Owner: Luis A Compres. Market Value: $206,800.

**Analysis:** Returned data for a **completely different property** — 1423 E Lycoming St, owned by Luis A Compres. The assessment values ($87,800 → $206,800) and the "no demolitions recorded" statement are all real data for the wrong address. This is the same wrong-entity failure seen with the Investigative Agent in Prompt 2, but now it's a Copilot Studio agent. The address-to-parcel resolution in the MCP tools is unreliable.

#### Philly MCP - Com (Copilot Studio)

**Result: FAIL**

> The address-based lookup failed because the system requires the parcel number, and the column names in the database differ from what I tried... I've identified the correct column for addresses: address_std.
>
> Error Code: GenAIToolPlannerRateLimitReached

**Analysis:** Made progress — identified that `address_std` is the correct column name — but exhausted the Copilot Studio rate limit before completing the query. This is a two-stage failure: first the MCP tool couldn't resolve the address, then the agent's self-correction loop hit a platform ceiling. At least COM MCP recognized the problem and tried to fix it, unlike GCC MCP which confidently returned the wrong property.

#### Philly SP/PDF - GCC (Copilot Studio)

**Result: PASS**

> The assessment value of 4763 Griscom Street in 2017 was $56,900, with $42,390 attributed to the building and $14,510 to the land. The current assessment value (2025) is $24,800, entirely attributed to the land as the property is now a vacant lot.
>
> The property maintained a steady value of $56,900 through 2018 while the structure was standing. In 2019, the building was demolished by the city, leading to a significant drop in the assessment value to $37,200. By 2020, the value further declined to $17,500 as the property was now vacant land. The current assessment value of $24,800 reflects a modest recovery driven by land value appreciation in the surrounding area, not any improvement to the property.
>
> *1 reference: Property_Enforcement_File_4763_Griscom.pdf*

**Analysis:** Perfect answer. Year-by-year assessment trajectory, building vs. land breakdown, causal explanation (demolition), and the insight that current recovery is land appreciation, not property improvement. Cited the source. This is what a good analyst brief looks like.

#### Foundry Agent (Philly Web SPA)

**Result: FAIL**

> There is no assessment history currently returned for 4763 Griscom Street (parcel 882474300), so I can't provide its assessed value in 2017 or today.

**Analysis:** Resolved to the **wrong parcel number** (882474300 instead of 232452100). In Prompt 2, the Foundry Agent correctly used parcel 232452100 — but here it gets a different parcel for the same address. The address resolution is non-deterministic. At least the agent was honest about returning no data rather than fabricating an answer.

#### Investigative Agent (OpenAI Web SPA)

**Result: FAIL**

> The assessment history for 4763 Griscom Street (parcel 232068200) is as follows:
> 2017 market value: $64,500. Current (2025) market value: $102,300.
> A significant increase occurred for tax year 2023, with a much steeper jump now set for 2025 — over 55% higher than in 2017.

**Analysis:** Wrong parcel again (232068200 instead of 232452100 — and different from the wrong parcel in Prompt 2). The values ($64,500 → $102,300 with building components) describe a property that still has a building, not one where the building was demolished. The "citywide reassessment trends" explanation is plausible for the wrong property but completely misses the demolition that is the actual story. Confidently wrong.

#### Triage Agent (Semantic Kernel Web SPA)

**Result: FAIL**

> In 2017, the assessment value (market value) of 4763 Griscom Street was $48,600. Currently (2024), the market value is $70,200. In 2025, it is projected to rise to $101,900.
>
> Since 2022, the assessment split switched from all taxable to mostly exempt, indicating a change in property status, likely to nonprofit, tax-exempt, or government use.

**Analysis:** Yet another wrong parcel (different numbers from every other agent). The tax-exempt narrative is fabricated from a different property's data — GEENA LLC is not a tax-exempt entity, and the property was demolished, not repurposed. The "nonprofit or government use" interpretation is completely wrong and potentially misleading for an investigator. Routing: Triage → AreaAnalyst.

### Prompt 3 Comparison Matrix

| Dimension | MCP - GCC | MCP - Com | SP/PDF - GCC | Foundry Agent | Investigative Agent | Triage Agent |
|---|---|---|---|---|---|---|
| **2017 value** | $87,800 (wrong property) | N/A (rate limited) | $56,900 (correct) | N/A (no data) | $64,500 (wrong parcel) | $48,600 (wrong parcel) |
| **2025 value** | $206,800 (wrong property) | N/A | $24,800 (correct) | N/A | $102,300 (wrong parcel) | $101,900 (wrong parcel) |
| **Demolition mentioned** | No | N/A | Yes (city, 2019) | No | No | No |
| **Correct parcel** | No (returned 1423 E Lycoming) | N/A | N/A (used PDF) | No (882474300) | No (232068200) | No (unknown) |
| **Dangerous error** | Yes (wrong property, confident) | No (admitted failure) | No | No (admitted no data) | Yes (wrong parcel, confident) | Yes (fabricated tax-exempt narrative) |
| **Grade** | Fail | Fail | Pass | Fail | Fail | Fail |

### Prompt 3 Analysis

#### Address resolution is a systemic MCP failure

Every SQL-backed agent either resolved 4763 Griscom Street to a different wrong parcel number or couldn't resolve it at all. Across Prompts 2 and 3, the agents have produced at least 4 different parcel numbers for the same address:

| Agent | Prompt 2 Parcel | Prompt 3 Parcel | Correct (232452100) |
|---|---|---|---|
| Foundry Agent | 232452100 | 882474300 | P2 only |
| Investigative Agent | 332326800 | 232068200 | Never |
| GCC MCP | N/A (token error) | Wrong (1423 E Lycoming) | Never |

The address-to-parcel mapping is non-deterministic — the same agent gets different parcels for the same address across prompts. This is a fundamental tool reliability issue, not a model issue.

#### Document agent is 3 for 3

SP/PDF-GCC has passed every prompt cleanly. When the investigation report covers the topic, the document agent delivers accurate, cited, well-structured answers. The pattern is clear: for property-specific narrative questions about investigated properties, documents win.

#### Honest failure is better than confident wrong answers

The Foundry Agent and COM MCP both failed but admitted it — "no assessment history returned" and "the lookup failed." The GCC MCP, Investigative Agent, and Triage Agent all returned confident answers about the wrong property. In an investigative context, an honest "I couldn't find that" is infinitely safer than detailed analysis of the wrong address.

#### The MCP tool needs an address resolution layer

The root cause is clear: the MCP tools don't have a reliable address-to-parcel resolver. The `get_property_profile` tool apparently accepts addresses but maps them inconsistently. A dedicated address normalization and geocoding step — or a fuzzy-match lookup against `address_std` — would fix this class of failures across all MCP agents.

---

## Round 1 — Prompt 4 (2026-03-07)

### Prompt

> Trace the complete ownership history of 4763 Griscom Street. How many times was it sold at sheriff sale?

### Ground Truth

From the investigation report (Transfer_Chain_Analysis_4763_Griscom.pdf), 6 owners, 2 sheriff sales:

1. 1999-11-10: Ofides/Shehinsky → Michael L. Bryan — $10,650 (deed)
2. 2004-03-23: Bryan → Hillard J. Habeeb — $146,000 (deed)
3. 2013-01-08: Habeeb → Henry M. DeJesus — $13,200 (**sheriff sale #1**)
4. 2014-07-10: DeJesus → Hao Kim Luong — $20,000 (deed)
5. 2014-08-05: Luong → Ricky H. Martinez — $21,500 (deed)
6. 2019-12-24: Martinez → GEENA LLC — $6,500 (**sheriff sale #2**)

### Results

#### Philly MCP - GCC (Copilot Studio)

**Result: FAIL**

> Assignment of Mortgage: Oct 22, 2008 — Mortgage Electronic Registration Systems Inc → U S Bank National Association TR
> Satisfaction: Aug 31, 2005 — PNC Mortgage Corp of America; Washington Mutual Bank FA → Vo Duc Minh
> Mortgage: Aug 29, 2005 — Vo Duc Minh → Fremont Investment & Loan
>
> The search for sheriff sale records did not return any results. Therefore, it appears that there are no records of 4763 Griscom Street being sold at a sheriff sale.

**Analysis:** Wrong property entirely. The names (Vo Duc Minh, Fremont Investment & Loan, US Bank, PNC Mortgage) don't appear anywhere in the known chain. Only returned mortgage-related documents, not deed transfers. Confidently stated no sheriff sales — there were 2.

#### Philly MCP - Com (Copilot Studio)

**Result: PASS**

> Here's the ownership chain for 4763 Griscom Street (parcel 232452100):
>
> 1. 1999-11-10 DEED: OFIDES George; OFIDES Vasiliky; SHEHINSKY Russell → BRYAN MICHAEL L for $10,650
> 2. 2004-03-23 DEED: BRYAN MICHAEL L → HABEEB HILLARD J for $146,000
> 3. 2013-01-08 DEED SHERIFF: HABEEB HILLARD J → DEJESUS HENRY M for $13,200 [Sheriff sale]
> 4. 2014-07-10 DEED: DEJESUS HENRY M → LUONG HAO KIM for $20,000
> 5. 2014-08-05 DEED: LUONG HAO KIM → MARTINEZ RICKY H for $21,500
> 6. 2019-12-24 SHERIFF'S DEED: MARTINEZ RICKY H → GEENA LLC for $6,500 [Sheriff sale]
>
> Answer: It was sold at sheriff sale 2 times (in 2013 and 2019).

**Analysis:** Perfect. Correct parcel (232452100), complete 6-transfer chain with dates, prices, and deed types. Correctly identified both sheriff sales. Clean presentation — omitted mortgage assignments to focus on ownership changes. This is COM MCP's first success since Prompt 1 and shows that when the address resolves correctly, the MCP agent produces excellent results.

#### Philly SP/PDF - GCC (Copilot Studio)

**Result: PASS**

> Complete ownership history with all 6 transfers, 2 sheriff sales identified and dated. Added characterization: "Quick Flip to Luong," "Second Quick Flip to Martinez."
>
> *1 reference: Transfer_Chain_Analysis_4763_Griscom.pdf*

**Analysis:** Matches COM MCP's chain exactly, with added investigative color ("Quick Flip" labels). Four consecutive passes for the document agent. The investigation report was designed to tell this story, so the document agent delivers it cleanly.

#### Foundry Agent (Philly Web SPA)

**Result: FAIL**

> There was an internal error with address-to-parcel mapping and transfer lookups. To proceed accurately, I need the correct OPA parcel number for 4763 Griscom Street to pull the ownership and sheriff sale history directly.
>
> Do you have the parcel number?

**Analysis:** Address resolution failed again (different error mode than P3 where it used parcel 882474300). Honest about the failure and asked for help. The Foundry Agent has now failed P3 and P4 on address resolution after succeeding in P2 — confirming the non-deterministic nature of the problem.

#### Investigative Agent (OpenAI Web SPA)

**Result: FAIL**

> There is no ownership or transfer history available in the database for 4763 Griscom Street (parcel number 882500350).

**Analysis:** Wrong parcel (882500350 — the 4th different wrong parcel this agent has produced across 3 prompts). No data found. At least admitted the gap rather than fabricating a chain.

#### Triage Agent (Semantic Kernel Web SPA)

**Result: FAIL**

> Property transfer records for parcel 652507900 (4763 Griscom Street) show no real estate transactions, including sheriff sales. Attempts to retrieve a detailed property profile resulted in a 404 error.
>
> Conclusion: There is no evidence that 4763 Griscom Street has ever been sold at a sheriff sale, nor any transfer history available in Philadelphia's property record systems.

**Analysis:** Wrong parcel (652507900), 404 on profile lookup, then confidently concluded "no evidence" of any sheriff sales. This is a dangerous false negative — there were 2 sheriff sales with full documentation. The confident tone ("nor any transfer history available in Philadelphia's property record systems") implies the data doesn't exist anywhere, when in fact the agent simply looked up the wrong property. Routing: Triage → OwnerAnalyst.

### Prompt 4 Comparison Matrix

| Dimension | MCP - GCC | MCP - Com | SP/PDF - GCC | Foundry Agent | Investigative Agent | Triage Agent |
|---|---|---|---|---|---|---|
| **Correct parcel** | No (wrong property) | Yes (232452100) | N/A (used PDF) | No (error) | No (882500350) | No (652507900) |
| **Complete chain** | No (3 mortgage docs) | Yes (6 transfers) | Yes (6 transfers) | No | No | No |
| **Sheriff sale count** | 0 (wrong) | 2 (correct) | 2 (correct) | N/A | N/A | 0 (wrong) |
| **Honest about failure** | No | N/A (succeeded) | N/A (succeeded) | Yes | Yes | No |
| **Dangerous error** | Yes (wrong property, no sheriff sales) | No | No | No | No | Yes (confident false negative) |
| **Grade** | Fail | Pass | Pass | Fail | Fail | Fail |

### Prompt 4 Analysis

#### COM MCP breaks through

COM MCP resolved the correct parcel (232452100) for the first time since... ever. In P1 it used entity search (not address resolution), in P2 it hit token limits, in P3 it hit rate limits. Here it found the parcel and produced a flawless ownership chain. This proves the MCP approach works when address resolution succeeds — the problem is getting it to succeed consistently.

#### Address resolution scorecard (P2-P4)

| Agent | P2 | P3 | P4 | Correct parcel (232452100) |
|---|---|---|---|---|
| COM MCP | Token error | Rate limited | **232452100** | 1 of 3 |
| GCC MCP | Token error | Wrong (1423 E Lycoming) | Wrong (mortgage docs) | 0 of 3 |
| Foundry | **232452100** | 882474300 | Error | 1 of 3 |
| Investigative | 332326800 | 232068200 | 882500350 | 0 of 3 |
| Triage | Correct owner | Unknown | 652507900 | 0 of 3 |

Five agents, 15 attempts at address resolution, **2 successes**. The tool needs fixing.

#### Document agent: 4 for 4

SP/PDF-GCC continues to deliver clean, cited answers for every property-specific question about the investigated properties. The pattern is unambiguous: when the question is about a property covered by the investigation reports, the document agent wins.

---

## Round 1 — Prompt 5 (2026-03-07)

### Prompt

> The transfer records show 4763 Griscom was sold for $146,000 in 2004. What was the fair market value at the time of that sale?

### Ground Truth

From the investigation report (Transfer_Chain_Analysis_4763_Griscom.pdf):

- Fair market value at time of the 2004 sale: **$53,155**
- The $146,000 purchase price was **275% of fair market value** — a key red flag in the investigation
- The FMV is embedded in the **deed/transfer record itself** (not in the assessment history table, which only goes back to 2015)

### Results

#### Philly MCP - GCC (Copilot Studio)

**Result: FAIL**

> The fair market value of the property located at 4763 Griscom in 2004 is not directly available in the provided assessment data. The earliest available assessment data is from 2015, with a market value of $111,000.

**Analysis:** Looked in the assessment history table (which starts at 2015) instead of the deed record where the FMV is embedded. The 2015 value of $111,000 doesn't match the real property's value (~$56,900 per the investigation report), confirming this is yet another wrong property. Acknowledged the gap honestly, but searched the wrong data source for the wrong property.

#### Philly MCP - Com (Copilot Studio)

**Result: PASS**

> $53,155.20.
>
> Details: The deed for 4763 Griscom St recorded on 2004-03-25 shows total consideration of $146,000 with a fair market value of $53,155.20 (OPA account 232452100, record_id 5089276711393154).

**Analysis:** Found the answer in the right place — the deed record, not the assessment table. Correct parcel (232452100 again, consistent with P4), specific record ID cited. Clean, precise answer. COM MCP is now 2 for 2 since it started resolving the correct parcel.

#### Philly SP/PDF - GCC (Copilot Studio)

**Result: PASS**

> The fair market value of the property at 4763 Griscom Street in 2004 was recorded as $53,155.
>
> *1 reference: Transfer_Chain_Analysis_4763_Griscom.pdf*

**Analysis:** Five for five. Direct extraction from the investigation report, cited.

#### Foundry Agent (Philly Web SPA)

**Result: FAIL**

> Philadelphia's open property data does not provide public record of assessment values prior to 2015. The earliest available assessment for 4763 Griscom St (parcel 882162200) is in 2015, with a fair market value of $420,600.

**Analysis:** Two problems: wrong parcel (882162200 — yet another new one) and wrong data source (assessment table instead of deed record). The $420,600 figure is for a completely different property. The AVI historical context is reasonable but doesn't answer the question. The FMV was in the transfer record all along.

#### Investigative Agent (OpenAI Web SPA)

**Result: FAIL**

> The City of Philadelphia's property assessment records for 4763 Griscom Street do not provide a fair market value specifically for 2004. The oldest available market value assessment on file is from 2015, which is $116,900.

**Analysis:** Same wrong approach (assessment table instead of deed record) and likely wrong property ($116,900 doesn't match the real 2015 value). The AVI context is informed, but the agent never checked the transfer record where the FMV lives.

#### Triage Agent (Semantic Kernel Web SPA)

**Result: FAIL**

> Philadelphia assessment records for 4763 Griscom Street do not show fair market values prior to 2015. For context, the market value in 2015 was $474,500.

**Analysis:** Wrong property ($474,500 is wildly different from the real ~$56,900) and wrong data source. Routing: Triage → AreaAnalyst — the triage router sent this to an area-level analyst when it needed a transfer-level lookup.

### Prompt 5 Comparison Matrix

| Dimension | MCP - GCC | MCP - Com | SP/PDF - GCC | Foundry Agent | Investigative Agent | Triage Agent |
|---|---|---|---|---|---|---|
| **FMV stated** | "Not available" | $53,155.20 (correct) | $53,155 (correct) | "Not available" | "Not available" | "Not available" |
| **Data source used** | Assessment table | Deed record | PDF | Assessment table | Assessment table | Assessment table |
| **Correct parcel** | No ($111K in 2015) | Yes (232452100) | N/A (used PDF) | No (882162200) | No ($116.9K in 2015) | No ($474.5K in 2015) |
| **2015 value reported** | $111,000 | N/A | N/A | $420,600 | $116,900 | $474,500 |
| **Grade** | Fail | Pass | Pass | Fail | Fail | Fail |

### Prompt 5 Analysis

#### The FMV is in the deed, not the assessment table

Four agents searched the assessment history table (which starts at 2015) and concluded the 2004 FMV doesn't exist. COM MCP found it in the **deed/transfer record** where it's stored as a field on the transaction. This is a tool usage distinction, not a data availability problem — the information is in the database, but only one agent looked in the right table.

#### Four wrong properties, four different 2015 values

The agents that used assessment data reported four completely different 2015 values, confirming each resolved to a different wrong parcel:

| Agent | 2015 Market Value | Real Value (~$56,900) |
|---|---|---|
| GCC MCP | $111,000 | Wrong property |
| Foundry | $420,600 | Wrong property |
| Investigative | $116,900 | Wrong property |
| Triage | $474,500 | Wrong property |

#### COM MCP has found its groove

Since resolving the correct parcel in P4, COM MCP has now passed two consecutive prompts with precise, well-sourced answers. The pattern: once address resolution succeeds, COM MCP's tool selection and data interpretation are strong. The bottleneck is entirely in that first address-to-parcel step.

#### Document agent: 5 for 5

SP/PDF-GCC continues its perfect streak. This was expected to be a "Document advantage" prompt and it delivered as designed.

---

## Round 1 — Prompt 6 (2026-03-07)

### Prompt

> Who are the top 5 private property owners in Philadelphia by code violation count? Exclude government entities.

### Ground Truth

No ground truth from investigation reports — this requires querying 584K properties across the full database. Cross-agent consensus (COM MCP, Foundry, Investigative all agree on top 2; COM MCP and Investigative agree on #3):

1. GEENA LLC — 1,411 violations (194 properties, 178 vacant, 40 demolitions)
2. S3 ENTERPRISES LLC — 1,009 violations (77 properties, 45 vacant)
3. ULATOWSKI WALTER — 915 violations (140 properties)
4. CORESTATES GROUP LLC — 773 violations (99 properties)
5. CHOICE RENTALS LLC — 763 violations (56 properties)

This prompt was designed as **"MCP dominates"** — the investigation reports only cover GEENA LLC and two properties; answering requires citywide SQL aggregation.

### Results

#### Philly MCP - GCC (Copilot Studio)

**Result: PARTIAL**

> 1. GEENA LLC — 1,411 violations, 194 properties, 178 vacant, 40 demolitions
> 2. PHILADELPHIA REDEVELOPMENT — 1,073 violations, 80 properties

**Analysis:** Only returned 2 entities instead of 5, and one of them (Philadelphia Redevelopment) is a government entity — exactly what the prompt said to exclude. Got GEENA LLC right with data matching other agents. The truncated list and failed government filter both hurt.

#### Philly MCP - Com (Copilot Studio)

**Result: PASS**

> Top 5 private property owners in Philadelphia by total code violations (excluding government entities):
>
> 1. GEENA LLC — 1,411 violations (194 properties; 178 listed vacant; 40 demolitions)
> 2. S3 ENTERPRISES LLC — 1,009 violations (77 properties; 45 listed vacant)
> 3. ULATOWSKI WALTER — 915 violations (140 properties)
> 4. CORESTATES GROUP LLC — 773 violations (99 properties)
> 5. CHOICE RENTALS LLC — 763 violations (56 properties)
>
> Source: Citywide violation aggregation by owner; government owners excluded from the ranking.

**Analysis:** Complete top 5 with government entities properly excluded. Includes ULATOWSKI WALTER at #3, confirming the Investigative Agent's data and filling the gap in the Foundry Agent's list (which skipped individuals). This is the most complete answer — 5 entities, mixed LLCs and individuals, with sourcing context. COM MCP continues its strong streak since resolving address issues.

#### Philly SP/PDF - GCC (Copilot Studio)

**Result: PARTIAL**

> The retrieval results do not provide a comprehensive list of the top private property owners in Philadelphia by code violation count. However, based on the available information, GEENA LLC is identified as a significant private property owner with a substantial number of code violations. GEENA LLC has accumulated 64 code enforcement investigations for the property at 4763 Griscom Street alone, with a 70.3% failure rate in inspections.
>
> *2 references: Property_Enforcement_File_4763_Griscom.pdf, Entity_Investigation_Report.pdf*

**Analysis:** Correctly acknowledged it can't answer a citywide question from 2 property reports. Provided what it could (GEENA LLC details) and cited sources. This is an honest, well-scoped answer — the document agent knows its limits. Expected behavior for this "MCP dominates" prompt.

#### Foundry Agent (Philly Web SPA)

**Result: PASS**

> 1. GEENA LLC — 1,411 violations, 194 properties, 178 vacant, 40 demolitions
> 2. S3 ENTERPRISES LLC — 1,009 violations, 77 properties, 45 vacant, 2 demolitions
> 3. CORESTATES GROUP LLC — 773 violations, 99 properties, 3 vacant, 1 demolition
> 4. CHOICE RENTALS LLC — 763 violations, 56 properties, 0 vacant
> 5. GILLER REALTY LLC — 702 violations, 134 properties, 6 vacant, 4 demolitions

**Analysis:** Complete top 5 with detailed stats for each. All appear to be private entities (LLCs). Offered to dig deeper into any of them. Clean, structured, actionable answer. The Foundry Agent excels at aggregate queries that don't require address resolution.

#### Investigative Agent (OpenAI Web SPA)

**Result: PARTIAL**

> 1. GEENA LLC — 1,411 violations, 194 properties, 178 vacant, 40 demolitions
> 2. S3 ENTERPRISES LLC — 1,009 violations, 77 properties, 45 vacant, 2 demolitions
> 3. ULATOWSKI WALTER — 915 violations, 140 properties, 0 vacant, 0 demolitions
>
> The other entities in the top 10 are government-affiliated.

**Analysis:** Only listed 3 instead of 5. GEENA and S3 match the Foundry Agent. ULATOWSKI WALTER at 915 violations would rank #3 (above Foundry's CORESTATES at 773) — either Foundry filtered out individuals or used a different entity classification. The agent stopped at 3 and noted the rest were government, but didn't filter deeper to find #4 and #5 private owners.

#### Triage Agent (Semantic Kernel Web SPA)

**Result: FAIL**

> The top 5 property owners by code violation count are all government entities. Since you requested private owners, none of the top 5 overall are eligible. Please clarify if you want to see the top private LLCs or individuals instead.

**Analysis:** The prompt explicitly said "Exclude government entities" — the agent should have filtered them out, not asked for permission. This is a comprehension failure: the instruction was clear, and the agent punted instead of executing. Routing: Triage → ViolationAnalyst. The ViolationAnalyst sub-agent apparently can't apply a filter that was stated in the original prompt.

### Prompt 6 Comparison Matrix

| Dimension | MCP - GCC | MCP - Com | SP/PDF - GCC | Foundry Agent | Investigative Agent | Triage Agent |
|---|---|---|---|---|---|---|
| **Entities listed** | 2 | 5 (complete) | 1 (GEENA only) | 5 (complete) | 3 | 0 |
| **Gov excluded** | No (included Phila Redevelopment) | Yes | N/A | Yes | Yes | No (asked to clarify) |
| **GEENA LLC data** | Correct | Correct | Partial (1 property) | Correct | Correct | N/A |
| **Includes individuals** | N/A | Yes (ULATOWSKI) | N/A | No (LLCs only) | Yes (ULATOWSKI) | N/A |
| **Acknowledged limits** | No | N/A | Yes | N/A | Partial | No |
| **Grade** | Partial | Pass | Partial | Pass | Partial | Fail |

### Prompt 6 Analysis

#### MCP dominance confirmed — two agents delivered

This was designed as the prompt where SQL agents should crush document agents. COM MCP and the Foundry Agent both delivered complete top-5 lists. COM MCP's list is arguably the most complete, including both LLCs and individuals (ULATOWSKI WALTER at #3). GCC MCP stumbled with only 2 results and a government entity included.

#### No address resolution needed = no address resolution failures

Prompt 6 doesn't reference a specific street address. It's a pure aggregate query. The Foundry Agent — which failed P3, P4, and P5 on address resolution — produced the best answer here. This confirms the pattern: the Foundry Agent's SQL skills are strong; its address resolver is broken.

#### Document agent's honest limitation

SP/PDF-GCC gave the most professionally appropriate answer for an agent that knows its scope: "I can tell you about GEENA LLC from my reports, but I can't rank all 584K property owners." In a real investigative workflow, this is the right response — don't guess, state what you know and what you don't.

#### ULATOWSKI WALTER: the real #3

COM MCP and the Investigative Agent both found ULATOWSKI WALTER at 915 violations (140 properties), ranking #3. The Foundry Agent skipped this individual — likely filtering to LLCs only. COM MCP's list (which includes both LLCs and individuals) is the most accurate answer to the prompt, which asked about "property owners," not "LLCs."

---

## Round 1 — Prompt 7 (2026-03-07)

### Prompt

> What financial institutions were involved in the mortgage history of 2400 Bryn Mawr Avenue, and what happened to them?

### Ground Truth

From the investigation report (Ownership_Financial_History_2400_Bryn_Mawr.pdf):

- **Washington Mutual Bank (WaMu)** — original mortgage lender (2002); failed 2008, seized by FDIC, acquired by JPMorgan Chase
- **Financial Freedom Senior Funding / IndyMac Bank** — reverse mortgage (2006); IndyMac failed July 2008, seized by FDIC
- **MERS** — mortgage registry/nominee; remains active
- **Financial Freedom Acquisition LLC** — successor entity post-IndyMac; wound down when CIT exited reverse mortgages 2018
- **OneWest Bank** — formed from IndyMac remnants; merged with CIT Group 2015, then CIT merged into First Citizens Bank 2022
- **HUD** — HECM (reverse mortgage) guarantee
- **Walter P. Lomax Jr.** — private second mortgage lender
- Property foreclosed 2016; sheriff sale to GEENA LLC for $230,000
- Correct parcel: 521273000

This prompt was designed as **"Document dominates"** — the institutional failure narrative and what happened to the banks requires contextual knowledge beyond raw SQL transfer records.

### Results

#### Philly MCP - GCC (Copilot Studio)

**Result: FAIL**

> Asian Bank: Involved in a mortgage on April 17, 2013. Satisfied October 23, 2014.
> Vist Bank: Involved in a mortgage on May 7, 2018.
> Tompkins Community Bank: Involved in a satisfaction of mortgage on August 7, 2024.

**Analysis:** Wrong property entirely. None of these institutions (Asian Bank, Vist Bank, Tompkins Community Bank) appear in the actual mortgage chain for 2400 Bryn Mawr. The address resolution failed again, returning transfer data for a completely different parcel.

#### Philly MCP - Com (Copilot Studio)

**Result: PASS**

> Complete mortgage trail for 2400 Bryn Mawr Ave (parcel 521273000):
>
> - **Washington Mutual Bank** — mortgage 2002-04-18; released 2006-08-01. Failed 2008, acquired by JPMorgan Chase.
> - **Financial Freedom Senior Funding / IndyMac Bank** — reverse mortgage 2006-07-17. IndyMac failed 2008; assets acquired by OneWest Bank 2009.
> - **MERS** — appeared on assignments. Remains active.
> - **Financial Freedom Acquisition LLC** — took assignment 2009-10-19. Brand discontinued when CIT exited reverse mortgages 2018.
> - **OneWest Bank** — received assignment 2015-01-29. Merged with CIT Group 2015; CIT merged into First Citizens Bank 2022.
> - **HUD** — HECM second note 2006-07-17. Continues to operate.
> - **Walter P. Lomax Jr.** — private mortgages 2006 and 2009.
> - Sheriff's Deed to GEENA LLC for $230,000 on 2016-06-16.

**Analysis:** Outstanding. Correct parcel, complete institutional chain with document IDs, and accurate narratives of what happened to each institution — including the WaMu → JPMorgan, IndyMac → OneWest → CIT → First Citizens chain. This was supposed to be a "Document dominates" prompt, but COM MCP matched the document agent by combining SQL transfer records with general knowledge about the 2008 financial crisis. Four straight passes for COM MCP.

#### Philly SP/PDF - GCC (Copilot Studio)

**Result: PASS**

> Complete list of 8 institutions with roles and fates:
> - WaMu: original mortgage, failed 2008, seized by FDIC
> - Financial Freedom / IndyMac: reverse mortgage, failed July 2008
> - HUD: HECM guarantee, involved as foreclosure party 2016
> - Walter P. Lomax Jr.: private lender
> - Financial Freedom Acquisition LLC: reconstituted from IndyMac
> - MERS: named in nationwide litigation
> - OneWest Bank: formed from IndyMac remnants, acquired by CIT Group 2015
>
> Summary: Anderson family → WaMu mortgage 2002 → reverse mortgage 2006 → foreclosure 2016 → sheriff sale to GEENA LLC.
>
> *1 reference: Ownership_Financial_History_2400_Bryn_Mawr.pdf*

**Analysis:** Six for six. Clean narrative with institutional fates, family context, and the foreclosure arc. Cited the source document. This is exactly the kind of prompt the investigation reports were written to answer.

#### Foundry Agent (Philly Web SPA)

**Result: FAIL**

> The mortgage history for 4808 Conshohocken Ave (parcel 521190000, address commonly associated with 2400 Bryn Mawr Ave):
>
> 1. Pennsylvania Housing Finance Agency (PHFA) — mortgage 2005, satisfied 2007
> 2. JPMorgan Chase / Margaretten & Company — satisfaction 2023
>
> No foreclosure or sheriff's sale in the property record.

**Analysis:** Wrong parcel (521190000 instead of 521273000). The institutions (PHFA, Margaretten & Company) and the "no foreclosure" conclusion are all real data for a different property. The agent tried to link 4808 Conshohocken Ave to 2400 Bryn Mawr — a creative but wrong address mapping. The actual 2400 Bryn Mawr had a foreclosure and sheriff sale.

#### Investigative Agent (OpenAI Web SPA)

**Result: FAIL**

> Parcel 521204600 (5100 Overbrook Avenue):
>
> ABN AMRO, Citifinancial, Ditech/GMAC, New Century Mortgage, Lend America/MERS, Ginnie Mae, FNF Servicing, Selene Finance. Sheriff sale to Penn Property Investor LLC 2020-02-25.

**Analysis:** Wrong property (5100 Overbrook Avenue). None of the institutions match the actual 2400 Bryn Mawr chain. The narrative about subprime lender failures (New Century bankruptcy 2007, Lend America shutdown 2009) is historically accurate and impressively detailed — but it's about the wrong property. A compelling, well-sourced answer for the wrong address. Same wrong-entity danger as P2.

#### Triage Agent (Semantic Kernel Web SPA)

**Result: FAIL**

> The top 5 private property owners in Philadelphia by code violation count are all government entities. No private non-governmental owners are included in the top 5.

**Analysis:** Answered **Prompt 6**, not Prompt 7. The response is identical to the Triage Agent's P6 failure — asking for clarification about government entity filtering instead of addressing 2400 Bryn Mawr's mortgage history. Either the agent received the wrong prompt, or the triage router misclassified the question. Either way, completely wrong.

### Prompt 7 Comparison Matrix

| Dimension | MCP - GCC | MCP - Com | SP/PDF - GCC | Foundry Agent | Investigative Agent | Triage Agent |
|---|---|---|---|---|---|---|
| **Correct parcel** | No | Yes (521273000) | N/A (used PDF) | No (521190000) | No (521204600) | N/A (wrong prompt) |
| **WaMu identified** | No | Yes + fate | Yes + fate | No | No | No |
| **IndyMac/Financial Freedom** | No | Yes + full chain | Yes + fate | No | No | No |
| **Foreclosure noted** | No | Yes (GEENA LLC, $230K) | Yes (GEENA LLC) | No ("no foreclosure") | Yes (wrong property) | No |
| **Institutional fates explained** | No | Yes (detailed) | Yes (detailed) | N/A | Yes (wrong property) | No |
| **Grade** | Fail | Pass | Pass | Fail | Fail | Fail |

### Prompt 7 Analysis

#### COM MCP defies the expected outcome

This prompt was designed as "Document dominates" — the assumption was that institutional failure narratives (WaMu collapse, IndyMac seizure, OneWest → CIT → First Citizens) couldn't be answered from SQL transfer records alone. COM MCP proved this wrong by combining the raw transfer chain (from SQL, with document IDs and dates) with general knowledge about what happened to each institution. The result matched the document agent's quality.

#### The address resolution gap widens

GCC MCP, Foundry Agent, and Investigative Agent all resolved 2400 Bryn Mawr to different wrong parcels. The Investigative Agent's answer is particularly instructive: it produced a detailed, historically accurate narrative about subprime lender failures at 5100 Overbrook Avenue — an answer that would be excellent if it were about the right property. The confidence and quality of wrong-property answers makes them more dangerous than obvious errors.

#### COM MCP is the clear MCP frontrunner

Since resolving its first correct parcel in P4, COM MCP has now passed 4 consecutive prompts (P4-P7) with high-quality answers. The pattern: GPT-4.1 + correct parcel = excellent results. GPT-4o (GCC MCP) + address resolution failures = consistent failures.

---

## Round 1 — Prompt 8 (2026-03-07)

### Prompt

> How many code violations at 4763 Griscom Street resulted in FAILED inspections, and what type of investigator handles them?

### Ground Truth

From the investigation report and COM MCP's corroborating SQL query:

- **45 failed inspections** out of 64 total code violation cases (70.3% failure rate)
- Investigator type: **CLIP — Vacant Lot Investigator** (primary), with some CLIP, CSU Investigator, and unrecorded
- Note: The Foundry Agent itself found "45 failed inspections" in Prompt 2 when it resolved the correct parcel

### Results

#### Philly MCP - GCC (Copilot Studio)

**Result: FAIL**

> There is one code violation at 4763 Griscom Street that resulted in a FAILED inspection. The type of investigator handling this case is not specified.

**Analysis:** Wrong property — 1 failed inspection instead of 45. Address resolution failure continues for GCC MCP.

#### Philly MCP - Com (Copilot Studio)

**Result: PASS**

> Failed inspections: 45 at 4763 Griscom Street. Investigator types on those FAILED cases: 14 by "CLIP – Vacant Lot Investigator," 3 by "CLIP," 1 by "CSU Investigator," and 27 with no investigator type recorded.

**Analysis:** Correct count (45) with a breakdown by investigator type that goes beyond the question — showing that 27 of 45 failed cases have no investigator type recorded. This is useful metadata that the document agent can't provide. Five straight passes for COM MCP.

#### Philly SP/PDF - GCC (Copilot Studio)

**Result: PASS**

> There have been 45 code violations at 4763 Griscom Street that resulted in FAILED inspections, which is a 70.3% failure rate. The investigations are handled by the Community Life Improvement Program (CLIP) - Vacant Lot Investigator.
>
> *1 reference: Property_Enforcement_File_4763_Griscom.pdf*

**Analysis:** Seven for seven. Correct count, failure rate percentage, investigator type identified, source cited. Clean and concise.

#### Foundry Agent (Philly Web SPA)

**Result: FAIL**

> There are 0 code violation cases at 4763 Griscom Street that resulted in FAILED inspections.

**Analysis:** The Foundry Agent reported **45 failed inspections** for this same property in Prompt 2 but now reports **0**. Same property, same question, opposite answer — because the address resolved to a different wrong parcel. This is the clearest demonstration yet of the non-deterministic address resolution problem: the agent contradicts its own prior answer.

#### Investigative Agent (OpenAI Web SPA)

**Result: FAIL**

> There are no code enforcement cases at 4763 Griscom Street that resulted in FAILED inspections — meaning there are currently zero open/failed code violations for this address.

**Analysis:** Wrong property, zero results. The confident phrasing ("currently zero open/failed") implies a clean property when the real one has 45 failures.

#### Triage Agent (Semantic Kernel Web SPA)

**Result: FAIL**

> 4763 Griscom Street has 0 code violations that resulted in FAILED inspections.

**Analysis:** Same false negative as Prompt 2 — the Triage Agent again claims zero violations for a property with 45 failed inspections. Routing: Triage → ViolationAnalyst. The ViolationAnalyst sub-agent consistently fails to retrieve violation data for this address.

### Prompt 8 Comparison Matrix

| Dimension | MCP - GCC | MCP - Com | SP/PDF - GCC | Foundry Agent | Investigative Agent | Triage Agent |
|---|---|---|---|---|---|---|
| **Failed count** | 1 (wrong) | 45 (correct) | 45 (correct) | 0 (wrong) | 0 (wrong) | 0 (wrong) |
| **Failure rate** | N/A | N/A | 70.3% | N/A | N/A | N/A |
| **Investigator type** | "Not specified" | Detailed breakdown | CLIP Vacant Lot | N/A | N/A | N/A |
| **Self-consistent** | N/A | Yes | Yes | **No** (said 45 in P2) | N/A | No (said 0 in P2 too) |
| **Grade** | Fail | Pass | Pass | Fail | Fail | Fail |

### Prompt 8 Analysis

#### The Foundry Agent contradicts itself

In Prompt 2, the Foundry Agent correctly found "45 failed inspections" for 4763 Griscom. In Prompt 8, it reports 0. The question is essentially the same; the address resolution randomly succeeded in P2 and failed in P8. This is the most damaging demonstration of non-deterministic behavior: an investigator using this tool would get different answers to the same question depending on when they ask.

#### COM MCP adds value beyond the document

Both COM MCP and SP/PDF-GCC got 45 failed inspections, but COM MCP provided something the document couldn't: a breakdown showing that 27 of 45 failed cases have no investigator type recorded. This is live database metadata that reveals a data quality issue — potentially useful for an investigator questioning why so many cases lack assigned investigators.

#### 4 agents report 0 failures for a 45-failure property

GCC MCP (1), Foundry (0), Investigative (0), and Triage (0) all effectively say this property is clean. The real property has a 70.3% failure rate across 64 violation cases. In an investigative context, these false negatives could lead to a property being overlooked when it should be flagged as one of the most problematic in the portfolio.

---

## Round 1 — Prompt 9 (2026-03-07)

### Prompt

> Compare the vacancy rates and violation rates between zip codes 19104 and 19132. Which is worse?

### Ground Truth

Cross-agent consensus (all 4 MCP agents that answered agree on the raw numbers):

- **19104** (West Philly / University City): 11,947 properties, 2,516 vacant (21.1%), 45,818 investigations, 27,412 failed (59.9%)
- **19132** (North Philly / Strawberry Mansion): 20,650 properties, 4,549 vacant (22.0%), 83,284 investigations, 51,698 failed (62.0%)
- **19132 is worse** on both vacancy rate and violation rate

This prompt was designed as **"MCP dominates"** — requires citywide SQL aggregation by zip code. Documents only cover 2 specific properties.

### Results

#### Philly MCP - GCC (Copilot Studio)

**Result: PASS**

> 19104: 21.06% vacancy, 59.83% violation rate. 19132: 22.03% vacancy, 62.06% violation rate. Overall, zip code 19132 has worse vacancy and violation rates.

**Analysis:** First clean pass for GCC MCP since Prompt 1. No address resolution needed (zip codes, not street addresses) = no address resolution failure. Clean comparison with both metrics and a clear conclusion. The data matches all other MCP agents exactly.

#### Philly MCP - Com (Copilot Studio)

**Result: PASS**

> 19104: 21.1% vacancy, 59.9% failure rate, 229 failed investigations per 100 properties.
> 19132: 22.0% vacancy, 62.0% failure rate, 250 failed investigations per 100 properties.
> Bottom line: 19132 is worse on both metrics.

**Analysis:** Same data as GCC MCP plus an additional "failed investigations per 100 properties" metric that normalizes for property count. Six consecutive passes for COM MCP.

#### Philly SP/PDF - GCC (Copilot Studio)

**Result: PARTIAL**

> The provided documents do not contain specific information about the vacancy rates and violation rates for zip codes 19104 and 19132. However, I can provide some insights based on GEENA LLC properties in other zip codes (19131 and 19124).

**Analysis:** Expected behavior for a "MCP dominates" prompt. The document agent correctly acknowledged it can't answer a zip-code comparison from property-specific reports, then pivoted to what it could offer (GEENA LLC data from nearby zip codes). Honest, well-scoped, cited 3 sources. Not a failure — just the wrong tool for this job.

#### Foundry Agent (Philly Web SPA)

**Result: PASS**

> Detailed comparison with neighborhood names (University City, Strawberry Mansion), per-property failed rates (2.29 vs 2.50), and vacant license counts (1,075 vs 1,658). 19132 overall worse. Fits citywide patterns of property distress and disinvestment.

**Analysis:** Most comprehensive answer — added neighborhood context, vacant license counts, and a citywide framing. The Foundry Agent excels at aggregate queries that don't require address resolution. First pass since P6.

#### Investigative Agent (OpenAI Web SPA)

**Result: PASS**

> 19104: 21.1% vacancy, 3.84 investigations/property, 2.3 failed/property.
> 19132: 22.0% vacancy, 4.03 investigations/property, 2.5 failed/property.
> 19132 also has far more demolitions (1,654 vs 830), especially city-initiated.

**Analysis:** Strong answer with a unique additional dimension — demolition counts (1,654 vs 830) that no other agent surfaced. This adds real investigative value, showing that 19132 has deeper structural distress beyond just violations. First pass since Prompt 1.

#### Triage Agent (Semantic Kernel Web SPA)

**Result: FAIL**

> 4763 Griscom Street currently has zero code violations that resulted in FAILED inspections.

**Analysis:** Answered **Prompt 8**, not Prompt 9. Second time the Triage Agent has responded to the wrong prompt (also answered P6 in P7). The triage routing pattern appears to have a prompt queuing or context carryover problem — it's processing a prior prompt instead of the current one.

### Prompt 9 Comparison Matrix

| Dimension | MCP - GCC | MCP - Com | SP/PDF - GCC | Foundry Agent | Investigative Agent | Triage Agent |
|---|---|---|---|---|---|---|
| **19104 vacancy** | 21.06% | 21.1% | N/A | 21.1% | 21.1% | N/A (wrong prompt) |
| **19132 vacancy** | 22.03% | 22.0% | N/A | 22.0% | 22.0% | N/A |
| **19104 failed rate** | 59.83% | 59.9% | N/A | 2.29/property | 2.3/property | N/A |
| **19132 failed rate** | 62.06% | 62.0% | N/A | 2.50/property | 2.5/property | N/A |
| **Additional metrics** | None | Per-100 properties | GEENA LLC context | Vacant licenses | Demolition counts | N/A |
| **Conclusion correct** | Yes | Yes | N/A | Yes | Yes | N/A |
| **Grade** | Pass | Pass | Partial | Pass | Pass | Fail |

### Prompt 9 Analysis

#### No address resolution = everybody works

This is the second "no street address" prompt (after P6), and the pattern holds: when agents don't need to resolve a street address to a parcel number, the MCP agents all succeed. GCC MCP and the Investigative Agent — which have failed nearly every address-based prompt — both delivered clean passes here. The problem is definitively address resolution, not model capability or tool design.

#### Aggregate query results by prompt type

| Prompt Type | Address-based (P2-P5, P7-P8) | Aggregate (P1, P6, P9) |
|---|---|---|
| GCC MCP | 0 Pass, 1 Partial, 5 Fail | 2 Pass, 1 Fail |
| COM MCP | 4 Pass, 0 Partial, 2 Fail | 2 Pass, 1 Fail |
| Foundry | 1 Pass, 0 Partial, 5 Fail | 2 Pass, 1 Partial |
| Investigative | 0 Pass, 1 Partial, 5 Fail | 1 Pass, 1 Partial, 1 Fail |

The data is clear: address-based queries are the failure mode. Aggregate queries work.

#### Four MCP agents agree on raw numbers

All four MCP agents that answered (GCC MCP, COM MCP, Foundry, Investigative) returned identical underlying data (11,947 / 2,516 / 45,818 / 27,412 for 19104; 20,650 / 4,549 / 83,284 / 51,698 for 19132). This confirms the MCP tools return consistent data when the query doesn't involve address resolution. The differentiation is in presentation and additional analysis.

---

## Round 1 — Prompt 10 (2026-03-07)

### Prompt

> GEENA LLC bought 2400 Bryn Mawr Avenue for $230,000 at sheriff sale. The assessed value at the time was $357,100. What percentage discount was that, and how has the assessment changed since?

### Ground Truth

From the investigation report (Property_Case_File_2400_Bryn_Mawr.pdf):

- Purchase price: $230,000 (sheriff sale, 2016)
- Assessed value at time of sale: $357,100
- Discount: ($357,100 - $230,000) / $357,100 = **35.6%** below assessed value
- Correct parcel: 521273000

### Results

#### Philly MCP - GCC (Copilot Studio)

**Result: FAIL**

> [Returned the P9 zip code comparison (19104 vs 19132) instead of answering P10]

**Analysis:** Answered the wrong prompt — returned the same P9 zip code comparison data. Either the session carried over the previous prompt or the agent didn't receive P10. No attempt to address the discount calculation.

#### Philly MCP - Com (Copilot Studio)

**Result: PASS**

> The discount was $127,100, which is about 35.6% below the assessed value (sale price was ~64.4% of assessed).

**Analysis:** Correct math, concise answer. Seven consecutive passes for COM MCP (P4-P10). Stated both the dollar discount and the percentage, plus the complement (64.4% of assessed).

#### Philly SP/PDF - GCC (Copilot Studio)

**Result: PASS**

> GEENA LLC bought 2400 Bryn Mawr Avenue for $230,000 in 2016, when the assessed value was $357,100. The discount was approximately 35.6%.
>
> *1 reference: Property_Case_File_2400_Bryn_Mawr.pdf*

**Analysis:** Eight for eight (7 Pass, 1 Partial). Correct calculation with the full formula shown, cited the source document. Consistent, reliable, sourced.

#### Foundry Agent (Philly Web SPA)

**Result: PASS**

> If we use your figure ($357,100): Discount = $127,100, about 35.6%.
>
> However, the OPA market value for 2016 (parcel 521192100) was $159,400. Using that figure, the purchase price was $70,600 (44%) **above** the city assessment, not a discount.

**Analysis:** Calculated the 35.6% correctly AND challenged the $357,100 premise against its own OPA lookup. The OPA value ($159,400) is likely from a different parcel (521192100 vs correct 521273000), but the analytical behavior — questioning an assumption and providing an alternative interpretation — is exactly what an investigator should do. Presented both scenarios without picking a winner, letting the analyst decide.

#### Investigative Agent (OpenAI Web SPA)

**Result: FAIL**

> [Returned the P9 zip code comparison (19104 vs 19132) instead of answering P10]

**Analysis:** Same issue as GCC MCP — answered the previous prompt instead of P10. The demolition counts differ slightly from its P9 answer (1,523 vs 1,654 for 19132), suggesting this might be a re-run of P9 rather than a carryover.

#### Triage Agent (Semantic Kernel Web SPA)

**Result: FAIL**

> Server error (500): "An assistant message with 'tool_calls' must be followed by tool messages responding to each 'tool_call_id'."
>
> Error occurred 3 times.

**Analysis:** Hard crash — the Semantic Kernel agent loop broke when a tool call response wasn't properly returned. This is an infrastructure/orchestration bug, not a model issue. The error message indicates the agent issued a tool call but the tool response was never fed back into the conversation, breaking the OpenAI API contract. Third consecutive failure for the Triage Agent.

### Prompt 10 Comparison Matrix

| Dimension | MCP - GCC | MCP - Com | SP/PDF - GCC | Foundry Agent | Investigative Agent | Triage Agent |
|---|---|---|---|---|---|---|
| **Answered P10** | No (answered P9) | Yes | Yes | Yes | No (answered P9) | No (crashed) |
| **Discount %** | N/A | 35.6% (correct) | 35.6% (correct) | 35.6% (correct) | N/A | N/A |
| **Questioned premise** | N/A | No | No | Yes ($159,400 OPA vs $357,100) | N/A | N/A |
| **Source cited** | N/A | No | Yes (PDF) | No | N/A | N/A |
| **Grade** | Fail | Pass | Pass | Pass | Fail | Fail |

### Prompt 10 Analysis

#### Two agents answered the wrong prompt

GCC MCP and the Investigative Agent both returned P9 answers instead of P10. This could be session context carryover, prompt not received, or the agents re-processing their previous response. Either way, they failed to engage with the actual question.

#### Foundry Agent's best analytical moment

Despite likely using the wrong parcel (521192100 vs 521273000), the Foundry Agent produced the most intellectually honest answer by presenting two interpretations: the user's $357,100 yields a 35.6% discount, but the OPA assessment ($159,400) would mean GEENA LLC paid 44% above assessment. This "here are two ways to look at it" approach is the gold standard for investigative AI — it doesn't blindly accept the premise but also doesn't dismiss it.

#### COM MCP completes a 7-prompt streak

COM MCP has now passed every prompt since P4, when it first resolved the correct parcel. Its performance split: P1 Pass, P2-P3 Fail (token/rate limits), P4-P10 Pass (7 straight). Once the address resolution and platform limits were overcome, COM MCP has been the most consistent MCP agent.

#### Triage Agent: 0 for 10 (Round 1) → 9 for 10 (Round 2 Take 3)

The Triage Agent started at 0/10 in Round 1 — the only agent with zero passes. After `search_properties` was added (Take 1: 1/10), sub-agent system prompts were improved (Take 2: 6/10), and further refinements including `excludeGovernment` prompt strengthening (Take 3: 9/10), it has shown the steepest improvement curve of any agent and is now tied with the Foundry Agent at 90%. P5 is a clean PASS ($53,155.20 from transfer record). P6 recovered from an initial hallucination regression to PASS after prompt placement fixes. P9 returns exact zip code numbers. Only P3 remains PARTIAL (correct parcel and current value, but claims flat assessment instead of the $37,200→$24,800 decline). See "Round 2 Retesting" section for full details.

---

## Round 2 Retesting

After Round 1 testing (70 responses), improvements were made to tool architecture and system prompts. Key changes: new `search_properties` fuzzy address resolver, entity network summary mode, improved tool descriptions, and system prompt workflow guidance. See `docs/improvements/improvements-round-2.md` for full details.

### Round 2 Take 1 Results (5 agents x 10 prompts = 50 runs)

| Agent | Round 1 | Round 2 Take 1 | Change |
|---|---|---|---|
| COM MCP (GPT-4.1) | 8P/0Pa/2F | **10P/0Pa/0F** | **PERFECT SCORE** |
| Investigative Agent | 1P/0Pa/9F | **8P/1Pa/1F** | +7 Pass (biggest improvement) |
| Foundry Agent | 4P/0Pa/6F | **8P/1Pa/1F** | +4 Pass |
| GCC MCP (GPT-4o) | 2P/0Pa/8F | **4P/3Pa/3F** | +2 Pass |
| Triage Agent (SK) | 0P/0Pa/10F | **1P/1Pa/8F** | +1 Pass (still last) |

**Key finding:** `search_properties` was the highest-impact single change. Zero address resolution failures for agents that used it (was 87% failure rate in Round 1). The Triage Agent was the only agent that did NOT call `search_properties`, confirming the tool was the fix.

### Round 2 Take 2: Triage Agent Retest (10 runs)

After further sub-agent improvements to the Semantic Kernel team-of-agents (improved sub-agent system prompts, routing logic, and `search_properties` integration into sub-agents), the Triage Agent was retested on all 10 prompts.

**Result: 1P/1Pa/8F → 6P/2Pa/2F** — the largest single-round improvement for this agent.

| # | Prompt | Round 1 | Take 1 | Take 2 | Notes |
|---|--------|---------|--------|--------|-------|
| P1 | GEENA LLC count + vacancy | N/T | FAIL (17 props, 23.5%) | **PASS** (330 props, 87%) | 330 matches COM MCP's distinct parcel method |
| P2 | 4763 Griscom since purchase | FAIL | FAIL (wrong parcel: 6105 N Lawrence) | **PASS** | Correct parcel via search_properties. All key facts: $6,500 sheriff's deed, 64 violations, 45 failed, demolition |
| P3 | Assessment 2017 vs today | FAIL | FAIL (no data) | **FAIL** ($20,200 / $78,500) | Ground truth: $56,900 / $24,800. Wrong parcel despite P2/P4 resolving correctly. Misses demolition story. |
| P4 | Ownership chain | FAIL | FAIL (didn't answer) | **PASS** | Perfect 6-owner chain matching COM MCP exactly |
| P5 | $146K vs $53K FMV origin | FAIL | FAIL (couldn't retrieve) | **PARTIAL** | Correctly identifies OPA assessment concept but hedges, doesn't find the field in transfer record |
| P6 | Top 5 private violators | FAIL | PARTIAL (listed govt, asked to filter) | **PARTIAL** | Same behavior — recognized govt vs private but didn't auto-filter |
| P7 | Financial institutions at 2400 Bryn Mawr | FAIL | FAIL (wrong parcel: 3825 Folsom) | **PASS** | Correct parcel, comprehensive bank failure narrative (WaMu, IndyMac, MERS, OneWest, HUD) |
| P8 | Failed violations + investigator | FAIL | FAIL ("several" — no number) | **PASS** | 45 failed, CLIP Vacant Lot Investigator, CSU for unsafe |
| P9 | Zip 19104 vs 19132 | FAIL | PARTIAL (right direction, no numbers) | **FAIL** | Blank — no response. Regression from Take 1. |
| P10 | Premium % calculation | FAIL | PASS (174.7%) | **PASS** | Correct math: 174.7% premium |

#### Take 2 Analysis

**What improved:**
- `search_properties` is now working for most prompts — address resolution fixed for P2, P4, P7, P8
- Sub-agent routing improved (OwnerAnalyst, ViolationAnalyst used appropriately)
- P1 now returns the defensible 330-parcel count instead of 17

**What's still broken:**
- P3 gets the wrong parcel despite P2 and P4 resolving correctly in the same session — non-deterministic resolution persists for individual sub-agents
- P6 recognizes government vs private distinction but doesn't proactively filter (same as Take 1)
- P9 blank response is a regression from Take 1's partial — likely a crash or timeout in the sub-agent loop
- P5 hedges on FMV source — doesn't check transfer record where the field lives

#### Round 3 Improvement Candidates (from Take 2)

1. **Mandate `search_properties` in ALL sub-agent system prompts** — fixes P3's parcel mismatch
2. **Add FMV field documentation to `get_property_transfers` tool description** — fixes P5 hedging
3. **Add `exclude_government` parameter to `get_top_violators` tool** — fixes P6 for all agents
4. **Debug P9 blank response** — investigate sub-agent timeout/crash causing regression
5. **Parcel caching in triage loop** — pass resolved parcels from one sub-agent to the next

### Round 2 Take 3: Triage Agent Retest (4 runs)

After further sub-agent system prompt improvements (mandating `search_properties` in all sub-agents, improved routing), the Triage Agent was retested on the 4 prompts that failed or partially passed in Take 2 (P3, P5, P6, P9).

**Result: 6P/2Pa/2F → 7P/2Pa/1F**

| # | Prompt | Take 2 | Take 3 | Notes |
|---|--------|--------|--------|-------|
| P3 | Assessment 2017 vs today | FAIL ($20,200 / $78,500) | **PARTIAL** ($24,800 / $24,800) | Correct parcel + current value ($24,800). Claims flat since 2017; ground truth: $37,200 → $24,800. Misses the decline. Good demolition context. |
| P5 | $146K vs $53K FMV origin | PARTIAL (hedged) | **PASS** ($53,155.20) | Clean, confident retrieval from transfer record — no hedging. |
| P6 | Top 5 private violators | PARTIAL (asked to filter) | Initially FAIL (hallucinated), then **PASS** after prompt fix | First run hallucinated 5 fake entities. After moving excludeGovernment instruction to top of prompt + few-shot example + "NEVER fabricate" rule, correctly returns GEENA LLC #1 with 1,411 violations. |
| P9 | Zip 19104 vs 19132 | FAIL (blank) | Initially PARTIAL (no numbers), then **PASS** after redeploy | First run: correct direction, no numbers. After full deploy: exact numbers matching ground truth (19104 21.1%/59.8%, 19132 22.0%/62.1%). |

#### Take 3 Analysis

**What improved:**
- P3 now resolves the correct parcel and current value — sub-agent `search_properties` is working, but assessment history query still incomplete
- P5 retrieves $53,155.20 directly from the transfer record instead of hedging
- P6 initially regressed to hallucination, then fixed by strengthening ViolationAnalyst prompt (moved excludeGovernment instruction to top, added few-shot example, added "NEVER fabricate" rule). Now returns correct data with GEENA LLC #1.
- P9 returns exact numbers after full deploy — AreaAnalyst completes the zip code aggregation successfully

**Key learning: P6 regression and recovery.**
The initial Take 3 run showed P6 regressing from PARTIAL (honest "these are government, want me to filter?") to FAIL (hallucinated fake entity names). The `excludeGovernment` parameter existed in the tool AND was documented in the sub-agent prompt, but the model wasn't following the instruction. Three prompt changes fixed it: (1) moved the instruction to the very top of the ViolationAnalyst prompt, (2) added a few-shot example showing the expected tool call, (3) added explicit "NEVER fabricate entity names" rule. This demonstrates that prompt placement and emphasis matter as much as prompt content — having the right instruction buried in a long prompt is not the same as having it front and center.

**What's still a Partial:**
- P3: Assessment history query returns only current year, not historical values — sub-agent needs to query year-by-year assessment data

### Round 2 Take 3: Non-Triage Retests (5 runs)

The `excludeGovernment` parameter and FMV field documentation changes affected all MCP agents, not just the Triage Agent. Five additional retests were run on agents with prior failures or partials on P5 and P6.

| Agent | Prompt | Before | After | Notes |
|-------|--------|--------|-------|-------|
| Investigative Agent | P5 | FAIL | **PASS** | $53,155.20 from transfer record, correct parcel and parties |
| Investigative Agent | P6 | PARTIAL | **PASS** | GEENA LLC #1 with 1,411. Added failed counts, vacancy, demolitions per entity. Best P6 response of any agent. |
| Foundry Agent | P5 | FAIL | **PASS** | $53,155.20 from transfer record, correct parcel and parties |
| GCC MCP | P5 | FAIL | **FAIL** | GPT-4o could not execute the query at all ("I'm not sure how to help") |
| GCC MCP | P6 | PARTIAL | **FAIL** | GPT-4o could not execute the query at all. Regression from PARTIAL. |

#### The Model Gap: GPT-4.1 vs GPT-4o

The non-Triage retests provide the clearest evidence yet of the model gap. The same tool improvements that produced dramatic gains for GPT-4.1 agents had zero effect on the GPT-4o agent:

**GPT-4.1 agents (COM MCP, IA, Foundry, Triage):** Every agent that received the FMV tool description and `excludeGovernment` parameter improvements either maintained or improved their scores. The Investigative Agent went from 8P/1Pa/1F to a perfect 10/10. The Foundry Agent went from 8P/1Pa/1F to 9P/1Pa/0F.

**GPT-4o agent (GCC MCP):** Could not even execute the P5 or P6 queries. Returned "I'm not sure how to help" on both. P6 regressed from PARTIAL (at least recognized the data existed) to FAIL (could not execute at all). The same tool descriptions that helped GPT-4.1 agents find and use the right parameters were invisible to GPT-4o.

**The gap in numbers:** After all Round 2 improvements, GPT-4.1 agents average 9.5 Pass out of 10. The GPT-4o agent scores 4 Pass out of 10. This is not a data problem or a tool problem — the same backend, the same tools, the same parameters. The model is the bottleneck.

**Implication for Government Cloud:** GCC Copilot Studio is locked to GPT-4o. No amount of tool improvement, prompt engineering, or data enrichment can close a gap this large. Organizations deploying in Government Cloud should expect fundamentally lower agent performance until GCC upgrades to a more capable model.

---

## Final Scorecard

### By Agent (Latest Results)

Scores reflect the most recent test run for each agent: Round 1 for doc agents (unchanged), Round 2 Take 1 for COM MCP/IA/FA/GCC MCP, Round 2 Take 3 for Triage.

| Agent | Pass | Partial | Fail | Pass Rate | Round | Notes |
|---|---|---|---|---|---|---|
| **MCP - Com** | 10 | 0 | 0 | 100% | R2 T1 | **PERFECT SCORE.** R1-R2 used GPT-5 Auto; retested GPT-4.1 in R3: same 10/10 |
| **SP/PDF - Com** | 8 | 2 | 0 | 80% (10/10 usable) | R1 | Partial on P6, P9 (expected — can't do citywide). Zero failures. |
| **SP/PDF - GCC** | 8 | 2 | 0 | 80% (10/10 usable) | R1 | Partial on P6, P9 (expected — can't do citywide). Zero failures. |
| **Investigative Agent** | 10 | 0 | 0 | 100% | R2 T3 | **PERFECT SCORE.** P5 + P6 fixed by tool description + excludeGovernment |
| **Foundry Agent** | 9 | 1 | 0 | 90% | R2 T3 | P5 fixed by FMV tool description. P1 remains Partial. |
| **Triage Agent** | 9 | 1 | 0 | 90% | R2 T3 | Sub-agent improvements: 0→1→6→9 Pass across 4 rounds. P3 remains Partial. |
| **MCP - GCC** | 4 | 2 | 4 | 40% | R2 T3 | GPT-4o couldn't execute P5/P6 retests. P6 regressed Partial→Fail. |
| **M365 Copilot** | 2 | 3 | 5 | 20% | New | Platform-assigned model. Tool reliability issues beyond address resolution. |

### By Prompt

Triage column shows R2 Take 3 results. All other agents show their latest round.

| # | Prompt | SP/PDF GCC | SP/PDF Com | COM MCP | GCC MCP | Foundry | Investigative | Triage | M365 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GEENA LLC property count | Pass | Pass | Pass | Fail | Partial | Partial | **Pass** | Partial |
| 2 | 4763 Griscom since purchase | Pass | Pass | Fail | Fail | Pass | Fail | **Pass** | Fail |
| 3 | Assessment 2017 vs 2025 | Pass | Pass | Fail | Fail | Fail | Fail | Partial | Fail |
| 4 | Ownership chain + sheriff sales | Pass | Pass | Pass | Fail | Fail | Fail | **Pass** | **Pass** |
| 5 | $146K FMV at 2004 sale | Pass | Pass | Pass | Fail | **Pass** | **Pass** | **Pass** | Fail |
| 6 | Top 5 private violators | Partial | Partial | Pass | Fail | Pass | **Pass** | **Pass** | **Pass** |
| 7 | Financial institutions + fates | Pass | Pass | Pass | Fail | Fail | Fail | **Pass** | Fail |
| 8 | Failed violations + investigator | Pass | Pass | Pass | Fail | Fail | Fail | **Pass** | Fail |
| 9 | Zip code 19104 vs 19132 | Partial | Partial | Pass | Pass | Pass | Pass | Partial | Partial |
| 10 | Purchase discount % | Pass | Pass | Pass | Fail | Pass | Fail | **Pass** | Partial |

### Key Patterns

### COM SP/PDF vs GCC SP/PDF

Both document agents scored 8 Pass / 2 Partial / 0 Fail — identical pass rates. The 2 Partials (P6, P9) are structural: documents can't answer citywide aggregate queries. Neither agent ever failed.

Qualitative differences (COM SP/PDF = GPT-4.1, GCC SP/PDF = GPT-4o):

| Dimension | GCC SP/PDF (GPT-4o) | COM SP/PDF (GPT-4.1) |
|---|---|---|
| **Answer depth** | Concise, direct extraction | More analytical — adds context and implications |
| **P2 (Griscom since purchase)** | Good narrative | Added: "never gone more than four months without a new violation," 2 source citations |
| **P3 (Assessment change)** | Year-by-year trajectory | Added: summary table with building/land split per year |
| **P5 (FMV at 2004 sale)** | $53,155 stated | Added: "275% of fair market value," "hallmark of predatory or inflated transactions" |
| **P8 (Failed violations)** | 45 failed, CLIP investigator | Added: period-based breakdown (pre/post demolition investigator types) |
| **P9 (Zip code comparison)** | Qualitative ("among highest") | GEENA LLC-specific counts per zip code (50/45 in 19104, 36/33 in 19132) |
| **P10 (Discount + assessment)** | 35.6% discount only | Added: full assessment trajectory ($357K → $317K → $265.6K), 25.6% total decline |

**Takeaway:** GPT-4.1 produces richer analytical answers from the same documents — more context, more implications, more structured output. But both models achieve the same pass/fail rate. For document agents, the model upgrade improves quality but doesn't change reliability. This contrasts sharply with MCP agents, where GPT-4.1 vs GPT-4o is the difference between 80% and 20% pass rates.

### Key Patterns

**Address resolution is the #1 failure mode.** Across prompts 2-5 and 7-8 (address-based queries), agents produced at least 10 different wrong parcel numbers for 2 addresses. Non-deterministic: the same agent gets different parcels for the same address across prompts. The Foundry Agent found 45 failed inspections in P2 (correct parcel) and 0 in P8 (wrong parcel) — contradicting itself.

**Aggregate queries work; address queries don't.** On prompts 1, 6, and 9 (entity search or zip code aggregation), all MCP agents that answered returned consistent, identical data. On address-based prompts, only COM MCP achieved reliable resolution (starting P4).

**COM MCP (GPT-4.1) vs GCC MCP (GPT-4o).** The model gap is stark: COM MCP passed 8/10, GCC MCP passed 2/10. Both hit the same MCP backend, but GPT-4.1's tool selection and address resolution are dramatically better than GPT-4o's.

**Document agents excel within scope.** Both SP/PDF agents (GCC and Com) passed or partially passed every prompt with zero failures. Their 2 Partials (P6, P9) were expected by design — citywide aggregate queries the documents can't answer. Within scope, 100% reliable. GPT-4.1 produces richer analysis from the same documents but doesn't change the pass rate.

**Pro-code agents now lead the standings.** After Round 2 Take 3 improvements, the Investigative Agent achieved a perfect 10/10 (matching COM MCP). The Foundry Agent reached 9/10, and the Triage Agent reached 9/10. All three pro-code GPT-4.1 agents now outperform every document agent. Meanwhile, GCC MCP (GPT-4o) remained at 4/10 — the same tool improvements that produced perfect scores for GPT-4.1 agents had zero effect on GPT-4o. The model, not the architecture, is the limiting factor.

## Epilogue: Pro-Code Agent Architectures

The Investigative Agent (OpenAI chat), Foundry Agent (Azure AI Foundry), and Triage Agent (Semantic Kernel team-of-agents) are supplemental to the main demo — sprinkles on top of the Copilot Studio comparison. They represent what's possible with pro-code agent architectures hitting the same MCP backend, and are included in Use Case 2 only.

### What we learned

**The Investigative Agent achieved a perfect 10/10** — matching COM MCP as the only two agents with zero failures. It went from 1/10 in Round 1 to 10/10 after Round 2 improvements. The FMV tool description fixed P5, and the `excludeGovernment` parameter fixed P6 (with the richest P6 response of any agent — failed counts, vacancy rates, and demolitions per entity). Its Round 1 weakness (address resolution) was entirely a tool gap, not a model gap.

**The Foundry Agent reached 9/10** (up from 4/10 in Round 1). The FMV tool description fixed P5. Its one remaining PARTIAL (P1: GEENA LLC property count) is a minor counting methodology difference — it returned a defensible answer, just not the ground truth number. Its analytical moment on P10 (questioning the $357,100 premise against OPA data) remains the single best response in the entire evaluation.

**The Triage Agent has shown the most dramatic improvement arc** (0→1→6→9 Pass across four test rounds). Round 1: 0/10 — failures spanned false negatives, wrong parcels, wrong prompts, crashes. Round 2 Take 1: 1/10 — only used `search_properties` once. Round 2 Take 2: 6/10 — sub-agent system prompts improved, `search_properties` integrated into sub-agents. Round 2 Take 3: 9/10 — P5 retrieves FMV directly, P6 recovered from hallucination regression after prompt placement fix, P9 returns exact numbers. Only P3 remains PARTIAL (assessment history incomplete). The Triage Agent is now tied with the Foundry Agent at 90% and demonstrates that even the most complex multi-agent architecture can match simpler agents with sufficient iteration.

**Build complexity requires more iteration, not less.** After Round 1, the simplest agents (COM MCP and both SP/PDF agents via Copilot Studio) outperformed all three pro-code agents. However, iterative improvements to tool descriptions, system prompts, and sub-agent routing have closed the gap completely for GPT-4.1 agents. COM MCP reached 10/10 with tool changes alone. The Investigative Agent reached a perfect 10/10 with FMV + excludeGovernment improvements. The Foundry Agent hit 9/10 (P1 Partial). The Triage Agent went from 0/10 to 9/10 across four rounds. The lesson: pro-code architectures have higher initial cost but respond extremely well to iterative refinement — and can ultimately match or exceed low-code platforms when paired with the right model (GPT-4.1). The GCC MCP agent (GPT-4o) did not benefit from the same improvements, remaining at 4/10.

### Danger Taxonomy (Updated from Use Case 1)

1. **Critical: Wrong-entity analysis** — real data, wrong property. Agent confidently reports on a different address. (Investigative P2, GCC MCP P3, P7)
2. **Critical: False negative** — data exists but agent claims it doesn't. 45 violations → "zero violations." (Triage P2/P8, M365 P2, multiple agents P3-P5)
3. **Critical: Self-contradiction** — same agent, same property, different answers. (Foundry P2 vs P8: 45 → 0; M365 P4 vs P5: parcel works → "does NOT exist")
4. **High: Non-deterministic address resolution** — 10+ different wrong parcel numbers across agents and prompts for 2 addresses
5. **High: Wrong prompt answered** — agent responds to a previous question instead of the current one (Triage P7/P9, GCC MCP P10, Investigative P10)
6. **High: Incorrect data availability claim** — agent states data doesn't exist in the system when it does, never attempts the lookup. (M365 P7: "mortgage histories are not included" — they are in transfer records)
7. **Medium: Confident fabrication** — plausible but wrong narrative (Triage P3: tax-exempt explanation for a demolished building)

### Recommendation

After Round 2 Take 3, the iterative improvement process has reached diminishing returns for GPT-4.1 agents. Three agents are at 9-10/10 (COM MCP, Investigative Agent, Triage Agent), and the Foundry Agent is at 9/10. The only remaining PARTIAL is the Triage Agent's P3 (assessment history incomplete). The document agents remain at 8P/2Pa/0F — their 2 Partials are structural (can't answer citywide queries) and unfixable without adding more data.

The GCC MCP agent (GPT-4o) remains at 4/10 despite receiving every tool and prompt improvement. This is the clearest evidence in the evaluation that the model — not the data, tools, or architecture — is the limiting factor for Government Cloud deployments.

---

## Round 3: Model Validation (20 runs)

During Round 3 preparation, we discovered that Commercial Copilot Studio defaults to GPT-5 Auto, not GPT-4.1. All COM MCP results from Rounds 1-2 used GPT-5 Auto. To validate the findings, two tests were run — same backend, same tools, different model configurations:

1. **COM MCP reconfigured to GPT-4.1** — all 10 prompts retested
2. **COM SP/PDF with GPT-5 Auto** — all 10 prompts tested as a new comparison point

### COM MCP: GPT-5 Auto vs GPT-4.1

| # | Prompt | GPT-5 Auto (R2) | GPT-4.1 (R3) |
|---|--------|------------------|---------------|
| 1 | GEENA LLC count + vacancy | Pass (330, 86.7%) | Pass (330, 86.7%) |
| 2 | 4763 Griscom since purchase | Pass | Pass |
| 3 | Assessment 2017 vs now | Pass | Pass |
| 4 | Ownership chain | Pass | Pass (includes mortgage assignments) |
| 5 | $146K FMV | Pass ($53,155.20) | Pass ($53,155.20) |
| 6 | Top 5 violators | Pass | Pass (richer per-entity detail) |
| 7 | Financial institutions | Pass | Pass |
| 8 | Failed violations | Pass (45) | Pass (45) |
| 9 | Zip code comparison | Pass | Pass |
| 10 | Discount + assessment | Pass (35.6%) | Pass (35.6%) |

**COM MCP: GPT-5 Auto 10/10, GPT-4.1 10/10. No performance difference on this workload.**

GPT-4.1 responses were qualitatively similar — same facts, same parcel numbers, same calculations. The original 10/10 result was not inflated by GPT-5 Auto.

### COM SP/PDF: GPT-5 Auto (new test)

| # | Prompt | GPT-5 Auto | Score |
|---|--------|------------|-------|
| 1 | GEENA LLC count + vacancy | 194, 91.8% from report | Pass |
| 2 | 4763 Griscom since purchase | Vacant lot, violations, demolition | Pass |
| 3 | Assessment 2017 vs now | $56,900 → $24,800, demolition | Pass |
| 4 | Ownership chain | Complete chain, 2 sheriff sales, doc IDs cited | Pass |
| 5 | $146K FMV | $53,155, 275% calculation | Pass |
| 6 | Top 5 violators | Only GEENA LLC — can't do citywide from docs | Partial |
| 7 | Financial institutions | Complete institutional chain | Pass |
| 8 | Failed violations | 45 failed, CLIP + Property Maintenance | Pass |
| 9 | Zip code comparison | GEENA LLC properties only, not citywide | Partial |
| 10 | Discount + assessment | 35.6%, $357,100 → $265,600 | Pass |

**COM SP/PDF with GPT-5 Auto: 8P / 2Pa / 0F — identical to COM SP/PDF with GPT-4.1.** The 2 Partials (P6, P9) are structural limitations of document agents, unchanged by model.

### Model Validation Finding

The model gap that defines this evaluation is **GPT-4o vs everything above it**, not GPT-4.1 vs GPT-5 Auto:

| Model | COM MCP | COM SP/PDF |
|-------|---------|------------|
| GPT-4o (GCC) | 4/10 | 8/10 |
| GPT-4.1 | 10/10 | 8/10 |
| GPT-5 Auto | 10/10 | 8/10 |

GPT-4.1 is sufficient for perfect scores with the right tools. The bottleneck is GPT-4o, which cannot effectively use the same tools regardless of improvements. Organizations choosing between GPT-4.1 and GPT-5 Auto can expect equivalent agent performance on this class of workload.

This round adds another dimension to the evaluation's core thesis: we are testing every combination of agent architecture, model, and data path against the same backend. Same APIM gateway, same Functions, same SQL. The only variables are who does the orchestration and which model reasons over the results.

---

---

## M365 Copilot Testing (10 runs)

M365 Copilot uses the same `/mcp` endpoint as Copilot Studio — zero code, 3 JSON manifest files. The model is platform-assigned (no user control). Unlike Copilot Studio, M365 Copilot presents each external tool call to the user for confirmation before executing — a "human in the loop" UX that can be disabled via admin pre-approval or the `x-openai-isConsequential` manifest property.

### Results

| # | Prompt | Score | Notes |
|---|--------|-------|-------|
| 1 | GEENA LLC count + vacancy | **Partial** | Got 330 properties (matches COM MCP), but entity network tool failed — no vacancy % |
| 2 | 4763 Griscom since purchase | **Fail** | Found correct parcel (232452100) but all detail lookups returned no data. Concluded "no violations, no demolitions" — false negative (64 violations, 45 failed) |
| 3 | Assessment 2017 vs now | **Fail** | Couldn't resolve address despite correct parcel in P2. Asked user for parcel number. |
| 4 | Ownership chain | **Pass** | Outstanding. Correct parcel, complete 6-transfer chain, both sheriff sales, mortgage context, speculative pattern analysis |
| 5 | $146K FMV | **Fail** | Claimed parcel 232452100 "does NOT exist in OPA system" despite using it successfully in P4. Sent user to property.phila.gov |
| 6 | Top 5 private violators | **Pass** | Perfect match with ground truth. Best P6 of any agent — both LLCs and individuals, rich per-entity analysis, government properly excluded |
| 7 | Financial institutions | **Fail** | Claimed "mortgage histories are not included in the city's datasets" — wrong. Transfer records contain the full institutional chain (COM MCP proved this in R1) |
| 8 | Failed violations | **Fail** | Couldn't resolve address. Asked user for parcel number. |
| 9 | Zip code comparison | **Partial** | Tools "failed to execute." Gave qualitative answer from general knowledge — correct direction (19132 worse) but zero database numbers |
| 10 | Discount + assessment | **Partial** | Correctly calculated 35.6% discount. Couldn't resolve parcel for assessment trajectory. |

**Final: 2 Pass / 3 Partial / 5 Fail — 20% Pass Rate**

### M365 Copilot Analysis

#### Tool reliability is the defining failure mode — not address resolution

Unlike other agents whose failures were almost entirely address resolution, M365 Copilot exhibits a different failure pattern: tools that return no data even with the correct parcel (P2), tools that fail entirely (P1, P9), and incorrect assumptions about data availability (P7). The agent found parcel 232452100 in P2 and produced a perfect ownership chain from it in P4, but claimed the same parcel "does NOT exist" in P5. This is non-deterministic tool execution at the tool-call level, beyond the address-resolution non-determinism seen with other agents.

#### The confirmation UX is a demo asset

M365 Copilot shows each external tool call to the user and requires confirmation before executing. For demos, this is a strong differentiator — it makes the MCP tool calls visible and explainable rather than a black box. Enterprise security and compliance teams value this "human in the loop" pattern. For production, admins can pre-approve specific agents so actions execute without confirmation (available since August 2025).

#### Platform-assigned model creates a black box

Unlike every other agent in the evaluation where we know the model (GPT-4o or GPT-4.1), M365 Copilot's model is platform-assigned and not configurable. The 20% pass rate is the worst of any MCP agent, but we cannot attribute this to a specific model version. The failure modes (tool reliability, incorrect assumptions about data availability) differ from the GPT-4o agent's failures (address resolution, inability to execute queries), suggesting either a different model or different orchestration logic.

#### When it works, it's excellent

P4 (ownership chain) and P6 (top 5 violators) are among the best responses in the entire evaluation. P4 includes mortgage context and speculative pattern analysis. P6 matches COM MCP's quality exactly — the only two agents that included both LLCs and individuals with rich per-entity analysis. The problem isn't capability — it's consistency.

#### New danger taxonomy entry

M365 Copilot introduces a new failure mode not seen with other agents: **incorrect data availability claims** (P7). The agent confidently stated that mortgage histories "are not included in the city's datasets" when they are — COM MCP retrieved the complete institutional chain from the same transfer records. This is different from a false negative (where data is retrieved but not recognized); here the agent never attempted the lookup because it assumed the data didn't exist.

---

*Testing complete. 176 responses scored across 10 prompts, 8 agents, and 6 test rounds (Round 1: 70, Round 2 Take 1: 53, Round 2 Take 2: 10, Round 2 Take 3: 13, Round 3: 20, M365 Copilot: 10). Two agents achieved perfect 10/10: COM MCP and Investigative Agent. GPT-4.1 agents average 9.5/10 (validated by Round 3 retest); GPT-4o agent: 4/10; M365 Copilot (platform-assigned model): 2/10.*
