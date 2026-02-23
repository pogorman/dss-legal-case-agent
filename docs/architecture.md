# Architecture

## Overview

Four-tier architecture following the same pattern as the philly-profiteering project. All tiers communicate over HTTPS with managed identity or subscription key auth.

```
┌──────────────────────────────────────┐
│         Copilot Studio Agent         │
│    (or Web SPA via /chat endpoint)   │
└──────────────┬───────────────────────┘
               │ Streamable HTTP (MCP)
               │ POST /mcp (JSON-RPC 2.0)
               │ POST /chat (OpenAI-style)
               ▼
┌──────────────────────────────────────┐
│  Container App: dss-case-agent       │
│  Express + TypeScript + Node 20      │
│  Routes: /mcp, /chat, /healthz       │
│  Auth: Managed identity (AOAI)       │
│  Secrets: APIM subscription key      │
└──────────────┬───────────────────────┘
               │ HTTPS + Ocp-Apim-Subscription-Key
               ▼
┌──────────────────────────────────────┐
│  Azure API Management (shared)       │
│  Product: dss-demo                   │
│  API: dss-case-api (5 operations)    │
│  Policy: inject x-functions-key      │
└──────────────┬───────────────────────┘
               │ HTTPS + x-functions-key
               ▼
┌──────────────────────────────────────┐
│  Azure Functions: dss-demo-func      │
│  5 HTTP-triggered functions          │
│  Auth: Managed identity → SQL        │
│  Runtime: Node 20, TypeScript        │
└──────────────┬───────────────────────┘
               │ Azure AD token
               ▼
┌──────────────────────────────────────┐
│  Azure SQL: dss-demo                 │
│  5 tables, synthetic data            │
│  Private endpoint (VNet)             │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  Static Web App: swa-dss-legal-case  │
│  Vanilla HTML/CSS/JS                 │
│  AAD built-in auth                   │
│  Calls Container App /chat endpoint  │
└──────────────────────────────────────┘
```

## Component Details

### Azure SQL Database (`dss-demo`)

- Hosted on existing SQL Server (shared with philly-profiteering)
- 5 tables: `cases`, `people`, `timeline_events`, `statements`, `discrepancies`
- 50 synthetic cases: 2 hand-crafted (rich detail) + 48 procedurally generated
- Total: 275 people, 325 timeline events, 338 statements, 150 discrepancies
- Basic tier (5 DTU) — sufficient for demo
- Accessed via managed identity only (no passwords)
- **Public network access: Disabled** — all SQL traffic flows over private endpoint
- Private endpoint `pe-sql-philly` on subnet `snet-private-endpoints` (10.0.2.0/24)
- Private DNS zone `privatelink.database.windows.net` resolves the server FQDN to the private IP
- Portal Query Editor does not work (requires public access) — use Azure Data Studio or temporarily re-enable public access for ad-hoc queries

### Azure Functions (`dss-demo-func`)

- Node 20, TypeScript, Azure Functions v4
- 5 HTTP-triggered functions with `function` auth level
- System-assigned managed identity with `db_datareader` on dss-demo
- Flex Consumption plan
- **VNet integrated** via `snet-dss-functions` (10.0.3.0/24) — all outbound traffic routes through the VNet
- `vnetRouteAllEnabled: true` — ensures SQL DNS resolution uses the private DNS zone
- SQL connection via `@azure/identity` DefaultAzureCredential + access token → private endpoint

### Container App (`dss-case-agent`)

- Node 20, TypeScript, Express
- POST /mcp: MCP streamable HTTP transport (JSON-RPC 2.0)
- POST /chat: OpenAI chat completions with tool-calling loop (GPT-4.1)
- GET /healthz: Health check
- System-assigned managed identity with `Cognitive Services OpenAI User` role
- APIM subscription key stored as Container App secret

### API Management (shared instance)

- New product: `dss-demo` with subscription key requirement
- New API: `dss-case-api` with 5 GET operations
- Inbound policy injects `x-functions-key` from named value `dss-func-key`
- Routes: /dss/cases, /dss/cases/{caseId}, etc.

### Static Web App (`swa-dss-legal-case`)

- Vanilla HTML/CSS/JS (no framework, no build step)
- AAD built-in authentication
- Modern government-application UI: classification banner, DSS branding, scales of justice logo
- Two panels: Agent Chat (with welcome hero, prompt chips, tool badges) and Case Browser (sortable table, detail views)
- Calls Container App /chat endpoint for agent interaction
- Case Browser uses embedded data (no API dependency)
- AI disclaimer footer, responsive design

## Authentication Flow

1. **User → SWA**: AAD built-in auth (`/.auth/login/aad`)
2. **SWA → Container App /chat**: Direct HTTPS call (CORS enabled)
3. **Container App → APIM**: HTTPS + `Ocp-Apim-Subscription-Key` header
4. **APIM → Functions**: HTTPS + `x-functions-key` header (injected by policy)
5. **Functions → SQL**: Azure AD token via `DefaultAzureCredential`
6. **Container App → Azure OpenAI**: Azure AD token via `DefaultAzureCredential`

