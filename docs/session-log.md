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
- Demo guide backup prompt for closed case now references `2024-DR-21-0149` (a generated closed case)

---

## Session 3 — 2026-02-19

### What was done
- **Favicon**: Created scales of justice icon (navy/gold DSS branding) — SVG + 32px PNG + 180px Apple touch icon
- **Fixed favicon auth**: Favicon routes were behind AAD `/*` auth rule. Added anonymous access for `favicon.svg`, `favicon-32.png`, `apple-touch-icon.png` in `staticwebapp.config.json`
- **Fixed stale case reference**: Demo guide backup prompt referenced non-existent `2024-DR-08-0156`, updated to `2024-DR-21-0149` (actual closed case)
- **Copilot Studio MCP guide**: Added full connection instructions to `docs/user-guide.md` — MCP onboarding wizard steps, server config values, tool verification, troubleshooting, and fallback OpenAPI YAML schema
- **Full doc audit**: Verified all data counts match live DB (50/275/325/338/150), all URLs consistent, no stale references
- **Initial git commit + push**: All project files committed and pushed to `github.com/pogorman/dss-legal-case-agent` (5 commits on main)

### Open items
- Set up Copilot Studio agent pointing at `/mcp` endpoint (instructions now in user-guide.md)
- Demo dry run with live audience walkthrough

---

## Session 4 — 2026-02-19

### What was done

#### SharePoint Documents for Copilot Studio Comparison Demo
- Created `sharepoint-docs/` folder with realistic legal documents for Cases 1 and 2
- **Case 1 (2024-DR-42-0892) — 6 documents:**
  - `DSS_Investigation_Report.md` — Case manager Renee Dawson's investigation notes, interviews, observations, recommendations
  - `Medical_Records.md` — Spartanburg Medical Center records: admission, radiology, Dr. Chowdhury's assessment, nursing notes with parent statements
  - `Sheriff_Report_24-06-4418.md` — Lt. Odom's investigation, Marcus Webb interview (pp. 3-5), Dena Holloway interview (pp. 6-8)
  - `Court_Orders_and_Filings.md` — Emergency removal order, probable cause hearing, 30-day review
  - `Home_Study_Report.md` — Kinship placement assessment for Theresa Holloway
  - `GAL_Report.md` — Karen Milford's Guardian ad Litem report
- **Case 2 (2024-DR-15-0341) — 5 documents:**
  - `DSS_Investigation_Report.md` — Monica Vance's full investigation from referral through TPR filing
  - `Substance_Abuse_Evaluation.md` — Dr. Raymond Ellis's clinical evaluation of Crystal Price
  - `Court_Orders_and_Filings.md` — All 6 court events: emergency order, probable cause, 90-day review, voluntary relinquishment, TPR petition, TPR probable cause
  - `TPR_Petition_and_Affidavit.md` — Formal petition with statutory grounds, Monica Vance's sworn affidavit
  - `GAL_Reports.md` — Thomas Reed's initial and updated reports recommending TPR
- **Demo_Comparison_Prompts.md** — 6 categories of prompts with expected MCP vs SharePoint agent responses
- All documents use page markers matching seed data `page_reference` values
- All key statements, dates, and facts match the SQL seed data
- Fixed factual errors in sheriff report (DOBs, address, doctor/case manager names)

#### Web Front End Redesign
- Modernized `web/index.html` with professional government application look:
  - Gold "FOR OFFICIAL USE ONLY" classification banner
  - Redesigned header with scales of justice logo, DSS Office of General Counsel subtitle, PRODUCTION badge
  - Tab icons (chat bubble, file cabinet)
  - Welcome hero area with branding and description
  - Prompt chips with icons
  - Chat input footer with AI disclaimer
  - Dark navy footer with DSS branding
- Overhauled `web/css/style.css`:
  - Extended design token system (shadows, radii, more color variants)
  - Classification banner styling
  - Refined typography hierarchy
  - Message animation (fade-in slide-up)
  - Polished blockquote styling with gold accent
  - Status badge dot indicators
  - Custom scrollbar styling
  - Better table styling with hover states
  - Responsive improvements

