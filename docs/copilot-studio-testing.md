# Copilot Studio Testing — Response Comparison

## Overview

Multiple agent configurations are tested against the same prompts to compare accuracy, citation quality, and cross-document reasoning. Agents use either the MCP server (`POST /mcp`) backed by structured SQL data, Copilot Studio Knowledge (documents uploaded directly to the agent), or Copilot Studio connected to a SharePoint document library.

### Agent Matrix

| Agent Name | Backend | Model | Status |
|---|---|---|---|
| DSS Legal (Web) | /chat endpoint → MCP/SQL | GPT-4.1 | Active |
| DSS Legal (MCP) - Com | Copilot Studio → MCP/SQL | GPT-4.1 | Active |
| DSS Legal (MCP) - GCC | Copilot Studio → MCP/SQL | GPT-4o | Active |
| DSS Legal (SP/PDF) - Com | Copilot Studio → SharePoint PDFs | GPT-4.1 | Active |
| DSS Legal (SP/DOCX) - Com | Copilot Studio → SharePoint DOCXs | GPT-4.1 | Active |
| DSS Legal (KB/DOCX) - Com | Copilot Studio → Uploaded DOCXs | GPT-4.1 | Active |
| DSS Legal (KB/PDF) - Com | Copilot Studio → Uploaded PDFs | GPT-4.1 | Active |
| DSS Legal (SP/PDF) - GCC | Copilot Studio → SharePoint PDFs | GPT-4o | Pending GCC config |
| DSS Legal (SP/DOCX) - GCC | Copilot Studio → SharePoint DOCXs | GPT-4o | Active |
| DSS Legal (KB/PDF) - GCC | Copilot Studio → Uploaded PDFs | GPT-4o | Active |
| DSS Legal (KB/DOCX) - GCC | Copilot Studio → Uploaded DOCXs | GPT-4o | Active |

**Model constraint:** GCC Copilot Studio is locked to GPT-4o; Commercial Copilot Studio uses GPT-4.1. Neither can be changed.

**Knowledge (KB) agent file naming:** Copilot Studio Knowledge uploads are flat (no folder structure). Source PDFs and DOCXs were copied and renamed with the case number appended to the filename (e.g., `DSS_Investigation_Report - dr-42-0892.docx`) to disambiguate documents across cases.

> **Note on markdown (.md) files:** Markdown files were tested in Rounds 1-2 but dropped from Round 3 onward. SharePoint-connected .md files returned no results at all ("no information found"). Directly uploaded .md files performed inconsistently — found unique details on simple retrieval (the admitting nurse Rebecca Torres) but missed critical content on cross-document reasoning. Neither format reflects real-world legal document storage; organizations store legal documents as PDF or DOCX. Round 1-2 .md results are preserved below for historical reference.

### Test Prompts

