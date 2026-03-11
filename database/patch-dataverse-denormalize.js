/**
 * Add denormalized text columns to Dataverse child tables and populate them.
 * This eliminates the need for multi-step GUID lookups — the MCP can filter
 * directly on human-readable case IDs and person names.
 *
 * New columns:
 *   legal_person:          legal_caseidtext
 *   legal_timelineevent:   legal_caseidtext
 *   legal_statement:       legal_caseidtext, legal_personname
 *   legal_discrepancy:     legal_caseidtext, legal_personaname, legal_personbname
 *
 * Usage: node database/patch-dataverse-denormalize.js
 */

const ENV_URL = "https://og-dv.crm.dynamics.com";
const API_BASE = `${ENV_URL}/api/data/v9.2`;
const TENANT_ID = "125ec668-dcca-47ba-9487-0304f441b3f1";
const CLIENT_ID = "51f81489-12ee-4a9e-aaae-a2591f45987d";
const PREFIX = "legal";
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
      Prefer: "odata.maxpagesize=5000",
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

/** Fetch all pages of a collection */
async function fetchAll(endpoint) {
  const results = [];
  let url = endpoint;
  while (url) {
    const data = await api("GET", url);
    results.push(...data.value);
    url = data["@odata.nextLink"] || null;
  }
  return results;
}

// ── Column Definitions ────────────────────────────────────────

const NEW_COLUMNS = {
  [`${PREFIX}_person`]: [
    {
      schema: `${PREFIX}_caseidtext`,
      display: "Case ID (Text)",
      type: "String",
      max: 100,
      description:
        "Human-readable case number (e.g. '2024-DR-42-0892'). " +
        "Use this column to filter people by case number directly, without needing the Dataverse record GUID. " +
        "Values match legal_caseid in the Legal Case table.",
    },
  ],
  [`${PREFIX}_timelineevent`]: [
    {
      schema: `${PREFIX}_caseidtext`,
      display: "Case ID (Text)",
      type: "String",
      max: 100,
      description:
        "Human-readable case number (e.g. '2024-DR-42-0892'). " +
        "Use this column to filter timeline events by case number directly. " +
        "Values match legal_caseid in the Legal Case table.",
    },
  ],
  [`${PREFIX}_statement`]: [
    {
      schema: `${PREFIX}_caseidtext`,
      display: "Case ID (Text)",
      type: "String",
      max: 100,
      description:
        "Human-readable case number (e.g. '2024-DR-42-0892'). " +
        "Use this column to filter statements by case number directly. " +
        "Values match legal_caseid in the Legal Case table.",
    },
    {
      schema: `${PREFIX}_personname`,
      display: "Person Name",
      type: "String",
      max: 200,
      description:
        "Full name of the person who made this statement (e.g. 'Marcus Webb', 'Dena Holloway'). " +
        "Use this column to filter statements by person name directly, without needing the person's GUID. " +
        "Values match legal_fullname in the Person table.",
    },
  ],
  [`${PREFIX}_discrepancy`]: [
    {
      schema: `${PREFIX}_caseidtext`,
      display: "Case ID (Text)",
      type: "String",
      max: 100,
      description:
        "Human-readable case number (e.g. '2024-DR-42-0892'). " +
        "Use this column to filter discrepancies by case number directly. " +
        "Values match legal_caseid in the Legal Case table.",
    },
    {
      schema: `${PREFIX}_personaname`,
      display: "Person A Name",
      type: "String",
      max: 200,
      description:
        "Full name of Person A in the discrepancy (e.g. 'Marcus Webb'). " +
        "Use this to filter discrepancies involving a specific person. " +
        "Their account is in legal_personaaccount.",
    },
    {
      schema: `${PREFIX}_personbname`,
      display: "Person B Name",
      type: "String",
      max: 200,
      description:
        "Full name of Person B in the discrepancy (e.g. 'Dena Holloway'). " +
        "Use this to filter discrepancies involving a specific person. " +
        "Their account is in legal_personbaccount.",
    },
  ],
};

// ── Step 1: Add columns ───────────────────────────────────────

async function addColumns() {
  for (const [table, columns] of Object.entries(NEW_COLUMNS)) {
    console.log(`\n  ${table}:`);
    for (const col of columns) {
      const attrDef = {
        "@odata.type": "#Microsoft.Dynamics.CRM.StringAttributeMetadata",
        SchemaName: col.schema,
        DisplayName: lbl(col.display),
        Description: lbl(col.description),
        RequiredLevel: { Value: "None" },
        MaxLength: col.max,
      };

      try {
        await api(
          "POST",
          `EntityDefinitions(LogicalName='${table}')/Attributes`,
          attrDef
        );
        console.log(`    + ${col.schema}: created`);
      } catch (e) {
        if (
          (e.detail && e.detail.includes("already exists")) ||
          (e.detail && e.detail.includes("DuplicateAttributeSchemaName"))
        ) {
          console.log(`    = ${col.schema}: already exists`);
        } else {
          console.log(`    ! ${col.schema} FAILED: ${e.message}`);
          if (e.detail) console.log(`      ${e.detail.substring(0, 300)}`);
        }
      }
      await sleep(1000);
    }
  }
}

// ── Step 2: Build lookup maps ─────────────────────────────────

