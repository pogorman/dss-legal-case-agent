# AI Agent Accuracy Spectrum for Government

## Purpose

Government agencies are deploying AI agents across a wide range of use cases, from simple document lookup to legal case preparation. Not all use cases require the same level of accuracy, and not all agent architectures deliver it. This report presents a five-level accuracy framework based on 304 empirical test runs across 19 agent configurations and two government use cases, with specific recommendations for Government Community Cloud customers at each level.

## The Five Levels

### Level 1: Information Discovery

**"Help me find the right policy document."**

The simplest AI use case: retrieval-augmented generation over knowledge bases, frequently asked questions, and policy manuals. A wrong answer is a minor inconvenience because users can easily verify the result themselves.

**Who uses this:** Citizens on self-service portals, employees searching benefits information, new hires navigating onboarding materials.

**What works:** Out-of-the-box Copilot with SharePoint grounding. No custom engineering required. Model choice has minimal impact.

**Recommendation:** Deploy with minimal customization. Ensure document libraries have clean metadata and consistent naming. This is a quick win with low risk.

### Level 2: Summarization and Synthesis

**"Summarize this 100-page report for my briefing."**

Condensing lengthy documents into actionable summaries: meeting transcripts, legislative text, audit reports, policy analyses. A wrong answer wastes time and may cause misunderstanding, but the stakes are internal and the original document is available for verification.

**Who uses this:** Legislative staffers, program managers, policy analysts, agency leadership preparing for briefings, communications teams drafting public summaries.

**What we found:** Document-based agents (Copilot Studio with SharePoint grounding) scored 8 out of 10 on both use cases with zero customization. GPT-4o and GPT-4.1 performed identically at this level. The task is simple enough that model capability is not the differentiator.

**Recommendation:** Copilot Studio with SharePoint document libraries. Invest in document hygiene (consistent formatting, meaningful filenames, metadata tags) rather than custom engineering. This is where most agencies should start.

### Level 3: Operational Decision Support

**"Show me the portfolio-level picture."**

Multi-source data aggregation, dashboards-via-conversation, workload triage, and pattern detection. A wrong answer misallocates resources but is verifiable against existing reports and dashboards.

**Who uses this:** Case worker supervisors, property inspection managers, program directors, budget analysts, operations staff monitoring workloads.

**What we found:** Aggregate queries (portfolio summaries, citywide statistics, workload counts) worked reliably across all agent types in our evaluation, including the weakest performers. When asked "How many properties does GEENA LLC own?" or "How many active cases does DSS have?", every agent architecture returned correct answers. This is where Model Context Protocol agents begin to outperform document agents because live structured data delivers answers that static documents cannot.

**Recommendation:** Connect agents to structured data sources (databases, APIs) via Model Context Protocol rather than relying solely on document search. Write clear tool descriptions that explain what each data source contains. Add summary modes for tools that can return large result sets to prevent token overflow.

### Level 4: Investigative and Analytical

**"Cross-reference these records and find what doesn't add up."**

Timeline reconstruction, discrepancy detection, entity resolution across multiple data sources, pattern analysis across large datasets. A wrong answer means missed evidence, false leads, and misdirected investigations.

**Who uses this:** Fraud investigators, auditors, compliance officers, legal researchers, child welfare investigators, property inspectors analyzing ownership networks.

**What we found:** This is where accuracy diverges dramatically based on engineering decisions.

**The model gap:** GPT-4.1 agents averaged 9.5 out of 10. The GPT-4o agent scored 4 out of 10. Same tools, same data, same backend. The tool improvements that lifted one agent from 1 out of 10 to a perfect 10 out of 10 had zero effect on the GPT-4o agent. It could not execute the same multi-step queries.

**The tool gap:** Address resolution (converting "4763 Griscom Street" to a database identifier) failed 87 percent of the time before we added a dedicated fuzzy-search tool. After adding that one tool, address failures dropped to zero for agents using GPT-4.1.

