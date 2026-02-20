import {
  app,
  HttpRequest,
  HttpResponseInit,
  InvocationContext,
} from "@azure/functions";
import { getPool, sql } from "../db/client";

async function getTimeline(
  request: HttpRequest,
  context: InvocationContext
): Promise<HttpResponseInit> {
  const caseId = request.params.caseId;
  if (!caseId) {
    return { status: 400, jsonBody: { error: "caseId is required" } };
  }

  const eventType = request.query.get("type");

  try {
    const pool = await getPool();
    const req = pool.request().input("caseId", sql.VarChar(20), caseId);

    let query = `
      SELECT event_id, case_id, event_date, event_time, event_type,
             description, source_document, parties_involved
      FROM timeline_events
      WHERE case_id = @caseId
    `;

    if (eventType) {
      req.input("eventType", sql.VarChar(100), eventType);
      query += " AND event_type = @eventType";
    }

    query += " ORDER BY event_date, event_time";

    const result = await req.query(query);

    return {
      status: 200,
      jsonBody: result.recordset,
    };
  } catch (error) {
    context.error("Error getting timeline:", error);
    return {
      status: 500,
      jsonBody: { error: "Failed to retrieve timeline" },
    };
  }
}

app.http("getTimeline", {
  methods: ["GET"],
  authLevel: "function",
  route: "cases/{caseId}/timeline",
  handler: getTimeline,
});
