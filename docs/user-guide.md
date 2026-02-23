# User Guide

## Accessing the Application

1. Navigate to the Static Web App URL (provided after deployment)
2. Sign in with your Azure AD credentials
3. You'll land on the **Case Browser** — the main portal page

## Agent Chat

The AI Case Agent is accessed via the floating chat button in the bottom-right corner of the screen. Click the navy circle with the chat icon to open the agent widget.

### Suggested Prompts

On first load, three starter prompts are displayed:
- **"List available cases"** — Returns all cases with IDs, good starting point
- **"Give me a detailed timeline for case 2024-DR-42-0892"** — Chronological events
- **"Show me the discrepancies between the parents' accounts in case 2024-DR-42-0892"** — Conflicting accounts

Click any prompt chip to send it, or type your own in the text box.

### The Demo Prompt

For the full demo, use this prompt (replacing names as needed):

> I represent DSS in case 2024-DR-42-0892. After reviewing the case, can you provide:
> 1. A detailed timeline of pertinent facts with source citations
> 2. A chart of discrepancies between the two parents' accounts
> 3. All statements made by Marcus Webb to case managers or law enforcement
> 4. All statements made by Dena Holloway to case managers or law enforcement

The agent will call multiple tools and return a structured response with:
- A chronological timeline with dates, times, and source document references
- A comparison table of discrepancies between the parents
- Statements organized by person with dates, recipients, and page citations

### Tool Badges

Below each assistant response, small badges show which tools were called (e.g., `get_timeline`, `get_discrepancies`). This is for transparency — the audience can see exactly what data the agent queried.

### Follow-Up Questions

You can ask follow-ups in the same conversation:
- "Can you make the timeline more detailed — include specific times where available?"
- "What did the medical records say about the injuries?"
- "Summarize the GAL's recommendation"

The key demo point: **follow-up questions return consistent results** because the agent queries the same structured data every time.

### Clearing the Conversation

Click the **New Chat** button in the widget header to reset the conversation. This clears all messages and returns to the welcome screen with suggested prompts.

## Case Browser

The Case Browser is the main content area, always visible behind the chat widget.

- The table shows all cases with ID, title, type, county, filed date, and status
- Click a case ID to see details: parties, stat counts (timeline events, statements, discrepancies)
- This panel is read-only — it exists to show the demo audience the data structure

## Tips for Presenters

