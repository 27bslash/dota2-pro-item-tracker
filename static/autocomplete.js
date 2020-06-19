async function t() {
  let res = await fetch("files/hero_ids");
  let data = await res.json();
  return data;
}
arr = [];
let lst = document.querySelector("ul");
let search = document.getElementById("search");
function autocomplete() {
  data = t();
  data.then((result) => {
    search.addEventListener("input", (e) => {
      if (e.target.value.length > 2) {
        arr = result.heroes.filter((x) =>
          x.name
            .toLowerCase()
            .replace(/_/g, " ")
            .includes(e.target.value.toLowerCase())
        );
      }
      display(arr);
    });
  });
}
autocomplete();

const display = () => {
  lst.innerHTML = "";
  let displayArr = [];
  let linkArr = [];
  for (let h of arr) {
    linkArr.push(h.name);
    displayArr.push(h.name.replace(/_/g, " "));
  }
  for (let i = 0; i < displayArr.length; i++) {
    const div = document.createElement("div");
    div.innerHTML = displayArr[i];
    let a = document.createElement("a");
    a.href = `hero/${linkArr[i]}`;
    div.setAttribute("class", "hero-suggestion");
    a.setAttribute("class", "suggestion-link");
    lst.appendChild(a).appendChild(div);
  }
  if (search.value === "") {
    console.log(lst);
    lst.innerHTML = "";
  }
};
// document.addEventListener("click", function (e) {
//   if (e.target.className === "hero-suggestion") {
//     console.log(document.getElementById("search").value);
//     document.getElementById("search").value = e.target.innerHTML;
//     lst.innerHTML = "";
//   }
// });
// document.getElementById("search").addEventListener("keyup", function (e) {
//   if (e.key == "ArrowDown") {
//     let suggestionIdx = -1;
//     resetSuggestion();
//     suggestionIdx =(suggestionidx < lst.children.length - 1)
//         ? suggestionIdx + 1
//         : lst.children.length - 1;
//     lst[suggestionidx].classList.add("selected");
//     return;
//   }
// });
// const resetSuggestion = () => {
//   for (let i = 0; i < lst.children.length; i++) {
//     lst.children[i].classList.remove("selected");
//   }
// };