### Decisions made
- Markdown format for SharePoint docs (easy to upload, Copilot Studio indexes them)
- Documents contain same facts as SQL data in unstructured prose — tests retrieval precision
- Some information intentionally spread across multiple documents to test cross-document synthesis
- Kept existing JS files unchanged — UI redesign is HTML/CSS only
- Classification banner adds "internal system" feel appropriate for government demo

### Open items
- Upload documents to SharePoint and create Copilot Studio agent grounded in them
- Set up Copilot Studio MCP agent pointing at `/mcp` endpoint
- Demo dry run with side-by-side comparison

## Session 5 — 2026-02-19

### What was done

#### Full Portal Layout
- Rewrote `web/index.html` with complete internal government portal:
  - Global navigation bar with dropdowns (Home, Case Intelligence, Legal Resources, Forms & Templates, Training & CLE, Support)
  - Search bar in nav (disabled, decorative)
  - Left sidebar with Quick Links (SCCIS, Odyssey, LegalServer, CAPSS, eFiling, Policy Manual), Alerts & Notices (3 SC-specific items), Upcoming Deadlines (4 items), Circuit Contacts (6 of 16 circuits)
  - Breadcrumb navigation
  - Multi-column footer with Office of General Counsel address, Internal Systems, Legal References, Administration links
  - Footer bottom with copyright and SC Code citation

#### Floating Chat Widget
- Converted agent chat from tab panel to floating bottom-right widget:
  - Floating action button (FAB) with chat bubble icon and "AI" badge
  - Chat widget as floating panel (440px wide, 600px tall) with navy header
  - "New Chat" button to clear conversation history and reset to welcome screen
  - Open/close animation
  - Responsive sizing for mobile
- Case Browser is now the default main content (always visible)
- Removed tab switching — no more chat/browser tabs
- Updated `app.js` for FAB toggle and clear functionality
- Updated `chat.js` with `reset()` function to clear conversation and restore suggested prompts

#### Deployment
- Pushed to origin/main
- Deployed to SWA production: https://happy-wave-016cd330f.1.azurestaticapps.net
- Worked around SWA CLI `crypto is not defined` error with `NODE_OPTIONS="--experimental-global-webcrypto"`

### Decisions made
- Floating widget pattern (like Intercom/Drift) rather than tab — portal content stays visible while chatting
- Case Browser loads automatically on page load (no lazy loading behind tab)
- FAB button has "AI" badge to draw attention before first use
- Shorter welcome text in widget to fit the smaller viewport

### Open items
- Upload documents to SharePoint and create Copilot Studio agent grounded in them
- Set up Copilot Studio MCP agent pointing at `/mcp` endpoint
- Demo dry run with side-by-side comparison

---

## Session 6 — 2026-02-23

### What was done

#### Investigated SQL Portal Access Issue
- O'G reported inability to run queries via Azure Portal Query Editor on both databases
- Confirmed root cause: SQL Server `philly-stats-sql-01` has **public network access disabled** (`Deny Public Network Access = Yes`)
- Portal Query Editor requires public access — this is expected behavior, not a misconfiguration

#### Verified Private Networking Already in Place
- Ran Azure CLI audit of the full networking stack — everything is already correctly configured:
  - Private endpoint `pe-sql-philly` on `snet-private-endpoints` (10.0.2.0/24)
  - Private DNS zone `privatelink.database.windows.net` linked to VNet
  - Function App `dss-demo-func` VNet-integrated via `snet-dss-functions` (10.0.3.0/24)
  - Additional private endpoints for blob/queue/table storage
- SQL traffic flows: Function App → VNet → private endpoint → SQL (all private, no public internet)

#### Updated Bicep to Reflect Actual Deployed State
- Added existing VNet and subnet references (`vnet`, `funcSubnet`, `peSubnet`)
- Added private endpoint resource (`pe-sql-philly`) with SQL Server private link connection
- Added private DNS zone (`privatelink.database.windows.net`) and VNet link
- Added private endpoint DNS zone group for automatic DNS record management
- Added `virtualNetworkSubnetId` and `vnetRouteAllEnabled` to Function App definition
- Fixed `functionSubnetName` default to match actual subnet name (`snet-dss-functions`)
- Removed empty string default from `existingVnetName` (now required)

