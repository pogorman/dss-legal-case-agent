/**
 * DSS Legal Case Intelligence — Main App Logic
 * Handles floating chat widget, clear/reset, auth display, and initialization.
 */

(function () {
  "use strict";

  // ---- Floating Chat Widget ----
  const chatFab = document.getElementById("chatFab");
  const chatWidget = document.getElementById("chatWidget");
  const clearChatBtn = document.getElementById("clearChatBtn");

  chatFab.addEventListener("click", () => {
    const isOpen = chatWidget.classList.toggle("open");
    chatFab.classList.toggle("open", isOpen);
    if (isOpen) {
      const input = document.getElementById("chatInput");
      if (input) input.focus();
    }
  });

  // ---- Clear / New Chat ----
  clearChatBtn.addEventListener("click", () => {
    AgentChat.reset();
  });

  // ---- Load Cases on startup ----
  CaseBrowser.loadCases();

  // ---- Auth: display user email ----
  async function loadUserInfo() {
    try {
      const response = await fetch("/.auth/me");
      if (response.ok) {
        const data = await response.json();
        const principal = data.clientPrincipal;
        if (principal && principal.userDetails) {
          document.getElementById("userEmail").textContent =
            principal.userDetails;
        }
      }
    } catch {
      // Auth endpoint not available (local dev) — ignore
    }
  }

  loadUserInfo();
})();
