# Improvements Round 2 — Tool Architecture and Prompt Engineering

## Overview

After 70 test runs across 7 agents and 10 prompts (Use Case 2) plus 15 retest runs (Use Case 1), three categories of failure were identified that could not be fixed with data additions alone. Unlike Round 1 (which added 11 SQL rows and 1 tool filter), Round 2 changes zero data — every improvement is to the tool layer, system prompts, or tool descriptions.

This distinction matters: Round 1 proved that structured data quality drives agent accuracy. Round 2 proves that even with perfect data, **tool design and prompt engineering determine whether the model can find and use it.**

---

## Problem Summary

| # | Problem | Use Case | Root Cause | Prompts Affected |
|---|---------|----------|------------|------------------|
| 1 | Address resolution broken — 87% failure rate | UC2 | No tool to convert street addresses to parcel numbers | P2, P3, P4, P5, P8, P10 |
| 2 | Token overflow on large entities | UC2 | Entity network returns all 631 rows instead of summary | P1 (GCC MCP) |
| 3 | Tool selection gap — agents don't call `get_case_summary` for people questions | UC1 | Tool description doesn't mention it returns nurses, doctors, witnesses | P1 (all MCP agents) |
| 4 | No guidance for address-first workflow | UC2 | System prompt doesn't tell model to resolve addresses before querying | P2-P5, P8, P10 |

---

## 1. New Tool: `search_properties` (Address Resolution)

**Problem:** Use Case 2 testing revealed that every prompt involving a street address (6 of 10) had an 87% failure rate across SQL-backed agents. The MCP server had no tool to convert "4763 Griscom St" into parcel number `232452100`. Agents were forced to guess parcel numbers or use `run_query` with ad-hoc SQL — producing different wrong parcels on every attempt.

**Prompts affected:** P2, P3, P4, P5, P8, P10 (any prompt mentioning a street address)

### What Was Built

A new Azure Function (`searchProperties`) that:
1. Normalizes input addresses to USPS format (uppercase, `STREET→ST`, `AVENUE→AVE`, directional abbreviations)
2. Strips apartment/unit suffixes
3. Searches `opa_properties.address_std` with prefix match first, then contains fallback
4. Returns up to 5 matching properties with parcel number, address, owner, category, and market value

### Verification

| Input Address | Returned Parcel | Correct? |
|---|---|---|
| 4763 Griscom St | 232452100 | Yes |
| 2400 Bryn Mawr Ave | 521273000 | Yes |

Both test addresses — the two properties featured in the investigation reports — resolve correctly on first attempt.

### Files Changed

- **New:** `functions/src/functions/searchProperties.ts` — Azure Function with address normalization and fuzzy matching
- **Modified:** `mcp-server/src/tools.ts` — New `search_properties` tool definition
- **Modified:** `mcp-server/src/tool-executor.ts` — Tool execution routing
- **Modified:** `mcp-server/src/apim-client.ts` — APIM backend call
- **Modified:** `infra/modules/apim.bicep` — New APIM operation (POST /search-properties)

### Tool Definition

```typescript
{
  name: "search_properties",
  description: "ALWAYS use this tool FIRST when given a street address to find matching OPA parcel numbers. Returns up to 5 matches with parcel number, address, owner, and market value.",
  inputSchema: {
    type: "object",
    properties: {
      address: { type: "string", description: "Street address to search for" },
      limit: { type: "number", description: "Max results (default 5)" }
    },
    required: ["address"]
  }
}
```

---

## 2. Entity Network Summary Mode

**Problem:** GEENA LLC has 631 rows in the entity network. When the GCC MCP agent (GPT-4o) received all 631 rows, it exceeded the token limit and crashed. The COM MCP agent (GPT-4.1) handled the data but produced inflated counts because it couldn't deduplicate reliably.

**Prompts affected:** P1 (GCC MCP token overflow failure)

### What Was Built

A `?summary=true` query parameter on the existing `GET /entities/{entityId}/network` endpoint. When enabled, the response changes from 631 raw rows to:

- **Aggregate stats:** total parcels (deduplicated), total addresses, vacant count, zip count, total/avg market value
- **Top 10 properties** by market value (with parcel number, address, owner, category)
- **Zip code distribution** with property and vacancy counts per zip
- **Violation summary:** total violations, failed count, demolitions

### Files Changed

- **Modified:** `functions/src/functions/getEntityNetwork.ts` — Summary mode with `SELECT DISTINCT` subqueries
- **Modified:** `mcp-server/src/tools.ts` — Updated `get_entity_network` tool to accept `summary` boolean
- **Modified:** `mcp-server/src/apim-client.ts` — Passes `?summary=true` query param

