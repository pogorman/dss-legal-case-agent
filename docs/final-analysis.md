# Final Analysis — Slide Outline, Demo Artifacts, and Open Items

**Date:** 2026-03-11
**Context:** Pre-demo review of 26-slide outline, demo readiness, and remaining work

---

## 1. Slide Outline Review — Final Recommendations

Full review of all 26 slides (S1–S26) from `scripts/generate-slide-outline-pdf.py`.

### Content Issues

**S2 At a Glance — "15 agent configurations" on UC1 tile.** The scorecard (S25) lists 15 UC1 rows, but some are the same agent with different models (DV/Com appears 3 times). If someone counts the appendix in the whitepaper, make sure the number matches. Consider "15 scored configurations" to be precise.

**S9 Level 3 — missing the Dataverse MCP angle.** The outline says "Agents with structured data access — both Copilot Studio MCP and pro-code — answer every aggregate query correctly." But CS/DV/GCC scored 2/10 and CS/DV/Com with GPT-5 Auto scored 4/11. The claim "every aggregate query correctly" only holds for the *right model* on structured data. Suggest qualifying: "...answer every aggregate query correctly — **when paired with a capable model.**"

**S11 Model Gap — "GPT-4.1" score reads "9.5/10".** This is the Investigative Agent's score, not a pure model-vs-model test. The Dataverse MCP tests are the true apples-to-apples comparison (same infra, different model). Consider leading with the Dataverse results since they're the cleanest controlled experiment.

**S13 Level 5 — "7 of 8 document agents."** Double-check: there are now 15 UC1 configs. Is this "7 of 8 *document-based* agents" (excluding MCP/Dataverse agents)? Worth being precise since someone will count.

**S16 Results After Iteration — missing UC1 document agents.** The table shows 4 UC2 agents but doesn't show the UC1 improvement story (SP/PDF/GCC going from 3→9, KB agents improving). This is a missed opportunity since the audience is government — the document improvement story (zero code, zero engineering) is arguably the most relevant to them.

**S17 Code Spectrum — "same fidelity with GPT-4.1."** The headline says fidelity is the same across zero-to-full code. But M365 Copilot scored 2/10 and can't choose its model. The statement is only true if you exclude M365 and GCC GPT-4o. Suggest: "same fidelity **when you control the model**."

**S21 Live Demo — only UC1?** The demo card lists Level 2–5 demos, all from the legal case side. No UC2 (Philly) demo segment. Is that intentional? The aggregate query demo (S9/Level 3) would be perfect with a UC2 prompt like "top 5 violators."

### Structural Issues

**No transition slide between presentation and demo.** S20 (GCC) → S21 (Live Demo) is abrupt. The audience needs a mental gear shift. The demo card helps, but consider whether S21 needs a stronger "here's what you're about to see" framing.

**S22-S23 (Surprising Findings) come after the demo.** This is good — the audience just saw the system work, and now you show them where it failed. Strong placement, no change needed.

**Cover page says "Target: 25 slides"** but there are 26. Minor — update to 26 or remove the target.

### Things That Are Working Well

- S5 Meet the Agents early introduction is excellent — sets up the vocabulary for the rest of the talk
- Danger Taxonomy placement (S14) before the iterative process (S15) is the right order
- The Bottom Line (S24) with "three numbers to remember" is a strong closer
- Speaker notes throughout are narrative-quality — these will carry the presentation

---

## 2. Demo Artifacts Needed

Based on S21 (Live Demo) and the demo guide.

### Must-Have (blocking)

