import sql from "mssql";
import { DefaultAzureCredential } from "@azure/identity";

const SQL_SERVER = process.env.SQL_SERVER || "";
const SQL_DATABASE = process.env.SQL_DATABASE || "dss-demo";

let pool: sql.ConnectionPool | null = null;
let tokenExpiry = 0;

async function getAccessToken(): Promise<string> {
  const credential = new DefaultAzureCredential();
  const token = await credential.getToken(
    "https://database.windows.net/.default"
  );
  tokenExpiry = token.expiresOnTimestamp;
  return token.token;
}

export async function getPool(): Promise<sql.ConnectionPool> {
  const now = Date.now();

  if (pool?.connected && now < tokenExpiry - 60_000) {
    return pool;
  }

  if (pool) {
    try {
      await pool.close();
    } catch {
      // ignore close errors
    }
    pool = null;
  }

  const accessToken = await getAccessToken();

  const config: sql.config = {
    server: SQL_SERVER,
    database: SQL_DATABASE,
    authentication: {
      type: "azure-active-directory-access-token",
      options: { token: accessToken },
    },
    options: {
      encrypt: true,
      trustServerCertificate: false,
    },
  };

  pool = await new sql.ConnectionPool(config).connect();
  return pool;
}

export { sql };
