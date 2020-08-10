// hide most used items
itemWindow = document.querySelector(".most-used");
const toggleWindow = () => {
  itemWindow.classList.toggle("closed");
  if (itemWindow.classList.contains("closed")) {
    document.getElementById("arrow").className = "fas fa-caret-down";
  } else {
    document.getElementById("arrow").className = "fas fa-caret-up";
  }
};
