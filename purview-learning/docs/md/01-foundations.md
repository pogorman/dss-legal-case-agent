# Module 01: Foundations

## What This Module Covers
- What data governance actually is (industry-wide)
- The regulatory landscape driving governance investment
- How Microsoft Purview fits into the picture
- Purview's history and evolution (the mergers that created it)
- Portal navigation and product areas
- Licensing (what requires what)
- Where Power Platform enters the picture

---

## 1. Data Governance — The Industry Standard Concept

> **Industry Standard:** Data governance is the practice of managing the availability, usability, integrity, and security of data in an organization. It's not a Microsoft invention — it's a discipline that exists across every enterprise platform.

### The Core Pillars (Universal)

Every data governance program, regardless of vendor, addresses these pillars:

| Pillar | What It Means | Example |
|--------|--------------|---------|
| **Data Discovery** | Know what data you have and where it lives | Scanning databases, file shares, cloud storage for sensitive data |
| **Data Classification** | Label data by sensitivity/type | PII, PHI, financial, public, confidential, top secret |
| **Data Protection** | Control who can access/share data | Encryption, access controls, DLP policies |
| **Data Lineage** | Track where data came from and where it goes | Source system → ETL → data warehouse → report |
| **Data Quality** | Ensure data is accurate, complete, consistent | Deduplication, validation rules, master data management |
| **Data Retention** | Keep data as long as required, delete when not | Legal holds, retention schedules, records management |
| **Audit & Accountability** | Track who did what and when | Audit logs, access reviews, compliance reports |

These pillars exist whether you're using Microsoft, AWS, Google Cloud, or on-premises systems. The vendors just implement them differently.

### Industry Frameworks and Regulations

The reason governance matters isn't academic — it's driven by regulations and legal requirements:

| Framework/Regulation | Scope | Key Requirements |
|---------------------|-------|-----------------|
| **HIPAA** | Healthcare (US) | PHI protection, breach notification, minimum necessary access |
| **FERPA** | Education (US) | Student record privacy, consent requirements |
| **CJIS** | Criminal Justice (US) | Data encryption, access controls, audit logging |
| **FedRAMP** | Federal IT (US) | Security controls for cloud services, authorization to operate |
| **StateRAMP** | State/Local IT (US) | FedRAMP-equivalent for state and local government |
| **NIST 800-53** | Federal (US) | Security and privacy control catalog (the bible) |
| **NIST AI RMF** | AI Systems (US) | AI risk management — govern, map, measure, manage |
| **GDPR** | EU citizens | Data subject rights, consent, right to erasure, DPO requirement |
| **SOC 2** | Service orgs | Trust service criteria — security, availability, processing integrity |
| **PCI DSS** | Payment cards | Cardholder data protection, network segmentation |

> **Why this matters to you:** As a Microsoft technical seller, customers will reference these frameworks when evaluating governance solutions. Purview maps to many of these controls, but it's important to know which framework a customer cares about so you can speak their language.

### Vendor Landscape (Not Just Microsoft)

Microsoft Purview competes with and complements other governance tools:

| Vendor/Tool | Strength | Overlap with Purview |
|-------------|----------|---------------------|
| **Collibra** | Data catalog, business glossary, stewardship | Data Map, catalog |
| **Informatica** | Data quality, lineage, master data | Data Map, lineage |
| **Alation** | Data catalog, search, collaboration | Data Map, catalog |
| **BigID** | Data discovery, classification, privacy | Sensitive information types, classification |
| **OneTrust** | Privacy management, consent, assessments | Compliance Manager, privacy risk management |
| **Varonis** | File system monitoring, access analysis | Information protection, DLP |
| **Splunk** | SIEM, log aggregation, threat detection | Audit log, insider risk (different angle) |
| **AWS Macie** | S3 data classification | Sensitive information types (AWS equivalent) |
| **Google DLP** | Cloud DLP for GCP | Data loss prevention (GCP equivalent) |

> **Microsoft-Specific:** Microsoft's play is consolidation — one portal, one platform, one licensing model that covers governance + compliance + risk + AI. Most competitors are point solutions. This is Purview's pitch: breadth.

---

## 2. Microsoft Purview — What It Actually Is

### The Merger Story

Microsoft Purview as it exists today (2026) is the result of two major product lines being merged under one brand:

**Before Purview (pre-2022):**
- **Azure Purview** — Data governance for Azure/multi-cloud. Data catalog, data map, lineage, scanning. Think: "where is my data and what's in it?"
- **Microsoft 365 Compliance Center** — Compliance tools for M365. DLP, information protection, retention, eDiscovery, audit, insider risk. Think: "protect and govern Office 365 content."

**After the rebrand (2022+):**
- Both products were unified under the **Microsoft Purview** brand
- Single portal: `purview.microsoft.com` (replacing `compliance.microsoft.com`)
- But underneath, the two product lines are still somewhat distinct:
  - **Data Governance** solutions (formerly Azure Purview) — Data Map, Data Catalog, Data Estate Insights
  - **Risk and Compliance** solutions (formerly M365 Compliance) — DLP, Information Protection, Audit, eDiscovery, Insider Risk, Communication Compliance, Records Management
  - **AI Governance** solutions (new) — AI Hub, DSPM for AI