---

## 3. Improved Tool Descriptions (Both Use Cases)

**Problem:** Use Case 1 Prompt 1 — all 3 MCP agents had nurse data available in the `people` table (added in Round 1) but none called `get_case_summary` to look for it. They only checked `get_timeline` and `get_statements_by_person`. The tool description didn't mention it returns medical staff and witnesses.

### Use Case 1 Changes (DSS Legal)

**`get_case_summary`** description updated from:
> "Returns the case overview including filing date, status, county, and involved parties."

To:
> "Returns the case overview including ALL people involved (parents, children, nurses, doctors, case workers, attorneys, law enforcement, judges) with their roles and source citations, plus filing date, status, county, and case summary. Use this when asked about who is involved in a case or when looking for a specific person's role."

**`get_statements_by_person`** description updated to mention `made_to` filter and cross-audience comparison.

### Use Case 2 Changes (Philly MCP)

**`get_property_profile`** description updated to mention using `search_properties` first when starting from a street address.

**`run_query`** description updated to prefer dedicated tools over ad-hoc SQL.

### Files Changed

- **Modified:** `dss-legal-case-agent/mcp-server/src/mcp/tools.ts` — Tool descriptions
- **Modified:** `mcp-apim/mcp-server/src/tools.ts` — Tool descriptions

---

## 4. System Prompt — Address Resolution Workflow

**Problem:** Even with `search_properties` available, the model needs explicit instructions to use it before calling property-specific tools. Without this, GPT-4o especially tends to skip the lookup and guess parcel numbers.

### What Was Added

A new section in the Philly MCP system prompt:

```
CRITICAL — Address Resolution Workflow:
When a user mentions a street address:
1. ALWAYS call search_properties FIRST to resolve the address to an OPA parcel number
2. Use the returned parcel_number for ALL subsequent property tool calls
3. NEVER guess or construct a parcel number — always look it up

Tool Selection Guide:
- Street address mentioned → search_properties FIRST, then property tools
- Entity/owner name mentioned → search_entities, then get_entity_network
- Citywide stats or rankings → get_top_violators or get_area_stats
- Specific parcel number already known → property tools directly
- Complex or unusual queries → run_query (last resort)
```

A similar Tool Selection Guide was added to the DSS Legal system prompt:

```
Tool Selection Guide:
- Questions about people, parties, roles, nurses, doctors → get_case_summary
- Questions about what happened and when → get_timeline
- Questions about what someone said → get_statements_by_person
- Questions about conflicting accounts → get_discrepancies
- When unsure, call get_case_summary first
```

### Files Changed

- **Modified:** `mcp-apim/mcp-server/src/tool-executor.ts` — Philly MCP system prompt
- **Modified:** `dss-legal-case-agent/mcp-server/src/chat/completions.ts` — DSS Legal system prompt

---

## Summary

| # | Improvement | Type | Data Changes | Code Changes | Prompts Targeted |
|---|---|---|---|---|---|
| 1 | `search_properties` tool | New tool + function | 0 | 5 files | UC2 P2-P5, P8, P10 |
| 2 | Entity network summary mode | Tool enhancement | 0 | 3 files | UC2 P1 |
| 3 | Improved tool descriptions | Prompt engineering | 0 | 2 files | UC1 P1, UC2 all |
| 4 | System prompt workflow guidance | Prompt engineering | 0 | 2 files | UC1 P1, UC2 P2-P5, P8, P10 |

**Total data changes:** 0 rows
**Total code changes:** 12 files across 2 projects
**Both Container Apps redeployed:** Philly MCP + DSS MCP

---

## What This Demonstrates

Round 2 is the proof point that **agent quality is iterative.** The data was already correct — Round 1 ensured that. But the tools, prompts, and workflows around the data weren't guiding the model effectively. This is the same pattern every organization will face:

1. **Round 0 (Baseline):** Deploy the agent, test it, discover failures
2. **Round 1 (Data):** Fix data gaps — add missing rows, create discrete queryable facts
3. **Round 2 (Tools + Prompts):** Fix tool gaps — add missing tools, improve descriptions, guide model behavior through system prompts

Each round requires retesting. Each round fixes a different layer. No single round produces a production-ready agent.

---

## Retest Results (2026-03-08)

53 test runs completed: 50 for Use Case 2 (5 agents x 10 prompts, including Triage Agent retest), 3 for Use Case 1 (3 agents x P1 only).

