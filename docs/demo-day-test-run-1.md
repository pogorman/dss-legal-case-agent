# Demo Day Test Run 1 — 2026-03-12

**Purpose:** Validate all demo agents after SharePoint libraries and Copilot Studio agents were configured.

---

## Part 1: Document Quality Demo

**Agents under test:**

| Agent | SharePoint Library | Model | Environment |
|---|---|---|---|
| Case Analyst - Raw Docs | Case Files - Raw | GPT-4o | GCC |
| Case Analyst - Cross-Ref | Case Files - Cross-Referenced | GPT-4o | GCC |
| Case Analyst - Enriched | Case Files - Enriched | GPT-4o | GCC |

---

### Prompt 1 — The Skeletal Survey Trap

```
Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey?
```

**Expected:** Raw = FAIL → Cross-Ref = PASS → Enriched = PASS

| Agent | Score | Result |
|---|---|---|
| Raw Docs | FAIL | Confidently wrong — quotes Sheriff Report "no fractures detected" without cross-checking Medical Records |
| Cross-Ref | PASS | Found both sources, noted Sheriff Report summary is misleading, cited both fractures with correct descriptions |
| Enriched | PASS | Same quality as Cross-Ref — found both sources, cited both fractures |

#### Raw Docs Response

The Sheriff's Office investigation did not find any fractures in Jaylen Webb's skeletal survey. The radiology report indicated no fractures detected on the skeletal survey.

**Citation:** Sheriff_Report_24-06-4418.pdf

**Analysis:** False negative. The citation is real and the quote is accurate, but the Sheriff Report's summary is misleading — the Medical Records document bilateral fractures (right femur, left humerus) at different healing stages indicating non-accidental injury.

#### Cross-Ref Response

The Sheriff's Office investigation noted that the radiology report indicated no fractures detected on the skeletal survey. However, the medical records clarify that this refers only to areas outside the known fracture sites. The complete findings, including two diagnosed fractures (right femur transverse fracture and left humerus spiral fracture), are detailed in the radiology report.

**Citations:** Sheriff_Report_24-06-4418-case2.pdf, Medical_Records-case2.pdf

**Analysis:** Pass. Agent found both sources and correctly identified that the Sheriff Report's "no fractures" summary is misleading. Cited both fractures (right femur transverse, left humerus spiral) from the Medical Records.

#### Enriched Response

The Sheriff's Office investigation noted that the radiology report indicated no fractures detected on the skeletal survey. However, the medical records clarify that this refers only to areas outside the known fracture sites. The complete findings, including two diagnosed fractures (right femur transverse fracture and left humerus spiral fracture), are detailed in the radiology report.

**Citations:** Sheriff_Report_24-06-4418-case2.pdf, Medical_Records-case2.pdf

**Analysis:** Pass. Same result as Cross-Ref — the cross-reference header is doing the heavy lifting. Metadata didn't change the outcome for this prompt.

---

### Prompt 2 — Marcus Webb's Statements

```
What did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement?
```

**Expected:** Raw = FAIL → Cross-Ref = PARTIAL → Enriched = PASS

| Agent | Score | Result |
|---|---|---|
| Raw Docs | FAIL | Only found Sheriff Report; missed hospital staff statements from Medical Records nursing notes; misattributed Dena's "8:00 PM" quote to Marcus |
| Cross-Ref | PARTIAL | Found LE statements and Dena's conflicting account, but still missed hospital staff statements from nursing notes |
| Enriched | PARTIAL | Found 3 sources, got 10 PM time correct, identified Marcus/Dena conflict — but still missed Medical Records nursing notes for hospital staff statement |

#### Raw Docs Response

The documents do not provide specific details about what Marcus Webb told the hospital staff regarding when he put Jaylen to bed. However, Marcus Webb stated to law enforcement that he put Jaylen to bed in his crib at approximately 8:00 PM on June 11, 2024. He mentioned that after putting Jaylen to bed, he went to the living room, sat on the couch to watch television, and fell asleep. He claimed that he did not go into Jaylen's room after putting him to bed and suggested that Jaylen might have climbed out of his crib and fallen.

**Citation:** Sheriff_Report_24-06-4418.pdf

**Analysis:** Fail. Agent couldn't find hospital staff statements (buried in Medical Records nursing notes). Misattributed the 8:00 PM bedtime to Marcus — that's Dena Holloway's quote. Marcus told both hospital staff and law enforcement ~10:00 PM. Also hallucinated consistency ("no information indicating a different account") when it simply couldn't retrieve the second source.

