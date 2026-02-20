/**
 * DSS Legal Case Intelligence — Agent Chat Panel
 * Sends messages to /chat endpoint, renders markdown responses with tool badges.
 */

const AgentChat = (function () {
  "use strict";

  // Configure the backend URL — points to the Container App chat endpoint
  const CHAT_API_URL = window.__CHAT_API_URL || "https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/chat";

  const messagesContainer = document.getElementById("chatMessages");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");
  const suggestedPrompts = document.getElementById("suggestedPrompts");

  const conversationHistory = [];

  // ---- Markdown Rendering ----
  function renderMarkdown(text) {
    if (typeof marked !== "undefined") {
      return marked.parse(text);
    }
    // Fallback: escape HTML and convert newlines
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\n/g, "<br>");
  }

  // ---- Message Rendering ----
  function addMessage(role, content, toolsCalled) {
    // Hide suggested prompts after first message
    if (suggestedPrompts) {
      suggestedPrompts.style.display = "none";
    }

    const messageEl = document.createElement("div");
    messageEl.className = `message ${role}`;

    if (role === "assistant") {
      const contentEl = document.createElement("div");
      contentEl.className = "content";
      contentEl.innerHTML = renderMarkdown(content);
      messageEl.appendChild(contentEl);

      // Tool badges
      if (toolsCalled && toolsCalled.length > 0) {
        const badgesEl = document.createElement("div");
        badgesEl.className = "tool-badges";

        // Deduplicate tool names
        const uniqueTools = [...new Set(toolsCalled.map((t) => t.name))];
        uniqueTools.forEach((name) => {
          const badge = document.createElement("span");
          badge.className = "tool-badge";
          badge.textContent = name;
          badgesEl.appendChild(badge);
        });

        messageEl.appendChild(badgesEl);
      }
    } else {
      messageEl.textContent = content;
    }

    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function addTypingIndicator() {
    const indicator = document.createElement("div");
    indicator.className = "typing-indicator";
    indicator.id = "typingIndicator";
    indicator.innerHTML =
      '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
    messagesContainer.appendChild(indicator);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function removeTypingIndicator() {
    const indicator = document.getElementById("typingIndicator");
    if (indicator) {
      indicator.remove();
    }
  }

  // ---- Send Message ----
  async function sendMessage(text) {
    const trimmed = text.trim();
    if (!trimmed) return;

    addMessage("user", trimmed);
    conversationHistory.push({ role: "user", content: trimmed });

    chatInput.value = "";
    chatInput.style.height = "auto";
    chatInput.disabled = true;
    sendBtn.disabled = true;

    addTypingIndicator();

    try {
      const response = await fetch(CHAT_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: conversationHistory }),
      });

      removeTypingIndicator();

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error || `Request failed with status ${response.status}`
        );
      }

      const data = await response.json();
      const assistantContent =
        data.content || "I was unable to generate a response.";

      addMessage("assistant", assistantContent, data.tools_called);
      conversationHistory.push({
        role: "assistant",
        content: assistantContent,
      });
    } catch (error) {
      removeTypingIndicator();
      addMessage(
        "assistant",
        `**Error:** ${error.message || "Failed to connect to the agent. Please try again."}`
      );
    } finally {
      chatInput.disabled = false;
      sendBtn.disabled = false;
      chatInput.focus();
    }
  }

  // ---- Event Listeners ----
  sendBtn.addEventListener("click", () => sendMessage(chatInput.value));

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(chatInput.value);
    }
  });

  // Auto-resize textarea
  chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
  });

  // Suggested prompt chips
  document.querySelectorAll(".prompt-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt");
      sendMessage(prompt);
    });
  });

  return { sendMessage };
})();
