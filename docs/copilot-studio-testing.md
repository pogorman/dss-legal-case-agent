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
