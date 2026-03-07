# Use Case 2: Philly Poverty Profiteering — Comparison Prompts

## Overview

10 prompts designed to compare structured-data agents (MCP/SQL with 34M rows) against document-backed agents (5 PDFs about GEENA LLC and two properties). Same testing methodology as Use Case 1 (Legal Case Analysis).

**Document corpus for document-backed agents:**
- Entity_Investigation_Report.pdf (GEENA LLC portfolio overview)
- Property_Enforcement_File_4763_Griscom.pdf (violations + demolition)
- Transfer_Chain_Analysis_4763_Griscom.pdf (ownership chain)
- Property_Case_File_2400_Bryn_Mawr.pdf (property profile + violations)
- Ownership_Financial_History_2400_Bryn_Mawr.pdf (transfers + mortgage crisis)

---

## Prompt 1: Simple Fact Extraction

**Prompt:** "How many properties does GEENA LLC own, and what percentage are vacant?"

**Ground Truth:**
- 194 properties, 178 vacant (91.8%)
- Total assessed value: $8,621,700

**What It Tests:** Basic fact retrieval. Both agent types should get this — it's stated explicitly in the Entity Investigation Report and queryable via search_entities + get_entity_network.

**Expected MCP advantage:** Can return the live count (may differ slightly if data has been updated since the report was written).

---

## Prompt 2: Cross-Document Reasoning

**Prompt:** "What happened to 4763 Griscom Street between when GEENA LLC bought it and today? Have they done anything with the property?"

**Ground Truth:**
- Bought December 24, 2019 for $6,500 at sheriff sale (Transfer Chain doc)
- Building had already been demolished June 2019 (Enforcement File)
- 43+ violations since acquisition, all CLIP vacant lot violations (Enforcement File)
- No permits, no licenses, no development applications filed (both docs)
- Current assessed value: $24,800 (Enforcement File)

**What It Tests:** Synthesizing facts from the Enforcement File and Transfer Chain docs. The agent needs to connect the purchase date with the violation timeline and the absence of any development activity.

---

## Prompt 3: Specific Numeric Extraction

**Prompt:** "What was the assessment value of 4763 Griscom Street in 2017, and what is it now? What happened?"

**Ground Truth:**
- 2017: $56,900 ($42,390 building + $14,510 land)
- 2025: $24,800 ($0 building + $24,800 land)
- Decline: 56.4% ($32,100 loss)
- Cause: City demolished the building in June 2019; building value went to $0

**What It Tests:** Extracting specific numbers from a table and explaining the causal relationship. The assessment history table is in the Enforcement File. MCP agents use get_property_assessments.

---

## Prompt 4: Ownership Chain Reconstruction

**Prompt:** "Trace the complete ownership history of 4763 Griscom Street. How many times was it sold at sheriff sale?"

**Ground Truth:**
- 6 owners: Ofides/Shehinsky → Bryan ($10,650, 1999) → Habeeb ($146,000, 2004) → DeJesus ($13,200, sheriff sale 2013) → Luong ($20,000, 2014) → Martinez ($21,500, 2014) → GEENA LLC ($6,500, sheriff sale 2019)
- **Two sheriff sales:** 2013 (Habeeb→DeJesus) and 2019 (Martinez→GEENA LLC)
- 26-day flip between Luong and Martinez

**What It Tests:** Complete chain reconstruction with dates and prices. All in the Transfer Chain Analysis doc. MCP agents use get_property_transfers.

---

## Prompt 5: Cross-Document Conflict / Contradiction

**Prompt:** "The transfer records show 4763 Griscom was sold for $146,000 in 2004. What was the fair market value at the time of that sale?"

**Ground Truth:**
- Purchase price: $146,000 (Habeeb from Bryan, March 2004)
- Fair market value recorded on deed: $53,155
- The purchase price was **275% of fair market value** — a $92,845 overpayment
- The Transfer Chain doc calls this "a hallmark of predatory or inflated transactions"

**What It Tests:** Identifying a discrepancy between price and value within a single transaction. This mirrors the DSS skeletal survey prompt — a fact that looks straightforward but contains a buried conflict. MCP agents would return both values from the transfer record.

---

## Prompt 6: Aggregate Query (MCP Advantage)

**Prompt:** "Who are the top 5 private property owners in Philadelphia by code violation count? Exclude government entities."

**Ground Truth (from get_top_violators):**
1. GEENA LLC — 194 properties, 1,411 violations, 823 failed
2. S3 ENTERPRISES LLC — 77 properties, 1,009 violations, 603 failed
3. ULATOWSKI WALTER — 140 properties, 915 violations, 516 failed
4. CORESTATES GROUP LLC — 99 properties, 773 violations, 453 failed
5. CHOICE RENTALS LLC — 56 properties, 763 violations, 419 failed

**What It Tests:** Aggregate query across 584K properties and 1.6M violations. **Document agents can only answer about GEENA LLC** (the one entity in their corpus) and will likely present it as #1 with no awareness of the other 4. This is the Philly equivalent of DSS Prompt 9 (TPR aggregate).

**Expected result:** MCP returns all 5 with exact counts. Doc agents return only GEENA LLC.