## Network Architecture

All SQL traffic is private — the SQL server has public network access **disabled**.

```
┌──────────────────────────────────────────────────────────────────┐
│  VNet: vnet-philly-profiteering (10.0.0.0/16)                    │
│                                                                  │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐  │
│  │ snet-dss-functions       │  │ snet-private-endpoints       │  │
│  │ 10.0.3.0/24              │  │ 10.0.2.0/24                  │  │
│  │                          │  │                              │  │
│  │ Function App (outbound)  │  │ pe-sql-philly ──→ SQL Server │  │
│  │ dss-demo-func            │──│                              │  │
│  │ (VNet integration)       │  │ pe-blob-philly ──→ Storage   │  │
│  └──────────────────────────┘  │ pe-queue-philly ──→ Storage  │  │
│                                │ pe-table-philly ──→ Storage  │  │
│  ┌──────────────────────────┐  └──────────────────────────────┘  │
│  │ snet-functions           │                                    │
│  │ 10.0.1.0/24              │  Private DNS Zones:                │
│  │ (philly-profiteering)    │  • privatelink.database.windows.net│
│  └──────────────────────────┘  • privatelink.blob.core.windows.net│
│                                • privatelink.queue.core.windows.net│
│                                • privatelink.table.core.windows.net│
└──────────────────────────────────────────────────────────────────┘
```

**How it works:**
1. Function App outbound traffic routes through `snet-dss-functions` (VNet integration + `vnetRouteAllEnabled`)
2. DNS for `philly-stats-sql-01.database.windows.net` resolves via the private DNS zone to the private endpoint IP
3. Traffic flows entirely within the Azure backbone — never touches the public internet
4. Both databases on the server (`dss-demo` and PhillyStats) benefit from the same private endpoint

**Implications:**
- Azure Portal Query Editor **does not work** (requires public network access)
- `deploy-sql.js` requires temporarily enabling public access on the SQL server
- Any new app that needs SQL access must be VNet-integrated or use a private endpoint

## SharePoint Comparison Layer

In addition to the MCP-backed agent, the demo includes unstructured legal documents in `sharepoint-docs/` for creating a second Copilot Studio agent grounded in SharePoint. This enables a side-by-side comparison:

```
┌──────────────────────────────────┐    ┌──────────────────────────────────┐
│   Copilot Studio Agent (MCP)     │    │ Copilot Studio Agent (SharePoint)│
│   Queries structured SQL via     │    │  Searches uploaded documents via │
│   MCP tools — precise, complete  │    │  semantic search — approximate   │
└──────────────┬───────────────────┘    └──────────────┬───────────────────┘
               │                                      │
               ▼                                      ▼
┌──────────────────────────────────┐    ┌──────────────────────────────────┐
│  Container App → APIM →         │    │  SharePoint Document Library     │
│  Functions → Azure SQL           │    │  11 Markdown files (Cases 1-2)  │
│  50 cases, fully structured      │    │  Same facts, narrative prose    │
└──────────────────────────────────┘    └──────────────────────────────────┘
```

### SharePoint Documents (11 files)

**Case 2024-DR-42-0892 (CPS):** DSS Investigation Report, Medical Records, Sheriff Report #24-06-4418, Court Orders and Filings (3 orders), Home Study Report, GAL Report

**Case 2024-DR-15-0341 (TPR):** DSS Investigation Report, Substance Abuse Evaluation, Court Orders and Filings (6 orders), TPR Petition and Affidavit, GAL Reports (initial + updated)

All documents use page markers matching the `page_reference` values in the SQL seed data. Key statements are embedded verbatim in narrative prose. Some information is intentionally spread across multiple documents to test cross-document synthesis.

## Web Front End

The Static Web App features a modern government-application design:

- **Classification banner**: Gold "FOR OFFICIAL USE ONLY — SC DSS INTERNAL SYSTEM" bar
- **Header**: Scales of justice icon, "Legal Case Intelligence" title, Office of General Counsel subtitle, PRODUCTION badge, user email display
- **Agent Chat**: Welcome hero with branding, icon-labeled prompt chips, animated message bubbles, tool badges, AI disclaimer footer
- **Case Browser**: Searchable case table with status badges, detail views with stat cards
- **Footer**: Dark navy with DSS branding and "Internal Use Only" notice

## Data Provenance

All data in this system is **synthetic**. No real PII or case data was ever loaded into Azure SQL or committed to the repository.

### Source Material

SC DSS Office of General Counsel provided reference materials through Arya Hekmat (Director, Network Operations & Data Center Services, SC DSS) in January–February 2026:

1. **6 legal pleading templates** from an active Spartanburg County case — complaint for ex parte removal, summons/notice documents, permanency planning orders (reunification and TPR paths), TPR summons/complaint, and order of dismissal. These are heavily templated documents with `[CHOOSE ONE]` placeholders and boilerplate statutory language. They established the **case lifecycle structure** (complaint → removal → permanency planning → TPR → dismissal).