1. **Start with Case Browser** (it's the default view) to establish that structured data exists
2. **Click the chat button** in the bottom-right corner to open the agent
3. **Run the demo prompt** and point out tool badges showing which queries ran
4. **Run a follow-up** — prove consistency by asking for the same data in a different way
5. **Click "New Chat"** to reset between demo scenarios
6. **Compare with SharePoint results** (shown separately) — the contrast sells itself

## SharePoint Comparison Demo

The `sharepoint-docs/` folder contains 11 realistic legal documents for Cases 1 and 2, ready to upload to SharePoint. These contain the same facts as the SQL database but in unstructured narrative prose.

### Setting Up the SharePoint Agent

1. Upload all files from `sharepoint-docs/Case-2024-DR-42-0892/` and `sharepoint-docs/Case-2024-DR-15-0341/` to a SharePoint document library
2. Create a new Copilot Studio agent grounded in that SharePoint library
3. Use the same prompts on both agents to compare results

### Comparison Prompts

See `sharepoint-docs/Demo_Comparison_Prompts.md` for 19 ready-made prompts across 6 categories:
1. **Factual Retrieval** — timelines, dates, names
2. **Cross-Referencing Statements** — comparing what different people said
3. **Discrepancy Identification** — finding contradictions
4. **Filtering and Precision** — medical-only events, law-enforcement-only statements
5. **Multi-Case / Aggregate Queries** — counts, circuit filtering (MCP-only, 50 cases)
6. **Precision Stress Tests** — page numbers, session counts, time gap calculations

Each prompt includes expected MCP vs. SharePoint responses and why MCP wins.

### Document Inventory

**Case 2024-DR-42-0892 (CPS Emergency Removal) — 6 documents:**
| Document | Content |
|----------|---------|
| `DSS_Investigation_Report.md` | Case manager notes, interviews, recommendations |
| `Medical_Records.md` | Hospital admission, radiology, Dr. Chowdhury's assessment, nursing notes |
| `Sheriff_Report_24-06-4418.md` | Lt. Odom investigation, parent interviews |
| `Court_Orders_and_Filings.md` | Emergency order, probable cause hearing, 30-day review |
| `Home_Study_Report.md` | Kinship placement assessment for Theresa Holloway |
| `GAL_Report.md` | Karen Milford's Guardian ad Litem report |

**Case 2024-DR-15-0341 (TPR) — 5 documents:**
| Document | Content |
|----------|---------|
| `DSS_Investigation_Report.md` | Full investigation from referral through TPR filing |
| `Substance_Abuse_Evaluation.md` | Dr. Ellis clinical eval, OUD diagnosis |
| `Court_Orders_and_Filings.md` | All 6 court events including voluntary relinquishment |
| `TPR_Petition_and_Affidavit.md` | Formal petition with statutory grounds + sworn affidavit |
| `GAL_Reports.md` | Thomas Reed's initial and updated reports |

## Database Access

The SQL server (`philly-stats-sql-01`) has **public network access disabled**. All application traffic flows through a private endpoint on the VNet.

### Portal Query Editor

The Azure Portal Query Editor **will not work** — it requires public network access. You'll see this error:

> An instance-specific error occurred while establishing a connection to SQL Server. Connection was denied because Deny Public Network Access is set to Yes.

### Running Ad-Hoc Queries

Options for running queries against the database:

1. **Azure Data Studio / SSMS** from a VNet-connected machine (VM or VPN)
2. **Temporarily enable public access** on the SQL server, run your query, then disable it again
3. **Cloud Shell** with VNet integration (if configured)

### Redeploying Seed Data

The `deploy-sql.js` script runs from your local machine, so it requires temporarily enabling public access:

1. Azure Portal → SQL Server → Networking → Public network access → **Selected networks**
2. Add your client IP to the firewall rules
3. Run `node database/deploy-sql.js`
4. Set Public network access back to **Disabled**

## Available Cases

The system contains **50 synthetic cases** across all 16 SC judicial circuits.

### Primary Demo Cases (rich detail)

| Case ID | Description |
|---------|-------------|
| 2024-DR-42-0892 | CPS emergency removal — Webb/Holloway (Spartanburg) — 12 timeline events, 15 statements, 6 discrepancies |
| 2024-DR-15-0341 | Termination of Parental Rights — Price (Richland) — 10 timeline events, 12 statements, 4 discrepancies |

### Additional Cases (48 generated)

Browse all 50 cases in the **Case Browser** tab. Case types include:
- Child Protective Services
- Termination of Parental Rights
- Child Neglect
- Physical Abuse
- Guardianship
- Kinship Placement

Counties span the entire state, from Abbeville to York.

---

## Connecting Copilot Studio to the MCP Endpoint

The MCP endpoint is ready for Copilot Studio at:
```
https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/mcp
```

### Prerequisites

- Access to [Copilot Studio](https://copilotstudio.microsoft.com)
- An agent created (or create a new one)
- **Generative Orchestration** must be enabled on the agent (this is required for MCP tools)

### Step-by-Step Setup

1. Open your agent in Copilot Studio
2. Go to the **Tools** page
3. Select **Add a tool** → **New tool** → **Model Context Protocol**
4. Fill in the MCP onboarding wizard:
   - **Server name**: `DSS Case Intelligence`
   - **Server description**: `Queries structured DSS legal case data including timelines, statements, discrepancies, and party information across 50 synthetic cases. Returns cited results with source documents and page references.`
   - **Server URL**: `https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/mcp`
   - **Authentication**: Select **None** (the endpoint is unauthenticated for this POC)
5. Select **Create**
6. On the **Add tool** dialog, select **Create a new connection**
7. Select **Add to agent**

### Verify It Works

Once connected, the agent auto-discovers 5 tools:

| Tool | Description |
|------|-------------|
| `list_cases` | Returns all available cases |
| `get_case_summary` | Case overview + parties for a specific case |
| `get_timeline` | Chronological events with optional type filter |
| `get_statements_by_person` | Statements by a named person with citations |
| `get_discrepancies` | Conflicting accounts between parties |

Test with: **"List available cases"** — the agent should call `list_cases` and return all 50 cases.

Then try the money prompt from the demo guide to verify all tools work end-to-end.

### Troubleshooting

- **Tools not appearing**: Ensure Generative Orchestration is enabled in agent settings
- **Connection errors**: The Container App may need to warm up — send a quick health check to `https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/healthz` first
- **SSE errors**: Copilot Studio no longer supports SSE transport (deprecated August 2025). The DSS endpoint uses Streamable HTTP which is the current supported transport
- **Agent not calling tools**: Make sure the server description is filled in — the orchestrator uses it to decide when to invoke the MCP server

### Alternative: Custom Connector (Power Apps)

If the MCP onboarding wizard isn't available in your environment, you can create a custom connector in Power Apps using this OpenAPI schema:

```yaml
swagger: '2.0'
info:
  title: DSS Case Intelligence
  description: MCP server for DSS legal case data - timelines, statements, discrepancies, and party information
  version: 1.0.0
host: dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io
basePath: /
schemes:
  - https
paths:
  /mcp:
    post:
      summary: DSS Case Intelligence MCP Server
      x-ms-agentic-protocol: mcp-streamable-1.0
      operationId: InvokeMCP
      responses:
        '200':
          description: Success
```

1. Go to **Tools** → **Add a tool** → **New tool** → **Custom connector**
2. In Power Apps, select **New custom connector** → **Import OpenAPI file**
3. Import the YAML above and complete the setup
