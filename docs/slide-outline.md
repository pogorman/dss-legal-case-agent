# AI Agent Accuracy Spectrum -- Slide Outline

Target: 21 slides, 50-60 minutes (40-45 min presentation + live demo + 10-15 min Q&A)

---

## Slide 1: Title

**AI Agent Accuracy for Government: A Five-Level Framework**

Subtitle: Findings from 305 Test Runs Across 19 Agent Configurations

Visual: Clean title slide with agency-appropriate branding

Speaker notes: "Some of you may remember me from such demos as the delegation demo, or [insert another]. Those demos and this one have something in common: I like to build test harnesses for real-world use cases my customers care about. And both this demo and the delegation demo deal with the same fundamental topic: accuracy."

---

## Slide 2: The Question

**"Not all AI use cases are created equal."**

- Your policy lookup chatbot and your legal case preparation tool have fundamentally different accuracy requirements
- This framework helps you decide where to deploy aggressively, where to add guardrails, and where human review is non-negotiable

Visual: Spectrum arrow from "Low Stakes" to "High Stakes"

Speaker notes: "What this demo is: a process and methods -- with real-world examples -- for making your agents better. What it isn't: a data extraction demo, other than to show ideas on tools and process when extraction is necessary. You'll probably have more questions than answers when we're done. Let's get into it."

---

## Slide 3: The Five Levels (Overview)

| Level | Name | Stakes | Example |
|---|---|---|---|
| 1 | Discovery | Inconvenience | "Find our leave policy" |
| 2 | Summarization | Wasted time | "Summarize this audit report" |
| 3 | Operational | Misallocated resources | "How many open cases by type?" |
| 4 | Investigative | Missed evidence | "Build a timeline from these records" |
| 5 | Adjudicative | Wrong legal outcome | "Prepare facts for this hearing" |

Visual: Stacked bar or pyramid with color-coded levels (green to red)

Talking point: "Where does your highest-priority use case fall?"

---

## Slide 4: Levels 1-2 -- The Quick Win

**Document agents score 8 out of 10 with zero engineering**

- Point Copilot at your SharePoint library
- No custom code, no databases, no tool design
- Model choice barely matters at this level
- Good enough for policy lookup, report summarization, meeting notes

Visual: Simple diagram: Copilot arrow SharePoint arrow Answer

Talking point: "This is where most agencies should start. It works today."

---

## Slide 5: Level 3 -- Structured Data Starts Winning

**Aggregate queries work across all agent types**

- "How many active cases?" "What's the breakdown by county?" "Top 5 violators?"
- Document agents cannot answer these -- they only have individual files
- Model Context Protocol connects AI to live databases and APIs

Visual: Side-by-side comparison. Document agent: "I don't have that information." MCP agent: table with counts.

Talking point: "This is where you start investing in data structure."

---

## Slide 6: Level 4 -- The Inflection Point

**This is where engineering decisions determine success or failure**

Three gaps emerged in testing:
- **The model gap:** GPT-4.1 scores 9.5/10 vs GPT-4o at 4/10
- **The tool gap:** One missing tool caused 87% failure rate
- **The data gap:** Facts buried in narrative text were invisible to agents

Visual: Three gap icons with before/after numbers

Talking point: "Level 4 is where the investment pays off -- or doesn't."

---

## Slide 7: The Model Gap (Detail)

**GPT-4.1 vs GPT-4o: Same tools, same data, same backend**

| Model | Average Score |
|---|---|
| GPT-4.1 | 9.5 out of 10 |
| GPT-4o (Government Cloud) | 4 out of 10 |
| Platform-assigned (M365 Copilot) | 2 out of 10 |

- Government Cloud Copilot Studio is locked to GPT-4o today
- No amount of prompt engineering closed this gap
- Pro-code agents can use GPT-4.1 in Government Cloud via Azure OpenAI directly

Visual: Bar chart with three bars showing dramatic gap

Talking point: "The model is the single biggest variable at Level 4."

---

## Slide 8: The Tool Gap (Detail)

**87% failure rate from one missing tool**