### Use Case 2 — Round 1 vs Round 2 Comparison

| Prompt | GCC MCP R1→R2 | COM MCP R1→R2 | IA R1→R2 | FA R1→R2 | Triage R1→R2 |
|--------|---------------|---------------|----------|----------|--------------|
| P1 (GEENA LLC count) | F→**F** | P→P | F→**P** | F→**P** | F→**F** (17 props, wrong) |
| P2 (4763 Griscom history) | F→**P** | P→P | F→**P** | F→**P** | F→**F** (wrong parcel) |
| P3 (assessment 2017 vs today) | F→**Pa** | P→P | F→**P** | P→P | F→**F** (no data) |
| P4 (ownership chain) | F→**P** | P→P | F→**P** | P→P | F→**F** (no answer) |
| P5 ($53,155 FMV source) | F→**Pa** | P→P | Pa→Pa | Pa→Pa | F→**F** (generic, no data) |
| P6 (top 5 private violators) | F→**F** | P→P | F→F | F→F | F→**F** (gov entities) |
| P7 (financial institutions) | F→**Pa** | P→P | F→**P** | P→P | F→**F** (wrong parcel) |
| P8 (failed violations count) | F→**P** | P→P | F→**P** | P→P | F→**F** (no count, generic) |
| P9 (zip code comparison) | P→P | P→P | P→P | P→P | F→**Pa** (right direction, no numbers) |
| P10 (purchase premium %) | F→**F** | P→P | F→**P** | P→P | F→**P** (174.7%, correct) |

### Use Case 2 — Agent Totals

| Agent | Round 1 | Round 2 | Change |
|-------|---------|---------|--------|
| **COM MCP (GPT-4.1)** | 8P / 0Pa / 2F | **10P / 0Pa / 0F** | **+2P, -2F → PERFECT** |
| **Investigative Agent** | 1P / 0Pa / 9F | **8P / 1Pa / 1F** | +7P, +1Pa, -8F |
| **Foundry Agent** | 4P / 0Pa / 6F | **8P / 1Pa / 1F** | +4P, +1Pa, -5F |
| **GCC MCP (GPT-4o)** | 2P / 0Pa / 8F | **4P / 3Pa / 3F** | +2P, +3Pa, -5F |
| **Triage Agent (SK)** | 0P / 0Pa / 10F | **1P / 1Pa / 8F** | +1P, +1Pa, -2F |

### Use Case 1 — P1 (ER Time + Nurse)

| Agent | Round 1 | Round 2 | Notes |
|-------|---------|---------|-------|
| **Web SPA** | Partial | **Pass** | Called `get_case_summary`, found Rebecca Torres. |
| **MCP-Com** | Partial | Partial | Still says "does not specify the admitting nurse." Did not find nurse in people roster. |
| **MCP-GCC** | Fail | **Partial** | Found both Rebecca Torres AND Patricia Daniels — but used wrong admission time (12:47 AM from Sheriff Report instead of 3:15 AM). |

### Analysis

**1. COM MCP achieved a perfect 10/10 — the only agent to do so in Use Case 2.**

The `search_properties` tool eliminated the two remaining address resolution failures (P2 and P8 were its only Round 1 failures). COM MCP now matches the Web SPA's perfect score from Use Case 1. This agent went from 80% to 100% with zero data changes — only tool and prompt improvements.

**2. The Investigative Agent had the largest improvement: 1/10 → 8/10.**

This is the most dramatic turnaround in the entire evaluation. In Round 1, the Investigative Agent was essentially useless — resolving wrong parcels, answering the wrong prompts, producing unreliable results. With `search_properties` providing deterministic address resolution, it became a top performer. The same code, same model, same data — only the tool layer changed.

**3. The Foundry Agent doubled its score: 4/10 → 8/10.**

Same pattern as the Investigative Agent. Address resolution was the bottleneck, not the model or the architecture.

**4. GCC MCP improved but remains the weakest: 2/10 → 4P/3Pa/3F.**

Three issues persist:
- **P1 still fails with token overflow** — the summary mode parameter may not be reaching the function. The Copilot Studio GCC orchestrator may not be passing `summary=true` in the action configuration.
- **P6 still lists government entities** — the `get_top_violators` tool returns all owners by default. GPT-4o doesn't think to ask for private-only filtering, while GPT-4.1 (COM MCP) does.
- **P10 completely broke** — "No information was found" on 3 attempts. This is either an orchestrator routing failure or a context issue in the GCC Copilot Studio session.

**5. The Triage Agent barely improved: 0/10 → 1P/1Pa/8F.**