**The danger taxonomy emerges at this level:**
- Misattribution: a real fact attributed to the wrong person (a mother's bedtime statement attributed to the father)
- False negatives: the agent retrieved the correct data but failed to recognize the answer within it
- Hallucinated specifics: invented case numbers, dates, or statistics stated with confidence

**Recommendation:** Purpose-built tools with fuzzy matching and entity resolution. GPT-4.1 or equivalent as the minimum model. Explicit workflow guidance in system prompts. Tool descriptions that tell the model when and why to use each tool. Ground truth test suites with known answers. Budget for iterative testing because the initial deployment will not be good enough.

### Level 5: Legal and Adjudicative

**"Prepare the facts for this hearing. A family's future depends on the accuracy."**

Case preparation, evidence compilation, hearing summaries, regulatory determinations, benefits adjudication. A wrong answer can produce an incorrect legal outcome, a due process violation, or direct harm to vulnerable populations.

**Who uses this:** Attorneys, hearing officers, administrative law judges, child welfare legal teams, benefits adjudicators, regulatory compliance officers.

**What we found:** Even our highest-scoring agent (10 out of 10 on factual accuracy) produced a dangerous result: it faithfully reproduced a sheriff's report statement that "no fractures detected on skeletal survey" while the medical records in the same case documented bilateral long bone fractures in a child abuse investigation. The agent was not wrong about what the document said. It was wrong about what was true. This is the hardest failure mode to detect because the citation is real and the confidence is justified, but the conclusion is dangerous.

**The five categories of AI failure we documented:**

1. **False negative (Critical):** Data retrieved but not recognized as the answer
2. **Faithfully reproduced misinformation (Critical):** Agent accurately quoted a source document that itself contained an error
3. **Misattribution (High):** Correct fact assigned to the wrong person
4. **Hallucinated fact with confidence (High):** Invented specific detail with no source
5. **Silent failure (Medium):** No results returned without indicating anything went wrong

**Recommendation:** Everything from Level 4, plus mandatory human review workflows, citation and source linking so practitioners can verify each claim, audit logging of every tool call, and organizational culture that treats AI output as a draft. The agent accelerates the human; it does not replace them. Trust but verify is not optional at this level.

## The Evidence

This framework is grounded in 304 empirical test runs across two government use cases, 19 agent configurations, and six testing rounds.

### Use Case 1: Legal Case Analysis

- **Domain:** Department of Social Services, Office of Legal Services
- **Data:** 50 synthetic legal cases with 277 people, 333 timeline events, 338 statements, and 151 discrepancies
- **Agents tested:** 11 configurations across 3 structured database agents and 8 document-based agents
- **Result:** The custom web application scored a perfect 10 out of 10. Document agents scored 3 to 8 out of 10, with 7 of 8 faithfully reproducing a misleading medical finding.

### Use Case 2: Investigative Analytics

- **Domain:** City of Philadelphia property and code enforcement investigation
- **Data:** 34 million rows of real public records (584,000 properties, 1.6 million code violations)
- **Agents tested:** 8 configurations including 3 pro-code agents with custom orchestration
- **Result:** Two agents achieved perfect 10 out of 10 scores after iterative tool improvements. The GPT-4o agent plateaued at 4 out of 10 despite identical improvements.

### Cross-Use-Case Results by Agent Type

| Agent Configuration | Use Case 1 | Use Case 2 | Model |
|---|---|---|---|
| Custom Web Application | 10/10 | -- | GPT-4.1 |
| Investigative Agent (OpenAI SDK) | -- | 10/10 | GPT-4.1 |
| Copilot Studio MCP (Commercial) | 8/10 | 10/10 | GPT-4.1 |
| Foundry Agent (Azure AI Foundry) | -- | 9/10 | GPT-4.1 |
| Triage Agent (Semantic Kernel) | -- | 9/10 | GPT-4.1 |
| Copilot Studio MCP (Government Cloud) | 9/10 | 4/10 | GPT-4o |
| SharePoint/PDF (Commercial) | 8/10 | 8/10 | GPT-4.1 |
| SharePoint/PDF (Government Cloud) | 3-8/10 | 8/10 | GPT-4o |
| M365 Copilot | -- | 2/10 | Platform-assigned |

## What Government Cloud Customers Should Do

### At Every Level

1. **Test with known answers.** Build a ground truth test suite before building the agent. Without known answers, you cannot measure improvement.
2. **Fix the data first.** If the answer is not in the data, no model will find it. Make facts discrete and queryable, not buried in narrative paragraphs.
3. **Fix the tools second.** If the model cannot reach the data, add tools. If the model does not know which tool to use, improve descriptions.
4. **Retest after every change.** Each fix can introduce new failure modes. The only way to know is to run the full test suite again.

### The Model Gap

Government Community Cloud is currently locked to GPT-4o for Copilot Studio agents. This model scored 4 out of 10 on investigative queries where GPT-4.1 scored 9.5 out of 10. No amount of tool or prompt engineering closed this gap in our evaluation.

**Options for Government Cloud customers:**

- Use Copilot Studio document agents for Levels 1 through 3 (GPT-4o is adequate for retrieval and summarization)
- Deploy pro-code agents (using Azure OpenAI GPT-4.1 directly) for Level 4 and 5 workloads
- Monitor Government Cloud model updates. When GPT-4.1 becomes available in Government Cloud, Copilot Studio agents will benefit immediately

### The Code Investment Spectrum

The engineering investment changes what you can customize, not whether the agent works at Level 4 and above.

| Approach | Code Required | Best For |
|---|---|---|
| M365 Copilot | Zero (3 JSON manifests) | Level 1-2 (when model constraints are addressed) |
| Copilot Studio | Zero to low | Levels 1-3 (Commercial), Levels 1-2 (Government Cloud) |
| Azure AI Foundry Agent | Minimal | Levels 3-4 |
| Custom agent (OpenAI SDK, Semantic Kernel) | Full | Levels 4-5 |

Every architecture scored 9 to 10 out of 10 with GPT-4.1. The investment buys customization, governance controls, and audit capabilities, all of which matter most at Levels 4 and 5.

## Five Findings That Surprised Us

1. **The most dangerous agent was also the most accurate quoting its source.** Seven of eight document agents faithfully reproduced a sheriff's report statement about fracture findings while the medical records in the same case told a different story. The agents were not wrong about what the document said. They were wrong about what was true.

2. **A single missing tool caused an 87 percent failure rate.** No tool existed to convert a street address into a database identifier. Adding one fuzzy-match lookup tool produced zero failures in retesting. One agent went from 1 out of 10 to a perfect 10 out of 10.

3. **The most complex agent needed four rounds of iteration.** The Semantic Kernel team-of-agents pattern started at 0 out of 10 and reached 9 out of 10, but only after four rounds of sub-agent prompt engineering. A simpler Copilot Studio agent scored 8 out of 10 with no customization at all.

4. **The model retrieved the answer and did not recognize it.** On one prompt, the agent called the right tools, received data containing the answer, and concluded the data did not exist. This false negative is invisible to users because the tool calls look correct.

5. **A pro-code agent challenged its own premise and was right.** The Foundry Agent was asked about a price-to-assessment ratio. Instead of calculating the answer, it checked the source data, found the premise was wrong, and recalculated using verified numbers. No other agent questioned the input.

## Conclusion

Not all AI use cases require the same investment. Levels 1 and 2 work with existing Copilot licenses and SharePoint document libraries. Level 3 benefits from structured data connections via Model Context Protocol. Levels 4 and 5 require purpose-built tools, capable models (GPT-4.1 minimum), iterative testing, and human review workflows.

The most important lesson from 304 test runs: **the agent is a research assistant, never the decision-maker.** At Level 5, where legal outcomes depend on accuracy, trust but verify is not a suggestion. It is the only responsible operating model.

---

*Based on 304 test runs across 2 government use cases, 19 agent configurations, 6 testing rounds, and 3 rounds of iterative improvement. All test data is available in the project archive.*