| Artifact | Status | Notes |
|---|---|---|
| **Web UI running** (`happy-wave` SWA) | Deployed | Warm up before demo |
| **Container App alive** (`dss-case-agent`) | Deployed | Hit warm-up button 5 min before |
| **Azure SQL data loaded** (50 cases) | Deployed | Verify Case 1 `2024-DR-42-0892` returns data |
| **Copilot Studio agent (SP/PDF/Com)** | ? | Need for Level 2 side-by-side comparison |
| **Copilot Studio agent (MCP/Com)** | ? | Need for Level 3-4 comparison |
| **SharePoint library with Case 1 docs** | ? | Cross-referenced versions uploaded? |
| **Demo prompts printed/accessible** | Exists as MD | `Demo_Comparison_Prompts.md` — need a cheat sheet or the demo guide PDF open |
| **Browser tabs pre-staged** | N/A | SWA, Copilot Studio, maybe Azure Portal for architecture |

### Level-by-Level Demo Script (from S21)

| Level | Demo | What to Show | Agent | Time |
|---|---|---|---|---|
| L2 | SharePoint summarization | "Summarize the medical records for case 2024-DR-42-0892" | CS SP/PDF/Com | 2 min |
| L3 | Aggregate query | "How many active cases by type?" or "Top 5 violators" | CS MCP/Com or Web UI | 2 min |
| L4 | The money prompt | Timeline + discrepancies + statements for Case 1 | Web UI (Case Analyst) | 5 min |
| L5 | Skeletal survey trap | "What did the skeletal survey show?" | Show both agent responses | 3 min |

### Likely Missing

1. **Copilot Studio agents — are they still live and configured?** They were tested extensively but demos rot. Verify they still respond.
2. **SharePoint doc library — cross-referenced versions.** The R1 cross-referenced docs exist locally but are they in the SharePoint library the Copilot Studio agents point to?
3. **Philly UC2 docs in SharePoint.** "Upload 5 Philly PDFs to SharePoint for document agent testing" is still an open item. If UC2 is demoed, those need to be uploaded.
4. **Fallback screenshots/recordings.** If any live agent fails during demo, are there screenshots of correct responses? Consider capturing a few golden-path screenshots.
5. **Demo guide PDF is stale.** The demo guide was written around the original DSS-only comparison prompts. It doesn't cover the five-level narrative or UC2. It needs an update to match the S21 demo flow.

---

## 3. What Else Is Left?

### Already Identified (from MEMORY.md open items)

- ~~Slide outline review~~ (done)
- Demo dry run (50-60 min target)
- Upload 5 Philly PDFs to SharePoint
- Consider BFG to purge real names from git history (private repo — low urgency)

### Likely Forgetting

1. **Demo guide PDF update.** It's written for the old "MCP vs SharePoint" comparison format. It doesn't follow the five-level narrative structure. Should be rewritten to match S21's Level 2→3→4→5 flow with exact prompts, expected answers, and timing.

2. **Warm-up timing and sequence.** The warm-up button handles the SWA→Container App→APIM→Functions→SQL→OpenAI chain, but what about Copilot Studio cold start? Do CS agents need a throwaway prompt to warm up? Plan for this.

3. **Backup plan if live demo fails.** Screenshots, screen recording, or pre-recorded clips for each demo segment. Live demos with cold-start Azure services + Copilot Studio + SharePoint = lots of failure modes.

4. **Audience-specific framing.** The outline says "Tech Series" on S18. Is this always a tech audience? If presenting to non-technical decision makers, some slides would be skipped. Worth having a "short version" slide list (maybe 15 slides) noted somewhere.

5. **Whitepaper distribution.** The whitepaper PDF is finalized. How is it being shared? QR code on the Next Steps slide? Email follow-up? OneDrive shared link? S26 mentions "QR code to whitepaper" as a visual note but the actual link isn't prepared.

6. **Session log update.** Per documentation requirements, `docs/session-log.md` should be updated with this session's work.

7. **Dataverse MCP testing doc.** "Generate PDF for `docs/dataverse-mcp-server-testing.md` when content is finalized" is still open. Not blocking the demo, but if someone asks about the Dataverse results, having a polished PDF to share would be useful.

---

## Priority Recommendation

Fix the cover page "25 slides" → "26 slides," qualify the S9 and S17 headlines, then focus entirely on verifying every live demo artifact works end-to-end. The slide content is 95% done — the demo readiness is the risk.
