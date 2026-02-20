/**
 * Chat completions endpoint with tool-calling loop.
 * Uses Azure OpenAI GPT-4.1 with managed identity auth.
 */

import { Request, Response } from "express";
import { DefaultAzureCredential, getBearerTokenProvider } from "@azure/identity";
import { AzureOpenAI } from "openai";
import { TOOL_DEFINITIONS, callTool } from "../mcp/tools";
import type {
  ChatCompletionMessageParam,
  ChatCompletionTool,
  ChatCompletionToolMessageParam,
} from "openai/resources/chat/completions";

const AZURE_OPENAI_ENDPOINT = process.env.AZURE_OPENAI_ENDPOINT || "";
const AZURE_OPENAI_DEPLOYMENT = process.env.AZURE_OPENAI_DEPLOYMENT || "gpt-4.1";

const SYSTEM_PROMPT = `You are a legal case analysis assistant for the South Carolina Department of Social Services (DSS) General Counsel team. You have access to structured case data through specialized tools.

When answering questions:
- Always cite source documents and page references when available
- Present timelines in chronological order with dates
- Present discrepancies in a clear comparison format
- Be precise and factual — only state what the data shows
- Use professional legal language appropriate for attorneys
- When presenting statements, include who the statement was made to and the date
- If data is not available for a query, say so clearly rather than guessing

Available tools allow you to: list cases, get case summaries with parties, retrieve chronological timelines, look up statements by person, and compare discrepancies between parties.`;

let openaiClient: AzureOpenAI | null = null;

function getOpenAIClient(): AzureOpenAI {
  if (!openaiClient) {
    const credential = new DefaultAzureCredential();
    const tokenProvider = getBearerTokenProvider(
      credential,
      "https://cognitiveservices.azure.com/.default"
    );

    openaiClient = new AzureOpenAI({
      azureADTokenProvider: tokenProvider,
      endpoint: AZURE_OPENAI_ENDPOINT,
      apiVersion: "2025-01-01-preview",
    });
  }
  return openaiClient;
}

function buildTools(): ChatCompletionTool[] {
  return TOOL_DEFINITIONS.map((t) => ({
    type: "function" as const,
    function: {
      name: t.name,
      description: t.description,
      parameters: t.inputSchema,
    },
  }));
}

interface ChatRequest {
  messages: ChatCompletionMessageParam[];
}

interface ToolCallRecord {
  name: string;
  arguments: string;
}

export async function chatHandler(req: Request, res: Response): Promise<void> {
  const body = req.body as ChatRequest;

  if (!body?.messages || !Array.isArray(body.messages)) {
    res.status(400).json({ error: "messages array is required" });
    return;
  }

  try {
    const client = getOpenAIClient();
    const tools = buildTools();
    const toolsCalled: ToolCallRecord[] = [];

    const messages: ChatCompletionMessageParam[] = [
      { role: "system", content: SYSTEM_PROMPT },
      ...body.messages,
    ];

    const MAX_TOOL_ROUNDS = 10;
    let round = 0;

    while (round < MAX_TOOL_ROUNDS) {
      round++;

      const completion = await client.chat.completions.create({
        model: AZURE_OPENAI_DEPLOYMENT,
        messages,
        tools,
        tool_choice: "auto",
      });

      const choice = completion.choices[0];
      if (!choice) {
        throw new Error("No completion choice returned");
      }

      messages.push(choice.message);

      // If no tool calls, we're done
      if (!choice.message.tool_calls || choice.message.tool_calls.length === 0) {
        res.json({
          content: choice.message.content,
          tools_called: toolsCalled,
        });
        return;
      }

      // Execute tool calls
      for (const toolCall of choice.message.tool_calls) {
        const fnName = toolCall.function.name;
        const fnArgs = JSON.parse(toolCall.function.arguments);

        toolsCalled.push({
          name: fnName,
          arguments: toolCall.function.arguments,
        });

        let toolResult: string;
        try {
          const result = await callTool(fnName, fnArgs);
          toolResult = JSON.stringify(result);
        } catch (error) {
          toolResult = JSON.stringify({
            error:
              error instanceof Error ? error.message : "Tool execution failed",
          });
        }

        const toolMessage: ChatCompletionToolMessageParam = {
          role: "tool",
          tool_call_id: toolCall.id,
          content: toolResult,
        };
        messages.push(toolMessage);
      }
    }

    // Exceeded max rounds
    res.json({
      content: "I completed the maximum number of tool calls. Here is what I found so far based on the data retrieved.",
      tools_called: toolsCalled,
    });
  } catch (error) {
    console.error("Chat completion error:", error);
    res.status(500).json({
      error: "Failed to process chat request",
      details: error instanceof Error ? error.message : String(error),
    });
  }
}
