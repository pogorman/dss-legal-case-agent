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
  const madeTo = request.query.get("made_to");

  if (!personName && !madeTo) {
    return {
      status: 400,
      jsonBody: { error: "person and/or made_to query parameter is required" },
    };
  }

  try {
    const pool = await getPool();
    const req = pool.request().input("caseId", sql.VarChar(20), caseId);

    let whereClause = "WHERE s.case_id = @caseId";
    if (personName) {
      req.input("personName", sql.VarChar(100), `%${personName}%`);
      whereClause += " AND p.full_name LIKE @personName";
    }
    if (madeTo) {
      req.input("madeTo", sql.VarChar(100), `%${madeTo}%`);
      whereClause += " AND s.made_to LIKE @madeTo";
    }

    const result = await req.query(`
        SELECT s.statement_id, s.case_id, s.statement_date, s.made_to,
               s.statement_text, s.source_document, s.page_reference,
               p.full_name, p.role
        FROM statements s
        JOIN people p ON s.person_id = p.person_id
        ${whereClause}
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
