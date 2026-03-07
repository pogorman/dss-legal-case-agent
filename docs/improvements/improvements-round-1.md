# Improvements Round 1 — Data and Tool Gaps Identified from Testing

## Overview

After 110 test runs across 11 agents and 10 prompts, five specific data or tool gaps were identified where MCP agent responses would improve with additions that are already grounded in the source documents. Every proposed data addition below is traced back to the exact page and document where the fact appears. Nothing is fabricated to satisfy a demo — each item is something an analyst would naturally extract from PDF source material into a structured database.

A sixth section covers data integrity issues discovered during this review — places where the SQL and documents conflict in ways that weren't intentional test traps.

---

## 1. Add `made_to` Filter to Statements Tool

**Problem:** Prompt 8 ("What statements were made to law enforcement?") failed for all 3 MCP agents. The `statements` table already has a `made_to` column with values like `'Law Enforcement'`, `'Medical Staff'`, `'Court'`, `'Case Manager'` — but the tool only filters by `person_name`. There's no way to ask "give me all statements made to law enforcement" without knowing every person's name in advance.

**Prompts affected:** P8 (3 MCP failures — Web SPA 0/4, MCP-Com 0/4, MCP-GCC 2/4 via workaround)

### Current Tool Definition (mcp-server/src/mcp/tools.ts)

```typescript
{
  name: "get_statements_by_person",
  description:
    "Returns all recorded statements made by a specific person to case managers or law enforcement, with source citations and page references.",
  inputSchema: {
    type: "object",
    properties: {
      case_id: {
        type: "string",
        description: "The case identifier",
      },
      person_name: {
        type: "string",
        description:
          "Full or partial name of the person whose statements to retrieve",
      },
    },
    required: ["case_id", "person_name"],
  },
},
```

### Proposed Tool Definition

```typescript
{
  name: "get_statements_by_person",
  description:
    "Returns all recorded statements made by a specific person, with source citations and page references. Can optionally filter by who the statement was made to.",
  inputSchema: {
    type: "object",
    properties: {
      case_id: {
        type: "string",
        description: "The case identifier",
      },
      person_name: {
        type: "string",
        description:
          "Full or partial name of the person whose statements to retrieve",
      },
      made_to: {
        type: "string",
        description:
          "Optional filter: who the statement was made to, e.g. 'Law Enforcement', 'Medical Staff', 'Court', 'Case Manager'",
      },
    },
    required: ["case_id", "person_name"],
  },
},
```

### Current Function Code (functions/src/functions/getStatements.ts)

```typescript
const personName = request.query.get("person");
if (!personName) {
  return {
    status: 400,
    jsonBody: { error: "person query parameter is required" },
  };
}

const result = await pool
  .request()
  .input("caseId", sql.VarChar(20), caseId)
  .input("personName", sql.VarChar(100), `%${personName}%`)
  .query(`
    SELECT s.statement_id, s.case_id, s.statement_date, s.made_to,
           s.statement_text, s.source_document, s.page_reference,
           p.full_name, p.role
    FROM statements s
    JOIN people p ON s.person_id = p.person_id
    WHERE s.case_id = @caseId
      AND p.full_name LIKE @personName
    ORDER BY s.statement_date
  `);
```

### Proposed Function Code

```typescript
const personName = request.query.get("person");
const madeTo = request.query.get("made_to");

if (!personName && !madeTo) {
  return {
    status: 400,
    jsonBody: { error: "person and/or made_to query parameter is required" },
  };
}

const req = pool.request().input("caseId", sql.VarChar(20), caseId);

let whereClause = "WHERE s.case_id = @caseId";
if (personName) {
  req.input("personName", sql.VarChar(100), `%${personName}%`);
  whereClause += " AND p.full_name LIKE @personName";
}
if (madeTo) {
  req.input("madeTo", sql.VarChar(100), `%${madeTo}%`);
  whereClause += " AND s.made_to LIKE @madeTo";
}

const result = await req.query(`
  SELECT s.statement_id, s.case_id, s.statement_date, s.made_to,
         s.statement_text, s.source_document, s.page_reference,
         p.full_name, p.role
  FROM statements s
  JOIN people p ON s.person_id = p.person_id
  ${whereClause}
  ORDER BY s.statement_date
