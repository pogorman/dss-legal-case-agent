import {
  app,
  HttpRequest,
  HttpResponseInit,
  InvocationContext,
} from "@azure/functions";
import { getPool } from "../db/client";

async function listCases(
  request: HttpRequest,
  context: InvocationContext
): Promise<HttpResponseInit> {
  try {
    const pool = await getPool();
    const result = await pool.request().query(`
      SELECT case_id, case_title, case_type, circuit, county,
             filed_date, status, plaintiff, summary
      FROM cases
      ORDER BY filed_date DESC
    `);

    return {
      status: 200,
      jsonBody: result.recordset,
    };
  } catch (error) {
    context.error("Error listing cases:", error);
    return {
      status: 500,
      jsonBody: { error: "Failed to retrieve cases" },
    };
  }
}

app.http("listCases", {
  methods: ["GET"],
  authLevel: "function",
  route: "cases",
  handler: listCases,
});
