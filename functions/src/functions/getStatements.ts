import {
  app,
  HttpRequest,
  HttpResponseInit,
  InvocationContext,
} from "@azure/functions";
import { getPool, sql } from "../db/client";

async function getStatements(
  request: HttpRequest,
  context: InvocationContext
): Promise<HttpResponseInit> {
  const caseId = request.params.caseId;
  if (!caseId) {
    return { status: 400, jsonBody: { error: "caseId is required" } };
  }

  const personName = request.query.get("person");
  if (!personName) {
    return {
      status: 400,
      jsonBody: { error: "person query parameter is required" },
    };
  }

  try {
    const pool = await getPool();
    const result = await pool
      .request()
      .input("caseId", sql.VarChar(20), caseId)
      .input("personName", sql.VarChar(100), `%${personName}%`)
      .query(`
        SELECT s.statement_id, s.case_id, s.statement_date, s.made_to,
               s.statement_text, s.source_document, s.page_reference,
               p.full_name, p.role
        FROM statements s
        JOIN people p ON s.person_id = p.person_id
        WHERE s.case_id = @caseId
          AND p.full_name LIKE @personName
        ORDER BY s.statement_date
      `);

    return {
      status: 200,
      jsonBody: result.recordset,
    };
  } catch (error) {
    context.error("Error getting statements:", error);
    return {
      status: 500,
      jsonBody: { error: "Failed to retrieve statements" },
    };
  }
}

app.http("getStatements", {
  methods: ["GET"],
  authLevel: "function",
  route: "cases/{caseId}/statements",
  handler: getStatements,
});