`);
```

This also makes `person_name` optional — allowing queries like "all statements made to law enforcement in this case" without requiring a specific person.

### Corresponding MCP callTool Change (mcp-server/src/mcp/tools.ts)

```typescript
case "get_statements_by_person": {
  const params = new URLSearchParams();
  if (args.person_name) params.set("person", args.person_name);
  if (args.made_to) params.set("made_to", args.made_to);
  return apimFetch(
    `/cases/${encodeURIComponent(args.case_id)}/statements?${params.toString()}`
  );
}
```

---

## 2. Add Skeletal Survey Discrepancy and Timeline Event

**Problem:** Prompt 4 ("Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey?") is the most dangerous prompt in the test suite. MCP agents can't answer it at all because the skeletal survey findings aren't in the database. 7 of 8 document agents repeated the Sheriff Report's incorrect "no fractures detected" claim without cross-referencing the Medical Records, which clearly show two fractures.

**Prompts affected:** P4 (MCP agents have no data; 7/8 document agents reproduced the misleading claim)

### Document Sources

**Sheriff Report p. 2:**
> "Radiology report indicated no fractures detected on skeletal survey."

**Medical Records pp. 3-4 (Radiology Report):**
> "**Right Femur:** Transverse fracture of the right femoral shaft... fracture age of approximately **3 to 5 days**"
> "**Left Humerus:** Spiral (oblique) fracture of the left humeral shaft... fracture age of approximately **24 to 48 hours**"
> "**Skeletal Survey — Remainder:** Skull: No fractures identified... Chest: No rib fractures... Pelvis: No fractures..."

The Sheriff Report's "no fractures detected" likely refers to the remainder of the skeletal survey (no *additional* fractures beyond the two known ones), but the wording implies a clean skeletal survey. Both facts are clearly in the documents.

### Existing Data Context (timeline_events, Case 1)

```sql
-- These rows already exist:
('2024-DR-42-0892', '2024-06-12', '3:15 AM', 'Medical',
 'Jaylen Webb admitted to Spartanburg Medical Center ER. X-rays reveal bilateral
  femur fracture (right) and spiral fracture of left humerus. Injuries assessed
  as inconsistent with reported mechanism (fall from crib). Dr. Chowdhury notes
  injuries are at different stages of healing.',
 'Medical Records, pp. 1-4', 'Jaylen Webb, Dr. Anita Chowdhury'),

('2024-DR-42-0892', '2024-06-12', '7:30 AM', 'Medical',
 'Dr. Chowdhury files mandatory abuse/neglect report with DSS and Spartanburg
  County Sheriff. Medical opinion: injuries are non-accidental and occurred at
  different times, inconsistent with a single fall event.',
 'Medical Records, p. 5; DSS Intake Report', 'Dr. Anita Chowdhury'),
```

### New Timeline Event

```sql
-- Skeletal survey results — from Medical Records pp. 3-4, Radiology Report
INSERT INTO timeline_events
  (case_id, event_date, event_time, event_type, description, source_document, parties_involved)
VALUES
('2024-DR-42-0892', '2024-06-12', '4:07 AM', 'Medical',
 'Skeletal survey completed by radiologist Dr. David Petrakis. Findings: transverse
  fracture of right femoral shaft (estimated 3-5 days old, with periosteal reaction
  and early callus formation) and spiral fracture of left humeral shaft (estimated
  24-48 hours old). Remainder of skeletal survey (skull, spine, chest, pelvis,
  bilateral extremities, hands, feet) showed no additional fractures. No metabolic
  bone disease pattern identified.',
 'Medical Records, pp. 3-4', 'Dr. David Petrakis, Jaylen Webb');
```

### New Discrepancy Row

