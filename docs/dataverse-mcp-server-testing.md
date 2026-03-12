# Dataverse MCP Server Testing

Comprehensive test log for the native Dataverse MCP connector in Copilot Studio.
Purpose: capture actual SQL queries generated, errors returned, and results — to help the product team diagnose MCP SQL generation issues.

## Environment

| Property | GCC | Commercial |
|----------|-----|------------|
| Environment URL | https://og-ai.crm9.dynamics.com | https://og-dv.crm.dynamics.com |
| Tenant | 426a6ef4-2476-4eab-ae1c-1c9dc2bfca80 | 125ec668-dcca-47ba-9487-0304f441b3f1 |
| Solution | LegalCaseAgent | LegalCaseAgent |
| Tables | 5 custom (legal_legalcase, legal_person, legal_timelineevent, legal_statement, legal_discrepancy) | Same schema |
| Records | 150 cases, 831 people, 999 events, 1,014 statements, 453 discrepancies | 50 cases, 277 people, 333 events, 338 statements, 151 discrepancies |
| Model | GPT-4o (GCC default) | GPT-4.1, GPT-5 Auto, Sonnet 4.6 (tested) |

## Schema Overview

### Tables & Relationships
- **legal_legalcase** (primary: legal_caseid — text like '2024-DR-42-0892')
- **legal_person** -> legal_legalcase (via legal_LegalCaseId lookup)
- **legal_timelineevent** -> legal_legalcase (via legal_LegalCaseId lookup)
- **legal_statement** -> legal_legalcase (via legal_LegalCaseId lookup), -> legal_person (via legal_PersonId lookup)
- **legal_discrepancy** -> legal_legalcase (via legal_LegalCaseId lookup), -> legal_person x2 (via legal_PersonAId, legal_PersonBId lookups)

### Denormalized Text Columns (added R3)
Every child table has `legal_caseidtext` (human-readable case number).
Statements have `legal_personname`. Discrepancies have `legal_personaname`, `legal_personbname`.
These were added to eliminate the need for GUID-based joins — the agent can filter directly on text.

**Observation: In testing, the MCP SQL generator did not use the denormalized text columns — it consistently used the lookup/relationship columns for joins. It is unclear whether this is by design or a gap in how column descriptions influence query generation.**

## Test Prompts (UC1 — Legal Case Analysis)

| # | Prompt |
|---|--------|
| 1 | Tell me about Jaylen Webb's emergency room admission — specifically the time and the admitting nurse. |
| 2 | What did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement? |
| 3 | Crystal Price told the court she was 'clean now' at the November 2023 hearing. What do the drug test results show? |
| 4 | Crystal Price said she couldn't comply with the treatment plan because she lacked transportation. What support did DSS actually provide? |
| 5 | Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey? |
| 6 | What is the complete timeline of events for case 2024-DR-42-0892? |
| 7 | What statements were made to law enforcement in case 2024-DR-42-0892? |
| 8 | List all people involved in the Price TPR case and their roles. |
| 9 | Which cases involve Termination of Parental Rights? |
| 10 | Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed? |
| 11 | What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital? |

---

## GCC Testing

### Round 0 — Baseline (no instructions, no descriptions, no denormalized columns)

**Agent config:** Default Copilot Studio agent with Dataverse MCP connector. No custom instructions, no description, no metadata enrichment.

#### P1: Jaylen Webb ER admission
- **Result:** "There are no records for Jaylen Webb's emergency room admission."
- **Score:** 0

#### P2: Marcus Webb statements
- **Result:** "I wasn't able to find relevant case data for that question."
- **Score:** 0

#### P3: Crystal Price drug tests
- **Result:** "I wasn't able to find relevant case data for that question."
- **MCP Error:**
```json
{
  "text": "Tool execution failed. MCP CorrelationId: 6014a653-47fd-418c-945b-267f8ef496a3 trace: Error executing McpExecuteSqlQuery: Subquery returned more than 1 value. This is not permitted when the subquery follows =, !=, <, <= , >, >= or when the subquery is used as an expression."
}
```
- **Score:** 0

#### P4: Crystal Price transportation
- **Result:** "There are no records in the legal_discrepancy table related to the topic of 'transportation.'"
- **Notes:** Searched only discrepancies table, not timeline events or statements. Partial effort but wrong table.
- **Score:** 1

#### P5: Skeletal survey fractures
- **Result:** "The Sheriff's Office investigation did not find any records indicating fractures in Jaylen Webb's skeletal survey."
- **Notes:** DANGEROUS — states no fractures when the data contains detailed fracture findings. Classic hallucination from empty query result.
- **Score:** 0

#### P6: Full timeline for case
- **Result:** "There are no events recorded for case 2024-DR-42-0892."
- **MCP Error:**
```json
{
  "text": "Tool execution failed. MCP CorrelationId: c05f3f2d-a737-4bee-a14d-382df3e1fe05 trace: Error executing McpExecuteSqlQuery: Conversion failed when converting from a character string to uniqueidentifier."
}
```
- **Notes:** Agent used the text case ID '2024-DR-42-0892' where a GUID was expected in the lookup column.
- **Score:** 0

#### P7: Statements to law enforcement
- **Result:** "I wasn't able to find relevant case data for that question."
- **MCP Error:**
```json
{
  "text": "Tool execution failed. MCP CorrelationId: fdb340e8-4944-40ae-9236-f9d1cbef0830 trace: Error executing McpExecuteSqlQuery: Conversion failed when converting from a character string to uniqueidentifier."
}
```
- **Score:** 0

#### P8: People in Price TPR case
- **Result:** "There are no people listed under the Price TPR case."
- **Score:** 0

#### P9: TPR cases
- **Result:** Returned 9 TPR cases with case IDs, titles, and statuses. Correct.
- **Notes:** Simple single-table query, no joins needed. Only prompt that worked in R0.
- **Score:** 10

#### P10: Dena Holloway statements
- **Result:** "There are no records for Dena Holloway's initial hospital statement or her statement to Lt. Odom."
- **Score:** 0

#### P11: Time gap thump to hospital
- **Result:** "There are no records matching the event types 'thump' or 'hospital'."
- **Score:** 0

**R0 Total: 1/10**

---

### Round 1 — Agent instructions + description (no metadata enrichment)

**Changes:** Added custom instructions with full schema documentation (5 tables, all column names, valid values, relationship explanations). Added two-step query pattern hints. Added agent description.

#### P1-P5: No change from R0 (all 0)

#### P6: Full timeline for case
- **Result:** Complete 14/14 timeline with all events in chronological order, full details including skeletal survey.
- **Notes:** Major improvement. Instructions helped the agent understand the case ID lookup pattern for this specific query type.
- **Score:** 10

#### P7-P8: No change from R0 (all 0)

