# Document-to-Database Mapping Guide

## How Legal PDFs Become Queryable Structured Data

This guide illustrates the extraction pipeline from source legal documents (PDFs) to the structured SQL tables that power the MCP agent. Every row in the database traces back to a specific page and paragraph in a source document. The pipeline described here reflects a realistic enterprise pattern using Azure Document Intelligence, Power Automate AI Builder, or similar extraction tooling.

---

## 1. Source Document Inventory

Each case produces a standard set of legal documents. These arrive as PDFs (or Word documents converted to PDF) from case management systems, courts, hospitals, and law enforcement.

### Case 1: 2024-DR-42-0892 (CPS Emergency Removal)

| Document | Pages | Primary Content |
|---|---|---|
| Medical_Records.pdf | 9 | ER admission, radiology, physician assessment, nursing notes |
| Sheriff_Report_24-06-4418.pdf | 8+ | Investigation narrative, parent interviews, evidence log |
| DSS_Investigation_Report.pdf | 15 | Intake, home visit, interviews, analysis, recommendations |
| Court_Orders_and_Filings.pdf | ~12 | Emergency removal, probable cause, 30-day review orders |
| GAL_Report.pdf | ~4 | Guardian ad Litem observations and recommendations |
| Home_Study_Report.pdf | ~3 | Kinship placement assessment |

### Case 2: 2024-DR-15-0341 (Termination of Parental Rights)

| Document | Pages | Primary Content |
|---|---|---|
| DSS_Investigation_Report.pdf | 11 | Intake, home visit, compliance, TPR recommendation |
| Court_Orders_and_Filings.pdf | ~20 | Emergency removal through TPR probable cause (6 orders) |
| TPR_Petition_and_Affidavit.pdf | ~8 | Statutory grounds, affidavit, prayer for relief |
| Substance_Abuse_Evaluation.pdf | ~6 | Clinical evaluation, diagnosis, treatment recommendation |
| GAL_Reports.pdf | ~6 | Two reports: initial and updated |

---

## 2. Extraction Pipeline Overview

```
  PDF Documents
       |
       v
  +-----------------------+
  | Document Intelligence |    Layout analysis, table extraction,
  | or AI Builder         |    key-value pair recognition
  +-----------------------+
       |
       v
  +-----------------------+
  | Entity Extraction     |    Names, dates, roles, case numbers,
  | (GPT-4 / custom)      |    quoted statements, medical findings
  +-----------------------+
       |
       v
  +-----------------------+
  | Classification &      |    Route extracted entities to the
  | Mapping Rules         |    correct SQL table based on content type
  +-----------------------+
       |
       v
  +-----------------------+
  | Azure SQL             |    cases, people, timeline_events,
  | (structured tables)   |    statements, discrepancies
  +-----------------------+
```

**Key extraction patterns by document type:**

| Document Type | Primary extraction target | Extraction approach |
|---|---|---|
| Court Orders | Case metadata, timeline events, quoted statements | Table/header extraction + date parsing |
| Medical Records | Timeline events, people, medical findings | Structured header fields + narrative parsing |
| Sheriff Reports | Timeline events, quoted statements, discrepancies | Narrative interview parsing + timestamp extraction |
| DSS Investigation Reports | Everything — interviews, timeline, compliance | Section-based extraction (each section maps to a different table) |
| Substance Abuse Evaluations | People, timeline events | Structured intake form fields |
| GAL Reports | People, statements, timeline events | Narrative parsing with attribution |

---

## 3. Table-by-Table Mapping

### 3a. `cases` Table — Extracted from Court Filings Header

The case record comes from the header block that appears at the top of every court filing.

**Source: Court_Orders_and_Filings.pdf, p. 1**

