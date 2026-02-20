/**
 * DSS Legal Case Intelligence — Main App Logic
 * Handles tab switching, auth display, and initialization.
 */

(function () {
  "use strict";

  // ---- Tab Switching ----
  const tabs = document.querySelectorAll(".tab");
  const panels = document.querySelectorAll(".panel");

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetPanel = tab.getAttribute("data-panel");

      tabs.forEach((t) => t.classList.remove("active"));
      panels.forEach((p) => p.classList.remove("active"));

      tab.classList.add("active");
      const panel = document.getElementById(`panel-${targetPanel}`);
      if (panel) {
        panel.classList.add("active");
      }

      // Load case data on first visit to browser tab
      if (targetPanel === "browser" && !window.__casesLoaded) {
        window.__casesLoaded = true;
        CaseBrowser.loadCases();
      }
    });
  });

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