> **Why the history matters:** When you read documentation or talk to customers, you'll encounter references to both lineages. Someone who "knows Purview" from the Azure side may have never touched DLP or eDiscovery. Someone from the M365 compliance side may not know about Data Map. They're different skill sets that now live under one roof.

### The Three Pillars of Modern Purview

| Pillar | What's In It | Lineage |
|--------|-------------|---------|
| **Data Security** | Information Protection, DLP, Insider Risk Management, DSPM for AI | M365 Compliance |
| **Data Governance** | Data Map, Data Catalog, Data Estate Insights, Data Quality, Data Sharing | Azure Purview |
| **Risk & Compliance** | Audit, eDiscovery, Communication Compliance, Compliance Manager, Records Management | M365 Compliance |

Plus the new **AI Governance** capabilities that span across pillars:
- **AI Hub** — Visibility into AI app usage across the org
- **DSPM for AI** — Data Security Posture Management specifically for AI workloads

---

## 3. Portal Navigation

### The New Purview Portal (`purview.microsoft.com`)

The portal is organized into solution areas accessible from the left navigation:

```
purview.microsoft.com
├── Home (dashboard, recommendations)
├── Data Security
│   ├── Information Protection
│   │   ├── Labels (sensitivity labels)
│   │   ├── Label policies
│   │   └── Auto-labeling
│   ├── Data Loss Prevention
│   │   ├── Policies
│   │   ├── Alerts
│   │   └── Activity explorer
│   ├── Insider Risk Management
│   │   ├── Alerts
│   │   ├── Cases
│   │   └── Policies
│   └── DSPM for AI
│       ├── Overview
│       ├── Policies
│       └── Data assessments
├── Data Governance
│   ├── Data Map
│   ├── Data Catalog
│   ├── Data Estate Insights
│   └── Data Sharing
├── Risk & Compliance
│   ├── Audit
│   │   ├── Audit (Standard)
│   │   └── Audit (Premium)
│   ├── eDiscovery
│   │   ├── Content Search
│   │   ├── eDiscovery (Standard)
│   │   └── eDiscovery (Premium)
│   ├── Communication Compliance
│   ├── Compliance Manager
│   └── Records Management
├── AI Hub (preview)
│   ├── AI app discovery
│   ├── AI interactions
│   └── Recommendations
└── Settings
    ├── Roles & scopes
    ├── Audit log
    └── Connected apps
```

> **GCC Note:** Not all of these are available in GCC tenants. You've already confirmed that AI Hub is missing from your GCC tenant. DSPM for AI is visible but may have limited functionality. We'll track GCC availability as we go through each module.

### The Classic Portal (`compliance.microsoft.com`)

Still exists and still works. Some admin tasks redirect here. Microsoft is migrating everything to `purview.microsoft.com` but the transition isn't complete. You may bounce between both portals during this learning process.

---

## 4. Licensing — What Requires What

This is the part that trips everyone up. Purview licensing is complex because features span multiple SKUs.

### The Simplified View

| Feature Area | Included In | Add-On Required |
|-------------|-------------|-----------------|
| **Audit (Standard)** | M365 E3, E5, G3, G5 | No |
| **Audit (Premium)** | M365 E5, G5 | E5 Compliance add-on for E3 |
| **Information Protection (basic)** | M365 E3, G3 | No |
| **Information Protection (advanced)** | M365 E5, G5 | E5 Compliance for E3 |
| **DLP (Exchange, SharePoint, OneDrive)** | M365 E3, G3 | No |
| **DLP (Teams, Endpoint, advanced)** | M365 E5, G5 | E5 Compliance for E3 |
| **Insider Risk Management** | M365 E5, G5 | E5 Compliance for E3 |
| **eDiscovery (Standard)** | M365 E3, G3 | No |
| **eDiscovery (Premium)** | M365 E5, G5 | E5 Compliance for E3 |
| **Communication Compliance** | M365 E5, G5 | E5 Compliance for E3 |
| **Data Map / Catalog** | Azure subscription | Pay-as-you-go (vCore hours) |
| **AI Hub** | M365 E3+ with Copilot licenses | Included with M365 Copilot |
| **DSPM for AI** | M365 E5, G5 | E5 Compliance for E3 |

> **Industry Standard:** Every vendor has this problem. Splunk charges by ingestion volume. Collibra charges per data asset. BigID charges per data source. Microsoft charges per user per month. The licensing model is Microsoft-specific but the "governance costs money" reality is universal.

> **For Your Demo:** The DSS scenario runs on a GCC tenant. GCC G5 licensing includes most Purview features. The key gap you've already found is AI Hub — it's not in GCC yet. When demoing to government customers, always confirm GCC feature availability.

### Power Platform Licensing Nuance

Power Platform has its **own DLP system** managed in the Power Platform Admin Center, separate from Purview DLP:

| DLP System | Where It Lives | What It Governs |
|-----------|---------------|-----------------|
| **Purview DLP** | purview.microsoft.com | M365 content: Exchange, SharePoint, OneDrive, Teams, endpoints |
| **Power Platform DLP** | admin.powerplatform.microsoft.com | Connectors: which connectors can be used together in flows/apps |