- Agents could not convert "4763 Griscom St" to a database parcel ID
- 15 address lookups across 5 agents, only 2 succeeded
- One fuzzy-match tool added: zero failures in retesting
- Investigative Agent: 1 out of 10 to a perfect 10 out of 10

Visual: Before/after with the single tool highlighted as the change

Talking point: "Tool design is as important as model selection. Maybe more."

---

## Slide 9: Level 5 -- Trust But Verify

**Even our best agent reproduced a dangerous error**

- Sheriff's Report: "no fractures detected on skeletal survey"
- Medical Records: bilateral long bone fractures documented
- 7 of 8 document agents quoted the sheriff's report without cross-checking
- The citation was real. The confidence was justified. The conclusion was dangerous.

Visual: Split screen -- Sheriff Report quote on left, Medical Records finding on right

Talking point: "This is why Level 5 requires human review. Always."

Speaker notes: "Connect to daily experience: Copilot helps you draft an email -- you review it. Copilot helps you write code -- you review it. Why would we skip human review at any of these five levels, especially Level 5 where the stakes are a family's future?"

---

## Slide 10: The Danger Taxonomy

**Five categories of AI failure, ranked by severity**

1. **False negative (Critical)** -- Data retrieved, answer not recognized
2. **Faithfully reproduced misinformation (Critical)** -- Source document had an error, agent quoted it accurately
3. **Misattribution (High)** -- Real fact, wrong person
4. **Hallucinated fact with confidence (High)** -- Invented detail with no source
5. **Silent failure (Medium)** -- No results, no indication anything went wrong

Visual: Severity ladder or risk matrix, color-coded red to yellow

Talking point: "These are not hypothetical. We documented each one across 305 test runs."

---

## Slide 11: The Iterative Process

**Deploying an agent is not a one-time event**

- **Round 0:** Baseline testing -- measure failures against ground truth
- **Round 1:** Fix the data -- make facts discrete and queryable
- **Round 2:** Fix the tools -- help the model reach the data
- **Round 3:** Validate across models -- confirm what works where

Visual: Circular improvement diagram with 4 stages, arrows showing iteration

Talking point: "Every organization will go through these rounds, in this order."

---

## Slide 12: Results After Iteration

**Four agents reached 9-10 out of 10 after iterative improvement (three at perfect 10)**

| Agent | Round 1 | Final | Rounds |
|---|---|---|---|
| Commercial MCP (Copilot Studio) | 8/10 | 10/10 | 2 |
| Investigative Agent (OpenAI SDK) | 1/10 | 10/10 | 2 |
| Foundry Agent (Azure AI Foundry) | 4/10 | 9/10 | 2 |
| Triage Agent (Semantic Kernel) | 0/10 | 10/10 | 5 |

Visual: Improvement arc showing Round 1 baseline to final score

Talking point: "The Triage Agent took five rounds to reach a perfect score. The investment is real -- but so are the results."

---

## Slide 13: The Code Spectrum

**Zero code to full code -- same accuracy with GPT-4.1**

| Approach | Code | Best For |
|---|---|---|
| M365 Copilot | Zero (3 JSON manifests) | Levels 1-2 |
| Copilot Studio | Zero to low code | Levels 1-3 |
| Azure AI Foundry Agent | Minimal code | Levels 3-4 |
| Custom SDK (OpenAI, Semantic Kernel) | Full code | Levels 4-5 |

Visual: Horizontal spectrum from zero to full code with accuracy bars all at 9-10

Talking point: "The investment buys governance and customization, not accuracy. Accuracy comes from the model and the data."

---

## Slide 14: Why Copilot Studio (Tech Series)

**One platform, declarative to pro-code**

- Same environment hosts zero-code SharePoint agents AND MCP-connected structured data agents
- Model flexibility: swap GPT-4o for GPT-4.1, accuracy goes from 4/10 to 10/10 -- no config changes
- Enterprise governance built in: DLP, audit logging, admin pre-approval for tool calls
- M365 distribution: agents show up in Teams and Copilot chat -- no separate app to deploy
- Our test data proves the platform works -- the model is the variable, not the architecture

