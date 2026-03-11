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
- Analyzed all source documents to understand how real data was used to create synthetic data
- Confirmed: real case structure and attorney prompt patterns were used as templates; all PII was replaced with synthetic data; no real data was ever loaded into Azure SQL
- Added `.docx`, `.msg`, `.pdf` to `.gitignore` to prevent source documents from being committed
- Added comprehensive "Data Provenance" section to `architecture.md`
- Updated `CLAUDE.md` with data provenance summary, `faqs.md` with data origin FAQ

#### Sanitized Source Word Documents
- Created `scripts/sanitize-docs.py` — Python script using python-docx to find/replace all real PII with synthetic data
- Ran script on all 6 Word documents — 163 paragraphs updated across all files
- Verification: zero real names found in any document, all synthetic names present

### Decisions made
- Bicep now manages the private endpoint and DNS zone resources (previously created outside of Bicep)
- Documented that Portal Query Editor won't work as a known limitation, not a bug
- Kept `deploy-sql.js` workflow as-is (temporarily enable public access) since it's an infrequent operation
- Source documents with real case data excluded from git via `.gitignore` — kept locally for reference only
- Data provenance fully documented so the synthetic-vs-real boundary is clear for anyone reviewing the project
- Word docs sanitized in-place rather than creating copies — originals no longer needed since all data is now synthetic

---

## Session 7 — 2026-03-05

### What was done

#### Demo Preparation
- Created `docs/demo-notes.md` with:
  - Data design decision explanation: structured SQL data was created first, SharePoint documents were written from that data (not extracted from docs)
  - Audience framing script: "This is what digitization looks like"
  - Key demo sections summary table with best "wow" prompts
  - Recommended demo flow (factual retrieval → discrepancies → scalability → precision)
  - 5 discrepancy questions grounded in actual seed data and SharePoint documents
  - Recommended question order for maximum demo impact

#### Removed All State-Specific Branding
- Site is now generic "Department of Social Services" — no South Carolina references
- "Office of General Counsel" changed to "Office of Legal Services"
- SC county names replaced with generic region names throughout the UI
- SC-specific links in sidebar genericized, footer address/phone genericized
- System prompt in `mcp-server/src/chat/completions.ts` updated
- All 50 plaintiff entries in `web/js/cases.js` changed to "Department of Social Services"

#### Warm-Up Button and Popup
- Added "Warm Up" button in the header bar
- Opens a status popup with three animated stages: Container App, Database Connection, AI Model
- Fires a real `/healthz` request then a real `/chat` request to prime the full pipeline
- Shows spinners that transition to checkmarks with per-stage timing
- Auto-closes after 4 seconds on success — one-click pipeline primer for demos

### Decisions made
- Genericized branding to make the demo reusable across any state DSS — not tied to SC
- Warm-up uses real requests (not synthetic pings) so the entire cold-start chain is primed
- Auto-close on the warm-up popup keeps the flow moving without requiring a dismiss click
- Demo flow should start with easy contradictions and build to cross-document bombshells

### Open items
- Upload documents to SharePoint and create Copilot Studio agent grounded in them
- Set up Copilot Studio MCP agent pointing at `/mcp` endpoint
- Demo dry run with side-by-side comparison
- Consider deleting `.msg` email file once no longer needed for reference (still contains real names)

---

## Session 8 — 2026-03-05

### What was done

#### Diagnosed Function App 503 Outage
- Function App `dss-demo-func` was returning 503 Service Unavailable on all requests
- Azure reported state as "Running" / "Normal" but no requests could complete
- Root cause: Storage account `dssdemofuncsa` had `publicNetworkAccess: Disabled`, preventing the Function App runtime (and Kudu deployment engine) from accessing the deployment package blob
- Previous workaround of toggling public access was unsustainable for a demo environment

#### Permanent Fix: Private Endpoints for Function App Storage
- Created three private endpoints on `snet-private-endpoints` (10.0.2.0/24):
  - `pe-blob-dss` → `dssdemofuncsa` blob (10.0.2.8)
  - `pe-queue-dss` → `dssdemofuncsa` queue (10.0.2.9)
  - `pe-table-dss` → `dssdemofuncsa` table (10.0.2.10)
- Registered DNS A records in existing private DNS zones (`privatelink.blob/queue/table.core.windows.net`)
- Function App now reaches its storage account entirely over the VNet — no public access needed, ever

#### Fixed APIM Function Key Injection
- APIM had no API-level policy for `dss-case-api` — was not injecting the function key
- Added inbound policy to inject function key as `?code=` query parameter from named value `dss-func-key`
- Previously worked because the Function App was configured with anonymous auth level or the key was injected differently; after redeployment the auth requirement was enforced

#### Redeployed Functions Successfully
- `func azure functionapp publish dss-demo-func --typescript` now succeeds via Kudu → VNet → private endpoint → storage
- All 5 functions verified working through APIM

#### Verified Full Pipeline End-to-End
- APIM `/dss/cases` → returns all 50 cases
- Container App `/chat` with "What do you know about Jaylen Webb?" → agent called `list_cases` + `get_case_summary`, returned full case summary with parties, injuries, timeline, and source citations

### Decisions made
- Private endpoints for storage (matching the SQL private endpoint pattern) rather than toggling public access
- ~$8/month added cost is justified for demo reliability
- APIM policy uses `?code=` query parameter (not `x-functions-key` header) — both work, but query param is simpler for Functions auth
- Created temp `infra/apim-policy.json` for the az rest call, then deleted it

### Open items
- Upload documents to SharePoint and create Copilot Studio agent grounded in them
- Set up Copilot Studio MCP agent pointing at `/mcp` endpoint
- Demo dry run with side-by-side comparison
- Update Bicep to include storage private endpoints (currently created via CLI, not in IaC)

---

## Session 9 — 2026-03-05

### What was done

#### Copilot Studio MCP Testing — 5-Way Response Comparison
- Tested the same question ("What time was Jaylen Webb brought to the ER, and who was the admitting nurse?") across 5 agent configurations:
  1. **GCC Copilot Studio (MCP tool)** — hallucinated the time (2:00 AM vs actual 3:15 AM) and fabricated a source citation (Dictation PDF p. 4)
  2. **Commercial Copilot Studio (MCP tool)** — correct time, correct citation, noted nurse not in structured data
  3. **Web SPA (GPT-4.1 /chat)** — nearly identical to Commercial, correct on all points
  4. **Commercial Copilot Studio (Knowledge — uploaded docs)** — found the nurse (Rebecca Torres, RN, BSN) from Medical_Records.md but didn't return the admission time
  5. **Commercial Copilot Studio (SharePoint library)** — total failure, "No information was found"
- Key finding: Rebecca Torres exists in the markdown documents but was never modeled into the SQL schema — neither structured nor unstructured approach alone gave a complete answer
- Documented the SharePoint indexing pipeline difference: direct upload to Copilot Studio processes and indexes immediately; SharePoint library depends on Microsoft Search crawler which may not index `.md` files

#### Organized docs/ Folder
- Created `docs/README.md` — index file linking all documentation
- Created `docs/copilot-studio-testing.md` — full writeup of the 5-way comparison with analysis
- Moved `docs/sanitize-docs.py` to `scripts/sanitize-docs.py`
- Deleted `docs/test-responses.txt` (raw data absorbed into the testing doc)
- Updated all path references in `CLAUDE.md`, `docs/architecture.md`, `docs/session-log.md`, and the script docstring

#### Generated docx/pdf Versions of SharePoint Documents
- Created `scripts/convert-md-to-docs.py` — converts all markdown files to `.docx` (python-docx) and `.pdf` (fpdf2)
- Converted all 12 markdown files in `sharepoint-docs/`
- Reorganized into format-specific subfolders for easy drag-and-drop into separate SharePoint libraries:
  - `Case-2024-DR-42-0892/Case-2024-DR-42-0892-md/`
  - `Case-2024-DR-42-0892/Case-2024-DR-42-0892-docx/`
  - `Case-2024-DR-42-0892/Case-2024-DR-42-0892-pdf/`
  - (same pattern for Case-2024-DR-15-0341)
- Removed loose files from case folder roots — only subfolders remain

### Decisions made
- Demo narrative shifted from "structured is better" to "structured and unstructured are complementary" — stronger sales message
- GCC hallucination (2:00 AM) is a cautionary tale worth showing in demos
- SharePoint `.md` indexing failure motivates having `.docx`/`.pdf` versions available
- `scripts/` folder created to separate utility scripts from documentation

### Open items
- Retest SharePoint Copilot Studio agent with `.docx` and `.pdf` versions after indexing completes
- Retest GCC MCP agent to determine if hallucination is consistent or intermittent
- Demo dry run with side-by-side comparison
- Update Bicep to include storage private endpoints (still created via CLI, not in IaC)

---

## Session 10 — 2026-03-06

### What was done

#### Copilot Studio Testing — Rounds 5-6 (Prompts 3.2 and 4)

Continued systematic testing across all 11 agent configurations. Full results in `docs/copilot-studio-testing.md`.

**Prompt 3.2: Crystal Price transportation barrier** (MCP agents only)
- Tested: "Crystal Price said she couldn't comply with the treatment plan because she lacked transportation. What support did DSS actually provide?"
- **MCP - GCC: Perfect answer** — found bus passes (monthly), 3 housing referrals, IOP transport offered and declined, compliance numbers (5/12 IOP, 2/8 parenting). Called `get_discrepancies`.
- **Web SPA and MCP - Com: False negatives** — both concluded "no evidence of support" / "no record of support." Neither called `get_discrepancies`. Same GPT-4.1 tool selection failure as Prompt 3.
- Confirmed pattern: GPT-4.1 never calls `get_discrepancies` on contradiction questions; GPT-4o (GCC) consistently does.

