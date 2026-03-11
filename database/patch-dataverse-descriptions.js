/**
 * Patch rich descriptions onto Dataverse tables and columns
 * so the Dataverse MCP server exposes better tool metadata.
 *
 * Usage: node database/patch-dataverse-descriptions.js
 */

const ENV_URL = "https://og-dv.crm.dynamics.com";
const API_BASE = `${ENV_URL}/api/data/v9.2`;
const TENANT_ID = "125ec668-dcca-47ba-9487-0304f441b3f1";
const CLIENT_ID = "51f81489-12ee-4a9e-aaae-a2591f45987d";
const LANG = 1033;

let TOKEN;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const lbl = (text) => ({
  "@odata.type": "Microsoft.Dynamics.CRM.Label",
  LocalizedLabels: [
    {
      "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
      Label: text,
      LanguageCode: LANG,
    },
  ],
});

// ── Auth ──────────────────────────────────────────────────────
async function authenticate() {
  const scope = `${ENV_URL}/.default offline_access`;
  const loginBase = "https://login.microsoftonline.com";

  const dcRes = await fetch(
    `${loginBase}/${TENANT_ID}/oauth2/v2.0/devicecode`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `client_id=${CLIENT_ID}&scope=${encodeURIComponent(scope)}`,
    }
  );
  const dc = await dcRes.json();
  if (dc.error) throw new Error(`Device code failed: ${dc.error_description || dc.error}`);
  console.log(`\n  ${dc.message}\n`);

  const interval = (dc.interval || 5) * 1000;
  while (true) {
    await sleep(interval);
    const tokenRes = await fetch(
      `${loginBase}/${TENANT_ID}/oauth2/v2.0/token`,
      {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: [
          `client_id=${CLIENT_ID}`,
          `grant_type=urn:ietf:params:oauth:grant-type:device_code`,
          `device_code=${dc.device_code}`,
        ].join("&"),
      }
    );
    const td = await tokenRes.json();
    if (td.access_token) {
      TOKEN = td.access_token;
      return;
    }
    if (td.error === "authorization_pending") {
      process.stdout.write(".");
      continue;
    }
    throw new Error(`Auth failed: ${td.error_description || td.error}`);
  }
}