These are **two different DLP systems**. They don't share policies. They don't share the same portal. This is one of the most confusing aspects of Microsoft governance, and we'll dig deep into it in Module 04.

---

## 5. Where Power Platform Meets Purview

This is your primary interest, so let's map it out at a high level. We'll go deep in Module 09, but here's the landscape:

### What Purview Can See About Power Platform Today

| Purview Feature | Power Platform Visibility | Notes |
|----------------|--------------------------|-------|
| **Unified Audit Log** | Copilot Studio bot creation/updates, Power Automate flow runs, Power Apps launches | Activity types: `PowerPlatformAdministratorActivity`, `MicrosoftCopilot` |
| **DLP (Purview)** | Limited — if a flow writes to SharePoint/Exchange, Purview DLP can trigger on that content | Purview DLP doesn't see inside Power Platform directly |
| **DLP (Power Platform)** | Full — connector classification (Business, Non-Business, Blocked), connector groups | This is the primary governance lever for Power Platform |
| **Information Protection** | Sensitivity labels can apply to Power BI datasets, some Power Platform assets | Coverage expanding but not universal |
| **Insider Risk** | Can correlate Power Platform activity as part of risk signals | Requires E5 + configuration |
| **AI Hub** | Can detect Copilot Studio as an "AI app" and surface interaction data | Not available in GCC yet |
| **DSPM for AI** | Can assess data exposure through AI-connected data sources | You've seen this in your GCC portal — needs exploration |

### What Power Platform Admin Center Governs (Not Purview)

| Feature | What It Does |
|---------|-------------|
| **DLP Policies** | Classify connectors as Business/Non-Business/Blocked per environment |
| **Managed Environments** | Enhanced governance: sharing limits, solution checker, maker welcome content |
| **Environment Security Groups** | Control who can access each environment |
| **Tenant Isolation** | Block/allow cross-tenant connector traffic |
| **Connector Consent** | Require admin approval for certain connectors |

> **The Key Insight:** Power Platform governance is split between two systems. Purview handles the *content* and *audit trail*. Power Platform Admin Center handles the *maker experience* and *connector policies*. A complete governance story requires both.

---

## 6. Key Terminology Reference

| Term | Industry or Microsoft? | Definition |
|------|----------------------|------------|
| Data governance | Industry | Discipline of managing data availability, integrity, security |
| Data classification | Industry | Categorizing data by sensitivity or type |
| Data loss prevention (DLP) | Industry | Preventing unauthorized data sharing/exfiltration |
| Data lineage | Industry | Tracking data flow from source to destination |
| eDiscovery | Industry (legal) | Process of finding electronic information for legal proceedings |
| Records management | Industry | Managing business records through their lifecycle |
| SIEM | Industry | Security Information and Event Management |
| Sensitivity label | Microsoft | Microsoft's implementation of data classification |
| Sensitive information type (SIT) | Microsoft | Pattern/keyword definitions that identify sensitive data (SSN, credit card, etc.) |
| Unified audit log (UAL) | Microsoft | Microsoft's centralized audit log across M365 services |
| Compliance Manager | Microsoft | Assessment tool that scores your compliance posture |
| Data Map | Microsoft | Purview's metadata catalog for data assets |
| Adaptive protection | Microsoft | Dynamic DLP enforcement based on insider risk signals |
| Managed environment | Microsoft (Power Platform) | Enhanced governance mode for PP environments |
| AI Hub | Microsoft | Dashboard for AI app discovery and interaction monitoring |
| DSPM for AI | Microsoft | Data Security Posture Management for AI workloads |

---

## 7. Your Starting Position

Based on your GCC testing so far, here's what you've confirmed:

| Area | Status | Next Step |
|------|--------|-----------|
| Unified Audit Log | Working, entries found | Module 02: deep dive into activity types |
| AI Hub | Not in GCC | Track availability, test in Commercial |
| DSPM for AI | Visible in portal | Module 05: explore and document |
| Information Protection | Unknown | Module 03: check label configuration |
| Purview DLP | Unknown | Module 04: check policy configuration |
| Power Platform DLP | Unknown | Module 04: check PP Admin Center |
| eDiscovery | Unknown | Module 06: check if enabled |
| Data Map | Unknown | Module 08: check if configured |

---

## Summary

**What you should take away from this module:**

1. Data governance is an **industry discipline** with universal pillars — Microsoft didn't invent it, they implemented it
2. Microsoft Purview is the **merger of two product lines** (Azure Purview + M365 Compliance) under one brand
3. The portal is at `purview.microsoft.com` but you may still hit `compliance.microsoft.com` for some tasks
4. Licensing is E3/G3 for basics, E5/G5 for advanced features — AI Hub requires Copilot licenses
5. Power Platform governance is **split between two systems** — Purview (content/audit) and PP Admin Center (connectors/environments)
6. GCC availability lags Commercial — always verify before promising a feature to a government customer

**Next: Module 02 — Unified Audit Log** (this is where your GCC testing left off, so it's the natural next step)
