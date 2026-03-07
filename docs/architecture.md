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
│  Policy: inject function key via      │
│  query param from named value        │
└──────────────┬───────────────────────┘
               │ HTTPS + ?code= query param
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
- Total: 277 people, 333 timeline events, 338 statements, 151 discrepancies
- Basic tier (5 DTU) — sufficient for demo
- Accessed via managed identity only (no passwords)
- **Public network access: Disabled** — all SQL traffic flows over private endpoint
- Private endpoint `pe-sql-philly` on subnet `snet-private-endpoints` (10.0.2.0/24)
- Private DNS zone `privatelink.database.windows.net` resolves the server FQDN to the private IP
- Portal Query Editor does not work (requires public access) — use Azure Data Studio or temporarily re-enable public access for ad-hoc queries

### Azure Functions (`dss-demo-func`)

- Node 20, TypeScript, Azure Functions v4
- 5 HTTP-triggered functions with `function` auth level (getStatements supports optional `made_to` filter)
- System-assigned managed identity with `db_datareader` on dss-demo
- Flex Consumption plan
- **VNet integrated** via `snet-dss-functions` (10.0.3.0/24) — all outbound traffic routes through the VNet
- `vnetRouteAllEnabled: true` — ensures DNS resolution uses the private DNS zones
- SQL connection via `@azure/identity` DefaultAzureCredential + access token → private endpoint
- **Storage account `dssdemofuncsa`** — public network access disabled, accessed via private endpoints:
  - `pe-blob-dss` (10.0.2.8), `pe-queue-dss` (10.0.2.9), `pe-table-dss` (10.0.2.10)
  - DNS records in `privatelink.blob/queue/table.core.windows.net` zones
  - Identity-based auth (managed identity with Storage Blob Data Owner, Storage Account Contributor, Storage Queue/Table Data Contributor roles)
  - Deployment via `func azure functionapp publish` works because Kudu uploads through the VNet → private endpoint path

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
- Inbound policy injects function key as `?code=` query parameter from named value `dss-func-key`
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
4. **APIM → Functions**: HTTPS + `?code=` query parameter (injected by policy from named value)
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
│  │ (VNet integration)       │  │ pe-blob-philly ──→ phillyfuncsa│ │
│  └──────────────────────────┘  │ pe-queue-philly──→ phillyfuncsa│ │
│                                │ pe-table-philly──→ phillyfuncsa│ │
│                                │                              │  │
│                                │ pe-blob-dss ───→ dssdemofuncsa│  │
│                                │ pe-queue-dss ──→ dssdemofuncsa│  │
│                                │ pe-table-dss ──→ dssdemofuncsa│  │
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
3. DNS for `dssdemofuncsa.blob.core.windows.net` (and queue/table) resolves via private DNS zones to private endpoint IPs
4. Traffic flows entirely within the Azure backbone — never touches the public internet
5. Both databases on the server (`dss-demo` and PhillyStats) benefit from the same SQL private endpoint
6. Both storage accounts (`phillyfuncsa` and `dssdemofuncsa`) have their own private endpoints on the same subnet

**Implications:**
- Azure Portal Query Editor **does not work** (requires public network access on SQL)
- `deploy-sql.js` requires temporarily enabling public access on the SQL server
- Function App deployments (`func azure functionapp publish`) work because Kudu runs within the Function App's VNet context, reaching storage via private endpoints
- Any new app that needs SQL or storage access must be VNet-integrated or use a private endpoint

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

DSS Office of Legal Services provided reference materials in January–February 2026:

1. **6 legal pleading templates** from an active case — complaint for ex parte removal, summons/notice documents, permanency planning orders (reunification and TPR paths), TPR summons/complaint, and order of dismissal. These are heavily templated documents with `[CHOOSE ONE]` placeholders and boilerplate statutory language. They established the **case lifecycle structure** (complaint → removal → permanency planning → TPR → dismissal).