---

## Prompt 7: Financial Institution Analysis

**Prompt:** "What financial institutions were involved in the mortgage history of 2400 Bryn Mawr Avenue, and what happened to them?"

**Ground Truth (from Ownership & Financial History doc):**
- Washington Mutual — original mortgage (2002). Failed Sept 2008, seized by FDIC.
- Financial Freedom Senior Funding Corp — reverse mortgage (2006). Subsidiary of IndyMac.
- IndyMac Bank F.S.B. — co-lender (2006). Failed July 2008, seized by FDIC.
- U.S. Dept. of HUD — HECM guarantee (2006). Foreclosure party in 2016.
- Walter P. Lomax Jr. — private second mortgage lender (2006, 2009).
- MERS — mortgage tracking (2009). Named in nationwide litigation.
- Financial Freedom Acquisition LLC — reconstituted from IndyMac (2009).
- OneWest Bank N.A. — final holder, formed from IndyMac remnants (2015).

**What It Tests:** Dense narrative extraction with institutional context. The document contains a rich financial institution timeline table. MCP agents return raw transfer/mortgage records but lack the narrative about institutional failures — they'd show the names but not that WaMu and IndyMac collapsed.

**Expected result:** Document agents should excel here — this is narrative context the database doesn't capture.

---

## Prompt 8: Filtering Precision

**Prompt:** "How many code violations at 4763 Griscom Street resulted in FAILED inspections, and what type of investigator handles them?"

**Ground Truth:**
- 45 FAILED inspections out of 64 total (70.3% failure rate)
- Investigators: "CLIP" and "CLIP - VACANT LOT INVESTIGATOR"
- All violations are "NOTICE OF VIOLATION" case type

**What It Tests:** Filtering and counting within a single property's enforcement history. MCP agents use get_property_violations with status filter. Document agents need to extract from the Enforcement File narrative.

---

## Prompt 9: Area Statistics (MCP Advantage)

**Prompt:** "Compare the vacancy rates and violation rates between zip codes 19104 and 19132. Which is worse?"

**Ground Truth (from get_area_stats):** Real-time zip code statistics from 584K properties. Both are among the highest-vacancy, highest-violation zips in the city.

**What It Tests:** Cross-area aggregate comparison. **Document agents have no zip-level statistics** — the Entity Investigation Report mentions these zip codes as GEENA LLC concentrations but doesn't contain city-wide area stats. This is a query only the structured data can answer.

---

## Prompt 10: Arithmetic / Time Analysis

**Prompt:** "GEENA LLC bought 2400 Bryn Mawr for $230,000 in 2016. The assessed value at the time was $357,100. What was the discount percentage, and how has the assessment changed since then?"

**Ground Truth:**
- Purchase: $230,000. Assessed: $357,100. Discount: **35.6%** ($127,100 below assessed)
- Fair market value on deed: $360,671. Discount to FMV: **36.2%**
- Current assessment (2025): $265,600. Decline since purchase: **25.6%** ($91,500 loss)
- Assessment peaked at $357,100 (2015-2017), dropped to $317,100 (2018), then $265,600 (2019-2025)

**What It Tests:** Multi-step arithmetic from structured data. Both the Property Case File and Ownership History docs contain these numbers. MCP agents compute from get_property_profile + get_property_assessments. Tests whether agents can do the percentage calculations correctly.

---

## Prompt Summary

| # | Prompt | What It Tests | Expected Winner |
|---|--------|--------------|----------------|
| 1 | GEENA LLC property count + vacancy % | Simple fact extraction | Tie |
| 2 | What happened to 4763 Griscom since purchase | Cross-document synthesis | Slight doc advantage (narrative) |
| 3 | Assessment 2017 vs 2025 + explanation | Numeric extraction + causation | Tie |
| 4 | Complete ownership chain of 4763 Griscom | Chain reconstruction | Tie |
| 5 | $146K purchase vs $53K fair market value | Contradiction / discrepancy detection | Document (narrative flags it) |
| 6 | Top 5 private violators citywide | Aggregate across 584K properties | **MCP dominates** |
| 7 | Financial institutions + what happened to them | Narrative context extraction | **Document dominates** |
| 8 | Failed violations count + investigator type | Filtering precision | Tie (slight MCP for exact count) |
| 9 | Zip code comparison (19104 vs 19132) | Cross-area aggregate | **MCP dominates** |
| 10 | Purchase discount % + assessment change | Multi-step arithmetic | Tie |

### Design Notes

- **Prompts 6 and 9** are designed to be impossible for document agents — the documents cover 2 properties and 1 entity; the database covers 584,000 properties across all of Philadelphia.
- **Prompt 7** is designed to favor document agents — the narrative about institutional failures (WaMu, IndyMac, FDIC seizures) isn't in the SQL data.
- **Prompt 5** mirrors the DSS "skeletal survey" trap — a discrepancy buried in the data that could mislead if not caught.
- **Prompts 1, 3, 4, 8, 10** test core extraction and precision where both approaches should compete.
- Unlike DSS (synthetic data), this is **real public data** — every number is verifiable against City of Philadelphia records.