The Semantic Kernel team-of-agents architecture is the only agent that did NOT use `search_properties` in Round 2. Its sub-agents (OwnerAnalyst, ViolationAnalyst, AreaAnalyst) still resolve addresses to wrong parcels — P2 went to parcel 611076000 (Greta Campbell at 6105 N Lawrence St), P7 went to parcel 243058000 (Coley Doris at 3825 Folsom St). The routing layer adds overhead without adding intelligence, and the sub-agents don't inherit the system prompt guidance about the address resolution workflow. Its only pass (P10) required no data lookup — pure math. Its only partial (P9) got the directional answer right but returned no numbers. This confirms that the tool improvements work — but only for agents whose architecture allows them to actually call the tools.

**6. P6 (top private violators) is a systemic weakness.**

Only COM MCP correctly filters to private owners. GCC MCP, IA, and FA all return government entities (PHA, Land Bank, City of Phila). The `get_top_violators` tool doesn't accept a filter parameter — it returns the raw top-N by violation count, and the model must decide to exclude government entities. GPT-4.1 does this naturally; GPT-4o and the pro-code agents' system prompts don't guide this behavior. A possible Round 3 fix: add an `exclude_government` parameter to `get_top_violators`.

**6. P5 ($53,155 FMV) separates good from great.**

COM MCP was the only agent to identify the Common Level Ratio (CLR) formula: $15,680 assessed × 3.39 CLR = $53,155.20. All other agents called it a "city assessment" or "OPA value" — close but imprecise. This level of analytical depth comes from the model's ability to cross-reference multiple transfer records and recognize the pattern, not from any tool improvement.

**8. Address resolution is solved — for agents that use it.**

Every agent that called `search_properties` got parcel 232452100 for "4763 Griscom St" and 521273000 for "2400 Bryn Mawr Ave." Zero address resolution failures for COM MCP, IA, FA, and GCC MCP in Round 2, compared to 87% failure in Round 1. The Triage Agent — the only agent that did NOT call `search_properties` — continued to fail on every address-based prompt, providing the control group that confirms the tool was the fix.

**9. DSS Legal Web SPA now finds the nurse.**

The improved `get_case_summary` tool description ("ALL people involved including nurses, doctors...") caused the Web SPA to call `get_case_summary` and find Rebecca Torres. MCP-Com still didn't find her — suggesting the Copilot Studio orchestrator's tool selection logic differs from the custom chat endpoint's. MCP-GCC found both nurses but hallucinated the wrong admission time — a GPT-4o faithfulness issue, not a tool issue.

### Remaining Issues for Round 3

| Issue | Agent(s) | Type | Possible Fix |
|---|---|---|---|
| P1 token overflow persists | GCC MCP | Tool config | Verify Copilot Studio action passes `summary=true` |
| P6 returns government entities | GCC MCP, IA, FA, Triage | Tool design | Add `exclude_government` filter to `get_top_violators` |
| Triage sub-agents ignore search_properties | Triage | Architecture | Sub-agents need system prompt with address resolution workflow |
| P10 "no information found" | GCC MCP | Orchestrator | Investigate GCC Copilot Studio routing failure |
| MCP-Com doesn't find nurse | MCP-Com (UC1) | Tool selection | May need role="Nurse" instead of role="Witness" in people table |
| MCP-GCC wrong admission time | MCP-GCC (UC1) | Model | GPT-4o faithfulness issue — no tool fix available |

### Updated Rankings — All Agents, Both Use Cases

**Use Case 2 (post-Round 2):**

| Rank | Agent | Pass | Partial | Fail | Round 1 Rank |
|------|-------|------|---------|------|-------------|
| 1 | COM MCP (GPT-4.1) | 10 | 0 | 0 | 2 |
| 2 (tie) | Investigative Agent (GPT-4.1) | 8 | 1 | 1 | 6 |
| 2 (tie) | Foundry Agent (GPT-4.1) | 8 | 1 | 1 | 4 |
| 2 (tie) | SP/PDF - GCC (GPT-4o) | 8 | 2 | 0 | 1 |
| 2 (tie) | SP/PDF - Com (GPT-4.1) | 8 | 2 | 0 | 3 |
| 6 | GCC MCP (GPT-4o) | 4 | 3 | 3 | 5 |
| 7 | Triage Agent (SK, GPT-4.1) | 1 | 1 | 8 | 7 |

**Note:** SP/PDF agents were not retested (unaffected by MCP changes). Their Round 1 scores carry forward. Triage Agent retested separately (10 additional runs).