Visual: Copilot Studio logo with radiating connections to SharePoint, MCP, Teams, Foundry

Talking point: "Commercial Copilot Studio MCP scored a perfect 10 out of 10. The architecture is sound. The limiting factor is model availability in GCC."

Speaker notes: "This slide is critical for the tech series. MUST articulate the platform value, not just the results."

---

## Slide 15: What to Do at Each Level

| Level | Action |
|---|---|
| 1-2 | Deploy Copilot with SharePoint. Clean up document metadata. Done. |
| 3 | Connect to structured data via MCP. Clear tool descriptions. Summary modes. |
| 4 | Purpose-built tools. GPT-4.1 minimum. Ground truth test suite. Budget 3+ rounds. |
| 5 | Level 4 + human review workflows + audit logging + citation linking. |

Visual: Checklist format, one row per level, with investment increasing rightward

Talking point: "Match your investment to your accuracy requirement."

---

## Slide 16: Government Cloud Customers

**The GCC reality today**

- Copilot Studio locked to GPT-4o (adequate for Levels 1-3)
- Pro-code agents can use GPT-4.1 via Azure OpenAI (Levels 4-5)
- Monitor model updates -- GCC parity will improve over time

**Decision tree:**
- Is your use case Level 1-3? Use Copilot Studio today.
- Is your use case Level 4-5? Deploy a pro-code agent with GPT-4.1.
- Are you planning for Level 4-5 in the future? Start building ground truth test suites now.

Visual: Decision tree flowchart

Talking point: "Know what works today. Plan for what's coming."

---

## Slide 17: Live Demo Title Card

**"Let me show you the difference between Level 2 and Level 4."**

[Switch to live demo -- follow the presenter guide]

- Level 2: SharePoint document summarization (2 min)
- Level 3: "How many cases by type?" aggregate query (2 min)
- Level 4: The money prompt -- timeline, discrepancies, statements (5 min)
- Level 5: The skeletal survey question (3 min)

Visual: Demo URL and case number reference

---

## Slide 18: Surprising Finding -- Agent Challenged Its Own Premise

**A pro-code agent questioned the question -- and was right**

- Asked about a $146,000 purchase vs a $357,100 assessment
- Agent checked the source data: actual assessment was $53,155
- Recalculated using verified numbers instead of the prompt's numbers
- No other agent questioned the input

Visual: Quote from agent response showing the correction

Talking point: "This is what custom orchestration enables -- but only with iterative testing."

---

## Slide 19: Surprising Finding -- False Negative

**The model retrieved the answer and didn't recognize it**

- Agent called the right tools
- Received data containing "two positive drug screens (fentanyl)"
- Concluded: "no drug test results exist in the available data"
- Invisible to users: tool calls look correct, answer sounds confident

Visual: Screenshot of tool output alongside agent's incorrect conclusion

Talking point: "This is why you need ground truth testing. You cannot catch this in production."

---

## Slide 20: The Bottom Line

**Three numbers to remember**

- **8/10** -- What you get with zero engineering (Levels 1-2)
- **9.5/10** -- What you get with purpose-built tools and GPT-4.1 (Levels 3-4)
- **Trust but verify** -- No score is high enough to skip human review (Level 5)

Visual: Three large numbers with icons (document, tools, human)

Talking point: "The question is not 'should we deploy AI?' The question is 'which level are we operating at, and have we invested accordingly?'"

Speaker notes: "So what do we do? Do we just give up on agents? No -- you continue to test them and make them better, and you always adhere to trust but verify. I have agents building apps for me right now. If I were building production enterprise apps, I'd have a team of human developers checking the work, helping test, reviewing agentic results. The AI accelerates the team. The team validates the AI."

---

## Slide 21: Next Steps

**Start the conversation**

- Where do your use cases fall on the spectrum?
- What data do you already have in structured form?
- What's your risk tolerance for AI-generated output?
- Ready for a deeper dive? We have the architecture, the test data, and the framework.

Visual: Contact information, QR code to executive summary PDF

Talking point: "I'm not here to sell you a product. I'm here to help you make the right investment for your mission."
