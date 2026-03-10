# Documentation Index

## Deliverables (docs/pdf/)

All PDFs are generated from hardcoded Python scripts — no separate MD source files.
To update content, edit the script in `scripts/` and regenerate.

| File | Generator | Description |
|---|---|---|
| [pdf/improving-agents-whitepaper-v1.pdf](pdf/improving-agents-whitepaper-v1.pdf) | `scripts/generate-executive-pdf.py` | Whitepaper -- five-level accuracy framework, 380 test runs |
| [pdf/demo-guide.pdf](pdf/demo-guide.pdf) | `scripts/generate-demo-guide-pdf.py` | Presenter guide -- demo script, talking points, Q&A handling |
| [pdf/slide-outline.pdf](pdf/slide-outline.pdf) | `scripts/generate-slide-outline-pdf.py` | 21-slide deck outline with key messages and visual suggestions |
| [pdf/architecture.pdf](pdf/architecture.pdf) | `scripts/generate-architecture-pdf.py` | System architecture, data flow, networking, data provenance |
| [pdf/user-guide.pdf](pdf/user-guide.pdf) | `scripts/generate-user-guide-pdf.py` | How to use the demo application |
| [pdf/faqs.pdf](pdf/faqs.pdf) | `scripts/generate-faqs-pdf.py` | Frequently asked questions from development sessions |

## Reference

| File | Description |
|---|---|
| [session-log.md](session-log.md) | Chronological log of development sessions |
| [erd.png](erd.png) | Entity relationship diagram |
| [sources/erd.mmd](sources/erd.mmd) | Mermaid source for ERD |

## Archive (testing data and improvement logs)

| File | Description |
|---|---|
| [archive/use-case-1-testing.md](archive/use-case-1-testing.md) | UC1: Legal Case Analysis -- 11 agents, 10 prompts, 128 test runs |
| [archive/use-case-2-testing.md](archive/use-case-2-testing.md) | UC2: Investigative Analytics -- 8 agents, 10 prompts, 176 test runs |
| [archive/improvements/](archive/improvements/) | Round-by-round tool and data improvements |
| [archive/test-responses/](archive/test-responses/) | Raw agent responses organized by use case |
