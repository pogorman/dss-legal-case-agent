/**
 * MCP Tool definitions and APIM backend calls.
 * Each tool maps to an Azure Function endpoint exposed through APIM.
 */

const APIM_BASE_URL = process.env.APIM_BASE_URL || "";
const APIM_SUBSCRIPTION_KEY = process.env.APIM_SUBSCRIPTION_KEY || "";

interface ToolDefinition {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties: Record<string, unknown>;
    required?: string[];
  };
}

export const TOOL_DEFINITIONS: ToolDefinition[] = [
  {
    name: "list_cases",
    description:
      "Returns all available cases with their IDs, titles, types, and status. Use this to orient at the start of a session.",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "get_case_summary",
    description:
      "Returns the case overview including ALL people involved (parents, children, nurses, doctors, case workers, attorneys, law enforcement, judges) with their roles and source citations, plus filing date, status, county, and case summary. Use this when asked about who is involved in a case or when looking for a specific person's role.",
    inputSchema: {
      type: "object",
      properties: {
        case_id: {
          type: "string",
          description: "The case identifier, e.g. '2024-DR-42-0892'",
        },
      },
      required: ["case_id"],
    },
  },
  {
    name: "get_timeline",
    description:
      "Returns a chronological list of events for a case with dates, descriptions, and source document references. Can filter by event type. Use for questions about what happened and when.",
    inputSchema: {
      type: "object",
      properties: {
        case_id: {
          type: "string",
          description: "The case identifier",
        },
        event_type: {
          type: "string",
          description:
            "Optional filter: 'Medical', 'Court', 'DSS Action', 'Law Enforcement', 'Family', 'Placement'",
        },
      },
      required: ["case_id"],
    },
  },
  {
    name: "get_statements_by_person",
    description:
      "Returns recorded statements for a case with source citations, page references, dates, and who the statement was made to. Use when asked about what someone said, or to compare what someone told different audiences (hospital vs law enforcement).",
    inputSchema: {
      type: "object",
      properties: {
        case_id: {
          type: "string",
          description: "The case identifier",
        },
        person_name: {
          type: "string",
          description:
            "Full or partial name of the person whose statements to retrieve",
        },
        made_to: {
          type: "string",
          description:
            "Optional filter: who the statement was made to, e.g. 'Law Enforcement', 'Medical Staff', 'Court', 'Case Manager'",
        },
      },
      required: ["case_id"],
    },
  },
  {
    name: "get_discrepancies",
    description:
      "Returns side-by-side comparison of conflicting accounts between parties on key topics, showing what each party claimed and what evidence contradicted them. Use when asked to compare or find contradictions.",
    inputSchema: {
      type: "object",
      properties: {
        case_id: {
          type: "string",
          description: "The case identifier",
        },
      },
      required: ["case_id"],
    },
  },
];

async function apimFetch(path: string): Promise<unknown> {
  const url = `${APIM_BASE_URL}${path}`;
  const response = await fetch(url, {
    headers: {
      "Ocp-Apim-Subscription-Key": APIM_SUBSCRIPTION_KEY,
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`APIM call failed: ${response.status} ${body}`);
  }

  return response.json();
}

export async function callTool(
  name: string,
  args: Record<string, string>
): Promise<unknown> {
  switch (name) {
    case "list_cases":
      return apimFetch("/cases");

    case "get_case_summary":
      return apimFetch(`/cases/${encodeURIComponent(args.case_id)}`);

    case "get_timeline": {
      const typeParam = args.event_type
        ? `?type=${encodeURIComponent(args.event_type)}`
        : "";
      return apimFetch(
        `/cases/${encodeURIComponent(args.case_id)}/timeline${typeParam}`
      );
    }

    case "get_statements_by_person": {
      const stmtParams = new URLSearchParams();
      if (args.person_name) stmtParams.set("person", args.person_name);
      if (args.made_to) stmtParams.set("made_to", args.made_to);
      return apimFetch(
        `/cases/${encodeURIComponent(args.case_id)}/statements?${stmtParams.toString()}`
      );
    }

    case "get_discrepancies":
      return apimFetch(
        `/cases/${encodeURIComponent(args.case_id)}/discrepancies`
      );

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}
