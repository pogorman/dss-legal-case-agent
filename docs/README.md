# Documentation Index

## Deliverables

| File | Description |
|---|---|
| [executive-summary.pdf](executive-summary.pdf) | C-suite summary -- five-level accuracy framework, 304 test runs, zero abbreviations |
| [demo-guide.pdf](demo-guide.pdf) | Presenter guide -- five-level demo script, talking points, Q&A handling |
| [slide-outline.md](slide-outline.md) | 20-slide deck outline with key messages and visual suggestions |

## Reference

| File | Description |
|---|---|
| [architecture.md](architecture.md) | System architecture, data flow, networking, data provenance |
| [user-guide.md](user-guide.md) | How to use the demo application |
| [faqs.md](faqs.md) | Frequently asked questions from development sessions |
| [session-log.md](session-log.md) | Chronological log of development sessions |
| [erd.png](erd.png) | Entity relationship diagram |

## Sources (used to generate deliverables)

| File | Generates |
|---|---|
| [sources/executive-summary.md](sources/executive-summary.md) | executive-summary.pdf (via `scripts/generate-executive-pdf.py`) |
| [sources/demo-guide.md](sources/demo-guide.md) | demo-guide.pdf (via `scripts/generate-demo-guide-pdf.py`) |
| [sources/erd.mmd](sources/erd.mmd) | erd.png (Mermaid diagram source) |

## Archive (testing data and improvement logs)

| File | Description |
|---|---|
| [archive/use-case-1-testing.md](archive/use-case-1-testing.md) | UC1: Legal Case Analysis -- 11 agents, 10 prompts, 128 test runs |
| [archive/use-case-2-testing.md](archive/use-case-2-testing.md) | UC2: Investigative Analytics -- 8 agents, 10 prompts, 176 test runs |
| [archive/improvements/](archive/improvements/) | Round-by-round tool and data improvements |
| [archive/test-responses/](archive/test-responses/) | Raw agent responses organized by use case |

## Scripts

Utility scripts live in [`../scripts/`](../scripts/):

| File | Description |
|---|---|
| [generate-executive-pdf.py](../scripts/generate-executive-pdf.py) | Generates executive-summary.pdf from hardcoded content |
| [generate-demo-guide-pdf.py](../scripts/generate-demo-guide-pdf.py) | Generates demo-guide.pdf from sources/demo-guide.md |
| [sanitize-docs.py](../scripts/sanitize-docs.py) | Replaces real PII with synthetic data in source Word docs |
| [convert-md-to-docs.py](../scripts/convert-md-to-docs.py) | Converts sharepoint-docs markdown files to .docx and .pdf |
