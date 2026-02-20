# Session Log

## Session 1 — 2026-02-19

### What was done
- Created full project from spec (greenfield build)
- **Database layer**: `schema.sql` with 5 tables + indexes, `seed.sql` with 2 synthetic cases
  - Case 1 (2024-DR-42-0892): CPS emergency removal — 8 people, 12 timeline events, 15 statements, 6 discrepancies
  - Case 2 (2024-DR-15-0341): TPR — 8 people, 10 timeline events, 12 statements, 4 discrepancies
- **Azure Functions**: 5 HTTP-triggered functions (listCases, getCaseSummary, getTimeline, getStatements, getDiscrepancies) with managed identity SQL auth via DefaultAzureCredential
- **MCP Server**: Express app with POST /mcp (MCP streamable HTTP), POST /chat (OpenAI tool-calling loop with GPT-4.1), GET /healthz. 5 tool definitions mapping to APIM endpoints. Dockerfile included.
- **Web Front End**: Vanilla HTML/CSS/JS SPA with navy/gold DSS branding. Agent Chat panel with markdown rendering, tool badges, suggested prompts. Case Browser panel with embedded data. AAD auth via staticwebapp.config.json.
- **Infrastructure**: Bicep template provisioning SQL DB, Function App, Container App, SWA, APIM product/API/operations/policy. Parameters file. deploy.sh orchestration script.
- **Documentation**: README.md, architecture.md, session-log.md, user-guide.md, faqs.md

### Full Azure deployment completed
- **SQL Database**: `dss-demo` created on `philly-stats-sql-01` — schema deployed, seed data loaded (2 cases, 16 people, 22 events, 27 statements, 10 discrepancies verified)
- **Function App**: `dss-demo-func` deployed on Flex Consumption (FC1), identity-based storage, VNet integrated via `snet-dss-functions` (10.0.3.0/24), managed identity granted `db_datareader` on dss-demo
- **APIM**: Product `dss-demo`, API `dss-case-api` with 5 operations, inbound policy injecting `x-functions-key` via named value `dss-func-key`, subscription key created
- **Container App**: `dss-case-agent` on `philly-mcp-env`, image `phillymcpacr.azurecr.io/dss-case-agent:latest`, managed identity granted `Cognitive Services OpenAI User` on `foundry-og-agents`
- **Static Web App**: `swa-dss-legal-case` (Free tier), built-in AAD auth, deployed to `https://happy-wave-016cd330f.1.azurestaticapps.net`

### End-to-end testing
- MCP endpoint: `initialize`, `tools/list`, `tools/call` all verified working
- Chat endpoint: "List available cases" returned structured response with `list_cases` tool call
- **Money demo prompt** (4-part legal analysis): Agent called all 4 tools (`get_timeline`, `get_discrepancies`, `get_statements_by_person` x2) and returned full timeline table, discrepancy chart, and cited statements for both parents
- APIM gateway: All 5 endpoints verified returning data through the full chain

### Decisions made
- Used embedded case data in the Case Browser (no API dependency for the read-only view)
- Used marked.js from CDN for markdown rendering (avoids a build step for the SWA)
- MCP endpoint is unauthenticated per spec (POC — noted in code)
- Used LIKE-based person name matching in getStatements for flexibility
- Switched SWA to Free tier for built-in AAD auth (Standard tier custom auth was overly complex for a demo)
- Created new VNet subnet `snet-dss-functions` (10.0.3.0/24) since existing `snet-functions` was delegated to Container Apps
- Used identity-based storage for Function App (subscription policy prevents shared key access)
- Reused existing Container App environment `philly-mcp-env` instead of creating new one

### Open items
- Set up Copilot Studio agent pointing at `/mcp` endpoint
- Demo dry run with live audience walkthrough

---

## Session 2 — 2026-02-19

### What was done
- **Expanded data to 50 cases**: Wrote `database/generate-seed.js` — procedural generator using seeded PRNG (seed=42) for reproducibility
  - Keeps 2 hand-crafted demo cases (rich detail for primary demo prompts)
  - Generates 48 additional cases across all 16 SC judicial circuits, 46 counties, 6 case types
  - Each generated case: 5-8 timeline events, 5-8 statements, 2-4 discrepancies, 5-6 people
  - Realistic SC-specific data: judicial circuits, county mappings, judge names, case manager names
- **Deployed expanded data to Azure SQL**: 50 cases, 275 people, 325 timeline events, 338 statements, 150 discrepancies
- **Updated `deploy-sql.js`**: Now drops existing tables before recreating, auto-detects `seed-expanded.sql` if present
- **Updated Case Browser**: `web/js/cases.js` now embeds all 50 cases with people, counts (pulled from live APIM + SQL)
- **Redeployed SWA**: 50 cases visible in Case Browser
- **Verified end-to-end**: Chat endpoint returns all 50 cases, money prompt still returns full detail for hand-crafted cases
- **Updated all documentation**: CLAUDE.md, architecture.md, user-guide.md, session-log.md, demo-guide.md with 50-case data counts

### Decisions made
- Breadth over depth: 48 generated cases have moderate detail (5-8 events/statements) vs hand-crafted cases' 10-15
- Used seeded PRNG for deterministic output — `generate-seed.js` always produces the same data
- Person IDs start at 17 for generated cases (1-16 used by hand-crafted cases)
- Kept original `seed.sql` for reference; `seed-expanded.sql` is the deployed version

### Open items
- Set up Copilot Studio agent pointing at `/mcp` endpoint
- Demo dry run with live audience walkthrough
- Consider adding a third hand-crafted case (closed case `2024-DR-08-0156` referenced in demo guide) for richer demo variety
