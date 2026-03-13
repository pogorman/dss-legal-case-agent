/**
 * Fire all 19 Phase 1 prompts at the GCC Copilot Studio agent via Direct Line API.
 * Captures responses and writes results to docs/test-responses/phase-2-connector/
 *
 * Usage: npx tsx scripts/phase-2/test-connector-agent.ts
 */

const DIRECT_LINE_SECRET = process.env.DL_SECRET!;
const BASE_URL = "https://directline.botframework.com/v3/directline";

interface Activity {
  type: string;
  from: { id: string; name?: string };
  text?: string;
  timestamp?: string;
  id?: string;
}

interface ConversationResponse {
  conversationId: string;
  token: string;
}

const PROMPTS = [
  // Section 1: Factual Retrieval
  { id: "1.1", section: "Factual Retrieval", prompt: "What is the complete timeline of events for case 2024-DR-42-0892?" },
  { id: "1.2", section: "Factual Retrieval", prompt: "When was Jaylen Webb admitted to the hospital and what injuries were found?" },
  { id: "1.3", section: "Factual Retrieval", prompt: "List all people involved in the Price TPR case and their roles." },
  { id: "1.4", section: "Factual Retrieval", prompt: "What court hearings have occurred in the Webb case and what were the outcomes?" },
  // Section 2: Cross-Referencing
  { id: "2.1", section: "Cross-Referencing", prompt: "What did Marcus Webb tell medical staff vs. what he told law enforcement about the night Jaylen was injured?" },
  { id: "2.2", section: "Cross-Referencing", prompt: "Compare Dena Holloway's initial hospital statement with her later statement to Lt. Odom. What changed?" },
  { id: "2.3", section: "Cross-Referencing", prompt: "What has Crystal Price said about her sobriety at each court hearing? How do those statements compare to her drug test results?" },
  // Section 3: Discrepancies
  { id: "3.1", section: "Discrepancies", prompt: "What are the key discrepancies between Marcus Webb's and Dena Holloway's accounts?" },
  { id: "3.2", section: "Discrepancies", prompt: "Are there any contradictions in Crystal Price's statements about her compliance with the treatment plan?" },
  { id: "3.3", section: "Discrepancies", prompt: "What evidence contradicts the parents' claim that Jaylen fell from his crib?" },
  // Section 4: Filtering
  { id: "4.1", section: "Filtering", prompt: "Show me only the medical events in the Webb case timeline." },
  { id: "4.2", section: "Filtering", prompt: "What statements were made to law enforcement in case 2024-DR-42-0892?" },
  { id: "4.3", section: "Filtering", prompt: "List all court orders for the Price case in chronological order." },
  // Section 5: Aggregate
  { id: "5.1", section: "Aggregate", prompt: "How many active cases does DSS currently have?" },
  { id: "5.2", section: "Aggregate", prompt: "List all cases in the Seventh Judicial Circuit." },
  { id: "5.3", section: "Aggregate", prompt: "Which cases involve Termination of Parental Rights?" },
  { id: "5.4", section: "Aggregate", prompt: "Are there any cases in Richland County besides the Price case?" },
  // Section 6: Stress Tests
  { id: "6.1", section: "Stress Tests", prompt: "What page of the medical records contains Dr. Chowdhury's assessment that the injuries occurred at different times?" },
  { id: "6.2", section: "Stress Tests", prompt: "How many IOP sessions had Crystal Price completed as of the November 2023 review vs. the April 2024 hearing?" },
];

async function startConversation(): Promise<ConversationResponse> {
  const res = await fetch(`${BASE_URL}/conversations`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${DIRECT_LINE_SECRET}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) {
    throw new Error(`Start conversation failed: ${res.status} ${await res.text()}`);
  }
  return res.json() as Promise<ConversationResponse>;
}

