# Documentation Index

## Core Documentation

| File | Description |
|---|---|
| [architecture.md](architecture.md) | System architecture, data flow, networking, data provenance |
| [user-guide.md](user-guide.md) | How to use the demo application |
| [faqs.md](faqs.md) | Frequently asked questions from development sessions |
| [session-log.md](session-log.md) | Chronological log of development sessions |

## Evaluation & Testing

| File | Description |
|---|---|
| [executive-summary.md](executive-summary.md) | C-suite summary — both use cases, zero abbreviations |
| [executive-summary.pdf](executive-summary.pdf) | PDF version of the executive summary |
| [use-case-1-testing.md](use-case-1-testing.md) | UC1: Legal Case Analysis — 11 agents, 10 prompts, 128 test runs |
| [use-case-2-testing.md](use-case-2-testing.md) | UC2: Investigative Analytics — 7 agents, 10 prompts, 146 test runs |
| [improvements/](improvements/) | Round-by-round tool and data improvements |
| [test-responses/](test-responses/) | Raw agent responses organized by use case |

## Demo Resources

| File | Description |
|---|---|
| [demo-guide.md](demo-guide.md) | Step-by-step demo script, talking points, data design framing, and discrepancy questions |
| [ogs-presenter-guide.pdf](ogs-presenter-guide.pdf) | Presenter quick-reference guide |

## Reference

| File | Description |
|---|---|
| [erd.mmd](erd.mmd) | Entity relationship diagram (Mermaid source) |
| [erd.png](erd.png) | Entity relationship diagram (rendered) |

## Scripts

Utility scripts live in [`../scripts/`](../scripts/):

| File | Description |
|---|---|
| [sanitize-docs.py](../scripts/sanitize-docs.py) | Replaces real PII with synthetic data in source Word docs |
| [convert-md-to-docs.py](../scripts/convert-md-to-docs.py) | Converts sharepoint-docs markdown files to .docx and .pdf |
| [generate-executive-pdf.py](../scripts/generate-executive-pdf.py) | Generates executive-summary.pdf from hardcoded content |
| [generate-presenter-guide.py](../scripts/generate-presenter-guide.py) | Generates ogs-presenter-guide.pdf |
| [generate-data-listing.js](../scripts/generate-data-listing.js) | Dumps full database contents to markdown (run on-demand) |