2. **Attorney feedback** from two DSS attorneys who tested an early Copilot prototype. One provided screenshots; the other provided a detailed example prompt requesting: (1) timeline of pertinent facts with citations, (2) chart of discrepancies between parents' accounts, (3) statements by each parent to case managers/law enforcement. The feedback noted the AI output "was not as detailed as I imagined" and had some incorrect timeline items — this set the accuracy bar for the demo.

### What Was Synthesized

| Real Data Element | Synthetic Replacement |
|---|---|
| Real case numbers | 2024-DR-42-0892 |
| Real defendant names | Webb / Holloway (Case 1), Price (Case 2) |
| Child names | Synthetic children |
| Attorney / caseworker names | Synthetic names |
| Specific dates and facts | Invented timeline events, statements, discrepancies |
| Thompson/Legette case details | Not used — only the prompt structure was adopted |

### What Was Kept (public, non-PII)

- General case type structure (CPS, TPR, etc.)
- Court procedural flow (hearings, orders, filings)
- Statutory references (public law)

### The "Money Prompt"

The attorney's 4-part prompt structure became the primary demo prompt:
1. Timeline of pertinent facts with source citations
2. Chart of discrepancies between parents' accounts
3. Statements by Parent A to case managers/law enforcement
4. Statements by Parent B to case managers/law enforcement

This directly shaped the 5 MCP tools (list_cases, get_case_summary, get_timeline, get_statements_by_person, get_discrepancies) and the SQL schema design.

### Source Document Sanitization

The original Word documents contained real case data. These were sanitized using `scripts/sanitize-docs.py`, which replaced all real names, case numbers, dates, and addresses with synthetic equivalents. The mapping is stored locally only (not in the committed version of the script). Sanitization verified: zero real names remain in any document.

### Source Document Handling

- Sanitized Word documents (`.docx`) are stored in `docs/` but **excluded from git** via `.gitignore`
- The `.msg` email file still contains real names and screenshots — kept locally only, excluded from git
- `scripts/sanitize-docs.py` can be re-run if documents are re-obtained from DSS
- No real PII was ever loaded into Azure SQL — only synthetic data from `seed.sql` / `seed-expanded.sql`
- The `sharepoint-docs/` folder contains entirely synthetic documents written from scratch

## Warm-Up Feature

The web UI includes a "Warm Up" button in the header that primes the entire cold-start chain before a demo. It runs two sequential requests:

1. **GET /healthz** — Wakes the Container App (which may be scaled to zero)
2. **POST /chat** — Sends a lightweight chat request that traverses the full pipeline: Container App → APIM → Functions → Azure SQL (warms DB connection pool) → Azure OpenAI (loads model context)

The UI shows a three-stage progress popup (Container App, Database Connection, AI Model) with spinners, checkmarks, and per-stage timing. Auto-closes after 4 seconds on success.

## Design Decisions

- **Embedded case data in SWA**: The Case Browser panel uses JS-embedded data matching seed-expanded.sql (50 cases). This eliminates an API dependency for the read-only browser view and ensures the demo works even if the backend is slow to start.
- **Procedural seed generation**: `database/generate-seed.js` produces 50 cases with seeded PRNG (seed=42) for reproducibility. Keeps 2 hand-crafted demo cases and generates 48 with randomized SC counties, circuits, case types, names, and dates.
- **Unauthenticated MCP endpoint**: The /mcp endpoint is unauthenticated for the POC. Production would require API key or OAuth. Noted in code comments.
- **Same APIM instance**: Reuses the existing APIM to avoid additional cost and provisioning time. Isolated via separate product and API.
- **marked.js CDN**: Using a CDN-hosted markdown renderer for the chat panel to keep the SWA simple (no build step).
- **Free tier SWA**: Switched from Standard to Free tier for built-in AAD login support without custom provider config.
- **Identity-based Function App storage**: Azure policy prevents shared key access on storage accounts; using system-assigned identity with RBAC roles instead of connection strings.
- **Private endpoints for Function App storage**: Storage account `dssdemofuncsa` has public network access disabled. Private endpoints for blob, queue, and table services on `snet-private-endpoints` ensure the Function App (and Kudu deployments) can access storage entirely over the VNet. This eliminates the need to toggle public access for deployments.
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
