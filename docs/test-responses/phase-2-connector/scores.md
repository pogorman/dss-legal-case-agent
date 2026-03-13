# Phase 2 Custom Connector Agent — Scored Results

**Agent:** GCC Copilot Studio + Custom Connector (DSS Case API)
**Model:** GPT-4o (GCC default)
**Date:** 2026-03-12
**Prompts:** 19 (same Phase 1 rubric from Demo_Comparison_Prompts.md)

## Scoring Method

Each prompt is scored 0-10 against the expected MCP agent response defined in Phase 1. Section averages are the arithmetic mean of the prompt scores in that section (e.g., 3 prompts scoring 10, 10, 0 = 20/3 = 6.7). The overall average is the arithmetic mean of all 19 individual prompt scores, not a mean of section averages. This produces decimal values like 9.3 or 6.7 when section sizes don't divide evenly.

- **10/10:** All expected details present and accurate, with source citations
- **7-9/10:** Most details correct, minor omissions (missing cross-references, no editorial analysis)
- **4-6/10:** Partially correct, missing notable details or has inaccuracies
- **1-3/10:** Responded but with wrong data or wrong case
- **0/10:** No usable response (agent refused, asked for input, or returned error)

## Individual Scores

### Section 1: Factual Retrieval

**1.1** "What is the complete timeline of events for case 2024-DR-42-0892?"
**Score: 10/10**

14 events in chronological order with dates, times, sources, parties. More detail than expected -- includes skeletal survey event not in the rubric.

**Q:** What is the complete timeline of events for case 2024-DR-42-0892?

**A:** Here is the complete timeline of events for case 2024-DR-42-0892:

