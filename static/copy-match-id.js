document.addEventListener("click", (event) => {
  if (event.target.className === "fas fa-copy") {
    navigator.clipboard.writeText(event.target.id);
  }
});
