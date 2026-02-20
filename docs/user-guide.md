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
