# Copilot Studio Testing — Response Comparison

## Overview

Five agent configurations were tested against the same question about Case 1 (`2024-DR-42-0892`). Three use the MCP server (`POST /mcp`) backed by structured SQL data. Two use Copilot Studio with the same markdown documents — one uploaded directly as knowledge, the other connected via a SharePoint document library.

| Agent | Backend | LLM Orchestration |
|---|---|---|
| GCC Copilot Studio | MCP tool (structured SQL) | GCC Copilot Studio runtime |
| Commercial Copilot Studio | MCP tool (structured SQL) | Commercial Copilot Studio runtime |
| Web SPA | `/chat` endpoint (structured SQL) | GPT-4.1 direct tool-calling loop |
| Commercial Copilot Studio (Knowledge) | Uploaded markdown documents | Commercial Copilot Studio RAG |
| Commercial Copilot Studio (SharePoint) | SharePoint document library with same markdown files | Commercial Copilot Studio RAG |

## Test Prompt

Asked about Jaylen Webb's emergency room admission — specifically the time and the admitting nurse.

## Ground Truth

The answer spans two data sources:

- **From SQL** (`timeline_events`): Jaylen Webb admitted at **3:15 AM** on June 12, 2024. Dr. Anita Chowdhury is the physician. Source: `Medical Records, pp. 1-4`. No nurse is stored.
- **From documents** (`sharepoint-docs/Case-2024-DR-42-0892/Medical_Records.md`): Nursing notes are authored by **Rebecca Torres, RN, BSN** — Emergency Department. She appears on multiple notes but was never modeled into the SQL schema.

Neither source alone has the complete answer.

## Responses

### GCC Copilot Studio (MCP tool)

> Jaylen Webb was brought to the emergency room at 2:00 AM on June 12, 2024. The admitting nurse's name is not specified in the available documents. The timeline and events related to the case can be found in the source documents: Dictation PDF, p. 4, and Medical Records, pp. 1-4.

### Commercial Copilot Studio (MCP tool)

> **Jaylen Webb Emergency Room Admission Details**
>
> Admission Time: Jaylen Webb was brought to the Spartanburg Medical Center emergency room at 3:15 AM on June 12, 2024. X-rays at admission revealed multiple fractures inconsistent with the reported mechanism of injury (Medical Records, pp. 1-4).
>
> Admitting Nurse: The available medical timeline and statements do not identify the admitting nurse by name. The medical records reference Dr. Anita Chowdhury as the attending physician, but no nurse is listed in the documented events (Medical Records, pp. 1-4).
>
> If you need further details or wish to search for a specific nurse's name in other documents, please let me know.

### Web SPA (GPT-4.1 via /chat endpoint)

> Jaylen Webb was admitted to the Spartanburg Medical Center Emergency Room on June 12, 2024, at 3:15 AM. The medical timeline identifies Dr. Anita Chowdhury as the physician assessing Jaylen Webb; however, the available summary does not specifically identify the admitting nurse. The event is sourced from "Medical Records, pp. 1-4."
>
> If you require the name of the admitting nurse, additional review of the complete medical record would be necessary. Currently, no specific nurse is named in the available DSS or medical summaries.
>
> Source: Medical Records, pp. 1-4 (cited in Medical Event Timeline for 2024-DR-42-0892).

### Commercial Copilot Studio (Knowledge — uploaded documents)

> Jaylen Webb was brought to the emergency room and admitted at Spartanburg Medical Center. The admitting nurse was Rebecca Torres, RN, BSN.
>
> *1 reference: Medical_Records.md*

### Commercial Copilot Studio (SharePoint document library)

> No information was found that could help answer this.
>
> I'm sorry, I'm not sure how to help with that. Can you try rephrasing?

## Comparison Matrix

| Dimension | GCC (MCP) | Commercial (MCP) | SPA (MCP) | Commercial (Knowledge) | Commercial (SharePoint) |
|---|---|---|---|---|---|
| **Admission time** | 2:00 AM — WRONG | 3:15 AM — correct | 3:15 AM — correct | Not provided | No results |
| **Admitting nurse** | "Not specified" | "Not identified" | "Not identified" | **Rebecca Torres, RN, BSN** — correct | No results |
| **Source citation** | Dictation PDF p. 4 (wrong) + Medical Records pp. 1-4 | Medical Records pp. 1-4 | Medical Records pp. 1-4 | Medical_Records.md | None |
| **Dr. Chowdhury mentioned** | No | Yes | Yes | No | No |
| **Overall accuracy** | Poor — hallucinated time and citation | Good (but incomplete) | Good (but incomplete) | Partial — found nurse, missed time | **Total failure** |

## Analysis

### GCC hallucinated the admission time

The MCP tool returns structured data with `event_time: "3:15 AM"`. GCC reported "2:00 AM" — a fabricated value. This suggests one of:

