# Demo Cheat Sheet (One Page)

## Pre-Demo (10 min before)

| Step | Action |
|------|--------|
| 1 | Open SWA: `https://happy-wave-016cd330f.1.azurestaticapps.net` |
| 2 | Click **Warm Up** — wait for green checkmarks (primes Container App → APIM → Functions → SQL → OpenAI) |
| 3 | Open Copilot Studio SP/PDF/Com agent — send a throwaway prompt to warm up |
| 4 | Open Copilot Studio MCP/Com agent — send a throwaway prompt to warm up |
| 5 | Pre-stage browser tabs: SWA, both CS agents, slide deck |

## Demo Flow (S21 — ~12 min total)

### Level 2: SharePoint Summarization (2 min) — CS SP/PDF/Com

**Prompt:** "Summarize the medical records for case 2024-DR-42-0892"

**What to show:** Agent pulls from SharePoint docs, returns a narrative summary. It works — but it's a summary, not structured data.

**Talking point:** "This is where most agencies should start. Zero code, immediate value."

---

### Level 3: Aggregate Query (2 min) — Web UI (Case Analyst)

**Prompt:** "How many active cases does DSS have by case type?"

**What to show:** Exact counts from SQL via MCP. Document agents can't do this.

**Talking point:** "The moment you need to count or filter across cases, you need structured data."

---

### Level 4: The Money Prompt (5 min) — Web UI (Case Analyst)

**Prompt:** "Build a complete timeline for case 2024-DR-42-0892. Include all discrepancies between Marcus Webb's and Dena Holloway's accounts."

**What to show:** Structured timeline with exact dates, all 6 discrepancies with source citations. Let it run — the response is impressive.

**Talking point:** "This is what a paralegal spends hours doing. The agent does it in seconds — but a human still reviews it."

---

### Level 5: The Skeletal Survey Trap (3 min) — Talk through, show screenshot

**Prompt:** "What did the skeletal survey show for Jaylen Webb?"

**What to show:** Explain the trap — Sheriff's Report says "no fractures," Medical Records document bilateral fractures. 7 of 8 document agents quoted the sheriff without cross-checking.

**Talking point:** "The citation was real. The confidence was justified. The conclusion was dangerous. This is why Level 5 requires human review. Always."

## Fallback Plan

| If... | Then... |
|-------|---------|
| SWA won't load | Show the architecture slide and talk through it |
| Container App times out | Re-click Warm Up, fill with the Level 5 skeletal survey story |
| CS agent is slow | "This is a cold start — in production you'd pin these" |
| Any agent gives wrong answer | "This is exactly the point — let me show you what the right answer looks like" |

## Key Numbers

| Stat | Value |
|------|-------|
| Test runs | 462 |
| Agent configs | 21 |
| Cases in DB | 50 (Case 1: `2024-DR-42-0892`, Case 2: `2024-DR-15-0341`) |
| Best zero-code score | 10/10 (SP/PDF/Com after cross-referencing) |
| Best pro-code score | 10/10 (Case Analyst, Investigative, Triage) |
| Worst-to-best arc | Triage: 0/10 → 10/10 in 5 rounds |
| Models tested | 5 (GPT-4o, 4.1, 5 Auto, 5 Reasoning, Sonnet 4.6) |
| Model gap | Sonnet 11/11, GPT-5 Reasoning 10/11, GPT-4o 3.2/11 best (same infra) |
| GCC DV MCP rounds | 6 (R0-R5), best = 3.2/10 with instructions |
