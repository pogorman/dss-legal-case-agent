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
