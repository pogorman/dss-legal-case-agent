# DSS Legal Case Intelligence

A professional demo application for the South Carolina Department of Social Services (DSS) General Counsel team. Demonstrates how a Copilot Studio agent backed by structured SQL data (via MCP) produces dramatically better results than one backed by unstructured SharePoint documents.

## Architecture

```
Copilot Studio Agent
        |
        | Streamable HTTP (MCP protocol)
        v
Container App: dss-case-agent
  POST /mcp   — MCP endpoint (Copilot Studio)
  POST /chat  — Chat completions + tool calling (web SPA)
  GET  /healthz
        |
        | HTTPS + Ocp-Apim-Subscription-Key
        v
Azure API Management (existing instance)
  Product: dss-demo | API: dss-case-api | 5 GET operations
        |
        | HTTPS + x-functions-key (injected by APIM policy)
        v
Azure Functions v4 (dss-demo-func)
  5 HTTP-triggered functions | Managed identity SQL auth
        |
        | Azure AD token via private endpoint
        v
Azure SQL Database: dss-demo
  5 tables, 50 synthetic cases
```

## Project Structure

```
dss-legal-case-agent/
├── database/             SQL schema, seed data, and tooling
│   ├── schema.sql        Table definitions (5 tables)
│   ├── seed.sql          Original 2 hand-crafted cases
│   ├── seed-expanded.sql Generated 50-case dataset (deployed)
│   ├── generate-seed.js  Procedural case generator (seeded PRNG)
│   ├── deploy-sql.js     Deploys schema + seed to Azure SQL
│   └── grant-identity.js Grants managed identity db_datareader
├── functions/            Azure Functions (TypeScript, Node 20)
│   └── src/functions/    5 HTTP-triggered functions
├── mcp-server/           Container App (TypeScript, Node 20)
│   └── src/              Express app with /mcp, /chat, /healthz
├── web/                  Static Web App (vanilla HTML/CSS/JS)
│   ├── css/
│   └── js/
├── infra/                Bicep templates
│   ├── main.bicep
│   └── parameters.json
├── sharepoint-docs/       SharePoint comparison documents
│   ├── Case-2024-DR-42-0892/  6 legal documents (CPS case)
│   ├── Case-2024-DR-15-0341/  5 legal documents (TPR case)
│   └── Demo_Comparison_Prompts.md
├── docs/                 Documentation
│   ├── architecture.md
│   ├── demo-guide.md
│   ├── session-log.md
│   ├── user-guide.md
│   └── faqs.md
└── deploy.sh             Deployment script
```

## Quick Start

### Prerequisites

- Azure CLI with active subscription
- Node.js 20+
- Azure Functions Core Tools v4
- Docker (for Container App)
- Access to existing SQL Server, APIM, and Azure OpenAI instances

### Deploy

1. Edit `infra/parameters.json` with your Azure resource names
2. Run `deploy.sh` (see environment variables in the script header)
3. Run `cd database && npm install mssql && node deploy-sql.js` (deploys schema + 50 cases to Azure SQL)
4. Configure AAD auth on the Static Web App

### Local Development

```bash
# Functions
cd functions && npm install && npm run build && func start

# MCP Server
cd mcp-server && npm install && npm run dev

# Web (any static server)
cd web && npx serve .
```

## Demo Flow

1. **Case Browser tab** — Show the structured data (50 synthetic cases)
2. **Agent Chat tab** — "List available cases"
3. **Money prompt:**
   > I represent DSS in case 2024-DR-42-0892. After reviewing the case, can you provide:
   > 1. A detailed timeline of pertinent facts with source citations
   > 2. A chart of discrepancies between the two parents' accounts
   > 3. All statements made by Marcus Webb to case managers or law enforcement
   > 4. All statements made by Dena Holloway to case managers or law enforcement
4. **Follow-up** — "Can you make the timeline more detailed — include specific times where available?"
5. **Key selling point** — Same timeline, same citations. Consistency proof point.

## MCP Tools

| Tool | Description |
|------|-------------|
| `list_cases` | All available cases |
| `get_case_summary` | Case overview + parties |
| `get_timeline` | Chronological events (optional type filter) |
| `get_statements_by_person` | Statements by a named person with citations |
| `get_discrepancies` | Conflicting accounts between parties |

## Synthetic Data

50 fictional cases with realistic but entirely fabricated data across all 16 SC judicial circuits:

- **50 cases**, 275 people, 325 timeline events, 338 statements, 150 discrepancies
- **2024-DR-42-0892** — CPS emergency removal (Webb/Holloway, Spartanburg): 12 timeline events, 15 statements, 6 discrepancies — primary demo case
- **2024-DR-15-0341** — TPR (Price, Richland): 10 timeline events, 12 statements, 4 discrepancies — secondary demo case
- **48 generated cases** — varied case types (CPS, TPR, Neglect, Physical Abuse, Guardianship, Kinship) across 46 counties

## SharePoint Comparison Documents

The `sharepoint-docs/` folder contains realistic legal documents for Cases 1 and 2, formatted as Markdown files ready for upload to SharePoint. These documents contain the same facts as the SQL database but embedded in unstructured narrative prose — simulating what a real legal office would have in their document library.

Use these to create a second Copilot Studio agent grounded in SharePoint, then compare it side-by-side with the MCP-backed agent. See `sharepoint-docs/Demo_Comparison_Prompts.md` for ready-made prompts that highlight the MCP advantage.

### Document Inventory (11 files)

**Case 2024-DR-42-0892 (CPS Emergency Removal):**
- DSS Investigation Report, Medical Records, Sheriff Report, Court Orders, Home Study Report, GAL Report

**Case 2024-DR-15-0341 (TPR):**
- DSS Investigation Report, Substance Abuse Evaluation, Court Orders, TPR Petition & Affidavit, GAL Reports