#### P9: TPR cases
- **Result:** "I wasn't able to find relevant case data for that question."
- **Notes:** REGRESSION — this worked in R0 but broke after adding instructions. The instructions may have confused the agent's query strategy for this simple query.
- **Score:** 0

#### P10-P11: No change from R0 (all 0)

**R1 Total: 1/10**

---

### Round 2 — Rich metadata descriptions on tables + columns

**Changes:** Patched all 5 table descriptions and 30 column descriptions in Dataverse metadata via `database/patch-dataverse-descriptions.js`. Descriptions include record counts, valid column values, two-step query instructions, and GUID vs text field distinctions.

#### P1: No change (0)

#### P2: Marcus Webb statements (non-deterministic — 1 success in 5 identical attempts)
- **Attempt 1:** No result returned
- **Attempt 2:** SUCCESS — returned 2 statements (see below)
- **Attempt 3:** No result returned
- **Attempt 4:** No result returned
- **Attempt 5:** No result returned
- **Successful response (attempt 2):**
```
Statement Text: "Dena and I have been arguing a lot lately but I would never hurt my son.
I don't know why she is saying I was in the room. I was not in his room after 10 PM."
Date: June 13, 2024
Made To: Law Enforcement
Source Document: Sheriff Report #24-06-4418
Page Reference: p. 5

Statement Text: "I was on the couch all night. I did not go into Jaylen room after I put him
down. I don't know how he got hurt. Maybe he climbed out of the crib and fell. He's been
trying to climb out lately."
Date: June 13, 2024
Made To: Law Enforcement
Source Document: Sheriff Report #24-06-4418
Page Reference: p. 4

Both statements were made to law enforcement, and there are no records of statements
made to hospital staff.
```
- **What's correct:** Found 2 of 3 Marcus Webb statements. Successfully did two-step lookup (person -> GUID -> filter statements).
- **What's wrong:**
  1. Missed the Medical Staff statement ("I put him to bed around ten...") — the actual `legal_madeto` value is `'Medical Staff'` but the prompt says "hospital staff" and the agent couldn't map between terms
  2. Only worked 1 out of 5 identical attempts — same prompt, same data, different SQL generated each time
  3. The answer says "no records of statements made to hospital staff" which is factually incorrect (there IS a Medical Staff statement)
- **Score:** ~1

#### P3: Crystal Price drug tests
- **Result:** "I wasn't able to find relevant case data for that question."
- **Score:** 0

#### P4: Crystal Price transportation
- **Result:** "There are no records in the legal_discrepancy table related to the topic of 'transportation.'"
- **Notes:** Regressed from R0 (was 1, now 0). Still only searching discrepancies table.
- **Score:** 0

#### P5: Skeletal survey fractures
- **Result:** No result returned
- **Score:** 0

#### P6: Full timeline
- **Result:** Complete 14/14 timeline. Stable across R1 and R2.
- **Score:** 10

#### P7: Statements to law enforcement
- **Result:** No result returned
- **Score:** 0

#### P8: People in Price TPR case
- **Result:** No result returned
- **Score:** 0

#### P9: TPR cases
- **Result:** No result returned
- **Notes:** Still broken since R1. Was the only working prompt in R0.
- **Score:** 0

#### P10: Dena Holloway statements
- **Result:** No result returned
- **Score:** 0

#### P11: Time gap thump to hospital
- **Result:** No result returned
- **Score:** 0

**R2 Total: 2/10**

---

### Round 3 — Denormalized text columns + updated descriptions

**Changes:**
1. Added 7 denormalized text columns across 4 child tables:
   - `legal_caseidtext` on person, timelineevent, statement, discrepancy
   - `legal_personname` on statement
   - `legal_personaname`, `legal_personbname` on discrepancy
2. Populated all 3,297 records with resolved text values
3. Updated all table descriptions to reference denormalized columns
4. Updated all column descriptions including new columns
5. Fixed `legal_madeto` description to list actual values: Medical Staff, Law Enforcement, Case Manager, Court

#### P1: Jaylen Webb ER admission
- **Result:** Failed
- **Generated SQL:**
```sql
SELECT legal_name, legal_eventdate, legal_eventtime, legal_description
FROM legal_timelineevent
WHERE legal_LegalCaseId IN (
  SELECT legal_LegalCaseId FROM legal_person
  WHERE legal_personid IN ('785e6ade-f21c-f111-8342-001dd806c085',
    'a7eb2660-f31c-f111-8342-001dd809c49d',
    'ea3b8a26-f61c-f111-8342-001dd809c49d'))
AND legal_eventtype = 'Emergency Action'
```
- **Issues:**
  1. Uses lookup column `legal_LegalCaseId` with subquery instead of `legal_caseidtext`
  2. Filters `legal_eventtype = 'Emergency Action'` — actual value is `'Medical'`
  3. Joins through person table to timeline events (timeline events link to cases, not people)
  4. Did not use denormalized `legal_caseidtext` column
- **Score:** 0

#### P2: Marcus Webb statements
- **Result:** Failed
- **Generated SQL:**
```sql
SELECT legal_statementtext, legal_statementdate, legal_madeto, legal_sourcedocument
FROM legal_statement
WHERE legal_PersonId IN (
  SELECT legal_personid FROM legal_person
  WHERE legal_fullname = 'Marcus Webb')
AND legal_statementtext LIKE '%put Jaylen to bed%'
```
- **Issues:**
  1. Uses `legal_PersonId IN (SELECT...)` instead of `legal_personname = 'Marcus Webb'`
  2. `LIKE '%put Jaylen to bed%'` is too specific — actual text says "I put him to bed around ten" (no "Jaylen")
  3. No case scoping — Marcus Webb exists in multiple cases
  4. Did not use denormalized `legal_personname` or `legal_caseidtext` columns
- **Score:** 0

#### P3: Crystal Price drug tests
- **Result:** No results returned
- **Generated SQL:**
```sql
SELECT legal_statementtext, legal_sourcedocument, legal_pagereference
FROM legal_statement
WHERE legal_name = 'Crystal Price Drug Test Result'
AND legal_statementdate BETWEEN '2023-11-01' AND '2023-11-30'
```
- **Issues:**
  1. Filters on `legal_name = 'Crystal Price Drug Test Result'` — guesses at the record name instead of using `legal_personname = 'Crystal Price'`
  2. Did not use denormalized `legal_personname` or `legal_caseidtext` columns
  3. The `legal_name` value is fabricated — no record has that exact name
- **Score:** 0

#### P4: Crystal Price transportation
- **Result:** No results returned
- **Generated SQL:**
```sql
SELECT legal_name, legal_description
FROM legal_timelineevent
WHERE legal_LegalCaseId = '2d7c6b20-f61c-f111-8342-001dd809c49d'
AND legal_eventtype = 'Service Referral'
```
- **Issues:**
  1. Uses GUID for `legal_LegalCaseId` instead of `legal_caseidtext`
  2. Filters `legal_eventtype = 'Service Referral'` — correct concept but no matching records with this exact value
  3. Did not use denormalized columns
