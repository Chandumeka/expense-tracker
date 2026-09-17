/* =========================================================
   script.js
   Handles: theme (light/dark) persistence, delete confirmation
   modals, and auto-dismissing flash alerts.
   ========================================================= */

// ---------- THEME TOGGLE ----------
function initTheme() {
  const savedTheme = localStorage.getItem("expense_tracker_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const next = current === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("expense_tracker_theme", next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  const icon = document.getElementById("theme-icon");
  if (!icon) return;
  icon.className = theme === "light" ? "bi bi-moon-stars-fill" : "bi bi-sun-fill";
}

// ---------- DELETE CONFIRMATION ----------
function confirmDelete(formId, itemLabel) {
  if (confirm(`Are you sure you want to delete this ${itemLabel || "item"}? This cannot be undone.`)) {
    document.getElementById(formId).submit();
  }
}

// ---------- AUTO-DISMISS FLASH ALERTS ----------
function autoDismissAlerts() {
  const alerts = document.querySelectorAll(".alert-auto-dismiss");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.classList.remove("show");
      alert.classList.add("fade");
      setTimeout(() => alert.remove(), 300);
    }, 4000);
  });
}

// ---------- TOGGLE ADD TRANSACTION FORM FIELDS BASED ON TYPE ----------
function handleTypeChange(selectEl) {
  const categorySelect = document.getElementById("category");
  if (!categorySelect) return;

  if (selectEl.value === "income") {
    // Limit categories sensibly for income vs expense
    setCategoryOptions(categorySelect, ["Salary", "Other"]);
  } else {
    setCategoryOptions(categorySelect, ["Food", "Travel", "Bills", "Shopping", "Other"]);
  }
}

function setCategoryOptions(selectEl, options) {
  selectEl.innerHTML = "";
  options.forEach((opt) => {
    const optionEl = document.createElement("option");
    optionEl.value = opt;
    optionEl.textContent = opt;
    selectEl.appendChild(optionEl);
  });
}

// ---------- INIT ON PAGE LOAD ----------
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  autoDismissAlerts();

  const themeBtn = document.getElementById("theme-toggle-btn");
  if (themeBtn) {
    themeBtn.addEventListener("click", toggleTheme);
  }

  const typeSelect = document.getElementById("type");
  if (typeSelect) {
    typeSelect.addEventListener("change", () => handleTypeChange(typeSelect));
  }
});