// ── API Helper ────────────────────────────────────────────────
async function api(method, endpoint, body = null) {
  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE}/${endpoint}`;
  const opts = {
    method,
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      "Content-Type": "application/json",
      "OData-MaxVersion": "4.0",
      "OData-Version": "4.0",
      Accept: "application/json",
    },
  };
  if (body) opts.body = JSON.stringify(body);

  for (let attempt = 0; attempt < 5; attempt++) {
    const res = await fetch(url, opts);
    if (res.status === 429 || res.status === 503) {
      const wait = Math.pow(2, attempt + 1) * 5000;
      console.log(`    (${res.status} retry in ${wait / 1000}s...)`);
      await sleep(wait);
      continue;
    }
    if (!res.ok) {
      const text = await res.text();
      const err = new Error(`${method} ${endpoint}: ${res.status}`);
      err.detail = text.substring(0, 600);
      throw err;
    }
    if (res.status === 204) return null;
    const ct = res.headers.get("content-type") || "";
    return ct.includes("json") ? res.json() : null;
  }
  throw new Error(`${method} ${endpoint}: exhausted retries`);
}

// ── Description Definitions ───────────────────────────────────

const TABLE_DESCRIPTIONS = {
  legal_legalcase:
    "50 legal cases. The primary identifier is legal_caseid, a text field with values like '2024-DR-42-0892'. " +
    "This is NOT the Dataverse record ID (GUID). Filter cases by legal_casetype (stored as full text: " +
    "'Child Protective Services', 'Termination of Parental Rights', 'Adult Protective Services', " +
    "'Adoption', 'Guardianship', 'Interstate Compact' — never use abbreviations like CPS or TPR), " +
    "legal_county, legal_circuit, or legal_status (Active, Closed, Pending Review, Dismissed). " +
    "To find related records in People, Timeline Events, Statements, or Discrepancies, first query this table " +
    "to get the record's Dataverse ID, then use that ID to filter the lookup column in the related table.",

  legal_person:
    "277 people linked to legal cases. Each person has a legal_fullname (text), legal_role, " +
    "legal_relationship (describes their connection to the case), legal_dob, legal_notes, " +
    "and legal_caseidtext (the human-readable case number like '2024-DR-42-0892'). " +
    "Filter by legal_caseidtext to find all people on a case. " +
    "To find a person's statements, filter the Statement table by legal_personname.",

  legal_timelineevent:
    "333 chronological events linked to legal cases. Each event has legal_eventdate, " +
    "legal_eventtime (text like '9:30 PM'), legal_eventtype, legal_description (detailed narrative), " +
    "legal_sourcedocument, legal_partiesinvolved, and legal_caseidtext (the human-readable case number). " +
    "Filter by legal_caseidtext to get all events for a case. " +
    "Sort by legal_eventdate and legal_eventtime for chronological order.",

  legal_statement:
    "338 recorded statements from people involved in legal cases. Each statement has legal_statementdate, " +
    "legal_madeto (values: 'Medical Staff', 'Law Enforcement', 'Case Manager', 'Court'), " +
    "legal_statementtext (the full verbatim text), legal_sourcedocument, legal_pagereference, " +
    "legal_caseidtext (case number like '2024-DR-42-0892'), and legal_personname (who made the statement). " +
    "Filter by legal_personname to find statements by a specific person. " +
    "Filter by legal_caseidtext to find statements for a specific case. " +
    "Filter by legal_madeto to find statements made to a specific recipient type.",

  legal_discrepancy:
    "151 contradictions between accounts from different people on the same case. " +
    "Each record has legal_topic (what the contradiction is about), legal_personaaccount (what Person A said), " +
    "legal_personbaccount (what Person B said), legal_contradictedby (evidence that contradicts), " +
    "legal_sourcedocument, legal_caseidtext (case number like '2024-DR-42-0892'), " +
    "legal_personaname (Person A's name), and legal_personbname (Person B's name). " +
    "Filter by legal_caseidtext to find all discrepancies for a case. " +
    "Filter by legal_personaname or legal_personbname to find discrepancies involving a specific person.",
};

const COLUMN_DESCRIPTIONS = {
  legal_legalcase: {
    legal_caseid:
      "The human-readable case number, e.g. '2024-DR-42-0892'. This is the primary text identifier used in queries. " +
      "This is NOT the Dataverse record GUID.",
    legal_casetitle:
      "Case title, typically in format 'DSS v. LastName -- CaseType', e.g. 'DSS v. Webb/Holloway -- CPS'.",
    legal_casetype:
      "Type of legal case. Stored values are the full text: 'Child Protective Services' (users may say CPS), " +
      "'Termination of Parental Rights' (users may say TPR), 'Adult Protective Services' (users may say APS), " +
      "'Adoption', 'Guardianship', 'Interstate Compact' (users may say ICPC). " +
      "Always filter on the full text value, never the abbreviation.",
    legal_circuit:
      "Judicial circuit number, e.g. '7th Circuit'. There are 16 circuits.",
    legal_county:
      "County name, e.g. 'Spartanburg', 'Richland'. There are 46 counties across the dataset.",
    legal_fileddate:
      "Date the case was filed with the court.",
    legal_status:
      "Current case status. Values: Active, Closed, Pending Review, Dismissed.",
    legal_plaintiff:
      "The plaintiff, typically 'Department of Social Services' or 'DSS'.",
    legal_summary:
      "Narrative summary of the case including key facts, parties, and current posture.",
  },

  legal_person: {
    legal_fullname:
      "Person's full name, e.g. 'Marcus Webb', 'Dena Holloway', 'Crystal Price'. Use this to search for specific individuals.",
    legal_role:
      "Person's role in the case. Values: Mother, Father, Child, Caseworker, Attorney, Guardian ad Litem, " +
      "Therapist, Physician, Teacher, Neighbor, Relative, Foster Parent, Law Enforcement, Judge.",
    legal_relationship:
      "Describes the person's specific relationship to the case, e.g. 'Biological father of Jaylen Webb', " +
      "'Assigned DSS caseworker', 'Presiding Family Court judge'.",
    legal_dob:
      "Person's date of birth.",
    legal_notes:
      "Additional notes about the person relevant to the case.",
    legal_caseidtext:
      "Human-readable case number (e.g. '2024-DR-42-0892'). Use this to filter people by case number " +
      "directly without needing the Dataverse record GUID. Values match legal_caseid in the Legal Case table.",
  },

  legal_timelineevent: {
    legal_name:
      "Short label for the event, e.g. 'ER Admission', 'Sheriff Interview', 'Probable Cause Hearing'.",
    legal_eventdate:
      "Date the event occurred. Use this with legal_eventtime for full chronological ordering.",
    legal_eventtime:
      "Time of day the event occurred, stored as text (e.g. '3:15 AM', '1:30 PM'). May be empty if time is unknown.",
    legal_eventtype:
      "Category of event. Values: Incident, Investigation, Court Hearing, Home Visit, Medical Exam, " +
      "Interview, Placement, Service Referral, Report Filed, Emergency Action, Family, Medical, " +
      "Law Enforcement, DSS Action, Court.",
    legal_description:
      "Detailed narrative description of what happened during this event, including specifics about " +
      "findings, statements made, and actions taken.",
    legal_sourcedocument:
      "Source document reference, e.g. 'Medical Records, pp. 1-4', 'Sheriff Report #24-06-4418, p. 1'.",
    legal_partiesinvolved:
      "Names of people involved in this event, comma-separated.",
    legal_caseidtext:
      "Human-readable case number (e.g. '2024-DR-42-0892'). Use this to filter timeline events by case " +
      "number directly without needing the Dataverse record GUID.",
  },

  legal_statement: {
    legal_name:
      "Short label for the statement, e.g. 'Marcus Webb - Hospital Statement', 'Dena Holloway - Sheriff Interview'.",
    legal_statementdate:
      "Date the statement was made.",
    legal_madeto:
      "Category of who received the statement. Values: 'Medical Staff', 'Law Enforcement', 'Case Manager', 'Court'. " +
      "Use this to filter statements by recipient type (e.g. WHERE legal_madeto = 'Medical Staff').",
    legal_statementtext:
      "The full verbatim text of what the person said. This is the primary content field for analyzing " +
      "what someone reported, claimed, or disclosed.",
    legal_sourcedocument:
      "Source document reference, e.g. 'Dictation PDF, p. 3', 'Sheriff Report #24-06-4418, pp. 3-5'.",
    legal_pagereference:
      "Specific page number(s) in the source document.",
    legal_caseidtext:
      "Human-readable case number (e.g. '2024-DR-42-0892'). Use this to filter statements by case " +
      "number directly without needing the Dataverse record GUID.",
    legal_personname:
      "Full name of the person who made this statement (e.g. 'Marcus Webb', 'Dena Holloway'). " +
      "Use this to filter statements by person name directly without needing the person's GUID.",
  },

  legal_discrepancy: {
    legal_topic:
      "What the contradiction is about, e.g. 'Timeline of injury discovery', 'Bedtime routine', " +
      "'Knowledge of prior injuries'. Use this to search for discrepancies on a specific subject.",
    legal_personaaccount:
      "What Person A said or claimed about the topic.",
    legal_personbaccount:
      "What Person B said or claimed about the same topic -- contradicting Person A's account.",
    legal_contradictedby:
      "Evidence or facts that contradict one or both accounts, e.g. medical findings, timeline inconsistencies.",
    legal_sourcedocument:
      "Source document where the discrepancy was identified.",
    legal_caseidtext:
      "Human-readable case number (e.g. '2024-DR-42-0892'). Use this to filter discrepancies by case " +
      "number directly without needing the Dataverse record GUID.",
    legal_personaname:
      "Full name of Person A in the discrepancy (e.g. 'Marcus Webb'). Use this to filter discrepancies " +
      "involving a specific person. Their account is in legal_personaaccount.",
    legal_personbname:
      "Full name of Person B in the discrepancy (e.g. 'Dena Holloway'). Use this to filter discrepancies " +
      "involving a specific person. Their account is in legal_personbaccount.",
  },
};

// ── Patch Functions ───────────────────────────────────────────

async function patchTableDescription(logicalName, description) {
  // Get the entity metadata first to retrieve MetadataId and required fields
  const entity = await api(
    "GET",
    `EntityDefinitions(LogicalName='${logicalName}')?$select=MetadataId,SchemaName,DisplayName,DisplayCollectionName,HasNotes,HasActivities,IsActivity`
  );

  // PUT full entity definition with updated Description
  await api("PUT", `EntityDefinitions(${entity.MetadataId})`, {
    "@odata.type": "#Microsoft.Dynamics.CRM.EntityMetadata",
    MetadataId: entity.MetadataId,
    SchemaName: entity.SchemaName,
    DisplayName: entity.DisplayName,
    DisplayCollectionName: entity.DisplayCollectionName,
    Description: lbl(description),
    HasNotes: entity.HasNotes,
    HasActivities: entity.HasActivities,
    IsActivity: entity.IsActivity,
  });
  console.log(`  Table ${logicalName}: patched`);
}

async function patchColumnDescription(tableName, columnName, description) {
  // Get the attribute metadata to find its type and MetadataId
  const attr = await api(
    "GET",
    `EntityDefinitions(LogicalName='${tableName}')/Attributes(LogicalName='${columnName}')?$select=MetadataId,AttributeType,SchemaName,DisplayName,RequiredLevel`
  );

  // Map AttributeType to OData type
  const typeMap = {
    String: "#Microsoft.Dynamics.CRM.StringAttributeMetadata",
    Memo: "#Microsoft.Dynamics.CRM.MemoAttributeMetadata",
    DateTime: "#Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
    Uniqueidentifier: "#Microsoft.Dynamics.CRM.UniqueIdentifierAttributeMetadata",
    Lookup: "#Microsoft.Dynamics.CRM.LookupAttributeMetadata",
  };
  const odataType = typeMap[attr.AttributeType] || "#Microsoft.Dynamics.CRM.AttributeMetadata";

  try {
    await api(
      "PUT",
      `EntityDefinitions(LogicalName='${tableName}')/Attributes(${attr.MetadataId})`,
      {
        "@odata.type": odataType,
        MetadataId: attr.MetadataId,
        SchemaName: attr.SchemaName,
        DisplayName: attr.DisplayName,
        RequiredLevel: attr.RequiredLevel,
        Description: lbl(description),
      }
    );
    console.log(`    ${columnName}: patched`);
  } catch (e) {
    console.log(`    ${columnName}: SKIP (${e.message})`);
    if (e.detail) console.log(`      ${e.detail.substring(0, 200)}`);
  }
}

// ── Main ──────────────────────────────────────────────────────

async function main() {
  console.log("=".repeat(50));
  console.log("  Patch Dataverse Descriptions");
  console.log("  Target:", ENV_URL);
  console.log("=".repeat(50));

  console.log("\nStep 1: Authenticate");
  await authenticate();
  const me = await api("GET", "WhoAmI");
  console.log(`  Connected as ${me.UserId}`);

  console.log("\nStep 2: Patch table descriptions");
  for (const [table, desc] of Object.entries(TABLE_DESCRIPTIONS)) {
    await patchTableDescription(table, desc);
  }

  console.log("\nStep 3: Patch column descriptions");
  for (const [table, columns] of Object.entries(COLUMN_DESCRIPTIONS)) {
    console.log(`\n  ${table}:`);
    for (const [col, desc] of Object.entries(columns)) {
      await patchColumnDescription(table, col, desc);
    }
  }

  console.log("\nStep 4: Publish customizations");
  await api("POST", "PublishAllXml");
  console.log("  Published all customizations");

  console.log("\nDone. Descriptions patched and published.");
}

main().catch((e) => {
  console.error("\nFatal:", e.message);
  if (e.detail) console.error(e.detail);
  process.exit(1);
});
