# MCP Agent vs. SharePoint Agent -- Demo Comparison Prompts

**Demo for:** SC DSS General Counsel
**Goal:** Show that MCP-backed agents deliver more precise, reliable answers for structured legal case data than SharePoint-grounded agents searching through narrative documents.

**Two agents being compared:**

| | MCP Agent | SharePoint Agent |
|---|---|---|
| **Data source** | Structured SQL database via MCP tools | Unstructured documents uploaded to SharePoint |
| **Query method** | SQL queries with filters, joins, aggregations | Keyword/semantic search over narrative text |
| **Strength** | Precision, completeness, cross-referencing | Natural language summaries of document content |
| **Weakness** | Requires structured data model | Cannot filter, count, or cross-reference reliably |

**Available demo cases:**
- **Case 1:** `2024-DR-42-0892` -- DSS v. Webb & Holloway, CPS Emergency Removal (Spartanburg, Seventh Judicial Circuit). Child abuse, conflicting parent accounts, medical evidence of non-accidental injuries.
- **Case 2:** `2024-DR-15-0341` -- DSS v. Price, Termination of Parental Rights (Richland, Fifth Judicial Circuit). Neglect, substance abuse, failed treatment plan compliance.
- **Cases 3-50:** Procedurally generated across all 16 SC judicial circuits and 46 counties for volume/aggregate queries.

---

## 1. Factual Retrieval (Timeline, Dates, Names)

Prompts where MCP excels because it can query exact dates, event types, and people from structured tables.

---

**Prompt 1.1:** "What is the complete timeline of events for case 2024-DR-42-0892?"

- **MCP agent returns:** All 12 timeline events in chronological order with exact dates, times, event types, descriptions, source documents, and parties involved. Formatted as a clean table or ordered list. Nothing missing.
- **SharePoint agent returns:** A narrative summary pieced together from searching multiple documents. Likely misses events or gets dates wrong because the information is scattered across dictation PDFs, medical records, sheriff reports, and court filings.
- **Why MCP wins:** The timeline_events table is purpose-built for this query. One SQL call returns every event, in order, with zero ambiguity. SharePoint has to find and reconcile information across multiple documents with no guarantee of completeness.

---

**Prompt 1.2:** "When was Jaylen Webb admitted to the hospital and what injuries were found?"

- **MCP agent returns:** Admitted June 12, 2024 at 3:15 AM to Spartanburg Medical Center ER. X-rays revealed bilateral femur fracture (right) and spiral fracture of left humerus. Dr. Chowdhury assessed injuries as inconsistent with reported mechanism (fall from crib) and noted injuries at different stages of healing. Source: Medical Records, pp. 1-4.
- **SharePoint agent returns:** Probably finds the admission date and injuries but may miss the detail about different healing stages or the specific time of admission. Could conflate the initial ER admission with Dr. Chowdhury's later mandatory report at 7:30 AM.
- **Why MCP wins:** The structured data separates each event with its own timestamp, description, and source. No risk of conflating two events or missing a detail buried in a paragraph.

---

**Prompt 1.3:** "List all people involved in the Price TPR case and their roles."

- **MCP agent returns:** Complete list of 8 people with full names, roles, relationships, and notes: Crystal Price (parent/mother), Brandon Price (parent/father, incarcerated, rights relinquished), Amari Price (child, age 7), Destiny Price (child, age 5), Monica Vance (case manager), Dr. Raymond Ellis (substance abuse evaluator), Sandra Patterson (foster parent, pre-adoptive), Thomas Reed (GAL).
- **SharePoint agent returns:** Likely identifies the main parties (Crystal, the children) but may miss supporting figures like Dr. Ellis or Thomas Reed. Roles and relationships may be vague because they are mentioned in passing within documents rather than explicitly listed.
- **Why MCP wins:** The people table is a definitive roster. Every person, every role, every relationship -- no hunting through documents.

---

**Prompt 1.4:** "What court hearings have occurred in the Webb case and what were the outcomes?"

- **MCP agent returns:** Three court events, filtered by event_type = 'Court': (1) June 14, 2024 -- ex parte emergency removal order granted by Judge Easley; (2) June 18, 2024 -- probable cause hearing, court finds probable cause, Karen Milford appointed GAL; (3) July 18, 2024 -- 30-day review, case plan approved with parenting classes, psych evals, and supervised visitation, next hearing September 12.
- **SharePoint agent returns:** May identify the hearings but could confuse dates or mix up which outcomes go with which hearing. Court filings are separate documents and the agent has to correlate them.
- **Why MCP wins:** Filtering by event_type gives exact results with no noise. Each hearing is a discrete record with its outcome attached.

---

## 2. Cross-Referencing Statements

