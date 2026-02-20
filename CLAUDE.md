# DSS Legal Case Agent — Project Instructions

## Project Overview
Sales demo for SC DSS General Counsel. Shows MCP-backed agent vs SharePoint-backed agent. Four-tier: SWA → Container App (MCP/Chat) → APIM → Functions → Azure SQL.

## Documentation Requirements
After every session or when O'G asks, update these files in `docs/`:
- `architecture.md` — system architecture and design decisions
- `session-log.md` — append a new session entry with what was done, decisions, open items
- `user-guide.md` — how to use the demo application
- `faqs.md` — append any clarification questions asked during sessions

## Key File Paths
- Database: `database/schema.sql`, `database/seed.sql` (2 hand-crafted), `database/seed-expanded.sql` (50 cases), `database/generate-seed.js` (generator)
- Database tools: `database/deploy-sql.js` (deploys schema + seed to Azure SQL), `database/grant-identity.js` (grants managed identity db_datareader)
- Functions: `functions/src/functions/` (5 files), `functions/src/db/client.ts`
- MCP Server: `mcp-server/src/index.ts`, `mcp-server/src/mcp/server.ts`, `mcp-server/src/mcp/tools.ts`, `mcp-server/src/chat/completions.ts`
- Web: `web/index.html`, `web/js/chat.js`, `web/js/cases.js` (50 embedded cases), `web/js/app.js`, `web/css/style.css`
- SharePoint docs: `sharepoint-docs/` — 11 realistic legal documents for Cases 1-2, plus `Demo_Comparison_Prompts.md`
- Infra: `infra/main.bicep`, `infra/parameters.json`, `deploy.sh`

## Conventions
- TypeScript for all backend code (Functions + MCP Server)
- Vanilla HTML/CSS/JS for the web front end (no framework, no build step)
- Azure managed identity for all service-to-service auth (SQL, OpenAI)
- APIM subscription key for Container App → APIM auth
- Seed data person_id values are IDENTITY-generated — references in statements/discrepancies assume insertion order
- Cases 1-2 are hand-crafted with rich detail (12+ timeline events, 15+ statements, 6+ discrepancies) for the primary demo prompts
- Cases 3-50 are procedurally generated with moderate detail (5-8 events, 5-8 statements, 2-4 discrepancies) for volume

## Synthetic Cases (50 total)
- Case 1: `2024-DR-42-0892` — CPS (Webb/Holloway, Spartanburg) — primary demo case
- Case 2: `2024-DR-15-0341` — TPR (Price, Richland) — secondary demo case
- Cases 3-50: Generated across all 16 SC judicial circuits, 46 counties, 6 case types

## Data Counts
- 50 cases, 275 people, 325 timeline events, 338 statements, 150 discrepancies

## SQL Deployment
To redeploy data: temporarily enable SQL public access, run `node database/deploy-sql.js`, then disable public access. The script drops and recreates all tables, loads schema.sql, then seed-expanded.sql.