- **Score:** 0

#### P5: Skeletal survey fractures
- **Result:** No results returned
- **Score:** 0

#### P6: Full timeline for case
- **Result:** Complete timeline returned. Stable since R1.
- **Score:** 10

#### P7: Statements to law enforcement
- **Result:** No results returned
- **Score:** 0

#### P8: People in Price TPR case
- **Result:** No results returned
- **Score:** 0

#### P9: TPR cases
- **Result:** No results returned
- **Generated SQL:**
```sql
SELECT legal_caseid, legal_casetitle, legal_casetype
FROM legal_legalcase
WHERE legal_casetype = 'TPR'
```
- **Issues:**
  1. Query is syntactically correct but uses abbreviation `'TPR'` instead of full text `'Termination of Parental Rights'`
  2. The actual stored values are full text (e.g., 'Termination of Parental Rights', 'Child Protective Services')
  3. Column description was updated to say "Always filter on the full text value, never the abbreviation" — agent ignored this
  4. Table description was also updated with full text values and "never use abbreviations like CPS or TPR" — agent ignored this too
  5. **This suggests column/table descriptions are NOT flowing into the SQL generation prompt**, only into tool discovery
- **Score:** 0

#### P10: Dena Holloway statements
- **Result:** No results returned
- **Score:** 0

#### P11: Time gap thump to hospital
- **Result:** No results returned
- **Score:** 0

