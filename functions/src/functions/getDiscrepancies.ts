import {
  app,
  HttpRequest,
  HttpResponseInit,
  InvocationContext,
} from "@azure/functions";
import { getPool, sql } from "../db/client";

async function getDiscrepancies(
  request: HttpRequest,
  context: InvocationContext
): Promise<HttpResponseInit> {
  const caseId = request.params.caseId;
  if (!caseId) {
    return { status: 400, jsonBody: { error: "caseId is required" } };
  }

  try {
    const pool = await getPool();
    const result = await pool
      .request()
      .input("caseId", sql.VarChar(20), caseId)
      .query(`
        SELECT d.discrepancy_id, d.case_id, d.topic,
               d.person_a_account, d.person_b_account,
               d.contradicted_by, d.source_document,
               pa.full_name AS person_a_name, pa.role AS person_a_role,
               pb.full_name AS person_b_name, pb.role AS person_b_role
        FROM discrepancies d
        LEFT JOIN people pa ON d.person_a_id = pa.person_id
        LEFT JOIN people pb ON d.person_b_id = pb.person_id
        WHERE d.case_id = @caseId
        ORDER BY d.discrepancy_id
      `);

    return {
      status: 200,
      jsonBody: result.recordset,
    };
  } catch (error) {
    context.error("Error getting discrepancies:", error);
    return {
      status: 500,
      jsonBody: { error: "Failed to retrieve discrepancies" },
    };
  }
}

app.http("getDiscrepancies", {
  methods: ["GET"],
  authLevel: "function",
  route: "cases/{caseId}/discrepancies",
  handler: getDiscrepancies,
});
