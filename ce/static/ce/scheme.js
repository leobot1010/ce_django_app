console.log("✅ scheme.js loaded");

document.addEventListener("DOMContentLoaded", function () {
  const deptInput = document.getElementById("id_new_departments");
  const checkbox = document.getElementById("id_departments_disabled");

  if (deptInput && checkbox) {
    deptInput.addEventListener("input", function () {
      if (deptInput.value.trim().length > 0) {
        checkbox.checked = false;  // Automatically uncheck
      }
    });
  }
});

