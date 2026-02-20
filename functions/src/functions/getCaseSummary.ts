import {
  app,
  HttpRequest,
  HttpResponseInit,
  InvocationContext,
} from "@azure/functions";
import { getPool, sql } from "../db/client";

async function getCaseSummary(
  request: HttpRequest,
  context: InvocationContext
): Promise<HttpResponseInit> {
  const caseId = request.params.caseId;
  if (!caseId) {
    return { status: 400, jsonBody: { error: "caseId is required" } };
  }

  try {
    const pool = await getPool();

    const caseResult = await pool
      .request()
      .input("caseId", sql.VarChar(20), caseId)
      .query(`
        SELECT case_id, case_title, case_type, circuit, county,
               filed_date, status, plaintiff, summary
        FROM cases
        WHERE case_id = @caseId
      `);

    if (caseResult.recordset.length === 0) {
      return { status: 404, jsonBody: { error: "Case not found" } };
    }

    const peopleResult = await pool
      .request()
      .input("caseId", sql.VarChar(20), caseId)
      .query(`
        SELECT person_id, full_name, role, relationship, dob, notes
        FROM people
        WHERE case_id = @caseId
        ORDER BY person_id
      `);

    return {
      status: 200,
      jsonBody: {
        ...caseResult.recordset[0],
        people: peopleResult.recordset,
      },
    };
  } catch (error) {
    context.error("Error getting case summary:", error);
    return {
      status: 500,
      jsonBody: { error: "Failed to retrieve case summary" },
    };
  }
}

app.http("getCaseSummary", {
  methods: ["GET"],
  authLevel: "function",
  route: "cases/{caseId}",
  handler: getCaseSummary,
});