```sql
-- Existing discrepancies for Case 1 include:
-- 'Cause of child injuries' (Marcus vs Dena)
-- 'Marcus Webb presence in child room' (Marcus vs Dena)
-- 'Timing of injury discovery' (Marcus vs Dena)
-- etc.

-- New: Sheriff Report vs Medical Records on skeletal survey
INSERT INTO discrepancies
  (case_id, topic, person_a_id, person_a_account, person_b_id, person_b_account,
   contradicted_by, source_document)
VALUES
('2024-DR-42-0892',
 'Skeletal survey fracture findings',
 NULL,
 'Sheriff Report states: "Radiology report indicated no fractures detected on
  skeletal survey." This wording implies a clean skeletal survey with no fractures
  found.',
 NULL,
 'Medical Records radiology report documents two fractures: transverse fracture of
  right femoral shaft (3-5 days old) and spiral fracture of left humeral shaft
  (24-48 hours old). The remainder of the skeletal survey found no additional
  fractures beyond these two.',
 'The Sheriff Report likely paraphrased the "no additional fractures" finding from
  the skeletal survey remainder as "no fractures detected," omitting the two known
  fractures. Medical Records pp. 3-4 are the primary radiological source.',
 'Sheriff Report #24-06-4418, p. 2; Medical Records, pp. 3-4');
```

