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
- Public network access disabled by default; temporarily enabled for deployments only

### Azure Functions (`dss-demo-func`)

- Node 20, TypeScript, Azure Functions v4
- 5 HTTP-triggered functions with `function` auth level
- System-assigned managed identity with `db_datareader` on dss-demo
- Flex Consumption plan
- SQL connection via `@azure/identity` DefaultAzureCredential + access token

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

- Vanilla HTML/CSS/JS (no framework)
- AAD built-in authentication
- Two panels: Agent Chat and Case Browser
- Calls Container App /chat endpoint for agent interaction
- Case Browser uses embedded data (no API dependency)

## Authentication Flow

1. **User → SWA**: AAD built-in auth (`/.auth/login/aad`)
2. **SWA → Container App /chat**: Direct HTTPS call (CORS enabled)
3. **Container App → APIM**: HTTPS + `Ocp-Apim-Subscription-Key` header
4. **APIM → Functions**: HTTPS + `x-functions-key` header (injected by policy)
5. **Functions → SQL**: Azure AD token via `DefaultAzureCredential`
6. **Container App → Azure OpenAI**: Azure AD token via `DefaultAzureCredential`

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