async function buildMaps() {
  // Case GUID → case_id text
  console.log("\n  Building case map...");
  const cases = await fetchAll(
    `${PREFIX}_legalcases?$select=${PREFIX}_legalcaseid,${PREFIX}_caseid`
  );
  const caseMap = {};
  for (const c of cases) {
    caseMap[c[`${PREFIX}_legalcaseid`]] = c[`${PREFIX}_caseid`];
  }
  console.log(`    ${Object.keys(caseMap).length} cases`);

  // Person GUID → full_name
  console.log("  Building person map...");
  const people = await fetchAll(
    `${PREFIX}_persons?$select=${PREFIX}_personid,${PREFIX}_fullname`
  );
  const personMap = {};
  for (const p of people) {
    personMap[p[`${PREFIX}_personid`]] = p[`${PREFIX}_fullname`];
  }
  console.log(`    ${Object.keys(personMap).length} people`);

  return { caseMap, personMap };
}

// ── Step 3: Populate denormalized columns ─────────────────────

async function populateTable(tableName, collectionName, idField, lookupFields, caseMap, personMap) {
  // Build $select with id + all lookup value fields
  const selectFields = [idField];
  const lookupValueFields = {};
  for (const [colName, lookupSchema] of Object.entries(lookupFields)) {
    const valueField = `_${lookupSchema.toLowerCase()}_value`;
    selectFields.push(valueField);
    lookupValueFields[colName] = valueField;
  }

  console.log(`\n  Populating ${tableName}...`);
  const records = await fetchAll(
    `${collectionName}?$select=${selectFields.join(",")}`
  );
  console.log(`    ${records.length} records to update`);

  let updated = 0;
  let skipped = 0;
  let errors = 0;

  for (const rec of records) {
    const patch = {};
    let hasData = false;

    for (const [colName, valueField] of Object.entries(lookupValueFields)) {
      const guid = rec[valueField];
      if (!guid) continue;

      let resolvedValue;
      if (colName.includes("caseidtext")) {
        resolvedValue = caseMap[guid];
      } else {
        resolvedValue = personMap[guid];
      }

      if (resolvedValue) {
        patch[colName] = resolvedValue;
        hasData = true;
      }
    }

    if (!hasData) {
      skipped++;
      continue;
    }

    try {
      await api("PATCH", `${collectionName}(${rec[idField]})`, patch);
      updated++;
      if (updated % 50 === 0) process.stdout.write(".");
    } catch (e) {
      errors++;
      if (errors <= 3) {
        console.error(`\n    ERR ${rec[idField]}: ${e.message}`);
        if (e.detail) console.error(`    ${e.detail.substring(0, 200)}`);
      }
    }
  }
  console.log(`\n    Done: ${updated} updated, ${skipped} skipped, ${errors} errors`);
}

// ── Main ──────────────────────────────────────────────────────

async function main() {
  console.log("=".repeat(55));
  console.log("  Denormalize Dataverse Tables");
  console.log("  Target:", ENV_URL);
  console.log("=".repeat(55));

  console.log("\nStep 1: Authenticate");
  await authenticate();
  const me = await api("GET", "WhoAmI");
  console.log(`  Connected as ${me.UserId}`);

  console.log("\nStep 2: Add denormalized columns");
  await addColumns();

  console.log("\nStep 3: Publish (make columns available)");
  await api("POST", "PublishAllXml", {});
  console.log("  Published");

  // Wait for publish to propagate
  console.log("  Waiting 10s for propagation...");
  await sleep(10000);

  console.log("\nStep 4: Build lookup maps");
  const { caseMap, personMap } = await buildMaps();

  console.log("\nStep 5: Populate denormalized columns");

  // People: caseidtext
  await populateTable(
    `${PREFIX}_person`,
    `${PREFIX}_persons`,
    `${PREFIX}_personid`,
    { [`${PREFIX}_caseidtext`]: `${PREFIX}_LegalCaseId` },
    caseMap,
    personMap
  );

  // Timeline Events: caseidtext
  await populateTable(
    `${PREFIX}_timelineevent`,
    `${PREFIX}_timelineevents`,
    `${PREFIX}_timelineeventid`,
    { [`${PREFIX}_caseidtext`]: `${PREFIX}_LegalCaseId` },
    caseMap,
    personMap
  );

  // Statements: caseidtext, personname
  await populateTable(
    `${PREFIX}_statement`,
    `${PREFIX}_statements`,
    `${PREFIX}_statementid`,
    {
      [`${PREFIX}_caseidtext`]: `${PREFIX}_LegalCaseId`,
      [`${PREFIX}_personname`]: `${PREFIX}_PersonId`,
    },
    caseMap,
    personMap
  );

  // Discrepancies: caseidtext, personaname, personbname
  await populateTable(
    `${PREFIX}_discrepancy`,
    `${PREFIX}_discrepancies`,
    `${PREFIX}_discrepancyid`,
    {
      [`${PREFIX}_caseidtext`]: `${PREFIX}_LegalCaseId`,
      [`${PREFIX}_personaname`]: `${PREFIX}_PersonAId`,
      [`${PREFIX}_personbname`]: `${PREFIX}_PersonBId`,
    },
    caseMap,
    personMap
  );

  console.log("\nStep 6: Final publish");
  await api("POST", "PublishAllXml", {});
  console.log("  Published all customizations");

  console.log("\nDone. Denormalized columns added and populated.");
}

main().catch((e) => {
  console.error("\nFatal:", e.message);
  if (e.detail) console.error(e.detail);
  process.exit(1);
});