1. **Weaker/different orchestrator model** — GCC may use a different Azure OpenAI model version than Commercial Copilot Studio, leading to less faithful tool-result interpretation
2. **Tool call failure with fallback generation** — The MCP call may have failed silently, and the GCC orchestrator generated an answer from nothing (hallucinating with confidence)
3. **Context window or prompt differences** — GCC's Copilot Studio runtime may truncate or reformat tool results differently

### GCC also fabricated a source citation

"Dictation PDF, p. 4" does not correspond to the ER admission event. The correct and only source is "Medical Records, pp. 1-4". This reinforces that GCC either didn't receive clean tool output or the model garbled it.

### Commercial (MCP) and SPA are nearly identical

Both got the time right, both correctly noted the nurse isn't in the structured data, both cited Dr. Chowdhury as context, and both referenced the correct source. The only difference is presentation style. This makes sense — both hit the same MCP tools and the same SQL data. Quality depends on the orchestrating LLM, not the data layer.

### Knowledge-based agent found what structured data missed

The document-backed agent correctly identified Rebecca Torres as the nurse — a detail that exists in the Medical Records markdown but was never modeled into the SQL schema. However, it didn't return the admission time (3:15 AM), which is prominently in the same document. RAG retrieval likely chunked the document and surfaced the nursing notes section without the timeline section.

### SharePoint document library returned nothing

The same markdown files that worked when uploaded as knowledge produced zero results when connected as a SharePoint document library. This is a Copilot Studio indexing/retrieval problem, not a data problem.

The root cause is **two completely different indexing pipelines**:

| | Direct Upload (Knowledge) | SharePoint Document Library |
|---|---|---|
| **Indexing** | Copilot Studio processes files immediately at upload time — chunking, embedding, and storing in its own vector index | Depends on SharePoint's search index (Microsoft Search / Graph connector) with its own crawl schedule |
| **Chunking** | Copilot Studio's RAG pipeline controls chunk size, overlap, and embedding | Microsoft Search's content extraction pipeline — optimized for enterprise search, not RAG |
| **File format support** | Parses content directly regardless of format (md, txt, pdf, docx) | Crawler may skip or poorly parse `.md` files — SharePoint historically treats markdown as opaque or low-priority |
| **Latency** | Ready immediately after upload | Crawl delay ranges from minutes to hours; no guarantee of when (or whether) content is indexed |
| **Visibility** | You can see what's been uploaded and indexed | Opaque — no direct way to confirm what the crawler extracted from a given file |

When you upload files directly, Copilot Studio owns the entire pipeline from file bytes to vector embeddings. When you point at SharePoint, you're depending on Microsoft Search to have already crawled, extracted text from, and indexed those files — and for the Graph connector to surface that index to Copilot Studio's retrieval layer. For `.md` files, that chain likely broke at the extraction step.

**Potential fixes for the SharePoint path:**
- Convert `.md` files to `.docx` or `.pdf` before uploading to SharePoint
- Wait longer for the crawl to complete and retest
- Verify files appear in SharePoint search results directly (if they don't show up in SharePoint search, they won't show up in Copilot Studio either)

But this brittleness is exactly what the demo is meant to expose — "just put your docs in SharePoint" is not a reliable AI strategy without understanding the indexing pipeline underneath.

This is the worst outcome of all five — not a wrong answer, not a partial answer, but a complete inability to find information that is demonstrably present in the connected documents.

### Neither approach alone gave a complete answer

| Fact | MCP agents | Knowledge (uploaded) | SharePoint library |
|---|---|---|---|
| Admission time (3:15 AM) | 2 of 3 correct | Missed | No results |
| Admitting nurse (Rebecca Torres) | All 3 missed (not in SQL) | Correct | No results |
| Source citation | 2 of 3 correct | Correct | No results |

This is the most important takeaway: **structured and unstructured approaches are complementary, not competing** — and how you connect unstructured data matters enormously. The SQL schema captured the timeline with precision but didn't model every person mentioned in the documents. The uploaded knowledge search found the nurse but missed the timeline. The SharePoint-connected search found nothing at all from the same files.

## Demo Implications

This test reshapes the demo narrative from "structured is better" to something more nuanced:

1. **Structured data gives precision and consistency.** Three MCP-backed agents returned the same time from the same tool. The data is queryable, cross-referenceable, and fully cited.
2. **Unstructured documents preserve details that weren't modeled.** Rebecca Torres was a real detail in the medical records that the schema designers (us) didn't think to capture. In a real case, an attorney might need that name.
3. **How you connect documents matters as much as having them.** The same markdown files produced correct answers when uploaded as knowledge and zero answers from a SharePoint library. The retrieval pipeline — not just the data — determines whether the agent can find anything.
4. **GCC's hallucination remains the cautionary tale.** Even with structured data, the orchestrating LLM matters. GCC confidently stated "2:00 AM" — an attorney relying on this would have incorrect facts.
5. **The ideal system combines both.** MCP tools for structured queries (timelines, discrepancies, cross-party comparisons) plus document search for the long tail of details that didn't make it into the schema. This is a stronger sales message than "pick one."

## Test Date

2026-03-05
