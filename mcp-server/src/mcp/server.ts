/**
 * MCP Streamable HTTP transport handler.
 * Implements JSON-RPC 2.0 over POST /mcp for Copilot Studio integration.
 */

import { Request, Response } from "express";
import { TOOL_DEFINITIONS, callTool } from "./tools";

const SERVER_INFO = {
  name: "dss-case-agent",
  version: "1.0.0",
};

const CAPABILITIES = {
  tools: {},
};

interface JsonRpcRequest {
  jsonrpc: "2.0";
  id?: string | number;
  method: string;
  params?: Record<string, unknown>;
}

interface JsonRpcResponse {
  jsonrpc: "2.0";
  id?: string | number | null;
  result?: unknown;
  error?: { code: number; message: string; data?: unknown };
}

function makeResult(id: string | number | undefined, result: unknown): JsonRpcResponse {
  return { jsonrpc: "2.0", id: id ?? null, result };
}

function makeError(
  id: string | number | undefined,
  code: number,
  message: string
): JsonRpcResponse {
  return { jsonrpc: "2.0", id: id ?? null, error: { code, message } };
}

async function handleRequest(req: JsonRpcRequest): Promise<JsonRpcResponse> {
  switch (req.method) {
    case "initialize":
      return makeResult(req.id, {
        protocolVersion: "2025-03-26",
        serverInfo: SERVER_INFO,
        capabilities: CAPABILITIES,
      });

    case "notifications/initialized":
      // Notification — no response needed, but return ack for streamable HTTP
      return makeResult(req.id, {});

    case "tools/list":
      return makeResult(req.id, { tools: TOOL_DEFINITIONS });

    case "tools/call": {
      const params = req.params as {
        name: string;
        arguments?: Record<string, string>;
      };

      if (!params?.name) {
        return makeError(req.id, -32602, "Missing tool name");
      }

      const toolDef = TOOL_DEFINITIONS.find((t) => t.name === params.name);
      if (!toolDef) {
        return makeError(req.id, -32602, `Unknown tool: ${params.name}`);
      }

      try {
        const result = await callTool(params.name, params.arguments || {});
        return makeResult(req.id, {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        });
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Tool execution failed";
        return makeResult(req.id, {
          content: [{ type: "text", text: `Error: ${message}` }],
          isError: true,
        });
      }
    }

    default:
      return makeError(req.id, -32601, `Method not found: ${req.method}`);
  }
}

export async function mcpHandler(req: Request, res: Response): Promise<void> {
  // NOTE: Production would require API key or OAuth authentication here.
  // Unauthenticated for POC demo — read-only data only.

  const body = req.body;

  if (!body || typeof body !== "object" || body.jsonrpc !== "2.0") {
    res.status(400).json(makeError(undefined, -32700, "Parse error"));
    return;
  }

  // Handle single request (Copilot Studio sends single requests)
  if (!Array.isArray(body)) {
    const response = await handleRequest(body as JsonRpcRequest);
    res.json(response);
    return;
  }

  // Handle batch requests
  const responses = await Promise.all(
    (body as JsonRpcRequest[]).map(handleRequest)
  );
  res.json(responses);
}
