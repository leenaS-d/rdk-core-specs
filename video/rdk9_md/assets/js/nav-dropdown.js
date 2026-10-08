document.addEventListener("click", (event) => {
  for (const dropdown of document.querySelectorAll(".nav-dropdown[open]")) {
    if (!dropdown.contains(event.target)) {
      dropdown.open = false;
    }
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    for (const dropdown of document.querySelectorAll(".nav-dropdown[open]")) {
      dropdown.open = false;
    }
  }
});