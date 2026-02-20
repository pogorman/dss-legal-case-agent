# User Guide

## Accessing the Application

1. Navigate to the Static Web App URL (provided after deployment)
2. Sign in with your Azure AD credentials
3. You'll land on the **Agent Chat** tab

## Agent Chat

The Agent Chat panel lets you interact with the AI agent backed by structured case data.

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

## Case Browser

Switch to the **Case Browser** tab to view the underlying structured data.

- The table shows all cases with ID, title, type, county, filed date, and status
- Click a case ID to see details: parties, stat counts (timeline events, statements, discrepancies)
- This panel is read-only — it exists to show the demo audience the data structure

## Tips for Presenters

1. **Start with Case Browser** to establish that structured data exists
2. **Switch to Agent Chat** and run the demo prompt
3. **Point out tool badges** — show the audience which specific queries ran
4. **Run a follow-up** — prove consistency by asking for the same data in a different way
5. **Compare with SharePoint results** (shown separately) — the contrast sells itself

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
