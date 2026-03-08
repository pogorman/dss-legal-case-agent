# Handoff: Session 21 Changes to mcp-apim Repo

This file summarizes changes made in the `dss-legal-case-agent` Claude Code session that affected the `mcp-apim` (Philly Profiteering) repo. Read this to get up to speed.

## Code Changes Already Deployed (mcp-apim repo)

### 1. New Azure Function: `searchProperties`
- **File:** `functions/src/functions/searchProperties.ts`
- POST `/search-properties` with `{ address, limit }` body
- Normalizes input to USPS format (uppercase, STREET->ST, AVENUE->AVE, directional abbreviations)
- Strips apartment/unit suffixes
- Searches `opa_properties.address_std` — prefix match first, contains fallback
- Returns up to 5 matches with parcel_number, address, owner, category, market_value
- Deployed via staging directory pattern (npm workspaces workaround)

### 2. Entity Network Summary Mode
- **File:** `functions/src/functions/getEntityNetwork.ts`
- Added `?summary=true` query parameter
- Returns aggregate stats (total_parcels, vacant_count, zip_distribution, top 10 by market value, violation summary) instead of all 631 rows
- Fixed duplicate rows with `SELECT DISTINCT ea.parcel_number` subquery

### 3. MCP Server Changes
- **File:** `mcp-server/src/tools.ts` — new `search_properties` tool definition, updated `get_entity_network` with summary param, improved descriptions
- **File:** `mcp-server/src/tool-executor.ts` — added `search_properties` to switch, updated system prompt with address resolution workflow and tool selection guide
- **File:** `mcp-server/src/apim-client.ts` — added `searchProperties()` function, updated `getEntityNetwork()` to pass `?summary=true`

### 4. APIM Bicep
- **File:** `infra/modules/apim.bicep` — 3 new operations: searchProperties (POST), searchTransfers (POST), getPropertyTransfers (GET). Now 15 total operations.

### 5. Container App Redeployed
- ACR build + container app update completed

## Round 2 Retest Results (50 UC2 runs)

| Agent | Round 1 | Round 2 | Change |
|---|---|---|---|
| COM MCP (GPT-4.1) | 8P/0Pa/2F | **10P/0Pa/0F** | PERFECT |
| Investigative Agent | 1P/0Pa/9F | **8P/1Pa/1F** | +7 Pass |
| Foundry Agent | 4P/0Pa/6F | **8P/1Pa/1F** | +4 Pass |
| GCC MCP (GPT-4o) | 2P/0Pa/8F | 4P/3Pa/3F | +2 Pass |
| Triage Agent (SK) | 0P/0Pa/10F | **1P/1Pa/8F** | Still last |

## Triage Agent Failure Analysis

The Triage Agent is the ONLY agent that did NOT call `search_properties`. Every other MCP-backed agent used it and achieved zero address resolution failures. The Triage Agent continued resolving addresses to wrong parcels:

- P2 (4763 Griscom St): Resolved to parcel 611076000 → described "6105 N Lawrence St" owned by "Greta Campbell" (completely wrong property)
- P7 (2400 Bryn Mawr Ave): Resolved to parcel 243058000 → described "3825 Folsom St" owned by "Coley Doris" (completely wrong property)
- P1: Said GEENA LLC owns 17 properties (correct: 330 parcels)
- P3: "I couldn't retrieve assessment data"
- P4: Asked a clarifying question instead of answering
- P5: Generic explanation, admitted it couldn't retrieve data
- P8: No count given ("there were several"), wrong investigator type
- P9: Got direction right (19132 > 19104) but no numbers — **PARTIAL**
- P10: Correct math (174.7% premium) — **PASS** (no data lookup needed)

### Root Cause
The sub-agents (OwnerAnalyst, ViolationAnalyst, AreaAnalyst) have their own system prompts that do NOT include:
1. The address resolution workflow ("ALWAYS call search_properties FIRST")
2. The tool selection guide
3. Any awareness of the `search_properties` tool's existence or purpose

The triage routing layer adds overhead without adding intelligence. The sub-agents can't benefit from tool improvements they don't know about.

## Remaining Issues (Round 3 Candidates)

1. **GCC MCP P1 token overflow** — summary mode built but Copilot Studio GCC action may not pass `summary=true`
2. **P6 top private violators** — `get_top_violators` returns government entities by default. Need `exclude_government` filter. 4 of 5 agents fail this prompt.
3. **Triage Agent architecture** — see prompt below for fix approach
