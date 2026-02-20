/**
 * Deploys schema.sql and seed.sql to Azure SQL using Azure CLI token auth.
 * Sends each file as a single batch to avoid splitting issues with semicolons in string literals.
 * Usage: node deploy-sql.js
 */
const sql = require("mssql");
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const SQL_SERVER = "philly-stats-sql-01.database.windows.net";
const SQL_DATABASE = "dss-demo";

async function getToken() {
  const token = execSync(
    'az account get-access-token --resource https://database.windows.net/ --query accessToken -o tsv',
    { encoding: "utf-8" }
  ).trim();
  return token;
}

async function runSqlFile(pool, filePath, label) {
  console.log(`=== Running ${label} ===`);
  const content = fs.readFileSync(filePath, "utf-8");

  try {
    await pool.request().query(content);
    console.log(`  OK: ${label} executed successfully.`);
  } catch (err) {
    console.error(`  FAIL: ${err.message}`);
    throw err;
  }
}

async function main() {
  console.log("Getting Azure AD token...");
  const token = await getToken();

  console.log(`Connecting to ${SQL_SERVER}/${SQL_DATABASE}...`);
  const pool = await new sql.ConnectionPool({
    server: SQL_SERVER,
    database: SQL_DATABASE,
    authentication: {
      type: "azure-active-directory-access-token",
      options: { token },
    },
    options: {
      encrypt: true,
      trustServerCertificate: false,
    },
  }).connect();

  console.log("Connected.\n");

  // Drop existing tables (reverse dependency order)
  console.log("=== Dropping existing tables ===");
  const dropSql = `
    IF OBJECT_ID('discrepancies', 'U') IS NOT NULL DROP TABLE discrepancies;
    IF OBJECT_ID('statements', 'U') IS NOT NULL DROP TABLE statements;
    IF OBJECT_ID('timeline_events', 'U') IS NOT NULL DROP TABLE timeline_events;
    IF OBJECT_ID('people', 'U') IS NOT NULL DROP TABLE people;
    IF OBJECT_ID('cases', 'U') IS NOT NULL DROP TABLE cases;
  `;
  await pool.request().query(dropSql);
  console.log("  OK: Tables dropped.\n");

  await runSqlFile(pool, path.join(__dirname, "schema.sql"), "schema.sql");
  console.log("");

  // Use expanded seed if it exists, otherwise fall back to seed.sql
  const seedFile = fs.existsSync(path.join(__dirname, "seed-expanded.sql"))
    ? "seed-expanded.sql"
    : "seed.sql";
  await runSqlFile(pool, path.join(__dirname, seedFile), seedFile);

  console.log("\n=== Verifying row counts ===");
  const tables = ["cases", "people", "timeline_events", "statements", "discrepancies"];
  for (const table of tables) {
    const result = await pool.request().query(`SELECT COUNT(*) AS cnt FROM ${table}`);
    console.log(`  ${table}: ${result.recordset[0].cnt} rows`);
  }

  await pool.close();
  console.log("\nDone.");
}

main().catch((err) => {
  console.error("Fatal:", err.message);
  process.exit(1);
});
