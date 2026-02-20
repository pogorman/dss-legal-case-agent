const sql = require("mssql");
const { execSync } = require("child_process");

async function main() {
  const token = execSync(
    'az account get-access-token --resource https://database.windows.net/ --query accessToken -o tsv',
    { encoding: "utf-8" }
  ).trim();

  const pool = await new sql.ConnectionPool({
    server: "philly-stats-sql-01.database.windows.net",
    database: "dss-demo",
    authentication: { type: "azure-active-directory-access-token", options: { token } },
    options: { encrypt: true, trustServerCertificate: false },
  }).connect();

  await pool.request().query(`
    IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'dss-demo-func')
    BEGIN
      CREATE USER [dss-demo-func] FROM EXTERNAL PROVIDER;
      ALTER ROLE db_datareader ADD MEMBER [dss-demo-func];
    END
  `);
  console.log("Granted db_datareader to dss-demo-func");

  await pool.close();
}

main().catch((err) => { console.error(err.message); process.exit(1); });