```
STATE OF SOUTH CAROLINA          )     IN THE FAMILY COURT
                                 )     FIFTH JUDICIAL CIRCUIT
COUNTY OF RICHLAND               )     CASE NO. 2023-DR-15-0341

SOUTH CAROLINA DEPARTMENT OF     )
SOCIAL SERVICES,                 )
          Plaintiff,             )     EMERGENCY REMOVAL ORDER
     v.                          )
CRYSTAL PRICE,                   )
          Respondent.            )

CHILDREN:
     Amari Price, DOB: September 28, 2017 (age 5)
     Destiny Price, DOB: May 14, 2019 (age 4)

DATE: August 8, 2023, 4:00 PM
BEFORE: The Honorable Harold Wynn, Family Court Judge
```

**Extracted to SQL:**

```sql
INSERT INTO cases (case_id, case_title, case_type, circuit, county, filed_date,
                   status, plaintiff, summary)
VALUES (
  '2024-DR-15-0341',                              -- CASE NO. from header
  'DSS v. Price — Termination of Parental Rights', -- plaintiff v. respondent + order type
  'Termination of Parental Rights',                -- from petition filing type
  'Fifth Judicial Circuit',                        -- from header
  'Richland',                                      -- COUNTY OF from header
  '2024-02-08',                                    -- DATE FILED from TPR Petition
  'Active',                                        -- from case status
  'SC Department of Social Services',              -- Plaintiff from header
  'Petition for termination of parental rights...' -- summarized from petition body
);
```

**Extraction method:** Document Intelligence key-value pair extraction on the court filing header block. Case number, circuit, and county are in fixed positions. The `case_type` requires classifying the filing type (Emergency Removal, TPR, etc.) from the order title.

---

### 3b. `people` Table — Extracted from Multiple Documents

People appear across every document type. The extraction tool must deduplicate across sources (the same person appears in medical records, court filings, and investigation reports).

**Source: Medical_Records.pdf, p. 1 (header table)**

```
| Attending Physician | Anita Chowdhury, MD, FAAP |
| Admission Date/Time | 06/12/2024, 03:15 AM      |
```

**Source: Medical_Records.pdf, p. 8 (nursing notes byline)**

```
Author: Rebecca Torres, RN, BSN — Emergency Department
```

**Source: Sheriff_Report_24-06-4418.pdf, p. 1 (narrative)**

```
The undersigned interviewed the attending ER nursing staff, specifically
Charge Nurse Patricia Daniels, RN (Employee ID: SMC-4492).
```

**Source: Court_Orders_and_Filings.pdf, p. 4 (appearances table)**

```
| Party             | Representation  |
|-------------------|-----------------|
| Monica Vance      | DSS Case Manager|
| Thomas Reed, Esq. | Guardian ad Litem|
```

**Extracted to SQL:**

```sql
INSERT INTO people (case_id, full_name, role, relationship, dob, notes) VALUES
-- From Medical Records p. 1 header table:
('2024-DR-42-0892', 'Dr. Anita Chowdhury', 'Witness',
 'Attending pediatrician, Spartanburg Medical Center', NULL,
 'Board-certified pediatrician. Examined Jaylen Webb on admission.'),

-- From Medical Records p. 8 nursing notes byline:
('2024-DR-42-0892', 'Rebecca Torres', 'Witness',
 'Emergency Department RN, Spartanburg Medical Center', NULL,
 'RN, BSN. Performed initial triage assessment. Authored nursing notes pp. 8-9.'),

-- From Sheriff Report p. 1 narrative:
('2024-DR-42-0892', 'Patricia Daniels', 'Witness',
 'Charge Nurse, Spartanburg Medical Center Emergency Department', NULL,
 'RN, Charge Nurse (Employee ID: SMC-4492). Interviewed by Lt. Frank Odom.'),

-- From Court Orders appearances table:
('2024-DR-15-0341', 'Thomas Reed', 'Guardian ad Litem',
 'Court-appointed GAL for Amari and Destiny Price', NULL,
 'Appointed September 2023. Recommends TPR and adoption by Patterson family.');
```

