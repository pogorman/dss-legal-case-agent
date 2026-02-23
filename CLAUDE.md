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

## Data Provenance
- Source material: real SC DSS legal pleadings (Spartanburg case) + attorney feedback (Laurel's prompt), provided by Arya Hekmat (SC DSS)
- **All data in the system is synthetic** — real case structure was used as a template, all PII replaced with fictional names/dates/facts
- Laurel's 4-part prompt (timeline, discrepancies, statements by each parent) shaped the MCP tools and SQL schema
- Source Word docs have been **sanitized** via `docs/sanitize-docs.py` — all real PII replaced with synthetic data, verified clean
- Source documents (`.docx`, `.msg`) are in `docs/` locally but **excluded from git** via `.gitignore`
- The `.msg` email still contains real names/screenshots — local only, not sanitizable
- No real PII was ever loaded into Azure SQL
- See `docs/architecture.md` → "Data Provenance" section for full details including replacement mapping

## Networking
- SQL Server (`philly-stats-sql-01`) has **public network access disabled**
- Private endpoint `pe-sql-philly` on `snet-private-endpoints` (10.0.2.0/24)
- Private DNS zone `privatelink.database.windows.net` linked to VNet
- Function App VNet-integrated via `snet-dss-functions` (10.0.3.0/24) with `vnetRouteAllEnabled`
- All SQL traffic flows: Function App → VNet → private endpoint → SQL (never public internet)
- Portal Query Editor does NOT work (requires public access)

## SQL Deployment
To redeploy data: temporarily enable SQL public access in the Azure Portal (SQL Server → Networking), add your client IP to the firewall, run `node database/deploy-sql.js`, then set public access back to **Disabled**. The script drops and recreates all tables, loads schema.sql, then seed-expanded.sql.