#### Cross-Ref Response

Marcus Webb did not provide a direct statement to hospital staff about when he put Jaylen to bed. The information about Jaylen's condition and the events leading up to the hospital visit was primarily provided by Dena Holloway.

To law enforcement, Marcus Webb stated that he was on the couch all night and did not go into Jaylen's room after putting him to bed. He suggested that Jaylen may have climbed out of the crib and fallen, and he denied handling Jaylen roughly or knowing how the injuries occurred. When confronted with inconsistencies between his statement and Dena Holloway's statement regarding his presence in or near the child's room at 9:30 PM, Marcus Webb maintained that he was not in Jaylen's room after 10 PM.

There is a conflict between Marcus Webb's statement to law enforcement and Dena Holloway's revised statement. Holloway stated that she heard a loud thump from Jaylen's room at approximately 9:30 PM and assumed Marcus was in there with the child, which contradicts Webb's claim of not being in the room after 10 PM.

**Citations:** Sheriff_Report_24-06-4418-case2.pdf, DSS_Investigation_Report-case2.pdf

**Analysis:** Partial. Improvement over Raw — correctly identified the conflict between Marcus and Dena's accounts and the 9:30 PM thump detail. But still claims Marcus didn't provide a statement to hospital staff (he did — it's in the Medical Records nursing notes). Cross-references improved reasoning about conflicts but didn't fix the retrieval gap.

#### Enriched Response

Marcus Webb did not provide a direct statement to hospital staff about when he put Jaylen to bed. The information provided to the medical staff was primarily from Dena Holloway, who stated that Marcus put Jaylen to bed and that she was in the bedroom at that time.

To law enforcement, Marcus Webb stated that he put Jaylen to bed at approximately 10:00 PM on June 11, 2024, and then slept on the couch. He denied entering Jaylen's room after putting him to bed.

There is a conflict in the accounts provided by Marcus Webb and Dena Holloway. While Webb claimed he was on the couch all night and did not enter Jaylen's room after putting him to bed, Holloway later revised her statement to law enforcement, indicating she heard a loud thump from Jaylen's room at approximately 9:30 PM and assumed Marcus was in the room with the child.

**Citations:** Sheriff_Report_24-06-4418-case2.pdf, DSS_Investigation_Report-case2.pdf, Court_Orders_and_Filings-case2.pdf

**Analysis:** Partial. Better than Raw — correct 10 PM bedtime (not the misattributed 8 PM), found the Marcus/Dena conflict, pulled from 3 different sources. But still claims Marcus didn't provide a statement to hospital staff. The Medical Records nursing notes contain his direct statement to hospital staff and the metadata keywords ("Marcus Webb hospital statement, nursing interview") weren't enough to bridge the retrieval gap this run.

---

### Prompt 3 — The Timeline

```
What is the complete timeline of events for case 2024-DR-42-0892?
```

**Expected:** Raw = FAIL → Cross-Ref = PASS (skip Enriched — same result)

| Agent | Score | Result |
|---|---|---|
| Raw Docs | FAIL | Case contamination — returned Case 2 (Price/TPR) events for a Case 1 (Webb/CPS) query |
| Cross-Ref | PASS | Correct case, 10+ chronological events, zero case contamination |

#### Raw Docs Response

*(Agent returned Crystal Price / TPR timeline events for case 2024-DR-42-0892, which is the Webb/CPS case. Full response included: November 14, 2023 ninety-day review hearing for Ms. Price, IOP compliance issues, fentanyl drug screens, February 2024 TPR preparation, Amari and Destiny Price foster care status, Monica Vance TPR recommendation.)*

**Citation:** Case 2 documents (misattributed)

**Analysis:** Fail. Complete case contamination. The agent retrieved Case 2 (2024-DR-15-0341, Price/TPR) events and presented them as the timeline for Case 1 (2024-DR-42-0892, Webb/CPS). Zero correct events. Without case-number-aware cross-references, the agent has no way to distinguish which events belong to which case.

#### Cross-Ref Response

**June 11, 2024**
- ~9:30 PM: Dena Holloway hears a loud thump from the child's room. Marcus Webb is in or near the child's room. Ms. Holloway calls out; Webb responds everything is fine.

**June 12, 2024**
- ~3:15 AM: Jaylen Webb presented to Spartanburg Medical Center ED by both parents.
- Dr. Anita Chowdhury diagnoses bilateral femur fracture and spiral fracture of left humerus — inconsistent with reported crib fall.
- ~7:30 AM: Dr. Chowdhury files mandatory abuse report with DSS and Sheriff's Office.
- ~11:00 AM: Lt. Frank Odom responds to hospital, observes injuries, initiates investigation.

**June 13, 2024**
- DSS Case Manager Renee Dawson interviews Dena Holloway at hospital. Holloway states child fell from crib; Webb was only adult present after bedtime.
- Lt. Odom interviews both parents separately. Marcus Webb says he was asleep on couch, denies entering child's room after ~10 PM bedtime.
- Dena Holloway materially changes her account to Lt. Odom — discloses 9:30 PM thump, Webb in/near room, prior rough handling (2-3 occasions).

**June 14, 2024**
- 10:00 AM: Court reviews Petition for Emergency Protective Custody...

**June 14, 2024**
- 10:00 AM: Court reviews Petition for Emergency Protective Custody, supporting affidavit, medical records, and Sheriff Report. Court issues Ex Parte Order placing Jaylen Webb in emergency protective custody of DSS.

**June 18, 2024**
- 9:30 AM: Probable Cause Hearing held pursuant to S.C. Code Ann. Section 63-7-710.

**June 19, 2024**
- Home Study Report completed.

**Citations:** Court_Orders_and_Filings-case2.pdf, Home_Study_Report-case2.pdf

**Analysis:** Pass. All events are from the correct case (Webb/CPS, 2024-DR-42-0892). 10+ events in chronological order, zero contamination from the Price/TPR case. Cross-reference headers with explicit case numbers prevented the case mixing seen in the Raw Docs agent.

---

## Part 2: Model Selection Demo

**Agent under test:** Case Analyst - Dataverse MCP (Commercial Copilot Studio)

| Model | Environment | Notes |
|---|---|---|
| GPT-4.1 | Commercial | Starting model (Commercial default) |
| GPT-5 Auto | Commercial | Second model tested |
| Sonnet 4.6 | Commercial | Swap during demo |

---

### Prompt 1 — Aggregate Query (TPR Cases)

```
Which cases involve Termination of Parental Rights?
```

**Expected:** GPT-4.1 = FAIL → GPT-5 Auto = FAIL → Sonnet 4.6 = PASS

| Model | Score | Result |
|---|---|---|
| GPT-4.1 | FAIL | Zero results — abbreviation 'TPR' instead of full text value |
| GPT-5 Auto | FAIL | Same abbreviation problem — zero results |
| GPT-5 Reasoning | PASS | Found 9 TPR cases with case numbers, circuits, counties, statuses — **surprise vs. prior testing (was 0/10)** |
| Sonnet 4.6 | PASS | 9 TPR cases grouped by status (Active/Closed/Dismissed), full summaries with children, parents, treatment plans, key patterns |

#### GPT-4.1 Response

No cases involving Termination of Parental Rights (TPR) are currently recorded in the system.

#### GPT-5 Auto Response

There are currently no cases in the system with the case type Termination of Parental Rights (TPR).

**Analysis:** GPT-4.1 and GPT-5 Auto both fail — abbreviation "TPR" instead of full text value. Confirms connector-level issue.

#### GPT-5 Reasoning Response

Found 9 TPR cases with full details:
- 2024-DR-22-0165 — DSS v. Nelson — Fourth Circuit (Chesterfield) — Closed
- 2024-DR-38-0342 — DSS v. Wright — Fourth Circuit (Marlboro) — Closed
- 2025-DR-45-0184 — DSS v. Morris — Fifth Circuit (Richland) — Dismissed
- 2025-DR-21-0289 — DSS v. Parker — Fifth Circuit (Richland) — Active
- 2025-DR-09-0443 — DSS v. Reed — Fourth Circuit (Dillon) — Active
- 2024-DR-15-0341 — DSS v. Price — Fifth Circuit (Richland) — Active
- 2023-DR-25-0194 — DSS v. Williams — Fifth Circuit (Kershaw) — Dismissed
- 2024-DR-42-0424 — DSS v. Taylor — Third Circuit (Sumter) — Active
- 2025-DR-24-0382 — DSS v. Young — Fifth Circuit (Kershaw) — Active

**Analysis:** Pass. GPT-5 Reasoning now solves the TPR abbreviation problem — previously scored 0/10 on this prompt. Significant improvement, possibly from model updates. Still, GPT-4.1 and GPT-5 Auto remain broken on this query.

#### Sonnet 4.6 Response

**9 cases found, grouped by status:**

**Active (5):** DSS v. Young (Kershaw), DSS v. Taylor (Sumter), DSS v. Price (Richland), DSS v. Reed (Dillon), DSS v. Parker (Richland)

**Closed (2):** DSS v. Wright (Marlboro) — reunified, DSS v. Nelson (Chesterfield) — reunified

**Dismissed (2):** DSS v. Williams (Kershaw) — insufficient evidence, DSS v. Morris (Richland) — insufficient evidence

Each case included: case number, county, circuit, filing date, status, child names/ages, parent names, removal reasons, and treatment plan details. Response concluded with key patterns analysis (treatment plan commonalities, removal reasons, circuit concentration, outcomes).

**Analysis:** Pass. Comprehensive — same 9 cases as GPT-5 Reasoning but with significantly richer detail (case summaries, child/parent names, treatment plans) and organized by status category with a pattern analysis section. Demonstrates Sonnet's structured output strength.

---

### Prompt 2 — Cross-Reference Reasoning (Marcus Webb)

```
What did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement?
```

**Expected:** GPT-4.1 = FAIL → Sonnet 4.6 = PASS

| Model | Score | Result |
|---|---|---|
| GPT-4.1 | PASS | Found all 3 statements (hospital + 2 LE) with direct quotes and page cites, flagged crib-climbing addition, 9:30 PM discrepancy, and non-accidental injury finding |
| GPT-5 Auto | PARTIAL | Found both LE statements with quotes, but couldn't retrieve hospital staff statement — inferred from discrepancy record instead |
| GPT-5 Reasoning | PASS | Found hospital staff quote with page cite, compared to LE statements, noted bedtime nuance — missed second LE statement |
| Sonnet 4.6 | PASS | Found all 3 statements (hospital staff + 2 LE), cited page numbers, identified formal discrepancy, flagged 9:30 PM thump predates stated 10 PM bedtime |

#### GPT-4.1 Response

**To Hospital Staff:** "I put him to bed around ten. He was fine, running around all day. I fell asleep on the couch watching TV. Next thing I know, Dena is shaking me saying something is wrong with Jaylen." *(Medical Records, Nursing Notes, p. 8)*

**To Law Enforcement (Statement 1):** "I was on the couch all night. I did not go into Jaylen room after I put him down. I don't know how he got hurt. Maybe he climbed out of the crib and fell. He's been trying to climb out lately." *(Sheriff Report #24-06-4418, p. 4)*

**To Law Enforcement (Statement 2):** "Dena and I have been arguing a lot lately but I would never hurt my son. I don't know why she is saying I was in the room. I was not in his room after 10 PM." *(Sheriff Report #24-06-4418, p. 5)*

**Comparison:** Generally consistent (~10 PM bedtime, couch all night), but LE statements add crib-climbing speculation not mentioned to hospital staff. Flagged 9:30 PM thump discrepancy (Dena's account places Marcus in/near room before stated bedtime). Also noted medical records indicate non-accidental injuries at two separate times, inconsistent with a single fall.

**Summary:** Marcus Webb told hospital staff and law enforcement that he put Jaylen to bed around 10 PM and did not re-enter the room, but his answers to law enforcement included more detail about possible causes for Jaylen's injuries. There are inconsistencies between his account and other evidence regarding his presence in the room and the timing and cause of Jaylen's injuries.

**Analysis:** Pass (9/10). Found all three statements with direct quotes and page citations — including the hospital staff nursing notes. Noted the crib-climbing addition to LE, the 9:30 PM discrepancy, and the non-accidental injury finding. Significant improvement over prior testing (was 9/10, confirmed).

#### GPT-5 Auto Response

**Statement to Law Enforcement (June 13, 2024):**
- "I was on the couch all night. I did not go into Jaylen's room after I put him down. I don't know how he got hurt. Maybe he climbed out of the crib and fell. He's been trying to climb out lately."
- "Dena and I have been arguing a lot lately but I would never hurt my son. I don't know why she is saying I was in the room. I was not in his room after 10 PM."
Source: Sheriff Report #24-06-4418, pp. 4–5

**Statement to Hospital Staff:** No direct hospital statement retrieved. Inferred from discrepancy record that he stated he put Jaylen to bed at 10 PM and did not re-enter the room.

**Analysis:** Partial (5/10). Found both LE statements with direct quotes and page citations — better than GPT-4.1 on LE retrieval. But couldn't retrieve the actual hospital staff quote from Medical Records nursing notes. Fell back to inferring the hospital statement from the discrepancy table, which is indirect. The prompt specifically asks about hospital staff — missing that source is a significant gap.

#### GPT-5 Reasoning Response

Case 2024-DR-42-0892 — Child Protective Services.

To hospital staff: He said, "I put him to bed around ten." Source: Medical Records, Nursing Notes (p. 8).

To law enforcement: He did not give a specific bedtime; he stated he was not in Jaylen's room after 10 PM and that he was on the couch after putting Jaylen down. Sources: Sheriff Report #24-06-4418 (pp. 5, 4).

Bottom line: He gave a specific "around 10 PM" time to hospital staff; to law enforcement he did not restate an exact bedtime, but his statements indicate he did not return to the room after 10 PM.

**Analysis:** Pass (9/10). Found the hospital staff statement with direct quote and page citation — a key retrieval that all Part 1 document agents missed. Correctly compared the two accounts and noted the nuance (specific time to hospital, no exact time to LE). Missed the second LE statement and the Dena discrepancy, but the core comparison is accurate.

#### Sonnet 4.6 Response

**Hospital Staff Statement (June 12, 2024):** "I put him to bed around ten. He was fine, running around all day. I fell asleep on the couch watching TV. Next thing I know, Dena is shaking me saying something is wrong with Jaylen." *(Medical Records, Nursing Notes, p. 8)*

**LE Statement 1 (June 13, 2024):** "I was on the couch all night. I did not go into Jaylen room after I put him down. I don't know how he got hurt. Maybe he climbed out of the crib and fell. He's been trying to climb out lately." *(Sheriff Report #24-06-4418, p. 4)*

**LE Statement 2 (same day):** "Dena and I have been arguing a lot lately but I would never hurt my son. I don't know why she is saying I was in the room. I was not in his room after 10 PM." *(Sheriff Report #24-06-4418, p. 5)*

**Discrepancy:** Consistent bedtime (~10 PM) across all statements, but Dena's revised statement places Marcus in/near the room at 9:30 PM — before the stated bedtime. Marcus denies being in the room after 10 PM, but the thump occurred at 9:30 PM.

**Analysis:** Pass (10/10). Found all three statements including hospital staff nursing notes (which every Part 1 document agent missed). Cited specific page numbers. Identified the formal discrepancy and noted the critical timeline detail — the thump predates the stated bedtime.

---

### Prompt 3 — Time Calculation

```
What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?
```

**Expected:** GPT-4.1 = FAIL → Sonnet 4.6 = PASS

| Model | Score | Result |
|---|---|---|
| GPT-4.1 | | |
| Sonnet 4.6 | | |

#### GPT-4.1 Response


#### Sonnet 4.6 Response


---

## GCC Dataverse MCP Retest (GPT-4o)

**Agent under test:** Case Analyst - Dataverse MCP (GCC Copilot Studio)
**Model:** GPT-4o (GCC default, no model picker)
**Change:** Fresh agent instructions pasted (same as Commercial agent template + query guidance hints)
**Baseline:** Best prior score R2 = 2/10 (timeline + partial Marcus Webb)

| # | Prompt | R0 | R1 | R2 | R3 | R4 (this run) |
|---|--------|----|----|----|----|----------------|
| 1 | Jaylen Webb ER admission | 0 | 0 | 0 | 0 | 0 |
| 2 | Marcus Webb statements | 0 | 0 | ~1 | 0 | 5 |
| 3 | Crystal Price drug tests | 0 | 0 | 0 | 0 | 0 |
| 4 | Crystal Price transportation | 1 | 1 | 0 | 0 | 0 |
| 5 | Skeletal survey fractures | 0 | 0 | 0 | 0 | 0 |
| 6 | Timeline for case | 0 | 10 | 10 | 10 | 10 |
| 7 | Statements to law enforcement | 0 | 0 | 0 | 0 | 10 |
| 8 | People in Price TPR | 0 | 0 | 0 | 0 | 0 |
| 9 | TPR cases | 10 | 0 | 0 | 0 | 10 |
| 10 | Dena Holloway statements comparison | 0 | 0 | 0 | 0 | 0 |
| 11 | Time gap thump to hospital | 0 | 0 | 0 | 0 | 0 |
| **Total** | | **1** | **1** | **2** | **1** | **35** |

---

### P1: Jaylen Webb ER admission

```
Tell me about Jaylen Webb's emergency room admission — specifically the time and the admitting nurse.
```

**Score: 0**

#### Response

Failed — attempted to query People table for Jaylen Webb's GUID but used invalid table/column names. Listed available tables, found correct names, but then hit invalid column names on legal_timelineevent. Never retrieved data.

**Analysis:** Same failure pattern as R0-R3. The MCP SQL generator can't resolve table/column names reliably despite having the schema. Instructions didn't help.


---

### P2: Marcus Webb statements

```
What did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement?
```

**Score: 5 (partial)**

#### Response

*(First attempt: 0 — described correct query strategy with pseudo-SQL but never executed. Second attempt below.)*

Marcus Webb did not provide any statements to hospital staff regarding when he put Jaylen to bed. However, he did provide multiple statements to law enforcement:

1. "Dena and I have been arguing a lot lately but I would never hurt my son. I don't know why she is saying I was in the room. I was not in his room after 10 PM."
2. "I was on the couch all night. I did not go into Jaylen's room after I put him down. I don't know how he got hurt. Maybe he climbed out of the crib and fell. He's been trying to climb out lately."

**Analysis:** Partial. Executed queries on second attempt and found both LE statements (improvement over R0-R3). But missed the hospital staff statement — likely because `legal_madeto` stores `'Medical Staff'` not `'Hospital Staff'`, so the filter returned nothing. Same retrieval gap as R2.


---

### P3: Crystal Price drug tests

```
Crystal Price told the court she was 'clean now' at the November 2023 hearing. What do the drug test results show?
```

**Score: 0**

#### Response

"There are no statements recorded in the database for Crystal Price made to the court in November 2023. Therefore, I cannot provide any information on her drug test results based on court statements from that period."

**Analysis:** Same failure as R0-R3. Agent searched statements table for Crystal Price + court + November 2023 and got no results. The data exists across multiple tables (statements, timeline events, discrepancies) but the agent couldn't assemble it. Instructions didn't help.

---

### P4: Crystal Price transportation

```
Crystal Price said she couldn't comply with the treatment plan because she lacked transportation. What support did DSS actually provide?
```

**Score: 0**

#### Response

"There are no statements in the database indicating that Crystal Price mentioned transportation issues to a DSS Caseworker. Therefore, there is no information on what support DSS provided in response to her claim."

**Analysis:** Same failure as R0-R3. The data spans statements + timeline events but the agent only searched statements for transportation keywords. Instructions didn't help the agent cross-reference tables.


---

### P5: Skeletal survey fractures

```
Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey?
```

**Score: 0**

#### Response

"The Sheriff's Office investigation did not find any fractures in Jaylen Webb's skeletal survey based on the available data."

**Analysis:** Dangerous false negative — same as R0-R3. The database contains detailed fracture findings (right femur transverse, left humerus spiral) but the agent confidently states no fractures were found. This is the Level 5 failure case: the answer sounds authoritative but is factually wrong. Instructions didn't help.

---

### P6: Timeline for case

```
What is the complete timeline of events for case 2024-DR-42-0892?
```

**Score: 10**

#### Response

Returned 7 timeline events in chronological order with full detail:
1. June 11, 9:30 PM — Dena hears thump, Marcus says everything fine (Sheriff Report pp. 6-7)
2. June 11, 10:00 PM — Marcus puts Jaylen to bed (Dictation PDF p. 3)
3. June 12, 2:00 AM — Jaylen found crying, driven to ER (Dictation PDF p. 4)
4. June 12, 3:15 AM — ER admission, bilateral fractures found, Dr. Chowdhury notes different healing stages (Medical Records pp. 1-4)
5. June 12, 4:07 AM — Skeletal survey by Dr. Petrakis, right femur 3-5 days old, left humerus 24-48 hours (Medical Records pp. 3-4)
6. June 12, 7:30 AM — Dr. Chowdhury files mandatory abuse report (Medical Records p. 5)
7. June 12, 11:00 AM — Lt. Odom responds to hospital (Sheriff Report p. 1)

**Analysis:** Pass (10/10). Same strong performance as R1-R3. The case ID text filter works reliably on the timeline_events table. Full detail including times, descriptions, parties, and source documents with page citations.

---

### P7: Statements to law enforcement

```
What statements were made to law enforcement in case 2024-DR-42-0892?
```

**Score: 10**

#### Response

Found all 4 LE statements with full quotes and page citations:
1. Marcus Webb (June 13, p. 5, Sheriff Report): "Dena and I have been arguing a lot lately but I would never hurt my son. I don't know why she is saying I was in the room. I was not in his room after 10 PM."
2. Dena Holloway (June 13, p. 8, Sheriff Report): "Marcus has a temper. He gets frustrated when Jaylen won't stop crying. I have seen him grab Jaylen roughly by the arm before, maybe two or three times. I should have said something sooner."
3. Marcus Webb (June 13, p. 4, Sheriff Report): "I was on the couch all night. I did not go into Jaylen room after I put him down. I don't know how he got hurt. Maybe he climbed out of the crib and fell. He's been trying to climb out lately."
4. Dena Holloway (June 13, p. 7, Sheriff Report): "Actually, I need to correct something. Around 9:30 PM I heard a loud thump from Jaylen room. I assumed Marcus was in there. I called out and Marcus said everything was fine. I did not check on Jaylen at that time."

**Analysis:** Perfect — major improvement over R0-R3 (all scored 0). Successfully filtered statements by case + `made_to = 'Law Enforcement'` and returned all 4 direct quotes with dates and page citations. Both Marcus statements and both Dena statements (initial + revised). Instructions clearly helped with this query pattern.


---

### P8: People in Price TPR

```
List all people involved in the Price TPR case and their roles.
```

**Score: 0**

#### Response

"I'm sorry, I'm not sure how to help with that. Can you try rephrasing?"

**Analysis:** Complete refusal — same as R0-R3. The prompt requires resolving "Price TPR" to a case ID, then querying the people table. The agent can't handle the indirect case reference. Instructions didn't help.

---

### P9: TPR cases

```
Which cases involve Termination of Parental Rights?
```

**Score: 10**

#### Response

Found all 9 TPR cases with full summaries:
- 2025-DR-24-0382 — DSS v. Young (Kershaw) — Active
- 2024-DR-42-0424 — DSS v. Taylor (Sumter) — Active
- 2024-DR-22-0165 — DSS v. Nelson (Chesterfield) — Closed
- 2025-DR-45-0184 — DSS v. Morris (Richland) — Dismissed
- 2023-DR-25-0194 — DSS v. Williams (Kershaw) — Dismissed
- 2025-DR-09-0443 — DSS v. Reed (Dillon) — Active
- 2025-DR-21-0289 — DSS v. Parker (Richland) — Active
- 2024-DR-15-0341 — DSS v. Price (Richland) — Active
- 2024-DR-38-0342 — DSS v. Wright (Marlboro) — Closed

Each case included circuit, county, filed date, status, children, parents, treatment plan details, and outcomes.

**Analysis:** Pass (10/10). Back to R0 performance after R1-R3 regression. The instructions appear to have helped the agent use the full text "Termination of Parental Rights" instead of the abbreviation "TPR". This is the GCC GPT-4o agent — notable because all OpenAI models in Commercial failed this prompt except GPT-5 Reasoning.

---

### P10: Dena Holloway statements comparison

```
Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?
```

**Score: 0**

#### Response

"It appears that there are no statements from Dena Holloway made to either Hospital Staff or Lt. Odom in the database."

**Analysis:** Same failure as R0-R3. The `made_to` column stores "Medical Staff" not "Hospital Staff", and "Law Enforcement" not "Lt. Odom" — the agent can't resolve these natural-language references to the actual column values. Instructions didn't help with value-level mapping.

---

### P11: Time gap thump to hospital

```
What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?
```

**Score: 0**

#### Response

*(First attempt):* Query returned null for time gap — no matching records for "thump heard by Dena" and "Jaylen taken to hospital" descriptions.

*(Second attempt):* "There are no records in the legal_timelineevent table with the event type 'Thump Heard.'"

**Analysis:** Same failure as R0-R3. The agent searched for exact event type matches ("Thump Heard") instead of searching description text with LIKE. The thump event exists (event_type = 'Family', description contains 'thump') but the agent can't do fuzzy text matching on descriptions. Instructions didn't help.