**Extraction method:** People are the hardest entity to extract reliably because they appear in different formats:
- **Structured headers** (Medical Records intake form) — key-value extraction
- **Bylines** ("Author: Rebecca Torres, RN, BSN") — pattern matching on `Author:` prefix
- **Narrative mentions** ("Charge Nurse Patricia Daniels, RN") — named entity recognition
- **Court appearance tables** — table extraction

Deduplication is critical. "Dr. Anita Chowdhury" appears on Medical Records pp. 1, 5, 6, 7; in the Sheriff Report p. 2; in the DSS Investigation Report p. 1; and in Court Transcripts. All of these are the same person and should produce one `people` row, not six.

---

### 3c. `timeline_events` Table — Extracted from Narrative and Structured Sources

Timeline events are the most varied extraction target. They come from three distinct patterns:

#### Pattern 1: Structured date/time fields (Medical Records)

**Source: Medical_Records.pdf, p. 1**

```
Admission Date/Time: 06/12/2024, 03:15 AM
Time of Arrival: 03:15 AM (via private vehicle)
Triage Level: ESI Level 2 — Emergent
```

**Source: Medical_Records.pdf, pp. 3-4 (Radiology Report)**

```
Exam: Skeletal survey, pediatric (complete)
Date: 06/12/2024, 04:07 AM
Ordering Physician: Anita Chowdhury, MD
...
Right Femur: Transverse fracture of the right femoral shaft...
  fracture age of approximately 3 to 5 days
Left Humerus: Spiral (oblique) fracture of the left humeral shaft...
  fracture age of approximately 24 to 48 hours
Skeletal Survey — Remainder: ... No fractures identified ...
```

**Extracted to SQL:**

```sql
-- From Medical Records p. 1 — structured admission fields:
('2024-DR-42-0892', '2024-06-12', '3:15 AM', 'Medical',
 'Jaylen Webb admitted to Spartanburg Medical Center ER. X-rays reveal bilateral
  femur fracture (right) and spiral fracture of left humerus. Injuries assessed
  as inconsistent with reported mechanism (fall from crib).',
 'Medical Records, pp. 1-4', 'Jaylen Webb, Dr. Anita Chowdhury'),

-- From Medical Records pp. 3-4 — radiology report header + findings:
('2024-DR-42-0892', '2024-06-12', '4:07 AM', 'Medical',
 'Skeletal survey completed by radiologist Dr. David Petrakis. Findings: transverse
  fracture of right femoral shaft (estimated 3-5 days old) and spiral fracture of
  left humeral shaft (estimated 24-48 hours old). Remainder of skeletal survey
  showed no additional fractures.',
 'Medical Records, pp. 3-4', 'Dr. David Petrakis, Jaylen Webb'),
```

**Extraction method:** Date and time fields are in structured header positions. The description is synthesized from the findings section. The `event_type` ("Medical") is classified from the document type and section context.

#### Pattern 2: Court order paragraphs with embedded dates

**Source: Court_Orders_and_Filings.pdf (Case 2), Ninety-Day Review, Finding 4**

```
4. Drug Screening Results: Respondent tested positive for fentanyl on
   two (2) separate occasions in October 2023.
```

**Source: TPR_Petition_and_Affidavit.pdf, p. 4 (paragraph 16, with specific dates)**

```
16. Respondent tested positive for fentanyl on October 8, 2023 and
    October 22, 2023. The Respondent failed to appear for scheduled
    drug screens on December 5, 2023, January 15, 2024, and March 3, 2024.
```

**Extracted to SQL:**

```sql
-- Court Orders give "October 2023" (imprecise).
-- TPR Petition gives exact dates. Use the most specific source:
('2024-DR-15-0341', '2023-10-08', NULL, 'Medical',
 'Crystal Price submits to court-ordered random drug screen. Result: positive
  for fentanyl.',
 'DSS Investigation Report, p. 6; TPR Petition, p. 4', 'Crystal Price'),

('2024-DR-15-0341', '2023-10-22', NULL, 'Medical',
 'Crystal Price submits to court-ordered random drug screen. Result: positive
  for fentanyl.',
 'DSS Investigation Report, p. 6; TPR Petition, p. 4', 'Crystal Price'),

('2024-DR-15-0341', '2023-12-05', NULL, 'Medical',
 'Crystal Price fails to appear for scheduled court-ordered drug screen. Per DSS
  policy and court order, missed screens are treated as presumptive positive.',
 'DSS Investigation Report, p. 7; TPR Petition, p. 4', 'Crystal Price'),
```