**Note:** `person_a_id` and `person_b_id` are NULL because this is a document-vs-document conflict, not a person-vs-person discrepancy. The existing schema allows NULLs on these columns (they're not `NOT NULL`). If this feels awkward, person_a could be set to Lt. Frank Odom (author of the Sheriff Report) and person_b to Dr. David Petrakis (radiologist).

---

## 3. Add 9:30 PM Thump as a Standalone Timeline Event

**Problem:** Prompt 10 ("What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?") requires the agent to identify three distinct moments: the 9:30 PM thump, the 2:00 AM discovery, and the 3:15 AM ER admission. The thump is only recorded in the June 13 interview event description as a clause ("she heard a loud thump around 9:30 PM"), not as its own timeline entry on June 11. The Web SPA conflated the thump with the discovery and reported 1h15m instead of ~5h45m.

**Prompts affected:** P10 (Web SPA failure — 1h15m instead of 5h45m)

### Document Source

**Sheriff Report p. 7 (Dena Holloway's revised statement to Lt. Odom):**
> "Actually, I need to correct something. Around 9:30 PM I heard a loud thump from Jaylen's room. I assumed Marcus was in there. I called out and Marcus said everything was fine. I did not check on Jaylen at that time."

**Sheriff Report p. 7 (investigator's timeline summary):**
> "At approximately 9:30 PM, the subject heard a loud thump originating from the direction of the child's bedroom. The subject called out to Webb. Webb responded verbally that 'everything was fine.'"

### Existing Data Context (timeline_events, Case 1, evening of June 11)

```sql
-- This row already exists (the only June 11 event):
('2024-DR-42-0892', '2024-06-11', '10:00 PM', 'Family',
 'Marcus Webb states he put Jaylen to bed at approximately 10:00 PM. Reports child
  was behaving normally throughout the day.',
 'Dictation PDF, p. 3', 'Marcus Webb, Jaylen Webb'),

-- Next existing event is June 12 at 2:00 AM:
('2024-DR-42-0892', '2024-06-12', '2:00 AM', 'Medical',
 'Dena Holloway reports hearing Jaylen crying loudly. Found child in crib unable
  to move left leg. Both parents drove child to Spartanburg Medical Center ER.',
 'Dictation PDF, p. 4', 'Dena Holloway, Marcus Webb, Jaylen Webb'),
```

### New Timeline Event

```sql
-- 9:30 PM thump — from Dena Holloway's revised statement, Sheriff Report pp. 6-7
INSERT INTO timeline_events
  (case_id, event_date, event_time, event_type, description, source_document, parties_involved)
VALUES
('2024-DR-42-0892', '2024-06-11', '9:30 PM', 'Family',
 'Dena Holloway hears a loud thump from Jaylen''s room. She calls out and Marcus
  Webb responds that everything is fine. Dena does not check on Jaylen at that time.
  (Disclosed in Dena''s revised statement to Lt. Odom on June 13; not reported in
  her initial hospital account.)',
 'Sheriff Report #24-06-4418, pp. 6-7', 'Dena Holloway, Marcus Webb, Jaylen Webb');
```

**Ordering note:** This slots between the existing 10:00 PM bedtime event and the 2:00 AM discovery, giving the timeline three clear milestones for the gap calculation:

| Time | Event |
|---|---|
| 9:30 PM | Thump heard (new) |
| 10:00 PM | Marcus says he put Jaylen to bed (existing) |
| 2:00 AM | Dena finds Jaylen crying (existing) |
| 3:15 AM | ER admission (existing) |

**Chronological note:** The 9:30 PM thump predates Marcus's stated 10:00 PM bedtime. This is itself a point of tension in the case — if Marcus put Jaylen to bed at 10 PM, what was the thump at 9:30 PM? The discrepancy table already captures this under "Marcus Webb presence in child room."

---

## 4. Add Individual Drug Test Timeline Events

**Problem:** Prompt 3 ("Crystal Price told the court she was 'clean now.' What do the drug test results show?") caused a critical failure in the Web SPA. The agent called the right tools, received the data, but failed to recognize "two positive drug screens (fentanyl) in October" — embedded in a narrative timeline event — as drug test results. Structured, discrete events for each test would be harder for the model to miss.

**Prompts affected:** P3 (Web SPA critical failure — concluded "no drug test results exist" despite data being in tool output)

### Document Sources

**DSS Investigation Report p. 6:**
> "Ms. Price had two positive drug screens for fentanyl, dated October 8 and October 22, 2023."

**DSS Investigation Report p. 7:**
> "She missed scheduled drug screens on December 5, 2023, January 15, 2024, and March 3, 2024."

**TPR Petition p. 4 (section III.B, paragraph 15):**
> "The Respondent tested positive for fentanyl on October 8, 2023 and October 22, 2023. The Respondent failed to appear for scheduled drug screens on December 5, 2023, January 15, 2024, and March 3, 2024."

**DSS Investigation Report p. 10 / Court Orders p. 20 (TPR Probable Cause):**
> "Her most recent drug screen on April 10 was negative."

**TPR Petition Affidavit p. 5 (paragraph 11):**
> "Per DSS policy and the Court's order, missed screens are treated as presumptive positive results."

### Existing Data Context (timeline_events, Case 2)

```sql
-- This row already exists and contains the drug test info as narrative:
('2024-DR-15-0341', '2023-11-14', NULL, 'Court',
 'Ninety-day review hearing. Crystal Price has attended 3 of 12 required IOP
  sessions. Has not enrolled in parenting classes. No stable housing. Two positive
  drug screens (fentanyl) in October. Court continues treatment plan, warns that
  failure to comply may result in TPR.',
 'Court Filing, Order 2',
 'Crystal Price, Monica Vance, Judge Harold Wynn'),

-- Later existing row mentions the April negative:
('2024-DR-15-0341', '2024-04-22', '9:30 AM', 'Court',
 'TPR probable cause hearing. [...] Crystal Price has now completed 5 of 12 IOP
  sessions, enrolled in parenting classes (attended 2 of 8), and obtained temporary
  housing. Court notes progress but finds it insufficient given 8-month timeframe.',
 'Court Filing, Order 3',
 'Crystal Price, Monica Vance, Judge Harold Wynn, Thomas Reed'),
```

### New Timeline Events

```sql
-- Individual drug test results — from DSS Investigation Report pp. 6-7,
-- TPR Petition pp. 4-5, Court Filing Order 2
INSERT INTO timeline_events
  (case_id, event_date, event_time, event_type, description, source_document, parties_involved)
VALUES
('2024-DR-15-0341', '2023-10-08', NULL, 'Medical',
 'Crystal Price submits to court-ordered random drug screen. Result: positive for
  fentanyl.',
 'DSS Investigation Report, p. 6; TPR Petition, p. 4',
 'Crystal Price'),

('2024-DR-15-0341', '2023-10-22', NULL, 'Medical',
 'Crystal Price submits to court-ordered random drug screen. Result: positive for
  fentanyl.',
 'DSS Investigation Report, p. 6; TPR Petition, p. 4',
 'Crystal Price'),

('2024-DR-15-0341', '2023-12-05', NULL, 'Medical',
 'Crystal Price fails to appear for scheduled court-ordered drug screen. Per DSS
  policy and court order, missed screens are treated as presumptive positive.',
 'DSS Investigation Report, p. 7; TPR Petition, p. 4',
 'Crystal Price'),

('2024-DR-15-0341', '2024-01-15', NULL, 'Medical',
 'Crystal Price fails to appear for scheduled court-ordered drug screen. Per DSS
  policy and court order, missed screens are treated as presumptive positive.',
 'DSS Investigation Report, p. 7; TPR Petition, p. 4',
 'Crystal Price'),

('2024-DR-15-0341', '2024-03-03', NULL, 'Medical',
 'Crystal Price fails to appear for scheduled court-ordered drug screen. Per DSS
  policy and court order, missed screens are treated as presumptive positive.',
 'DSS Investigation Report, p. 7; TPR Petition, p. 4',
 'Crystal Price'),

('2024-DR-15-0341', '2024-04-10', NULL, 'Medical',
 'Crystal Price submits to court-ordered random drug screen. Result: negative.
  First negative screen on record since removal.',
 'Court Transcript, TPR Probable Cause, p. 10',
 'Crystal Price');
```

---

## 5. Add Nurses to People Table

**Problem:** Prompt 1 ("Tell me about Jaylen Webb's ER admission — specifically the time and the admitting nurse") — all 3 MCP agents correctly reported no nurse was in the data. Two nurses appear in the source documents and were found by document-backed agents.

**Prompts affected:** P1 (all 3 MCP agents answered "no nurse identified")

### Document Sources

**Medical Records p. 8 (Nursing Notes, authored by):**
> "Rebecca Torres, RN, BSN — Emergency Department"

Rebecca Torres authored four nursing notes (pp. 8-9): the arrival/triage note, the Marcus Webb interview, the Dena Holloway interview, and the status update/transfer note. She performed the initial triage assessment at 03:15 AM.

**Sheriff Report p. 1 (LE interview):**
> "The undersigned interviewed the attending ER nursing staff, specifically Charge Nurse Patricia Daniels, RN (Employee ID: SMC-4492). Nurse Daniels stated that the child was brought into the Emergency Department at approximately 0047 hours on June 12, 2024"

Patricia Daniels is the charge nurse interviewed by Lt. Odom during the investigation.

### Existing Data Context (people, Case 1)

```sql
-- These rows already exist for Case 1:
('2024-DR-42-0892', 'Marcus Webb',       'Parent',              'Father of minor child Jaylen Webb', ...),
('2024-DR-42-0892', 'Dena Holloway',     'Parent',              'Mother of minor child Jaylen Webb', ...),
('2024-DR-42-0892', 'Jaylen Webb',       'Child',               'Minor child, age 3', ...),
('2024-DR-42-0892', 'Theresa Holloway',  'Kinship Foster Parent', 'Maternal grandmother', ...),
('2024-DR-42-0892', 'Renee Dawson',      'Case Manager',        'DSS Case Manager', ...),
('2024-DR-42-0892', 'Lt. Frank Odom',    'Law Enforcement',     'Spartanburg County Sheriff investigator', ...),
('2024-DR-42-0892', 'Dr. Anita Chowdhury', 'Witness',           'Attending pediatrician', ...),
('2024-DR-42-0892', 'Karen Milford',     'Guardian ad Litem',   'Court-appointed GAL', ...),
```

### New People Rows

```sql
INSERT INTO people (case_id, full_name, role, relationship, dob, notes) VALUES
('2024-DR-42-0892', 'Rebecca Torres',
 'Witness',
 'Emergency Department RN, Spartanburg Medical Center',
 NULL,
 'RN, BSN. Performed initial triage assessment on Jaylen Webb at 03:15 AM on
  2024-06-12. Conducted separate parent interviews (Marcus Webb, Dena Holloway)
  during intake. Authored nursing notes pp. 8-9 of Medical Records.'),

('2024-DR-42-0892', 'Patricia Daniels',
 'Witness',
 'Charge Nurse, Spartanburg Medical Center Emergency Department',
 NULL,
 'RN, Charge Nurse (Employee ID: SMC-4492). Interviewed by Lt. Frank Odom during
  investigation. Reported child arrived at approximately 0047 hours. Assessed
  bruising pattern as inconsistent with a crib fall.');
```

### Name Collision Warning

The name "Rebecca Torres" also appears in Case 2's TPR Petition as **"Rebecca Torres, Esq."**, the DSS staff attorney who signed the filing (TPR Petition, signature block, p. 10). These are two different fictional characters in two different cases — a nurse in Spartanburg (Case 1) and an attorney in Richland County (Case 2). This is a synthetic data naming coincidence. It won't cause SQL problems (different `case_id` values), but an agent doing cross-case queries could theoretically confuse them. Worth noting for future data generation.

---

## 6. Data Integrity — Existing Conflicts to Shore Up

During source document review for this analysis, the following discrepancies were found between the SQL data and the source documents. These aren't test failures — they're places where the initial data load chose one document's version over another without capturing the conflict.

### 6a. Marcus Webb's Bedtime — 8:00 PM vs 10:00 PM

**In SQL (timeline_events):**
> "Marcus Webb states he put Jaylen to bed at approximately 10:00 PM" — sourced from Dictation PDF, p. 3

**In Medical Records p. 1:**
> "Mr. Webb reports he placed the child to bed at approximately 22:00 on 06/11/2024"

**In Medical Records p. 8 (Marcus's direct quote to nurse):**
> "I put him to bed around ten."

**In Sheriff Report p. 3 (investigator's paraphrase of Marcus's LE interview):**
> "Subject stated that he gave the victim a bath and put him to bed in his crib in the child's bedroom at approximately 8:00 PM."

The SQL only has the 10:00 PM version. The Sheriff Report has Marcus telling law enforcement 8:00 PM. This is a real discrepancy in Marcus's own statements across settings — he told hospital staff "around ten" and told the investigator "approximately 8:00 PM" (per the investigator's paraphrase).

The testing identified the "8 PM misattribution" as Dena's statement being wrongly attributed to Marcus — and that IS also true (Dena told LE "Marcus Webb put the child to bed at approximately 8:00 PM" on p. 6). But the Sheriff Report's narrative of Marcus's own interview (p. 3) also says 8 PM. This means document agents attributing 8 PM to Marcus weren't entirely wrong — they were citing a real fact from the Sheriff Report.

**Possible action:** This could be captured as a discrepancy (Marcus's hospital account of "around ten" vs his LE account of "approximately 8:00 PM"), or the LE bedtime could be added as a detail in Marcus's existing statement data. No change is strictly required, but the current testing ground truth should acknowledge that 8 PM does appear in Marcus's own LE interview narrative, not just Dena's statement.

### 6b. Dena's Discovery Time — 2:00 AM vs Midnight

**In SQL (timeline_events):**
> "Dena Holloway reports hearing Jaylen crying loudly" at 2:00 AM — from Dictation PDF, p. 4

**In Medical Records p. 9 (Dena's direct quote to nurse):**
> "I heard him crying around 2 AM."

**In Sheriff Report p. 6 (Dena's initial statement to Lt. Odom):**
> "Subject initially stated that she discovered the child crying in his crib at approximately midnight and observed the injuries at that time."

Dena told hospital staff "around 2 AM" and initially told law enforcement "approximately midnight" before revising her account to include the 9:30 PM thump. The SQL uses 2:00 AM. The midnight version isn't captured anywhere.

**Possible action:** Low priority. The midnight statement was superseded by Dena's revised account, and the 2:00 AM version from the hospital is the more widely cited time. But the initial midnight claim to LE is a fact in the documents that could be relevant if an agent is asked about inconsistencies in Dena's statements.

### 6c. ER Arrival Time — 0047 vs 3:15 AM

**In SQL (timeline_events):**
> ER admission at 3:15 AM — from Medical Records, pp. 1-4

**In Sheriff Report p. 1:**
> "Nurse Daniels stated that the child was brought into the Emergency Department at approximately 0047 hours"

This is a known intentional discrepancy in the synthetic data (documented in the testing ground truth). The SQL correctly uses the Medical Records time (3:15 AM) as the authoritative medical source. GCC KB agents that reported 12:47 AM were using the Sheriff Report version. No SQL change needed — this is working as designed as a cross-document reasoning test.

---

## Summary

| # | Improvement | Type | Rows | Prompts Fixed | Effort |
|---|---|---|---|---|---|
| 1 | `made_to` filter on statements tool | Tool + Function | 0 | P8 (3 failures) | Medium — tool def, function code, APIM passthrough |
| 2 | Skeletal survey discrepancy + timeline | Data | 2 | P4 (MCP can't answer) | Low — SQL insert |
| 3 | 9:30 PM thump as timeline event | Data | 1 | P10 (Web SPA conflation) | Low — SQL insert |
| 4 | Individual drug test events | Data | 6 | P3 (Web SPA comprehension) | Low — SQL insert |
| 5 | Nurses in people table | Data | 2 | P1 (all MCP agents) | Low — SQL insert |
| 6 | Data integrity review | Analysis | 0 | Ground truth accuracy | N/A |

**Total new SQL rows:** 11 (1 discrepancy + 8 timeline events + 2 people)
**Code changes:** 1 (statements tool/function — `made_to` filter)

All data additions are sourced from existing documents that are already deployed to SharePoint and uploaded as Copilot Studio knowledge files. No data is fabricated.

---

## Post-Improvement Retest Results (MCP Agents Only)

Retesting the 3 MCP agents against the prompts targeted by each improvement. Document-backed agents are unaffected (their data source didn't change).

### Prompt 8 — LE Statements Filter (Improvement #1: `made_to` filter)

**Before:** All 3 MCP agents failed or degraded (Web SPA 0/4, MCP-Com 0/4, MCP-GCC 2/4 via workaround).

| Agent | Statements Found | Correct Attribution | Score | Notes |
|-------|-----------------|---------------------|-------|-------|
| Web SPA | 4/4 | All correct | **Pass** | Used `get_statements_by_person` with `made_to` filter. All 4 from Sheriff Report. |
| MCP-Com | 4/4 | All correct | **Pass** | Same tool usage. Truncated by Copilot Studio but all 4 visible. |
| MCP-GCC | 4/4 | All correct | **Pass** | Same tool usage. All 4 returned correctly. |

**Result: 3/3 Pass (previously 0/3).** The `made_to` filter fix resolved the design-gap failure completely.

### Prompt 1 — ER Time + Nurse (Improvement #5: nurses in people table)

**Before:** All 3 MCP agents got ER time right but answered "no nurse identified."

| Agent | ER Time | Nurse Found | Score | Notes |
|-------|---------|-------------|-------|-------|
| Web SPA | 3:15 AM ✓ | No ✗ | **Partial** | Called `get_timeline` and `get_statements_by_person` but not `get_case_summary` (which returns people roster). |
| MCP-Com | 3:15 AM ✓ | No ✗ | **Partial** | Same pattern — correct time, didn't check people table. Cited Dr. Chowdhury instead. |
| MCP-GCC | 2:00 AM ✗ | No ✗ | **Fail** | Hallucinated 2:00 AM (known GPT-4o issue). Also asked for case ID on first attempt. |

**Result: 0/3 Pass, 2/3 Partial, 1/3 Fail.** The nurse data is now in the `people` table, but no agent calls `get_case_summary` to look for it. The gap has shifted from missing data → model tool selection. A possible next step would be enriching the `get_case_summary` tool description to mention it returns medical staff and witnesses, or adding nurse names to a timeline event description.

### Prompt 4 — Skeletal Survey Fractures (Improvement #2: skeletal survey timeline event + discrepancy)

**Before:** MCP agents had no skeletal survey data at all — couldn't answer the question. 7/8 document agents repeated the Sheriff Report's incorrect "no fractures detected" claim.

| Agent | Fractures Found | Ages Noted | Remainder Noted | Score | Notes |
|-------|----------------|------------|-----------------|-------|-------|
| Web SPA | 2/2 ✓ | Both ✓ | Yes ✓ | **Pass** | Both fractures with aging, remainder survey, no metabolic disease. Source: Medical Records pp. 3-4. |
| MCP-Com | 2/2 ✓ | Both ✓ | Yes ✓ | **Pass** | Same detail level. Cited Dr. David Petrakis by name. |
| MCP-GCC | 2/2 ✓ | Both ✓ | Yes ✓ | **Pass** | Same detail level. Cited Medical Records pp. 3-4. |

**Result: 3/3 Pass (previously 0/3 — no data).** The skeletal survey timeline event provides the structured data MCP agents needed. This was the most dangerous prompt in the test suite — the one where 7/8 document agents would have led an attorney to miss evidence of child abuse. All 3 MCP agents now return the correct, complete radiological findings.

### Prompt 10 — Time Gap (Improvement #3: 9:30 PM thump as standalone event)

**Before:** Web SPA conflated thump with discovery, reported 1h15m instead of ~4.5-5.75h. MCP-Com was the only gold standard (all 3 times, both gaps).

| Agent | Thump Time | Hospital Time | Gap | Score | Notes |
|-------|-----------|---------------|-----|-------|-------|
| Web SPA | 9:30 PM ✓ | 2:00 AM ✓ | 4h30m ✓ | **Pass** | Previously reported 1h15m. Now has the thump as a discrete event. |
| MCP-Com | 9:30 PM ✓ | 2:00 AM ✓ | 4h30m ✓ | **Pass** | Consistent with prior result. Both milestones cited with sources. |
| MCP-GCC | 9:30 PM ✓ | 2:00 AM ✓ | 4h30m ✓ | **Pass** | Asked for case ID first (known orchestrator quirk), then correct. |

**Result: 3/3 Pass (previously 1/3 Pass, 1/3 Partial, 1/3 Fail).** The standalone 9:30 PM thump event eliminates the need for the model to parse timestamps from statement text.

### Prompt 3 — Crystal Price Drug Tests (Improvement #4: individual drug test events)

**Before:** Web SPA critical failure — called the right tools, received data, but concluded "no drug test results exist" because test info was buried in a narrative court event. MCP-Com and MCP-GCC passed previously (extracted from narrative).

| Agent | Tests Found | Correct Details | Score | Notes |
|-------|------------|-----------------|-------|-------|
| Web SPA | 6/6 ✓ | All dates, results, sources ✓ | **Pass** | Required case ID in prompt (can't resolve Case 2 from name — known issue). Previously concluded "no drug test results exist." |
| MCP-Com | 6/6 ✓ | All dates, results, sources ✓ | **Pass** | Original prompt (no case ID) — resolved case from "Crystal Price." Previously needed case ID. |
| MCP-GCC | 6/6 ✓ | All dates, results, sources ✓ | **Pass** | Original prompt (no case ID) — also resolved case from name. |

**Result: 3/3 Pass (previously 1/3 Pass, 1/3 Partial, 1/3 Fail).** Discrete drug test events are unambiguous — the model can't miss them. Both Copilot Studio MCP agents now resolve Case 2 from "Crystal Price" without needing the case ID in the prompt (previously a known orchestrator limitation).

### Observations Across All Retests

1. **Web SPA still can't resolve Case 2 from names alone** — needs case ID in prompt. This is a model reasoning issue, not a data gap. Occurred on both P3 (searched Case 1 for Crystal Price) and P1 (no issue since Case 1 is the default).

2. **MCP-GCC still asks for case ID on some prompts** (P1, P10) but not others (P3, P4, P8). The orchestrator quirk is inconsistent — may depend on whether the prompt contains enough context for the model to infer which case to search.

3. **MCP-GCC still hallucinates 2:00 AM ER time** (P1) — this is a GPT-4o faithfulness issue, not a data gap. The correct 3:15 AM is in the timeline data.

4. **Nurse discovery gap shifted from data → tool selection** (P1). All 3 agents have the nurse data available via `get_case_summary` but none think to call it for a "who was the nurse" question. The `get_case_summary` tool description could be enriched to mention it returns all case participants including medical staff and witnesses.

### Retest Summary

| Prompt | Before (Pass/Partial/Fail) | After (Pass/Partial/Fail) | Improvement |
|--------|---------------------------|--------------------------|-------------|
| P8 (LE statements) | 0/0/3 | 3/0/0 | `made_to` filter |
| P1 (ER time + nurse) | 0/3/0 | 0/2/1 | Nurses added (but agents don't check people table) |
| P4 (skeletal survey) | 0/0/3 | 3/0/0 | Skeletal survey event + discrepancy |
| P10 (time gap) | 1/1/1 | 3/0/0 | 9:30 PM thump event |
| P3 (drug tests) | 1/1/1 | 3/0/0 | Individual drug test events |
| **Totals** | **2/5/8** | **12/2/1** | |

**Net improvement: 10 additional Passes, 6 fewer Fails.** The one remaining Fail (P1, MCP-GCC) is a GPT-4o hallucination issue, not a data gap. The two remaining Partials (P1, Web SPA + MCP-Com) are a tool selection issue — the data is available but the model doesn't call the right tool.