**Prompt 4: Skeletal survey fractures** (all 11 agents)
- Tested: "Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey?"
- This is a cross-document conflict: Sheriff Report says "no fractures detected on skeletal survey" (misleading — refers to no *additional* fractures); Medical Records show bilateral femur fracture + spiral humerus fracture on skeletal survey.
- "Skeletal survey" is NOT in the SQL schema — MCP agents cannot surface the conflict.
- **SP/PDF - Com: GOLD STANDARD** — only agent (1 of 11) to catch the cross-document conflict. Found fractures from Court Orders, quoted Sheriff Report's "no fractures" claim, explained it refers to no additional fractures. Two-source cross-reference.
- **7 of 8 document agents repeated the Sheriff Report's incorrect "no fractures" claim** — single source, no cross-reference. An attorney would conclude no fractures existed.
- **Web SPA (MCP): Best MCP response** — found fractures from SQL timeline, correctly distinguished medical vs. law enforcement sources. Could not surface the Sheriff Report conflict (not in SQL).
- **MCP - Com and MCP - GCC (with case #): Honest absence** — correctly said the info isn't in the data.
- **MCP - GCC (without case #): Fabricated a self-contradictory answer** — fixed when case # added.
- New danger category identified: "misleading source faithfully reproduced" — document agents retrieve an inaccurate source document and present it as the definitive answer. Harder to catch than hallucination because the citation checks out.

#### Testing Documentation
- Updated `docs/copilot-studio-testing.md` with full Round 5 (Prompt 3.2) and Round 6 (Prompt 4) results
- Added ground truth sections for Prompts 3.2 and 4
- Updated "no single agent wins" summary table with Prompt 4 column
- Added new danger level to the failure taxonomy: "misleading source faithfully reproduced"

### Key findings (cumulative through 4 prompts)

1. **SP/PDF - Com is the strongest document agent** — gold standard on Prompts 3, 4; no 8 PM error on Prompt 2; strong on Prompt 1
2. **GPT-4.1 never calls `get_discrepancies`** — confirmed across Prompts 3, 3.2, and 4. GPT-4o (GCC) consistently does.
3. **Every agent has a failure mode** — no unconditional winner across all prompts
4. **MCP agents fail responsibly when data is absent** — honest "not in data" vs. document agents repeating incorrect sources
5. **Cross-document conflict detection is extremely rare** — only 1 of 8 document agents caught the skeletal survey conflict

### Decisions made
- Prompt 4 (skeletal survey) is the strongest "you need both structured + unstructured" demo prompt
- Testing methodology: always test with and without case number in prompt for MCP agents
- SP/PDF - GCC status changed from "Pending GCC config" to "Active" (tested successfully)

### Open items
- Additional test prompts for next session (new prompts beyond demo-notes.md)
- Demo dry run with side-by-side comparison
- Update Bicep to include storage private endpoints (still CLI-only)

---

## Session 11 — 2026-03-06

### What was done

#### Copilot Studio Testing — Round 7 (Prompts 5-10, in progress)

Designed 6 new test prompts from `Demo_Comparison_Prompts.md`, one per category:

| # | Demo # | Prompt | Category |
|---|--------|--------|----------|
| 5 | 1.1 | Complete timeline (Case 1, 12 events) | Factual Retrieval |
| 6 | 1.3 | People roster (Case 2, 8 people) | Factual Retrieval |
| 7 | 2.2 | Dena Holloway statement evolution | Cross-Referencing |
| 8 | 4.2 | Statements to law enforcement (Case 1, 4 statements) | Filtering |
| 9 | 5.3 | TPR cases (9 total) | Aggregate |
| 10 | 6.3 | Time gap: thump → ER (5h45m) | Precision |

**Prompt 5 completed across all 11 agents.** Results:

| Agent | Score | Key Issue |
|---|---|---|
| Web | 12/12 | Perfect |
| MCP - Com | 12/12 | Perfect |
| MCP - GCC | 12/12 | Perfect + parties listed per event |
| SP/PDF - Com | 12/12 | 8-10 PM bedtime range, richer medical detail from docs |
| SP/DOCX - Com | 12/12 | 8 PM flat error, fabricated June 12 2:30 PM DSS visit |
| KB/DOCX - Com | 9/12 | Strong investigation, no post-removal events |
| SP/DOCX - GCC | 9/12 | Correct 10 PM, only 1 source doc |
| KB/PDF - GCC | 10/12 | Best KB agent, GAL visit detail, correct 10 PM |
| KB/DOCX - GCC | 8/12 | Good interviews, 1 source doc, no post-removal |
| KB/PDF - Com | 6/12 | Collapsed investigation into 1 summary block |
| SP/PDF - GCC | ~4/12 | **Case 2 cross-contamination** — merged Crystal Price data into Webb timeline |

Key findings from Prompt 5:
- **All 3 MCP agents: 12/12** — structured data makes timeline enumeration trivial
- **SP/PDF - Com matched MCP at 12/12** — continues to be the strongest document agent
- **SP/PDF - GCC worst performer** — cross-contaminated Case 1 with Case 2 data (dangerous for attorneys)
- **8 PM bedtime error** persists in Commercial doc agents; GCC agents (GPT-4o) consistently get 10 PM correct
- **GPT-4o uses "materially changes her account"** — legal phrasing that GPT-4.1 doesn't use
- **KB agents score lower than SP agents** — flat file structure loses document context that SharePoint preserves

#### Executive Summary (draft)
- Created initial `docs/executive-summary.md` — one-page comparison of MCP vs document-backed agents

### Decisions made
- Round 7 testing covers 6 categories (one prompt each) rather than exhaustive testing of all 19 prompts
- Prompt 5 is a strong demo prompt — the 12/12 vs 4/12 contrast is immediately compelling
- Executive summary will be a living document updated after each prompt completes

### Open items
- **Resume testing at Prompt 7** (Statement Evolution: "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?")
- Prompts 7-10 still pending across all 11 agents
- Demo dry run with side-by-side comparison
- Update Bicep to include storage private endpoints (still CLI-only)

---

## Session 12 — 2026-03-06

### What was done

#### Copilot Studio Testing — Prompt 6 (People Roster, all 11 agents)

Tested: "List all people involved in the Price TPR case and their roles."

Ground truth: 8 people in SQL. 4 additional people exist only in documents (Patricia Holloway, Judge Harold Wynn, Michael Patterson, Rebecca Torres).

**Results:**

| Agent | Core (of 8) | Doc-Only Extras | Key Issue |
|---|---|---|---|
| Web SPA | 8/8 | 0 | Clean, complete |
| MCP - Com | 8/8 | 0 | Clean |
| MCP - GCC | 8/8 | 0 | Richest detail (DOBs, notes) |
| SP/PDF - Com | 8/8 | 4 | Best overall — 12 people, 4 sources |
| SP/DOCX - Com | 8/8 | 4 | Matches SP/PDF-Com, summary table |
| KB/PDF - Com | 8/8 | 2 | Solid, mild padding (Notary) |
| KB/DOCX - Com | 8/8 | 2 | Clean, found Rebecca Torres |
| KB/PDF - GCC | 8/8 | 3 | Padding (Unit Supervisor, Notary) |
| SP/PDF - GCC | 5/8 | 2 | Missing children as entries + Thomas Reed |
| SP/DOCX - GCC | 5/8 | 3 | Missing children as entries + Dr. Ellis |
| KB/DOCX - GCC | 7/8 | 3 | Missing Dr. Ellis |

**Key findings:**
- **Zero hallucinated people** across all 11 agents — cleanest prompt so far
- **Commercial doc agents dominated** — all 4 scored 8/8 core; only 1 of 4 GCC doc agents did (KB/PDF)
- **Document agents add genuine value** — 4 real people in docs but not SQL
- **GCC SharePoint agents underperformed again** — both scored 5/8 (same pattern as Prompt 5)
- **GPT-4.1 more thorough at enumeration** than GPT-4o — widest completeness gap of any prompt

#### Copilot Studio Testing — Prompt 7 (Statement Evolution, all 11 agents)

Tested: "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

Ground truth: 3 key changes (9:30 PM thump, Marcus in/near room, rough handling history). Bonus: intermediate case manager progression.

**Results:**

| Agent | Changes (of 3) | Key Detail |
|---|---|---|
| Web SPA | 3/3 | Direct quotes, referenced Discrepancy 6 |
| MCP - GCC | 3/3 | 6 discrepancies enumerated, 4.5-hour delay |
| MCP - Com | **2/3** | **Missing rough handling** |
| SP/PDF - Com | 3/3 | Summary table, fear motive, demeanor shift |
| SP/DOCX - Com | 3/3 | Summary table, "material" legal framing |
| KB/PDF - Com | 3/3 | Grandmother placement wish (unique) |
| KB/DOCX - Com | 3/3 | 3 sources, Medical Records detail |
| SP/PDF - GCC | 3/3 | Demeanor noted |
| SP/DOCX - GCC | 3/3 | "Responsibility and awareness" lens |
| KB/PDF - GCC | 3/3 | 2 sources |
| KB/DOCX - GCC | 3/3 | Most detailed demeanor analysis |

**Key findings:**
- **Strongest consensus yet** — 10/11 found all 3 changes
- **MCP-Com the only miss** — omitted rough handling (comprehension gap, not retrieval)
- **No agent noted intermediate progression** (hospital → case manager → LE)
- **Zero hallucinations** across all 11 agents
- **SP-Com agents surfaced fear motive** ("scared," "didn't want to get anyone in trouble") — unique to sheriff report retrieval

#### Copilot Studio Testing — Prompt 8 (LE Statements Filter, all 11 agents)

Tested: "What statements were made to law enforcement in case 2024-DR-42-0892?"

Ground truth: 4 statements with `made_to = 'Law Enforcement'` in SQL (Marcus Webb ×2, Dena Holloway ×2).

**Critical discovery:** MCP tool `get_statements_by_person` has no `made_to`/audience filter parameter — a genuine API design gap, not a model failure. All 3 MCP agents failed or degraded. This is the **first prompt where document agents strictly outperform MCP**.

**Results:**

| Agent | Score | Key Detail |
|---|---|---|
| Web SPA | **Fail** | Tool lacks audience filter, returned all statements |
| MCP - Com | **Fail** | 3 attempts, all failed (couldn't filter by audience) |
| MCP - GCC | Partial (2/4) | Pivoted to timeline tool, found 2 LE interactions |
| SP/PDF - Com | **Pass** (4/4) | 3 source documents, complete |
| SP/DOCX - Com | **Pass** (4/4) | Identified intermediate interview as unique detail |
| KB/PDF - Com | **Pass** (4/4) | Included DSS follow-up context |
| KB/DOCX - Com | **Pass** (4/4) | Unique Marcus quote from sheriff report |
| KB/PDF - GCC | **Pass** (4/4) | Best GCC agent on this prompt |
| KB/DOCX - GCC | **Pass** (4/4) | No 8 PM error (unlike other GCC agents) |
| SP/PDF - GCC | **Fail** | Returned court testimony instead of LE statements |
| SP/DOCX - GCC | **Fail** | Returned hospital versions of statements |

**Key findings:**
- **First MCP failure mode from tool design** — not model error but missing API capability
- **KB agents swept**: all 4 KB agents (Com + GCC) scored 4/4 — strongest group on this prompt
- **GCC SP agents failed again** — SP/PDF-GCC and SP/DOCX-GCC continued their poor performance streak
- **MCP-GCC showed adaptability** — pivoted to timeline tool when statement tool failed (only MCP agent to partially succeed)

#### Copilot Studio Testing — Prompt 9 (TPR Aggregate Query, all 11 agents)

Tested: "Which cases involve Termination of Parental Rights?"

Ground truth: 9 TPR cases in SQL database. Document agents only have docs for 2 cases (1 CPS, 1 TPR). Fixed ground truth table error — `2024-DR-01-0537` (Union) is Guardianship, not TPR; replaced with `2025-DR-45-0184` (Morris, Richland).

**Results:**

| Agent | TPR Found | Grade | Notes |
|---|---|---|---|
| Web SPA | 9/9 | **Pass** | Concise list with case IDs |
| MCP - Com | 9/9 | **Pass** | Full summaries |
| MCP - GCC | 9/9 | **Pass** | Richest detail |
| SP/PDF - Com | 1/9 | Partial | Also flagged CPS case as potential TPR |
| SP/DOCX - Com | 1/9 | Partial | Statutory citations (§63-7-2570) |
| KB/PDF - Com | 1/9 | Partial | Good detail |
| KB/DOCX - Com | 1/9 | Partial | Accurate within scope |
| SP/PDF - GCC | 1/9 | Partial | Generic framing |
| SP/DOCX - GCC | 1/9 | Partial | Both parents covered |
| KB/PDF - GCC | 1/9 | Partial | GAL detail |
| KB/DOCX - GCC | 1/9 | Partial | Procedural chronology |

**Key findings:**
- **Clearest architectural advantage for MCP** — aggregate queries across 50 cases are trivial with SQL, impossible with limited doc corpus
- **All 8 document agents scored Partial** — found the 1 TPR case in their corpus accurately, but missed 8 others
- **No document agent acknowledged the limitation** — none said "I can only see 2 cases"
- **Zero hallucinations** — no fabricated cases or misclassified types
- SP-Com agents showed value-add by flagging Webb/Holloway (CPS) as potential TPR; SP/DOCX-Com cited actual SC statutory grounds

#### Copilot Studio Testing — Prompt 10 (Time Gap Calculation, all 11 agents)

Tested: "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

Ground truth: 9:30 PM thump → 2:00 AM discovery → 3:15 AM ER admission. Correct gaps: 4h30m (thump→discovery), 5h45m (thump→ER), 1h15m (discovery→ER).

**Results:**

| Agent | Thump | Hospital | Gap | Grade |
|---|---|---|---|---|
| Web SPA | 2:00 AM ❌ | 3:15 AM | 1h15m (wrong start) | **Fail** |
| MCP - Com | 9:30 PM ✓ | 2:00+3:15 AM | 4h30m+5h45m ✓ | **Pass** (gold standard) |
| MCP - GCC | 9:30 PM ✓ | 2:00 AM | ~4h (imprecise) | Partial |
| SP/PDF - Com | 9:30 PM ✓ | 2:00+3:15 AM | ~4.5h ✓ | **Pass** |
| SP/DOCX - Com | 9:30 PM ✓ | 3:15 AM | 5h45m ✓ | **Pass** |
| KB/PDF - Com | 9:30 PM ✓ | "after midnight" | 2.5h (partial) | Partial |
| KB/DOCX - Com | 9:30 PM ✓ | 2:00 AM | ~4.5h ✓ | **Pass** |
| SP/PDF - GCC | 9:30 PM ✓ | **7:30 AM** ❌ | 10h (fabricated) | **Fail** |
| SP/DOCX - GCC | 9:30 PM ✓ | 2:00 AM | ~4.5h ✓ | **Pass** |
| KB/PDF - GCC | 9:30 PM ✓ | 12:47 AM | ~3h17m | Partial |
| KB/DOCX - GCC | 9:30 PM ✓ | ~midnight | ~2.5h (wrong event) | Partial |

**Key findings:**
- **MCP-Com: gold standard** — only agent to identify all 3 milestones and calculate both intervals
- **Web SPA failed despite having the data** — conflated 9:30 PM thump with 2:00 AM discovery (comprehension error, not retrieval)
- **SP/PDF-GCC hallucinated 7:30 AM** — fabricated time, continues worst-agent pattern
- **10/11 agents correctly identified 9:30 PM** — only Web SPA missed it
- **Arithmetic is a genuine weakness** — even correct retrieval doesn't guarantee correct calculation

#### ALL 10 PROMPTS COMPLETE — Testing finished for all 11 agents

#### Documentation Updates
- Updated `docs/copilot-studio-testing.md` with all Prompt 6-10 results and analysis
- Fixed ground truth error in Prompt 9 table (Union/Guardianship → Morris/Richland/TPR)
- Updated `docs/executive-summary.md` — complete 11×10 scorecard, final Win/Loss rankings
- Updated `docs/session-log.md`

### Open items
- Demo dry run with side-by-side comparison
- Update Bicep to include storage private endpoints (still CLI-only)
- Consider adding `made_to` filter to `get_statements_by_person` tool (design gap found in P8)

---

## Session 13 — 2026-03-06

### What was done

#### Executive Summary PDF
- Created `scripts/generate-executive-pdf.py` — Python script using fpdf2 to produce a polished, executive-friendly PDF
- Output: `docs/executive-summary.pdf` (5 pages)
  - Cover page with navy banner, title, scope stats (110 test runs, 11 agents, 10 prompts)
  - Key Findings rewritten in business language (no backtick code refs, no tool names)
  - Color-coded failure severity table, format comparison table
  - Results at a Glance — 10-row summary with plain-English takeaways
  - Agent Scorecard — color-coded Pass/Partial/Fail grid (green/amber/red) + overall rankings
  - Recommendation page with callout box for bottom line
- All technical jargon replaced with executive-friendly language

#### Redemption Round (Round 8) — Testing Doc
- Added **Round 8 — Redemption Round** section to `docs/copilot-studio-testing.md`
- Identified all 24 Fail scenarios across 10 agents (SP/PDF-Com excluded — zero Fails)
- For each of 8 prompt groups, wrote:
  - Original prompt (unchanged, for transience check)
  - Revised prompt (more specific wording, decomposed questions, explicit cross-referencing guidance)
  - Explanation of what changed and why
- Key prompt revision strategies:
  - P1/P3/P5/P6/P8: Added case numbers for retrieval precision
  - P2: "In his own words" + explicit Dena/Marcus attribution warning
  - P4: Changed from yes/no to "compare these two documents" to force cross-referencing
  - P8: Named Lt. Odom, explicitly excluded hospital/DSS/court audiences
  - P10: Decomposed into 3 explicit milestones before asking for calculation
- Empty results table ready for testing

### Decisions made
- Redemption round tests both original and revised prompts — original for transience, revised for fairness
- Prompt 4 is the heaviest retest (7 agents) — should be tested first
- PDF uses fpdf2 (already installed) — no new dependencies needed

### Open items
- **Run all 24 redemption retests** (original + revised prompts for each)
- Update executive summary PDF after redemption results
- Demo dry run with side-by-side comparison
- Update Bicep to include storage private endpoints (still CLI-only)
- Consider adding `made_to` filter to `get_statements_by_person` tool (design gap found in P8)

---

## Session 14 — 2026-03-06

### What was done

#### Executive Summary PDF — Copilot Studio Reframing
- Rebranded PDF from "AI Agent Evaluation" to "Copilot Studio Evaluation" throughout (title, header, cover, body text)
- Broadened scope from legal-only to multi-use-case framework:
  - Cover subtitle: "Across Government Use Cases"
  - New "Use Cases" subsection on The Question page listing both use cases
  - New "Use Case 1: Legal Case Analysis" section header before existing findings
  - New "Use Case 2: Investigative Analytics" page describing Philly Poverty Profiteering workload (34M rows, 14 tools), marked as "testing planned"
  - Recommendation now anchored to "Based on Use Case 1 results" with forward-looking close: "Use Case 2 will test whether this finding holds at scale"
- Fixed em dash encoding errors (Helvetica doesn't support Unicode em dashes)

### Decisions made
- Single authoritative PDF that grows with each use case (not separate PDFs per use case)
- Philly Poverty Profiteering is "Use Case 2: Investigative Analytics" — same MCP/SQL architecture, same Copilot Studio agent configs, much larger dataset
- PDF structure supports adding Use Case 2 results later without restructuring

### Open items
- **Run all 24 redemption retests** (original + revised prompts for each)
- **Run Use Case 2 testing** (Philly Poverty Profiteering across same Copilot Studio agent configs)
- Update executive summary PDF after both sets of results
- Demo dry run with side-by-side comparison
- Update Bicep to include storage private endpoints (still CLI-only)
- Consider adding `made_to` filter to `get_statements_by_person` tool (design gap found in P8)

---

## Session 15 — 2026-03-06

### What was done

#### PII Scrub — Real Names Removed from Git
- Discovered real names from the original SC DSS case (parties, attorneys, caseworker, GAL, child with DOB) committed in 5 files
- Scrubbed all real names from: `docs/architecture.md`, `scripts/sanitize-docs.py`, `CLAUDE.md`, `docs/demo-guide.md`, `docs/faqs.md`
- `sanitize-docs.py` REPLACEMENTS dict emptied — mapping is now local-only (not version controlled)
- Architecture doc mapping table replaced with generic descriptions
- Verified zero real names remain in any committed file via grep
- Real names still exist in git history — BFG Repo Cleaner not yet run (repo is private)

#### Executive Summary PDF — Abbreviation Removal
- Full rewrite of `scripts/generate-executive-pdf.py` to eliminate all abbreviations for C-suite readability
- Key renames: MCP → Structured Data, GCC → Government Cloud, KB → Uploaded, SP → SharePoint, Com → Commercial, Pa → Partial, ER → Emergency Room, DB → database, DOCX → Word
- Dropped Model column from scorecard (redundant with environment label + footnote)
- Added Gov Cloud footnote explaining GPT-4o vs GPT-4.1 mapping

#### Executive Summary PDF — Prompts Tested Page
- Added full "Prompts Tested" table (new page) between scorecard and overall rankings
- Shows all 10 verbatim questions asked + "What It Tests" column
- PDF now 10 pages (was 9)

### Decisions made
- Real→synthetic name mapping is local-only from now on — sanitize script requires manual population
- "Knowledge Base" → "Uploaded" in executive PDF (plainer English for non-technical audience)
- Model column dropped from scorecard — environment label + footnote is sufficient

### Open items
- **Run all 24 redemption retests** (original + revised prompts for each)
- **Run Use Case 2 testing** (Philly Poverty Profiteering across same Copilot Studio agent configs)
- **Consider BFG Repo Cleaner** to purge real names from git history
- Update executive summary PDF after redemption results
- Demo dry run with side-by-side comparison
- Update Bicep to include storage private endpoints (still CLI-only)
- Consider adding `made_to` filter to `get_statements_by_person` tool (design gap found in P8)

---

## Session 16 — 2026-03-07

### What was done

#### Improvements Round 1 — Data and Tool Gap Analysis
- Reviewed all 110 test results across 11 agents and 10 prompts to identify where data or tool additions would improve MCP agent responses
- Cross-referenced every proposed data addition against the source PDF documents to verify nothing was fabricated — all data traces back to specific pages
- Created `docs/improvements/` subfolder with two documents:
  - `improvements-round-1.md` — 5 improvements + data integrity analysis, with SQL/code snippets and document source citations
  - `document-to-database-mapping.md` — guide showing how PDF content maps to each SQL table, illustrating the extraction pipeline from documents to structured data

#### Improvement 1: `made_to` Filter on Statements Tool
- **Problem:** P8 ("What statements were made to law enforcement?") failed for all 3 MCP agents because the tool only filters by `person_name`, not by audience
- **Changes:**
  - `mcp-server/src/mcp/tools.ts` — added optional `made_to` parameter to tool definition; made `person_name` optional; updated `callTool` to pass both params as query string
  - `functions/src/functions/getStatements.ts` — added `made_to` query parameter with LIKE filter; made `person_name` optional (at least one of `person_name` or `made_to` required)
- No schema change needed — `statements.made_to` column already exists

#### Improvement 2: Skeletal Survey Discrepancy + Timeline Event
- **Problem:** P4 ("Did the Sheriff's Office investigation find fractures?") — MCP agents can't answer at all; skeletal survey not in SQL
- **Document sources:** Medical Records pp. 3-4 (radiology report with fractures), Sheriff Report p. 2 ("no fractures detected")
- **Added to `seed.sql` and `seed-expanded.sql`:**
  - 1 timeline event: skeletal survey at 4:07 AM on June 12 with full findings from Dr. David Petrakis
  - 1 discrepancy: Sheriff Report "no fractures detected" vs Medical Records documenting two fractures

#### Improvement 3: 9:30 PM Thump as Standalone Timeline Event
- **Problem:** P10 (time gap calculation) — Web SPA conflated thump with discovery, reported 1h15m instead of 5h45m
- **Document source:** Sheriff Report pp. 6-7 (Dena Holloway's revised statement)
- **Added to both seed files:** 1 timeline event for June 11, 9:30 PM — the thump from Jaylen's room

#### Improvement 4: Individual Drug Test Timeline Events
- **Problem:** P3 ("Crystal Price clean now") — Web SPA received drug test data but failed to recognize narrative text as test results
- **Document sources:** DSS Investigation Report pp. 6-7, TPR Petition p. 4, Court Transcript p. 10
- **Added to both seed files:** 6 timeline events — Oct 8 positive, Oct 22 positive, Dec 5 missed, Jan 15 missed, Mar 3 missed, Apr 10 negative

#### Improvement 5: Nurses in People Table
- **Problem:** P1 (ER admission nurse) — all 3 MCP agents correctly reported "no nurse identified" but the data was in the documents
- **Document sources:** Medical Records p. 8 (Rebecca Torres, RN, BSN), Sheriff Report p. 1 (Patricia Daniels, RN, Charge Nurse)
- **Added to both seed files:** 2 people rows for Case 1
- **Noted:** Rebecca Torres name collision with Case 2's TPR Petition (Rebecca Torres, Esq., DSS Staff Attorney) — different characters, same name

#### Data Integrity Findings
- Marcus Webb bedtime: Sheriff Report p. 3 says 8:00 PM (investigator's paraphrase of LE interview); Medical Records say "around ten" / 22:00. The "8 PM misattribution" from testing isn't purely Dena's statement — Marcus's own LE interview narrative also says 8 PM.
- Dena discovery time: Sheriff Report p. 6 says "approximately midnight" (initial LE statement); Medical Records say 2:00 AM. SQL uses 2:00 AM.
- ER arrival time: Sheriff Report says 0047 (12:47 AM); Medical Records say 3:15 AM. Known intentional discrepancy — working as designed.

### Data counts (updated)
- Case 1: 10 people (+2), 14 timeline events (+2), 15 statements, 7 discrepancies (+1)
- Case 2: 8 people, 16 timeline events (+6), 12 statements, 4 discrepancies
- Total across 50 cases: 277 people, 333 timeline events, 338 statements, 151 discrepancies

### Decisions made
- All data additions validated against source PDFs before implementation — no fabricated data
- Source documents (sharepoint-docs/) are not modified — they are the documents of truth
- Drug test events added as separate INSERT block (not interleaved) for readability
- `person_name` made optional on statements tool — enables audience-only queries ("all statements to law enforcement")
- Skeletal survey discrepancy uses NULL person_a_id/person_b_id (document-vs-document conflict, not person-vs-person)

### Open items
- **Deploy updated seed data** to Azure SQL (enable public access → `node database/deploy-sql.js` → disable)
- **Rebuild and deploy Functions** (`cd functions && npm run build && func azure functionapp publish dss-demo-func --typescript`)
- **Rebuild and deploy Container App** (`docker build` → `docker push` → `az containerapp update`)
- ~~Retest Prompts 1, 3, 4, 8, 10 with MCP agents to verify improvements~~ — DONE (Session 17)
- **Run all 24 redemption retests** (original + revised prompts)
- ~~Update executive summary PDF after retesting~~ — DONE (Session 17)
- Demo dry run with side-by-side comparison
- Update Bicep to include storage private endpoints (still CLI-only)

---

## Session 17 — 2026-03-07

### What was done

#### Deployed All Round 1 Improvements
- **Azure SQL**: Enabled public access via CLI → deployed `seed-expanded.sql` via `node database/deploy-sql.js` → verified counts (277 people, 333 events, 151 discrepancies) → removed firewall rule → disabled public access. All automated via `az sql server update` and `az sql server firewall-rule`.
- **Azure Functions**: Built TypeScript (`npm run build`) → published via `func azure functionapp publish dss-demo-func --typescript`. All 5 functions deployed with updated `getStatements` supporting `made_to` filter.
- **Container App**: Built image in ACR via `az acr build --registry phillymcpacr --image dss-case-agent:latest --file mcp-server/Dockerfile mcp-server/` → updated Container App via `az containerapp update`. No local Docker needed.
- **Health check**: Confirmed healthy at `/healthz`.

#### Post-Improvement Retest — All 3 MCP Agents × 5 Prompts

Retested all 5 prompts targeted by the Round 1 improvements across all 3 MCP agents (15 test runs).

**Results summary: 12 Pass / 2 Partial / 1 Fail** (up from 2 Pass / 5 Partial / 8 Fail)

| Prompt | Before | After | What Fixed It |
|--------|--------|-------|---------------|
| P8 (LE statements) | 0P/0Pa/3F | 3P/0Pa/0F | `made_to` filter on statements tool |
| P4 (skeletal survey) | 0P/0Pa/3F | 3P/0Pa/0F | Skeletal survey timeline event + discrepancy |
| P10 (time gap) | 1P/1Pa/1F | 3P/0Pa/0F | 9:30 PM thump as standalone event |
| P3 (drug tests) | 1P/1Pa/1F | 3P/0Pa/0F | Individual drug test events |
| P1 (ER + nurse) | 0P/3Pa/0F | 0P/2Pa/1F | Nurses in people table (but agents don't call `get_case_summary`) |

**Detailed results per agent:**

| Agent | P1 | P3 | P4 | P8 | P10 |
|-------|----|----|----|----|-----|
| Web SPA | Partial (time ✓, nurse ✗) | Pass (6/6 tests, case ID required) | Pass (both fractures) | Pass (4/4 LE statements) | Pass (4h30m correct) |
| MCP-Com | Partial (time ✓, nurse ✗) | Pass (6/6, original prompt) | Pass (both fractures) | Pass (4/4) | Pass (4h30m correct) |
| MCP-GCC | Fail (2:00 AM hallucination) | Pass (6/6, original prompt) | Pass (both fractures) | Pass (4/4) | Pass (4h30m, case ID required) |

**Key observations:**
1. **Web SPA still can't resolve Case 2 from names** — needs case ID in prompt (P3). Known model reasoning issue.
2. **MCP-GCC still asks for case ID on some prompts** (P1, P10) but not others (P3, P4, P8). Inconsistent orchestrator behavior.
3. **MCP-GCC still hallucinates 2:00 AM ER time** (P1) — GPT-4o faithfulness issue, not a data gap.
4. **P1 nurse gap shifted from data → tool selection** — nurse data is in `people` table via `get_case_summary` but no agent thinks to call that tool for a "who was the nurse" question.
5. **MCP-Com resolved Case 2 from "Crystal Price" alone** (P3) — previously needed case ID. Improvement in orchestrator behavior.
6. **MCP-GCC also resolved Case 2 from name** (P3) — same improvement.

#### Documentation Updates
- Updated `docs/improvements/improvements-round-1.md` with full post-improvement retest results section
- Updated `docs/session-log.md` (this entry)
- Updated executive summary PDF script with Round 1 improvements page
- Updated `MEMORY.md` with deployment status and retest results
- Updated `docs/copilot-studio-testing.md` ground truth sections for affected prompts

### Decisions made
- All 3 deployments (SQL, Functions, Container App) done via CLI — no Portal interaction needed
- SQL public access toggling automated via `az sql server update` + `az sql server firewall-rule create/delete`
- Container App image built in ACR (`az acr build`) — no local Docker dependency
- P1 nurse improvement declared "data gap resolved, tool selection gap remains" — possible next step is enriching `get_case_summary` description

### Open items
- **Run all 24 redemption retests** (original + revised prompts for document agents)
- **Run Use Case 2 testing** (Philly Poverty Profiteering)
- **Consider BFG Repo Cleaner** to purge real names from git history
- Consider enriching `get_case_summary` tool description to mention medical staff/witnesses (P1 nurse gap)
- Demo dry run with side-by-side comparison
- Update Bicep to include storage private endpoints (still CLI-only)

---

## Session 18 — 2026-03-07

### What was done
- **Presenter Guide PDF**: Created `scripts/generate-presenter-guide.py` (fpdf2) generating `docs/ogs-presenter-guide.pdf` — single-page two-column printed guide for demos. Iterated through 4 versions fixing column overflow, margin management, and orphaned word wrapping. Key pattern: `set_col_margins(cx, cw)` dynamically sets `l_margin`/`r_margin` to constrain fpdf2 text wrapping to the active column.

- **Use Case 2: Philly Investigation Documents**: Created 5 investigator-style markdown reports for GEENA LLC and two properties, using live data from the Philly MCP server's 34M-row SQL database:
  - `Entity_Investigation_Report.md` — GEENA LLC portfolio: 194 properties, 178 vacant, $8.6M value, 1,411 violations
  - `Property_Enforcement_File_4763_Griscom.md` — 64 violations, 45 failed, city demolition, assessment decline
  - `Transfer_Chain_Analysis_4763_Griscom.md` — 6-owner chain, two sheriff sales, $146K at 275% FMV
  - `Property_Case_File_2400_Bryn_Mawr.md` — 4,141 sq ft stone colonial, condition 7, 34 violations
  - `Ownership_Financial_History_2400_Bryn_Mawr.md` — Anderson family, WaMu/IndyMac collapse, reverse mortgage foreclosure

- **Comparison Prompts**: Created `Philly_Comparison_Prompts.md` — 10 test prompts with ground truth, expected winners, and design rationale. Prompts 6 and 9 designed to be impossible for document agents (require city-wide aggregation). Prompt 7 designed to favor document agents (institutional failure narrative).

- **PDF Conversion**: Created `scripts/convert-philly-docs.py` — markdown-to-PDF converter using fpdf2. Handles H1-H3, tables, bullets, numbered lists, code blocks, bold metadata, and paragraphs. Added `sanitize_text()` to replace Unicode characters (em dashes, arrows, smart quotes) unsupported by Helvetica. Generated 6 PDFs (5 investigation reports + comparison prompts).

- **Documentation**: Updated architecture.md (Use Case 2 documents section), user-guide.md (Philly comparison setup), faqs.md (Use Case 2 Q&A), session-log.md, MEMORY.md.

### Files created
- `scripts/generate-presenter-guide.py` → `docs/ogs-presenter-guide.pdf`
- `scripts/convert-philly-docs.py`
- `sharepoint-docs/Philly-GEENA-LLC/Entity_Investigation_Report.md` + `.pdf`
- `sharepoint-docs/Philly-GEENA-LLC/Property_Enforcement_File_4763_Griscom.md` + `.pdf`
- `sharepoint-docs/Philly-GEENA-LLC/Transfer_Chain_Analysis_4763_Griscom.md` + `.pdf`
- `sharepoint-docs/Philly-2400-Bryn-Mawr/Property_Case_File_2400_Bryn_Mawr.md` + `.pdf`
- `sharepoint-docs/Philly-2400-Bryn-Mawr/Ownership_Financial_History_2400_Bryn_Mawr.md` + `.pdf`
- `sharepoint-docs/Philly_Comparison_Prompts.md` + `.pdf`

### Decisions made
- Documents written as investigator reports (source-first framing) — looks like data was extracted FROM documents, not the reverse
- Only PDFs for customer-facing demo; markdown kept as source for iteration
- fpdf2 with Helvetica (no Unicode fonts) — requires `sanitize_text()` for special characters
- Two-column PDF layout uses dynamic margin switching pattern for fpdf2

### Open items
- **Run Use Case 2 testing** — 10 Philly prompts across MCP and document-backed agents
- Upload 5 Philly PDFs to SharePoint for document agent testing
- Run all 24 redemption retests (document agents, Use Case 1)
- Consider BFG Repo Cleaner to purge real names from git history
- Demo dry run with side-by-side comparison

---

## Session 19 — 2026-03-07

### What was done
- **Use Case 2 testing started**: Ran Prompt 1 ("How many properties does GEENA LLC own, and what percentage are vacant?") across 5 agents
- **Two new agents introduced**: Investigative Agent (Semantic Kernel + OpenAI) and Foundry Agent (Azure AI Foundry) from the Philly Profiteering web SPA — pro-code agents alongside Copilot Studio for comparison
- **Key finding — ambiguous ground truth**: 5 agents returned 3 different property counts (194, 330, 631). The investigation report says 194, the MCP database returns 631 raw rows or 330 distinct parcels. No single correct answer — "ownership" means different things depending on deduplication and entity network traversal
- **Scoring rubric adapted**: Shifted from "correct vs incorrect" (Use Case 1, synthetic data) to "defensible, sourced answer" (Use Case 2, real data with inherent ambiguity)
- **GCC MCP token limit failure**: Copilot Studio GCC hit OpenAIModelTokenLimit — the MCP tool returned all 631 property rows as raw JSON, overwhelming the context window. Data was visible in tool activity but the model couldn't summarize it
- **Documentation restructured**:
  - `docs/copilot-studio-testing.md` renamed to `docs/use-case-1-testing.md` (executive summary added)
  - Created `docs/use-case-2-testing.md` — new testing doc with 5-agent matrix, adapted scoring rubric, Prompt 1 results
  - Created `docs/executive-summary-combined.md` — "no kidding" C-suite summary covering both use cases, zero abbreviations
  - Test response files reorganized: `docs/test-responses/use-case-1-dss-legal/` and `docs/test-responses/use-case-2-poverty/`

### Prompt 1 results

| Agent | Properties | Vacancy % | Grade |
|---|---|---|---|
| Philly MCP - GCC | Error (token limit) | Error | Fail |
| Philly MCP - Com | 330 distinct parcels | 86.67% | Pass |
| Philly SP/PDF - GCC | 194 (from report) | 91.8% | Pass |
| Investigative Agent (Web SPA) | 631 (raw rows) | ~60% | Partial |
| Foundry Agent (Web SPA) | 631 (raw rows) | 45.3% | Partial |

### Decisions made
- Use Case 2 gets its own testing doc (`use-case-2-testing.md`) rather than folding into Use Case 1
- Pro-code agents (Investigative, Foundry) positioned as epilogue/"what's next" — mic drop showing what custom agent architectures can do beyond Copilot Studio
- Combined executive summary uses zero abbreviations for C-suite readability
- Original `copilot-studio-testing.md` kept alongside `use-case-1-testing.md` during transition

### Open items
- **Run Use Case 2 prompts 2-10** across all 5 agents
- Upload 5 Philly PDFs to SharePoint for document agent testing
- Run all 24 redemption retests (document agents, Use Case 1)
- Consider BFG Repo Cleaner to purge real names from git history
- Demo dry run with side-by-side comparison
- Update Bicep to include storage private endpoints (still CLI-only)
- Consider adding summary/count mode to Philly MCP entity network tool (fixes GCC token limit)

## Session 20 — 2026-03-07

### What was done
- **Use Case 2 testing completed**: Ran all 10 prompts across 7 agents (70 total responses scored)
- **Triage Agent added**: Semantic Kernel team-of-agents pattern (6th agent, later 7th with COM SP/PDF)
- **COM SP/PDF added**: Commercial (GPT-4.1) SharePoint/PDF document agent — 7th agent, run with clean context windows for all 10 prompts
- **Full testing doc written**: `docs/use-case-2-testing.md` now contains ground truth, per-agent results, comparison matrices, and analysis for all 10 prompts plus final scorecard and epilogue

### Final Rankings (70 responses)

| Agent | Pass | Partial | Fail | Rate |
|---|---|---|---|---|
| SP/PDF - Com (GPT-4.1) | 8 | 2 | 0 | 80% |
| MCP - Com (GPT-4.1) | 8 | 0 | 2 | 80% |
| SP/PDF - GCC (GPT-4o) | 8 | 2 | 0 | 80% |
| Foundry Agent | 4 | 1 | 5 | 40% |
| MCP - GCC (GPT-4o) | 2 | 1 | 7 | 20% |
| Investigative Agent | 1 | 2 | 7 | 10% |
| Triage Agent (SK) | 0 | 0 | 10 | 0% |

### Key findings
1. **Address resolution is the #1 failure mode** — 10+ different wrong parcel numbers across agents for 2 addresses. Non-deterministic: same agent gets different parcels for the same address across prompts. Foundry Agent found 45 failed inspections in P2 (correct parcel) and 0 in P8 (wrong parcel) — contradicting itself
2. **GPT-4.1 >> GPT-4o for MCP agents** — COM MCP 80% vs GCC MCP 20%. Same backend, same tools. For document agents the model doesn't change the pass rate (both 80%) but GPT-4.1 produces richer analytical answers
3. **Aggregate queries work; address queries fail** — prompts using entity search or zip codes (P1, P6, P9) all MCP agents pass. Address-based prompts (P2-P5, P7-P8) only COM MCP reliably passes
4. **Low-code beat pro-code** — Copilot Studio COM MCP outperformed all 3 pro-code agents (Foundry 40%, Investigative 10%, Triage 0%)
5. **Document agents are 100% reliable within scope** — both SP/PDF agents scored 8P/2Pa/0F. The 2 Partials are structural (can't do citywide aggregates)
6. **Updated danger taxonomy**: wrong-entity analysis (real data, wrong property), self-contradiction (same agent, opposite answers), wrong-prompt response (agent answers a previous question)

### Decisions made
- Triage Agent (SK team-of-agents) is not demo-ready — 0/10 passes
- Pro-code agents positioned as "sprinkles on top" — supplemental to Copilot Studio comparison
- Address resolution fix is top priority before further testing
- GCC SP/PDF scorecard corrected from 7P/2Pa/1F to 8P/2Pa/0F

### Open items
- **Fix address-to-parcel resolution** in Philly MCP tools (top priority)
- Upload 5 Philly PDFs to SharePoint for document agent testing
- Run all 24 redemption retests (document agents, Use Case 1)
- Consider BFG Repo Cleaner to purge real names from git history
- Demo dry run with side-by-side comparison
- Update Bicep to include storage private endpoints (still CLI-only)
- Consider summary/count mode for Philly MCP entity network tool (fixes GCC token limit)

## Session 21 — 2026-03-08

### What was done

#### Improvements Round 2 — Tool Architecture and Prompt Engineering
- **New `search_properties` Azure Function** — fuzzy address-to-parcel lookup with USPS normalization (STREET→ST, AVENUE→AVE, directional abbreviations). Prefix match first, then contains fallback. Both test addresses resolve correctly (4763 Griscom → 232452100, 2400 Bryn Mawr → 521273000)
- **Entity network summary mode** — `?summary=true` on GET /entities/{entityId}/network returns counts + top 10 + zip distribution instead of all 631 rows. Fixes GCC MCP token overflow on P1
- **Improved tool descriptions** — DSS `get_case_summary` now emphasizes "ALL people involved (nurses, doctors, case workers...)" to fix nurse lookup gap. Philly `get_property_profile` references `search_properties`. `run_query` deprioritized vs dedicated tools
- **System prompt workflow guidance** — Philly MCP: "ALWAYS call search_properties FIRST when given a street address." DSS: Tool Selection Guide directing people questions to `get_case_summary`
- **APIM + Bicep updates** — 3 new operations (searchProperties, searchTransfers, getPropertyTransfers), 12→15 total
- **Both Container Apps redeployed** (Philly MCP + DSS MCP)
- Deployment used staging directory pattern for npm workspaces (documented in MEMORY.md)

#### Round 2 Retesting — 53 test runs
- **Use Case 2**: 50 runs (5 agents x 10 prompts — GCC MCP, COM MCP, IA, FA, Triage Agent)
- **Use Case 1**: 3 runs (3 agents x P1 only)

#### Round 2 Results

| Agent | Round 1 | Round 2 | Change |
|---|---|---|---|
| COM MCP (GPT-4.1) | 8P/0Pa/2F | **10P/0Pa/0F** | **PERFECT SCORE** |
| Investigative Agent | 1P/0Pa/9F | **8P/1Pa/1F** | +7 Pass (biggest improvement) |
| Foundry Agent | 4P/0Pa/6F | **8P/1Pa/1F** | +4 Pass |
| GCC MCP (GPT-4o) | 2P/0Pa/8F | **4P/3Pa/3F** | +2 Pass |
| Triage Agent (SK) | 0P/0Pa/10F | **1P/1Pa/8F** | +1 Pass (still last) |
| Web SPA (UC1 P1) | Partial | **Pass** | Found nurse via get_case_summary |
| MCP-Com (UC1 P1) | Partial | Partial | Still doesn't find nurse |
| MCP-GCC (UC1 P1) | Fail | **Partial** | Found both nurses, wrong time |

#### Documentation Updates
- Created `docs/improvements/improvements-round-2.md` — full improvement details + retest results
- Updated `docs/executive-summary-combined.md`:
  - New "Iterative Improvement Process" section (Rounds 0-2 with pattern for organizations)
  - New "Five Findings That Surprised Us" section
  - Updated UC2 standings table with Round 2 results
  - Updated UC2 results narrative, pro-code section, footer
- Updated `MEMORY.md` with Round 2 results and open items
- Updated `docs/faqs.md` with Round 2 FAQ entry

### Key findings
1. **Address resolution tool was the highest-impact single change** — zero lookup failures for agents that used `search_properties`, vs 87% failure in Round 1
2. **Triage Agent is the control group** — only agent that did NOT call `search_properties`, continued to fail on all address-based prompts, confirming the tool was the fix
3. **COM MCP achieved perfect 10/10** — same data, same model, only tool changes
4. **IA went from 1/10 to 8/10** — most dramatic improvement of any agent in either use case
5. **P6 (top private violators) is systemic** — 4 of 5 agents return government entities. Need `exclude_government` filter
6. **GCC MCP P1 still token overflow** — summary mode built but Copilot Studio may not be passing the parameter

### Decisions made
- Triage Agent retested despite 0/10 Round 1 — results confirm architecture is the bottleneck, not tools
- Total evaluation now at 248 test runs across 2 improvement rounds
- "Five Findings That Surprised Us" positioned as executive-friendly highlight section

### Open items
- **Round 3 candidates:** GCC MCP P1 (verify summary param), P6 (exclude_government filter), MCP-Com nurse (role="Witness" vs "Nurse")
- **Triage Agent architecture fix:** sub-agents need system prompt with address resolution workflow
- Upload 5 Philly PDFs to SharePoint for document agent testing
- Run all 24 redemption retests (document agents, Use Case 1)
- Consider BFG Repo Cleaner to purge real names from git history
- Demo dry run with side-by-side comparison
- Regenerate executive summary PDF with Round 2 results

## Session 22 — 2026-03-07

### What was done

#### Triage Agent Round 2 Take 2 Retesting
- Retested the Triage Agent (Semantic Kernel team-of-agents) on all 10 Use Case 2 prompts after sub-agent improvements made in a separate session
- Sub-agent improvements included: improved system prompts, routing logic, and `search_properties` integration into sub-agents
- **Score improvement: 1P/1Pa/8F → 6P/2Pa/2F** — the largest single-round improvement for the Triage Agent
- Full trajectory across 3 rounds: 0P/0Pa/10F (R1) → 1P/1Pa/8F (R2 T1) → 6P/2Pa/2F (R2 T2)
- Results file: `docs/test-responses/use-case-2-poverty/retests-semantic-kernel-triage-agent-take-2.txt`

#### Per-prompt results
- **Now passing:** P1 (330 props/87%), P2 (correct parcel via search_properties), P4 (perfect 6-owner chain), P7 (correct parcel, full bank narrative), P8 (45 failed, CLIP investigator), P10 (174.7% premium)
- **Partial:** P5 (hedges on FMV source), P6 (recognizes govt vs private but doesn't auto-filter)
- **Still failing:** P3 (wrong parcel despite P2/P4 resolving correctly — non-deterministic), P9 (blank response — regression from Take 1's partial)

#### Round 3 Improvement Candidates Identified
1. Mandate `search_properties` in ALL sub-agent system prompts (fixes P3 parcel mismatch)
2. Add FMV field documentation to `get_property_transfers` tool description (fixes P5)
3. Add `exclude_government` parameter to `get_top_violators` tool (fixes P6)
4. Debug P9 blank response — investigate sub-agent timeout/crash
5. Parcel caching in triage loop — pass resolved parcels between sub-agents

#### Documentation Updates
- Updated `docs/use-case-2-testing.md` with Round 2 retesting section, updated Final Scorecard, updated narratives throughout
- Updated UC2 rankings to reflect latest results across all rounds
- Total evaluation now at 133 scored responses (70 R1 + 53 R2T1 + 10 R2T2)

### Key findings
1. **Iterative improvement works across all architectures** — tool descriptions, system prompts, and data enrichment are all legitimate agent development activities that produce measurable results
2. **`search_properties` integration into sub-agents was the key fix** — prompts where sub-agents used it passed; prompts where they didn't (P3) still fail
3. **Non-deterministic resolution persists** — P3 gets the wrong parcel despite P2 and P4 resolving correctly in the same session, showing that sub-agent state is not shared
4. **P9 blank response is a regression** — Take 1 got a partial (right direction, no numbers); Take 2 returned nothing. Likely a timeout or crash in the sub-agent loop
5. **Triage Agent is no longer last** — at 6P/2Pa/2F, it now outperforms GCC MCP (4P/3Pa/3F)

### Decisions made
- This is an iterative improvement cycle — each round identifies specific tool/prompt gaps, fixes them, and retests
- Triage Agent moved from "not demo-ready" to "conditionally demo-ready" — 6/10 passes with known gaps
- Round 3 candidates are specific and scoped (5 items), not architectural overhauls

### Open items
- **Round 3 candidates:** Mandate search_properties in all sub-agent prompts (P3), FMV field docs (P5), exclude_government filter (P6), debug P9 blank response, parcel caching
- **Carry-forward:** GCC MCP P1 token overflow, MCP-Com nurse lookup, upload Philly PDFs to SharePoint, UC1 redemption retests
- Regenerate executive summary PDF with Round 2 Take 2 results
- Consider BFG Repo Cleaner for git history
- Demo dry run

---

## Session 22 — 2026-03-08

### What was done

#### Round 2 Take 3: Triage Agent Retests (P3, P5, P6, P9)
- **P3 (Assessment 2017 vs today): PARTIAL** — correct parcel + current value ($24,800), but claims flat since 2017. Ground truth: $37,200 decline to $24,800.
- **P5 ($146K FMV origin): PASS** — clean retrieval of $53,155.20 from transfer record, no hedging
- **P6 (Top 5 private violators): Initially FAIL (hallucinated fake entities), then PASS after prompt fix** — moved excludeGovernment instruction to top of ViolationAnalyst prompt, added few-shot example, added "NEVER fabricate" rule
- **P9 (Zip 19104 vs 19132): Initially PARTIAL (no numbers), then PASS after full deploy** — exact numbers: 19104 21.1%/59.8%, 19132 22.0%/62.1%
- **Triage final score: 9P/1Pa/0F** (was 6P/2Pa/2F)

#### Round 2 Take 3: Non-Triage Retests (IA, Foundry, GCC MCP)
Tested P5 (FMV) and P6 (excludeGovernment) on agents that had prior failures/partials:
- **IA P5: FAIL → PASS** — $53,155.20, correct parcel and parties
- **IA P6: PARTIAL → PASS** — GEENA LLC #1 with 1,411. Richest P6 response of any agent (failed counts, vacancy, demolitions per entity)
- **Foundry P5: FAIL → PASS** — $53,155.20, correct parcel and parties
- **GCC MCP P5: FAIL → FAIL** — GPT-4o could not execute ("I'm not sure how to help")
- **GCC MCP P6: PARTIAL → FAIL** — GPT-4o could not execute. Regression.

#### Updated Final Standings
| Agent | Score | Change |
|-------|-------|--------|
| COM MCP (GPT-4.1) | 10P/0Pa/0F | unchanged (PERFECT) |
| Investigative Agent (GPT-4.1) | 10P/0Pa/0F | was 8P/1Pa/1F — **NOW PERFECT** |
| Foundry Agent (GPT-4.1) | 9P/1Pa/0F | was 8P/1Pa/1F |
| Triage Agent (GPT-4.1) | 9P/1Pa/0F | was 6P/2Pa/2F |
| SP/PDF - GCC (GPT-4o) | 8P/2Pa/0F | unchanged |
| SP/PDF - Com (GPT-4.1) | 8P/2Pa/0F | unchanged |
| GCC MCP (GPT-4o) | 4P/2Pa/4F | was 4P/3Pa/3F (P6 regressed) |

#### Documentation Updates
- Updated `docs/use-case-2-testing.md` with Take 3 results, non-Triage retests, model gap analysis, updated scorecard and by-prompt table
- Updated `docs/executive-summary-combined.md` with final UC2 results, rewrote Finding #2 (Triage 0→9 story), updated pro-code section, model gap narrative
- Updated `scripts/generate-executive-pdf.py` — replaced UC2 placeholder with real results table and findings
- Updated `scripts/generate-presenter-guide.py` — new 3 Messages (model gap, data, iteration), UC2 rankings, updated findings and feedback loop
- Regenerated both PDFs: `docs/executive-summary.pdf`, `docs/ogs-presenter-guide.pdf`
- Total evaluation: 274 test runs (UC1: 128, UC2: 146)

### Key findings
1. **The model gap is the defining result of Round 2.** GPT-4.1 agents average 9.5/10. GPT-4o agent: 4/10. Same tools, same data, same backend. The tool improvements that produced perfect scores for GPT-4.1 had zero effect on GPT-4o.
2. **Prompt placement matters as much as prompt content.** P6 excludeGovernment instruction existed in the ViolationAnalyst prompt but was buried — the model ignored it. Moving it to the top + adding a few-shot example + "NEVER fabricate" fixed it immediately.
3. **P6 regression (PARTIAL → FAIL → PASS) is a cautionary tale.** The initial sub-agent prompt changes caused the model to hallucinate fake entity names instead of honestly acknowledging government dominance. The fix required three specific prompt engineering techniques (placement, few-shot, explicit prohibition).
4. **Two agents achieved perfect 10/10:** COM MCP and Investigative Agent. Both use GPT-4.1, both benefit from tool improvements, both produce detailed analytical responses.
5. **The Triage Agent's 0→9 trajectory is the strongest evidence that iterative improvement works** — even for the most complex multi-agent architecture.

### Decisions made
- Round 2 testing is complete — diminishing returns for GPT-4.1 agents
- GCC MCP performance (4/10) is a platform constraint, not an engineering problem
- All docs and PDFs updated for demo readiness

### Open items
- Triage P3 (assessment history) — only remaining PARTIAL, low priority
- UC1 redemption retests (document agents) — carry-forward
- Upload Philly PDFs to SharePoint — carry-forward
- Demo dry run with updated materials
- Consider BFG Repo Cleaner for git history

## Session 24 — 2026-03-08

### What was done

#### Five-Level Accuracy Framework
Developed and documented a five-level accuracy spectrum for government AI use cases:
- **Level 1: Discovery** — find documents (low stakes, zero engineering)
- **Level 2: Summarization** — condense reports (document agents score 8/10 with zero customization)
- **Level 3: Operational** — aggregate queries (MCP starts outperforming documents)
- **Level 4: Investigative** — cross-referencing, timelines, discrepancies (inflection point: model gap + tool gap)
- **Level 5: Adjudicative** — legal case preparation (trust but verify, non-negotiable human review)

#### Three Demo Deliverables Created
1. **Executive summary** (`docs/sources/executive-summary.md`) — rewritten around 5-level framework with cross-use-case evidence table, GCC-specific recommendations, and code investment spectrum
2. **Presenter guide** (`docs/demo-guide.md`) — rewritten with 5-level narrative arc, 50-60 minute timing, expanded to include both use cases, side-by-side comparison, and Philly property demo
3. **Slide outline** (`docs/slide-outline.md`) — 20 slides covering framework, evidence, gaps, iteration process, findings, and recommendations

#### PDF Regenerated
- `scripts/generate-executive-pdf.py` — completely rewritten with 5-level framework content, level color badges, danger taxonomy table, iterative improvement results
- `docs/executive-summary.pdf` — regenerated (10 pages)

#### Docs Reorganization
- Created `docs/archive/` — moved testing docs, improvements, and test-responses
- Created `docs/sources/` — moved executive-summary.md (source for PDF) and erd.mmd (source for PNG)
- Updated `docs/README.md` — new structure with Deliverables, Reference, Sources, Archive sections
- Only deliverable PDFs and actionable docs remain in the top-level docs/ folder

### Decisions made
- 5-level framework replaces the old "MCP vs SharePoint" framing for demos
- Demo target: 50-60 minutes with both use cases and side-by-side comparison
- The framework narrative is: "match your investment to your accuracy requirement"
- Labels: Discovery, Summarization, Operational, Investigative, Adjudicative

### Open items
- Build PowerPoint deck from slide-outline.md
- Demo dry run with 5-level narrative (50-60 min)
- Update ogs-presenter-guide.pdf with new framework (currently outdated)
- Triage P3 (assessment history) — carry-forward
- Upload Philly PDFs to SharePoint — carry-forward
- Consider BFG Repo Cleaner for git history

## Session 25 — 2026-03-08

### What was done
- Organized O'G's raw demo talking points into demo-guide.md and slide-outline.md
- **Demo guide updates:**
  - New opening hook ("you may remember me from such demos as...")
  - "What it is / isn't" framing added to intro
  - "No way to avoid getting technical" transition line at Act 3
  - Human review thread (email, code, agents) added to Level 5 section
  - "So what? Do we give up?" close with personal practice story
  - M365 orchestration visibility talking point in expanded sections
  - Data engineering story added to Appendix A
  - New Appendix D: Copilot Studio value prop for tech series
  - Appendix D (What Not to Say) renumbered to Appendix E
- **Slide outline updates:**
  - Speaker notes on Slides 1, 2, 9, 20 with narrative beats
  - New Slide 14: Why Copilot Studio (tech series)
  - Renumbered to 21 slides
- **Executive summary updates:**
  - Added "Why Copilot Studio" section under Code Investment Spectrum
  - Sharpened Finding #2 with cost asymmetry framing
  - Deleted unused `docs/sources/executive-summary.md` (PDF script is source of truth)
- Regenerated both PDFs (executive-summary.pdf: updated, demo-guide.pdf: 12 pages)
- SWA deployed to production

### Decisions made
- `docs/sources/executive-summary.md` deleted — Python script is the sole source of truth for the PDF
- Copilot Studio value prop is a MUST for tech series audience
- Opening hook ties this demo to the delegation demo via "accuracy" as common thread

### Open items
- Build PowerPoint deck from slide-outline.md (21 slides)
- Demo dry run with new opening hook and closing (50-60 min target)
- Fill in second demo reference in opening hook ("you may remember me from...")
- Upload Philly PDFs to SharePoint — carry-forward
- Consider BFG Repo Cleaner for git history

## Session 25b — 2026-03-08

### What was done
- **Triage P3 (assessment history) confirmed PASS** — O'G manually tested, agent resolved address to parcel 232452100, returned assessment values across multiple years with trend narrative
- Triage Agent final score: **10P/0Pa/0F** (was 9P/1Pa/0F) — PERFECT, matching COM MCP and Investigative Agent
- Updated all docs, PDFs, and MEMORY.md with corrected Triage score
- Total test run count: 305 (was 304)

### Decisions made
- Triage P3 no longer a carry-forward item
- Three agents now at perfect 10/10: COM MCP, Investigative Agent, Triage Agent

### Open items
- Build PowerPoint deck from slide-outline.md (21 slides)
- Demo dry run with new opening hook and closing (50-60 min target)
- Fill in second demo reference in opening hook ("you may remember me from...")
- Upload Philly PDFs to SharePoint — carry-forward
- Consider BFG Repo Cleaner for git history

## Session 26 — 2026-03-08

### What was done
- **Executive summary PDF review and update** (9 pages -> 13 pages)
- Fixed "Azure OpenAI" -> "Pro-code agents" in model table (platform column described hosting, not agent type)
- Rewrote Tool Gap section with C-suite examples: users type "Griscom Street," database stores "GRISCOM ST," every downstream answer confidently wrong
- Replaced "fuzzy matching" language throughout with "address normalization" (tool uses USPS abbreviation expansion + SQL LIKE, not Levenshtein)
- Added two Level 5 examples: fentanyl false negative (agent had the data, missed the answer) and 8 PM misattribution (mother's statement attributed to father)
- Added "agent accelerates the human" paragraph to cover page below stats bar
- Rewrote danger taxonomy row 2: "source document that itself contained an error" -> "source whose characterization was misleading in isolation"
- Added GPT-5 Auto / M365 Copilot footnote to cross-use-case results table
- Rewrote "Fix the Data" with concrete examples (narrative fentanyl text -> 6 discrete events)
- Added "Improving Document Agents" subsection to iterative process
- Spelled out "Copilot Studio" in improvement table, added M365 Copilot row
- Split code investment table: Copilot Studio + SharePoint (Levels 1-3) vs Copilot Studio + MCP (Levels 1-4 Com, 1-3 GCC)
- Added Appendix: 11 UC1 agents + 8 UC2 agents with platform descriptions

### Decisions made
- "Fuzzy matching" retired as terminology in exec summary -- tool does normalization, not string distance
- Copilot Studio + MCP qualifies for Level 4 (Commercial with GPT-4.1 scored 10/10 on investigative prompts)
- Other PDF generators (demo-guide, faqs, slide-outline) flagged for future consistency pass on "fuzzy" language

### Open items
- Build PowerPoint deck from slide-outline PDF (21 slides)
- Demo dry run with 5-level narrative (50-60 min target)
- Upload Philly PDFs to SharePoint
- Consistency pass on other PDF generators (fuzzy -> address normalization)
- Consider BFG Repo Cleaner for git history

## Session 27 — 2026-03-08

### What was done
- **Document agent improvement round (Round 4)** — cross-reference headers as zero-code retrieval fix
- Created `sharepoint-docs/Case-2024-DR-42-0892 (R1 - Cross-Referenced)/` with all 6 case documents
- Added "Case File Cross-Reference" blockquote to top of each document listing all related documents and their key topics
- Added inline annotation to Sheriff Report line 49 ("no fractures detected") pointing to Medical Records for complete radiology findings
- Added inline annotation to Medical Records Radiologist Impression #5 clarifying "no additional fractures" scope
- Generated PDF and DOCX from cross-referenced MDs using existing converter
- **A/B testing: GCC document agent**
  - Original Prompt 3.3: 1 reference (Court Orders only), vague "non-accidental trauma" answer
  - Cross-referenced Prompt 3.3: 2 references (DSS + GAL), detailed medical findings + parental inconsistencies
  - Both skeletal survey prompts: correct answer on both versions (secondary sources)
- **A/B testing: Commercial document agent**
  - Original Prompt 3.3: **WRONG CASE** — retrieved Price TPR docs, talked about drug paraphernalia
  - Original skeletal survey: **TOTAL FAILURE** — "no information found" after 5-6 attempts
  - Cross-referenced Prompt 3.3: 4 references (Medical Records, GAL, DSS, Sheriff Report), gold standard response
  - Cross-referenced skeletal survey: Medical Records as primary source, complete radiology findings
  - **0/2 to 2/2 with zero content changes**
- Updated executive summary: expanded "Improving Document Agents" with A/B evidence, updated test count 305 -> 313, 6 -> 7 testing rounds
- Updated demo guide: added "Document Improvement" beat to Act 4 (Level 5), added A/B result to Appendix C Q4, added cross-reference stat to Key Stats table, updated test count
- Updated slide outline: added document improvement bullets to Slide 9 (Level 5), updated test count
- Regenerated all 3 PDFs (executive-summary, demo-guide, slide-outline)
- Total evaluation: **313 test runs** across 7 testing rounds and 4 rounds of iterative improvement

### Key finding
- Cross-reference headers are the highest-ROI document agent improvement: zero code, zero content changes, any paralegal can implement, and the Commercial agent went from catastrophic failure to gold standard responses

### Decisions made
- Cross-referenced docs live in a parallel directory for A/B comparison (not replacing originals)
- "R1 - Cross-Referenced" naming convention for document improvement rounds
- Test count: 305 + 8 new doc retest runs = 313

## Session 28 — 2026-03-08

### What was done
- **Summary PDF overhaul** (formerly "executive summary")
  - Renamed `executive-summary.pdf` → `summary.pdf` across all files
  - Renamed series title: "AI Agent Accuracy Spectrum" → "Agent Accuracy Spectrum for Copilot Studio"
  - Added subtitle: "A five-level framework for measuring AI agent accuracy / with a comparative look at pro-code agent architectures"
  - Renamed "AI Foundry Agent" → "Foundry Agent" throughout
  - Fixed `body_text` and `bullet` bold_lead alignment (fpdf2 markdown mode)
  - Fixed `callout_box` to auto-size height with equal padding
  - Added clickable Table of Contents (page 2) with internal PDF links
  - Added "Data Gap" subsection to Level 4 (structured data not extracted from documents)
  - Added Level 5 "Recommendation:" paragraph for consistency
  - Added "Reminder" callout box at end of Level 5
  - Model Gap: clarified gap only applies to structured data agents (doc agents 8/10 on both models)
  - Level 3: credited both MCP and pro-code agents for outperforming doc agents
  - M365 Copilot now shows "MCP" in all tables where Copilot Studio agents do
  - Custom Web App labeled "(pro-code / MCP Chat)" — identified as UC1 pro-code agent
  - All pro-code agents use consistent pattern: "(pro-code / <framework>)"
  - Commercial rows show "GPT-4.1 / GPT-5 Auto" inline instead of footnote
  - Danger taxonomy table: added 4th column (Example from Testing), auto-sizing rows, centered Failure Mode
  - Data Gap, Tool Gap, Level 5: replaced wordy paragraphs with compact tables
  - Tool Gap table: added Copilot Studio MCP (Commercial + GCC) before/after scores
  - Iterative Process restructured: Round 0 baseline → Improving Document Agents → Improving Structured Data Agents
  - Document improvement section: added before/after table, tightened text
  - Structured data rounds: condensed to one-liners
  - GCC section: added "Option 1: Improve document quality" before existing options
  - Five levels table: aligned Level centered, Name/Stakes/Example left-aligned
  - Model gap table: Platform column left-aligned
  - Fixed baseline stat: "11 + 7" → "11 + 8" (180 → 190 baseline test runs)
  - Stubbed Round 2 for document agents: topics, metadata tags, cloud flows (planned)
- Regenerated all 6 PDFs (summary, demo-guide, slide-outline, user-guide, faqs, architecture)
- Deleted old `docs/pdf/executive-summary.pdf`

### Decisions made
- "Summary" not "Executive Summary" — document stands alone, not summarizing something longer
- Series title includes "for Copilot Studio" — positions for the platform without being exclusive
- Pro-code agents use "(pro-code / <framework>)" pattern in tables
- Custom Web App is a distinct pro-code agent (UC1), not the same as UC2 pro-code agents
- Document agent Round 2 (topics, metadata, cloud flows) is first priority for next session — test both GCC and Commercial

### Next session priorities
1. **Document agent Round 2**: Configure Copilot Studio topics, SharePoint metadata tags, and Power Automate cloud flows to test whether platform configuration can push document agents past 8/10 — test both GCC and Commercial

## Session 29 — 2026-03-08

### What was done
- **Summary PDF refinements** (continued from Session 28)
  - "one day of engineering" → "30 minutes of engineering" (tool gap section + finding #2)
  - "A pro-code agent challenged its own premise" → "An advanced agent" (Foundry Agent is not pro-code)
  - GCC Model Gap Option 3: added Foundry Agent explicitly as zero-to-low-code path before custom agents
  - Bolded "When Government Cloud gains access to more capable models, every Copilot Studio agent improves overnight." in Why Copilot Studio section
  - Fixed fpdf2 `--` underline bleed: "-- no configuration changes" → "with no configuration changes"
  - Enabled `markdown=True` on all `body_text` calls (was only on bold_lead paths)
  - Reduced whitespace between Code Investment Spectrum and Why Copilot Studio (`ln(4)` → `ln(2)`)
  - Added "* Ranked by score" footnotes below all 5 score-ranked tables (model gap, tool gap, cross-use-case results, UC1 appendix, UC2 appendix)

### Decisions made
- "30 minutes" more accurately represents the search_properties tool engineering effort
- Foundry Agent is "advanced" not "pro-code" — zero-to-low code via portal or SDK
- Score-ranked table footnotes go below the table with `*` prefix, not above in parentheses

## Session 30 — 2026-03-08

### What was done
- **Cross-PDF consistency audit** — compared all 6 PDF generator scripts against the overhauled summary
- **Summary PDF bug fixes**
  - "305 test runs" → "313 test runs" in danger taxonomy intro
  - "six testing rounds" → "seven testing rounds" in evidence section intro
  - M365 Copilot labeled as "M365 Copilot (Com)" / "M365 Copilot Commercial" across all tables and footnotes
- **Demo guide updates (6 changes)**
  - Cover: added Responsible AI callout ("The agent accelerates the human...")
  - Key Stats table: added M365 Copilot Com (2/10), iterative improvement (0-1/10 → 10/10), changed "GPT-4.1 agents (Levels 3-5)" → "GPT-4.1 agents (structured data)", added "7 rounds"
  - Act 2 Level 3: added "agents with structured data access, including both Copilot Studio MCP agents and pro-code agents"
  - Act 3 model gap: added "Among agents with structured data access" qualifier with pro-code mention
  - New section: **The Iterative Process** — 4 rounds breakdown, improvement results table, document agent improvement table, pattern for organizations (demo guide now 20 pages)
  - Q&A: "6 rounds" → "7 rounds"
  - M365 Copilot → M365 Copilot (Com) in architecture matrix and key insight
- **FAQs updates**
  - Triage FAQ: reframed from "barely improved 0→1" to full 5-round improvement arc ending at 10/10
  - Triage 0/10 FAQ: reframed as "start at 0/10" with improvement story
  - New section: **M365 Copilot (Commercial)** — 3 Q&As (performance, why worse, what it's good for)
  - New section: **Iterative Improvement** — 2 Q&As (how many rounds, pattern for organizations)
  - Data Improvements FAQ: 110 → 190 baseline test runs across 19 agents
- **Slide outline update**
  - Slide 5 (Level 3): "Model Context Protocol connects AI..." → "Agents with structured data access -- both Copilot Studio MCP and pro-code -- start outperforming document agents here"
  - M365 Copilot labeled as "(Com)" in model gap and code spectrum tables
- **Architecture update**
  - M365 Copilot labeled as "(Com)" in agent table and zero-code description
- **Baseline count fix**: demo guide Round 0 and FAQs both updated from 110 → 190 (11 + 8 agents x 10 prompts)
- Regenerated all 5 updated PDFs (summary, demo-guide, faqs, slide-outline, architecture)

### Decisions made
- M365 Copilot always labeled "(Com)" or "Commercial" to leave room for a future GCC M365 Copilot agent
- "Agents with structured data access" is the umbrella term for Copilot Studio MCP + pro-code agents (replaces bare "MCP agents")
- Demo guide gets a dedicated Iterative Process section (not just scattered mentions) — mirrors the summary's structure
- Baseline test count is 190 (11 UC1 + 8 UC2 agents x 10 prompts each), not 110 (which was UC1 only)

### Next session priorities
1. **Document agent Round 2**: Configure Copilot Studio topics, SharePoint metadata tags, and Power Automate cloud flows to test whether platform configuration can push document agents past 8/10 — test both GCC and Commercial

## Session 29 — 2026-03-08

### What was done
- **PowerPoint deck generated** from slide outline PDF
  - New script: `scripts/generate-slide-deck.py` (python-pptx)
  - Output: `decks/agent-accuracy-spectrum.pptx` — 21 slides, widescreen 16:9
  - Navy/blue branding with 5-level color bar (green-to-red) on content slides
  - Tables: Five Levels, Results After Iteration, Code Spectrum, What to Do at Each Level
  - Visuals: horizontal bar chart (model gap), before/after cards (tool gap), split-screen (Level 5 sheriff vs medical), danger taxonomy severity pills, three big number cards (bottom line), decision tree (GCC), iterative process rounds
  - Speaker notes included on slides 1, 2, 7, 8, 9, 14, 20
  - New `decks/` folder for presentation outputs

### Decisions made
- PowerPoint generator follows same pattern as PDF generators (self-contained Python script, hardcoded content)
- Deck stored in `decks/` (separate from `docs/pdf/` which is for reference PDFs)

### Next session priorities
1. **Document agent Round 2**: Configure Copilot Studio topics, SharePoint metadata tags, and Power Automate cloud flows to test whether platform configuration can push document agents past 8/10 — test both GCC and Commercial

## Session 30 — 2026-03-08

### What was done
- **Summary PDF refinements** (continued from sessions 28/29)
  - **Tool Gap table**: Redesigned to match Data Gap table format (Issue / User Input / In Database / Agent Result). Removed duplicate before/after agent scores (now only in Iterative Process). Single row focused on address resolution.
  - **Data Extraction Options table**: Moved from inline (Data Gap section) to its own appendix page with TOC entry and intro paragraph
  - **Bold formatting**: Bolded "GPT-4o (Government Cloud) and GPT-4.1 (Commercial) performed identically at this level" in Level 1-2 section
  - **Removed Level 5 reminder callout box** (redundant with content above)
  - **Round 0 baseline testing**: Removed standalone section, distributed into each improvement subsection — Document Agents Round 0 (12 configs, 120 runs) and Structured Data Agents Round 0 (7 configs, 70 runs)
  - **Fixed fpdf2 markdown strikethrough bug**: All `--` in rendered text was being interpreted as strikethrough markers by fpdf2's `markdown=True`. Replaced 11 instances with periods, commas, or semicolons throughout the document
  - **Renamed section**: "What Government Cloud Customers Should Do" → "Government Cloud (GCC) Options" (TOC + heading)
  - **Split Option 3**: Separated Foundry Agent (zero to low code) from fully custom agent (maximum control) into Options 3 and 4. Now 5 options total.
  - **Added transition text**: Setup sentence before options ("five practical paths forward today") and transition paragraph after options leading into Code Investment Spectrum

### Decisions made
- `--` should never appear in text rendered with fpdf2 `markdown=True` (triggers strikethrough)
- Tool Gap and Data Gap tables share same column structure for visual continuity
- Round 0 baseline belongs in each improvement subsection, not as a standalone section

### Next session priorities
1. **Document agent Round 2**: Configure Copilot Studio topics, SharePoint metadata tags, and Power Automate cloud flows to test whether platform configuration can push document agents past 8/10 — test both GCC and Commercial

## Session 31 — 2026-03-09

### What was done
- **SP/PDF - GCC full 10-prompt retest with cross-referenced documents**
  - Cross-reference headers added in prior session (zero content changes, just document hygiene)
  - **Result: 3/10 → 7/10 (cross-refs) → 8/10 (+ metadata tags)** — worst agent in the entire test set now tied with Commercial SP/PDF at 8/10
  - Prompt-by-prompt results:

| Prompt | Before | After | Change |
|--------|--------|-------|--------|
| P1 (ER time + nurse) | Pass | Pass (now found Rebecca Torres) | — |
| P2 (Marcus Webb) | Fail | Partial → Pass (after metadata tags) | +2 |
| P3 (Crystal Price) | Partial | Pass (specific dates, missed screens) | +1 |
| P4 (Skeletal survey) | Fail | Pass (both fractures, 2 sources) | +2 |
| P5 (Timeline) | Fail | Pass (10+ events, zero case contamination) | +2 |
| P6 (People) | Fail | Partial (7/8, missing Thomas Reed) | +1 |
| P7 (Dena statements) | Pass | Pass (3/3 changes) | — |
| P8 (LE statements) | Fail | Pass (both parents, full detail) | +2 |
| P9 (TPR cases) | Partial | Partial (structural doc limitation) | — |
| P10 (Time gap) | Fail | Pass (9:30 PM → 3:15 AM = 5h45m) | +2 |

- **KB/PDF - GCC retest with cross-referenced documents** (2 prompts)
  - General skeletal survey prompt: Pass — full fracture detail, Medical Records source
  - Sheriff's Office trap prompt: Pass — "Yes, fractures found," 2-source cross-reference
- **SP/PDF - Com and SP/PDF - GCC retests from prior session** (doc-retest-1-com.txt, doc-retest-1.txt) documented
  - Commercial: 0/2 → 2/2 (total failure → perfect, 4 sources)
  - GCC: vague → detailed multi-source analysis
- **SharePoint metadata tags** added to Medical_Records.pdf (document topics/keywords)
  - P2 retested: Partial → Pass — agent now retrieves Medical Records nursing notes for parent statement queries
  - SP/PDF - GCC now at **8/10** (tied with SP/PDF - Com)
- **Copilot Studio system instruction tested** ("source hierarchy: Medical Records > Court Filings > ...")
  - No effect on P2 — the problem was retrieval, not reasoning. Metadata tags fixed it instead.
- **Updated all PDF generators and slide deck** with 3/10 → 8/10 results
  - `generate-executive-pdf.py`: Cross-use-case table, Round 0 baseline, full retest paragraph, GCC Options, UC1 appendix
  - `generate-demo-guide-pdf.py`: Key stats table, document improvement table, A/B result narrative
  - `generate-slide-outline-pdf.py`: GCC bullet updated
  - `generate-slide-deck.py`: Added GCC 3/10→7/10 bullet
- Regenerated all 4 outputs (summary.pdf, demo-guide.pdf, slide-outline.pdf, agent-accuracy-spectrum.pptx)

### Decisions made
- SP/PDF - GCC score updated from 3/10 to "3/10 to 8/10" (showing before/after) in all tables
- Document improvement table rows now both show 0/2 → 2/2 (GCC was previously "Vague → Detailed")
- GCC Options section Option 1 now leads with the 3→8 result instead of the narrow 0/2→2/2 metric
- System instructions (source hierarchy) don't fix retrieval gaps — metadata tags do
- SP/PDF - Com not retested (already 8/10 with 0 Fails; its 2 Partials are structural)
- P2 revised prompt tested for SP/PDF - GCC: Partial → Pass when given explicit document names

### Next session priorities
1. **KB agent retests**: Full 10-prompt battery on KB/PDF and KB/DOCX agents with cross-referenced documents
2. **SP/PDF remaining gaps**: P6 (missing Thomas Reed/GAL) and P9 (structural doc limitation) are the two remaining Partials

## Session 32 — 2026-03-09

### What was done
- **Demo guide: Document Improvement Walkthrough** — Added new "Act 4b: Document Improvement Walkthrough" section (5-7 minutes) to `generate-demo-guide-pdf.py`
  - Step 1: Baseline (3/10) — shows original document library, runs skeletal survey and Marcus Webb prompts, explains why they fail
  - Step 2: Cross-reference headers (3/10 → 7/10) — side-by-side comparison of original vs cross-referenced documents, highlights the key annotations, runs skeletal survey prompt to show it passes, full 10-prompt results table
  - Step 3: SharePoint metadata tags (7/10 → 8/10) — shows library metadata columns, explains retrieval gap on P2, runs Marcus Webb prompt to show it passes
  - Punchline: summary table (Step / Change / Score / Effort), callout box for GCC customers
- **Updated Act 4 (Level 5)**: Replaced "optional beat" document improvement text with a clean transition into Act 4b
- **Updated timing guide**: Added Act 4b row, adjusted running totals (now 65-70 min total), shortened Act 4 from "5-6 min" to "3-4 min"
- **Updated compressed/standard timing notes**: Both explicitly keep Act 4b walkthrough
- Regenerated demo-guide.pdf (now 25 pages, up from ~20)

### Decisions made
- Act 4b goes between Level 5 (trust-but-verify) and Act 5 (what this means) — Level 5 introduces the problem, 4b shows the fix, Act 5 wraps up
- Walkthrough designed for live demo: prompts to type, talking points for each step, what to show on screen
- Both compressed (25 min) and standard (40 min) formats keep the full walkthrough — this is the audience's favorite section
- **Cross-referenced Case 2 documents created** — 5 documents in `sharepoint-docs/Case-2024-DR-15-0341 (R1 - Cross-Referenced)/`
  - TPR_Petition_and_Affidavit, GAL_Reports, Court_Orders_and_Filings, DSS_Investigation_Report, Substance_Abuse_Evaluation (md/docx/pdf)
  - Every document's cross-reference header prominently mentions Thomas Reed as GAL
- **P6 retested with cross-referenced Case 2 docs**
  - SP/PDF-GCC: Partial → Pass (Thomas Reed found, 2 sources: GAL_Reports + DSS_Investigation_Report)
  - SP/PDF-Com: Pass → Pass (already passing, now 4 sources instead of 1, organized by category with summary table)
- **SP/PDF-GCC now at 9/10** — surpasses Commercial SP/PDF (8/10). Only P9 (structural) remains Partial.
- **SP/PDF-Com stays at 8/10** — P2 (bedtime time range) and P9 (structural) are the two remaining Partials
- Metadata tags tested on Webb GAL_Report for P6 — no effect because Thomas Reed is GAL for the Price case, not the Webb case. Cross-referenced Case 2 docs fixed it instead.

### Decisions made
- Cross-referenced Case 2 docs follow exact same pattern as Case 1 (blockquote header with document descriptions)
- Thomas Reed gap was a missing-document problem (Case 2 GAL Report not being retrieved), not a metadata problem
- SP/PDF-GCC at 9/10 surpasses Commercial SP/PDF (8/10) — document hygiene closed AND surpassed the model gap for document agents
- P9 is unfixable by design — useful demo point about document agent ceiling vs structured data

### Next session priorities
1. **Update all PDFs and slide deck**: 8/10 → 9/10 for GCC SP/PDF across all generators
2. **KB agent retests**: Full 10-prompt battery on KB/PDF and KB/DOCX agents with cross-referenced documents (both Case 1 and Case 2)
3. **SP/PDF-Com full retest**: Run all 10 prompts on Commercial with both cross-referenced doc sets to see if it also improves past 8/10

## Session 33 — 2026-03-09

### What was done
- **Summary PDF major restructure** — reorganized from 9 TOC sections to 7, telling a linear narrative
  - "The Danger Taxonomy" absorbed into Round 0 as the "oh crap" moment after baseline scores
  - "The Evidence" absorbed into The Iterative Process as a subsection with NO scores (pure scene-setter)
  - The Iterative Process is now a mega-section: Evidence → Round 0 → Round 1 → Round 2 → Pattern
  - Rounds unified across doc and data agents (previously separate improvement tracks)
  - Score progression tables build through rounds: R0 (1 col) → R1 (2 cols) → R2 (3 cols)
  - Cross-use-case results table removed (replaced by progressive round tables)
  - Pattern for Organizations expanded from 4 steps to 5 (added "Fix the documents")
- **Document improvement tables normalized to /10** across all PDFs
  - Commercial SP/PDF: 0/2 → 2/2 changed to 8/10 → 10/10 (demo guide, slide outline, summary)
  - GCC SP/PDF shown per-round: 3/10 → 7/10 → 9/10
- **Agent naming consistency**: "SharePoint/PDF" → "Copilot Studio SharePoint/PDF" in all summary tables
- **Added `sub_subsection_title` helper** to ExecutivePDF class (10pt bold, DARK color) for 3rd-level headings
- **Danger taxonomy table tightened**: font 7.5→7, line height 4→3.5, padding 2→1, shorter cell text
- **Demo guide updated**: Pattern text now includes "then documents" step
- **Slide outline updated**: Commercial doc agent normalized to 8/10 → 10/10
- Regenerated all 3 affected PDFs (summary, demo-guide, slide-outline)

### Score progression (unified rounds for summary PDF)
| Agent | R0 | R1 | R2 |
|---|---|---|---|
| Web SPA | 10 | 10 | 10 |
| COM MCP | 8 | 10 | 10 |
| COM SP/PDF | 8 | 10 | 10 |
| IA | 1 | 8 | 10 |
| Triage | 0 | 1 | 10 |
| GCC SP/PDF | 3 | 7 | 9 |
| FA | 4 | 8 | 9 |
| GCC MCP | 2 | 4 | 4 |
| M365 | 2 | -- | -- |

### Decisions made
- Danger Taxonomy has more emotional weight inside Round 0 than as a standalone section
- Evidence subsection without scores removes the baseline-vs-final confusion
- Doc agent improvement rounds mapped to data agent rounds: R1 = cross-refs (like data fixes), R2 = metadata (like tool refinements)
- SP/PDF (Gov Cloud) shown once in baseline table (UC1 score of 3/10, which progresses through rounds) with footnote about stable 8/10 UC2 score

### Next session priorities
1. **KB agent retests**: Full 10-prompt battery on KB/PDF and KB/DOCX agents with cross-referenced documents
2. **SP/PDF-Com full retest**: Run all 10 prompts on Commercial with both cross-referenced doc sets
3. **Review summary PDF layout**: Check page breaks and table rendering in the new structure

## Session 34 — 2026-03-09

### What was done
- **Whitepaper content edits**
  - M365 Copilot moved from Round 0 to Round 1 (it was tested after R0 improvements were in place); removed from baseline table, R1 shows `--`/`2/10`, R2 shows `--`/`2/10`/`--`
  - Removed Triage Agent sub-rounds detail from Round 2 Data Agents "What changed"
  - Code Investment Spectrum: "Zero" → "Config only" for low/no-code agents; added paragraph explaining MCP server/API is a separate pro-code investment
  - Conclusion: "existing Copilot and Copilot Studio licenses, plus SharePoint document libraries"
  - Danger taxonomy Agent(s) column simplified: specific agent names → "Document Agent", "Data Agent", or "Both"
  - Fixed fpdf2 strikethrough bug in test prompts appendix (`--` → parentheses)
  - Level 3: removed "(prior to improvements)", cleaned up Copilot Studio references
  - Model Gap: removed GCC locked-to-4o sentence, reordered for clarity
  - "30 minutes of engineering" → "simple engineering"
  - "every gap was fixable" changed from bullet to body text
  - Renamed "Web SPA" / "Custom Web App" → "Case Analyst Agent" globally
  - Added clarifying italic note under danger taxonomy about high-scoring agent failures

- **Whitepaper structural changes**
  - **New "Meet Your Agents" section** between At a Glance and The Five Levels — UC1 (11 agents) and UC2 (8 agents) tables with key box, replaces Appendix: Agent Configurations
  - **Removed Appendix: Agent Configurations** (content moved to Meet Your Agents)
  - **Removed Appendix: Data Extraction Options**
  - TOC reduced from 9 to 8 entries: At a Glance, Meet Your Agents, The Five Levels, The Iterative Process, GCC Options, Five Findings, Conclusion, Appendix: Test Prompts

- **At a Glance visual redesign**
  - Summary tile (full width): intro text on left with "Summary" label, Five Levels legend with colored badges on right
  - Three level tiles (L1-2, L3, L4) with title-cased headings
  - Combined use case tile (full width): UC1 left / UC2 right with faded vertical divider, stat chips (bold numbers in accent color), agent counts
  - Use case descriptions, data stats, and agent counts all in one cohesive card

- **Test prompt tables**: added `wrap=True` mode to `styled_table` with `multi_cell` wrapping and page-break protection for rows that would split across pages

### Decisions made
- M365 Copilot belongs in Round 1 (tested after R0 improvements were in place)
- "Case Analyst Agent" naming convention matches other agents (Investigative Agent, Triage Agent, Foundry Agent)
- Agent config tables belong early in the doc (Meet Your Agents) not buried in an appendix
- Data Extraction appendix cut — not core to the narrative
- "Config only" more honest than "Zero code" for agents that assume an existing MCP server

---

## Session 36 — 2026-03-10

### What was done
- **Dataverse MCP mentions** — Added Dataverse references to 4 sections: Level 3 Recommendation, GCC Options (new Option 5), Why Copilot Studio, and Conclusion
- **Whitepaper final review — 12 changes across the entire document:**
  1. **Cover title broadened** — "for Copilot Studio" → "for Government AI"; subtitle now "across Copilot Studio, Foundry, and pro-code architectures"
  2. **Page header updated** — matches new title on every page
  3. **Version number added** — "v1.0" on cover and footer
  4. **Footer simplified** — removed "Confidential" and stats repetition; now just "March 2026 | v1.0"
  5. **M365 Copilot explanation** — Added "Why M365 Copilot scored lowest" paragraph after Round 1 table explaining platform-assigned model, limited customization, no system prompt control
  6. **M365 Round 2 "--" explained** — Footnote now says "platform constraints prevent iterative improvement"
  7. **Danger Taxonomy framing** — Added bold callout: "Every failure below occurred in agents that ultimately scored 9 or 10 out of 10"; removed redundant italic footnote
  8. **Improvement Playbook** — Renamed from "The Pattern for Organizations"; added numbered steps (1-5) and framing intro
  9. **"Poverty Profiteering" renamed** — Appendix test prompts heading changed to "Investigative Analytics"
  10. **Level 5 tile tagline** — "Trust but Verify" → "Human in the Loop" (reserves "Trust but Verify" for the Conclusion callout)
  11. **Licensing sentence** — Added to Conclusion: Copilot Studio included with M365/Power Platform; Foundry and pro-code use consumption-based Azure OpenAI pricing
  12. **Next Steps section** — 4 bullets before appendix: Start at Level 1, Build your ground truth, Scale when ready, Get started (contact account team)

### Decisions made
- Title "for Government AI" is more shareable outside Microsoft ecosystem — CIO can forward without it looking like vendor collateral
- "Confidential" removed — want government buyers to share internally
- "Trust but Verify" reserved for the closing callout where it lands hardest; Level 5 tile uses "Human in the Loop"
- M365 Copilot needs explicit explanation since buyers already have licenses and will ask "why can't I just use that?"
- Numbered steps in Improvement Playbook give it methodological weight vs. unordered bullets
- Score formatting difference (prose "8 out of 10" vs. table "8/10") is intentional, left as-is

---

## Session 35 — 2026-03-10

### What was done
- **Meet Your Agents key box** — Fixed garbled text (2-column overflow), then removed the key box entirely as redundant (tables are self-documenting)

- **At a Glance page redesign (multiple iterations)**
  - Summary tile: removed legend, text now spans full width
  - Level tiles: iterated through 3 columns → combined tile → 2x2 grid → 4 separate stacked → final: 2x2 grid of 4 separate colored tiles at ~75% width
  - Added Level 5 tile: "Trust but Verify — Full accuracy at L4 means humans review conclusions, not raw data."
  - Five Levels legend moved to right sidebar beside level tiles, with vertical divider in summary tile removed
  - UC tiles: split from combined tile into 2 stacked tiles at ~75% width on the right
  - Meet Your Agents sidebar: added on the left beside UC tiles with 4 colored badge tiles (M365 Copilot light blue, Copilot Studio blue, Foundry medium blue, Pro-code navy) in a code-investment spectrum
  - Added "Full agent reference in Appendix." note at bottom of sidebar

- **Meet Your Agents moved to appendix** — Now "Appendix: Meet Your Agents" (first appendix, before Test Prompts). TOC updated accordingly.

- **Agent naming convention** — Changed from `SP/DOCX (GCC)` format to `SP/DOCX/GCC` slash format in both UC tables

- **Score updates** — UC1 table now shows final R2 scores: CS MCP/Com 8→10, CS SP/PDF/Com 8→10, CS SP/PDF/GCC "3/10 to 9/10"→9. Column header changed to "Final Score"

- **Content improvements**
  - "Levels 1-2" → "Levels 1 - 2" (avoids fpdf2 strikethrough)
  - Summary tile: "two" → "2", "seven" → "7"
  - Round 2 Data Agents "What changed" expanded with real content about Triage, Investigative, Foundry, GCC MCP agents
  - Round 2 intro text: "targeted tool descriptions, metadata, and additional cross-references" → "refined MCP tool descriptions, agent system prompts, and SharePoint metadata tags"
  - Combined result after Round 2 cleaned up — uses actual agent names, removed vague "GPT-4o agent" reference
  - Pattern for Organizations: removed numbered bullets
  - Added "Round 1 Scores" and "Round 2 Scores" sub-headings before tables (Round 0 kept as "Baseline Scores", removed duplicate)
  - Code Investment Spectrum: removed parenthetical details from Code Required column, added Dataverse MCP connector callout
  - Copilot Studio description: "Low-code, declarative" → "Highly configurable"
  - "orchestration ceiling" → "managed orchestration layer limited tool sequencing on the hardest prompt"

### Decisions made
- Meet Your Agents works better as an appendix — At a Glance sidebar provides the quick overview, appendix has the detail
- Agent naming uses slash format (`SP/DOCX/GCC`) for consistency and brevity
- Level 5 tile added to At a Glance to complete the narrative (trust but verify)
- Four agent categories (M365 Copilot, Copilot Studio, Foundry, Pro-code) map to code-investment spectrum
- Foundry Agent is "Low" code (not config only) — needs thin client code
- Dataverse MCP connector worth calling out in Code Investment Spectrum

## Session 37 — 2026-03-10

### What was done
- **KB agent retesting with cross-referenced documents** — 3 of 6 untested document agents retested on all 10 UC1 prompts with cross-referenced documents (KB/DOCX/Com deferred due to config issues)
  - KB/PDF/Com: 5/10 -> 8/10 (+3)
  - KB/PDF/GCC: 5/10 -> 9/10 (+4) — only agent to catch skeletal survey discrepancy
  - KB/DOCX/GCC: 4/10 -> 8/10 (+4) — still reproduced dangerous "no fractures" error on prompt 4
  - Test run count: 313 -> 343 (30 new runs)

- **Updated all docs with new scores**
  - Whitepaper: UC1 appendix table re-sorted, R2 document agents section adds KB retest results, R2 combined result mentions KB pattern, footnote updated
  - 313 -> 343 across 7 files: whitepaper, slide outline, slide deck, demo guide, FAQs, README
  - Regenerated: whitepaper PDF, slide outline PDF, demo guide PDF, FAQs PDF, PowerPoint deck

- **SP/DOCX retests with cross-referenced documents**
  - SP/DOCX/Com: 7/10 -> 9/10 (+2) — excellent nuance on skeletal survey (prompt 4), only failed time gap math (prompt 10)
  - SP/DOCX/GCC: 5/10 -> 7/10 (+2) — initially scored 3/10 because Case 2 DOCXs were missing from the library; after adding them, recovered to 7/10. Prompt 4 no longer reproduces "no fractures" error. Prompts 1, 5, 8 still fail (retrieval can't find Case 2 docs for those queries).
  - Test run count: 343 -> 370 (20 initial runs + 7 re-retests after missing docs fix)

- **Updated all docs with final SP/DOCX scores**
  - UC1 appendix table re-sorted, R2 narrative expanded to cover all retested document agents
  - 343 -> 370 across 6 files
  - Regenerated: whitepaper PDF, slide outline PDF, demo guide PDF, FAQs PDF, PowerPoint deck

- **KB/DOCX/Com retest** — Config issues resolved, tested all 10 prompts
  - KB/DOCX/Com: 6/10 -> **10/10** (+4) — perfect score, best skeletal survey answer of any agent
  - Prompt 4 (skeletal survey): contextualizes sheriff's "no fractures" as meaning no *additional* fractures beyond the two diagnosed — most nuanced interpretation across all 19 agents
  - Test run count: 370 -> 380

- **All 11 UC1 agents now have final scores** — no more Round 0 holdouts

### Final UC1 Scores (all agents retested)
| Agent | R0 | Final |
|---|---|---|
| Case Analyst Agent | 10 | 10 |
| CS MCP/Com | 8 | 10 |
| CS SP/PDF/Com | 8 | 10 |
| CS KB/DOCX/Com | 6 | **10** |
| CS SP/DOCX/Com | 7 | 9 |
| CS MCP/GCC | -- | 9 |
| CS SP/PDF/GCC | 3 | 9 |
| CS KB/PDF/GCC | 5 | 9 |
| CS KB/PDF/Com | 5 | 8 |
| CS KB/DOCX/GCC | 4 | 8 |
| CS SP/DOCX/GCC | 5 | 7 |

### Decisions made
- Document hygiene (cross-reference headers) is the single biggest lever for document agents — every agent improved, average +3 points
- KB/DOCX/Com at 10/10 breaks the "PDF always beats DOCX" pattern — DOCX outperformed PDF in the KB/Com config
- SP/DOCX/GCC retrieval issues (3 prompts can't find Case 2 docs) are a SharePoint/GPT-4o limitation, not a document quality issue

## Session 38 — 2026-03-10

### What was done
- **Whitepaper finalization** — Changed "Start at Level 1." to "Start simple." in Next Steps section to avoid collision with the five-level accuracy framework terminology
- Decided against retesting M365 Copilot — 2/10 score supports the "match investment to accuracy" narrative; platform-assigned model means improvements aren't attributable
- Regenerated whitepaper PDF (v1.0 final)

### Decisions made
- Whitepaper v1.0 is complete — no further content changes planned
- M365 Copilot stays at 2/10 (R1 only, no R2 retest)

## Session 39 — 2026-03-11

### What was done
- **Dataverse MCP agent testing (CS/DV/GCC)** — Configured Copilot Studio agent with native Dataverse MCP server connector, loaded all 1,149 records into 5 Dataverse tables
- **Round 0 (baseline, no instructions/description):** 1/10 — only prompt 9 (TPR cases) returned correct results; most prompts hit MCP SQL errors (`uniqueidentifier` conversion, subquery errors) or returned "no records found"
- **Round 1 (added agent instructions + description + query pattern hints):** 1/10 — prompt 5 (timeline) now worked perfectly (10/10), but prompt 9 (TPR) broke; net score unchanged
- **Patched Dataverse metadata descriptions** via `database/patch-dataverse-descriptions.js` — enriched all 5 table descriptions and 30 column descriptions so the MCP server exposes better tool metadata

### Dataverse description patches applied
Tables and columns received rich descriptions including valid values, query hints, and relationship explanations. Script: `database/patch-dataverse-descriptions.js`

**Table descriptions:**

| Table | Description |
|-------|-------------|
| legal_legalcase | 50 legal cases. Primary identifier is legal_caseid (text, e.g. '2024-DR-42-0892'), NOT the Dataverse GUID. Filter by legal_casetype (CPS, TPR, APS, Adoption, Guardianship, ICPC), legal_county, legal_circuit, legal_status (Active, Closed, Pending Review, Dismissed). To find related records, first query this table to get the GUID, then filter related tables. |
| legal_person | 277 people linked to cases via legal_LegalCaseId lookup. Query by legal_fullname, legal_role. To find statements, first get person record ID, then filter legal_statement by legal_PersonId. |
| legal_timelineevent | 333 chronological events linked via legal_LegalCaseId. Filter by legal_eventtype. Sort by legal_eventdate + legal_eventtime. |
| legal_statement | 338 recorded statements linked to cases (legal_LegalCaseId) and people (legal_PersonId). Contains legal_statementtext (full verbatim text), legal_madeto, legal_sourcedocument, legal_pagereference. |
| legal_discrepancy | 151 contradictions linked to cases (legal_LegalCaseId), Person A (legal_PersonAId), Person B (legal_PersonBId). Contains legal_topic, legal_personaaccount, legal_personbaccount, legal_contradictedby. |

**Column descriptions (key examples):**

| Column | Description |
|--------|-------------|
| legal_caseid | Human-readable case number (e.g. '2024-DR-42-0892'). NOT the Dataverse record GUID. |
| legal_casetype | Values: CPS, TPR, APS, Adoption, Guardianship, ICPC |
| legal_status | Values: Active, Closed, Pending Review, Dismissed |
| legal_role | Values: Mother, Father, Child, Caseworker, Attorney, Guardian ad Litem, Therapist, Physician, Teacher, Neighbor, Relative, Foster Parent, Law Enforcement, Judge |
| legal_eventtype | Values: Incident, Investigation, Court Hearing, Home Visit, Medical Exam, Interview, Placement, Service Referral, Report Filed, Emergency Action, Family, Medical, Law Enforcement, DSS Action, Court |
| legal_statementtext | Full verbatim text of what the person said — primary content field for analysis |
| legal_topic | What the discrepancy contradiction is about (e.g. 'Timeline of injury discovery', 'Bedtime routine') |
| legal_fullname | Person's full name (e.g. 'Marcus Webb', 'Dena Holloway') — use for person lookups |

### Agent instructions added to Copilot Studio
- Full schema description with all 5 tables, column names, valid values, and relationship explanations
- Two-step query pattern: always look up case/person by text field first to get GUID, then filter related tables by lookup
- Break complex queries into multiple simple queries rather than subqueries

### CS/DV/GCC test scores

| # | Prompt | R0 | R1 | R2 |
|---|--------|----|----|-----|
| 1 | Jaylen Webb ER admission | 0 | 0 | 0 |
| 2 | Marcus Webb statements | 0 | 0 | ~1 (1/5 tries; found LE statements, missed Medical Staff) |
| 3 | Crystal Price drug tests | 0 | 0 | 0 |
| 3.2 | Crystal Price transportation | 1 | 1 | 0 |
| 4 | Skeletal survey fractures | 0 | 0 | 0 |
| 5 | Timeline for case | 0 | 10 | 10 |
| 6 | People in Price TPR | 0 | 0 | 0 |
| 7 | Dena Holloway statements | 0 | 0 | 0 |
| 8 | Statements to law enforcement | 0 | 0 | 0 |
| 9 | TPR cases | 10 | 0 | 0 |
| 10 | Time gap thump to hospital | 0 | 0 | 0 |
| **Total** | | **1/10** | **1/10** | **2/10** |

**R2 notes:**
- P2 improvement: metadata descriptions enabled the two-step lookup (person → GUID → statements) — worked 1/5 attempts. Found 2 law enforcement statements but missed `Medical Staff` statement because `legal_madeto` value is `'Medical Staff'` not `'Hospital Staff'`. Fix: add valid `legal_madeto` values to column description in future round.
- P5 (timeline): stable at 10 across R1 and R2
- P3.2 (transportation): regressed from 1 to 0
- P9 (TPR cases): still broken since R1 (worked in R0 baseline only)
- MCP SQL generation remains non-deterministic — same prompt produces different SQL on each attempt

### MCP errors observed
- `Subquery returned more than 1 value` — agent writes SQL with scalar subqueries returning multiple rows
- `Conversion failed when converting from a character string to uniqueidentifier` — agent uses case number string where GUID is expected
- Both errors are in the Dataverse MCP server's SQL generation, not in our data

### Decisions made
- Dataverse MCP server's SQL generation is the bottleneck, not schema or instructions
- Rich metadata descriptions helped marginally (P2 partial success) but fundamental SQL generation quality is too low
- CS/DV/GCC final score: **R0=1, R1=1, R2=2** — to be added to whitepaper agent matrix
- Model-driven app (Steps 6-7 in deploy-dataverse.js) still needs debugging (views: POST savedqueries 400, app: POST appmodules 400)

---

## Session 40 — 2026-03-11

### What was done
- **CS/DV/GCC Round 3 testing** — Tested denormalized text columns + updated descriptions
- **Denormalized columns added (R3):** Created `database/patch-dataverse-denormalize.js` — added 7 text columns across 4 child tables (`legal_caseidtext`, `legal_personname`, `legal_personaname`, `legal_personbname`) and populated all 3,297 records with resolved values
- **Case type description fix:** Discovered `legal_casetype` stores full text ('Termination of Parental Rights') but descriptions listed abbreviations ('TPR'). Updated both table and column descriptions to list full text values with "never use abbreviations" instruction. Re-patched and retested — agent still generated `WHERE legal_casetype = 'TPR'`.
- **R3 result: 1/10** (regression from R2's 2/10) — P2 stopped working, P6 timeline still stable. Denormalized columns were never used by the MCP SQL generator in any observed query.
- **Created `docs/dataverse-mcp-server-testing.md`** — comprehensive test log with actual SQL queries, MCP errors, improvement narrative, key findings, and recommendations for the product team
- **Added Commercial replication instructions** to testing doc with step-by-step setup for deploying to a Commercial Dataverse environment

### CS/DV/GCC R3 test scores

| # | Prompt | R0 | R1 | R2 | R3 |
|---|--------|----|----|----|----|
| 1 | Jaylen Webb ER admission | 0 | 0 | 0 | 0 |
| 2 | Marcus Webb statements | 0 | 0 | ~1 | 0 |
| 3 | Crystal Price drug tests | 0 | 0 | 0 | 0 |
| 3.2 | Crystal Price transportation | 1 | 1 | 0 | 0 |
| 4 | Skeletal survey fractures | 0 | 0 | 0 | 0 |
| 5 | Timeline for case | 0 | 10 | 10 | 10 |
| 6 | People in Price TPR | 0 | 0 | 0 | 0 |
| 7 | Dena Holloway statements | 0 | 0 | 0 | 0 |
| 8 | Statements to law enforcement | 0 | 0 | 0 | 0 |
| 9 | TPR cases | 10 | 0 | 0 | 0 |
| 10 | Time gap thump to hospital | 0 | 0 | 0 | 0 |
| **Total** | | **1/10** | **1/10** | **2/10** | **1/10** |

### Key findings from R3
1. **Denormalized columns completely ignored** — MCP SQL generator used lookup/relationship columns in every cross-table query, never the text columns
2. **Descriptions don't influence SQL generation** — "never use abbreviations" instruction ignored; "use this column to filter directly" ignored. Descriptions appear to affect tool discovery only, not SQL generation
3. **Score regression** — P2 (Marcus Webb statements) worked 1/5 times in R2 but 0/5 in R3, suggesting adding more columns/descriptions may have made things worse
4. **P9 case type mismatch** — data stores 'Termination of Parental Rights' but MCP generates `'TPR'` despite descriptions explicitly mapping abbreviations to full text

### Decisions made
- Denormalized columns and description enrichment have hit their ceiling — no further improvements possible without platform changes
- Created comprehensive testing doc (`docs/dataverse-mcp-server-testing.md`) to share with Dataverse MCP product team
- Next step: replicate in Commercial Dataverse environment to test whether a different model (GPT-4.1/GPT-5 Auto) changes SQL generation quality
- Testing doc will become a PDF eventually (generator not yet created)

---

## Session 41 — 2026-03-11
**Focus:** Dataverse MCP — Commercial environment deployment and testing

### What happened
- Updated all 3 Dataverse scripts (deploy-dataverse.js, patch-dataverse-descriptions.js, patch-dataverse-denormalize.js) to target Commercial environment (og-dv.crm.dynamics.com)
- Deployed full schema (5 tables, 7 relationships, 7 denormalized columns) + 1,149 records to Commercial Dataverse
- Patched all table/column descriptions and populated denormalized text columns
- Created Copilot Studio agent with Dataverse MCP connector in Commercial
- Ran all 11 test prompts — scored 5/11 (vs GCC best of 2/11)

### Key finding
**The model matters.** Commercial scored 5/11 vs GCC's 1/11 (R3) with identical schema, descriptions, and instructions. Multi-step lookups (person → case → statements) that GCC could never do, Commercial handles reliably. Remaining failures are shared: person-to-case resolution when person isn't plaintiff, description adherence (TPR abbreviation), wrong event type guesses.

### Scores
| Prompt | GCC R3 | Com R0 |
|--------|--------|--------|
| P1 Jaylen ER | 0 | 0 |
| P2 Marcus statements | 0 | 9 |
| P3 Crystal drugs | 0 | 0 |
| P4 Crystal transport | 0 | 0 |
| P5 Skeletal survey | 0 | 0 |
| P6 Full timeline | 10 | 10 |
| P7 LE statements | 0 | 9 |
| P8 Price people | 0 | 0 |
| P9 TPR cases | 0 | 0 |
| P10 Dena comparison | 0 | 9 |
| P11 Time gap | 0 | 10 |

### Files changed
- `database/deploy-dataverse.js` — ENV_URL, TENANT_ID updated to Commercial
- `database/patch-dataverse-descriptions.js` — same
- `database/patch-dataverse-denormalize.js` — same
- `docs/dataverse-mcp-server-testing.md` — Commercial results added

---

## Session 42 — 2026-03-11
**Focus:** Dataverse MCP — Multi-model comparison (GPT-5 Auto + Sonnet 4.6)

### What happened
- Discovered Copilot Studio Commercial now offers Anthropic models (Sonnet 4.6) via model picker alongside OpenAI models
- Tested same 11 UC1 prompts on same Commercial Dataverse MCP agent with two additional models:
  - **Sonnet 4.6: 11/11 — perfect score.** Every prompt answered correctly, including all 6 prompts that every OpenAI model failed.
  - **GPT-5 Auto: 4/11 — worse than GPT-4.1 (6/11).** Lost Q2 (hospital staff statement) and Q11 (time gap), gained nothing new.
- Corrected GPT-4.1 score from 5/11 to 6/11 (renumbered prompts to match actual prompt list)

### Final multi-model scorecard
| # | Prompt | GPT-4o (GCC) | GPT-4.1 (Com) | GPT-5 Auto (Com) | Sonnet 4.6 (Com) |
|---|--------|:------:|:-------:|:----------:|:----------:|
| Q1 | ER admission | 0 | 0 | 0 | 10 |
| Q2 | Marcus bedtime | 0 | 9 | 5 | 10 |
| Q3 | Crystal "clean now" | 0 | 0 | 0 | 10 |
| Q4 | Crystal transportation | 0 | 0 | 0 | 10 |
| Q5 | Skeletal survey | 0 | 0 | 0 | 10 |
| Q6 | Full timeline | 10 | 10 | 10 | 10 |
| Q7 | Price TPR people | 0 | 9 | 8 | 10 |
| Q8 | Dena statement comparison | 0 | 9 | 9 | 10 |
| Q9 | Law enforcement statements | 0 | 9 | 9 | 10 |
| Q10 | TPR cases | 0 | 0 | 0 | 10 |
| Q11 | Time gap | 0 | 10 | 0 | 10 |
| **Passing** | | **1/11** | **6/11** | **4/11** | **11/11** |

### Key findings
1. **The model is everything.** Same connector, same data, same schema — scores range from 1/11 to 11/11 based solely on model selection.
2. **Newer doesn't mean better.** GPT-5 Auto scored worse than GPT-4.1 on structured data retrieval.
3. **Copilot Studio now supports Anthropic models** in Commercial — first confirmed test of Sonnet 4.6 with Dataverse MCP connector.
4. **Sonnet solved every shared OpenAI failure:** P1 (ER admission), P3 (drug tests), P4 (transportation), P5 (skeletal survey), P10 (TPR case type filtering) — all zero across every OpenAI model, all perfect with Sonnet.

### Files changed
- `docs/dataverse-mcp-server-testing.md` — GPT-5 Auto + Sonnet 4.6 results, multi-model comparison section, findings 8-10
- `scripts/generate-executive-pdf.py` — 15 agent configs, 462 test runs, 21 agents, Sonnet/GPT-5 Auto in R2 table + Meet Your Agents
- `docs/session-log.md` — Session 42
- `MEMORY.md` — Updated scores, milestones, open items

## Session 43 — 2026-03-11
**Focus:** Slide outline refinement — content accuracy, layout fixes, speaker notes

### What happened
- **S1 (Title):** Rewrote speaker note — references delegation demo and ALM demos
- **S2 (At a Glance):** Added talking point: "This is the whole story on one slide. Everything that follows is how we got here."
- **S5 (The Question):** Replaced speaker note entirely — old note was about what the demo is/isn't, new note ties to slide's "not all use cases are created equal" theme with concrete examples (policy chatbot vs legal case prep)
- **S8 (Level 3):** Fixed inaccurate claim "they only see individual files" → "they can't count, sum, or filter across a full dataset" (doc agents can cite multiple files)
- **S12 (Level 5):** Fixed page break issue — speaker note was orphaned on next page. Forced page break before S12 so all content stays together. Also moved speaker note earlier (before document improvement bullets) to keep it closer to slide heading
- **Speaker note method:** Added dry_run height measurement to prevent future orphaning across page breaks
- **Cover page:** Centered horizontal rule between "Slide Outline" and "25 Slides | March 2026" (moved from y=65 to y=71.5)

### Files changed
- `scripts/generate-slide-outline-pdf.py` — All slide outline edits above
- `docs/pdf/slide-outline.pdf` — Regenerated
- `docs/pdf/improving-agents-whitepaper-v1.pdf` — Regenerated
- `docs/pdf/demo-guide.pdf` — Regenerated
- `docs/pdf/faqs.pdf` — Regenerated
- `docs/pdf/user-guide.pdf` — Regenerated
- `docs/pdf/architecture.pdf` — Regenerated
- `decks/agent-fidelity-spectrum.pptx` — Regenerated
- `docs/session-log.md` — Session 43