**Extraction method:** Date extraction from numbered paragraphs in legal filings. Multiple documents may reference the same events at different levels of specificity. The extraction pipeline should prefer the most specific source (exact dates from the TPR Petition over "in October" from Court Orders).

#### Pattern 3: Narrative events with timestamps buried in prose

**Source: Sheriff_Report_24-06-4418.pdf, p. 7 (Dena Holloway's revised statement)**

```
The subject then provided the following revised statement:

    "Actually, I need to correct something. Around 9:30 PM I heard
    a loud thump from Jaylen's room. I assumed Marcus was in there.
    I called out and Marcus said everything was fine. I did not check
    on Jaylen at that time."
```

This describes an event on the evening of June 11, but it's recorded in a June 13 interview. The extraction tool must distinguish between *when the event happened* (June 11, 9:30 PM) and *when it was reported* (June 13, 4:00 PM).

**Extracted to SQL:**

```sql
-- The event itself (what happened on June 11):
('2024-DR-42-0892', '2024-06-11', '9:30 PM', 'Family',
 'Dena Holloway hears a loud thump from Jaylen''s room. She calls out and Marcus
  Webb responds that everything is fine. Dena does not check on Jaylen.
  (Disclosed in revised statement to Lt. Odom on June 13.)',
 'Sheriff Report #24-06-4418, pp. 6-7', 'Dena Holloway, Marcus Webb, Jaylen Webb'),

-- The interview where it was disclosed (also a timeline event):
('2024-DR-42-0892', '2024-06-13', '4:00 PM', 'Law Enforcement',
 'Lt. Odom interviews Dena Holloway at Spartanburg County Sheriff office. Dena
  changes account — now states Marcus was in the child room earlier in the evening
  and she heard a loud thump around 9:30 PM but did not check immediately.',
 'Sheriff Report #24-06-4418, pp. 6-8', 'Lt. Frank Odom, Dena Holloway'),
```

**Extraction method:** This is the hardest pattern. The extraction model must:
1. Recognize the quoted text is a statement about a past event
2. Extract the event date (June 11) from the context, not the interview date (June 13)
3. Create two timeline entries — one for the event, one for the disclosure
4. Link them via the description text

---

### 3d. `statements` Table — Extracted from Quoted Text with Attribution

Statements are direct or near-direct quotes from case participants, always attributed to a specific person and audience.

**Source: Medical_Records.pdf, p. 8 (Nursing Notes)**

```
Author: Rebecca Torres, RN, BSN

Parent Interview — Father (Marcus Webb): During intake history,
Mr. Webb provided the following account of events:

    "I put him to bed around ten. He was fine, running around all day.
    I fell asleep on the couch watching TV. Next thing I know, Dena is
    shaking me saying something is wrong with Jaylen."
```

**Source: Court_Orders_and_Filings.pdf (Case 2), p. 12 (Ninety-Day Review)**

```
7. Respondent Crystal Price addressed the Court and stated: "I have
   been trying to get to the IOP sessions but I don't have reliable
   transportation. I missed some appointments. I am looking for housing
   but it is hard without income. I am clean now." (Court Transcript, p. 12.)
```

**Extracted to SQL:**

```sql
-- Medical Records p. 8 — nursing notes interview:
INSERT INTO statements
  (case_id, person_id, statement_date, made_to, statement_text,
   source_document, page_reference)
VALUES
('2024-DR-42-0892',
 1,                    -- person_id for Marcus Webb (resolved via people table)
 '2024-06-12',         -- date from nursing note header
 'Medical Staff',      -- "Parent Interview" section = statement to medical staff
 'I put him to bed around ten. He was fine, running around all day. I fell asleep
  on the couch watching TV. Next thing I know, Dena is shaking me saying something
  is wrong with Jaylen.',
 'Medical Records, Nursing Notes',
 'p. 8'),

-- Court Orders, Ninety-Day Review, Finding 7:
('2024-DR-15-0341',
 9,                    -- person_id for Crystal Price
 '2023-11-14',         -- hearing date from order header
 'Court',              -- "addressed the Court" = statement to court
 'I have been trying to get to the IOP sessions but I don''t have reliable
  transportation. I missed some appointments. I am looking for housing but it is
  hard without income. I am clean now.',
 'Court Transcript, 90-Day Review',
 'p. 12'),
```

**Extraction method:** Statements follow predictable patterns:
- **Block quotes** (indented or in quotation marks) — extract the quoted text
- **Attribution phrases** ("Mr. Webb stated:", "Respondent addressed the Court and stated:") — extract the speaker and audience
- **Context headers** ("Parent Interview — Father", "Interview of Dena Holloway") — classify the `made_to` field
- **Page/paragraph references** — some documents include explicit page citations (Court Transcripts), while others require tracking the page from the document layout

The `person_id` foreign key requires resolving the speaker name against the `people` table. This is a join operation during loading, not during extraction.

---

### 3e. `discrepancies` Table — The Hardest Extraction Target

Discrepancies require the extraction tool to compare facts across multiple documents or sections and identify conflicts. This is where AI-assisted extraction earns its value — a human analyst or an LLM compares two accounts and flags the contradiction.

**Source: Medical_Records.pdf, pp. 3-4 vs. Sheriff_Report_24-06-4418.pdf, p. 2**

Document 1 (Medical Records, Radiology Report):
```
Right Femur: Transverse fracture of the right femoral shaft...
Left Humerus: Spiral (oblique) fracture of the left humeral shaft...
Skeletal Survey — Remainder: ... No fractures identified ...
```

Document 2 (Sheriff Report, Background):
```
Radiology report indicated no fractures detected on skeletal survey.
```

These two statements directly conflict. The Medical Records show two fractures; the Sheriff Report says none detected. The conflict arises because the Sheriff Report paraphrased the "remainder" finding (no *additional* fractures) as "no fractures detected" (no fractures at all).

**Extracted to SQL:**

```sql
INSERT INTO discrepancies
  (case_id, topic, person_a_id, person_a_account, person_b_id, person_b_account,
   contradicted_by, source_document)
VALUES
('2024-DR-42-0892',
 'Skeletal survey fracture findings',  -- topic: what the discrepancy is about
 NULL,                                 -- not a person-vs-person conflict
 'Sheriff Report states: "Radiology report indicated no fractures detected on
  skeletal survey."',                  -- account A: what one source says
 NULL,
 'Medical Records radiology report documents two fractures: transverse fracture
  of right femoral shaft (3-5 days old) and spiral fracture of left humeral shaft
  (24-48 hours old). Remainder of skeletal survey found no additional fractures.',
 'Sheriff Report likely paraphrased the "no additional fractures" finding as
  "no fractures detected," omitting the two known fractures. Medical Records
  pp. 3-4 are the primary radiological source.',
 'Sheriff Report #24-06-4418, p. 2; Medical Records, pp. 3-4');
```

**Extraction method:** Discrepancy extraction is a two-pass process:
1. **First pass (per-document):** Extract all factual claims with their sources
2. **Second pass (cross-document):** Compare claims on the same topic across documents. Flag contradictions.

This second pass is where an LLM adds the most value. A traditional extraction tool can pull the text; only a reasoning model can determine that "no fractures detected" and "transverse fracture of right femoral shaft" are contradictory claims about the same skeletal survey.

Person-vs-person discrepancies (e.g., Marcus says he wasn't in the room; Dena says he was) are easier to detect because the extraction tool can match statements by the same `topic` from different `person_id` values.

---

## 4. Extraction Challenges Specific to Legal Documents

### 4a. Same fact, different precision across documents

Drug test results appear in four documents at three levels of detail:

| Source | Text | Precision |
|---|---|---|
| Court Orders (Ninety-Day Review) | "two positive drug screens for fentanyl in October 2023" | Month only |
| DSS Investigation Report, p. 6 | "two positive drug screens for fentanyl, dated October 8 and October 22, 2023" | Exact dates |
| TPR Petition, p. 4 | "Respondent tested positive for fentanyl on October 8, 2023 and October 22, 2023" | Exact dates |
| TPR Affidavit, p. 5 | "missed screens are treated as presumptive positive results" | Policy rule |

**Rule:** Always extract from the most specific source. Deduplicate across documents by matching event dates. Attach all source citations to the single timeline event.

### 4b. Reported events vs. reporting events

A June 13 interview may describe events from June 11. The extraction tool must create timeline events for *both*:
- **June 11, 9:30 PM** — the thump Dena heard (the event)
- **June 13, 4:00 PM** — Dena's revised statement to Lt. Odom (the disclosure)

Without this distinction, timeline queries return events in the wrong order or miss critical gaps.

### 4c. Attributed statements vs. paraphrased narrative

Legal documents contain two types of speech:
- **Direct quotes** ("I put him to bed around ten.") — extract as `statements` rows
- **Investigator paraphrase** ("Subject stated that he put him to bed at approximately 8:00 PM") — extract as `timeline_events` description text

These can conflict. Marcus's direct quote says "around ten" (Medical Records p. 8). The investigator's paraphrase says "approximately 8:00 PM" (Sheriff Report p. 3). Both are in the documents. The extraction pipeline must decide which to use as the canonical time, or flag the conflict.

### 4d. People appearing across cases with different roles

The name "Rebecca Torres" appears in two cases with two different roles:
- **Case 1:** Rebecca Torres, RN, BSN — Emergency Department nurse (Medical Records p. 8)
- **Case 2:** Rebecca Torres, Esq. — DSS Staff Attorney (TPR Petition, signature block)

The extraction tool must not merge these into one person. The `case_id` foreign key prevents cross-case collisions in SQL, but the deduplication logic needs case-scoped matching, not global name matching.

### 4e. Nested documents

The TPR Petition contains a full Affidavit as an embedded document (separate pagination, separate signature block). Court Orders contain quoted testimony from transcripts. The extraction tool must handle documents-within-documents and track which sub-document a fact came from for accurate `source_document` and `page_reference` values.

---

## 5. What This Means for the Demo

The data extraction pipeline is the bridge between what agencies have (filing cabinets full of PDFs) and what an AI agent needs (queryable structured data). The key demo talking points:

1. **PDFs are the starting point, not the end state.** Every state agency stores legal documents as PDFs. The question is whether you query them directly (Copilot Studio + SharePoint) or extract the structured data first (MCP + SQL).

2. **Extraction is a one-time cost per document, not per query.** Once the data is in SQL, every subsequent query is fast, precise, and deterministic. Document-backed agents re-process the PDF on every question.

3. **The hard part isn't extraction — it's conflict resolution.** Pulling dates and names from PDFs is solved. Deciding that the Sheriff Report's "no fractures" contradicts the Medical Records' "two fractures" requires reasoning, not just parsing.

4. **Human review remains essential.** The extraction pipeline produces draft structured data. An analyst reviews it before it enters the production database. This is where the 8:00 PM vs. 10:00 PM bedtime discrepancy gets caught and flagged.

5. **The structured data advantage compounds.** Aggregate queries ("Which cases involve TPR?"), cross-case analysis, and arithmetic reasoning are only possible with structured data. No amount of PDF chunking enables "find all 9 TPR cases across 50 cases."