Prompts that require comparing what different people said to different audiences at different times.

---

**Prompt 2.1:** "What did Marcus Webb tell medical staff vs. what he told law enforcement about the night Jaylen was injured?"

- **MCP agent returns:** Side-by-side comparison. To medical staff (June 12): "I put him to bed around ten. He was fine, running around all day. I fell asleep on the couch watching TV. Next thing I know, Dena is shaking me saying something is wrong with Jaylen." To law enforcement (June 13): "I was on the couch all night. I did not go into Jaylen's room after I put him down. I don't know how he got hurt. Maybe he climbed out of the crib and fell. He's been trying to climb out lately." Key difference: The crib-climbing explanation only appears in the law enforcement statement, not the hospital statement.
- **SharePoint agent returns:** May summarize Marcus's statements generally but is unlikely to present them side by side with the precise wording differences. Could miss the detail that the crib-climbing theory was introduced only after the initial hospital statement.
- **Why MCP wins:** Statements are stored per-person, per-date, per-audience. The agent can pull Marcus's statements, filter by `made_to`, and present exact quotes for comparison.

---

**Prompt 2.2:** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

- **MCP agent returns:** Hospital statement (June 12, to medical staff): "I heard him crying around 2 AM. I went in and he couldn't move his leg. I think he fell out of his crib. Marcus put him to bed, I was in the bedroom." Sheriff interview (June 13, to law enforcement): "Around 9:30 PM I heard a loud thump from Jaylen's room. I assumed Marcus was in there. I called out and Marcus said everything was fine. I did not check on Jaylen at that time." Also added: "Marcus has a temper. He gets frustrated when Jaylen won't stop crying. I have seen him grab Jaylen roughly by the arm before, maybe two or three times." Changes: (1) Added the 9:30 PM thump she never mentioned at the hospital, (2) placed Marcus in/near the child's room, (3) disclosed a history of rough handling.
- **SharePoint agent returns:** Might note that Dena's story changed but probably will not itemize the three specific additions or provide the exact wording from each statement.
- **Why MCP wins:** The discrepancies table explicitly captures this (discrepancy #6: "Dena Holloway initial vs. revised account"), and the statements table has both versions verbatim with source references.

---

**Prompt 2.3:** "What has Crystal Price said about her sobriety at each court hearing? How do those statements compare to her drug test results?"

- **MCP agent returns:** Three statements to court: (1) Aug 15, 2023 -- "I know I need to get help. I will do everything the court asks." (2) Nov 14, 2023 -- "I am clean now." (3) Apr 22, 2024 -- "I have been going to my IOP sessions... I am trying." Drug test results per case manager: Two positive screens for fentanyl in October 2023 (between hearings 1 and 2), missed screens in December, January, and March, and one negative screen on April 10, 2024. The claim of being "clean now" at the November hearing came one month after two positive fentanyl results.
- **SharePoint agent returns:** Might find some of Crystal's statements but is unlikely to cross-reference the drug test timeline against her court testimony. The contradiction between "I am clean now" and the October fentanyl results requires connecting information from different documents.
- **Why MCP wins:** The agent can query Crystal's statements filtered by `made_to = 'Court'`, then pull the discrepancy record on "Drug use and sobriety" which documents the contradiction with lab results and missed screens.

---

## 3. Discrepancy Identification

Prompts that test the agent's ability to find contradictions in the case record.

---

**Prompt 3.1:** "What are the key discrepancies between Marcus Webb's and Dena Holloway's accounts?"

- **MCP agent returns:** All 6 discrepancies from the discrepancies table: (1) Cause of injuries -- crib fall vs. thump at 9:30 PM; (2) Marcus's presence in child's room -- denies being there vs. Dena places him there; (3) Timing of injury discovery -- 4.5-hour gap between thump and hospital; (4) History of rough handling -- Marcus denies it, Dena describes 2-3 prior incidents; (5) Single vs. multiple injury events -- both imply one night, but medical evidence shows days apart; (6) Dena's own changed story. Each includes what person A said, what person B said, what contradicts both, and the source documents.
- **SharePoint agent returns:** Likely identifies the main contradiction (crib fall vs. thump) but probably misses the nuances -- the timeline gap, the rough handling history, and especially the medical evidence that injuries occurred days apart (contradicting both parents, not just one).
- **Why MCP wins:** Discrepancies are pre-analyzed and stored as structured records. The MCP agent returns all six with full context. SharePoint has to piece together contradictions by reading across multiple documents -- exactly the kind of analysis where things get missed.

---

**Prompt 3.2:** "Are there any contradictions in Crystal Price's statements about her compliance with the treatment plan?"

- **MCP agent returns:** Yes. Crystal claims she has been trying but lacks transportation and support. Case manager Monica Vance documents that DSS provided bus passes monthly, three housing referrals, and offered IOP transportation assistance which Crystal declined. After 8 months, Crystal had completed only 5 of 12 IOP sessions and 2 of 8 parenting classes. Source: discrepancy record on "Compliance with treatment plan."
- **SharePoint agent returns:** May note that Crystal says she is trying and that her progress is slow, but is unlikely to surface the specific detail that transportation assistance was offered and declined -- which directly contradicts Crystal's stated reason for non-compliance.
- **Why MCP wins:** The discrepancy record captures both sides and the contradicting evidence in one structured record. SharePoint would need to find Crystal's statement in one document and the DSS records about bus passes and declined assistance in another.

---

**Prompt 3.3:** "What evidence contradicts the parents' claim that Jaylen fell from his crib?"

- **MCP agent returns:** Dr. Chowdhury's medical assessment: (1) Fracture pattern inconsistent with a fall from standard crib height; (2) spiral fracture of left humerus indicates torsional force, not impact; (3) femur fracture is approximately 24-48 hours older than the humerus fracture, indicating two separate injury events occurring days apart. A single crib fall cannot cause injuries at different healing stages. Source: Medical Records p. 5, Court Transcript p. 14.
- **SharePoint agent returns:** Probably finds that the doctor said the injuries were non-accidental, but may not articulate all three specific reasons or cite the exact page references.
- **Why MCP wins:** The medical statements and discrepancy records contain the exact medical reasoning with source citations. No ambiguity, no paraphrasing.

---

## 4. Filtering and Precision

Prompts that require structured data filtering -- where MCP can apply SQL WHERE clauses and SharePoint cannot.

---

**Prompt 4.1:** "Show me only the medical events in the Webb case timeline."

- **MCP agent returns:** Exactly 3 events filtered by event_type = 'Medical': (1) June 12, 2:00 AM -- Dena finds Jaylen crying, drives to ER; (2) June 12, 3:15 AM -- ER admission, x-rays reveal fractures; (3) June 12, 7:30 AM -- Dr. Chowdhury files mandatory abuse report. No court events, no law enforcement events, no placement events -- just medical.
- **SharePoint agent returns:** Probably returns a mix of medical and non-medical events because it cannot cleanly filter by event type. May include court testimony about medical evidence, blurring the line between medical events and legal proceedings.
- **Why MCP wins:** SQL filtering by event_type is deterministic. SharePoint search is semantic -- it will match anything that mentions medical topics, including non-medical events that reference medical evidence.

---

**Prompt 4.2:** "What statements were made to law enforcement in case 2024-DR-42-0892?"

- **MCP agent returns:** Exactly 4 statements filtered by made_to = 'Law Enforcement': Marcus Webb (2 statements on June 13), Dena Holloway (2 statements on June 13). Each with exact text, source document, and page reference.
- **SharePoint agent returns:** May find statements from the sheriff report but could also surface case manager notes that mention law enforcement, or court testimony that references what was said to law enforcement -- mixing primary statements with secondhand references.
- **Why MCP wins:** The `made_to` field allows precise filtering. SharePoint cannot distinguish between a statement *made to* law enforcement and a statement *about* law enforcement.

---

**Prompt 4.3:** "List all court orders for the Price case in chronological order."

- **MCP agent returns:** 5 court events in order: (1) Aug 8, 2023 -- emergency removal order; (2) Aug 15 -- probable cause, treatment plan ordered; (3) Nov 14 -- 90-day review, plan continued with warning; (4) Nov 20 -- Brandon Price voluntary relinquishment; (5) Feb 8, 2024 -- TPR petition filed; (6) Apr 22 -- TPR probable cause, merits hearing scheduled for July 15.
- **SharePoint agent returns:** Likely finds the major orders but may get the chronology wrong or miss the Brandon Price relinquishment, which is a separate filing.
- **Why MCP wins:** Timeline events filtered by case_id and event_type = 'Court' returns a clean, ordered list. No risk of missing a filing or getting the sequence wrong.

---

## 5. Multi-Case / Aggregate Queries

Prompts where MCP has access to all 50 cases in the database. SharePoint only has documents for the cases that were uploaded.

---

**Prompt 5.1:** "How many active cases does DSS currently have?"

- **MCP agent returns:** Exact count from `SELECT COUNT(*) FROM cases WHERE status = 'Active'`. Returns a number.
- **SharePoint agent returns:** Cannot count. May say "I found several active cases" or attempt to list ones it finds in documents, but has no way to guarantee completeness.
- **Why MCP wins:** Aggregate queries are SQL's bread and butter. SharePoint was not designed for counting or aggregation.

---

**Prompt 5.2:** "List all cases in the Seventh Judicial Circuit."

- **MCP agent returns:** Filtered list of all cases where circuit = 'Seventh Judicial Circuit', including case IDs, titles, types, counties, and statuses.
- **SharePoint agent returns:** May find some cases that mention "Seventh Judicial Circuit" in their text, but will miss cases where the circuit is only mentioned in metadata or filing headers.
- **Why MCP wins:** Circuit is a structured field. The query is deterministic and complete.

---

**Prompt 5.3:** "Which cases involve Termination of Parental Rights?"

- **MCP agent returns:** All cases where case_type = 'Termination of Parental Rights'. Exact list with case details.
- **SharePoint agent returns:** Finds cases that mention TPR in their documents, but may also surface CPS cases that discuss TPR as a possible outcome -- false positives.
- **Why MCP wins:** Filtering by case_type is exact. SharePoint search cannot distinguish between a case *that is* a TPR and a case *that mentions* TPR.

---

**Prompt 5.4:** "Are there any cases in Richland County besides the Price case?"

- **MCP agent returns:** Query `WHERE county = 'Richland' AND case_id != '2024-DR-15-0341'`. Returns exact list or confirms none exist.
- **SharePoint agent returns:** May find other Richland County cases if their documents mention the county, but cannot confirm completeness -- there is no way to know if it found all of them.
- **Why MCP wins:** The database is the single source of truth. The agent can give a definitive yes/no with a complete list. SharePoint can only say "I found these" without guaranteeing it found everything.

---

## 6. Precision Stress Tests

Detail-oriented prompts that push both agents to their limits. These are the "wow" moments in the demo.

---

**Prompt 6.1:** "What page of the medical records contains Dr. Chowdhury's assessment that the injuries occurred at different times?"

- **MCP agent returns:** Medical Records, page 5. Dr. Chowdhury's statement: "radiographic findings suggest the femur fracture is approximately 24-48 hours older than the humerus fracture, indicating two separate injury events." Also referenced in Court Transcript, Probable Cause Hearing, page 14.
- **SharePoint agent returns:** Might find the content of the assessment but is unlikely to return the specific page number. SharePoint document search does not track page-level references reliably.
- **Why MCP wins:** The source_document and page_reference fields in the statements table store this metadata explicitly. The agent does not have to search for it -- it is part of the structured record.

---

**Prompt 6.2:** "How many IOP sessions had Crystal Price completed as of the November 2023 review vs. the April 2024 hearing?"

- **MCP agent returns:** November 14, 2023: 3 of 12 sessions completed. April 22, 2024: 5 of 12 sessions completed. Net progress over 5 months: 2 additional sessions. Sources: Court Filing Order 2 and Court Filing Order 3.
- **SharePoint agent returns:** Might find one or both numbers but is unlikely to present them side by side with the exact comparison. If the numbers appear in different documents, the agent may not connect them.
- **Why MCP wins:** The timeline events for each court hearing contain the exact compliance numbers. The MCP agent can pull both events and compare directly. This kind of point-in-time comparison across multiple records is where structured data shines.

---

**Prompt 6.3:** "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

- **MCP agent returns:** Dena reports hearing the thump at approximately 9:30 PM on June 11. Jaylen was found crying at 2:00 AM on June 12 and admitted to the ER at 3:15 AM. Time from thump to discovery: approximately 4.5 hours. Time from thump to ER admission: approximately 5 hours and 45 minutes. Medical staff noted this delay as concerning.
- **SharePoint agent returns:** May reference the delay generally but is unlikely to calculate the exact time gaps or distinguish between when the child was found crying vs. when they arrived at the ER.
- **Why MCP wins:** The timeline has exact times for each event. The agent can calculate intervals precisely. SharePoint would need to find times scattered across narrative text and do mental math -- unreliable at best.

---

## Demo Tips

1. **Run prompts on both agents side by side.** The contrast is the whole point. Ask the same question to both and let the audience see the difference in precision.

2. **Start with Section 1** (factual retrieval) to establish that MCP returns complete, structured data. Then move to Section 3 (discrepancies) for the "wow" moment.

3. **Save Section 5** (multi-case queries) for the scalability argument. "This works across 50 cases. Imagine 5,000."

4. **End with Section 6** (stress tests) to drive home the precision point. Page numbers and session counts are the kind of details attorneys care about.

5. **Do not bash SharePoint.** The message is not "SharePoint is bad" -- it is "different tools for different jobs." SharePoint is great for searching through unstructured narratives, policy documents, and memos. But when case data is structured, MCP gives you precision that document search cannot match.

6. **The punchline:** "Would you rather have your attorneys search through PDFs, or query a database that already has the answers organized?"
