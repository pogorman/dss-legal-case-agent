/**
 * Deploy DSS Legal Case Agent schema and data to Dataverse (GCC).
 * Creates publisher, solution, 5 custom tables with relationships, views,
 * model-driven app, and loads all 50 cases of data.
 *
 * Prerequisites: pac auth profile configured for og-ai GCC environment
 * Usage: node database/deploy-dataverse.js [--schema-only] [--data-only]
 */

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

// ── Configuration ──────────────────────────────────────────────
const ENV_URL = "https://og-dv.crm.dynamics.com";
const API_BASE = `${ENV_URL}/api/data/v9.2`;
const TENANT_ID = "125ec668-dcca-47ba-9487-0304f441b3f1";
const CLIENT_ID = "51f81489-12ee-4a9e-aaae-a2591f45987d"; // Power Apps public client
const PREFIX = "legal";
const SOLUTION_UNIQUE = "LegalCaseAgent";
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

// ── Auth (Device Code Flow) ────────────────────────────────────
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
  if (dc.error) {
    throw new Error(`Device code failed: ${dc.error_description || dc.error}`);
  }

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

// ── API Helpers ────────────────────────────────────────────────
async function api(method, endpoint, body = null) {
  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE}/${endpoint}`;
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

async function apiCreate(endpoint, body) {
  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE}/${endpoint}`;

  for (let attempt = 0; attempt < 5; attempt++) {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${TOKEN}`,
        "Content-Type": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        Accept: "application/json",
        Prefer: "return=representation",
      },
      body: JSON.stringify(body),
    });
    if (res.status === 429 || res.status === 503) {
      const wait = Math.pow(2, attempt + 1) * 5000;
      console.log(`    (${res.status} retry in ${wait / 1000}s...)`);
      await sleep(wait);
      continue;
    }
    if (!res.ok) {
      const text = await res.text();
      const err = new Error(`POST ${endpoint}: ${res.status}`);
      err.detail = text.substring(0, 600);
      throw err;
    }
    // Try OData-EntityId header first
    const entityId = res.headers.get("OData-EntityId");
    if (entityId) {
      const match = entityId.match(/\(([0-9a-f-]+)\)/i);
      if (match) return match[1];
    }
    // Try response body
    if (res.status !== 204) {
      const ct = res.headers.get("content-type") || "";
      if (ct.includes("json")) {
        const data = await res.json();
        for (const key of Object.keys(data)) {
          if (
            key.endsWith("id") &&
            typeof data[key] === "string" &&
            /^[0-9a-f-]{36}$/i.test(data[key])
          ) {
            return data[key];
          }
        }
      }
    }
    return null;
  }
  throw new Error(`POST ${endpoint}: exhausted retries`);
}

// ── SQL Parser ─────────────────────────────────────────────────
function parseSqlFile(filePath) {
  const content = fs.readFileSync(filePath, "utf-8");
  const records = {
    cases: [],
    people: [],
    timeline_events: [],
    statements: [],
    discrepancies: [],
  };

  const blocks = content
    .split(/(?=INSERT\s+INTO\s+)/i)
    .filter((b) => /^INSERT/i.test(b.trim()));

  for (const block of blocks) {
    const m = block.match(/INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES?\s*/i);
    if (!m) continue;
    const table = m[1].toLowerCase();
    if (!records[table]) continue;

    const columns = m[2].split(",").map((c) => c.trim());
    // Strip SQL comment lines before parsing values
    const valuesRaw = block.substring(m[0].length);
    const valuesClean = valuesRaw
      .split("\n")
      .filter((line) => !line.trimStart().startsWith("--"))
      .join("\n");
    const tuples = parseValueTuples(valuesClean);

    for (const values of tuples) {
      const row = {};
      columns.forEach((col, i) => {
        row[col] = i < values.length ? values[i] : null;
      });
      records[table].push(row);
    }
  }

  return records;
}

function parseValueTuples(str) {
  const tuples = [];
  let i = 0;
  while (i < str.length) {
    while (i < str.length && str[i] !== "(") i++;
    if (i >= str.length) break;
    i++;

    const values = [];
    while (i < str.length) {
      while (i < str.length && /\s/.test(str[i])) i++;
      if (str[i] === ")") {
        i++;
        break;
      }
      if (str[i] === ",") {
        i++;
        continue;
      }

      if (str[i] === "'") {
        i++;
        let s = "";
        while (i < str.length) {
          if (str[i] === "'" && i + 1 < str.length && str[i + 1] === "'") {
            s += "'";
            i += 2;
          } else if (str[i] === "'") {
            i++;
            break;
          } else {
            s += str[i];
            i++;
          }
        }
        values.push(s);
      } else if (str.substring(i, i + 4).toUpperCase() === "NULL") {
        values.push(null);
        i += 4;
      } else {
        let n = "";
        while (i < str.length && /[0-9.\-]/.test(str[i])) {
          n += str[i];
          i++;
        }
        if (n) values.push(n.includes(".") ? parseFloat(n) : parseInt(n, 10));
        else i++; // skip unrecognized character to avoid infinite loop
      }
    }

    if (values.length > 0) tuples.push(values);
  }
  return tuples;
}

// ── Schema Definitions ─────────────────────────────────────────
const ENTITIES = [
  {
    schema: `${PREFIX}_legalcase`,
    collection: `${PREFIX}_legalcases`,
    display: "Legal Case",
    displayPlural: "Legal Cases",
    primaryName: {
      schema: `${PREFIX}_caseid`,
      display: "Case ID",
      maxLength: 100,
    },
    columns: [
      {
        schema: `${PREFIX}_casetitle`,
        display: "Case Title",
        type: "String",
        max: 200,
      },
      {
        schema: `${PREFIX}_casetype`,
        display: "Case Type",
        type: "String",
        max: 100,
      },
      {
        schema: `${PREFIX}_circuit`,
        display: "Circuit",
        type: "String",
        max: 100,
      },
      {
        schema: `${PREFIX}_county`,
        display: "County",
        type: "String",
        max: 100,
      },
      {
        schema: `${PREFIX}_fileddate`,
        display: "Filed Date",
        type: "DateTime",
      },
      {
        schema: `${PREFIX}_status`,
        display: "Status",
        type: "String",
        max: 50,
      },
      {
        schema: `${PREFIX}_plaintiff`,
        display: "Plaintiff",
        type: "String",
        max: 200,
      },
      {
        schema: `${PREFIX}_summary`,
        display: "Summary",
        type: "Memo",
        max: 10000,
      },
    ],
  },
  {
    schema: `${PREFIX}_person`,
    collection: `${PREFIX}_persons`,
    display: "Person",
    displayPlural: "People",
    primaryName: {
      schema: `${PREFIX}_fullname`,
      display: "Full Name",
      maxLength: 200,
    },
    columns: [
      {
        schema: `${PREFIX}_role`,
        display: "Role",
        type: "String",
        max: 100,
      },
      {
        schema: `${PREFIX}_relationship`,
        display: "Relationship",
        type: "String",
        max: 500,
      },
      {
        schema: `${PREFIX}_dob`,
        display: "Date of Birth",
        type: "DateTime",
      },
      {
        schema: `${PREFIX}_notes`,
        display: "Notes",
        type: "Memo",
        max: 10000,
      },
      {
        schema: `${PREFIX}_caseidtext`,
        display: "Case ID (Text)",
        type: "String",
        max: 100,
      },
    ],
  },
  {
    schema: `${PREFIX}_timelineevent`,
    collection: `${PREFIX}_timelineevents`,
    display: "Timeline Event",
    displayPlural: "Timeline Events",
    primaryName: {
      schema: `${PREFIX}_name`,
      display: "Name",
      maxLength: 200,
    },
    columns: [
      {
        schema: `${PREFIX}_eventdate`,
        display: "Event Date",
        type: "DateTime",
      },
      {
        schema: `${PREFIX}_eventtime`,
        display: "Event Time",
        type: "String",
        max: 20,
      },
      {
        schema: `${PREFIX}_eventtype`,
        display: "Event Type",
        type: "String",
        max: 100,
      },
      {
        schema: `${PREFIX}_description`,
        display: "Description",
        type: "Memo",
        max: 10000,
      },
      {
        schema: `${PREFIX}_sourcedocument`,
        display: "Source Document",
        type: "String",
        max: 500,
      },
      {
        schema: `${PREFIX}_partiesinvolved`,
        display: "Parties Involved",
        type: "Memo",
        max: 10000,
      },
      {
        schema: `${PREFIX}_caseidtext`,
        display: "Case ID (Text)",
        type: "String",
        max: 100,
      },
    ],
  },
  {
    schema: `${PREFIX}_statement`,
    collection: `${PREFIX}_statements`,
    display: "Statement",
    displayPlural: "Statements",
    primaryName: {
      schema: `${PREFIX}_name`,
      display: "Name",
      maxLength: 200,
    },
    columns: [
      {
        schema: `${PREFIX}_statementdate`,
        display: "Statement Date",
        type: "DateTime",
      },
      {
        schema: `${PREFIX}_madeto`,
        display: "Made To",
        type: "String",
        max: 100,
      },
      {
        schema: `${PREFIX}_statementtext`,
        display: "Statement Text",
        type: "Memo",
        max: 10000,
      },
      {
        schema: `${PREFIX}_sourcedocument`,
        display: "Source Document",
        type: "String",
        max: 500,
      },
      {
        schema: `${PREFIX}_pagereference`,
        display: "Page Reference",
        type: "String",
        max: 100,
      },
      {
        schema: `${PREFIX}_caseidtext`,
        display: "Case ID (Text)",
        type: "String",
        max: 100,
      },
      {
        schema: `${PREFIX}_personname`,
        display: "Person Name",
        type: "String",
        max: 200,
      },
    ],
  },
  {
    schema: `${PREFIX}_discrepancy`,
    collection: `${PREFIX}_discrepancies`,
    display: "Discrepancy",
    displayPlural: "Discrepancies",
    primaryName: {
      schema: `${PREFIX}_topic`,
      display: "Topic",
      maxLength: 200,
    },
    columns: [
      {
        schema: `${PREFIX}_personaaccount`,
        display: "Person A Account",
        type: "Memo",
        max: 10000,
      },
      {
        schema: `${PREFIX}_personbaccount`,
        display: "Person B Account",
        type: "Memo",
        max: 10000,
      },
      {
        schema: `${PREFIX}_contradictedby`,
        display: "Contradicted By",
        type: "Memo",
        max: 10000,
      },
      {
        schema: `${PREFIX}_sourcedocument`,
        display: "Source Document",
        type: "String",
        max: 500,
      },
      {
        schema: `${PREFIX}_caseidtext`,
        display: "Case ID (Text)",
        type: "String",
        max: 100,
      },
      {
        schema: `${PREFIX}_personaname`,
        display: "Person A Name",
        type: "String",
        max: 200,
      },
      {
        schema: `${PREFIX}_personbname`,
        display: "Person B Name",
        type: "String",
        max: 200,
      },
    ],
  },
];

const RELATIONSHIPS = [
  {
    name: `${PREFIX}_legalcase_person`,
    referenced: `${PREFIX}_legalcase`,
    referencing: `${PREFIX}_person`,
    lookup: `${PREFIX}_LegalCaseId`,
    display: "Legal Case",
    required: true,
  },
  {
    name: `${PREFIX}_legalcase_timelineevent`,
    referenced: `${PREFIX}_legalcase`,
    referencing: `${PREFIX}_timelineevent`,
    lookup: `${PREFIX}_LegalCaseId`,
    display: "Legal Case",
    required: true,
  },
  {
    name: `${PREFIX}_legalcase_statement`,
    referenced: `${PREFIX}_legalcase`,
    referencing: `${PREFIX}_statement`,
    lookup: `${PREFIX}_LegalCaseId`,
    display: "Legal Case",
    required: true,
  },
  {
    name: `${PREFIX}_person_statement`,
    referenced: `${PREFIX}_person`,
    referencing: `${PREFIX}_statement`,
    lookup: `${PREFIX}_PersonId`,
    display: "Person",
    required: false,
  },
  {
    name: `${PREFIX}_legalcase_discrepancy`,
    referenced: `${PREFIX}_legalcase`,
    referencing: `${PREFIX}_discrepancy`,
    lookup: `${PREFIX}_LegalCaseId`,
    display: "Legal Case",
    required: true,
  },
  {
    name: `${PREFIX}_persona_discrepancy`,
    referenced: `${PREFIX}_person`,
    referencing: `${PREFIX}_discrepancy`,
    lookup: `${PREFIX}_PersonAId`,
    display: "Person A",
    required: false,
  },
  {
    name: `${PREFIX}_personb_discrepancy`,
    referenced: `${PREFIX}_person`,
    referencing: `${PREFIX}_discrepancy`,
    lookup: `${PREFIX}_PersonBId`,
    display: "Person B",
    required: false,
  },
];

// ── Publisher & Solution ───────────────────────────────────────
async function ensurePublisherAndSolution() {
  // Publisher
  const pubs = await api(
    "GET",
    `publishers?$filter=uniquename eq '${PREFIX}'&$select=publisherid`
  );
  let publisherId;
  if (pubs.value.length > 0) {
    publisherId = pubs.value[0].publisherid;
    console.log(`  Publisher '${PREFIX}' exists`);
  } else {
    await api("POST", "publishers", {
      uniquename: PREFIX,
      friendlyname: "Legal",
      customizationprefix: PREFIX,
      customizationoptionvalueprefix: 18200,
    });
    // Query back to get the ID (POST may return 204)
    const created = await api(
      "GET",
      `publishers?$filter=uniquename eq '${PREFIX}'&$select=publisherid`
    );
    publisherId = created.value[0].publisherid;
    console.log(`  Created publisher '${PREFIX}' (${publisherId})`);
  }

  // Solution
  const sols = await api(
    "GET",
    `solutions?$filter=uniquename eq '${SOLUTION_UNIQUE}'&$select=solutionid`
  );
  if (sols.value.length > 0) {
    console.log(`  Solution '${SOLUTION_UNIQUE}' exists`);
    return;
  }
  await api("POST", "solutions", {
    uniquename: SOLUTION_UNIQUE,
    friendlyname: "Legal Case Agent",
    description:
      "DSS Legal Case Agent — tables, views, forms, and model-driven app",
    version: "1.0.0.0",
    "publisherid@odata.bind": `/publishers(${publisherId})`,
  });
  console.log(`  Created solution '${SOLUTION_UNIQUE}'`);
}

// ── Create Tables ──────────────────────────────────────────────
async function createTables() {
  for (const entity of ENTITIES) {
    console.log(`\n  Table: ${entity.display}`);

    let entityExists = false;
    try {
      await api(
        "GET",
        `EntityDefinitions(LogicalName='${entity.schema}')?$select=MetadataId`
      );
      console.log(`    Entity exists`);
      entityExists = true;
    } catch (e) {
      if (!e.message.includes("404")) throw e;
    }

    if (!entityExists) {
      // Create entity with primary name attribute
      const entityDef = {
        "@odata.type": "#Microsoft.Dynamics.CRM.EntityMetadata",
        SchemaName: entity.schema,
        CollectionSchemaName: entity.collection,
        DisplayName: lbl(entity.display),
        DisplayCollectionName: lbl(entity.displayPlural),
        Description: lbl(`${entity.display} for Legal Case Agent`),
        HasNotes: false,
        HasActivities: false,
        OwnershipType: "UserOwned",
        IsActivity: false,
        PrimaryNameAttribute: entity.primaryName.schema,
        Attributes: [
          {
            "@odata.type": "#Microsoft.Dynamics.CRM.StringAttributeMetadata",
            SchemaName: entity.primaryName.schema,
            DisplayName: lbl(entity.primaryName.display),
            RequiredLevel: { Value: "ApplicationRequired" },
            MaxLength: entity.primaryName.maxLength,
            IsPrimaryName: true,
          },
        ],
      };

      await api("POST", "EntityDefinitions", entityDef);
      console.log(`    Created entity`);
      console.log(`    Waiting 20s for provisioning...`);
      await sleep(20000); // GCC needs extra time
    }

    // Add columns (always runs, even if entity existed — catches partial deploys)
    for (const col of entity.columns) {
      let attrDef;
      if (col.type === "String") {
        attrDef = {
          "@odata.type": "#Microsoft.Dynamics.CRM.StringAttributeMetadata",
          SchemaName: col.schema,
          DisplayName: lbl(col.display),
          RequiredLevel: { Value: "None" },
          MaxLength: col.max,
        };
      } else if (col.type === "Memo") {
        attrDef = {
          "@odata.type": "#Microsoft.Dynamics.CRM.MemoAttributeMetadata",
          SchemaName: col.schema,
          DisplayName: lbl(col.display),
          RequiredLevel: { Value: "None" },
          MaxLength: col.max,
          Format: "Text",
        };
      } else if (col.type === "DateTime") {
        attrDef = {
          "@odata.type": "#Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
          SchemaName: col.schema,
          DisplayName: lbl(col.display),
          RequiredLevel: { Value: "None" },
          Format: "DateOnly",
          DateTimeBehavior: { Value: "DateOnly" },
        };
      }

      try {
        await api(
          "POST",
          `EntityDefinitions(LogicalName='${entity.schema}')/Attributes`,
          attrDef
        );
        console.log(`    + ${col.display}`);
      } catch (e) {
        if (
          (e.detail && e.detail.includes("already exists")) ||
          (e.detail && e.detail.includes("DuplicateAttributeSchemaName"))
        ) {
          console.log(`    = ${col.display} (exists)`);
        } else {
          console.log(`    ! ${col.display} FAILED: ${e.message}`);
          if (e.detail) console.log(`      ${e.detail.substring(0, 200)}`);
          // Continue with other columns instead of crashing
        }
      }
      await sleep(1000);
    }

    // Add entity to solution
    try {
      const meta = await api(
        "GET",
        `EntityDefinitions(LogicalName='${entity.schema}')?$select=MetadataId`
      );
      await api("POST", "AddSolutionComponent", {
        ComponentId: meta.MetadataId,
        ComponentType: 1,
        SolutionUniqueName: SOLUTION_UNIQUE,
        AddRequiredComponents: true,
      });
      console.log(`    Added to solution`);
    } catch (e) {
      console.log(`    Solution add note: ${e.message}`);
    }
  }
}

// ── Create Relationships ───────────────────────────────────────
async function createRelationships() {
  for (const rel of RELATIONSHIPS) {
    console.log(
      `  ${rel.referencing}.${rel.lookup} -> ${rel.referenced}`
    );

    // Check existence
    const existing = await api(
      "GET",
      `RelationshipDefinitions?$filter=SchemaName eq '${rel.name}'&$select=MetadataId`
    );
    if (existing.value && existing.value.length > 0) {
      console.log(`    Already exists, skipping`);
      continue;
    }

    await api("POST", "RelationshipDefinitions", {
      "@odata.type":
        "#Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata",
      SchemaName: rel.name,
      ReferencedEntity: rel.referenced,
      ReferencedAttribute: `${rel.referenced}id`,
      ReferencingEntity: rel.referencing,
      Lookup: {
        "@odata.type":
          "#Microsoft.Dynamics.CRM.LookupAttributeMetadata",
        SchemaName: rel.lookup,
        DisplayName: lbl(rel.display),
        RequiredLevel: {
          Value: rel.required ? "ApplicationRequired" : "None",
        },
      },
      CascadeConfiguration: {
        Assign: "NoCascade",
        Delete: "RemoveLink",
        Merge: "NoCascade",
        Reparent: "NoCascade",
        Share: "NoCascade",
        Unshare: "NoCascade",
      },
      AssociatedMenuConfiguration: {
        Behavior: "UseCollectionName",
        Group: "Details",
        Order: 10000,
      },
    });
    console.log(`    Created`);
    await sleep(2000);
  }
}

// ── Discover Entity Set Names ──────────────────────────────────
async function discoverEntitySets() {
  const sets = {};
  for (const entity of ENTITIES) {
    const meta = await api(
      "GET",
      `EntityDefinitions(LogicalName='${entity.schema}')?$select=EntitySetName,LogicalCollectionName`
    );
    sets[entity.schema] = meta.EntitySetName || meta.LogicalCollectionName;
    console.log(`  ${entity.schema} -> ${sets[entity.schema]}`);
  }
  return sets;
}

// ── Discover Navigation Property Names ─────────────────────────
async function discoverNavProps() {
  const navProps = {};
  for (const rel of RELATIONSHIPS) {
    try {
      // Query without $select — base type doesn't expose nav prop names
      const rels = await api(
        "GET",
        `RelationshipDefinitions/Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata?$filter=SchemaName eq '${rel.name}'&$select=SchemaName,ReferencingEntityNavigationPropertyName`
      );
      if (rels.value && rels.value.length > 0) {
        navProps[rel.name] =
          rels.value[0].ReferencingEntityNavigationPropertyName;
        console.log(`  ${rel.name} -> ${navProps[rel.name]}`);
      }
    } catch (e) {
      // Fallback: use the lookup schema name as navigation property
      navProps[rel.name] = rel.lookup;
      console.log(`  ${rel.name} -> ${rel.lookup} (fallback)`);
    }
  }
  return navProps;
}

// ── Views ──────────────────────────────────────────────────────
async function createViews() {
  const P = PREFIX;
  const views = [
    {
      entity: `${P}_legalcase`,
      name: "All Legal Cases",
      isDefault: true,
      fetch: `<fetch><entity name="${P}_legalcase"><attribute name="${P}_caseid"/><attribute name="${P}_casetitle"/><attribute name="${P}_casetype"/><attribute name="${P}_county"/><attribute name="${P}_status"/><attribute name="${P}_fileddate"/><order attribute="${P}_caseid"/></entity></fetch>`,
      layout: `<grid name="resultset" jump="${P}_caseid" select="1" icon="1" preview="1"><row name="result" id="${P}_legalcaseid"><cell name="${P}_caseid" width="140"/><cell name="${P}_casetitle" width="250"/><cell name="${P}_casetype" width="130"/><cell name="${P}_county" width="100"/><cell name="${P}_status" width="80"/><cell name="${P}_fileddate" width="100"/></row></grid>`,
    },
    {
      entity: `${P}_legalcase`,
      name: "Active Legal Cases",
      isDefault: false,
      fetch: `<fetch><entity name="${P}_legalcase"><attribute name="${P}_caseid"/><attribute name="${P}_casetitle"/><attribute name="${P}_casetype"/><attribute name="${P}_county"/><attribute name="${P}_fileddate"/><filter><condition attribute="${P}_status" operator="eq" value="Active"/></filter><order attribute="${P}_fileddate" descending="true"/></entity></fetch>`,
      layout: `<grid name="resultset" jump="${P}_caseid" select="1" icon="1" preview="1"><row name="result" id="${P}_legalcaseid"><cell name="${P}_caseid" width="140"/><cell name="${P}_casetitle" width="300"/><cell name="${P}_casetype" width="150"/><cell name="${P}_county" width="100"/><cell name="${P}_fileddate" width="100"/></row></grid>`,
    },
    {
      entity: `${P}_legalcase`,
      name: "Cases by Type",
      isDefault: false,
      fetch: `<fetch><entity name="${P}_legalcase"><attribute name="${P}_caseid"/><attribute name="${P}_casetitle"/><attribute name="${P}_casetype"/><attribute name="${P}_county"/><attribute name="${P}_status"/><attribute name="${P}_fileddate"/><order attribute="${P}_casetype"/><order attribute="${P}_caseid"/></entity></fetch>`,
      layout: `<grid name="resultset" jump="${P}_caseid" select="1" icon="1" preview="1"><row name="result" id="${P}_legalcaseid"><cell name="${P}_casetype" width="150"/><cell name="${P}_caseid" width="140"/><cell name="${P}_casetitle" width="250"/><cell name="${P}_county" width="100"/><cell name="${P}_status" width="80"/></row></grid>`,
    },
    {
      entity: `${P}_person`,
      name: "All People",
      isDefault: true,
      fetch: `<fetch><entity name="${P}_person"><attribute name="${P}_fullname"/><attribute name="${P}_role"/><attribute name="${P}_relationship"/><attribute name="${P}_legalcaseid"/><order attribute="${P}_fullname"/></entity></fetch>`,
      layout: `<grid name="resultset" jump="${P}_fullname" select="1" icon="1" preview="1"><row name="result" id="${P}_personid"><cell name="${P}_fullname" width="150"/><cell name="${P}_role" width="120"/><cell name="${P}_relationship" width="250"/><cell name="${P}_legalcaseid" width="140"/></row></grid>`,
    },
    {
      entity: `${P}_timelineevent`,
      name: "All Timeline Events",
      isDefault: true,
      fetch: `<fetch><entity name="${P}_timelineevent"><attribute name="${P}_name"/><attribute name="${P}_eventdate"/><attribute name="${P}_eventtype"/><attribute name="${P}_legalcaseid"/><order attribute="${P}_eventdate" descending="true"/></entity></fetch>`,
      layout: `<grid name="resultset" jump="${P}_name" select="1" icon="1" preview="1"><row name="result" id="${P}_timelineeventid"><cell name="${P}_eventdate" width="100"/><cell name="${P}_eventtype" width="120"/><cell name="${P}_name" width="250"/><cell name="${P}_legalcaseid" width="140"/></row></grid>`,
    },
    {
      entity: `${P}_statement`,
      name: "All Statements",
      isDefault: true,
      fetch: `<fetch><entity name="${P}_statement"><attribute name="${P}_name"/><attribute name="${P}_statementdate"/><attribute name="${P}_madeto"/><attribute name="${P}_personid"/><attribute name="${P}_legalcaseid"/><order attribute="${P}_statementdate" descending="true"/></entity></fetch>`,
      layout: `<grid name="resultset" jump="${P}_name" select="1" icon="1" preview="1"><row name="result" id="${P}_statementid"><cell name="${P}_statementdate" width="100"/><cell name="${P}_madeto" width="120"/><cell name="${P}_personid" width="150"/><cell name="${P}_legalcaseid" width="140"/></row></grid>`,
    },
    {
      entity: `${P}_discrepancy`,
      name: "All Discrepancies",
      isDefault: true,
      fetch: `<fetch><entity name="${P}_discrepancy"><attribute name="${P}_topic"/><attribute name="${P}_personaid"/><attribute name="${P}_personbid"/><attribute name="${P}_legalcaseid"/><order attribute="${P}_topic"/></entity></fetch>`,
      layout: `<grid name="resultset" jump="${P}_topic" select="1" icon="1" preview="1"><row name="result" id="${P}_discrepancyid"><cell name="${P}_topic" width="200"/><cell name="${P}_personaid" width="130"/><cell name="${P}_personbid" width="130"/><cell name="${P}_legalcaseid" width="140"/></row></grid>`,
    },
  ];

  for (const v of views) {
    const existing = await api(
      "GET",
      `savedqueries?$filter=name eq '${v.name}' and returnedtypecode eq '${v.entity}'&$select=savedqueryid`
    );
    if (existing.value.length > 0) {
      console.log(`  "${v.name}" exists, skipping`);
      continue;
    }

    try {
      await api("POST", "savedqueries", {
        name: v.name,
        returnedtypecode: v.entity,
        fetchxml: v.fetch,
        layoutxml: v.layout,
        querytype: 0,
        isdefault: v.isDefault,
      });
      console.log(`  Created: ${v.name}`);
    } catch (e) {
      console.log(`  Warning creating "${v.name}": ${e.message}`);
    }
  }
}

// ── Model-Driven App ──────────────────────────────────────────
async function createModelDrivenApp() {
  const existing = await api(
    "GET",
    `appmodules?$filter=uniquename eq '${SOLUTION_UNIQUE}'&$select=appmoduleid`
  );
  if (existing.value.length > 0) {
    console.log(`  App '${SOLUTION_UNIQUE}' exists, skipping`);
    return;
  }

  try {
    const sitemap = [
      `<SiteMap>`,
      `  <Area Id="LegalArea" ResourceId="SitemapDesigner.NewArea" DescriptionResourceId="SitemapDesigner.NewArea" Title="Legal Cases">`,
      `    <Group Id="LegalGroup" Title="Case Data" ResourceId="SitemapDesigner.NewGroup" DescriptionResourceId="SitemapDesigner.NewGroup">`,
      `      <SubArea Id="sub_legalcase" Entity="${PREFIX}_legalcase" Title="Legal Cases"/>`,
      `      <SubArea Id="sub_person" Entity="${PREFIX}_person" Title="People"/>`,
      `      <SubArea Id="sub_timeline" Entity="${PREFIX}_timelineevent" Title="Timeline Events"/>`,
      `      <SubArea Id="sub_statement" Entity="${PREFIX}_statement" Title="Statements"/>`,
      `      <SubArea Id="sub_discrepancy" Entity="${PREFIX}_discrepancy" Title="Discrepancies"/>`,
      `    </Group>`,
      `  </Area>`,
      `</SiteMap>`,
    ].join("");

    await api("POST", "appmodules", {
      uniquename: SOLUTION_UNIQUE,
      name: "Legal Case Agent",
      description:
        "DSS Legal Case Agent - view and analyze legal case data",
      clienttype: 4,
      sitemapxml: sitemap,
    });
    console.log(`  Created model-driven app 'Legal Case Agent'`);

    // Add entities as components
    const appResult = await api(
      "GET",
      `appmodules?$filter=uniquename eq '${SOLUTION_UNIQUE}'&$select=appmoduleid`
    );
    if (appResult.value.length > 0) {
      const appId = appResult.value[0].appmoduleid;
      const components = [];
      for (const entity of ENTITIES) {
        const meta = await api(
          "GET",
          `EntityDefinitions(LogicalName='${entity.schema}')?$select=MetadataId`
        );
        components.push({ ComponentType: 1, ComponentId: meta.MetadataId });
      }

      try {
        await api("POST", "AddAppComponents", {
          AppId: appId,
          Components: components,
        });
        console.log(`  Added entities to app`);
      } catch (e) {
        console.log(`  Note: AddAppComponents: ${e.message}`);
        console.log(
          `  You can add entities manually in make.powerapps.us`
        );
      }
    }
  } catch (e) {
    console.log(`  Note: App creation: ${e.message}`);
    console.log(
      `  You can create the app manually in make.powerapps.us`
    );
  }
}

// ── Data Loading ──────────────────────────────────────────────
async function loadData(records, entitySets, navProps) {
  const caseMap = {}; // SQL case_id -> Dataverse GUID
  const personMap = {}; // SQL person_id (1-based) -> Dataverse GUID
  const personNameMap = {}; // SQL person_id (1-based) -> full_name
  let personCounter = 0;
  let errors = 0;
  let created = 0;

  // Resolve nav prop names (fallback to lookup schema name)
  const caseNav =
    navProps[`${PREFIX}_legalcase_person`] ||
    `${PREFIX}_LegalCaseId`;
  const personNav =
    navProps[`${PREFIX}_person_statement`] ||
    `${PREFIX}_PersonId`;
  const personANav =
    navProps[`${PREFIX}_persona_discrepancy`] ||
    `${PREFIX}_PersonAId`;
  const personBNav =
    navProps[`${PREFIX}_personb_discrepancy`] ||
    `${PREFIX}_PersonBId`;

  // Per-entity nav prop for LegalCaseId (may differ per relationship)
  const caseNavFor = {};
  for (const rel of RELATIONSHIPS) {
    if (rel.lookup.toLowerCase().includes("legalcaseid")) {
      const np =
        navProps[rel.name] || rel.lookup;
      caseNavFor[rel.referencing] = np;
    }
  }

  const casesSet = entitySets[`${PREFIX}_legalcase`];
  const personsSet = entitySets[`${PREFIX}_person`];
  const eventsSet = entitySets[`${PREFIX}_timelineevent`];
  const statementsSet = entitySets[`${PREFIX}_statement`];
  const discrepanciesSet = entitySets[`${PREFIX}_discrepancy`];

  // 1. Cases
  console.log(`\n  Cases (${records.cases.length})...`);
  for (const c of records.cases) {
    try {
      const id = await apiCreate(casesSet, {
        [`${PREFIX}_caseid`]: c.case_id,
        [`${PREFIX}_casetitle`]: c.case_title,
        [`${PREFIX}_casetype`]: c.case_type,
        [`${PREFIX}_circuit`]: c.circuit,
        [`${PREFIX}_county`]: c.county,
        [`${PREFIX}_fileddate`]: c.filed_date,
        [`${PREFIX}_status`]: c.status,
        [`${PREFIX}_plaintiff`]: c.plaintiff,
        [`${PREFIX}_summary`]: c.summary,
      });
      caseMap[c.case_id] = id;
      created++;
      process.stdout.write(".");
    } catch (e) {
      console.error(`\n    ERR case ${c.case_id}: ${e.message}`);
      if (e.detail) console.error(`    ${e.detail.substring(0, 200)}`);
      errors++;
    }
  }
  console.log();

  // 2. People
  console.log(`  People (${records.people.length})...`);
  for (const p of records.people) {
    personCounter++;
    if (!caseMap[p.case_id]) {
      errors++;
      continue;
    }

    try {
      const caseNp = caseNavFor[`${PREFIX}_person`] || caseNav;
      const body = {
        [`${PREFIX}_fullname`]: p.full_name,
        [`${PREFIX}_role`]: p.role,
        [`${PREFIX}_relationship`]: p.relationship,
        [`${PREFIX}_notes`]: p.notes,
        [`${PREFIX}_caseidtext`]: p.case_id,
        [`${caseNp}@odata.bind`]: `/${casesSet}(${caseMap[p.case_id]})`,
      };
      if (p.dob) body[`${PREFIX}_dob`] = p.dob;

      const id = await apiCreate(personsSet, body);
      personMap[personCounter] = id;
      personNameMap[personCounter] = p.full_name;
      created++;
      process.stdout.write(".");
    } catch (e) {
      console.error(`\n    ERR person ${p.full_name}: ${e.message}`);
      if (e.detail) console.error(`    ${e.detail.substring(0, 200)}`);
      errors++;
    }
  }
  console.log();

  // 3. Timeline Events
  console.log(`  Timeline Events (${records.timeline_events.length})...`);
  for (const ev of records.timeline_events) {
    if (!caseMap[ev.case_id]) {
      errors++;
      continue;
    }

    try {
      const caseNp =
        caseNavFor[`${PREFIX}_timelineevent`] || caseNav;
      const name = `${ev.event_date} - ${ev.event_type}`;
      const body = {
        [`${PREFIX}_name`]: name.substring(0, 200),
        [`${PREFIX}_eventdate`]: ev.event_date,
        [`${PREFIX}_eventtime`]: ev.event_time,
        [`${PREFIX}_eventtype`]: ev.event_type,
        [`${PREFIX}_description`]: ev.description,
        [`${PREFIX}_sourcedocument`]: ev.source_document,
        [`${PREFIX}_partiesinvolved`]: ev.parties_involved,
        [`${PREFIX}_caseidtext`]: ev.case_id,
        [`${caseNp}@odata.bind`]: `/${casesSet}(${caseMap[ev.case_id]})`,
      };

      await apiCreate(eventsSet, body);
      created++;
      process.stdout.write(".");
    } catch (e) {
      console.error(`\n    ERR event: ${e.message}`);
      errors++;
    }
  }
  console.log();

  // 4. Statements
  console.log(`  Statements (${records.statements.length})...`);
  for (const s of records.statements) {
    if (!caseMap[s.case_id]) {
      errors++;
      continue;
    }

    try {
      const caseNp =
        caseNavFor[`${PREFIX}_statement`] || caseNav;
      const pNav =
        navProps[`${PREFIX}_person_statement`] || personNav;
      const name = `${s.made_to} - ${s.statement_date || "undated"}`;
      const body = {
        [`${PREFIX}_name`]: name.substring(0, 200),
        [`${PREFIX}_madeto`]: s.made_to,
        [`${PREFIX}_statementtext`]: s.statement_text,
        [`${PREFIX}_sourcedocument`]: s.source_document,
        [`${PREFIX}_pagereference`]: s.page_reference,
        [`${PREFIX}_caseidtext`]: s.case_id,
        [`${caseNp}@odata.bind`]: `/${casesSet}(${caseMap[s.case_id]})`,
      };
      if (s.statement_date) body[`${PREFIX}_statementdate`] = s.statement_date;
      if (s.person_id != null && personMap[s.person_id]) {
        body[`${pNav}@odata.bind`] =
          `/${personsSet}(${personMap[s.person_id]})`;
        if (personNameMap[s.person_id]) {
          body[`${PREFIX}_personname`] = personNameMap[s.person_id];
        }
      }

      await apiCreate(statementsSet, body);
      created++;
      process.stdout.write(".");
    } catch (e) {
      console.error(`\n    ERR statement: ${e.message}`);
      errors++;
    }
  }
  console.log();

  // 5. Discrepancies
  console.log(`  Discrepancies (${records.discrepancies.length})...`);
  for (const d of records.discrepancies) {
    if (!caseMap[d.case_id]) {
      errors++;
      continue;
    }

    try {
      const caseNp =
        caseNavFor[`${PREFIX}_discrepancy`] || caseNav;
      const paNav =
        navProps[`${PREFIX}_persona_discrepancy`] || personANav;
      const pbNav =
        navProps[`${PREFIX}_personb_discrepancy`] || personBNav;
      const body = {
        [`${PREFIX}_topic`]: (d.topic || "").substring(0, 200),
        [`${PREFIX}_personaaccount`]: d.person_a_account,
        [`${PREFIX}_personbaccount`]: d.person_b_account,
        [`${PREFIX}_contradictedby`]: d.contradicted_by,
        [`${PREFIX}_sourcedocument`]: d.source_document,
        [`${PREFIX}_caseidtext`]: d.case_id,
        [`${caseNp}@odata.bind`]: `/${casesSet}(${caseMap[d.case_id]})`,
      };
      if (d.person_a_id != null && personMap[d.person_a_id]) {
        body[`${paNav}@odata.bind`] =
          `/${personsSet}(${personMap[d.person_a_id]})`;
        if (personNameMap[d.person_a_id]) {
          body[`${PREFIX}_personaname`] = personNameMap[d.person_a_id];
        }
      }
      if (d.person_b_id != null && personMap[d.person_b_id]) {
        body[`${pbNav}@odata.bind`] =
          `/${personsSet}(${personMap[d.person_b_id]})`;
        if (personNameMap[d.person_b_id]) {
          body[`${PREFIX}_personbname`] = personNameMap[d.person_b_id];
        }
      }

      await apiCreate(discrepanciesSet, body);
      created++;
      process.stdout.write(".");
    } catch (e) {
      console.error(`\n    ERR discrepancy: ${e.message}`);
      errors++;
    }
  }
  console.log();

  console.log(
    `\n  Data loading complete: ${created} created, ${errors} errors`
  );
  return errors;
}

// ── Publish ────────────────────────────────────────────────────
async function publish() {
  await api("POST", "PublishAllXml", {});
  console.log("  Published all customizations");
}

// ── Main ───────────────────────────────────────────────────────
const args = process.argv.slice(2);
const schemaOnly = args.includes("--schema-only");
const dataOnly = args.includes("--data-only");

async function main() {
  console.log("=".repeat(50));
  console.log("  Dataverse Deployment: Legal Case Agent");
  console.log("  Target: og-ai.crm9.dynamics.com (GCC)");
  console.log("=".repeat(50));
  console.log();

  // Step 1: Auth
  console.log("Step 1: Authenticate");
  console.log("  Starting device code flow...");
  await authenticate();
  const whoAmI = await api("GET", "WhoAmI");
  console.log(`  Connected as ${whoAmI.UserId}\n`);

  if (!dataOnly) {
    // Step 2: Publisher & Solution
    console.log("Step 2: Publisher & Solution");
    await ensurePublisherAndSolution();

    // Step 3: Tables
    console.log("\nStep 3: Tables & Columns");
    await createTables();

    // Step 4: Relationships
    console.log("\nStep 4: Relationships");
    await createRelationships();

    // Step 5: Publish schema
    console.log("\nStep 5: Publish (schema)");
    await publish();
    console.log("  Waiting for publish to propagate...");
    await sleep(8000);

    // Step 6: Views
    console.log("\nStep 6: Views");
    await createViews();

    // Step 7: Model-driven app
    console.log("\nStep 7: Model-Driven App");
    await createModelDrivenApp();

    // Step 8: Publish views & app
    console.log("\nStep 8: Publish (views & app)");
    await publish();
    await sleep(3000);
  }

  if (!schemaOnly) {
    // Step 9: Discover entity set names & nav props
    console.log("\nStep 9: Discover Metadata");
    console.log("  Entity sets:");
    const entitySets = await discoverEntitySets();
    console.log("  Navigation properties:");
    const navProps = await discoverNavProps();

    // Step 10: Parse & load data
    console.log("\nStep 10: Parse Seed Data");
    const records = parseSqlFile(path.join(__dirname, "seed-expanded.sql"));
    console.log(
      `  Parsed: ${records.cases.length} cases, ${records.people.length} people, ` +
        `${records.timeline_events.length} events, ${records.statements.length} statements, ` +
        `${records.discrepancies.length} discrepancies`
    );

    console.log("\nStep 11: Load Data");
    await loadData(records, entitySets, navProps);
  }

  console.log("\n" + "=".repeat(50));
  console.log("  Deployment complete!");
  console.log(`  Environment: ${ENV_URL}`);
  console.log(`  Solution: ${SOLUTION_UNIQUE}`);
  console.log(
    "  Tables: Legal Cases, People, Timeline Events,"
  );
  console.log("          Statements, Discrepancies");
  if (!schemaOnly) {
    console.log(
      "  Run --data-only to reload data without recreating schema"
    );
  }
  console.log("=".repeat(50));
}

main().catch((err) => {
  console.error("\nFatal:", err.message);
  if (err.detail) console.error(err.detail);
  process.exit(1);
});
