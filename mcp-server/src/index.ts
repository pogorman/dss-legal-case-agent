/**
 * DSS Case Agent — Express application.
 * Endpoints:
 *   POST /mcp     — MCP streamable HTTP transport (Copilot Studio)
 *   POST /chat    — Chat completions with tool calling (web SPA)
 *   GET  /healthz — Health check
 */

import express from "express";
import { mcpHandler } from "./mcp/server";
import { chatHandler } from "./chat/completions";

const app = express();
const PORT = parseInt(process.env.PORT || "3000", 10);

app.use(express.json({ limit: "1mb" }));

// CORS for SWA frontend
app.use((_req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.header("Access-Control-Allow-Headers", "Content-Type, Authorization");
  if (_req.method === "OPTIONS") {
    res.sendStatus(204);
    return;
  }
  next();
});

// MCP endpoint — Copilot Studio connects here
app.post("/mcp", mcpHandler);

// Chat endpoint — web SPA connects here
app.post("/chat", chatHandler);

// Health check
app.get("/healthz", (_req, res) => {
  res.json({ status: "healthy", service: "dss-case-agent", timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`DSS Case Agent listening on port ${PORT}`);
  console.log(`  MCP endpoint:  POST /mcp`);
  console.log(`  Chat endpoint: POST /chat`);
  console.log(`  Health check:  GET  /healthz`);
});