async function sendMessage(conversationId: string, token: string, text: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/conversations/${conversationId}/activities`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type: "message",
      from: { id: "test-runner" },
      text,
    }),
  });
  if (!res.ok) {
    throw new Error(`Send message failed: ${res.status} ${await res.text()}`);
  }
}

async function pollForResponse(conversationId: string, token: string, watermark?: string): Promise<{ text: string; watermark: string }> {
  const maxAttempts = 60; // 60 seconds max wait
  let attempts = 0;
  let currentWatermark = watermark || "";

  while (attempts < maxAttempts) {
    const url = currentWatermark
      ? `${BASE_URL}/conversations/${conversationId}/activities?watermark=${currentWatermark}`
      : `${BASE_URL}/conversations/${conversationId}/activities`;

    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      throw new Error(`Poll failed: ${res.status} ${await res.text()}`);
    }

    const data = await res.json() as { activities: Activity[]; watermark: string };

    // Look for bot responses (not from our test-runner)
    const botMessages = data.activities.filter(
      (a: Activity) => a.type === "message" && a.from.id !== "test-runner"
    );

    if (botMessages.length > 0) {
      // Get the last bot message (the actual response, not typing indicators)
      const lastMsg = botMessages[botMessages.length - 1];
      if (lastMsg.text) {
        return { text: lastMsg.text, watermark: data.watermark };
      }
    }

    attempts++;
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  return { text: "[TIMEOUT - no response after 60s]", watermark: currentWatermark };
}

async function main() {
  if (!DIRECT_LINE_SECRET) {
    console.error("Set DL_SECRET environment variable");
    process.exit(1);
  }

  const fs = await import("fs");
  const path = await import("path");

  const outDir = path.join(__dirname, "..", "..", "docs", "test-responses", "phase-2-connector");
  fs.mkdirSync(outDir, { recursive: true });

  const results: Array<{
    id: string;
    section: string;
    prompt: string;
    response: string;
    timestamp: string;
  }> = [];

  console.log("=== Phase 2 Custom Connector Agent Test ===\n");
  console.log(`Firing ${PROMPTS.length} prompts at GCC Copilot Studio agent...\n`);

  for (const p of PROMPTS) {
    console.log(`[${p.id}] ${p.section}: ${p.prompt.substring(0, 60)}...`);

    try {
      // New conversation per prompt for clean state
      const conv = await startConversation();
      await sendMessage(conv.conversationId, conv.token, p.prompt);
      const { text } = await pollForResponse(conv.conversationId, conv.token);

      results.push({
        id: p.id,
        section: p.section,
        prompt: p.prompt,
        response: text,
        timestamp: new Date().toISOString(),
      });

      console.log(`  -> ${text.substring(0, 100)}${text.length > 100 ? "..." : ""}\n`);

      // Small delay between prompts to be polite
      await new Promise((resolve) => setTimeout(resolve, 2000));
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : String(err);
      console.error(`  -> ERROR: ${errMsg}\n`);
      results.push({
        id: p.id,
        section: p.section,
        prompt: p.prompt,
        response: `[ERROR] ${errMsg}`,
        timestamp: new Date().toISOString(),
      });
    }
  }

  // Write JSON results
  const jsonPath = path.join(outDir, "results.json");
  fs.writeFileSync(jsonPath, JSON.stringify(results, null, 2));
  console.log(`\nJSON results: ${jsonPath}`);

  // Write readable markdown
  const mdLines = [
    "# Phase 2 Custom Connector Agent — Test Results",
    "",
    `**Date:** ${new Date().toISOString().split("T")[0]}`,
    `**Agent:** GCC Copilot Studio + Custom Connector (DSS Case API)`,
    `**Model:** GPT-4o (GCC default)`,
    `**Prompts:** ${PROMPTS.length}`,
    "",
    "---",
    "",
  ];

  let currentSection = "";
  for (const r of results) {
    if (r.section !== currentSection) {
      currentSection = r.section;
      mdLines.push(`## ${currentSection}`, "");
    }
    mdLines.push(`### Prompt ${r.id}`, "");
    mdLines.push(`**Q:** ${r.prompt}`, "");
    mdLines.push(`**A:** ${r.response}`, "");
    mdLines.push("---", "");
  }

  const mdPath = path.join(outDir, "results.md");
  fs.writeFileSync(mdPath, mdLines.join("\n"));
  console.log(`Markdown results: ${mdPath}`);
  console.log("\nDone.");
}

main().catch(console.error);