1. **June 11, 2024, 9:30 PM**: Dena Holloway hears a loud thump from Jaylen's room. She calls out, and Marcus Webb responds that everything is fine. Dena does not check on Jaylen at that time. (Source: Sheriff Report #24-06-4418, pp. 6-7)
2. **June 11, 2024, 10:00 PM**: Marcus Webb states he put Jaylen to bed at approximately 10:00 PM. Reports child was behaving normally throughout the day. (Source: Dictation PDF, p. 3)
3. **June 12, 2024, 2:00 AM**: Dena Holloway reports hearing Jaylen crying loudly. Found child in crib unable to move left leg. Both parents drove child to Spartanburg Medical Center ER. (Source: Dictation PDF, p. 4)
4. **June 12, 2024, 3:15 AM**: Jaylen Webb admitted to Spartanburg Medical Center ER. X-rays reveal bilateral femur fracture (right) and spiral fracture of left humerus. Injuries assessed as inconsistent with reported mechanism (fall from crib). Dr. Chowdhury notes injuries are at different stages of healing. (Source: Medical Records, pp. 1-4)
5. **June 12, 2024, 4:07 AM**: Skeletal survey completed by radiologist Dr. David Petrakis. Findings: transverse fracture of right femoral shaft (estimated 3-5 days old, with periosteal reaction and early callus formation) and spiral fracture of left humeral shaft (estimated 24-48 hours old). Remainder of skeletal survey showed no additional fractures. No metabolic bone disease pattern identified. (Source: Medical Records, pp. 3-4)
6. **June 12, 2024, 7:30 AM**: Dr. Chowdhury files mandatory abuse/neglect report with DSS and Spartanburg County Sheriff. Medical opinion: injuries are non-accidental and occurred at different times. (Source: Medical Records, p. 5; DSS Intake Report)
7. **June 12, 2024, 11:00 AM**: Lt. Frank Odom responds to hospital. Observes child injuries. Interviews ER nursing staff. Requests DSS coordination. (Source: Sheriff Report #24-06-4418, p. 1)
8. **June 13, 2024, 9:00 AM**: Renee Dawson assigned as DSS case manager. Conducts initial assessment interview with Dena Holloway at hospital. (Source: Dictation PDF, pp. 4-6)
9. **June 13, 2024, 1:30 PM**: Lt. Odom interviews Marcus Webb at Spartanburg County Sheriff office. Marcus states he was asleep on the couch and did not hear anything. (Source: Sheriff Report #24-06-4418, pp. 3-5)
10. **June 13, 2024, 4:00 PM**: Lt. Odom interviews Dena Holloway at Spartanburg County Sheriff office. Dena changes account -- now states Marcus was in the child room earlier and she heard a thump at 9:30 PM. (Source: Sheriff Report #24-06-4418, pp. 6-8)
11. **June 14, 2024, 10:00 AM**: DSS files petition for emergency protective custody. Judge Easley grants ex parte emergency removal order. Jaylen placed in temporary DSS custody. (Source: Court Filing #2024-DR-42-0892, Order 1)
12. **June 18, 2024, 9:30 AM**: Probable cause hearing. Court finds probable cause for removal. Karen Milford appointed as Guardian ad Litem. (Source: Court Filing #2024-DR-42-0892, Order 2)
13. **June 20, 2024**: Jaylen discharged from hospital and placed with maternal grandmother Theresa Holloway under kinship foster care. (Source: Placement Agreement, DSS Form 1234)
14. **July 18, 2024, 2:00 PM**: Thirty-day review hearing. Case plan approved. Next merits hearing September 12, 2024. (Source: Court Filing #2024-DR-42-0892, Order 3)

---

**1.2** "When was Jaylen Webb admitted to the hospital and what injuries were found?"
**Score: 10/10**

June 12, 3:15 AM, both fractures, inconsistent with crib fall, different healing stages. All key details present.

**Q:** When was Jaylen Webb admitted to the hospital and what injuries were found?

**A:** Jaylen Webb was admitted to Spartanburg Medical Center ER on June 12, 2024, at 3:15 AM. The injuries found included a bilateral femur fracture (right) and a spiral fracture of the left humerus. The injuries were assessed as inconsistent with the reported mechanism (fall from crib) and were noted to be at different stages of healing.

---

**1.3** "List all people involved in the Price TPR case and their roles."
**Score: 10/10**

All 8 people with correct names, roles, relationships. Perfect match to rubric.

**Q:** List all people involved in the Price TPR case and their roles.

**A:** 1. Crystal Price - Mother (Parent). 2. Brandon Price - Father, incarcerated, rights relinquished (Parent). 3. Amari Price - Minor child, age 7 (Child). 4. Destiny Price - Minor child, age 5 (Child). 5. Monica Vance - DSS Case Manager (Case Manager). 6. Dr. Raymond Ellis - Substance abuse evaluator (Witness). 7. Sandra Patterson - Licensed foster parent, pre-adoptive (Foster Parent). 8. Thomas Reed - Court-appointed GAL (Guardian ad Litem).

---

**1.4** "What court hearings have occurred in the Webb case and what were the outcomes?"
**Score: 10/10**

3 hearings with dates, descriptions, outcomes. Correct and complete.

**Q:** What court hearings have occurred in the Webb case and what were the outcomes?

**A:** 1. Emergency Removal Order (June 14, 2024): Judge Easley granted ex parte emergency removal. Jaylen placed in temporary DSS custody. 2. Probable Cause Hearing (June 18, 2024): Court found probable cause. Karen Milford appointed GAL. 30-day review scheduled. 3. Thirty-Day Review (July 18, 2024): Case plan approved (parenting classes, psych evals, supervised visitation). Merits hearing scheduled September 12.

---

### Section 2: Cross-Referencing

**2.1** "What did Marcus Webb tell medical staff vs. what he told law enforcement about the night Jaylen was injured?"
**Score: 8/10**

Exact quotes from both audiences (1 medical staff, 2 law enforcement). Notes discrepancies. Does not explicitly call out that the crib-climbing theory was introduced only in the LE statement -- the reader can see it in the quotes, but the agent doesn't highlight this key analytical insight.

**Q:** What did Marcus Webb tell medical staff vs. what he told law enforcement about the night Jaylen was injured?

**A:** **To Medical Staff:** "I put him to bed around ten. He was fine, running around all day. I fell asleep on the couch watching TV. Next thing I know, Dena is shaking me saying something is wrong with Jaylen." (2024-06-12)

**To Law Enforcement:** "I was on the couch all night. I did not go into Jaylen's room after I put him down. I don't know how he got hurt. Maybe he climbed out of the crib and fell. He's been trying to climb out lately." (2024-06-13) / "Dena and I have been arguing a lot lately but I would never hurt my son. I don't know why she is saying I was in the room. I was not in his room after 10 PM." (2024-06-13)

---

**2.2** "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?"
**Score: 10/10**

All 3 changes identified: 9:30 PM thump, Marcus placed in room, rough handling history disclosed.

**Q:** Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?

**A:** Initial Hospital Statement (June 12): Heard crying at 2 AM, found child unable to move leg, believes crib fall. No mention of 9:30 PM or Marcus being in room.

Later Statement to Lt. Odom (June 13): Revealed 9:30 PM thump from Jaylen's room. Assumed Marcus was in room, called out, Marcus said everything was fine. Did not check on Jaylen. Also disclosed Marcus has a temper and she has seen him grab Jaylen roughly 2-3 times.

Changes: (1) Added 9:30 PM thump, (2) placed Marcus in/near child's room, (3) disclosed history of rough handling.

---

**2.3** "What has Crystal Price said about her sobriety at each court hearing? How do those statements compare to her drug test results?"
**Score: 10/10**

All 3 court statements with dates and quotes. Fentanyl positives contradicting "clean now." Also surfaced compliance and housing contradictions -- exceeded expectations.

**Q:** What has Crystal Price said about her sobriety at each court hearing? How do those statements compare to her drug test results?

**A:** Probable Cause (Aug 15, 2023): "I know I need to get help. I will do everything the court asks." 90-Day Review (Nov 14, 2023): "I am clean now." TPR Probable Cause (Apr 22, 2024): "I have been going to my IOP sessions... I am trying."

Contradicted by: October 8 and 22, 2023 both positive for fentanyl. Missed screens Dec 5, Jan 15, Mar 3. One negative April 2024. The "clean now" claim at November hearing came one month after two fentanyl positives. Also surfaced compliance contradictions (5/12 IOP, 2/8 parenting classes despite DSS providing bus passes and transport) and housing instability (month-to-month, 10x10 room, 4+ addresses since removal).

---

### Section 3: Discrepancies

**3.1** "What are the key discrepancies between Marcus Webb's and Dena Holloway's accounts?"
**Score: 10/10**

7 discrepancies (expected 6) including all 6 from rubric plus skeletal survey finding. Each with both accounts and contradicting evidence.

**Q:** What are the key discrepancies between Marcus Webb's and Dena Holloway's accounts?

**A:** (1) Cause of injuries -- crib fall vs. 9:30 PM thump. (2) Marcus's presence in child's room -- denies being there vs. Dena places him there. (3) Timing of injury discovery -- 4.5-hour gap. (4) History of rough handling -- Marcus denies, Dena describes 2-3 prior incidents. (5) Single vs. multiple injury events -- medical evidence shows days apart. (6) Dena's own initial vs. revised account -- omitted 9:30 PM thump and rough handling in hospital statement. (7) Skeletal survey discrepancy -- Sheriff Report says "no fractures detected" while Medical Records document two fractures.

---

**3.2** "Are there any contradictions in Crystal Price's statements about her compliance with the treatment plan?"
**Score: 10/10**

4 contradictions with source documents: compliance, drug use, housing stability, home condition at removal.

**Q:** Are there any contradictions in Crystal Price's statements about her compliance with the treatment plan?

**A:** Yes. (1) Claims she's trying but lacks transportation -- contradicted by DSS records: bus passes monthly, 3 housing referrals, IOP transport offered and declined. Only 5/12 IOP, 2/8 parenting in 8 months. (2) Claims "clean now" at November hearing -- contradicted by two fentanyl positives in October, missed screens Dec/Jan/Mar. (3) Claims stable housing -- inspection shows 10x10 room, month-to-month, 4+ addresses. (4) Claims kids were fine at removal -- home visit found utility shutoff, drug paraphernalia, no food, unsupervised children.

---

**3.3** "What evidence contradicts the parents' claim that Jaylen fell from his crib?"
**Score: 0/10**

"Please provide the case identifier." Agent couldn't resolve "Jaylen" and "the parents" to a specific case -- no last names or case ID in the prompt. Orchestration failure: GPT-4o didn't attempt a ListCases or name lookup to resolve the implicit reference.

**Q:** What evidence contradicts the parents' claim that Jaylen fell from his crib?

**A:** Please provide the case identifier, for example, 2024-DR-42-0892.

---

### Section 4: Filtering

**4.1** "Show me only the medical events in the Webb case timeline."
**Score: 1/10**

Returned 1 medical event from the wrong Webb case (Bryce Webb, June 2025, case 2024-DR-10-0261) instead of Jaylen Webb's case (2024-DR-42-0892). Agent found "Webb" via ListCases but resolved to the wrong case. Correct filtering concept, wrong case.

**Q:** Show me only the medical events in the Webb case timeline.

**A:** Event Date: June 26, 2025. Event Type: Medical. Description: Forensic interview of Bryce Webb completed. Parties Involved: Bryce Webb. Source: Psychological Evaluation, p. 15.

---

**4.2** "What statements were made to law enforcement in case 2024-DR-42-0892?"
**Score: 10/10**

All 4 LE statements (2 Dena, 2 Marcus) with exact quotes, dates, source documents, page references.

**Q:** What statements were made to law enforcement in case 2024-DR-42-0892?

**A:** (1) Dena Holloway (June 13): "Actually, I need to correct something. Around 9:30 PM I heard a loud thump..." (Sheriff Report, p. 7). (2) Dena Holloway (June 13): "Marcus has a temper. He gets frustrated when Jaylen won't stop crying..." (Sheriff Report, p. 8). (3) Marcus Webb (June 13): "I was on the couch all night..." (Sheriff Report, p. 4). (4) Marcus Webb (June 13): "Dena and I have been arguing..." (Sheriff Report, p. 5).

---

**4.3** "List all court orders for the Price case in chronological order."
**Score: 10/10**

5 court events in correct chronological order with full details, parties, and source documents.

**Q:** List all court orders for the Price case in chronological order.

**A:** (1) Aug 15, 2023: Probable cause hearing, treatment plan ordered. (2) Nov 14, 2023: 90-day review, plan continued with TPR warning. (3) Nov 20, 2023: Brandon Price voluntary relinquishment. (4) Feb 8, 2024: DSS files TPR petition. (5) Apr 22, 2024: TPR probable cause, merits hearing scheduled July 15.

---

### Section 5: Aggregate

**5.1** "How many active cases does DSS currently have?"
**Score: 9/10**

Returned definitive count (25). Minor inconsistency: previous run returned 24. The agent calls ListCases and counts -- correct approach. The variance suggests GPT-4o may occasionally miscount a large result set.

**Q:** How many active cases does DSS currently have?

**A:** The DSS currently has 25 active cases.

---

**5.2** "List all cases in the Seventh Judicial Circuit."
**Score: 10/10**

5 cases listed, all Spartanburg county, with IDs, titles, types, statuses, and summaries.

**Q:** List all cases in the Seventh Judicial Circuit.

**A:** (1) 2023-DR-24-0355: DSS v. Baker -- Child Neglect. (2) 2024-DR-25-0177: DSS v. Green -- Child Neglect. (3) 2024-DR-18-0308: DSS v. Parker -- Guardianship. (4) 2024-DR-42-0892: DSS v. Webb & Holloway -- CPS Emergency Removal. (5) 2024-DR-10-0261: DSS v. Webb -- Emergency Removal.

---

**5.3** "Which cases involve Termination of Parental Rights?"
**Score: 10/10**

9 TPR cases listed with IDs, circuits, counties, statuses, and summaries. Comprehensive.

**Q:** Which cases involve Termination of Parental Rights?

**A:** 9 cases listed: Young, Taylor, Price, Reed, Parker, Wright (closed), Nelson (closed), Williams (dismissed), Morris (dismissed).

---

**5.4** "Are there any cases in Richland County besides the Price case?"
**Score: 8/10**

Correctly answers yes and names 2 cases, but uses "for example" language rather than providing a definitive complete list. MCP agent would confirm completeness.

**Q:** Are there any cases in Richland County besides the Price case?

**A:** Yes, there are other cases in Richland County besides the Price case. For example, there is a case titled "DSS v. Taylor -- Physical Abuse" (2024-DR-41-0307, closed) and "DSS v. Parker -- TPR" (2025-DR-21-0289, active).

---

### Section 6: Stress Tests

**6.1** "What page of the medical records contains Dr. Chowdhury's assessment that the injuries occurred at different times?"
**Score: 7/10**

Correct: page 5 of the medical records. Missing the exact quote and the Court Transcript p. 14 cross-reference that the MCP agent provides.

**Q:** What page of the medical records contains Dr. Chowdhury's assessment that the injuries occurred at different times?

**A:** Dr. Chowdhury's assessment that the injuries occurred at different times is documented on page 5 of the medical records.

---

**6.2** "How many IOP sessions had Crystal Price completed as of the November 2023 review vs. the April 2024 hearing?"
**Score: 8/10**

Correct numbers: 3/12 at November, 5/12 at April. Missing the net calculation (2 sessions over 5 months) and the editorial note about the slow pace that the MCP agent provides.

**Q:** How many IOP sessions had Crystal Price completed as of the November 2023 review vs. the April 2024 hearing?

**A:** As of the November 2023 review, Crystal Price had completed 3 of 12 required IOP sessions. By the April 2024 hearing, she had completed 5 of 12 IOP sessions.

---

## Summary

### Section Averages

| Section | Prompts | Scores | Average |
|---------|---------|--------|---------|
| 1. Factual Retrieval | 4 | 10, 10, 10, 10 | **10.0/10** |
| 2. Cross-Referencing | 3 | 8, 10, 10 | **9.3/10** |
| 3. Discrepancies | 3 | 10, 10, 0 | **6.7/10** |
| 4. Filtering | 3 | 1, 10, 10 | **7.0/10** |
| 5. Aggregate | 4 | 9, 10, 10, 8 | **9.3/10** |
| 6. Stress Tests | 2 | 7, 8 | **7.5/10** |

### Overall: 161/190 = **8.5/10**

### Failure Analysis

The 2 hard failures (3.3 and 4.1) are both **orchestration issues**, not data access issues:

- **3.3 (0/10):** Prompt says "Jaylen" and "the parents" with no case ID or last names. GPT-4o didn't attempt a ListCases lookup or name search to resolve the implicit reference. The MCP agent handles this because its orchestration loop is more sophisticated.

- **4.1 (1/10):** Prompt says "the Webb case" which is ambiguous -- there are two Webb cases in the database (2024-DR-42-0892 and 2024-DR-10-0261). GPT-4o resolved to the wrong one. The MCP agent resolves this correctly because the prompt context and prior conversation make the intent clear.

Both failures demonstrate the same pattern: **the custom connector gives Copilot Studio the same data access as MCP, but the platform's built-in orchestration (GPT-4o) is less reliable at resolving ambiguous references.** When the prompt includes an explicit case ID or specific names, the connector agent performs at MCP-level fidelity.