2. **Attorney feedback** from two DSS attorneys:
   - **Kathryn Walsh** (plaintiff attorney): Screenshots of her initial Copilot test experience
   - **Laurel** (DSS attorney): A detailed example prompt and expected output from a different case, requesting: (1) timeline of pertinent facts with citations, (2) chart of discrepancies between parents' accounts, (3) statements by each parent to case managers/law enforcement. She noted the AI output "was not as detailed as I imagined" and had some incorrect timeline items — this set the accuracy bar for the demo.

### What Was Synthesized

| Real Data Element | Synthetic Replacement |
|---|---|
| Case number (2023SPA00144) | 2024-DR-42-0892 |
| Defendant names (Erickson) | Webb / Holloway (Case 1), Price (Case 2) |
| Child names | Synthetic children |
| Attorney / caseworker names | Synthetic names |
| Specific dates and facts | Invented timeline events, statements, discrepancies |
| Thompson/Legette case details | Not used — only the prompt structure was adopted |

### What Was Kept (public, non-PII)

- Spartanburg County / 7th Judicial Circuit geography (Case 1)
- SC Code statutory references (public law)
- General case type structure (CPS, TPR, etc.)
- Court procedural flow (hearings, orders, filings)

### The "Money Prompt"

Laurel's 4-part prompt structure became the primary demo prompt:
1. Timeline of pertinent facts with source citations
2. Chart of discrepancies between parents' accounts
3. Statements by Parent A to case managers/law enforcement
4. Statements by Parent B to case managers/law enforcement

This directly shaped the 5 MCP tools (list_cases, get_case_summary, get_timeline, get_statements_by_person, get_discrepancies) and the SQL schema design.

### Source Document Sanitization

The original Word documents contained real case data (Erickson family, case 2023SPA00144). These were sanitized using `docs/sanitize-docs.py`, which replaced all real PII with synthetic data:

| Real | Synthetic |
|---|---|
| Kelle L. Erickson | Dena Holloway |
| Adam Erickson | Marcus Webb |
| Lydia Erickson (DOB 5/3/2019) | Jaylen Webb (DOB 4/10/2021) |
| Walela McDaniel (caseworker) | Renee Dawson |
| Kathryn J Walsh (plaintiff attorney) | Jennifer M. Torres |
| Tim Edwards (defense attorney) | David Chen |
| Shawn Campbell (defense attorney) | Rachel Simmons |
| Jamia Foster (GAL) | Karen Milford |
| 2023SPA00144 | 2024SPA00892 |
| 2025-DR-42-1286 | 2024-DR-42-0892 |

Files were renamed from `2023SPA00144-*` to `2024SPA00892-*`. Sanitization verified: zero real names remain in any document.

### Source Document Handling

- Sanitized Word documents (`.docx`) are stored in `docs/` but **excluded from git** via `.gitignore`
- The `.msg` email file still contains real names and screenshots — kept locally only, excluded from git
- `docs/sanitize-docs.py` can be re-run if documents are re-obtained from DSS
- No real PII was ever loaded into Azure SQL — only synthetic data from `seed.sql` / `seed-expanded.sql`
- The `sharepoint-docs/` folder contains entirely synthetic documents written from scratch

## Design Decisions

- **Embedded case data in SWA**: The Case Browser panel uses JS-embedded data matching seed-expanded.sql (50 cases). This eliminates an API dependency for the read-only browser view and ensures the demo works even if the backend is slow to start.
- **Procedural seed generation**: `database/generate-seed.js` produces 50 cases with seeded PRNG (seed=42) for reproducibility. Keeps 2 hand-crafted demo cases and generates 48 with randomized SC counties, circuits, case types, names, and dates.
- **Unauthenticated MCP endpoint**: The /mcp endpoint is unauthenticated for the POC. Production would require API key or OAuth. Noted in code comments.
- **Same APIM instance**: Reuses the existing APIM to avoid additional cost and provisioning time. Isolated via separate product and API.
- **marked.js CDN**: Using a CDN-hosted markdown renderer for the chat panel to keep the SWA simple (no build step).
- **Free tier SWA**: Switched from Standard to Free tier for built-in AAD login support without custom provider config.
- **Identity-based Function App storage**: Azure policy prevents shared key access on storage accounts; using system-assigned identity with RBAC roles instead of connection strings.
- **Dedicated VNet subnet**: Created `snet-dss-functions` (10.0.3.0/24) since existing `snet-functions` was delegated to Container App environments.

## Deployed Resource URLs

| Resource | URL |
|---|---|
| Web App (SWA) | `https://happy-wave-016cd330f.1.azurestaticapps.net` |
| MCP Endpoint | `https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/mcp` |
| Chat Endpoint | `https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/chat` |
| Health Check | `https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/healthz` |
| APIM Gateway | `https://philly-profiteering-apim.azure-api.net/dss/cases` |
| Functions | `https://dss-demo-func.azurewebsites.net/api/cases` |
