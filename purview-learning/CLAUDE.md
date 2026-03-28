# Purview Learning — Project Instructions

## Purpose
This is O'G's Purview training directory — not a code project. It's a structured learning curriculum for Microsoft Purview with emphasis on Power Platform governance (Copilot Studio, custom connectors, DLP).

## Structure
- `docs/md/` — Source markdown for all modules (numbered 00-10)
- `docs/pdf/` — Generated PDFs (future: Python script like other project PDFs)
- `docs/html/` — Generated HTML versions (future)
- `docs/pptx/` — Generated slide decks (future)
- `MEMORY.md` — Tracks learning progress, key takeaways, open questions
- `README.md` — Curriculum overview and module index

## Conventions
- This is a **non-code directory** — only CLAUDE.md and MEMORY.md are required project files
- README.md exists as a curriculum index (exception to non-code rule, O'G requested it)
- Every module must clearly distinguish **industry standard** concepts from **Microsoft-specific** implementations
- Use callout blocks: `> **Industry Standard:**` and `> **Microsoft-Specific:**`
- Modules build on each other — don't skip ahead without O'G's direction
- O'G is learning at their own pace — wait for them to drive, don't push the agenda
- O'G has existing context: Semantic Kernel, MCP, APIM, managed identity, Azure SQL, Copilot Studio, GCC tenants
- When referencing Power Platform, cover Copilot Studio first (O'G's primary use case), then other PP components

## GCC Context
- O'G works with both GCC and Commercial tenants
- GCC tenant: `testtestmsftgccfo.onmicrosoft.com` (shared)
- Some Purview features (AI Hub) are not yet available in GCC — always note GCC availability
- Purview testing findings are tracked in the parent project's `memory/purview-testing.md`

## Module Numbering
- 00: Curriculum overview
- 01: Foundations (governance landscape, Purview evolution, portal nav)
- 02: Unified Audit Log
- 03: Information Protection (sensitivity labels, classification)
- 04: Data Loss Prevention (Purview DLP + Power Platform DLP)
- 05: AI Governance (AI Hub, DSPM for AI)
- 06: eDiscovery & Legal Hold
- 07: Insider Risk & Communication Compliance
- 08: Data Governance (catalog, lineage, data map)
- 09: Power Platform Deep Dive (Copilot Studio compliance, managed environments)
- 10: Applied — Demo Narrative (tying Purview to the DSS legal case demo)

## Updating
- After each learning session, update MEMORY.md with progress and key takeaways
- Add new modules to docs/md/ as O'G progresses
- Don't generate PDF/HTML/PPTX until O'G asks for them
