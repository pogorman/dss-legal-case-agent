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

  // ---- Warm Up Button + Popup ----
  const warmupBtn = document.getElementById("warmupBtn");
  const warmupStatus = document.getElementById("warmupStatus");
  const warmupPopup = document.getElementById("warmupPopup");
  const warmupFooter = document.getElementById("warmupFooter");
  const CHAT_API_URL = window.__CHAT_API_URL || "https://dss-case-agent.victoriouspond-48a6f41b.eastus2.azurecontainerapps.io/chat";
  const HEALTH_URL = CHAT_API_URL.replace(/\/chat$/, "/healthz");
  let warmupRunning = false;

  function setStep(id, state, detail) {
    const step = document.getElementById(id);
    const detailEl = document.getElementById(id + "Detail");
    step.className = "warmup-step " + state;
    detailEl.textContent = detail;
  }

  function resetSteps() {
    ["stepContainer", "stepDatabase", "stepAI"].forEach((id) => {
      setStep(id, "", "Waiting...");
    });
    warmupFooter.className = "warmup-footer";
    warmupFooter.textContent = "";
  }

  warmupBtn.addEventListener("click", async () => {
    if (warmupRunning) return;
    warmupRunning = true;

    // Reset and show popup
    resetSteps();
    warmupPopup.classList.add("open");
    warmupBtn.classList.remove("ready", "error");
    warmupBtn.classList.add("warming");
    warmupStatus.textContent = "";

    const totalStart = Date.now();

    // Stage 1: Container wake-up (healthz)
    setStep("stepContainer", "active", "Waking container...");
    let containerOk = false;
    try {
      const t0 = Date.now();
      const res = await fetch(HEALTH_URL);
      if (!res.ok) throw new Error(res.status);
      const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
      setStep("stepContainer", "done", `Online (${elapsed}s)`);
      containerOk = true;
    } catch {
      setStep("stepContainer", "error", "Failed to reach container");
    }

    if (!containerOk) {
      warmupBtn.classList.remove("warming");
      warmupBtn.classList.add("error");
      warmupStatus.textContent = "failed";
      warmupFooter.className = "warmup-footer show error";
      warmupFooter.textContent = "Warm-up failed — container unreachable";
      warmupRunning = false;
      autoClosePopup(5000);
      return;
    }

    // Stage 2 + 3: Real chat request (warms DB + AI in one call)
    setStep("stepDatabase", "active", "Connecting to SQL...");
    setStep("stepAI", "active", "Loading AI model...");
    try {
      const t0 = Date.now();
      const res = await fetch(CHAT_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [{ role: "user", content: "List available cases" }],
        }),
      });
      if (!res.ok) throw new Error(res.status);
      await res.json();
      const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
      setStep("stepDatabase", "done", `Connected (${elapsed}s)`);
      setStep("stepAI", "done", `Loaded (${elapsed}s)`);
    } catch {
      setStep("stepDatabase", "error", "Connection failed");
      setStep("stepAI", "error", "Load failed");
      warmupBtn.classList.remove("warming");
      warmupBtn.classList.add("error");
      warmupStatus.textContent = "failed";
      warmupFooter.className = "warmup-footer show error";
      warmupFooter.textContent = "Warm-up failed — chat pipeline error";
      warmupRunning = false;
      autoClosePopup(5000);
      return;
    }

    // All done
    const totalElapsed = ((Date.now() - totalStart) / 1000).toFixed(1);
    warmupBtn.classList.remove("warming");
    warmupBtn.classList.add("ready");
    warmupStatus.textContent = "ready";
    warmupFooter.className = "warmup-footer show ready";
    warmupFooter.textContent = `All services ready — ${totalElapsed}s total`;
    warmupRunning = false;
    autoClosePopup(4000);
  });

  function autoClosePopup(delay) {
    setTimeout(() => {
      warmupPopup.classList.remove("open");
    }, delay);
  }

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