| # | Prompt | Case | Key Challenge |
|---|---|---|---|
| 1 | "Tell me about Jaylen Webb's emergency room admission — specifically the time and the admitting nurse." | 2024-DR-42-0892 | Simple fact extraction + detail only in documents (nurse) |
| 2 | "What did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement?" | 2024-DR-42-0892 | Cross-document reasoning + consistency analysis |
| 3 | "Crystal Price told the court she was 'clean now' at the November 2023 hearing. What do the drug test results show?" | 2024-DR-15-0341 | Contradiction detection + compliance synthesis |
| 3.2 | "Crystal Price said she couldn't comply with the treatment plan because she lacked transportation. What support did DSS actually provide?" | 2024-DR-15-0341 | Contradiction detection — claim vs. DSS records |
| 4 | "Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey?" | 2024-DR-42-0892 | Cross-document conflict — Sheriff Report contradicts Medical Records |
| 5 | "What is the complete timeline of events for case 2024-DR-42-0892?" | 2024-DR-42-0892 | Full timeline enumeration (12 events) |
| 6 | "List all people involved in the Price TPR case and their roles." | 2024-DR-15-0341 | People roster completeness (8 people) |
| 7 | "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?" | 2024-DR-42-0892 | Statement evolution / change detection |
| 8 | "What statements were made to law enforcement in case 2024-DR-42-0892?" | 2024-DR-42-0892 | Filtering precision (4 LE statements, no false positives) |
| 9 | "Which cases involve Termination of Parental Rights?" | All cases | Aggregate query (9 TPR cases — doc agents can't answer) |
| 10 | "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?" | 2024-DR-42-0892 | Arithmetic from structured data (5h45m) |

---

## Ground Truth

### Prompt 1: ER Admission Time and Nurse

The answer spans two data sources:

- **From SQL** (`timeline_events`): Jaylen Webb admitted at **3:15 AM** on June 12, 2024. Dr. Anita Chowdhury is the physician. Source: `Medical Records, pp. 1-4`. No nurse is stored.
- **From documents** — two different nurses appear across the case files:
  - **Rebecca Torres, RN, BSN** — in `Medical_Records`, authored multiple nursing notes in the Emergency Department
  - **Patricia Daniels, RN** (Charge Nurse, Employee ID: SMC-4492) — in `Sheriff_Report_24-06-4418`, the ER nurse interviewed by law enforcement
- **Time discrepancy in source documents**: The Sheriff Report states the child arrived at **0047 hours** (12:47 AM), while the Medical Records timeline says **3:15 AM**. This is an inconsistency in the synthetic data itself.
- Neither nurse was modeled into the SQL schema.

Neither source alone has the complete answer.

### Prompt 2: Marcus Webb's Statements (Cross-Document)

Marcus Webb made two statements:

- **To hospital staff** (Medical Records, Nursing Notes, p. 8, June 12, 2024): Said he put Jaylen to bed "around ten," Jaylen was fine and running around all day, Marcus fell asleep on the couch watching TV, and was woken by Dena saying something was wrong.
- **To law enforcement** (Sheriff Report #24-06-4418, pp. 4-5, June 13, 2024): Said he was on the couch all night, did not go into Jaylen's room after putting him down, suggested Jaylen may have climbed out of the crib and fell. Denied being in the room despite Dena's claim that he was.

The accounts are **substantially consistent** on the bedtime (~10 PM) and couch story, but the law enforcement statement adds defensive details (denying being in the room, contradicting Dena).

**Common misattribution trap:** Dena Holloway told police that "Marcus Webb put the child to bed at approximately 8:00 PM" (Sheriff Report line 108). This is Dena's statement about Marcus, not Marcus's own words. Marcus consistently said "around ten" (hospital) and "after 10 PM" (law enforcement). Multiple document-backed agents have incorrectly attributed the 8:00 PM time to Marcus.

### Prompt 3: Crystal Price "Clean Now" (Drug Tests)

- **From SQL** (`timeline_events`): "Two positive drug screens (fentanyl) in October" + "3 of 12 IOP sessions" — no specific test dates, no missed screen dates
- **From SQL** (`statements`):
  - Crystal Price (person_id 9): "I have been trying to get to the IOP sessions but I don't have reliable transportation. I missed some appointments. I am looking for housing but it is hard without income. I am clean now." (Court Transcript, 90-Day Review, p. 12)
  - Monica Vance (person_id 13): "Ms. Price has attended only 3 of 12 required IOP sessions. She has not enrolled in parenting classes as ordered. She has had two positive drug screens for fentanyl in October. She does not have stable housing — she reports staying with various friends. I have attempted six home visits and reached her twice." (Court Transcript, 90-Day Review, p. 8)
- **From documents** (additional detail not in SQL):
  - Specific positive test dates: **October 8** and **October 22, 2023** (DSS Investigation Report, TPR Petition)
  - Missed screen dates: **December 5, 2023; January 15, 2024; March 3, 2024** (DSS Investigation Report, TPR Petition)
  - Missed screens = **presumptive positive** per DSS policy and court order (TPR Petition)
  - Court explicitly noted "clean now" claim was "contradicted by the two positive fentanyl screens in October 2023, approximately three weeks prior to this hearing" (Court Orders)

### Prompt 3.2: Crystal Price Transportation Barrier

- **From SQL** (`discrepancies` table, topic "Compliance with treatment plan"): Crystal claims she lacks transportation and support. DSS records show bus passes issued monthly, three housing referrals provided, and IOP transportation assistance offered but declined. Despite supports, Crystal completed only 5/12 IOP sessions and 2/8 parenting classes in 8 months.

### Prompt 4: Skeletal Survey Fractures (Cross-Document Conflict)

The answer requires cross-referencing two documents that directly contradict each other:

- **Sheriff Report (p. 2):** "Radiology report indicated no fractures detected on skeletal survey" — this is misleading
- **Medical Records (pp. 3-4):** Skeletal survey found a transverse right femur fracture (3-5 days old) and spiral left humerus fracture (24-48 hours old). The **remainder** of the skeletal survey found no additional fractures beyond those two.
- The Sheriff's "no fractures detected" likely refers to the remainder (no additional fractures), but the wording implies a clean skeletal survey.
- **"Skeletal survey" is NOT in the SQL schema.** MCP agents cannot surface this conflict — it exists only in the source documents.

---

## Round 1 — Initial Five-Agent Comparison (2026-03-05)

### Agents Tested

| Agent | Backend | Model |
|---|---|---|
| DSS Legal (MCP) - GCC | MCP tool (structured SQL) | GPT-4o |
| DSS Legal (MCP) - Com | MCP tool (structured SQL) | GPT-4.1 |
| DSS Legal (Web) | `/chat` endpoint (structured SQL) | GPT-4.1 |
| DSS Legal (KB/.md) - Com *(retired)* | Uploaded .md documents | GPT-4.1 |
| DSS Legal (SP/.md) - Com *(retired)* | SharePoint library with .md files | GPT-4.1 |

### Prompt 1 Responses

#### DSS Legal (MCP) - GCC

> Jaylen Webb was brought to the emergency room at 2:00 AM on June 12, 2024. The admitting nurse's name is not specified in the available documents. The timeline and events related to the case can be found in the source documents: Dictation PDF, p. 4, and Medical Records, pp. 1-4.

#### DSS Legal (MCP) - Com

> **Jaylen Webb Emergency Room Admission Details**
>
> Admission Time: Jaylen Webb was brought to the Spartanburg Medical Center emergency room at 3:15 AM on June 12, 2024. X-rays at admission revealed multiple fractures inconsistent with the reported mechanism of injury (Medical Records, pp. 1-4).
>
> Admitting Nurse: The available medical timeline and statements do not identify the admitting nurse by name. The medical records reference Dr. Anita Chowdhury as the attending physician, but no nurse is listed in the documented events (Medical Records, pp. 1-4).
>
> If you need further details or wish to search for a specific nurse's name in other documents, please let me know.

#### DSS Legal (Web)

> Jaylen Webb was admitted to the Spartanburg Medical Center Emergency Room on June 12, 2024, at 3:15 AM. The medical timeline identifies Dr. Anita Chowdhury as the physician assessing Jaylen Webb; however, the available summary does not specifically identify the admitting nurse. The event is sourced from "Medical Records, pp. 1-4."
>
> If you require the name of the admitting nurse, additional review of the complete medical record would be necessary. Currently, no specific nurse is named in the available DSS or medical summaries.
>
> Source: Medical Records, pp. 1-4 (cited in Medical Event Timeline for 2024-DR-42-0892).

#### DSS Legal (KB/.md) - Com *(retired)*

> Jaylen Webb was brought to the emergency room and admitted at Spartanburg Medical Center. The admitting nurse was Rebecca Torres, RN, BSN.
>
> *1 reference: Medical_Records.md*

#### DSS Legal (SP/.md) - Com *(retired)*

> No information was found that could help answer this.
>
> I'm sorry, I'm not sure how to help with that. Can you try rephrasing?

### Round 1 Comparison Matrix

| Dimension | MCP - GCC | MCP - Com | Web | KB/.md - Com | SP/.md - Com |
|---|---|---|---|---|---|
| **Admission time** | 2:00 AM — WRONG | 3:15 AM ✅ | 3:15 AM ✅ | Not provided | No results |
| **Admitting nurse** | "Not specified" | "Not identified" | "Not identified" | **Rebecca Torres** ✅ | No results |
| **Source citation** | Dictation PDF p. 4 (fabricated) + Medical Records pp. 1-4 | Medical Records pp. 1-4 | Medical Records pp. 1-4 | Medical_Records.md | None |
| **Dr. Chowdhury mentioned** | No | Yes | Yes | No | No |
| **Overall accuracy** | Poor — hallucinated time and citation | Good (but incomplete) | Good (but incomplete) | Partial — found nurse, missed time | **Total failure** |

### Round 1 Analysis

#### GCC hallucinated the admission time

The MCP tool returns structured data with `event_time: "3:15 AM"`. GCC reported "2:00 AM" — a fabricated value. This suggests one of:

1. **Different model** — GCC Copilot Studio uses **GPT-4o** (the only available model); Commercial uses **GPT-4.1**. GPT-4o is less faithful at reproducing specific values from tool output. This is confirmed as the most likely cause — see Round 2 analysis.
2. **Tool call failure with fallback generation** — The MCP call may have failed silently, and the GCC orchestrator generated an answer from nothing (hallucinating with confidence)
3. **Context window or prompt differences** — GCC's Copilot Studio runtime may truncate or reformat tool results differently

#### GCC also fabricated a source citation

"Dictation PDF, p. 4" does not correspond to the ER admission event. The correct and only source is "Medical Records, pp. 1-4". This reinforces that GCC either didn't receive clean tool output or the model garbled it.

#### MCP - Com and Web are nearly identical

Both got the time right, both correctly noted the nurse isn't in the structured data, both cited Dr. Chowdhury as context, and both referenced the correct source. The only difference is presentation style. This makes sense — both hit the same MCP tools and the same SQL data. Quality depends on the orchestrating LLM, not the data layer.

#### Knowledge agent found what structured data missed

The document-backed agent correctly identified Rebecca Torres as the nurse — a detail that exists in the Medical Records but was never modeled into the SQL schema. However, it didn't return the admission time (3:15 AM), which is prominently in the same document. RAG retrieval likely chunked the document and surfaced the nursing notes section without the timeline section.

#### SharePoint .md returned nothing

The same markdown files that worked when uploaded as knowledge produced zero results when connected as a SharePoint document library. This is a Copilot Studio indexing/retrieval problem, not a data problem. The root cause is two completely different indexing pipelines — Copilot Studio owns the full pipeline for uploaded files (immediate chunking + embedding), while SharePoint depends on Microsoft Search's crawler which does not reliably extract content from .md files.

#### Neither approach alone gave a complete answer

| Fact | MCP agents | KB/.md (uploaded) | SP/.md |
|---|---|---|---|
| Admission time (3:15 AM) | 2 of 3 correct | Missed | No results |
| Admitting nurse (Rebecca Torres) | All 3 missed (not in SQL) | Correct | No results |
| Source citation | 2 of 3 correct | Correct | No results |

**Structured and unstructured approaches are complementary, not competing** — and how you connect unstructured data matters enormously.

### Demo Implications (Round 1)

1. **Structured data gives precision and consistency.** Three MCP-backed agents returned the same time from the same tool. The data is queryable, cross-referenceable, and fully cited.
2. **Unstructured documents preserve details that weren't modeled.** Rebecca Torres was a real detail in the medical records that the schema designers didn't think to capture.
3. **How you connect documents matters as much as having them.** The same files produced correct answers when uploaded as knowledge and zero answers from a SharePoint library.
4. **GCC's hallucination is the cautionary tale.** Even with structured data, the orchestrating LLM matters. GCC confidently stated "2:00 AM" — an attorney relying on this would have incorrect facts.
5. **The ideal system combines both.** MCP tools for structured queries plus document search for the long tail of details.

---

## Round 2 — Expanded Testing (2026-03-06)

### New Agents Tested

SharePoint was retested with **PDF** and **DOCX** files instead of markdown.

| Agent | Backend | Model |
|---|---|---|
| DSS Legal (SP/PDF) - GCC | SharePoint library with PDF files | GPT-4o |
| DSS Legal (SP/PDF) - Com | SharePoint library with PDF files | GPT-4.1 |
| DSS Legal (SP/DOCX) - Com | SharePoint library with DOCX files | GPT-4.1 |

### Prompt 1: ER Time (New Agents + Consistency Retests)

#### DSS Legal (SP/PDF) - GCC

> Jaylen Webb was brought to the emergency room at 03:15 AM on June 12, 2024. The admitting nurse is not specified in the provided documents
>
> *1 reference: Medical_Records.pdf*

**Result:** Correct time. PDF format fixed the SharePoint indexing problem — the .md files returned nothing, but the PDF was found and cited. Nurse not identified (same as MCP agents).

#### DSS Legal (SP/PDF) - Com

> **Time of Admission:** Jaylen Webb was brought to the Emergency Department at Spartanburg Medical Center at approximately 3:15 AM on June 12, 2024.
>
> **Admitting Nurse:** The admitting nurse was Charge Nurse Patricia Daniels, RN (Employee ID: SMC-4492) [1][2].
>
> *2 references: [1] Sheriff_Report_24-06-4418.pdf; [2] Medical_Records.pdf*

**Result:** Correct time AND found a nurse — Patricia Daniels from the Sheriff Report, complete with employee ID. This is a **different nurse** than Rebecca Torres (found by the KB agent from the Medical Records nursing notes). Both are fictional characters in the synthetic source documents. The Commercial agent cross-referenced two PDFs, which the GCC SharePoint PDF agent did not. Notably, the Sheriff Report states arrival at 0047 hours (12:47 AM), but the agent reported 3:15 AM from Medical Records — it didn't surface the time discrepancy between documents.

#### DSS Legal (SP/DOCX) - Com

> **Time of Arrival:** Jaylen Webb was brought to the Emergency Department at approximately 3:15 AM on June 12, 2024.
>
> **Admitting Nurse:** The admitting nurse was Charge Nurse Patricia Daniels, RN (Employee ID: SMC-4492) [1][2][1].
>
> *2 references: [1] Sheriff_Report_24-06-4418.docx; [2] Medical_Records.docx*

**Result:** Nearly identical to the PDF result — same time, same nurse, same two-document cross-reference. Confirms that **.docx works as well as PDF** for SharePoint indexing. Both formats are fully functional; only .md files fail in SharePoint libraries.

#### DSS Legal (MCP) - Com — Consistency Retest

Run 1 (Round 1):
> Jaylen Webb was brought to the Spartanburg Medical Center emergency room at 3:15 AM on June 12, 2024. X-rays at admission revealed multiple fractures inconsistent with the reported mechanism of injury (Medical Records, pp. 1-4). [...] The medical records reference Dr. Anita Chowdhury as the attending physician, but no nurse is listed in the documented events (Medical Records, pp. 1-4).

Run 2:
> Jaylen Webb was brought to the Spartanburg Medical Center emergency room and admitted at 3:15 AM on June 12, 2024. At that time, x-rays revealed a bilateral femur fracture (right) and a spiral fracture of the left humerus. The admitting physician was Dr. Anita Chowdhury. The available records do not specify the name of the admitting nurse (Medical Records, pp. 1-4).

**Result:** Consistent across both runs. Same core facts (03:15 AM, Dr. Chowdhury, no nurse, Medical Records pp. 1-4). Second run added more clinical detail (specific fracture types). No hallucination, no drift.

#### DSS Legal (MCP) - GCC — Consistency Retest

Run 1 (Round 1):
> Jaylen Webb was brought to the emergency room at 2:00 AM on June 12, 2024. [...] Dictation PDF, p. 4, and Medical Records, pp. 1-4.

Run 2:
> Jaylen Webb was brought to the emergency room at approximately 2:00 AM on June 12, 2024. The admitting nurse's name is not available in the provided records. [...] Dictation PDF, p. 4; Medical Records, pp. 1-4.

**Result:** Consistently wrong. GCC returns 2:00 AM both times — a **systematic hallucination**, not random variance. Also consistently fabricates the "Dictation PDF, p. 4" citation. The hallucination is reproducible.

### Prompt 2: Marcus Webb's Statements (Cross-Document)

#### DSS Legal (Web)

> Marcus Webb's statements regarding when he put Jaylen to bed are as follows:
>
> **To Hospital Staff** (Medical Records, Nursing Notes, p. 8, statement made June 12, 2024):
> "I put him to bed around ten. He was fine, running around all day. I fell asleep on the couch watching TV. Next thing I know, Dena is shaking me saying something is wrong with Jaylen."
>
> **To Law Enforcement** (Sheriff Report #24-06-4418, p. 4 & 5, statements made June 13, 2024):
> "I was on the couch all night. I did not go into Jaylen room after I put him down. I don't know how he got hurt. Maybe he climbed out of the crib and fell. He's been trying to climb out lately."
> "Dena and I have been arguing a lot lately but I would never hurt my son. I don't know why she is saying I was in the room. I was not in his room after 10 PM."
>
> **Comparison and Consistency:**
> Both accounts state that Marcus put Jaylen to bed (stated as "around ten" to medical staff and "after 10 PM" to law enforcement) and remained on the couch afterward. In both, he denies being in Jaylen's room after initially putting him to bed and attributes any injury to a possible fall from the crib. Thus, Marcus gave substantially the same answer to both hospital staff and law enforcement regarding when he put Jaylen to bed and where he was afterward.
>
> Source citations: Medical Records, Nursing Notes, p. 8 (statement to hospital staff, 6/12/2024); Sheriff Report #24-06-4418, pp. 4-5 (statements to law enforcement, 6/13/2024)

**Result:** Attorney-grade response. Direct quotes from both sources, specific page numbers and dates, cross-reference comparison, and identifies the Dena contradiction. Best answer of all agents.

#### DSS Legal (MCP) - GCC

> Marcus Webb told hospital staff that he put Jaylen to bed around ten and that Jaylen was fine, running around all day. He mentioned that he fell asleep on the couch watching TV and was woken up by Dena, who said something was wrong with Jaylen [1].
>
> To law enforcement, Marcus Webb stated that he was on the couch all night and did not go into Jaylen's room after putting him down. He suggested that Jaylen might have climbed out of the crib and fallen, as he had been trying to climb out recently [2].
>
> There is a discrepancy between these accounts. Marcus Webb's statement to the hospital staff implies he was unaware of any issues until Dena woke him, while his statement to law enforcement suggests he was on the couch all night and did not re-enter Jaylen's room [3].
>
> Footnotes: [1] Medical Records, Nursing Notes, p. 8; [2] Sheriff Report #24-06-4418, p. 4; [3] Sheriff Report #24-06-4418, pp. 4-8

**Result:** Strong answer. Both sources found, near-verbatim quotes, footnote citations with page numbers, and identified the discrepancy between accounts. Much better performance than the ER time question — GCC's weakness appears to be specific fact extraction, not cross-document reasoning.

#### DSS Legal (KB/.md) - Com *(retired)*

> Marcus Webb's statements are as follows:
>
> **To Hospital Staff:**
> The documents do not provide specific details about what Marcus Webb told hospital staff regarding when he put Jaylen to bed.
>
> **To Law Enforcement:**
> Marcus Webb stated to law enforcement that he put Jaylen to bed and then stayed on the couch all night. He denied going into Jaylen's room after putting him down and suggested that Jaylen may have climbed out of the crib and fallen [1][2].
>
> The information provided to law enforcement does not directly contradict any specific statement to hospital staff, as the documents do not detail his statements to the hospital.
>
> *References: [1] DSS_Investigation_Report.md; [2] Sheriff_Report_24-06-4418.md*

**Result:** Partial. Found law enforcement statements only. Completely missed the hospital staff statements from Medical Records Nursing Notes. Honest about what it couldn't find rather than hallucinating.

#### DSS Legal (SP/PDF) - Com

> Marcus Webb told hospital staff that he put Jaylen to bed at 10:00 PM on the night of June 11, 2024. He gave the same answer to law enforcement, stating that he did not re-enter Jaylen's room after putting him to bed at 10:00 PM.
>
> *1 reference: DSS_Investigation_Report.pdf*

**Result:** Found both hospital and law enforcement facts — a major improvement over the KB agent which missed hospital statements entirely. However: no direct quotes, no separate source citations, no mention of the Dena contradiction, and relied on the DSS Investigation Report summary rather than primary source documents.

#### DSS Legal (SP/DOCX) - Com

> **1. Statement to Hospital Staff**
>
> Marcus Webb told hospital staff that he put Jaylen to bed at approximately 10:00 PM on June 11, 2024, and that Jaylen was behaving normally throughout the day. Both parents reported to hospital staff that Jaylen had fallen from his crib. Webb stated he was asleep on the couch at the time of the incident and did not witness any fall or injury [1][2].
>
> **2. Statement to Law Enforcement**
>
> In his interview with law enforcement (Lt. Frank Odom, Spartanburg County Sheriff's Office), Marcus Webb repeated that he put Jaylen to bed at approximately 8:00 PM, then went to the living room and fell asleep on the couch. He stated he did not enter Jaylen's room after putting him to bed and did not know how the child was injured. Webb denied any physical contact with Jaylen after bedtime and suggested the child may have climbed out of the crib and fallen, as Jaylen had been trying to climb out lately [2].
>
> **3. Consistency of Statements**
>
> Marcus Webb's account to hospital staff and law enforcement was consistent: he claimed to have put Jaylen to bed, was not in the child's room after that, and did not witness or know how the injuries occurred. He denied any rough handling or physical discipline, and maintained that Jaylen may have fallen from the crib [1][2].
>
> **4. Additional Context**
>
> Medical staff and law enforcement noted that the injuries were inconsistent with a fall from a crib and more consistent with non-accidental trauma. There were also inconsistencies between the parents' accounts and the medical evidence [1][2].
>
> *2 references: [1] Medical_Records.docx; [2] Sheriff_Report_24-06-4418.docx*

**Result:** Best SharePoint response on this question — structured sections, both sources, consistency analysis, medical context, and named Lt. Frank Odom (verified character in the documents). However, contains a **subtle attribution error**: the 8:00 PM bedtime in the law enforcement section is actually from **Dena Holloway's** initial statement to police (Sheriff Report line 108: "Subject initially stated that Marcus Webb put the child to bed at approximately 8:00 PM"), not Marcus's own statement. Marcus consistently said "around ten" (hospital) and "after 10 PM" (law enforcement). The agent pulled a real fact from the document but assigned it to the wrong person — a particularly dangerous error type for legal work, where who said what matters enormously.

### Round 2 Comparison Matrix

| Dimension | Web | MCP - Com | MCP - GCC | SP/PDF - GCC | SP/PDF - Com | SP/DOCX - Com |
|---|---|---|---|---|---|---|
| **ER time** | 03:15 AM ✅ | 03:15 AM ✅ (x2) | 2:00 AM ❌ (x2) | 03:15 AM ✅ | 03:15 AM ✅ | 03:15 AM ✅ |
| **Admitting nurse** | Not in data | Not in data | Not in data | Not specified | **Patricia Daniels** ✅ | **Patricia Daniels** ✅ |
| **Marcus Webb: hospital** | Full quote ✅ | — | Near-verbatim ✅ | — | Summary ⚠️ | Found ✅ |
| **Marcus Webb: law enforcement** | Full quote ✅ | — | Near-verbatim ✅ | — | Summary ⚠️ | Found, **8 PM error** ❌ |
| **Marcus Webb: cross-doc** | Yes + Dena ✅ | — | Yes ✅ | — | No detail ⚠️ | Yes + medical context ✅ |
| **Consistency (ER time)** | — | Consistent ✅ | Consistently wrong ❌ | — | — | — |

### Round 2 Analysis

#### SharePoint PDF vs .md — Format matters enormously

The same SharePoint library that returned "no information found" for .md files successfully retrieved and cited PDF files. **PDF is the minimum viable format for SharePoint-backed Copilot Studio agents.**

#### GCC MCP: inconsistent quality across question types

GCC hallucinated the ER time (simple fact extraction) but excelled at Marcus Webb (complex cross-document reasoning). This is likely a **model difference, not a platform difference**: GPT-4o is weaker at faithfulness to tool output for specific value extraction but capable at synthesis. The hallucination is systematic — same wrong answer both times.

#### KB/.md (uploaded): strong on simple retrieval, weak on cross-document

Found Rebecca Torres (unique find) but missed hospital statements in the Marcus Webb question. RAG chunking surfaces different sections for different queries — a **retrieval coverage problem**, not a comprehension problem.

#### SP/PDF: decent recall, weak on depth

Found facts from both sources for Marcus Webb but relied on the DSS Investigation Report summary rather than primary source documents. No quotes, no page-level citations, no discrepancy analysis.

#### Web SPA remains the gold standard for structured queries

Direct quotes, page numbers, dates, cross-reference analysis. The benchmark for attorney-facing AI.

### Updated Demo Narrative (Round 2)

1. **Structured data + good orchestration = precision.** DSS Legal (Web) and DSS Legal (MCP) - Com consistently deliver accurate, well-cited answers from SQL-backed tools.
2. **Document format is a hidden dependency.** SharePoint went from total failure (.md) to functional (.pdf) just by changing file format. Customers who "just put docs in SharePoint" may get zero results if the format isn't right.
3. **GPT-4o vs GPT-4.1 is a real gap.** Same tools, same data, but GCC is locked to GPT-4o while Commercial uses GPT-4.1. The hallucination difference is reproducible.
4. **Cross-document reasoning is the hard test.** Simple fact lookup works for most agents. Cross-document comparison separates the strong from the weak.
5. **No single approach wins everything.** The KB agent uniquely found Rebecca Torres; the MCP agents uniquely did cross-document reasoning with citations. The ideal architecture layers both.

---

## Round 3 — New Agent Type + New Test Prompt (2026-03-06)

### New Agent

**DSS Legal (KB/DOCX) - Com** — documents uploaded directly to Copilot Studio as Knowledge files in DOCX format. Since Copilot Studio Knowledge does not support folders, source documents were renamed with the case number appended (e.g., `Medical_Records - dr-42-0892.docx`) to disambiguate across cases.

### Prompt 1: ER Time + Nurse — KB/DOCX - Com

> Jaylen Webb was brought to the emergency room at approximately 3:15 AM on June 12, 2024. The admitting nurse was Rebecca Torres, RN, BSN, who performed the initial triage assessment upon arrival.
>
> *1 reference: Medical_Records - dr-42-0892.docx*

**Result:** Correct time (3:15 AM) AND found Rebecca Torres — same nurse the retired KB/.md agent found. The DOCX upload slightly outperforms the old .md upload: KB/.md missed the admission time entirely, while KB/DOCX got both time and nurse correct.

### Prompt 2: Marcus Webb — New Results

#### DSS Legal (MCP) - Com — Orchestrator Failure

In a clean conversation (no case number provided), the agent failed to populate the `case_id` parameter for the tool call. The activity window showed `case_id` as empty (it is a required field).

> Please provide the case identifier for which you want to retrieve all recorded statements made by a specific person.

When the case number `2024-DR-42-0892` was provided in a follow-up message, the agent still could not bind the parameter:

> Please provide the case identifier (case_id) for which you want to get the comparison of conflicting accounts.

**This is a Commercial Copilot Studio orchestrator failure**, not a data or model issue. The same tool definition with the same `case_id` parameter works correctly in GCC. The GPT-4.1 orchestrator failed to resolve the case from character names alone AND failed to use an explicitly provided case number in follow-up.

#### DSS Legal (MCP) - Com — Re-run with Case Number in Prompt

When the case number was included directly in the prompt ("In case 2024-DR-42-0892, what did Marcus Webb tell hospital staff about when he put Jaylen to bed, and did he give the same answer to law enforcement?"), the agent produced a near-perfect response:

> **To Hospital Staff:** Marcus Webb stated, "I put him to bed around ten. He was fine, running around all day. I fell asleep on the couch watching TV. Next thing I know, Dena is shaking me saying something is wrong with Jaylen."
>
> Source: Medical Records, Nursing Notes, p. 8
>
> **To Law Enforcement:** Marcus Webb said, "I was on the couch all night. I did not go into Jaylen room after I put him down. I don't know how he got hurt. Maybe he climbed out of the crib and fell. He's been trying to climb out lately." He also stated, "I was not in his room after 10 PM."
>
> Source: Sheriff Report #24-06-4418, pp. 4-5
>
> **Consistency of Answers:** Marcus Webb's account to both hospital staff and law enforcement is consistent regarding the time he put Jaylen to bed (around 10 PM) and that he was not in Jaylen's room afterward. Both statements indicate he was on the couch and unaware of what happened to Jaylen after putting him to bed.

**Result:** With the case number in the prompt, MCP - Com delivers a top-tier answer: direct quotes, both sources, page-level citations, consistency analysis. No 8 PM misattribution. Close to the Web SPA gold standard — only missing the Dena contradiction detail.

**Key takeaway:** Prompt design matters for Copilot Studio tool-calling agents. GCC inferred the case from character names alone; Commercial required the case number explicitly in the prompt text (not just in follow-up). This is a practical consideration for demo design and end-user guidance.

#### DSS Legal (MCP) - GCC — Consistency Retest (Run 3)

> Marcus Webb told hospital staff that he put Jaylen to bed around ten and that Jaylen was fine, running around all day. He mentioned that he fell asleep on the couch watching TV and was later woken up by Dena, who said something was wrong with Jaylen. This statement is documented in the Medical Records, Nursing Notes, page 8.
>
> To law enforcement, Marcus Webb stated that he was on the couch all night and did not go into Jaylen's room after putting him down. He suggested that Jaylen might have climbed out of the crib and fallen, as he had been trying to climb out recently. This statement is documented in the Sheriff Report #24-06-4418, page 4.
>
> There is a discrepancy between these accounts. Marcus Webb's statement to medical staff implies he was unaware of any issues until Dena woke him, while his statement to law enforcement suggests he was on the couch all night and did not re-enter Jaylen's room. This discrepancy is noted in the Sheriff Report #24-06-4418, pages 4-8.

**Result:** Consistent with Rounds 1-2. Third successful run with the same structure, same facts, same citations. GCC MCP is reliable on this question.

#### DSS Legal (KB/DOCX) - Com

> Marcus Webb told law enforcement that he put Jaylen to bed in his crib at approximately 8:00 PM, then went to the living room and stayed on the couch for the rest of the night. He stated he did not go back into Jaylen's room after putting him to bed, did not witness any fall or incident, and denied any physical contact with Jaylen after bedtime. Webb suggested that Jaylen may have climbed out of his crib and fallen, as he had been trying to do so recently. When confronted with inconsistencies between his account and other statements, Webb maintained that he was not in Jaylen's room after 10 PM and denied any involvement in Jaylen's injuries.
>
> There is no evidence in the available records that Marcus Webb gave a different answer to hospital staff; the documentation focuses on his statements to law enforcement and DSS. The records do not indicate that Webb provided a separate or conflicting account to hospital staff regarding when he put Jaylen to bed or his actions afterward.
>
> *2 references: Sheriff_Report_24-06-4418 (truncated); DSS_Investigation_Report - dr-42-0892.docx*

**Result:** Found law enforcement statements but **missed hospital staff statements entirely** — claimed "no evidence" they exist despite being in Medical Records Nursing Notes. Contains the **8:00 PM misattribution error**: attributed Dena Holloway's "approximately 8:00 PM" claim to Marcus Webb's own statement. This is the same error made by SP/DOCX - Com in Round 2, making it a recurring pattern across document-backed agents.

### Prompt 3: Crystal Price "Clean Now" — All Results

#### DSS Legal (Web) — Hallucinated Case Number

> There is no available data regarding Crystal Price's statement about being "clean now" at the November 2023 hearing, nor are there any medical (including drug test) results in the records for case 2023-CP-24-1123.
>
> If you require information from another case or further detail, please specify.

**Result: Total failure.** The Web SPA — previously the gold standard on Prompts 1 and 2 — hallucinated a nonexistent case number (`2023-CP-24-1123`). Crystal Price's actual case is `2024-DR-15-0341`. The agent fabricated a case ID, queried it, found nothing, and confidently reported "no available data" as if the information doesn't exist. This is **worse than asking for help** (which MCP - Com did on Marcus Webb) — the Web SPA silently failed and presented the absence of data as a factual answer. An attorney would conclude there are no drug test results in the system.

This is the first Case 2 question asked of the Web SPA. Prompts 1 and 2 were both Case 1 (`2024-DR-42-0892`), which the agent resolved correctly from character names. The failure suggests the `/chat` endpoint's tool-calling loop cannot reliably resolve case IDs from person names alone when the case isn't the primary/first case in the database.

#### DSS Legal (Web) — Retest with Case Number in Prompt

Prompt: "For case 2024-DR-15-0341, Crystal Price told the court she was 'clean now' at the November 2023 hearing. What do the drug test results show?"

Tools called: `get_statements_by_person`, `get_timeline`

> Crystal Price stated to the court at the November 14, 2023, 90-Day Review hearing: "I am clean now." (Court Transcript, 90-Day Review, p. 12).
>
> Regarding drug testing, the only medical event documented is a substance abuse evaluation conducted on September 10, 2023. At that time, Dr. Raymond Ellis diagnosed Ms. Price with Opioid Use Disorder, moderate severity, and recommended enrollment in an intensive outpatient program (IOP) with random drug testing (Substance Abuse Evaluation Report).
>
> No actual drug test results (pass/fail or dates/results of any specific drug screens) are provided in the available data. Therefore, there is no corroboration or contradiction in the record regarding Ms. Price's claim to be "clean" at the November 2023 hearing.
>
> If you require further or updated substance testing data, please specify.

**Result: Correct case, correct tools, wrong conclusion.** This is arguably the **most dangerous failure across all testing**. The agent:

1. Found the right case ✅
2. Called the right tools (`get_statements_by_person` and `get_timeline`) ✅
3. Found and correctly quoted Crystal's "I am clean now" statement with page citation ✅
4. **Concluded no drug test results exist** ❌

The timeline event for November 14, 2023 explicitly states: "Two positive drug screens (fentanyl) in October." Monica Vance's statement (also in the retrieved data) says: "She has had two positive drug screens for fentanyl in October." Both were returned by the tools the agent called — the model received the data and failed to recognize it as drug test results.

This is a **comprehension failure**, not a retrieval failure. The drug screening information is embedded in narrative text within timeline events and statements, and GPT-4.1 didn't connect "two positive drug screens for fentanyl" with the user's question about "drug test results." An attorney reading this response would conclude Crystal's "clean now" claim is uncontradicted by the record — the exact opposite of reality.

By contrast, MCP - Com (also GPT-4.1, but orchestrated by Copilot Studio) correctly identified the fentanyl screens from the same SQL data. The difference is in the orchestration layer, not the model.

#### DSS Legal (MCP) - Com

> **Crystal Price's Drug Test Results (November 2023 Hearing Context)**
>
> At the November 2023 review hearing, Crystal Price told the court she was "clean now." However, court records show she had two positive drug screens for fentanyl in October 2023. This was noted at the ninety-day review hearing, where the court continued her treatment plan and warned that failure to comply could result in termination of parental rights. As of the hearing, Crystal Price had attended only 3 of 12 required intensive outpatient program (IOP) sessions, had not enrolled in parenting classes, and had no stable housing.
>
> Summary: Despite Crystal Price's claim to the court, drug test results in the months leading up to the November 2023 hearing showed continued substance use, specifically two positive screens for fentanyl.
>
> *Source: Court Filing, Order 2*

**Result:** Found the core contradiction and compliance summary from SQL. Lacked specific drug test dates (Oct 8/22), missed screen dates, and direct quotes from Crystal or Monica Vance — all of which exist in the SQL `statements` table but weren't retrieved by the orchestrator.

#### DSS Legal (SP/PDF) - Com

> **Crystal Price's Drug Test Results at the November 2023 Hearing**
>
> At the November 14, 2023 ninety-day review hearing, Crystal Price told the court, "I am clean now." However, the drug test results submitted to the court showed otherwise:
>
> October 8, 2023: Crystal Price tested positive for fentanyl.
> October 22, 2023: Crystal Price tested positive for fentanyl.
>
> These positive drug screens were submitted to the court and directly contradicted her claim of current sobriety at the hearing. The court noted that her assertion of being "clean now" was not supported by the drug test results, which showed fentanyl use just weeks prior to the hearing.
>
> Additionally, Crystal Price missed scheduled drug screens on December 5, 2023, January 15, 2024, and March 3, 2024. Per DSS policy and court order, missed screens are treated as presumptive positive results.
>
> Summary of Compliance: Only 3 of 12 required IOP sessions completed. No enrollment in parenting classes. No stable housing. Multiple positive drug screens and missed drug screens.
>
> Conclusion: The drug test results from October 2023 show Crystal Price was not "clean" at the time of the November 2023 hearing, and her compliance with court-ordered treatment remained insufficient.
>
> *3 references: DSS_Investigation_Report.pdf; Court_Orders_and_Filings.pdf; TPR_Petition_and_Affidavit.pdf*

**Result:** Most comprehensive answer on this question. Specific drug test dates, missed screen dates, presumptive positive policy, compliance summary, three-document cross-reference. The best document-backed response across all prompts tested.

#### DSS Legal (SP/DOCX) - Com

> **Crystal Price's Drug Test Results at the November 2023 Hearing**
>
> At the November 14, 2023 ninety-day review hearing, Crystal Price stated to the court: "I am clean now." However, drug screening results presented at the hearing showed that she tested positive for fentanyl on two separate occasions in October 2023. These positive drug screens directly contradicted her assertion of sobriety at the time of the hearing.
>
> Summary: Despite Crystal Price's claim of being "clean now," the drug test results from October 2023 indicated recent fentanyl use, undermining her statement to the court.
>
> *1 reference: Court_Orders_and_Filings.docx*

**Result:** Found the core contradiction with Crystal's direct quote, but notably shallower than the PDF version. No specific drug test dates, no missed screens, no compliance summary. Single source citation vs three for the PDF agent. This is the second time SP/DOCX has underperformed SP/PDF on the same question.

#### DSS Legal (KB/DOCX) - Com

> **Crystal Price's Drug Test Results at the November 2023 Hearing**
>
> At the November 14, 2023, ninety-day review hearing, Crystal Price told the court she was "clean now." However, drug screening results submitted to the court showed that Crystal Price tested positive for fentanyl on two separate occasions in October 2023 (specifically, October 8 and October 22). These positive drug screens directly contradicted her claim of current sobriety at the hearing.
>
> The court noted her low compliance with the treatment plan, including only three of twelve required intensive outpatient sessions attended and failure to enroll in parenting classes.
>
> Summary: Crystal Price's drug test results in October 2023 were positive for fentanyl, contradicting her statement to the court in November 2023 that she was "clean now."
>
> *2 references: DSS_Investigation_Report - dr-15-0341.docx; Court_Orders_and_Filings - dr-15-0341.docx (truncated)*

**Result:** Strong answer with specific drug test dates (Oct 8 and Oct 22), direct quote, compliance summary, and two source citations. Outperformed SP/DOCX (which missed the specific dates from the same document format). Second to SP/PDF overall on this question.

#### DSS Legal (SP/DOCX) - GCC

> The drug test results show that Crystal Price tested positive for fentanyl on two separate occasions in October 2023, which contradicts her statement to the court that she was "clean now."
>
> *1 reference: Court_Orders_and_Filings.docx*

**Result:** Found the core contradiction but shallow — no specific dates, no missed screens, no compliance summary, single source. Similar depth to SP/DOCX - Com on this question. Both DOCX SharePoint agents (GCC and Commercial) produced minimal answers compared to the PDF SharePoint agent.

#### DSS Legal (KB/PDF) - Com — Prompt 3: Crystal Price

> **Crystal Price's Drug Test Results at the November 2023 Hearing**
>
> At the November 14, 2023 ninety-day review hearing, Crystal Price told the court she was "clean now." However, drug test results submitted to the court showed she had two positive drug screens for fentanyl, dated October 8 and October 22, 2023. These positive results directly contradicted her claim of current sobriety at the hearing.
>
> **Summary of Compliance:**
>
> Ms. Price had attended only three of twelve required intensive outpatient program sessions. She missed scheduled drug screens on December 5, 2023, January 15, 2024, and March 3, 2024.
>
> *1 reference: DSS_Investigation_Report - 2024-dr-15-0341.pdf*

**Result:** Near the SP/PDF - Com gold standard. Direct Crystal quote, specific drug test dates (Oct 8 + Oct 22), missed screen dates (Dec 5, Jan 15, Mar 3), and compliance summary. Only the third agent to surface both specific drug test dates AND missed screen dates (after MCP - GCC from SQL discrepancies and SP/PDF - Com from three PDFs). Missing only the April 2024 negative screen and the presumptive positive policy that SP/PDF - Com uniquely found. Single source citation vs SP/PDF - Com's three, but the content depth is comparable.

#### DSS Legal (KB/PDF) - Com — Prompt 2: Marcus Webb

> **Statement to Hospital Staff:**
>
> Marcus Webb told hospital staff that he put Jaylen to bed at approximately 10:00 PM on June 11, 2024. He reported that Jaylen had been behaving normally throughout the day, and after putting him down, Webb fell asleep on the couch while watching television. He stated that the next thing he knew, Ms. Holloway was shaking him and telling him something was wrong with Jaylen.
>
> **Statement to Law Enforcement:**
>
> In his interview with law enforcement at the Spartanburg County Sheriff's Office, Marcus Webb stated that he was on the couch all night and did not go into Jaylen's room after he put the child down. He denied witnessing any fall and suggested that Jaylen may have climbed out of the crib and fallen, noting that Jaylen had been trying to climb out lately. Webb denied ever handling Jaylen roughly and stated he did not know how the injuries occurred. When confronted with inconsistencies between his statement and Ms. Holloway's account regarding his presence in or near the child's room at 9:30 PM, Webb insisted he was not in Jaylen's room after 10 PM.
>
> **Consistency of Answers:**
>
> Marcus Webb's answers to hospital staff and law enforcement were generally consistent in that he denied witnessing any incident and claimed not to know how Jaylen was injured. However, the timing and details about his presence in Jaylen's room differed slightly, especially when law enforcement pressed him about the timeline and Ms. Holloway's statements.
>
> *1 reference: DSS_Investigation_Report - 2024-dr-42-0892.pdf*

**Result:** One of the strongest document-backed Prompt 2 answers. Correctly reported **10:00 PM** bedtime (no 8 PM misattribution error). Hospital statement includes key details: normal behavior, fell asleep on couch, Holloway waking him. Law enforcement statement includes crib climbing, denied rough handling, 9:30 PM confrontation with Holloway's account, and "not in Jaylen's room after 10 PM." Consistency analysis correctly identifies the timeline discrepancy when pressed by law enforcement. Only weakness: single source citation (DSS_Investigation_Report) — didn't separately cite Medical_Records or Sheriff_Report. The 8 PM error tally is now 4/8 document-backed agents (50%).

#### DSS Legal (KB/PDF) - Com — Prompt 1: ER Time + Nurse

> **Time of Arrival:** Jaylen Webb was brought to the Emergency Department at Spartanburg Medical Center at approximately 03:15 AM on June 12, 2024.
>
> **Admitting Nurse:** The admitting nurse was Charge Nurse Patricia Daniels, RN (Employee ID: SMC-4492).
>
> *2 references: [1] Medical_Records - 2024-dr-42-0892.pdf; [2] Sheriff_Report_24-06-4418 - 2024-dr-42-0892.pdf*

**Result:** Correct time (3:15 AM) from Medical Records AND Patricia Daniels with employee ID from Sheriff Report — two-source cross-reference. Matches SP/PDF - Com quality exactly (same nurse, same ID, same two documents). Commercial KB/PDF delivers the same caliber answer as Commercial SP/PDF on this question.

#### DSS Legal (KB/PDF) - GCC — Prompt 3: Crystal Price

> The drug test results for Crystal Price, submitted during the November 2023 hearing, show that she tested positive for fentanyl on two separate occasions in October 2023. These positive results directly contradicted her statement that she was "clean now." The specific dates of the positive drug screens were October 8 and October 22, 2023.
>
> *2 references: [1] Court_Orders_and_Filings - 2024-dr-15-0341.pdf; [2] DSS_Investigation_Report - 2024-dr-15-0341.pdf*

**Result:** Strong answer with specific drug test dates (Oct 8 and Oct 22), contradiction identified, Crystal's "clean now" claim referenced, and two-source cross-reference. Very similar to KB/DOCX - GCC on this question. No missed screen dates or compliance summary, but the core facts are correct and well-sourced. GCC KB agents (both DOCX and PDF) consistently perform well on Prompt 3.

#### DSS Legal (KB/PDF) - GCC — Prompt 2: Marcus Webb

> Marcus Webb told the hospital staff that Jaylen had fallen from his crib. When speaking to law enforcement, he stated that he was on the couch all night and did not go into Jaylen's room after putting him to bed. He suggested that Jaylen may have climbed out of the crib and fallen, denying any rough handling and stating that he did not know how the injuries occurred.
>
> *2 references: [1] Sheriff_Report_24-06-4418 - 2024-dr-42-0892.pdf; [2] DSS_Investigation_Report - 2024-dr-42-0892.pdf*

**Result:** Found both hospital and law enforcement statements with two-source cross-reference. **Did not make the 8 PM misattribution error** — but avoided it by not mentioning any specific bedtime time at all. The hospital statement is thin ("fallen from his crib" only, no bedtime context). Law enforcement detail is adequate but lacks the depth of KB/DOCX - GCC (no Lt. Odom, no 9:30 PM confrontation, no "not in Jaylen's room after 10 PM"). No direct quotes, no cross-document analysis. Factually correct but shallow — the opposite trade-off from KB/DOCX - GCC, which had richer detail but made the 8 PM error.

#### DSS Legal (KB/PDF) - GCC — Prompt 1: ER Time + Nurse

> Jaylen Webb was brought to the emergency room at approximately 12:47 AM on June 12, 2024. The admitting nurse was Charge Nurse Patricia Daniels, RN.
>
> *1 reference: Sheriff_Report_24-06-4418 - 2024-dr-42-0892.pdf*

**Result:** Identical to KB/DOCX - GCC: same 12:47 AM time from the Sheriff Report, same Patricia Daniels, same single source citation. This confirms the 12:47 AM retrieval is a consistent GCC KB behavior — both DOCX and PDF uploads produce the same result. The GCC KB agents retrieve from the Sheriff Report rather than Medical Records, while most other agents (and the MCP/SQL agents) report 3:15 AM from Medical Records.

#### DSS Legal (KB/DOCX) - GCC — Prompt 1: ER Time + Nurse

> Jaylen Webb was brought to the emergency room at approximately 12:47 AM on June 12, 2024. The admitting nurse was Charge Nurse Patricia Daniels, RN.
>
> *1 reference: Sheriff_Report_24-06-4418 - dr-42-0892.docx*

**Result:** Found Patricia Daniels (Charge Nurse) from the Sheriff Report — consistent with SP/PDF - Com and SP/DOCX - Com findings. But reported **12:47 AM** instead of 3:15 AM. This is NOT a hallucination: the Sheriff Report states arrival at "0047 hours" (12:47 AM), while Medical Records states 3:15 AM. This is the **first agent to surface the time discrepancy between documents** — every other agent reported 3:15 AM from Medical Records (or 2:00 AM hallucinated by MCP - GCC). The two source documents genuinely disagree on the arrival time. SP/PDF - Com cited the Sheriff Report alongside Medical Records but still reported 3:15 AM; KB/DOCX - GCC only retrieved the Sheriff Report and reported its time. This raises an interesting question about what constitutes a "correct" answer when synthetic source documents contain internal contradictions.

#### DSS Legal (KB/DOCX) - GCC — Prompt 2: Marcus Webb

> Marcus Webb provided different statements to hospital staff and law enforcement:
>
> To Hospital Staff: Marcus Webb stated that he put Jaylen to bed at approximately 8:00 PM and spent the remainder of the evening in the living room.
>
> To Law Enforcement: During the interview with Lt. Frank Odom at the Spartanburg County Sheriff's Office, Marcus Webb stated that he was on the couch all night and did not go into Jaylen's room after putting the child down. He suggested that Jaylen may have climbed out of the crib and fallen. He denied witnessing any fall and handling Jaylen roughly. When confronted with the inconsistency between his statement and Ms. Holloway's statement regarding his presence in or near the child's room at 9:30 PM, Marcus Webb stated that he was not in Jaylen's room after 10 PM.
>
> Therefore, Marcus Webb did not give the same answer to law enforcement as he did to hospital staff.
>
> *2 references: [1] Sheriff_Report_24-06-4418 - dr-42-0892.docx; [2] DSS_Investigation_Report - dr-42-0892.docx*

**Result:** Found both hospital and law enforcement statements with two-source cross-reference and good law enforcement detail (Lt. Frank Odom, crib climbing, Dena's 9:30 PM confrontation, "not in Jaylen's room after 10 PM"). However, made the **8 PM misattribution error** — attributed Dena Holloway's "approximately 8:00 PM" claim to Marcus's hospital statement. This is the fourth document-backed agent to make this error (4/6), confirming it as a pervasive document retrieval pattern. Notably concluded the statements were **different** (most other agents said "consistent"), which is actually more analytically useful — though the inconsistency was partly based on the misattributed 8 PM time.

#### DSS Legal (KB/DOCX) - GCC — Prompt 3: Crystal Price

> The drug test results for Crystal Price, submitted during the November 14, 2023, ninety-day review hearing, showed two positive drug screens for fentanyl on October 8 and October 22, 2023. These results directly contradicted Ms. Price's claim of current sobriety.
>
> *2 references: [1] DSS_Investigation_Report - dr-15-0341.docx; [2] TPR_Petition_and_Affidavit - dr-15-0341.docx*

**Result:** Strong answer with specific drug test dates (Oct 8 and Oct 22) and two-source cross-reference — only the third agent to surface exact dates (after SP/PDF - Com and KB/DOCX - Com). Correctly identified the contradiction with Crystal's sobriety claim. However, missing Crystal's direct "clean now" quote, missed screen dates, compliance summary, and presumptive positive policy. Outperforms both GCC SharePoint agents (SP/PDF - GCC and SP/DOCX - GCC) on this question, suggesting KB uploads produce better retrieval than SharePoint libraries for GCC agents.

#### DSS Legal (SP/PDF) - GCC — Prompt 3: Crystal Price

> The drug test results show that Crystal Price tested positive for fentanyl on two occasions and missed multiple scheduled drug screens, as noted in the review of the DSS case file and case manager Monica Vance's reports.
>
> *1 reference: GAL_Reports.pdf*

**Result:** Found the core contradiction — fentanyl positives and missed screens — but shallow. No specific drug test dates (Oct 8/Oct 22), no missed screen dates, no Crystal "clean now" quote, no compliance summary, no presumptive positive policy. Only cited GAL_Reports.pdf (single source) vs SP/PDF - Com's three-document cross-reference. Named Monica Vance (a good detail absent from most other shallow answers). Consistent with the GCC pattern on this prompt: SP/DOCX - GCC was equally shallow. SP/PDF - Com remains the clear winner on Prompt 3 with its 3-PDF synthesis.

#### DSS Legal (SP/PDF) - GCC — Prompt 2: Marcus Webb

> Marcus Webb's statements are as follows:
>
> To Hospital Staff: The documents do not provide specific details about what Marcus Webb told the hospital staff regarding when he put Jaylen to bed.
>
> To Law Enforcement: Marcus Webb stated to law enforcement that he put Jaylen to bed in his crib at approximately 8:00 PM on June 11, 2024. He mentioned that after putting Jaylen to bed, he went to the living room, sat on the couch to watch television, and fell asleep. He claimed that he did not go into Jaylen's room after putting him to bed and suggested that Jaylen might have climbed out of his crib and fallen.
>
> *1 reference: Sheriff_Report_24-06-4418.pdf*

**Result: Two failures.** First, missed hospital staff statements entirely — claimed "documents do not provide specific details" when Marcus's hospital statements are in Medical_Records.pdf (Nursing Notes, p. 8). Second, made the **8 PM misattribution error** — the "approximately 8:00 PM" bedtime is from Dena Holloway's initial statement to police, not Marcus Webb's. Marcus consistently said "around ten" (hospital) and "after 10 PM" (law enforcement). Only cited one source (Sheriff Report), no cross-document analysis. This is the third document-backed agent to make the 8 PM error, confirming it is a **document retrieval pattern** — not specific to GPT-4.1 or DOCX format, since this agent uses GPT-4o on PDFs. No MCP-backed agent has ever made this error (0/4).

#### DSS Legal (SP/DOCX) - GCC — Prompt 1: ER Time + Nurse

> The specific time Jaylen Webb was brought to the emergency room and the name of the admitting nurse are not mentioned in the provided documents. However, the medical records from Spartanburg Medical Center, including the emergency department records from June 12, 2024, were reviewed as part of the investigation.
>
> *1 reference: GAL_Report.docx*

**Result: Retrieval failure.** Neither the ER time nor the admitting nurse was found. The agent only retrieved the GAL Report — which references the medical records but does not contain the specific time or nurse name. The actual facts (3:15 AM, Patricia Daniels/Rebecca Torres) are in Medical_Records.docx and Sheriff_Report.docx, which the GCC SharePoint retrieval did not surface. Notably honest — did not hallucinate a time (unlike MCP - GCC's systematic 2:00 AM fabrication) — but this is the weakest Prompt 1 result across all agents tested.

#### DSS Legal (SP/DOCX) - GCC — Prompt 2: Marcus Webb

> Marcus Webb provided the following statements:
>
> To Hospital Staff: Marcus Webb stated that he put Jaylen to bed at approximately 10:00 PM on June 11, 2024, and that the child was behaving normally throughout the day.
> To Law Enforcement: Marcus Webb told Lt. Odom on June 13, 2024, that he was on the couch all night, did not enter the child's room after putting the child to bed, and does not know how the child was injured.
>
> These statements are consistent with each other regarding the time he put Jaylen to bed but do not provide additional details about the events leading to the child's injuries.
>
> *1 reference: Court_Orders_and_Filings.docx*

**Result:** Correct but shallow. Found both hospital and law enforcement statements with accurate facts — 10:00 PM bedtime (matching Marcus's "around ten"), Lt. Odom named (verified character), June 13 date. Notably, **did not make the 8 PM misattribution error** that both SP/DOCX - Com and KB/DOCX - Com (GPT-4.1) made on DOCX-backed agents. GPT-4o correctly attributed the 10 PM bedtime to Marcus rather than pulling Dena's "approximately 8:00 PM" claim. However, the response lacks depth: no direct quotes, no Dena contradiction, no crib climbing detail, no page numbers, and only a single source citation (Court_Orders_and_Filings.docx rather than citing Medical_Records and Sheriff_Report separately). Minimal cross-document analysis — just "consistent regarding the time."

#### DSS Legal (MCP) - Com (Retest — Tool Chain Analysis)

Tools called: `list_cases` → `get_timeline`

> **Crystal Price's Drug Test Results (November 2023 Hearing Context)**
>
> At the November 2023 review hearing, Crystal Price told the court she was "clean now." However, court records show she had two positive drug screens for fentanyl in October 2023. This was noted in the court's order at the ninety-day review hearing, which also documented her incomplete attendance at required treatment sessions and lack of stable housing.
>
> The medical evaluation from September 2023 diagnosed her with moderate opioid use disorder and recommended intensive outpatient treatment with random drug testing.
>
> Summary: Despite Crystal Price's claim of sobriety at the November hearing, drug test results showed recent fentanyl use.
>
> *Sources: Court Filing, Order 2; Substance Abuse Evaluation Report*

**Result:** Consistent with the first MCP - Com test on this question. Found the contradiction and compliance summary from the timeline, but lacked specific dates, missed screens, or the April 2024 negative. The agent called `list_cases` (resolving the case correctly) then `get_timeline` and stopped — never calling `get_discrepancies` or `get_statements_by_person`.

#### DSS Legal (MCP) - GCC

Tools called: `list_cases` → `get_statements_by_person` → `get_discrepancies`

Run 1:
> Crystal Price claimed to be "clean now" at the November 2023 hearing. However, the drug test results show discrepancies:
>
> - Positive Drug Screens: Crystal Price had two positive drug screens for fentanyl in October 2023, three months after the removal of her children.
> - Missed Drug Screens: She missed scheduled drug screens on December 5, January 15, and March 3.
> - Recent Negative Screen: The most recent drug screen in April 2024 was negative, but her compliance with testing has been inconsistent.
>
> These findings are documented in the Drug Screen Reports and Court Transcripts (pp. 8, 12).

Run 2 (clean conversation): Identical content and structure.

**Result: Best MCP-backed response on this question, consistent across two runs.** GCC MCP called `get_discrepancies` — a tool that neither the Web SPA nor MCP - Com used for this question. The `discrepancies` table contains the specific missed screen dates (Dec 5, Jan 15, Mar 3), the April 2024 negative screen, and the "inconsistent compliance" assessment — all verbatim from the `contradicted_by` and `person_b_account` fields. The GCC agent's tool selection was superior: it recognized that a question about contradicting a person's claim maps to the discrepancies tool, not just the timeline or statements tools.

This explains why the Web SPA failed so badly despite calling the right case — it called `get_statements_by_person` and `get_timeline` but **never called `get_discrepancies`**, which is where the drug test detail lives. The timeline event only says "two positive drug screens (fentanyl) in October" without dates or missed screens. The discrepancy record has the full picture. **Tool selection by the orchestrator determined the outcome more than model quality.**

### Round 3 Comparison Matrices

#### Prompt 1: ER Time + Nurse (All Results to Date)

| Dimension | Web | MCP - Com | MCP - GCC | SP/PDF - GCC | SP/PDF - Com | SP/DOCX - Com | SP/DOCX - GCC | KB/DOCX - Com | KB/DOCX - GCC | KB/PDF - GCC | KB/PDF - Com |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **ER time** | 3:15 AM ✅ | 3:15 AM ✅ (x2) | 2:00 AM ❌ (x3) | 3:15 AM ✅ | 3:15 AM ✅ | 3:15 AM ✅ | **Not found** ❌ | 3:15 AM ✅ | **12:47 AM** ⚠️ (Sheriff Rpt) | **12:47 AM** ⚠️ (Sheriff Rpt) | 3:15 AM ✅ |
| **Admitting nurse** | Not in data | Not in data | Not in data | Not specified | **Patricia Daniels** ✅ | **Patricia Daniels** ✅ | **Not found** ❌ | **Rebecca Torres** ✅ | **Patricia Daniels** ✅ | **Patricia Daniels** ✅ | **Patricia Daniels** ✅ (+ ID) |
| **Citations** | Med Rec pp. 1-4 | Med Rec pp. 1-4 | Fabricated + Med Rec | Medical_Records.pdf | Sheriff Rpt + Med Rec | Sheriff Rpt + Med Rec | GAL_Report.docx (wrong source) | Medical_Records DOCX | Sheriff Rpt DOCX | Sheriff Rpt PDF | Med Rec + Sheriff Rpt PDF |

#### Prompt 2: Marcus Webb Statements (All Results to Date)

| Dimension | Web | MCP - Com* | MCP - GCC | SP/PDF - Com | SP/PDF - GCC | SP/DOCX - Com | SP/DOCX - GCC | KB/DOCX - Com | KB/DOCX - GCC | KB/PDF - GCC | KB/PDF - Com |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Hospital stmt** | Full quote ✅ | Full quote ✅ | Near-verbatim ✅ (x3) | Summary ⚠️ | **Denied existence** ❌ | Found ✅ | Found ✅ | **Denied existence** ❌ | Found, **8 PM** ❌ | Thin ("fell from crib") ⚠️ | Found ✅ (10 PM) |
| **Law enforcement stmt** | Full quote ✅ | Full quote ✅ | Near-verbatim ✅ (x3) | Summary ⚠️ | Found, **8 PM error** ❌ | Found, **8 PM error** ❌ | Found ✅ | Found, **8 PM error** ❌ | Found ✅ (detailed) | Found ✅ (no time) | Found ✅ (detailed) |
| **Cross-doc comparison** | Yes + Dena ✅ | Yes ✅ | Yes ✅ (x3) | Noted, no detail ⚠️ | None ❌ | Yes + medical context ✅ | Minimal ⚠️ | No (one source only) ❌ | Yes + 9:30 PM detail ✅ | Minimal ⚠️ | Yes (structured) ✅ |
| **8 PM misattribution** | No ✅ | No ✅ | No ✅ | No ✅ | **Yes** ❌ | **Yes** ❌ | **No** ✅ | **Yes** ❌ | **Yes** ❌ | **No** ✅ | **No** ✅ |

\* MCP - Com required case number in prompt; failed without it. See orchestrator failure details above.

#### Prompt 3: Crystal Price "Clean Now" (All Results to Date)

| Dimension | Web (no case #) | Web (with case #) | MCP - Com | MCP - GCC | SP/PDF - Com | SP/PDF - GCC | SP/DOCX - Com | SP/DOCX - GCC | KB/DOCX - Com | KB/DOCX - GCC | KB/PDF - GCC | KB/PDF - Com |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Case resolution** | **Hallucinated** ❌ | Correct ✅ | Correct | Correct | Correct | Correct | Correct | Correct | Correct | Correct | Correct | Correct |
| **"Clean now" claim** | Not found | **Quoted** ✅ | Found | Found | Found | Not surfaced | **Quoted** | Found | **Quoted** | Not surfaced | Referenced ✅ | **Quoted** ✅ |
| **Fentanyl positive** | — | **Not recognized** ❌ | Yes, no dates | Yes, no dates | **Oct 8 + Oct 22** | Yes, no dates | Yes, no dates | Yes, no dates | **Oct 8 + Oct 22** | **Oct 8 + Oct 22** | **Oct 8 + Oct 22** | **Oct 8 + Oct 22** |
| **Contradiction detected** | — | **No** ❌ | Yes ✅ | Yes ✅ | Yes ✅ | Yes ✅ | Yes ✅ | Yes ✅ | Yes ✅ | Yes ✅ | Yes ✅ | Yes ✅ |
| **Missed screens** | — | No | No | **Dec 5, Jan 15, Mar 3** ✅ | **Dec 5, Jan 15, Mar 3** | Mentioned, no dates | No | No | No | No | No | **Dec 5, Jan 15, Mar 3** ✅ |
| **Apr 2024 negative** | — | No | No | **Yes** ✅ | No | No | No | No | No | No | No | No |
| **Presumptive positive** | — | No | No | No | **Yes** | No | No | No | No | No | No | No |
| **Compliance summary** | — | No | Yes | Yes | Yes | No | No | No | Yes | No | No | Yes ✅ |
| **Monica Vance named** | — | No | No | No | No | **Yes** | No | No | No | No | No | No |
| **Tools called** | — | statements + timeline | list_cases → timeline | list_cases → statements → **discrepancies** | N/A (docs) | N/A (docs) | N/A (docs) | N/A (docs) | N/A (docs) | N/A (docs) | N/A (docs) | N/A (docs) |
| **Citations** | Fabricated case # | Court Transcript p. 12 | 1 (Court Filing) | Drug Screen Rpts + Court Transcript pp. 8, 12 | **3 PDFs** | 1 PDF (GAL) | 1 DOCX | 1 DOCX | 2 DOCXs | **2 DOCXs** | **2 PDFs** | 1 PDF (DSS Inv Rpt) |

### Round 3 Analysis

#### GCC vs Commercial MCP: Same tools available, different tools called

The most striking finding in Round 3 is the divergence in tool selection between the two MCP agents on the same question. Both have access to the same five MCP tools and the same SQL database — the only difference is the orchestrating model (GPT-4o for GCC, GPT-4.1 for Commercial).

| Behavior | MCP - GCC (GPT-4o) | MCP - Com (GPT-4.1) |
|---|---|---|
| **Prompt 2 (Marcus Webb):** Case resolution | Inferred from names | Failed without explicit case # |
| **Prompt 2:** Tool chain | *(single call — statements + discrepancies)* | Failed → succeeded with case # in prompt |
| **Prompt 3 (Crystal Price):** Tool chain | `list_cases` → `get_statements_by_person` → `get_discrepancies` | `list_cases` → `get_timeline` |
| **Prompt 3:** Missed screen dates | ✅ (from discrepancies) | ❌ |
| **Prompt 3:** April 2024 negative | ✅ (from discrepancies) | ❌ |
| **Prompt 3:** Contradiction depth | Full — specific dates, compliance assessment | Surface — "two positives in October" |
| **Prompt 1 (ER time):** Accuracy | ❌ Hallucinated 2:00 AM (x3) | ✅ Correct 3:15 AM (x2) |

**Neither model is consistently better.** GPT-4o (GCC) makes better tool selection decisions — it calls more tools and picks the right ones for the question (particularly `get_discrepancies`). GPT-4.1 (Commercial) is more faithful at reproducing specific values from tool output (no hallucination on ER time). The ideal orchestrator would combine GPT-4o's tool selection instincts with GPT-4.1's factual faithfulness.

This has direct implications for customers choosing between GCC and Commercial Copilot Studio: the answer quality difference is not just "GCC is worse" or "Commercial is better" — they fail in different, complementary ways. GCC hallucinates specific facts but reasons better about which tools to call. Commercial reproduces facts accurately but may not call the right tools to find them.

#### Commercial MCP orchestrator requires explicit case numbers

MCP - Com failed to call tools when the case number was not in the prompt, even after the user provided it in follow-up. GCC MCP inferred the case from character names alone. When MCP - Com received the case number in the original prompt, it produced a near-perfect response. **Prompt design is critical for Commercial Copilot Studio tool-calling agents.**

#### 8 PM misattribution is a document-backed pattern, not model- or format-specific

Four of six document-backed agents have now attributed Dena Holloway's "approximately 8:00 PM" statement to Marcus Webb — across both models and both formats:

| Agent | Model | Format | 8 PM Error? |
|---|---|---|---|
| SP/DOCX - Com | GPT-4.1 | DOCX | **Yes** ❌ |
| KB/DOCX - Com | GPT-4.1 | DOCX | **Yes** ❌ |
| SP/PDF - GCC | GPT-4o | PDF | **Yes** ❌ |
| KB/DOCX - GCC | GPT-4o | DOCX | **Yes** ❌ |
| SP/DOCX - GCC | GPT-4o | DOCX | No ✅ |
| SP/PDF - Com | GPT-4.1 | PDF | No ✅ |

The error is 4/6 across document-backed agents regardless of model or format, but 0/4 across MCP-backed agents. The root cause is that document retrieval chunks contain both Dena's and Marcus's statements in proximity, and the model sometimes attributes Dena's "8:00 PM" claim to Marcus. The SQL `statements` table eliminates this risk entirely — each statement has an explicit person ID, making misattribution structurally impossible. This is the strongest argument for structured data over document retrieval in legal applications where "who said what" is critical.

#### SP/PDF consistently outperforms SP/DOCX

On the Crystal Price question, SP/PDF cross-referenced three documents, found specific dates, and surfaced the presumptive positive policy. SP/DOCX cited one document with a shallow answer. This is the second question where SP/PDF outperformed SP/DOCX despite both formats indexing successfully. The gap may be due to retrieval variance or PDF text extraction producing better chunks for the RAG pipeline.

#### KB/DOCX is strong on detail extraction, weak on cross-document

Found Rebecca Torres (ER nurse) and specific drug test dates — details other agents missed. But missed hospital staff statements entirely on Marcus Webb and made the 8 PM misattribution error. Consistent with the pattern: KB agents retrieve well for single-document queries but struggle with multi-document synthesis.

#### CRITICAL: Misleading responses are more dangerous than wrong answers

The Web SPA's Crystal Price results represent the most dangerous failure pattern in this testing. On retest with the correct case number, the agent retrieved Crystal's "I am clean now" statement, called the right tools, received data containing "two positive drug screens for fentanyl in October" — and then told the user there were no drug test results and no contradiction. An attorney relying on this response would present Crystal Price's sobriety claim as uncontested fact in court.

This is worse than a hallucination (which can sometimes be caught by checking sources) and worse than a "no results" response (which at least signals incompleteness). A **false negative with high-confidence framing** — "no actual drug test results are provided in the available data" — actively misleads the user into trusting an incorrect conclusion. The agent's authoritative tone makes the error harder to detect.

Three categories of dangerous responses have emerged across testing:

| Danger Level | Failure Type | Example | Risk |
|---|---|---|---|
| **Critical** | False negative — data retrieved but not recognized | Web SPA on Crystal Price: "no drug test results" when fentanyl positives are in the data | Attorney presents false claim as uncontested |
| **High** | Misattribution — real fact, wrong person | SP/DOCX and KB/DOCX: attributed Dena's "8 PM" statement to Marcus | Attorney misrepresents who said what in court |
| **High** | Hallucinated fact with confidence | MCP - GCC: "2:00 AM" admission time (actual: 3:15 AM) | Attorney cites wrong time in filings |
| **Medium** | Hallucinated case number, silent failure | Web SPA: fabricated case `2023-CP-24-1123` and reported no data | Attorney concludes no records exist |

Every one of these failures would survive a casual review — the responses are well-formatted, professionally worded, and cite sources (real or fabricated). Only a user who independently knows the correct answer would catch them. This underscores why AI-assisted legal work requires human verification against primary sources, regardless of which agent architecture is used.

#### Case ID resolution is an emerging reliability problem

Three agents have now failed to resolve case IDs from person names alone:

| Agent | Failure Mode | Prompt |
|---|---|---|
| DSS Legal (Web) | Hallucinated case number `2023-CP-24-1123` — silently wrong | Crystal Price (Prompt 3) |
| DSS Legal (MCP) - Com | Asked for case ID, couldn't use it when provided in follow-up | Marcus Webb (Prompt 2) |
| DSS Legal (MCP) - Com | Succeeded when case ID was in the original prompt | Marcus Webb (Prompt 2, retry) |

The Web SPA failure is the most dangerous: it fabricated a plausible-looking case number and reported no results, giving the user no signal that anything went wrong. MCP - Com at least asked for help (though it then failed to use the answer). All three agents succeeded on Case 1 prompts, suggesting Case 1 may be easier to resolve (first case, more distinctive names, or default behavior).

#### No single agent wins across all three prompts

| Agent | Prompt 1 (ER) | Prompt 2 (Marcus Webb) | Prompt 3 (Crystal Price) | Prompt 4 (Skeletal Survey) |
|---|---|---|---|---|
| DSS Legal (Web) | Good (no nurse) | **Best** | **Failed x2** (hallucinated case #; then missed contradiction) | **Best MCP** — found fractures from SQL, distinguished med vs. LE |
| DSS Legal (MCP) - Com | Good (no nurse) | Good (needed case #) | Good (no dates) | Honest absence — suggested checking medical records |
| DSS Legal (MCP) - GCC | **Failed** (hallucination) | **Best** (consistent x3) | **Best MCP** (used discrepancies tool, x2) | Fabrication without case #; honest absence with case # |
| DSS Legal (SP/PDF) - Com | **Best** (Patricia Daniels) | Shallow | **Best** (3-doc synthesis) | **GOLD STANDARD** — only agent to catch cross-doc conflict |
| DSS Legal (SP/PDF) - GCC | Good (3:15 AM, no nurse) | **Failed** (missed hospital, 8 PM error) | Shallow (fentanyl, no dates) | **Failed** — repeated Sheriff Report's incorrect claim |
| DSS Legal (SP/DOCX) - Com | Good (Patricia Daniels) | 8 PM error | Shallow | **Failed** — repeated incorrect claim |
| DSS Legal (SP/DOCX) - GCC | **Failed** (retrieval — nothing found) | Correct, shallow, **no 8 PM error** ✅ | Shallow | **Failed** — repeated incorrect claim |
| DSS Legal (KB/DOCX) - Com | **Best** (Rebecca Torres) | 8 PM error + missed hospital | Good (specific dates) | **Failed** — repeated incorrect claim |
| DSS Legal (KB/DOCX) - GCC | **12:47 AM** ⚠️ (real, from Sheriff Rpt) + Patricia Daniels | 8 PM error, but good detail + 9:30 PM | Good (specific dates, 2 sources) | **Failed** — repeated incorrect claim |
| DSS Legal (KB/PDF) - GCC | **12:47 AM** ⚠️ (same as KB/DOCX) + Patricia Daniels | Correct, thin, **no 8 PM error** ✅ | Good (specific dates, 2 sources) | **Failed** — repeated incorrect claim |
| DSS Legal (KB/PDF) - Com | 3:15 AM ✅ + Patricia Daniels (+ ID) | Found both, 10 PM ✅, **no 8 PM error** | **Strong** (dates + missed screens + compliance) | **Failed** — repeated incorrect claim |

### Updated Demo Narrative

1. **Structured data eliminates attribution errors.** MCP agents never misattribute who said what — person IDs in SQL are unambiguous. Document-backed agents repeatedly pull the 8 PM bedtime from Dena's statement and assign it to Marcus.
2. **Document agents find details the schema missed.** Rebecca Torres (KB), Patricia Daniels (SP), specific drug test dates, missed screen dates, presumptive positive policy — all absent from SQL but present in documents.
3. **Prompt design is a hidden variable.** Commercial MCP failed without a case number; GCC handled inference. The Web SPA hallucinated a case number rather than asking. End users won't always know to include case numbers — the system needs to be robust to natural-language queries.
4. **PDF outperforms DOCX in SharePoint.** Same content, but PDF consistently produces deeper, better-cited answers. This may influence document management recommendations.
5. **The ideal system layers structured + unstructured.** MCP for precision and attribution safety, documents for the long tail of details. Neither alone is sufficient.
6. **Every agent has a failure mode.** The Web SPA (best on Prompts 1-2) hallucinated a case number on Prompt 3. GCC MCP (best on Prompt 2) hallucinated the ER time on Prompt 1. No agent is unconditionally reliable — the demo narrative is about understanding and mitigating each failure mode, not picking a winner.
7. **Misleading responses are more dangerous than wrong ones.** The Web SPA retrieved Crystal Price's data, found her "clean now" quote, and then concluded there were no drug test results — when fentanyl positives were in the data it received. A confident false negative is the worst outcome in legal AI: the attorney trusts the system and presents a false claim as uncontested. This is the strongest argument for human-in-the-loop verification, regardless of architecture.

---

## Round 5 — Additional Test Prompts, MCP Agents (2026-03-06)

Testing additional prompts from `Demo_Comparison_Prompts.md` across the three MCP-backed agents (Web SPA, MCP - Com, MCP - GCC).

### Prompt 3.2: Crystal Price Transportation Barrier (Case 2)

**Prompt:** "Crystal Price said she couldn't comply with the treatment plan because she lacked transportation. What support did DSS actually provide?"

**Ground truth** (from `discrepancies` table, topic "Compliance with treatment plan"): Crystal claims she lacks transportation and support. DSS records show bus passes issued monthly, three housing referrals provided, and IOP transportation assistance offered but declined. Despite supports, Crystal completed only 5/12 IOP sessions and 2/8 parenting classes in 8 months.

**Note:** Web SPA required case number in prompt (same Case 2 resolution failure as Prompt 3).

#### DSS Legal (Web) — with case number

> Crystal Price stated to the court on November 14, 2023: "I have been trying to get to the IOP sessions but I don't have reliable transportation. I missed some appointments." (Court Transcript, 90-Day Review, p. 12).
>
> Regarding DSS support: There is no evidence in the DSS Action timeline that DSS provided transportation assistance or support specifically for Crystal Price to attend treatment sessions or appointments. DSS actions recorded include the initial referral (8/5/2023), an unannounced home visit finding the home in unsanitary condition (8/8/2023), and the emergency removal of the children (8/8/2[truncated]

**Result: False negative.** Found Crystal's statement but concluded "no evidence" DSS provided transportation support. The agent called `get_statements` and `get_timeline` but not `get_discrepancies`, where the bus passes, housing referrals, and declined IOP transportation detail lives. Same tool selection failure as Prompt 3 (drug tests). An attorney would conclude DSS failed to support Crystal — the opposite of reality.

#### DSS Legal (MCP) - Com

> **Crystal Price's Transportation Barrier and DSS Support Provided**
>
> Crystal Price stated in court that she was unable to consistently attend IOP sessions due to unreliable transportation. She also reported difficulty finding housing without income and expressed that she was "clean now."
>
> DSS ordered a treatment plan requiring substance abuse evaluation, parenting classes, stable housing, and employment. At the 90-day review, Crystal Price had attended only 3 of 12 required IOP sessions, had not enrolled in parenting classes, and lacked stable housing. By the TPR probable cause hearing, Crystal Price had completed 5 of 12 IOP sessions, attended 2 of 8 parenting classes, and obtained temporary housing. The court noted progress but found it insufficient given the 8-month timeframe.
>
> **No Evidence of DSS Transportation Support:** The timeline and statements do not document DSS providing transportation assistance or arranging services to help Crystal Price attend treatment sessions. The DSS actions focused on monitoring compliance and court-ordered requirements, but there is no record of direct transportation support.
>
> *Sources: Court Filing, Orders 1-3*

**Result: Same false negative as Web SPA.** Found compliance numbers from `get_timeline` (3/12 → 5/12 IOP, 2/8 parenting) but concluded "no record of direct transportation support." Did not call `get_discrepancies`. Both GPT-4.1 agents (Web SPA and MCP - Com) fail identically on this question — they don't recognize it as a contradiction/discrepancy question requiring the discrepancies tool.

#### DSS Legal (MCP) - GCC

> Crystal Price stated that she couldn't comply with the treatment plan due to a lack of transportation. However, DSS provided the following support:
>
> - **Bus Passes:** DSS issued bus passes to Crystal Price on a monthly basis.
> - **Referral Assistance:** DSS provided three housing referrals to assist her in finding stable housing.
> - **Transportation Assistance:** DSS offered transportation assistance for IOP sessions, which Crystal Price declined.
>
> Despite these supports, Crystal Price completed only 5 out of 12 IOP sessions and 2 out of 8 parenting classes over an 8-month period.
>
> *Footnotes: Dictation PDF p. 8; Court Transcripts*

**Result: Perfect answer.** Found every key fact from the `discrepancies` table: bus passes (monthly), three housing referrals, IOP transportation offered and declined, compliance numbers (5/12 IOP, 2/8 parenting, 8 months). The "offered but declined" detail is the critical finding — it directly contradicts Crystal's transportation excuse. GCC called `get_discrepancies` (same tool selection pattern as Prompt 3), while both GPT-4.1 agents missed it entirely.

### Prompt 3.2 Comparison

| Dimension | Web SPA | MCP - Com | MCP - GCC |
|---|---|---|---|
| **Crystal's claim** | Quoted ✅ | Found ✅ | Found ✅ |
| **Bus passes** | ❌ | ❌ | **Monthly** ✅ |
| **Housing referrals** | ❌ | ❌ | **3 referrals** ✅ |
| **IOP transport declined** | ❌ | ❌ | **Yes** ✅ |
| **Compliance numbers** | Partial | ✅ (3/12 → 5/12, 2/8) | ✅ (5/12, 2/8) |
| **Tools called** | statements + timeline | timeline | **discrepancies** ✅ |
| **Conclusion** | "No evidence of support" ❌ | "No record of support" ❌ | DSS provided, Crystal declined ✅ |

**Analysis:** This prompt reinforces the Prompt 3 finding: **GPT-4.1 (both Web and MCP - Com) consistently fails to call `get_discrepancies` on contradiction questions.** GPT-4o (GCC) consistently recognizes these as discrepancy questions and calls the right tool. The pattern is now confirmed across two different Case 2 contradiction prompts. For an attorney, the GPT-4.1 false negative is more dangerous than a missed detail — it reverses the narrative from "DSS supported Crystal and she declined" to "DSS didn't support Crystal."

---

## Round 6 — Skeletal Survey Cross-Document Conflict (2026-03-06)

### Prompt 4: "Did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey?"

**Ground truth:** The source documents directly contradict each other:

- **Sheriff Report (p. 2):** "Radiology report indicated no fractures detected on skeletal survey"
- **Medical Records (pp. 3-4):** Skeletal survey found a transverse right femur fracture (3-5 days old) and a spiral left humerus fracture (24-48 hours old). The **remainder** of the skeletal survey found no additional fractures beyond those two.

The Sheriff's characterization is misleading — "no fractures detected" likely refers to no *additional* fractures beyond the already-diagnosed femur and humerus injuries, but the wording makes it sound like the skeletal survey was clean. This is exactly the kind of discrepancy attorneys need to catch.

**Critical:** "Skeletal survey" is NOT in the SQL schema. MCP agents cannot answer this question from structured data alone — the conflict lives entirely in the source documents.

### MCP Agent Results (without case number)

#### DSS Legal (MCP) - GCC

> The Sheriff's Office investigation did not find fractures in Jaylen Webb's skeletal survey. However, the discrepancies in the case indicate that the medical records and the Sheriff's report suggest the injuries were non-accidental and occurred at two separate times, inconsistent with a single fall event. The medical records and the Sheriff's report are cited as sources for these findings.
>
> *Footnotes: Medical Records pp. 1-5; Sheriff Report #24-06-4418*

**Result: Self-contradictory fabrication.** Says "did not find fractures" then discusses fractures being non-accidental. The SQL data doesn't contain "skeletal survey" — GCC invented an answer rather than admitting absence.

#### DSS Legal (MCP) - Com

> Please provide the case identifier for which you want to retrieve all recorded statements made by a specific person.

**Result: Orchestrator failure.** Could not resolve case from prompt. Same pattern as previous prompts.

#### DSS Legal (Web)

> There is no available data in the timeline regarding the Sheriff's Office investigation findings or any mention of fractures in Jaylen Webb's skeletal survey.

**Result: Honest absence.** Called `get_timeline` only. Correctly identified the data isn't there without fabricating.

### MCP Agent Results (with case number in prompt)

Retested with: "For case 2024-DR-42-0892, did the Sheriff's Office investigation find fractures in Jaylen Webb's skeletal survey?"

#### DSS Legal (Web)

> The Sheriff's Office investigation, led by Lt. Frank Odom, included a response to the hospital on June 12, 2024, to observe Jaylen Webb's injuries and coordinate with DSS. The case chronology shows the following relevant findings:
>
> Medical X-rays at Spartanburg Medical Center ER revealed Jaylen Webb had a "bilateral femur fracture (right) and spiral fracture of left humerus." These injuries were determined to be at different stages of healing and assessed as inconsistent with the reported cause (fall from crib) (Medical Records, pp. 1-4). Dr. Chowdhury reported to both DSS and the Sheriff that the injuries were non-accidental and occurred at different times (Medical Records, p. 5; DSS Intake Report).
>
> While the Sheriff's Office received and acted upon this medical information (Sheriff Report #24-06-4418, p. 1), there is no explicit entry in the law enforcement timeline that independently documents the results of a skeletal survey by Sheriff's investigators. Instead, law enforcement appears to have relied on the medical findings from the hospital.
>
> In summary: The Sheriff's Office investigation did find, based on hospital records and medical reporting, that Jaylen Webb had fractures noted in his skeletal survey (bilateral femur and left humerus), but this information was sourced from medical and not independent law enforcement examination.
>
> *Tools: get_timeline, get_statements_by_person*

**Result: Best MCP response.** Found fractures from SQL timeline, correctly distinguished medical vs. law enforcement sources, cited three references (Medical Records pp. 1-5, DSS Intake Report, Sheriff Report p. 1). Could not surface the Sheriff Report's contradictory "no fractures" claim (not in SQL).

#### DSS Legal (MCP) - Com

> Based on the available law enforcement timeline for case 2024-DR-42-0892, there is no mention in the Sheriff's Office investigation events of any findings regarding fractures in Jaylen Webb's skeletal survey. The documented law enforcement activities include responding to the hospital, observing child injuries, interviewing ER staff, and conducting interviews with Marcus Webb and Dena Holloway, but do not specify results from a skeletal survey or reference fractures. If you need more detailed medical findings, please specify if you would like to review medical event records.

**Result: Honest absence.** Resolved case correctly with case number in prompt. Accurately described what IS in the law enforcement timeline and honestly noted skeletal survey isn't there. Suggested checking medical records — a responsible handoff.

#### DSS Legal (MCP) - GCC

> The Sheriff's Office investigation did not specifically mention finding fractures in Jaylen Webb's skeletal survey in the provided timeline events. The events included Lt. Frank Odom responding to the hospital, observing child injuries, and interviewing ER nursing staff, but there was no mention of fractures in the skeletal survey.
>
> For more detailed information, you may need to refer to the specific medical reports or further details from the Sheriff's Office investigation.

**Result: Honest absence — major improvement over first run.** Adding the case number stopped the fabrication. Now correctly says "not specifically mentioned" rather than inventing an answer. Suggests checking medical reports.

### MCP Agent Comparison (with case number)

| Dimension | Web SPA | MCP - Com | MCP - GCC |
|---|---|---|---|
| **Case resolution** | ✅ | ✅ | ✅ |
| **Found fractures from SQL?** | **Yes** — bilateral femur + spiral humerus ✅ | No — listed Sheriff activities only | No — "not mentioned" |
| **Sheriff Report conflict?** | No (not in SQL) | No (not in SQL) | No (not in SQL) |
| **Medical vs. LE distinction** | **Yes** — noted fractures from medical, not independent LE ✅ | Partially — suggested checking medical | No |
| **Tools called** | `get_timeline` + `get_statements_by_person` | Timeline only | Timeline only |
| **Honest about gaps?** | Yes ✅ | Yes ✅ | Yes ✅ |
| **Fabrication?** | No ✅ | No ✅ | No ✅ (fixed from first run) |
| **Citations** | Med Rec pp. 1-5, DSS Intake, Sheriff Rpt p. 1 | None specific | None specific |

### Document Agent Results

#### DSS Legal (SP/PDF) - Com

> The Spartanburg County Sheriff's Office investigation reviewed hospital records and radiology reports for Jaylen Webb. The radiology report from the skeletal survey indicated that Jaylen Webb sustained a bilateral femur fracture (right leg) and a spiral fracture of the left humerus. These injuries were diagnosed by the attending physician, Dr. Anita Chowdhury, and were assessed as inconsistent with the reported mechanism of injury (a fall from a crib). The spiral fracture of the left humerus indicated torsional force, and radiographic findings showed the femur fracture was approximately 24 to 48 hours older than the humerus fracture, indicating two separate injury events.
>
> The Sheriff's Office investigation report specifically notes: "Radiology report indicated no fractures detected on skeletal survey." However, this refers to the absence of additional fractures beyond those already diagnosed (right femur and left humerus). The skeletal survey confirmed the presence of these two fractures and did not identify any other fractures elsewhere in the body.
>
> **Summary of Findings:** Yes, the Sheriff's Office investigation found fractures in Jaylen Webb's skeletal survey: a right femur fracture and a spiral fracture of the left humerus. No other fractures were detected elsewhere in the skeletal survey.
>
> *2 references: [1] Court_Orders_and_Filings.pdf; [2] Sheriff_Report_24-06-4418.pdf*

**Result: GOLD STANDARD.** The only agent across all 11 to catch the cross-document conflict. Found fractures from Court Orders/Medical Records, quoted the Sheriff Report's "no fractures" claim, and correctly explained it refers to no *additional* fractures. Two-source cross-reference with clinical detail (torsional force, different healing stages). Clear summary with a definitive "Yes" answer. This is the response an attorney needs.

#### DSS Legal (SP/DOCX) - Com

> Based on the Spartanburg County Sheriff's Office investigation report, the radiology report from Jaylen Webb's skeletal survey indicated that no fractures were detected. The attending physician, Dr. Anita Chowdhury, did document that the injuries were "suspicious for non-accidental trauma" and recommended further investigation, but specifically, the skeletal survey did not reveal any fractures.
>
> *1 reference: Sheriff_Report_24-06-4418.docx*

**Result: Repeated incorrect claim.** Single source (Sheriff Report only). Mentioned Dr. Chowdhury's non-accidental trauma suspicion but didn't connect it to actual fractures documented by the same doctor.

#### DSS Legal (KB/DOCX) - Com

> The Spartanburg County Sheriff's Office investigation report states that the radiology report indicated no fractures detected on the skeletal survey for Jaylen Webb. The attending physician, Dr. Anita Chowdhury, documented that the injuries were "suspicious for non-accidental trauma" and recommended further investigation, but the skeletal survey itself did not reveal any fractures.
>
> *1 reference: Sheriff_Report_24-06-4418 - 2024-dr-42-0892.docx*

**Result: Repeated incorrect claim.** Nearly identical to SP/DOCX - Com. Single source.

#### DSS Legal (KB/PDF) - Com

> The Spartanburg County Sheriff's Office investigation report states that the radiology report indicated no fractures detected on the skeletal survey for Jaylen Webb. The attending physician, Dr. Anita Chowdhury, documented that the injuries were "suspicious for non-accidental trauma" and recommended further investigation, but the skeletal survey itself did not reveal any fractures.
>
> *1 reference: Sheriff_Report_24-06-4418 - 2024-dr-42-0892.pdf*

**Result: Repeated incorrect claim.** Nearly identical to the other Commercial agents. Single source. KB/PDF - Com, which was near gold standard on Prompt 3 (Crystal Price), failed here.

#### DSS Legal (SP/PDF) - GCC

> No, the Sheriff's Office investigation did not find any fractures in Jaylen Webb's skeletal survey. The radiology report indicated no fractures detected on the skeletal survey.
>
> *1 reference: Sheriff_Report_24-06-4418.pdf*

**Result: Repeated incorrect claim.** Single source.

#### DSS Legal (SP/DOCX) - GCC

> The Sheriff's Office investigation did not find any fractures in Jaylen Webb's skeletal survey. The radiology report indicated no fractures detected.
>
> *1 reference: Sheriff_Report_24-06-4418.docx*

**Result: Repeated incorrect claim.** Single source.

#### DSS Legal (KB/PDF) - GCC

> No, the Sheriff's Office investigation did not find any fractures in Jaylen Webb's skeletal survey. The radiology report indicated no fractures detected on the skeletal survey.
>
> *1 reference: Sheriff_Report_24-06-4418 - 2024-dr-42-0892.pdf*

**Result: Repeated incorrect claim.** Single source.

#### DSS Legal (KB/DOCX) - GCC

> No, the Sheriff's Office investigation did not find any fractures in Jaylen Webb's skeletal survey. The radiology report indicated no fractures detected on the skeletal survey.
>
> *1 reference: Sheriff_Report_24-06-4418 - dr-42-0892.docx*

**Result: Repeated incorrect claim.** Single source.

### Prompt 4 Comparison Matrix (All Agents)

| Agent | Answer | Caught conflict? | Sources | Correct? |
|---|---|---|---|---|
| **SP/PDF - Com** | **Yes, fractures found** | **Yes — explained "no additional"** ✅ | 2 (Court Orders + Sheriff) | **✅** |
| Web SPA (MCP) | Fractures from SQL timeline | No (not in SQL) | 3 (Med Rec + DSS + Sheriff) | **Partial** ✅ |
| MCP - Com | "Not in data" | No (not in SQL) | N/A | Honest absence |
| MCP - GCC (with case #) | "Not mentioned" | No (not in SQL) | N/A | Honest absence |
| MCP - GCC (no case #) | "Did not find fractures" | No — **self-contradictory** | SQL sources | **❌ Fabrication** |
| SP/DOCX - Com | No fractures ❌ | No | 1 (Sheriff) | **❌** |
| KB/DOCX - Com | No fractures ❌ | No | 1 (Sheriff) | **❌** |
| KB/PDF - Com | No fractures ❌ | No | 1 (Sheriff) | **❌** |
| SP/PDF - GCC | No fractures ❌ | No | 1 (Sheriff) | **❌** |
| SP/DOCX - GCC | No fractures ❌ | No | 1 (Sheriff) | **❌** |
| KB/PDF - GCC | No fractures ❌ | No | 1 (Sheriff) | **❌** |
| KB/DOCX - GCC | No fractures ❌ | No | 1 (Sheriff) | **❌** |

### Round 6 Analysis

#### The most dangerous prompt in the test set

7 of 8 document-backed agents told the user there were no fractures in the skeletal survey — when the child had a broken femur and a broken humerus. An attorney relying on any of those 7 agents could miss critical evidence of abuse in a child protection case. This is not a nuance error or a missing detail — it is a factually wrong answer on a question with life-or-death stakes.

#### Why only SP/PDF - Com caught it

SP/PDF - Com retrieved TWO documents (Court_Orders_and_Filings.pdf + Sheriff_Report_24-06-4418.pdf) and cross-referenced them. Every other document agent retrieved ONLY the Sheriff Report. The Sheriff Report contains the misleading "no fractures detected" line, and without a second source to contradict it, every agent repeated it as fact.

The key differentiator is **multi-document retrieval**. SP/PDF - Com's RAG pipeline surfaced the Court Orders PDF (which contains references to the medical findings), giving the model enough context to recognize the conflict. All other agents — across both models (GPT-4.1 and GPT-4o), both formats (PDF and DOCX), and both connection types (SharePoint and Knowledge uploads) — retrieved only the Sheriff Report.

This suggests SP/PDF - Com's retrieval pipeline has a meaningfully broader recall than other configurations. It is the third time SP/PDF - Com has been the strongest document agent (Prompt 3: best Crystal Price answer; Prompt 2: no 8 PM error; Prompt 4: only agent to catch the conflict).

#### MCP agents were responsibly limited

None of the three MCP agents could answer this question from SQL alone — "skeletal survey" isn't in the schema. But their failures were qualitatively different from the document agents':

- **Web SPA** found the actual fractures from timeline events and correctly noted they came from medical records, not independent Sheriff investigation. Partial but not misleading.
- **MCP - Com and MCP - GCC** (with case number) honestly said the information wasn't in the data and suggested checking other sources.
- **MCP - GCC** (without case number) fabricated a self-contradictory answer — but adding the case number fixed this.

An attorney reading the MCP responses would know to look elsewhere. An attorney reading 7 of 8 document agent responses would conclude the skeletal survey was clean.

#### New danger category: Document-sourced false negatives

This prompt reveals a failure mode not seen in previous testing: the document agents don't just miss information (retrieval failure) or misattribute it (8 PM error) — they actively retrieve a **misleading source document** and present its incorrect characterization as the definitive answer. The Sheriff Report's "no fractures detected" is technically in the document, so the agent isn't hallucinating — it's faithfully reproducing an inaccurate summary from a real source. This is arguably harder to catch than a hallucination because the citation checks out.

| Danger Level | Failure Type | Example | Prompt |
|---|---|---|---|
| **Critical** | False negative — data retrieved but not recognized | Web SPA: "no drug test results" when fentanyl positives in data | 3 |
| **Critical** | **Misleading source faithfully reproduced** | 7/8 doc agents: "no fractures" from Sheriff Report | **4** |
| **High** | Misattribution — real fact, wrong person | 4/8 doc agents: Dena's "8 PM" attributed to Marcus | 2 |
| **High** | Hallucinated fact with confidence | MCP - GCC: "2:00 AM" (actual: 3:15 AM) | 1 |
| **Medium** | Hallucinated case number, silent failure | Web SPA: fabricated case `2023-CP-24-1123` | 3 |

---

## Open Items

### Completed
- [x] ~~DSS Legal (Web) on Crystal Price "clean now"~~ — **failed** (hallucinated case number)
- [x] ~~DSS Legal (Web) on Crystal Price — retest with case number~~ — **failed again** (found quote but missed drug test contradiction)
- [x] ~~DSS Legal (MCP) - GCC on Crystal Price "clean now"~~ — **best MCP response** (used `get_discrepancies` tool, consistent x2)
- [x] ~~DSS Legal (SP/DOCX) - GCC on Crystal Price~~ — shallow but correct

### Completed (Round 4)
- [x] ~~DSS Legal (SP/DOCX) - GCC on Prompt 1 (ER time + nurse)~~ — **retrieval failure**, found nothing (only GAL_Report.docx surfaced)
- [x] ~~DSS Legal (SP/DOCX) - GCC on Prompt 2 (Marcus Webb statements)~~ — correct but shallow, **no 8 PM error** (GPT-4o avoided the misattribution GPT-4.1 made)

### Completed (Round 4 continued)
- [x] ~~DSS Legal (SP/PDF) - GCC on Prompt 2 (Marcus Webb)~~ — **failed**: missed hospital statements, 8 PM misattribution error
- [x] ~~DSS Legal (SP/PDF) - GCC on Prompt 3 (Crystal Price)~~ — shallow but correct, named Monica Vance

### Completed (Round 4 — KB/DOCX GCC)
- [x] ~~DSS Legal (KB/DOCX) - GCC on Prompt 3 (Crystal Price)~~ — strong: specific dates (Oct 8/22), 2-source cross-ref
- [x] ~~DSS Legal (KB/DOCX) - GCC on Prompt 2 (Marcus Webb)~~ — 8 PM error, but good detail (Lt. Odom, 9:30 PM confrontation, 2 sources)
- [x] ~~DSS Legal (KB/DOCX) - GCC on Prompt 1 (ER time + nurse)~~ — **12:47 AM** from Sheriff Report (real time, first agent to surface doc discrepancy) + Patricia Daniels

### Completed (Round 4 — KB/PDF GCC)
- [x] ~~DSS Legal (KB/PDF) - GCC on Prompt 1 (ER time + nurse)~~ — identical to KB/DOCX - GCC: 12:47 AM + Patricia Daniels from Sheriff Report
- [x] ~~DSS Legal (KB/PDF) - GCC on Prompt 2 (Marcus Webb)~~ — correct but thin, no 8 PM error (avoided by omitting all times)
- [x] ~~DSS Legal (KB/PDF) - GCC on Prompt 3 (Crystal Price)~~ — strong: specific dates (Oct 8/22), 2-source cross-ref, "clean now" referenced

### Completed (Round 4 — KB/PDF Com)
- [x] ~~DSS Legal (KB/PDF) - Com on Prompt 1 (ER time + nurse)~~ — 3:15 AM ✅ + Patricia Daniels with employee ID, 2 sources
- [x] ~~DSS Legal (KB/PDF) - Com on Prompt 2 (Marcus Webb)~~ — strong: 10 PM ✅, no 8 PM error, 9:30 PM confrontation, consistency analysis
- [x] ~~DSS Legal (KB/PDF) - Com on Prompt 3 (Crystal Price)~~ — **near gold standard**: direct quote, specific dates, missed screen dates, compliance summary

### Not Started
- [ ] Demo dry run with side-by-side comparison

## Test Dates

- Round 1: 2026-03-05
- Round 2: 2026-03-06
- Round 3: 2026-03-06
- Round 4: 2026-03-06 (completed all remaining Prompt 1-3 testing across all agents)
- Round 5: 2026-03-06 (Prompt 3.2 — MCP agents only)
- Round 6: 2026-03-06 (Prompt 4 — skeletal survey, all 11 agents)
- Round 7: 2026-03-06 (Prompts 5-10 — new prompts from Demo_Comparison_Prompts.md)

---

## Round 7 — New Prompts (2026-03-06)

Six prompts selected from `Demo_Comparison_Prompts.md`, one per category. These cover full timeline enumeration, people roster, statement evolution, filtering precision, aggregate queries, and arithmetic reasoning.

### Test Prompts

| # | Demo # | Prompt | Case | Category |
|---|--------|--------|------|----------|
| 5 | 1.1 | "What is the complete timeline of events for case 2024-DR-42-0892?" | Case 1 | Factual Retrieval |
| 6 | 1.3 | "List all people involved in the Price TPR case and their roles." | Case 2 | Factual Retrieval |
| 7 | 2.2 | "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?" | Case 1 | Cross-Referencing |
| 8 | 4.2 | "What statements were made to law enforcement in case 2024-DR-42-0892?" | Case 1 | Filtering |
| 9 | 5.3 | "Which cases involve Termination of Parental Rights?" | All | Aggregate |
| 10 | 6.3 | "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?" | Case 1 | Precision |

### Ground Truth

#### Prompt 5 — Complete Timeline (Case 1)

12 events in chronological order:

| # | Date | Time | Type | Description |
|---|------|------|------|-------------|
| 1 | 2024-06-11 | 10:00 PM | Family | Marcus puts Jaylen to bed |
| 2 | 2024-06-12 | 2:00 AM | Medical | Dena finds Jaylen crying, unable to move leg; drives to ER |
| 3 | 2024-06-12 | 3:15 AM | Medical | ER admission — bilateral femur fracture + spiral humerus fracture, different healing stages |
| 4 | 2024-06-12 | 7:30 AM | Medical | Dr. Chowdhury files mandatory abuse/neglect report |
| 5 | 2024-06-12 | 11:00 AM | Law Enforcement | Lt. Odom responds to hospital |
| 6 | 2024-06-13 | 9:00 AM | DSS Action | Renee Dawson interviews Dena at hospital |
| 7 | 2024-06-13 | 1:30 PM | Law Enforcement | Lt. Odom interviews Marcus at sheriff office |
| 8 | 2024-06-13 | 4:00 PM | Law Enforcement | Lt. Odom interviews Dena at sheriff office — **account changes** |
| 9 | 2024-06-14 | 10:00 AM | Court | Emergency protective custody petition, ex parte removal order |
| 10 | 2024-06-18 | 9:30 AM | Court | Probable cause hearing, GAL appointed |
| 11 | 2024-06-20 | — | Placement | Jaylen placed with maternal grandmother Theresa Holloway |
| 12 | 2024-07-18 | 2:00 PM | Court | 30-day review, case plan approved |

**Scoring:** Count how many of the 12 events each agent returns. Note any fabricated events.

#### Prompt 6 — People Roster (Case 2)

8 people:

| # | Name | Role |
|---|------|------|
| 1 | Crystal Price | Parent (mother) |
| 2 | Brandon Price | Parent (father, incarcerated, rights relinquished) |
| 3 | Amari Price | Child (age 7) |
| 4 | Destiny Price | Child (age 5) |
| 5 | Monica Vance | Case Manager |
| 6 | Dr. Raymond Ellis | Substance abuse evaluator |
| 7 | Sandra Patterson | Foster parent (pre-adoptive) |
| 8 | Thomas Reed | Guardian ad Litem |

**Scoring:** Count correct names + roles. Note any hallucinated people or missing entries.

#### Prompt 7 — Dena Holloway Statement Evolution

Three key changes between hospital (June 12) and law enforcement (June 13, 4 PM):

1. **9:30 PM thump** — Not mentioned at hospital. Introduced under LE questioning: "Around 9:30 PM I heard a loud thump from Jaylen's room."
2. **Marcus placed in/near room** — Hospital statement says she was in the bedroom with the door closed. LE statement says she assumed Marcus was in the room and he said "everything was fine."
3. **History of rough handling** — Never mentioned at hospital. To LE: "Marcus has a temper... I have seen him grab Jaylen roughly by the arm before, maybe two or three times."

Also note the intermediate case manager statement (June 13, 9 AM) still matched the hospital version — the change only came under LE questioning that afternoon.

**Scoring:** Did the agent identify all 3 changes? Did it note the progression (hospital → case manager → LE)?

#### Prompt 8 — Statements to Law Enforcement (Case 1)

4 statements, all from June 13, 2024:

| # | Person | Summary | Source |
|---|--------|---------|--------|
| 1 | Marcus Webb | Was on couch all night, didn't enter room after putting Jaylen down. Suggests crib climbing. | Sheriff Report p. 4 |
| 2 | Marcus Webb | Denies being in room after 10 PM. Says Dena is wrong. Denies rough handling. | Sheriff Report p. 5 |
| 3 | Dena Holloway | Revises account — 9:30 PM thump, assumed Marcus was in room, he said "everything was fine." | Sheriff Report p. 7 |
| 4 | Dena Holloway | Marcus has a temper, grabs Jaylen roughly, 2-3 prior incidents. | Sheriff Report p. 8 |

**Scoring:** Did the agent return exactly 4 statements? Did it include non-LE statements (false positives)? Did it filter correctly?

#### Prompt 9 — TPR Cases (Aggregate)

9 cases with case_type = 'Termination of Parental Rights':

| # | Case Number | County |
|---|-------------|--------|
| 1 | 2024-DR-15-0341 | Richland |
| 2 | 2023-DR-25-0194 | Kershaw |
| 3 | 2024-DR-22-0165 | Chesterfield |
| 4 | 2025-DR-21-0289 | Richland |
| 5 | 2024-DR-38-0342 | Marlboro |
| 6 | 2025-DR-24-0382 | Kershaw |
| 7 | 2024-DR-42-0424 | Sumter |
| 8 | 2025-DR-09-0443 | Dillon |
| 9 | 2025-DR-45-0184 | Richland |

**Scoring:** Did the agent return a count? Is it correct (9)? Did it list case numbers? Document agents should fail here — they only have docs for Cases 1-2.

#### Prompt 10 — Time Gap (Thump → ER)

Key timestamps:
- **9:30 PM (June 11):** Dena hears "loud thump" from Jaylen's room
- **2:00 AM (June 12):** Dena finds Jaylen crying, unable to move leg
- **3:15 AM (June 12):** ER admission at Spartanburg Medical Center

Correct answers:
- Thump → discovery: **4 hours 30 minutes**
- Thump → ER admission: **5 hours 45 minutes**
- Discovery → ER: **1 hour 15 minutes**

**Scoring:** Did the agent identify the 9:30 PM thump as the starting point? Did it calculate correctly? Did it distinguish between discovery (2 AM) and ER admission (3:15 AM)?

---

### Results — Prompt 5 (Complete Timeline)

#### DSS Legal (Web)
> **Prompt:** "What is the complete timeline of events for case 2024-DR-42-0892?"

**Tools called:** `get_timeline`

**Response:** Returned all 12 events in chronological order (June 11 – July 18, 2024) with exact dates, times, event type labels in parentheses, descriptions, and source citations. All details match ground truth — 9:30 PM thump revision, Judge Easley, Karen Milford GAL, Theresa Holloway kinship placement, September 12 merits hearing.

**Score:** 12/12 events | Fabricated: 0 | Missing: 0

---

#### DSS Legal (MCP) - Com
> **Prompt:** "What is the complete timeline of events for case 2024-DR-42-0892?"

**Response:** Returned all 12 events in chronological order (June 11 – July 18, 2024) with dates, times, event type labels as subheadings, descriptions, and source citations. Grouped events by date. All facts match ground truth — Karen Milford, Theresa Holloway, September 12 merits hearing all present.

**Score:** 12/12 events | Fabricated: 0 | Missing: 0

---

#### DSS Legal (MCP) - GCC
> **Prompt:** "What is the complete timeline of events for case 2024-DR-42-0892?"

**Response:** Returned all 12 events in chronological order with dates, times, event type labels, descriptions, source citations, **and** "Parties Involved" for each event — the most detailed output of the three MCP agents. All facts match ground truth.

**Score:** 12/12 events | Fabricated: 0 | Missing: 0

---

#### DSS Legal (SP/PDF) - Com
> **Prompt:** "What is the complete timeline of events for case 2024-DR-42-0892?"

**Sources cited:** Sheriff_Report_24-06-4418.pdf, Medical_Records.pdf, DSS_Investigation_Report.pdf, Court_Orders_and_Filings.pdf

**Response:** Returned all 12 events in chronological order, organized by narrative section (Incident, Reporting, Interviews, Court, Placement, Review). Added a "Summary of Key Findings" and "Current Status" section — value-added narrative MCP agents didn't provide. Key details:

- **"8:00–10:00 PM" range** for bedtime — ground truth is 10:00 PM. The 8 PM likely comes from documents (known error pattern from prior rounds). Presented as a range rather than a flat misattribution, so less wrong.
- **Fracture detail richer than MCP:** "transverse fracture of right femur (estimated age: 3–5 days)" and "spiral fracture of left humerus (estimated age: 24–48 hours)" — pulled from Medical_Records.pdf, more specific healing timeline than SQL stores.
- **9:30 PM thump** correctly merged into the initial narrative (embedded in Dena's account, not a separate SQL event).
- **Rough handling disclosure** included in Dena's revised statement.
- June 13 interview times are vague ("June 13, 2024" and "Afternoon") vs ground truth exact times (9:00 AM, 1:30 PM, 4:00 PM).
- Theresa Holloway address (88 Creekside Ln, Greenville) included — detail MCP agents didn't surface.
- Karen Milford, September 12 merits hearing both present.

**Score:** 12/12 events | Fabricated: 0 | Missing: 0 | Minor imprecisions: bedtime range (8-10 PM vs 10 PM), vague June 13 times

---

#### DSS Legal (SP/DOCX) - Com
> **Prompt:** "What is the complete timeline of events for case 2024-DR-42-0892?"

**Sources cited:** Sheriff Report, Medical Records, DSS Investigation Report, Court Orders, (references numbered 1-6)

**Response:** Returned all 12 ground truth events plus several extra events pulled from documents. The richest timeline of any agent so far — but also the most embellished. Key observations:

- **8:00 PM bedtime (flat error):** Says Marcus put Jaylen to bed "around 8:00 PM." Ground truth is 10:00 PM. Worse than SP/PDF-Com's "8:00–10:00 PM" range — this is the known 8 PM misattribution error recurring.
- **Extra detail from documents:** Evening routine (5:30 PM arrival, 6:00 PM dinner, bath) — not in SQL, possibly from documents or hallucinated.
- **4:07 AM skeletal survey** — very specific time not in SQL timeline. Could be real from Medical_Records.docx or fabricated. Fracture aging detail matches SP/PDF-Com (3-5 days femur, 24-48 hours humerus).
- **June 12, 2:30 PM "DSS investigator"** — **likely fabricated.** Ground truth: Renee Dawson was assigned June 13, not June 12. No June 12 DSS action in SQL.
- **June 14 extras:** "DSS initiates kinship home study" and "Sheriff's Office files report" — not separate ground truth events, but plausible from documents.
- **June 28 & July 10 GAL home visits** — not in SQL, likely from GAL_Report.docx. Real document content, not hallucinated.
- All 3 changes in Dena's revised statement captured (thump, Marcus in room, rough handling).
- Karen Milford, Theresa Holloway, September 12 merits hearing all present.

**Score:** 12/12 events | Fabricated: 1-2 (2:30 PM DSS investigator on June 12; evening routine details uncertain) | Extra from docs: 3-4 (4:07 AM skeletal survey, GAL visits, June 14 extras) | Error: 8 PM bedtime (should be 10 PM)

---

#### DSS Legal (KB/PDF) - Com
> **Prompt:** "What is the complete timeline of events for case 2024-DR-42-0892?"

**Sources cited:** DSS_Investigation_Report - 2024-dr-42-0892.pdf, GAL_Report - 2024-dr-42-0892.pdf, Court_Orders_and_Filings - 2024-dr-42-.pdf (3 references — notably missing Medical_Records and Sheriff_Report)

**Response:** Returned a condensed 7-item timeline that collapses multiple events into summary blocks. Key observations:

- **Missing entirely:** June 11 bedtime (event #1), June 12 2:00 AM discovery (event #2), June 12 11:00 AM Lt. Odom response (event #5). No bedtime time at all — neither 8 PM nor 10 PM.
- **Collapsed June 12-13 into one block:** "Both parents provide inconsistent accounts" — merges the hospital statements, Dawson interview, and LE interviews into a single paragraph dated "June 12, 2024 (Evening)." Loses the progression from hospital → case manager → law enforcement.
- **9:30 PM thump** mentioned ✅ but without context that it emerged only during LE interview.
- **Rough handling** mentioned ✅.
- **GAL visits (June 28, July 10)** included — from GAL_Report.pdf, not in SQL.
- **Theresa Holloway address** included (88 Creekside Ln, Greenville).
- **July 18 thirty-day review** present ✅ but missing key details: no mention of psychological evaluations, supervised visitation, or September 12 merits hearing date. Only mentions "parenting education."
- **Only 3 source docs referenced** — Medical_Records.pdf and Sheriff_Report.pdf not cited. This explains the missing LE and medical detail.

**Score:** 6/12 events as discrete entries (3:15 AM ER, 7:30 AM report, June 14 removal, June 18 hearing, June 20 placement, July 18 review) | Missing as discrete: 6 (bedtime, 2 AM discovery, 11 AM Lt. Odom, Dawson interview, Marcus interview, Dena revised interview) | Fabricated: 0 | Collapsed: 3 interview events merged into one "Evening" summary block

---

#### DSS Legal (KB/DOCX) - Com
> **Prompt:** "What is the complete timeline of events for case 2024-DR-42-0892?"

**Sources cited:** Sheriff_Report_24-06-4418 - dr-42-0892.docx, Court_Orders_and_Filings - dr-42-0892.docx, DSS_Investigation_Report - dr-42-.docx (3 references — missing Medical_Records.docx and GAL_Report.docx)

**Response:** Returned 10 events (June 11 – June 14) with good chronological detail through the investigation phase, then stopped at the emergency removal order. Key observations:

- **Bedtime "8:00–10:00 PM" range** — same hedge as SP/PDF-Com (better than SP/DOCX-Com's flat 8 PM error).
- **9:30 PM thump** as a separate entry ✅ — correctly attributed to Dena's later disclosure.
- **2:00 AM discovery** present ✅ — KB/PDF-Com missed this entirely.
- **All 3 June 13 interviews** present as discrete entries with exact times ✅ (9:00 AM Dawson, 1:30 PM Marcus, 4:00 PM Dena).
- **Dena's revised account** includes all 3 changes: thump, Marcus near room, rough handling ✅.
- **Timeline stops at June 14** — missing June 18 probable cause hearing (#10), June 20 placement (#11), and July 18 thirty-day review (#12). The response appears complete (not truncated), so these events were simply not returned.
- **No Medical_Records.docx cited** — yet still got ER details (likely cross-referenced from DSS Investigation Report and Court Orders which reference medical findings).

**Score:** 9/12 events | Fabricated: 0 | Missing: 3 (June 18 hearing, June 20 placement, July 18 review — entire post-removal phase absent)

---

#### DSS Legal (SP/PDF) - GCC
> **Prompt:** "What is the complete timeline of events for case 2024-DR-42-0892?"

**Response:** Starts with Case 1 events (June 11–18) but then **cross-contaminates with Case 2 (Crystal Price/TPR)** starting at "November 14, 2023." The agent merged two completely different cases into one timeline. Truncated mid-sentence. Key observations:

- **Case 1 events present:** June 11 incident (vague), June 12 ER admission + Dr. Chowdhury, June 14 removal + Dawson recommendation, June 18 probable cause hearing. That's roughly 4 discrete events.
- **Missing from Case 1:** June 11 bedtime time, 2:00 AM discovery, 7:30 AM mandatory report as separate event, 11:00 AM Lt. Odom, all 3 June 13 interviews, June 20 placement, July 18 review.
- **Cross-contamination:** November 14, 2023 ninety-day review (Judge Harold Wynn, Crystal Price, fentanyl screens) — this is entirely Case 2 data injected into Case 1's timeline. Continued through February–March 2024 with Price's IOP and drug screen details.
- **No 9:30 PM thump** mentioned in Case 1 section.
- **No Dena statement evolution** captured.

- After the Case 2 digression, **loops back and duplicates** June 14 and June 18 events from Case 1 — same events it already listed.
- **Only 2 unique source docs:** DSS_Investigation_Report.pdf (cited twice as refs 1 and 3) and Court_Orders_and_Filings.pdf. Missing Medical_Records.pdf, Sheriff_Report.pdf, GAL_Report.pdf.
- The duplicate DSS_Investigation_Report reference likely pulled Case 2 content from a file that covers both cases or from a similarly named file.

**Score:** ~4/12 Case 1 events | Fabricated: 0 | Missing: 8 | Duplicated: 2 (June 14, June 18 listed twice) | **Critical error: Case 2 data merged into Case 1 timeline**

---

#### DSS Legal (SP/DOCX) - GCC
> **Prompt:** "What is the complete timeline of events for case 2024-DR-42-0892?"

**Sources cited:** Court_Orders_and_Filings.docx (1 reference — only a single document retrieved)

**Response:** Strong chronological coverage from a single document. Key observations:

- **10:00 PM bedtime** ✅ — only doc agent to get the exact correct time (no 8 PM error).
- **9:30 PM thump** ✅ — correctly noted as Dena's later disclosure to Lt. Odom.
- **All 3 June 13 interviews** present (Dawson, Marcus, Dena) — no exact times but described as separate events.
- **"Materially changed her account"** — strong legal phrasing for Dena's revision.
- **Missing:** June 11 bedtime as standalone event (#1), June 12 2:00 AM discovery (#2), June 20 placement (#11).
- **September 12 merits hearing** listed as a future event ✅ — only agent to break this out as its own timeline entry.
- **Only 1 source doc** (Court_Orders_and_Filings.docx) — yet still captured LE and medical detail, likely because the court orders reference/summarize those events.
- **No cross-contamination** with Case 2 (unlike SP/PDF - GCC).
- June 13 interview times not specified (Dawson, Marcus, Dena all listed under "June 13" without exact times).

**Score:** 9/12 events + 1 future event (Sept 12) | Fabricated: 0 | Missing: 3 (bedtime standalone, 2 AM discovery, June 20 placement) | No Case 2 contamination

---

#### DSS Legal (KB/PDF) - GCC
> **Prompt:** "What is the complete timeline of events for case 2024-DR-42-0892?"

**Sources cited:** GAL_Report (ref 1), Court_Orders_and_Filings / DSS_Investigation_Report (ref 2) — 2 references

**Response:** The most complete document-agent response on Prompt 5. Truncated at July 18 mid-sentence but all key events present. Key observations:

- **9:30 PM thump as first event** — starts the timeline here rather than bedtime. No bedtime time given (avoids the 8 PM error entirely).
- **10:00 PM bedtime** ✅ — correctly attributed to Marcus's statement during LE interview.
- **2:00 AM discovery missing** — jumps from 9:30 PM thump to 3:15 AM ER admission.
- **All 3 June 13 interviews** present as discrete events (Dawson, Marcus, Dena) — no exact times but clearly separated.
- **"Materially changes her account"** — same strong legal phrasing as SP/DOCX-GCC (GPT-4o pattern).
- **Dena's temper disclosure** ✅ — "Mr. Webb has a temper and becomes frustrated when the child cries" (close but not exact: ground truth adds "grab Jaylen roughly by the arm").
- **June 20 placement** ✅, **June 18 hearing + Karen Milford** ✅, **Judge Easley** ✅.
- **GAL visits as separate entries** (June 28, July 10) — from GAL_Report, richer detail than other agents.
- **July 18 review** present but truncated — mentions supervision restrictions but likely missing case plan details and September 12 date.
- **No cross-contamination** with Case 2.

- **Full response completed:** July 18 review includes supervision restrictions. September 12 merits hearing broken out as its own entry ✅ (same pattern as SP/DOCX-GCC).
- **3 references:** GAL_Report - 2024-dr-42-0892.pdf, Court_Orders_and_Filings - 2024-dr-42-0892.pdf (×2).

**Score:** 10/12 events + 1 future event (Sept 12) + 2 GAL visits from docs | Fabricated: 0 | Missing: 2 (bedtime standalone, 2 AM discovery)

---

#### DSS Legal (KB/DOCX) - GCC
> **Prompt:** "What is the complete timeline of events for case 2024-DR-42-0892?"

**Sources cited:** Court_Orders_and_Filings - dr-42-0892.docx (2 references, same document — only 1 unique source)

**Response:** Very similar structure to KB/PDF-GCC but with fewer post-removal events. Key observations:

- **9:30 PM thump as first event** — same pattern as KB/PDF-GCC.
- **10:00 PM bedtime** ✅ — correctly attributed to Marcus's LE interview.
- **2:00 AM discovery missing** — same gap as KB/PDF-GCC.
- **All 3 June 13 interviews** present as discrete events ✅ (Dawson, Marcus, Dena).
- **"Materially changes her account"** — same GPT-4o legal phrasing.
- **Rough handling fully quoted** ✅ — "grab the child roughly by the arm on approximately two to three prior occasions" (most complete version of any doc agent).
- **Missing:** June 18 probable cause hearing, June 20 placement, Karen Milford appointment, Theresa Holloway placement — entire post-removal phase compressed to just "emergency protective custody shall remain in effect."
- **July 18 review** present but minimal — no case plan details (parenting classes, psych evals, supervised visitation).
- **September 12 merits hearing** ✅ as its own entry.
- **Only 1 unique source doc** — Court_Orders_and_Filings.docx. No GAL_Report, no Medical_Records, no Sheriff_Report, no DSS_Investigation_Report.

**Score:** 8/12 events + 1 future event (Sept 12) | Fabricated: 0 | Missing: 4 (bedtime standalone, 2 AM discovery, June 18 hearing, June 20 placement)

---

### Results — Prompt 6 (People Roster)

> **Ground truth:** 8 people in SQL. 4 additional people exist in documents only: Patricia Holloway (DSS Caseworker), Judge Harold Wynn, Michael Patterson (Sandra's husband), Rebecca Torres, Esq. (DSS Staff Attorney).

#### Summary Table

| Agent | Core (of 8) | Doc-Only Extras | Hallucinated | Key Issue |
|---|---|---|---|---|
| Web SPA | 8/8 | 0 | 0 | Clean, complete |
| MCP - Com | 8/8 | 0 | 0 | Clean, matches Web |
| MCP - GCC | 8/8 | 0 | 0 | Richest detail (DOBs, notes, addresses) |
| SP/PDF - Com | 8/8 | 4 | 0 | Best overall — 12 people, 4 sources |
| SP/DOCX - Com | 8/8 | 4 | 0 | Matches SP/PDF-Com, summary table |
| KB/PDF - Com | 8/8 | 2 | 0 | Solid, mild padding (Notary) |
| KB/DOCX - Com | 8/8 | 2 | 0 | Clean, found Rebecca Torres |
| KB/PDF - GCC | 8/8 | 3 | 0 | Padding (Unit Supervisor, Notary) |
| SP/PDF - GCC | 5/8 | 2 | 0 | Missing children as entries + Thomas Reed |
| SP/DOCX - GCC | 5/8 | 3 | 0 | Missing children as entries + Dr. Ellis |
| KB/DOCX - GCC | 7/8 | 3 | 0 | Missing Dr. Ellis |

#### DSS Legal (Web)
> **Prompt:** "List all people involved in the Price TPR case and their roles."

**Tools called:** `list_cases`, `get_case_summary`

**Response:** Listed all 8 people with names, roles, and brief descriptions. Accurate role labels (Parent, Child, Case Manager, Witness, Foster Parent, GAL). Noted Brandon Price's voluntary relinquishment and Sandra Patterson's pre-adoptive status.

**Score:** 8/8 people | Hallucinated: 0 | Missing: 0

---

#### DSS Legal (MCP) - Com
> **Prompt:** "List all people involved in the Price TPR case and their roles."

**Response:** Listed all 8 people with names, roles, and descriptions. Identical content coverage to Web SPA — clean enumeration from SQL data.

**Score:** 8/8 people | Hallucinated: 0 | Missing: 0

---

#### DSS Legal (MCP) - GCC
> **Prompt:** "List all people involved in the Price TPR case and their roles."

**Response:** Listed all 8 people with the richest detail of any MCP agent — DOBs, full notes (Kirkland Correctional, Longleaf Elementary, foster parent since 2019), addresses. Every field from the SQL `people` table surfaced.

**Score:** 8/8 people | Hallucinated: 0 | Missing: 0

---

#### DSS Legal (SP/PDF) - Com
> **Prompt:** "List all people involved in the Price TPR case and their roles."

**Sources cited:** TPR_Petition_and_Affidavit.pdf, GAL_Reports.pdf, Court_Orders_and_Filings.pdf, DSS_Investigation_Report.pdf (4 references)

**Response:** Listed 12 people — all 8 core plus Patricia Holloway (DSS Caseworker), Michael Patterson (foster co-parent), Rebecca Torres, Esq. (DSS Staff Attorney), and Judge Harold Wynn. Each person has a detailed role description. DSS listed as an organizational entity (Petitioner). Children listed as separate entries with DOBs.

**Score:** 8/8 people | Hallucinated: 0 | Doc-only extras: 4 (Patricia Holloway, Michael Patterson, Rebecca Torres, Judge Wynn) | **Best document agent — most complete roster from any agent**

---

#### DSS Legal (SP/DOCX) - Com
> **Prompt:** "List all people involved in the Price TPR case and their roles."

**Sources cited:** TPR_Petition_and_Affidavit.docx, Substance_Abuse_Evaluation.docx, DSS_Investigation_Report.docx, GAL_Reports.docx (4 references)

**Response:** Listed same 12 people as SP/PDF-Com with identical accuracy. Added a summary table at the end mapping each person to their role/title. Same 4 doc-only extras. Children as separate entries with DOBs.

**Score:** 8/8 people | Hallucinated: 0 | Doc-only extras: 4 | Matches SP/PDF-Com quality

---

#### DSS Legal (KB/PDF) - Com
> **Prompt:** "List all people involved in the Price TPR case and their roles."

**Sources cited:** TPR_Petition_and_Affidavit - 2024-dr-15-0341.pdf, DSS_Investigation_Report - 2024-dr-15-0341.pdf (2 references)

**Response:** Listed 10 people — all 8 core plus Patricia Holloway and a generic "Notary Public." Children listed as separate entries. Dr. Ellis identified but first name omitted. Sandra Patterson listed without Michael. Judge Wynn and Rebecca Torres not found (fewer source docs than SP agents).

**Score:** 8/8 people | Hallucinated: 0 | Doc-only extras: 2 (Patricia Holloway, Notary — Notary is padding)

---

#### DSS Legal (KB/DOCX) - Com
> **Prompt:** "List all people involved in the Price TPR case and their roles."

**Sources cited:** TPR_Petition_and_Affidavit - dr-15-0341.docx, DSS_Investigation_Report - dr-15-0341.docx, TPR_Petition_and_Affidavit - dr-15-0341.docx (3 references, 2 unique)

**Response:** Listed 10 people — all 8 core plus Patricia Holloway and Rebecca Torres, Esq. Children as separate entries. Dr. Ellis identified without first name. Clean response with accurate role descriptions. No Judge Wynn or Michael Patterson.

**Score:** 8/8 people | Hallucinated: 0 | Doc-only extras: 2 (Patricia Holloway, Rebecca Torres)

---

#### DSS Legal (SP/PDF) - GCC
> **Prompt:** "List all people involved in the Price TPR case and their roles."

**Sources cited:** TPR_Petition_and_Affidavit.pdf (1 reference)

**Response:** Listed 7 entries — Crystal Price, Brandon Price, Patricia Holloway, Monica Vance, Judge Wynn, Dr. Ellis, "Patterson Family." Children mentioned in Crystal/Brandon descriptions ("biological mother of Amari Price and Destiny Price") but **not listed as separate entries.** Thomas Reed completely absent. "Patterson Family" is vague — no first names.

**Score:** 5/8 people | Hallucinated: 0 | Missing as entries: 3 (Amari, Destiny, Thomas Reed) | Doc-only extras: 2 (Patricia Holloway, Judge Wynn) | Only 1 source doc

---

#### DSS Legal (SP/DOCX) - GCC
> **Prompt:** "List all people involved in the Price TPR case and their roles."

**Sources cited:** TPR_Petition_and_Affidavit.docx, DSS_Investigation_Report.docx, Court_Orders_and_Filings.docx (3 references)

**Response:** Listed 7 entries — Crystal Price, Brandon Price, Patricia Holloway, Monica Vance, Harold Wynn, Thomas Reed, Sandra and Michael Patterson. Children mentioned in Crystal's description but **not listed as separate entries.** Dr. Raymond Ellis completely absent. Better source coverage than SP/PDF-GCC (3 docs vs 1) but same child-listing gap.

**Score:** 5/8 people | Hallucinated: 0 | Missing as entries: 3 (Amari, Destiny, Dr. Ellis) | Doc-only extras: 3 (Patricia Holloway, Judge Wynn, Michael Patterson)

---

#### DSS Legal (KB/PDF) - GCC
> **Prompt:** "List all people involved in the Price TPR case and their roles."

**Sources cited:** DSS_Investigation_Report - 2024-dr-15-0341.pdf, Court_Orders_and_Filings - 2024-dr-15-0341.pdf, TPR_Petition_and_Affidavit - 2024-dr- (3 references)

**Response:** Listed all 8 core people plus Judge Harold Wynn, a generic "Unit Supervisor," and a generic "Notary Public." Children listed as separate entries under "Children Involved" subheading. Dr. Ellis identified without first name. Sandra and Michael Patterson listed together.

**Score:** 8/8 people | Hallucinated: 0 | Doc-only extras: 3 (Judge Wynn, Unit Supervisor, Notary — last two are unnamed padding)

---

#### DSS Legal (KB/DOCX) - GCC
> **Prompt:** "List all people involved in the Price TPR case and their roles."

**Sources cited:** Court_Orders_and_Filings - dr-15-0341.docx, DSS_Investigation_Report - dr-15 (2 references)

**Response:** Listed 10 entries — Crystal Price, Brandon Price, Amari Price, Destiny Price, Monica Vance, Thomas Reed, Judge Harold Wynn, Sandra Patterson, "Counsel for DSS" (unnamed), "Appointed Counsel for Crystal Price" (unnamed). **Dr. Raymond Ellis completely absent.** Children listed with DOBs. Two unnamed counsel entries are accurate roles but not specific people.

**Score:** 7/8 people | Hallucinated: 0 | Missing: 1 (Dr. Raymond Ellis) | Doc-only extras: 3 (Judge Wynn, 2 unnamed counsels)

---

#### Prompt 6 Key Findings

1. **Zero hallucinated people across all 11 agents** — cleanest prompt so far. No fabricated names or roles.
2. **All MCP agents: 8/8** — deterministic from SQL. GCC MCP surfaced the richest detail (every field from the people table).
3. **Commercial doc agents dominated** — all 4 Commercial doc agents scored 8/8 core; only 1 of 4 GCC doc agents did (KB/PDF-GCC).
4. **SP/PDF-Com and SP/DOCX-Com best overall** — 8/8 core plus 4 document-only extras (Patricia Holloway, Michael Patterson, Rebecca Torres, Judge Wynn). Four source docs each.
5. **GCC SharePoint agents underperformed again** — both SP/PDF-GCC and SP/DOCX-GCC scored 5/8, missing children as separate entries. Same pattern as Prompt 5 where GCC SP agents struggled with completeness.
6. **Document agents add genuine value on this prompt** — 4 real people exist in the documents but not in SQL. An attorney using only MCP would miss the caseworker, staff attorney, judge, and foster co-parent.
7. **GPT-4.1 (Commercial) more thorough at enumeration** — the completeness gap between Com and GCC doc agents is the widest of any prompt tested so far.
8. **Padding problem in GCC KB agents** — KB/PDF-GCC and KB/PDF-Com listed "Notary Public" and "Unit Supervisor" as involved people. Technically present in documents but noise for an attorney.

---

### Results — Prompt 7 (Statement Evolution)

#### Summary Table

| Agent | Changes (of 3) | Progression | Key Strength |
|---|---|---|---|
| Web SPA | 3/3 | No | Direct quotes, referenced Discrepancy 6, page citations |
| MCP - GCC | 3/3 | No | 6 discrepancies enumerated, 4.5-hour delay noted |
| MCP - Com | **2/3** | No | **Missing rough handling** |
| SP/PDF - Com | 3/3 | No | Summary table, fear motive, Dena's inference, demeanor shift |
| SP/DOCX - Com | 3/3 | No | Summary table, "material" legal framing, 2 sources |
| KB/PDF - Com | 3/3 | No | Direct quote, grandmother placement wish (unique detail) |
| KB/DOCX - Com | 3/3 | No | 3 sources, direct quotes, Medical Records detail |
| SP/PDF - GCC | 3/3 | No | Demeanor noted, 1 source |
| SP/DOCX - GCC | 3/3 | No | "Responsibility and awareness" analytical lens, 2 sources |
| KB/PDF - GCC | 3/3 | No | Demeanor noted, 2 sources |
| KB/DOCX - GCC | 3/3 | No | Most detailed demeanor analysis, category labels |

#### DSS Legal (Web)
> **Prompt:** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

**Tools called:** `get_statements_by_person`, `get_discrepancies`

**Response:** Direct quotes from both statements with page-level citations (Nursing Notes p. 9, Sheriff Report pp. 7-8). Identified all 3 changes: 9:30 PM thump, Marcus's presence near room, and rough handling history. Explicitly referenced "Discrepancy 6" from the database — the only agent to tie findings to a numbered discrepancy record. Cross-referenced Medical Records p. 9 and Sheriff Report pp. 6-8.

**Score:** 3/3 changes | Progression noted: No

---

#### DSS Legal (MCP) - Com
> **Prompt:** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

**Response:** Found both statements with source citations (Medical Records Nursing Notes p. 9, Sheriff Report p. 7). Identified 9:30 PM thump and Marcus's assurance. Key changes list notes timing shift and "implied possible prior knowledge." **Did not mention rough handling or temper** — the only agent to miss this change. Likely called `get_statements_by_person` but either didn't retrieve statement 4 (rough handling) or the orchestrator omitted it from the summary.

**Score:** 2/3 changes | Progression noted: No | Missing: rough handling / temper history

---

#### DSS Legal (MCP) - GCC
> **Prompt:** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

**Response:** Found both statements. Identified all 3 changes plus enumerated 6 discrepancies: (1) cause of injuries, (2) Marcus's presence, (3) 4.5-hour delay before seeking medical attention, (4) rough handling history, (5) single vs. multiple injury events, (6) internal inconsistency. The 4.5-hour delay calculation (9:30 PM → 2:00 AM) is a value-add no other agent provided. Source citations: Medical Records Nursing Notes p. 9, Sheriff Report pp. 6-8.

**Score:** 3/3 changes | Progression noted: No | Extra: 6 discrepancies, timing delay analysis

---

#### DSS Legal (SP/PDF) - Com
> **Prompt:** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

**Sources cited:** DSS_Investigation_Report.pdf, Sheriff_Report_24-06-4418.pdf (2 references)

**Response:** Most comprehensive document agent response. Found all 3 changes with detailed narrative. Unique details not surfaced by other agents: (1) Dena admitted being "scared" and not wanting to "get anyone in trouble" — the motive for initial omission, (2) Dena's inference that Marcus "was responsible," (3) demeanor shift from "nervous, brief, avoidant" to "emotional, more forthcoming." Included a summary comparison table (Aspect / Initial / Later) covering 6 dimensions. Two-source cross-reference.

**Score:** 3/3 changes | Progression noted: No | Best document agent — richest analysis, fear motive, summary table

---

#### DSS Legal (SP/DOCX) - Com
> **Prompt:** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

**Sources cited:** DSS_Investigation_Report.docx, Sheriff_Report_24-06-4418.docx (2 references)

**Response:** Closely matches SP/PDF-Com quality. All 3 changes found. Same fear motive details ("scared," "didn't want to get anyone in trouble"). Summary comparison table with 5 dimensions. Added legal framing: "These changes were considered material by investigators and the court." Two-source cross-reference. Only minor gap vs. SP/PDF-Com: no explicit "Dena believed Marcus was responsible" inference.

**Score:** 3/3 changes | Progression noted: No | "Material" legal framing, summary table

---

#### DSS Legal (KB/PDF) - Com
> **Prompt:** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

**Sources cited:** DSS_Investigation_Report - 2024-dr-42-0892.pdf (1 reference)

**Response:** Found all 3 changes. Included direct quote of rough handling statement ("Marcus has a temper. He gets frustrated when Jaylen won't stop crying..."). Unique detail: Dena "expressed a desire for Jaylen to be placed with her mother for safety" — a grandmother placement wish not surfaced by any other agent. Noted demeanor shift from non-disclosing to forthcoming. Single source only.

**Score:** 3/3 changes | Progression noted: No | Unique: grandmother placement wish

---

#### DSS Legal (KB/DOCX) - Com
> **Prompt:** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

**Sources cited:** DSS_Investigation_Report - dr-42-0892.docx, Medical_Records - dr-42-0892.docx, Sheriff_Report_24-06-4418 - dr-42-0892.docx (3 references)

**Response:** Strongest KB agent on this prompt. All 3 changes found with direct quotes from both statements. **Only document agent to cite 3 source docs** — DSS Investigation Report, Medical Records, and Sheriff Report. Unique Medical Records detail: Dena "hesitated when asked about recent injuries or falls, responding 'I don't think so' without further detail." This hospital-side detail adds nuance to the statement evolution that single-source agents missed. Also noted the later statement was "inconsistent with Webb's account" — cross-referencing Marcus's version.

**Score:** 3/3 changes | Progression noted: No | Best KB agent — 3 sources, direct quotes, Medical Records detail

---

#### DSS Legal (SP/PDF) - GCC
> **Prompt:** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

**Sources cited:** DSS_Investigation_Report.pdf (1 reference)

**Response:** Found all 3 changes. Noted demeanor details (nervous, avoided eye contact). Minor date confusion: labeled initial statement as "June 13, 2024, 9:00 AM" which is actually the Dawson case manager interview, not the hospital statement (June 12). Content is correct — this is the interview where Dena still gave the hospital version. Single source doc.

**Score:** 3/3 changes | Progression noted: No | Minor: conflated hospital and case manager interview dates

---

#### DSS Legal (SP/DOCX) - GCC
> **Prompt:** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

**Sources cited:** DSS_Investigation_Report.docx, Court_Orders_and_Filings.docx (2 references)

**Response:** Found all 3 changes. Added an analytical category ("Responsibility and Awareness") noting the shift from "in the bedroom all evening" to acknowledging hearing a noise and calling out — framing the change as increased admission of awareness. Two-source cross-reference.

**Score:** 3/3 changes | Progression noted: No

---

#### DSS Legal (KB/PDF) - GCC
> **Prompt:** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

**Sources cited:** DSS_Investigation_Report - 2024-dr-42-0892.pdf, Court_Orders_and_Filings - 2024-dr-42-0892.pdf (2 references)

**Response:** Found all 3 changes. Noted demeanor shift ("initial statement was more vague and less accusatory, later statement provided more context and concern"). Compact analysis. Two references.

**Score:** 3/3 changes | Progression noted: No

---

#### DSS Legal (KB/DOCX) - GCC
> **Prompt:** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"

**Sources cited:** DSS_Investigation_Report - dr-42-0892.docx, Court_Orders_and_Filings - dr-42-0892.docx (2 references)

**Response:** Most detailed demeanor analysis of any agent. Organized initial statement with category labels (Presence, Incident, Belief, Concerns, Demeanor) — useful for attorney review. Found all 3 changes. Noted "did not ask any questions about the investigation process, which was unusual" — a behavioral observation unique to this agent. Two references.

**Score:** 3/3 changes | Progression noted: No | Most structured format for initial statement

---

#### Prompt 7 Key Findings

1. **10 of 11 agents found all 3 changes** — the strongest consensus across any prompt tested. Statement comparison is a relative strength for all architectures.
2. **MCP - Com the only miss** — omitted rough handling / temper history. Likely a comprehension gap rather than retrieval failure, since the statement data should have been returned by `get_statements_by_person`. This is the first time MCP - Com underperformed the Web SPA on the same structured data.
3. **No agent noted the intermediate case manager progression** (hospital → Dawson interview → LE interview). All treated it as a two-stage comparison. The Dawson interview (June 13, 9 AM) still matched the hospital version — the change only came under LE questioning that afternoon. This three-stage evolution is a nuance that would matter to an attorney.
4. **SP/PDF - Com and SP/DOCX - Com strongest document agents** — summary tables, fear motive ("scared," "didn't want to get anyone in trouble"), demeanor shifts. SP/PDF-Com also surfaced Dena's inference that Marcus "was responsible."
5. **KB/DOCX - Com was the strongest KB agent** — the only document agent to cite 3 source docs (DSS + Medical + Sheriff). Surfaced unique Medical Records detail about Dena hesitating when asked about prior injuries.
6. **Web SPA was the strongest MCP agent** — direct quotes, page citations, and the only agent to reference a numbered discrepancy record (Discrepancy 6) from the database.
7. **MCP - GCC added the most analytical value** — enumerated 6 discrepancies and calculated the 4.5-hour delay (9:30 PM → 2:00 AM). No other agent quantified the timing gap.
8. **Zero hallucinations across all agents** — every cited fact was accurate. This prompt had the highest fidelity of any tested.
9. **Several doc agents conflated hospital and case manager interviews** — dating the "initial" statement as June 13, 9:00 AM (Dawson) rather than June 12 (hospital). Minor confusion but not factually wrong since the content matched.

---

### Results — Prompt 8 (LE Statements Filter)

> **Critical context:** The MCP tool `get_statements_by_person` requires a `person_name` parameter — there is no audience/`made_to` filter. To answer "what statements were made to law enforcement," an MCP agent would need to (1) identify each person involved, (2) call `get_statements_by_person` for each, (3) filter results by `made_to = 'Law Enforcement'`. Document agents have a structural advantage: the Sheriff Report IS the law enforcement interview record — no filtering needed.

#### Summary Table

| Agent | LE Content (of 4) | False Positives | 8 PM Error | Key Issue |
|---|---|---|---|---|
| Web SPA | **0/4** | 0 | — | FAIL — tool can't filter by audience |
| MCP - Com | **0/4** | 0 | — | FAIL — 3 tries, all failed |
| MCP - GCC | 2/4 | 1 | No | Pivoted to timeline events (workaround) |
| SP/PDF - Com | 4/4 | Low | No | Best — 3 sources, direct quotes, structured |
| SP/DOCX - Com | 4/4 | Moderate | No | **Only agent ever to note intermediate interview**, 4 sources |
| KB/PDF - Com | 4/4 | Moderate | Yes | Unique DSS follow-up quotes from both parents |
| KB/DOCX - Com | 4/4 | Low | Yes | Most detailed Marcus interview, unique clarification quote |
| SP/PDF - GCC | **0/4** | 2 | — | FAIL — returned court testimony instead of LE |
| SP/DOCX - GCC | 0.5/4 | 2 | No | Filtering failure — returned hospital versions |
| KB/PDF - GCC | 4/4 | 1 | Yes | Best GCC agent — direct quotes |
| KB/DOCX - GCC | 4/4 | 1 | No | Strong, no 8 PM error |

#### DSS Legal (Web)
> **Prompt:** "What statements were made to law enforcement in case 2024-DR-42-0892?"

**Tools called:** `get_statements_by_person`

**Response:** "There are no recorded statements made to law enforcement in case 2024-DR-42-0892."

**Analysis:** Total failure. The tool requires a person name, not an audience filter. The Web SPA likely tried to query for "law enforcement" as a person or couldn't determine which people to query. The SQL `statements` table has 4 records with `made_to = 'Law Enforcement'`, but the tool doesn't expose that filter.

**Score:** 0/4 statements | False positives: 0 | Missing: 4 | **Tool design limitation**

---

#### DSS Legal (MCP) - Com
> **Prompt:** "What statements were made to law enforcement in case 2024-DR-42-0892?"

**Response:** Failed on all 3 attempts. First and third: "No statements made to law enforcement are recorded." Second: "Please provide the full or partial name of the person whose statements you would like to retrieve." The orchestrator couldn't figure out how to decompose the question into per-person tool calls.

**Score:** 0/4 statements | False positives: 0 | Missing: 4 | **Orchestrator failure — couldn't decompose the query**

---

#### DSS Legal (MCP) - GCC
> **Prompt:** "What statements were made to law enforcement in case 2024-DR-42-0892?"

**Response:** Pivoted to timeline events instead of statements — a smart workaround. Returned 3 LE-related timeline entries: (1) Lt. Odom responds to hospital (June 12, 11 AM), (2) Marcus Webb interview (June 13, 1:30 PM), (3) Dena Holloway interview (June 13, 4:00 PM). Marcus's interview content covers Statement A (couch, didn't hear, crib climbing). Dena's covers Statement C (9:30 PM thump, account change). Missing: Marcus's confrontation quote (Statement B) and Dena's rough handling disclosure (Statement D). Lt. Odom at hospital is a false positive (LE action, not a statement TO LE).

**Score:** 2/4 statements | False positives: 1 (LE action at hospital) | Missing: 2 (confrontation, rough handling) | **Adaptive but incomplete**

---

#### DSS Legal (SP/PDF) - Com
> **Prompt:** "What statements were made to law enforcement in case 2024-DR-42-0892?"

**Sources cited:** Sheriff_Report_24-06-4418.pdf, DSS_Investigation_Report.pdf, Court_Orders_and_Filings.pdf (3 references)

**Response:** Structured response with 4 numbered sections: (1) Initial parental accounts as context, (2) Dena's revised statement to Lt. Odom with full direct quote of rough handling, (3) Marcus's statement with confrontation quote, (4) Medical/LE observations. All 4 LE statement contents present. Includes summary of LE findings. 10 PM bedtime correctly attributed to Marcus. Three-source cross-reference.

**Score:** 4/4 statements | False positives: ~2 (initial accounts + medical observations, but well-contextualized) | 8 PM error: No | **Best structured response**

---

#### DSS Legal (SP/DOCX) - Com
> **Prompt:** "What statements were made to law enforcement in case 2024-DR-42-0892?"

**Sources cited:** Medical_Records.docx, DSS_Investigation_Report.docx, Court_Orders_and_Filings.docx, Sheriff_Report_24-06-4418.docx (4 references)

**Response:** 5 numbered sections including: (1) Initial parental accounts, (2) **Hospital interview with Dena (June 13, 9:00 AM)** — the intermediate Dawson case manager interview that NO other agent across ALL prompts has ever identified as a separate step, (3) Dena's revised LE statement, (4) Marcus's LE statement at 1:30 PM, (5) Nursing staff observations (Patricia Daniels, grip-pattern bruising). All 4 LE statement contents present. Most source documents (4) of any agent on this prompt.

**Score:** 4/4 statements | False positives: ~3 (initial, hospital interview, nursing — but intermediate interview is a genuine insight) | 8 PM error: No | **Only agent to identify three-stage statement progression**

---

#### DSS Legal (KB/PDF) - Com
> **Prompt:** "What statements were made to law enforcement in case 2024-DR-42-0892?"

**Sources cited:** Sheriff_Report_24-06-4418 - 2024-dr-42-0892.pdf, DSS_Investigation_Report - 2024-dr-42-0892.pdf (2 references)

**Response:** Most detailed Marcus interview of any Com agent — evening routine (5:30 PM arrival, dinner, bath), denial of striking, "normal couple stuff," bruising question, confrontation quote. Dena's hospital statement labeled correctly, then revised statement with full direct quote. **Unique detail:** June 14 DSS follow-up statements from BOTH parents (Marcus: "I love my son. I want to cooperate." Dena: "I want Jaylen to be safe. If my mama can take him, that would be best right now.") — only agent to surface these. However, DSS follow-ups are NOT statements to law enforcement (made_to = 'Case Manager'), so these are false positives. **8 PM bedtime** attributed to Marcus's own account.

**Score:** 4/4 statements | False positives: ~2 (hospital + DSS follow-ups) | 8 PM error: Yes | **Most narrative detail, unique DSS follow-ups**

---

#### DSS Legal (KB/DOCX) - Com
> **Prompt:** "What statements were made to law enforcement in case 2024-DR-42-0892?"

**Sources cited:** Sheriff_Report_24-06-4418 - dr-42-0892.docx, DSS_Investigation_Report - dr-42-0892.docx (2 references)

**Response:** Most detailed Marcus interview across ALL agents — includes everything KB/PDF-Com found plus a unique additional quote: "I just assumed that's what she's saying because she's been trying to blame me for things lately." This clarification after the confrontation quote was not surfaced by any other agent. Dena's initial labeled correctly, revised statement with full direct quote. LE findings summary with grip-pattern bruising. **8 PM bedtime** attributed to Marcus.

**Score:** 4/4 statements | False positives: ~1.5 (initial + LE findings section) | 8 PM error: Yes | **Most detailed single interview of any agent, unique Marcus clarification**

---

#### DSS Legal (SP/PDF) - GCC
> **Prompt:** "What statements were made to law enforcement in case 2024-DR-42-0892?"

**Sources cited:** Court_Orders_and_Filings.pdf (1 reference)

**Response:** Returned Renee Dawson's court testimony ("child is at imminent risk") and Dr. Chowdhury's medical testimony. **Neither is a statement made to law enforcement** — both are court/medical testimony misidentified as LE statements. Zero actual LE content.

**Score:** 0/4 statements | False positives: 2 (court testimony confused as LE) | **FAIL — misunderstood the question**

---

#### DSS Legal (SP/DOCX) - GCC
> **Prompt:** "What statements were made to law enforcement in case 2024-DR-42-0892?"

**Sources cited:** DSS_Investigation_Report.docx (1 reference)

**Response:** Returned Marcus's and Dena's **initial hospital/general statements**, not their law enforcement interview statements. Marcus: "put Jaylen to bed at approximately 10:00 PM, fell asleep on couch" (hospital version). Dena: "heard crying at 2 AM, believed crib fall" (hospital version). Missing: 9:30 PM thump revision, crib climbing detail, confrontation, rough handling. Notes "inconsistencies" but doesn't provide LE-specific content.

**Score:** 0.5/4 statements | False positives: 2 (hospital versions presented as LE) | **Filtering failure — correct people, wrong audience**

---

#### DSS Legal (KB/PDF) - GCC
> **Prompt:** "What statements were made to law enforcement in case 2024-DR-42-0892?"

**Sources cited:** DSS_Investigation_Report - 2024-dr-42-0892.pdf, Sheriff_Report_24-06-4418 - 2024-dr-42-0892.pdf (2 references)

**Response:** Best GCC agent on this prompt. Marcus interview detailed: couch all night, crib climbing, denied rough handling, confrontation quote ("not in his room after 10 PM"), bruising question, denial of striking, "normal couple stuff." Also includes Sheriff Report's evening routine detail (5:30 PM, dinner, bath, **8 PM bedtime**). Dena: hospital statement labeled, then revised statement with full direct quote including "should have said something sooner." Two-source cross-reference.

**Score:** 4/4 statements | False positives: 1 (hospital statement, labeled) | 8 PM error: Yes (in evening routine section) | **Best GCC agent**

---

#### DSS Legal (KB/DOCX) - GCC
> **Prompt:** "What statements were made to law enforcement in case 2024-DR-42-0892?"

**Sources cited:** Court_Orders_and_Filings - dr-42-0892.docx, DSS_Investigation_Report - dr-42-0892.docx (2 references)

**Response:** Strong coverage. Marcus: couch all night, crib climbing, denied rough handling, confrontation quote, 10 PM bedtime (**no 8 PM error**). Dena: initial labeled, revised with 9:30 PM thump, rough handling, and direct quote. Notes discrepancies between parents' statements and medical findings. Two references.

**Score:** 4/4 statements | False positives: 1 (initial statement, labeled) | 8 PM error: No | **Strong and clean**

---

#### Prompt 8 Key Findings

1. **MCP tools have a critical design gap** — `get_statements_by_person` requires a person name and has no `made_to` filter. Both GPT-4.1 MCP agents (Web SPA + MCP-Com) returned NOTHING — the first prompt where MCP agents completely fail on a question the SQL data can answer. MCP-GCC showed adaptive behavior by pivoting to timeline events, but got only 2/4 statement contents.

2. **This prompt inverts the usual MCP advantage.** Document agents with access to the Sheriff Report have a structural advantage — the document IS the law enforcement interview record, so the "filtering" is implicit in the source. The SQL data has a `made_to` field that could answer this perfectly, but the tool API doesn't expose it.

3. **All 4 Commercial doc agents found all 4 LE statement contents.** SP/PDF-Com best structured (3 sources); SP/DOCX-Com most sources (4) and the only agent across all 8 prompts to identify the intermediate Dawson interview; KB agents most detailed individual interview accounts.

4. **GCC doc agents split again.** KB agents (both 4/4) succeeded; SP agents failed (0/4 and 0.5/4). This confirms the persistent GCC SharePoint retrieval weakness.

5. **SP/DOCX-Com's intermediate interview identification is a first.** The Dawson case manager interview (June 13, 9 AM) has been in the ground truth since Prompt 7 as a bonus element. SP/DOCX-Com is the first and only agent to ever surface it.

6. **8 PM error recurred** in KB/PDF-Com, KB/DOCX-Com, and KB/PDF-GCC — all from the Sheriff Report's account of the evening routine. The error correlates with agents that retrieve the full Sheriff Report detail.

7. **Tool design recommendation:** Adding a `get_statements` tool with optional `made_to` filter (or making `person_name` optional in `get_statements_by_person`) would fix the MCP gap. This is a schema/API issue, not a model issue.

---

### Results — Prompt 9 (TPR Aggregate)

#### DSS Legal (Web)
> **Prompt:** "Which cases involve Termination of Parental Rights?"

**Response:** Listed all 9 TPR cases with case IDs, case titles, counties, filed dates, and statuses. Concise tabular format. Used `list_cases` tool.

**Score:** 9/9 cases | Correct count: Yes | **Pass**

---

#### DSS Legal (MCP) - Com
> **Prompt:** "Which cases involve Termination of Parental Rights?"

**Response:** Listed all 9 TPR cases with full summaries including children's names/ages, removal reasons, treatment plan requirements, and current status. Clean organization by case.

**Score:** 9/9 cases | Correct count: Yes | **Pass**

---

#### DSS Legal (MCP) - GCC
> **Prompt:** "Which cases involve Termination of Parental Rights?"

**Response:** Listed all 9 TPR cases with detailed summaries. Richest detail of the three MCP agents — includes circuit information, full treatment plan items, and case outcomes for closed/dismissed cases.

**Score:** 9/9 cases | Correct count: Yes | **Pass**

---

#### DSS Legal (SP/PDF) - Com
> **Prompt:** "Which cases involve Termination of Parental Rights?"

**Response:** Found Price case (Case 2) with detailed TPR grounds (neglect, failure to remedy, substance abuse), full procedural history (7 orders listed chronologically), father's voluntary relinquishment, and current foster care status. **Also identified Webb/Holloway (Case 1)** as potential TPR — "TPR proceedings may be considered depending on the outcome of the investigation and subsequent hearings." Summary of TPR grounds. 4 references across both cases.

**Score:** 1/9 actual TPR cases | Flagged 1 CPS case as potential TPR (reasonable inference) | **Partial** — best document agent, but aggregate queries require structured data

---

#### DSS Legal (SP/DOCX) - Com
> **Prompt:** "Which cases involve Termination of Parental Rights?"

**Response:** Found Price case with detailed procedural history and **cited actual statutory grounds** (S.C. Code Ann. §63-7-2570(1), (2), (4)). Also identified Webb/Holloway case as removal/TPR consideration with "non-accidental trauma, inconsistent parental accounts, imminent risk of harm." 5 references across multiple documents.

**Score:** 1/9 actual TPR cases | Flagged 1 CPS case as potential TPR | **Partial** — statutory citations are a genuine value-add

---

#### DSS Legal (KB/PDF) - Com
> **Prompt:** "Which cases involve Termination of Parental Rights?"

**Response:** Found Price case only. Good detail — children's DOBs, grounds, procedural history (4 orders), GAL recommendation. 2 references (Court_Orders, TPR_Petition).

**Score:** 1/9 cases | **Partial** — accurate within scope, no acknowledgment of limitation

---

#### DSS Legal (KB/DOCX) - Com
> **Prompt:** "Which cases involve Termination of Parental Rights?"

**Response:** Found Price case only. Detailed grounds (neglect, failure to remedy, substance abuse), voluntary relinquishment, foster care status, merits hearing. 1 reference.

**Score:** 1/9 cases | **Partial** — accurate within scope

---

#### DSS Legal (SP/PDF) - GCC
> **Prompt:** "Which cases involve Termination of Parental Rights?"

**Response:** Generic framing — "Cases involving Termination of Parental Rights typically include..." Lists TPR grounds (neglect, failure to remedy, substance abuse) and gives Price case as example. 1 reference.

**Score:** 1/9 cases | **Partial** — treats aggregate question as generic legal question

---

#### DSS Legal (SP/DOCX) - GCC
> **Prompt:** "Which cases involve Termination of Parental Rights?"

**Response:** Found Price case with detail on both Crystal Price and Brandon Price's proceedings. 1 reference.

**Score:** 1/9 cases | **Partial** — accurate within scope

---

#### DSS Legal (KB/PDF) - GCC
> **Prompt:** "Which cases involve Termination of Parental Rights?"

**Response:** Found Price case with good detail — children, DOBs, grounds, GAL recommendation (Thomas Reed, Esq.), active processing status. 3 references.

**Score:** 1/9 cases | **Partial** — best GCC document agent detail

---

#### DSS Legal (KB/DOCX) - GCC
> **Prompt:** "Which cases involve Termination of Parental Rights?"

**Response:** Found Price case with detailed procedural history — all 6 orders listed chronologically. Termination grounds, GAL recommendation, court orders. 3 references.

**Score:** 1/9 cases | **Partial** — strongest procedural detail of any document agent

---

#### Prompt 9 — Summary

| Agent | TPR Cases Found | Grade | Notes |
|---|---|---|---|
| Web SPA | 9/9 | **Pass** | Concise list, all case IDs |
| MCP - Com | 9/9 | **Pass** | Full summaries per case |
| MCP - GCC | 9/9 | **Pass** | Richest detail |
| SP/PDF - Com | 1/9 + 1 flagged | Partial | Also flagged CPS case as potential TPR |
| SP/DOCX - Com | 1/9 + 1 flagged | Partial | Statutory citations (§63-7-2570) |
| KB/PDF - Com | 1/9 | Partial | Good detail |
| KB/DOCX - Com | 1/9 | Partial | Grounds + voluntary relinquishment |
| SP/PDF - GCC | 1/9 | Partial | Generic framing |
| SP/DOCX - GCC | 1/9 | Partial | Both parents covered |
| KB/PDF - GCC | 1/9 | Partial | GAL recommendation detail |
| KB/DOCX - GCC | 1/9 | Partial | Best procedural chronology |

**Key findings:**
- **MCP agents sweep** — all 3 found all 9 TPR cases. This is the clearest architectural advantage: aggregate queries across the full case database are trivial with SQL, impossible with limited document corpora.
- **All 8 document agents scored Partial** — they correctly found the 1 TPR case in their corpus (Price) with accurate detail, but missed 8 others. No hallucinated cases, no misclassifications.
- **SP-Com agents showed value-add** by flagging Webb/Holloway (CPS) as potential TPR based on the facts (non-accidental trauma, imminent risk). SP/DOCX-Com cited actual SC statutory grounds — useful for attorneys.
- **No document agent acknowledged the limitation** — none said "I can only see documents for 2 cases." This is a silent coverage gap that could mislead an attorney into thinking there's only 1 TPR case.
- **Zero hallucinations** across all 11 agents — no fabricated cases, no misclassified case types.

---

### Results — Prompt 10 (Time Gap)

#### DSS Legal (Web)
> **Prompt:** "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

**Response:** Conflated the 9:30 PM thump with the 2:00 AM discovery: "Dena Holloway reported hearing Jaylen crying loudly (associated with the thump) at approximately 2:00 AM." Calculated gap as 1 hour 15 minutes (2:00 AM → 3:15 AM). The SQL timeline has both events separately — the model merged them. Missed the clinically significant 4.5-hour delay entirely.

**Score:** 9:30 PM identified: **No** (said 2:00 AM) | 3:15 AM identified: Yes | Gap: **1h15m (wrong — discovery→ER, not thump→ER)** | Distinguished discovery vs ER: No | **Fail** — missed the entire 4.5-hour delay

---

#### DSS Legal (MCP) - Com
> **Prompt:** "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

**Response:** Gold standard. Identified all three milestones (9:30 PM thump, 2:00 AM discovery, 3:15 AM ER admission). Calculated both intervals: thump→discovery = 4h30m, thump→ER = 5h45m. Summary table with all three time points. Cited Sheriff Report, Dictation PDF, and Medical Records.

**Score:** 9:30 PM identified: Yes | 3:15 AM identified: Yes | Gap: **4h30m + 5h45m (both correct)** | Distinguished discovery vs ER: **Yes** | **Pass**

---

#### DSS Legal (MCP) - GCC
> **Prompt:** "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

**Response:** Correctly identified 9:30 PM thump and 2:00 AM hospital departure. But reported gap as "approximately 4 hours" — should be 4h30m. Did not mention 3:15 AM admission. For a question asking for the "exact" gap, being 30 minutes off is notable.

**Score:** 9:30 PM identified: Yes | 3:15 AM identified: No | Gap: **~4h (should be 4.5h)** | Distinguished discovery vs ER: No | **Partial** — correct start, imprecise arithmetic

---

#### DSS Legal (SP/PDF) - Com
> **Prompt:** "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

**Response:** Excellent. Identified 9:30 PM thump. Distinguished between "2:00 AM" (initial statements to medical staff) and "3:15 AM" (actual admission records). Reported "approximately four-and-one-half hour delay." Noted the delay was "clinically concerning by medical staff and DSS investigators." 3 references (Medical Records, Court Orders, DSS Investigation).

**Score:** 9:30 PM identified: Yes | 3:15 AM identified: Yes | Gap: **4.5h (correct for thump→departure)** | Distinguished 2:00 AM vs 3:15 AM: **Yes** | **Pass**

---

#### DSS Legal (SP/DOCX) - Com
> **Prompt:** "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

**Response:** Most precise answer. Identified 9:30 PM thump and 3:15 AM admission. Calculated "about 5 hours and 45 minutes" (thump→admission). Also noted midnight discovery as intermediate event. "Medical staff noted the delay… as concerning." 3 references.

**Score:** 9:30 PM identified: Yes | 3:15 AM identified: Yes | Gap: **5h45m (correct for thump→admission)** | Distinguished discovery vs ER: Yes (midnight discovery noted) | **Pass**

---

#### DSS Legal (KB/PDF) - Com
> **Prompt:** "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

**Response:** Identified 9:30 PM thump and midnight discovery. Calculated thump→discovery = 2h30m. However, admitted "the precise admission time is not stated in the available reports" and noted hospital visit was "shortly after midnight." Honest about limitation. 1 reference (Sheriff Report only).

**Score:** 9:30 PM identified: Yes | 3:15 AM identified: No (honest absence) | Gap: **2h30m (thump→discovery only)** | Distinguished discovery vs ER: No — couldn't find ER time | **Partial** — honest about missing data, but only answered half the question

---

#### DSS Legal (KB/DOCX) - Com
> **Prompt:** "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

**Response:** Identified 9:30 PM thump and 2:00 AM hospital presentation. Calculated "approximately four-and-a-half hours." 1 reference (Court_Orders_and_Filings).

**Score:** 9:30 PM identified: Yes | 3:15 AM identified: No | Gap: **4.5h (correct for thump→hospital departure)** | Distinguished discovery vs ER: No | **Pass**

---

#### DSS Legal (SP/PDF) - GCC
> **Prompt:** "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

**Response:** Identified 9:30 PM correctly but **hallucinated 7:30 AM** as hospital time. Calculated gap as "approximately 10 hours." No source in any document says 7:30 AM. 2 references (GAL_Report.pdf, Medical_Records.pdf).

**Score:** 9:30 PM identified: Yes | 3:15 AM identified: No | Gap: **10 hours (WRONG — 7:30 AM is fabricated)** | Distinguished discovery vs ER: No | **Fail** — hallucinated hospital time

---

#### DSS Legal (SP/DOCX) - GCC
> **Prompt:** "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

**Response:** Identified 9:30 PM thump and 2:00 AM hospital arrival. Calculated "approximately 4.5 hours." 2 references (GAL_Report.docx, DSS_Investigation_Report.docx).

**Score:** 9:30 PM identified: Yes | 3:15 AM identified: No | Gap: **4.5h (correct for thump→hospital)** | Distinguished discovery vs ER: No | **Pass**

---

#### DSS Legal (KB/PDF) - GCC
> **Prompt:** "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

**Response:** Identified 9:30 PM thump but used 12:47 AM from Sheriff Report as hospital time (same discrepancy seen in Prompt 1 — Sheriff Report records different time than Medical Records). Calculated "approximately 3 hours and 17 minutes." Math is correct for the stated times, but the ER time is wrong.

**Score:** 9:30 PM identified: Yes | 3:15 AM identified: No (used 12:47 AM from Sheriff Report) | Gap: **3h17m (correct math, wrong source time)** | Distinguished discovery vs ER: No | **Partial** — consistent with Prompt 1 doc discrepancy

---

#### DSS Legal (KB/DOCX) - GCC
> **Prompt:** "What was the exact time gap between the thump Dena heard and when they took Jaylen to the hospital?"

**Response:** Identified 9:30 PM thump and "approximately midnight" as discovery time. Calculated "approximately 2.5 hours." But the question asked about hospital, not discovery. Did not find or report the actual ER time. 1 reference (Sheriff Report only).

**Score:** 9:30 PM identified: Yes | 3:15 AM identified: No | Gap: **2.5h (thump→discovery, not thump→hospital)** | Distinguished discovery vs ER: No — answered wrong event | **Partial** — correct start time, answered discovery not hospital

---

#### Prompt 10 — Summary

| Agent | Thump Time | Hospital Time | Gap Reported | Grade |
|---|---|---|---|---|
| Web SPA | 2:00 AM ❌ | 3:15 AM | 1h15m (wrong start) | **Fail** |
| MCP - Com | 9:30 PM ✓ | 2:00 AM + 3:15 AM | 4h30m + 5h45m ✓ | **Pass** |
| MCP - GCC | 9:30 PM ✓ | 2:00 AM | ~4h (imprecise) | Partial |
| SP/PDF - Com | 9:30 PM ✓ | 2:00 AM + 3:15 AM | ~4.5h ✓ | **Pass** |
| SP/DOCX - Com | 9:30 PM ✓ | 3:15 AM | 5h45m ✓ | **Pass** |
| KB/PDF - Com | 9:30 PM ✓ | "shortly after midnight" | 2h30m (thump→discovery) | Partial |
| KB/DOCX - Com | 9:30 PM ✓ | 2:00 AM | ~4.5h ✓ | **Pass** |
| SP/PDF - GCC | 9:30 PM ✓ | **7:30 AM** ❌ | **10h (fabricated)** | **Fail** |
| SP/DOCX - GCC | 9:30 PM ✓ | 2:00 AM | ~4.5h ✓ | **Pass** |
| KB/PDF - GCC | 9:30 PM ✓ | 12:47 AM (Sheriff Rpt) | ~3h17m | Partial |
| KB/DOCX - GCC | 9:30 PM ✓ | ~midnight (discovery) | ~2.5h (wrong event) | Partial |

**Key findings:**
- **MCP-Com produced the gold standard** — the only agent to identify all three milestones (9:30 PM, 2:00 AM, 3:15 AM) and calculate both intervals. GPT-4.1 excelled at arithmetic reasoning here.
- **Web SPA failed despite having the data** — conflated the 9:30 PM thump with the 2:00 AM discovery, reporting 1h15m instead of 4.5–5.75h. The SQL timeline has both events as separate rows. This is a comprehension error, not a retrieval error.
- **SP/PDF-GCC hallucinated 7:30 AM** — no document contains this time. Continues its pattern as the weakest agent.
- **10/11 agents correctly identified 9:30 PM** as the thump time — only the Web SPA missed it.
- **SP/PDF-Com and SP/DOCX-Com both distinguished 2:00 AM (departure) from 3:15 AM (admission)** — the kind of nuance attorneys need.
- **KB/PDF-GCC consistently uses Sheriff Report's 12:47 AM** — same document discrepancy as Prompt 1. Not a hallucination, but an unreliable source.
- **Arithmetic is a genuine weakness** — even agents that retrieved the right times sometimes rounded (MCP-GCC: "~4h" instead of 4.5h) or answered the wrong interval (KB/DOCX-GCC: thump→discovery instead of thump→hospital).
