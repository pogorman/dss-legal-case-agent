# TODO

## Data Fixes
- [ ] **Rename 'Medical Staff' → 'Hospital Staff'** across all layers (Dataverse GCC + Commercial, Azure SQL, seed.sql, seed-expanded.sql, generate-seed.js, patch-dataverse-descriptions.js). R5 proved GPT-4o can't remap via instructions — data must match natural language.

## Demo Prep
- [ ] **Set Dataverse MCP agent to GPT-4o** before demo (swap to Sonnet live)
- [ ] **Part 2 Prompt 3** (time calculation) — still needs Commercial model results
- [ ] **Capture fallback screenshots** of golden-path agent responses

## Testing
- [ ] **Purview testing** — run agent prompts, observe what shows up in the Purview portal (audit log, AI hub, DLP). Portal-only, no custom dashboard.

## Housekeeping
- [ ] Uncommitted change in `web/css/style.css` — review and commit or discard