#### Updated All Documentation
- **architecture.md**: Added full Network Architecture section with VNet/subnet/private endpoint diagram, updated SQL and Function App component details with networking info
- **user-guide.md**: Added "Database Access" section explaining Portal Query Editor limitation and alternatives for ad-hoc queries and seed data deployment
- **faqs.md**: Added 3 FAQs about Portal Query Editor, public access, and impact on apps
- **CLAUDE.md**: Added Networking section, updated SQL Deployment instructions with explicit steps

#### Data Provenance Documentation
- O'G moved source Word docs and Outlook message to `docs/` folder — 3 `.docx` legal pleadings from an active Spartanburg case (Erickson, 2023SPA00144) + 1 `.msg` email thread with attorney feedback (Kathryn Walsh screenshots, Laurel's detailed prompt/output from Thompson/Legette case)
- Analyzed all source documents to understand how real data was used to create synthetic data
- Confirmed: real case structure and attorney prompt patterns were used as templates; all PII was replaced with synthetic data; no real data was ever loaded into Azure SQL
- Added `.docx`, `.msg`, `.pdf` to `.gitignore` to prevent source documents from being committed
- Verified source files are not tracked in git
- Added comprehensive "Data Provenance" section to `architecture.md` documenting: source material, what was synthesized vs kept, how Laurel's prompt shaped the MCP tools, and source document handling
- Updated `CLAUDE.md` with data provenance summary
- Updated `faqs.md` with data origin FAQ
- Updated memory file for cross-session context

### Decisions made
- Bicep now manages the private endpoint and DNS zone resources (previously created outside of Bicep)
- Documented that Portal Query Editor won't work as a known limitation, not a bug
- Kept `deploy-sql.js` workflow as-is (temporarily enable public access) since it's an infrequent operation
- Source documents with real case data excluded from git via `.gitignore` — kept locally for reference only
- Data provenance fully documented so the synthetic-vs-real boundary is clear for anyone reviewing the project

#### Sanitized Source Word Documents
- Created `docs/sanitize-docs.py` — Python script using python-docx to find/replace all real PII with synthetic data
- Replacement mapping: Erickson→Webb/Holloway, Lydia→Jaylen, Walela McDaniel→Renee Dawson, Kathryn Walsh→Jennifer Torres, Tim Edwards→David Chen, Shawn Campbell→Rachel Simmons, Jamia Foster→Karen Milford, plus case numbers and dates
- Ran script on all 6 Word documents — 163 paragraphs updated across all files
- Renamed files from `2023SPA00144-*` to `2024SPA00892-*`
- Verification: zero real names found in any document, all synthetic names present
- Updated architecture.md with full sanitization mapping table and handling notes
- Updated CLAUDE.md data provenance section with sanitization status
- The `.msg` email still contains real names/screenshots — cannot be sanitized with python-docx, kept local only

### Decisions made
- Bicep now manages the private endpoint and DNS zone resources (previously created outside of Bicep)
- Documented that Portal Query Editor won't work as a known limitation, not a bug
- Kept `deploy-sql.js` workflow as-is (temporarily enable public access) since it's an infrequent operation
- Source documents with real case data excluded from git via `.gitignore` — kept locally for reference only
- Data provenance fully documented so the synthetic-vs-real boundary is clear for anyone reviewing the project
- Word docs sanitized in-place rather than creating copies — originals no longer needed since all data is now synthetic
- Sanitize script kept in repo (`docs/sanitize-docs.py`) in case documents need to be re-processed

### Open items
- Upload documents to SharePoint and create Copilot Studio agent grounded in them
- Set up Copilot Studio MCP agent pointing at `/mcp` endpoint
- Demo dry run with side-by-side comparison
- Consider deleting `.msg` email file once no longer needed for reference (still contains real names)