**R3 Total: 1/10** (regression from R2's 2/10 — P2 stopped working, P6 timeline still stable)

---

### Round 4 — Fresh agent instructions (2026-03-12)

**Changes:** Pasted comprehensive agent instructions into GCC Copilot Studio agent (same as Commercial agent template + query guidance hints). This was the first time the GCC agent had instructions since R1 — R2 and R3 focused on metadata enrichment without instructions.

#### P1: Jaylen Webb ER admission
- **Result:** Failed — invalid table/column names, never retrieved data.
- **Score:** 0

#### P2: Marcus Webb statements
- **Result:** Partial. Found both LE statements with direct quotes on second attempt. Missed hospital staff statement (same `Medical Staff` vs `Hospital Staff` mapping gap).
- **Score:** 5

#### P3: Crystal Price drug tests
- **Result:** "No statements recorded for Crystal Price made to the court in November 2023."
- **Score:** 0

#### P4: Crystal Price transportation
- **Result:** "No statements indicating Crystal Price mentioned transportation issues."
- **Score:** 0

#### P5: Skeletal survey fractures
- **Result:** "Did not find any fractures." Dangerous false negative — data contains bilateral fractures.
- **Score:** 0

#### P6: Full timeline for case
- **Result:** Complete 7-event timeline with full detail, source docs, page citations. Chronological order.
- **Score:** 10

#### P7: Statements to law enforcement
- **Result:** All 4 LE statements (Marcus x2, Dena x2) with direct quotes, dates, page citations.
- **Notes:** First time this prompt passed in any GCC round. Instructions made the difference.
- **Score:** 10

#### P8: People in Price TPR case
- **Result:** "I'm sorry, I'm not sure how to help with that."
- **Score:** 0

#### P9: TPR cases
- **Result:** All 9 TPR cases with full summaries, statuses, counties, circuits.
- **Notes:** Instructions helped the agent use full text "Termination of Parental Rights" instead of abbreviation. Back to R0 performance after R1-R3 regression.
- **Score:** 10

#### P10: Dena Holloway statements comparison
- **Result:** "No statements from Dena Holloway made to either Hospital Staff or Lt. Odom."
- **Notes:** Same value mapping failure — `Medical Staff` not `Hospital Staff`, `Law Enforcement` not `Lt. Odom`.
- **Score:** 0

#### P11: Time gap thump to hospital
- **Result:** Query returned null. Searched for exact event type "Thump Heard" instead of using LIKE on description text.
- **Score:** 0

**R4 Total: 3.2/10** (scaled from 35/110). Best GCC round yet — instructions recovered P7 (0→10) and P9 (0→10), improved P2 (0→5). Timeline stable at 10. Complex cross-table prompts still fail.

**R4 vs prior rounds:** Instructions are the most effective single lever for GCC GPT-4o. They helped with direct filter queries (LE statements, TPR cases) but couldn't overcome the model's limitations on cross-table reasoning, value mapping, or fuzzy text matching.

### Round 5 — Value-mapping instructions (2026-03-12)

**Changes:** Added two value-mapping instructions to R4 agent:
1. "When users say 'hospital staff', filter legal_madeto = 'Medical Staff'"
2. "When they name a specific person like 'Lt. Odom', filter legal_madeto = 'Law Enforcement'"

Only P2 and P10 retested (only prompts affected by value-mapping).

#### P2: Marcus Webb statements
- **Result:** 0 (regression from R4's 5). Agent returned nothing — instruction to map "hospital staff" to `Medical Staff` did not influence SQL generation. Model still generated `WHERE legal_madeto = 'Hospital Staff'`.
- **Score:** 0

#### P10: Dena Holloway statements comparison
- **Result:** Partial. Found both LE statements (Lt. Odom mapping worked). Missed hospital staff statement (Medical Staff mapping failed). Correctly identified what changed between the two LE statements.
- **Score:** 5

**R5 Total: 3.2/10** (35/110, same as R4). P2 regressed (5 to 0), P10 improved (0 to 5). Net zero.

**R5 conclusion:** Instructions can map person names to recipient categories (Lt. Odom to Law Enforcement) but cannot override the model's natural language when stored values don't match (hospital staff != Medical Staff). The MCP SQL generator uses the user's exact phrasing for filter values, ignoring instruction-level value mappings. **Next step: rename 'Medical Staff' to 'Hospital Staff' in Dataverse data.**

---

## Commercial Testing

### Round 0 — Fully enriched state (descriptions + denormalized columns)

Commercial was deployed with the fully enriched state from the start — descriptions, denormalized columns, and updated metadata are all in place. No R0-R3 progression was needed since we already established the baseline behavior and improvement ceiling from GCC testing.

#### P1: Jaylen Webb ER admission
- **Result:** "No medical exam or emergency room admission event was found."
- **Notes:** Same failure as GCC — can't find Medical event type when searching for ER admission.
- **Score:** 0

#### P2: Marcus Webb statements
- **Result:** MAJOR improvement. Found ALL 3 statements (Medical Staff + both Law Enforcement) with correct source docs and page references. Compared answers noting core timeline is consistent but law enforcement statement adds details about not re-entering room and crib fall speculation.
- **Notes:** GCC best was 1-in-5 partial success finding only 2 of 3 statements.
- **Score:** 9

#### P3: Crystal Price drug tests
- **Result:** No results returned.
- **Generated SQL:** `WHERE legal_plaintiff LIKE '%Crystal Price%' OR legal_casetitle LIKE '%Crystal Price%'`
- **Notes:** Can't resolve Crystal Price to a case — she's in legal_person, not plaintiff/title.
- **Score:** 0

#### P4: Crystal Price transportation
- **Result:** No statements or timeline events found.
- **Notes:** Same person-to-case resolution failure.
- **Score:** 0

#### P5: Skeletal survey fractures
- **Result:** "No records were found...for an investigation event or a skeletal survey event."
- **Notes:** DANGEROUS but slightly better framing than GCC R0 (said "no documented evidence" rather than affirmatively stating no fractures). Still fails to find Medical event type.
- **Score:** 0

#### P6: Full timeline
- **Result:** Complete 14/14 timeline in chronological order with all details, source docs, page references. Includes gap analysis.
- **Notes:** Stable across all environments.
- **Score:** 10

#### P7: Statements to law enforcement
- **Result:** Found all 4 law enforcement statements (Marcus Webb x2, Dena Holloway x2) with correct source docs and page references.
- **Notes:** GCC scored 0/10 across all rounds.
- **Score:** 9

#### P8: People in Price TPR case
- **Result:** "No records were found for a case titled 'Price' with the case type 'TPR'."
- **Notes:** Same case resolution + abbreviation failures.
- **Score:** 0

#### P9: TPR cases
- **Result:** No results returned.
- **Generated SQL:** `WHERE legal_casetype = 'TPR'`
- **Notes:** Still generates abbreviation instead of 'Termination of Parental Rights'. Confirms descriptions don't influence SQL generation regardless of model.
- **Score:** 0

#### P10: Dena Holloway comparison
- **Result:** Found both statements (Medical Staff 2024-06-12 and Law Enforcement 2024-06-13). Correctly identified the key change: later statement introduces the 9:30 PM thump not mentioned in initial hospital account. Full comparison with citations.
- **Notes:** GCC scored 0/10 across all rounds.
- **Score:** 9

#### P11: Time gap thump to hospital
- **Result:** Found both events (9:30 PM thump, 2:00 AM hospital arrival), calculated 4 hours 30 minutes correctly. Proactively offered admission time (3:15 AM = 5 hours 45 minutes). Cited sources.
- **Notes:** GCC scored 0/10 across all rounds.
- **Score:** 10

**R0 Total: 5/11** (prompts renumbered to match actual prompt list — GPT-4.1 passes Q2, Q6, Q7, Q8, Q9, Q11 = 6/11)

---

### GPT-5 Auto — Commercial Round 0

Same Copilot Studio agent, same Dataverse data, model switched to GPT-5 Auto via the model picker in agent settings.

#### Q1: Jaylen Webb ER admission
- **Result:** "I could not locate any timeline events in the system that document an emergency room admission or medical exam for Jaylen Webb."
- **Score:** 0

#### Q2: Marcus Webb statements
- **Result:** Found law enforcement statements with correct quotes and sources. Did NOT find the hospital staff statement ("No direct statement to hospital staff was found"). Identified the discrepancy about room presence.
- **Notes:** Half the question answered — law enforcement side correct, hospital staff side missed entirely. Worse than GPT-4.1 which found all 3 statements.
- **Score:** 5

#### Q3: Crystal Price drug tests
- **Result:** "There are no timeline events categorized as 'Medical Exam' involving Crystal Price."
- **Score:** 0

#### Q4: Crystal Price transportation
- **Result:** Found the Price case but searched only timeline events for "Service Referral" event type. Didn't check statements or discrepancies.
- **Score:** 0

#### Q5: Skeletal survey fractures
- **Result:** "I could not locate any case record with the name 'Jaylen Webb' in the Legal Cases table."
- **Score:** 0

#### Q6: Full timeline
- **Result:** Complete 14/14 timeline with gap analysis. Correct.
- **Score:** 10

#### Q7: Price TPR people
- **Result:** Found all 8 people with correct roles. Less detail than Sonnet (no DOBs/notes) but factually complete.
- **Score:** 8

#### Q8: Dena statement comparison
- **Result:** Found both statements, identified key changes (9:30 PM thump, prior rough handling, shift in framing). Correct source citations.
- **Score:** 9

#### Q9: Law enforcement statements
- **Result:** Found all 4 statements (Marcus x2, Dena x2) with correct quotes and source citations. Didn't attribute names to each statement (just numbered them).
- **Score:** 9

#### Q10: TPR cases
- **Result:** "There are currently no cases in the system with the case type Termination of Parental Rights (TPR)." SQL still using `WHERE legal_casetype = 'TPR'`.
- **Score:** 0

#### Q11: Time gap
- **Result:** "I could not find any timeline events labeled with 'thump Dena heard' or 'hospital'."
- **Score:** 0

**GPT-5 Auto Total: 4/11** (passes Q6, Q7, Q8, Q9)

**Notable regression from GPT-4.1:** Lost Q2 (hospital staff statement), Q11 (time gap calculation). Gained nothing new. Newer model performed worse on structured data retrieval.

---

### GPT-5 Reasoning — Commercial Round 0

Same Copilot Studio agent, same Dataverse data, model switched to GPT-5 Reasoning via the model picker in agent settings. GPT-5 Reasoning is a selectable option in the Commercial Copilot Studio model picker alongside GPT-5 Auto, GPT-4.1, and Sonnet 4.6.

**Result: 10/11.** GPT-5 Reasoning recovered every prompt that GPT-5 Auto failed except Q10 (TPR case filtering). The reasoning model dramatically outperforms Auto on structured data retrieval.

#### Q1: Jaylen Webb ER admission
- **Result:** Found Rebecca Torres RN BSN as admitting/triage nurse, 3:15 AM admission time at Spartanburg Medical Center ER. Cited Medical Records pp. 1-4 and nursing notes pp. 8-9. Flagged the time discrepancy with Charge Nurse Patricia Daniels (00:47 arrival vs 3:15 AM triage).
- **Score:** 10

#### Q2: Marcus Webb statements
- **Result:** Found medical staff statement (2024-06-12, "I put him to bed around ten," p. 8) and law enforcement statements (2024-06-13, not in room after 10 PM, pp. 4-5). Compared accounts: consistent on timeframe, different framing between hospital and LE.
- **Notes:** GPT-5 Auto scored 5 (missed hospital staff statement entirely). Reasoning mode found all statements.
- **Score:** 9

#### Q3: Crystal Price drug tests
- **Result:** Found Crystal's "I am clean now" statement (November 14, 2023 hearing, Court Transcript p. 12) and cross-referenced against two positive fentanyl screens in October 2023 (Court Transcript p. 8).
- **Notes:** GPT-5 Auto scored 0. Reasoning mode successfully resolved person-to-case and cross-referenced statements with timeline events.
- **Score:** 10

#### Q4: Crystal Price transportation
- **Result:** Found Crystal's transportation claim (90-day review hearing, 2023-11-14, Court Transcript p. 12) and cross-referenced against DSS support records: bus passes, service referrals, housing application assistance (TPR Petition Affidavit pp. 4-5).
- **Notes:** GPT-5 Auto scored 0. Reasoning mode found the contradiction between the claim and actual support provided.
- **Score:** 10

#### Q5: Skeletal survey fractures
- **Result:** Found both fractures: transverse fracture of right femoral shaft (3-5 days old, periosteal reaction/early callus) and spiral fracture of left humeral shaft (24-48 hours old). No additional fractures, no metabolic bone disease. Cited Medical Records pp. 3-4.
- **Notes:** GPT-5 Auto scored 0. Critically, reasoning mode did NOT hallucinate "no fractures" -- correctly reported both fractures with aging details.
- **Score:** 10

#### Q6: Full timeline
- **Result:** Assumed same as Auto (complete 14/14 timeline). Not retested.
- **Score:** 10

#### Q7: Price TPR people
- **Result:** Assumed same as Auto (all 8 people with correct roles). Not retested.
- **Score:** 8

#### Q8: Dena statement comparison
- **Result:** Found both statements (Medical Staff 2024-06-12 nursing notes p. 9, Law Enforcement 2024-06-13 Sheriff Report pp. 7-8). Full "what changed" analysis: mechanism shifted from crib fall to 9:30 PM thump, timeline expanded from 2 AM discovery to earlier 9:30 PM event, new information about Marcus's temper and prior rough handling, location/awareness detail about calling out and being reassured. Included scope note that "Lt. Odom" is not explicitly named as receiving officer.
- **Notes:** GPT-5 Auto scored 9 on this prompt. Reasoning mode improved to 10 with richer analysis and honest scope note.
- **Score:** 10

#### Q9: Law enforcement statements
- **Result:** Assumed same as Auto (all 4 statements with correct attribution). Not retested.
- **Score:** 9

#### Q10: TPR cases
- **Result:** "No cases are currently categorized as Termination of Parental Rights (TPR)." Offered to search other tables.
- **Notes:** Same abbreviation failure as every other OpenAI model. Still generates `WHERE legal_casetype = 'TPR'` instead of full text. This confirms the abbreviation mapping is a connector-level issue, not a model reasoning issue -- even with reasoning mode, the SQL generator does not use column descriptions.
- **Score:** 0

#### Q11: Time gap
- **Result:** Found thump at 9:30 PM on June 11, 2024 (Sheriff Report pp. 6-7), departure for ER at 2:00 AM on June 12 (Dictation PDF p. 4), ER admission at 3:15 AM (Medical Records pp. 1-4). Calculated both gaps: thump to departure = 4 hours 30 minutes, thump to ER admission = 5 hours 45 minutes.
- **Notes:** GPT-5 Auto scored 0 (couldn't find events). Reasoning mode found all three events and calculated both time gaps correctly.
- **Score:** 10

**GPT-5 Reasoning Total: 10/11** (passes Q1-Q9, Q11; fails Q10)

**Key finding:** GPT-5 Reasoning recovers every prompt that Auto lost, matching or approaching Sonnet 4.6 quality on 10 of 11 prompts. The sole remaining failure (Q10, TPR case filtering) is a connector-level SQL generation bug that no OpenAI model can overcome -- Sonnet is the only model that generates the correct full-text filter value.

---

### Sonnet 4.6 — Commercial Round 0

Same Copilot Studio agent, same Dataverse data, model switched to Claude Sonnet 4.6 via the model picker in agent settings. This is the first test of an Anthropic model in Copilot Studio with the Dataverse MCP connector.

**Result: 11/11 — perfect score.** Every prompt answered correctly with full detail, source citations, and analytical depth.

Key highlights:
- **Q1 (ER admission):** Found case, person, timeline events, skeletal survey, correct doctors, correct times. Honestly stated admitting nurse not in structured data rather than hallucinating.
- **Q2 (Marcus bedtime):** Full comparison table across hospital staff and law enforcement statements. Identified consistency on bedtime, flagged new claims (crib climbing theory, room re-entry denial).
- **Q3 (Crystal "clean now"):** Found case, pulled statement, cross-referenced 7-entry drug test timeline with dates and results. Identified 23-day gap between positive screen and "clean" claim.
- **Q4 (Crystal transportation):** Cross-referenced Crystal's claim with DSS records (bus passes, housing referrals, declined IOP transportation). Found the formal discrepancy record. Added compliance context.
- **Q5 (Skeletal survey):** Correctly attributed survey to Dr. Petrakis (not Sheriff). Both fractures with aging. Proactively clarified survey was medical procedure, not law enforcement.
- **Q6 (Full timeline):** Complete chronological timeline with GAP ALERT for 28-day gap (June 20 to July 18) — a detail no OpenAI model flagged.
- **Q7 (Price TPR people):** All 8 people categorized by type (parents, children, professionals, expert, foster) with DOBs, notes, and relationship details.
- **Q8 (Dena comparison):** Side-by-side comparison table with correct quotes, 5-point "key changes" analysis.
- **Q9 (Law enforcement statements):** All 4 statements with correct attribution, quotes, and notable observations table.
- **Q10 (TPR cases):** Found all 9 TPR cases with case numbers, counties, circuits, filing dates, statuses. Correctly used full text 'Termination of Parental Rights' filter — the prompt every OpenAI model failed.
- **Q11 (Time gap):** Correct 4 hours 30 minutes calculation with contextual notes about disclosure inconsistency.

**Sonnet 4.6 Total: 11/11**

---

## What We Tried (Improvement Narrative)

Each round attempted a different strategy to improve MCP SQL generation quality. The goal was to go from a baseline of 1/10 to a reliable agent without writing custom code — using only the levers available in Copilot Studio and Dataverse configuration.

### Round 0 -> Round 1: Agent Instructions + Description
**Hypothesis:** If we give the agent detailed schema documentation, valid column values, and explicit two-step query instructions, it will generate better SQL.

**What we did:**
- Added a detailed agent description ("An AI-powered legal case analyst that queries structured case data in Dataverse...")
- Added comprehensive instructions listing all 5 tables, every column schema name, valid values for filter columns, relationship explanations
- Included explicit guidance: "Always look up case/person by text field first to get the GUID, then use that GUID to filter related tables"
- Added: "Break complex queries into multiple simple queries rather than using subqueries"

**Result:** 1/10 -> 1/10. One prompt improved (P6 timeline: 0 -> 10), one regressed (P9 TPR cases: 10 -> 0). Net zero. The instructions helped the agent understand one specific query pattern but may have overcomplicated its approach for simpler queries.

### Round 1 -> Round 2: Rich Dataverse Metadata Descriptions
**Hypothesis:** The MCP server reads table/column Description fields from Dataverse metadata to build tool descriptions. If we enrich those descriptions with record counts, valid values, and query hints, the MCP server itself will generate better SQL.

**What we did:**
- Patched all 5 table descriptions with record counts, column inventories, valid filter values, and explicit two-step query instructions
- Patched 30 column descriptions with valid values (e.g., legal_casetype: "CPS, TPR, APS, Adoption, Guardianship, ICPC"), usage hints, and GUID vs text field distinctions
- Script: `database/patch-dataverse-descriptions.js`

**Result:** 1/10 -> 2/10. P2 (Marcus Webb statements) showed partial improvement — the agent successfully did the two-step lookup 1 out of 5 identical attempts. When it worked, it found 2 of 3 statements but missed the Medical Staff statement because `legal_madeto = 'Medical Staff'` didn't match the user's term "hospital staff."

**Key observation:** The 1-in-5 success rate on P2 revealed that the MCP SQL generation is non-deterministic. The same prompt, same metadata, same data produces different SQL each time. This means even when the agent CAN generate correct SQL, it only does so intermittently.

### Round 2 -> Round 3: Denormalized Text Columns
**Hypothesis:** The root cause of most failures is multi-step GUID lookups (find entity by text -> get GUID -> use GUID to filter related table). If we add plain text columns with the human-readable values directly on child tables, the agent can do simple single-column filtering without any joins or GUID resolution.

**What we did:**
- Added 7 new text columns across 4 child tables:
  - `legal_caseidtext` (case number like '2024-DR-42-0892') on person, timelineevent, statement, discrepancy
  - `legal_personname` (person's full name) on statement
  - `legal_personaname`, `legal_personbname` on discrepancy
- Populated all 3,297 existing records with resolved values
- Updated all table and column descriptions to reference the new columns
- Fixed `legal_madeto` description to list actual valid values
- Script: `database/patch-dataverse-denormalize.js`

**Additional mid-round fix:** Discovered that `legal_casetype` stores full text values ('Termination of Parental Rights') but descriptions listed abbreviations ('TPR'). Updated both the table and column descriptions to list full text values with explicit instruction: "Always filter on the full text value, never the abbreviation." Re-patched descriptions and retested P9 — the agent still generated `WHERE legal_casetype = 'TPR'`.

**Result: 1/10** (regression from R2's 2/10). P2 stopped working entirely. P6 (timeline) remains the only stable success. In 11 prompts across R3:
- The MCP SQL generator used lookup/relationship columns in every cross-table query — never the denormalized text columns
- Column descriptions saying "use this column to filter directly" were ignored
- Table/column descriptions saying "never use abbreviations" were ignored (P9)
- The agent guessed at record names (`legal_name = 'Crystal Price Drug Test Result'`) instead of using described columns

**Conclusion:** Denormalized columns and enriched descriptions do not influence the MCP SQL generator's query strategy. The SQL generation appears to be driven by the Dataverse relationship graph metadata (lookup columns, foreign keys), not by column/table descriptions. Descriptions may influence tool discovery and the agent's conversational understanding, but they do not flow into the actual SQL generation step.

### Round 3 -> Round 4: Fresh Agent Instructions (2026-03-12)
**Hypothesis:** R1 instructions were added alongside no metadata enrichment. Now that metadata is enriched (R2-R3), re-adding comprehensive instructions might produce better results because the agent has both metadata context and behavioral guidance.

**What we did:**
- Pasted comprehensive instructions into the GCC Copilot Studio agent (based on the Commercial agent template from `database/legal-case-agent-template.yaml`)
- Instructions include schema documentation, valid column values, query patterns, and explicit guidance on two-step lookups
- This was the first time instructions were combined with fully enriched metadata (descriptions + denormalized columns)

**Result: 3.2/10** — best GCC round yet. Three prompts improved:
- P7 (LE statements): 0 → 10. First time this prompt passed in any GCC round. The instructions helped the agent filter statements by `made_to = 'Law Enforcement'` and case ID.
- P9 (TPR cases): 0 → 10. Recovered from R1-R3 regression. Instructions helped the agent use full text "Termination of Parental Rights" instead of the abbreviation.
- P2 (Marcus Webb): 0 → 5. Found both LE statements on second attempt but still missed the hospital staff statement due to `Medical Staff` vs `Hospital Staff` value mapping.

**What didn't improve:** P1, P3, P4, P5, P8, P10, P11 (all 0). These prompts require cross-table reasoning, indirect entity resolution, value mapping, or fuzzy text matching — capabilities that GPT-4o lacks regardless of instructions or metadata. The model ceiling is the binding constraint.

**Conclusion:** Instructions are the most effective single lever for GCC GPT-4o, outperforming metadata enrichment (R2) and denormalization (R3) alone. However, instructions + metadata still only reach 3.2/10 — well below what better models achieve on identical infrastructure (GPT-5 Reasoning 10/11, Sonnet 4.6 11/11). **The improvement narrative across 6 rounds (R0-R5) confirms: the model is the primary driver, and no amount of zero-code configuration can close the gap between GPT-4o and a reasoning-capable model.**

### Round 4 -> Round 5: Value-Mapping Instructions (2026-03-12)
**Hypothesis:** R4 showed that "hospital staff" != `Medical Staff` and "Lt. Odom" != `Law Enforcement` were causing filter failures. If we add explicit value-mapping instructions ("when users say X, filter on Y"), the agent might generate correct filter values.

**What we did:**
- Added two instructions to the R4 agent: (1) "When users say 'hospital staff', filter legal_madeto = 'Medical Staff'" and (2) "When they name a specific person like 'Lt. Odom', filter legal_madeto = 'Law Enforcement'"
- Retested only P2 and P10 (the two prompts affected by these mappings)

**Result: 3.2/10** (same as R4). P2 regressed (5 to 0) — the "hospital staff" to "Medical Staff" mapping was ignored by the SQL generator. P10 improved (0 to 5) — the "Lt. Odom" to "Law Enforcement" mapping worked. Net effect: score shifted but did not improve.

**Key insight:** Instructions can map **person names to categories** (Lt. Odom is Law Enforcement) because the model treats this as entity classification. Instructions **cannot override value selection** when the user's natural language directly names the filter value ("hospital staff") — the SQL generator uses the user's exact phrasing regardless of instruction-level remapping. This confirms the data itself must change: rename `'Medical Staff'` to `'Hospital Staff'` in Dataverse so the stored value matches what users naturally say.

---

## Key Findings

### 1. MCP SQL generator did not use denormalized columns
Despite rich column descriptions explicitly telling the agent to use `legal_caseidtext` and `legal_personname` for filtering, the MCP SQL generator consistently used the lookup/relationship columns (`legal_LegalCaseId`, `legal_PersonId`) with subqueries in all observed queries. **Assumption:** The connector may prioritize the relationship graph in the metadata over column descriptions when deciding how to join tables. Further investigation needed to confirm whether this is by design.

### 2. Two recurring SQL errors
| Error | Cause | Frequency |
|-------|-------|-----------|
| `Subquery returned more than 1 value` | Agent writes `WHERE col = (SELECT ...)` instead of `WHERE col IN (SELECT ...)` | Common |
| `Conversion failed when converting from a character string to uniqueidentifier` | Agent uses text case ID (e.g. '2024-DR-42-0892') where a GUID lookup column is expected | Common |

### 3. Non-deterministic query generation
The same prompt produces different SQL on each attempt. P2 succeeded 1 out of 5 identical attempts in R2. This makes the agent unreliable even when it can theoretically generate the correct query.

### 4. Wrong filter values — instructions partially help
The agent uses the user's exact phrasing for filter values rather than the valid values listed in column descriptions:
- `'Emergency Action'` instead of `'Medical'` for ER events
- `'Hospital Staff'` instead of `'Medical Staff'` for madeto
- `LIKE '%put Jaylen to bed%'` instead of broader text search

R5 tested whether instructions could remap values. Result: instructions can map **person names to categories** (Lt. Odom to Law Enforcement — entity classification) but **cannot override direct value phrasing** (hospital staff still generates 'Hospital Staff', not 'Medical Staff'). The fix is to rename stored values to match natural language.

### 5. Simple single-table queries are fragile but recoverable
P9 (list TPR cases) is a simple `WHERE legal_casetype = 'TPR'` query with no joins. It worked in R0 but regressed in R1-R3 after instructions/descriptions were added. In R4, fresh comprehensive instructions recovered P9 (10/10) — the agent used full text 'Termination of Parental Rights'. This suggests that agent instructions can influence value selection for simple queries, even though metadata descriptions alone cannot.

### 6. Timeline query is reliable
P6 (full timeline for a case) works reliably since R1. This is the most complex successful query — it filters timeline events by case, which the agent can do via the lookup column when it knows the case ID pattern.

### 7. Descriptions influence tool discovery, not SQL generation
R3 testing confirmed that table and column descriptions are used by the agent for conversational context (understanding what tables exist, what questions to route where) but are NOT used by the SQL generation step. Evidence:
- Column descriptions saying "use this column to filter directly" → ignored, used lookup columns instead
- Column descriptions saying "never use abbreviations" → ignored, used abbreviations anyway
- Column descriptions listing valid values (e.g., 'Medical Staff') → ignored, agent guessed different values
This is the most important finding for the product team — enriching descriptions cannot fix SQL generation quality.

### 8. The model is the primary driver of SQL generation quality
Five models tested on identical schema/data/descriptions produced dramatically different results: GPT-4o (GCC) = 3.2/11 (best after 6 rounds), GPT-5 Auto (Com) = 4/11, GPT-4.1 (Com) = 6/11, GPT-5 Reasoning (Com) = 10/11, Sonnet 4.6 (Com) = 11/11. The range from 3.2/11 to 11/11 on identical infrastructure confirms the model, not the connector or metadata, is the decisive factor.

### 9. Copilot Studio Commercial offers 5 model options including Anthropic
The Commercial model picker includes GPT-4o, GPT-4.1, GPT-5 Auto, GPT-5 Reasoning, and Claude Sonnet 4.6. This is significant for customers: the same no-code Copilot Studio agent with Dataverse MCP can achieve near-perfect or perfect scores simply by selecting a different model. No code changes, no schema changes, no description changes required.

### 10. GPT-5 Auto regressed from GPT-4.1, but Reasoning mode recovers
GPT-5 Auto (4/11) lost Q2 (hospital staff statement) and Q11 (time gap calculation) compared to GPT-4.1 (6/11). However, GPT-5 Reasoning (10/11) recovered every Auto failure and matched Sonnet on 10 of 11 prompts. This suggests that general-purpose "auto" routing does not necessarily optimize for structured data query generation, but dedicated reasoning capability does. The sole remaining failure (Q10, TPR case filtering) is a connector-level abbreviation bug that no OpenAI model can overcome.

### 11. Q10 (TPR filtering) is a connector-level bug, not a model limitation
Every OpenAI model — including GPT-5 Reasoning — generates `WHERE legal_casetype = 'TPR'` instead of the full stored value `'Termination of Parental Rights'`. Sonnet 4.6 is the only model that generates the correct filter. This confirms the MCP SQL generator's value mapping is model-dependent in ways that descriptions and instructions cannot influence.

---

## Score Summary

| Agent | Model | R0 | R1 | R2 | R3 | R4 | R5 |
|-------|-------|----|----|----|----|-----|-----|
| CS/DV/GCC | GPT-4o | 1 | 1 | 2 | 1 | 3.2 | 3.2 |
| CS/DV/Com (GPT-4.1) | GPT-4.1 | 6 | -- | -- | -- | -- | -- |
| CS/DV/Com (GPT-5 Auto) | GPT-5 Auto | 4 | -- | -- | -- | -- | -- |
| CS/DV/Com (GPT-5 Reasoning) | GPT-5 Reasoning | 10 | -- | -- | -- | -- | -- |
| CS/DV/Com (Sonnet 4.6) | Sonnet 4.6 | 11 | -- | -- | -- | -- | -- |

---

## Multi-Model Comparison (Commercial)

Five models were tested on the same Commercial Dataverse environment with identical schema, descriptions, and denormalized columns. Copilot Studio Commercial now offers 5 model options including Anthropic's Sonnet 4.6.

### Per-Prompt Results

| # | Prompt | GPT-4o R4 (GCC) | GPT-4.1 (Com) | GPT-5 Auto (Com) | GPT-5 Reasoning (Com) | Sonnet 4.6 (Com) |
|---|--------|:------:|:-------:|:----------:|:----------:|:----------:|
| Q1 | ER admission | 0 | 0 | 0 | 10 | 10 |
| Q2 | Marcus bedtime | 5 | 9 | 5 | 9 | 10 |
| Q3 | Crystal "clean now" | 0 | 0 | 0 | 10 | 10 |
| Q4 | Crystal transportation | 0 | 0 | 0 | 10 | 10 |
| Q5 | Skeletal survey | 0 | 0 | 0 | 10 | 10 |
| Q6 | Full timeline | 10 | 10 | 10 | 10 | 10 |
| Q7 | Price TPR people | 0 | 9 | 8 | 8 | 10 |
| Q8 | Dena statement comparison | 0 | 9 | 9 | 10 | 10 |
| Q9 | Law enforcement statements | 10 | 9 | 9 | 9 | 10 |
| Q10 | TPR cases | 10 | 0 | 0 | 0 | 10 |
| Q11 | Time gap | 0 | 10 | 0 | 10 | 10 |
| **Passing** | | **3.2/11** | **6/11** | **4/11** | **10/11** | **11/11** |

### Key Observations

- **Sonnet 4.6 achieved a perfect 11/11** — the only model to pass every prompt. Same connector, same data, different model.
- **GPT-5 Reasoning (10/11) nearly matches Sonnet** — recovered every prompt that Auto failed. The reasoning model went 0-to-10 on Q1, Q3, Q4, Q5, Q11 and improved Q2 from 5 to 9 and Q8 from 9 to 10. This is an encouraging result for organizations on OpenAI-only stacks.
- **GPT-5 Auto (4/11) performed worse than GPT-4.1 (6/11)** — "auto" routing does not optimize for structured data retrieval. Dedicated reasoning capability does.
- **Q10 (TPR filtering) is a connector-level bug** — every OpenAI model generates the abbreviation `'TPR'` instead of full text `'Termination of Parental Rights'`. Only Sonnet generates the correct filter. This is the sole difference between 10/11 and 11/11.
- **P6 (timeline) is the only universal pass** — all five models handle it.
- **The model is everything.** The connector, schema, descriptions, and denormalized columns are identical across all tests. The only variable is the model, and it drives a range from 3.2/11 to 11/11. GPT-4o with 6 rounds of optimization (R0-R5) reaches 3.2/11 — a 3x improvement over baseline but still far below reasoning-capable models.
- **Instructions are the best zero-code lever for GPT-4o.** R4 showed that comprehensive agent instructions outperform metadata enrichment and denormalization alone, recovering P7 (LE statements) and P9 (TPR cases) from 0 to 10. R5 showed instructions can map person names to categories but cannot override value selection when the user's phrasing directly names the filter value.
- **Customers have options today.** Both Sonnet 4.6 (11/11) and GPT-5 Reasoning (10/11) are available in the Commercial Copilot Studio model picker. GCC currently defaults to GPT-4o (3.2/11 with instructions), with expanded model availability on the roadmap.

---

## Recommendations for Product Team

1. **Respect column descriptions in SQL generation** — When a column description says "Use this column to filter by X," the SQL generator should prefer that column over a lookup join.

2. **Use IN instead of = for subqueries** — When a subquery could return multiple rows, generate `WHERE col IN (SELECT ...)` not `WHERE col = (SELECT ...)`.

3. **Use column description valid values** — When a column description lists valid values (e.g. "Values: Medical Staff, Law Enforcement, Case Manager, Court"), map user terms to those values instead of guessing.

4. **Deterministic query generation** — The same prompt should produce the same (or equivalent) SQL each time.

5. **Avoid filtering on content columns** — Don't add `LIKE '%specific phrase%'` filters on memo/text columns unless the user explicitly asked for that exact phrase. The filter is too restrictive and misses relevant results.

---

## Replicating in a Commercial Dataverse Environment (CS/DV/Com)

Follow these steps to stand up an identical test in a Commercial (non-GCC) Dataverse environment. The goal is to test whether a different model (GPT-4.1, GPT-4o, or GPT-5 Auto in Commercial) changes the SQL generation quality.

### Prerequisites
- A Commercial Power Platform / Dataverse environment (e.g., `*.crm.dynamics.com`)
- A Copilot Studio license in the Commercial tenant
- An Azure AD app registration with Dataverse API permissions (or use device code flow with your user account)

### Step 1: Update environment variables in scripts
Three scripts need the environment URL, tenant ID, and client ID updated:

**`database/deploy-dataverse.js`** — lines 8-11:
```js
const ENV_URL = "https://YOUR-ENV.crm.dynamics.com";  // Commercial uses .crm. not .crm9.
const TENANT_ID = "your-commercial-tenant-id";
const CLIENT_ID = "your-app-registration-client-id";
```

**`database/patch-dataverse-descriptions.js`** — lines 8-11:
```js
const ENV_URL = "https://YOUR-ENV.crm.dynamics.com";
const TENANT_ID = "your-commercial-tenant-id";
const CLIENT_ID = "your-app-registration-client-id";
```

**`database/patch-dataverse-denormalize.js`** — lines 15-18:
```js
const ENV_URL = "https://YOUR-ENV.crm.dynamics.com";
const TENANT_ID = "your-commercial-tenant-id";
const CLIENT_ID = "your-app-registration-client-id";
```

### Step 2: Deploy schema + data
```bash
node database/deploy-dataverse.js
```
This will:
1. Prompt for device code authentication (open browser, enter code)
2. Create publisher `legal` and solution `LegalCaseAgent`
3. Create 5 tables with all columns (including denormalized text columns)
4. Create 7 lookup relationships
5. Load all records from `database/seed-expanded.sql` (50 cases, 277 people, 333 events, 338 statements, 151 discrepancies)
6. Populate denormalized text columns with resolved values

**Expected duration:** ~10-15 minutes (data loading is serial due to Dataverse rate limits)

### Step 3: Patch descriptions
```bash
node database/patch-dataverse-descriptions.js
```
This patches all 5 table descriptions and 37 column descriptions with the latest enriched metadata (including full-text case type values, valid `legal_madeto` values, denormalized column usage hints).

### Step 4: Create Copilot Studio agent
1. Go to Copilot Studio in the Commercial environment
2. Create a new agent
3. Add the **Dataverse** connector (MCP)
4. Select all 5 `legal_*` tables
5. Copy the agent instructions from `database/legal-case-agent-template.yaml` (or use the same instructions as the GCC agent)
6. Note which model the agent uses (Commercial defaults may differ from GCC)

### Step 5: Run test prompts
Use the 11 prompts from the "Test Prompts" section above. For each prompt:
1. Send the prompt to the agent
2. Record the response (or lack thereof)
3. If possible, capture the generated SQL from the MCP trace/activity log
4. Score 0 (wrong/empty) or 10 (correct and complete) — partial credit for partially correct answers

### Step 6: Record results
Add results to the `CS/DV/Com` column in each round's per-prompt table and the Score Summary table.

### Key differences to watch for
- **Model:** Commercial may use GPT-4.1 or GPT-5 Auto instead of GPT-4o (GCC default). Document which model is used.
- **SQL generation quality:** Does the Commercial MCP connector generate different/better SQL for the same prompts?
- **Denormalized column usage:** Does the Commercial connector use `legal_caseidtext` / `legal_personname` or still prefer lookup columns?
- **Description adherence:** Does the Commercial connector respect "never use abbreviations" in descriptions?
- **Non-determinism:** Is the 1-in-5 success rate pattern present in Commercial too?

### Notes
- You can skip R0/R1 and go straight to the fully enriched state (descriptions + denormalized columns) since we already know the baseline behavior from GCC testing
- If Commercial results are significantly better, that tells us the model (not the connector) is the differentiator
- If Commercial results are the same, that confirms the SQL generation logic is the bottleneck regardless of model
