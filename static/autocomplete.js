// sort out this fetch request
async function t() {
  let url = `${window.location.origin}/files/hero_ids`;
  let res = await fetch(url);
  let data = await res.json();
  return data;
}
arr = [];
let heroGrid = document.querySelectorAll(".hero-img");
document.querySelector(".suggestions").classList.add("hide");
const autocomplete = () => {
  data = t();
  data.then((result) => {
    document.getElementById("search").addEventListener("input", (e) => {
      if (e.target.value.length > 1) {
        hideHeroes();
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
};
autocomplete();

const display = () => {
  document.querySelector("ul").innerHTML = "";
  document.querySelector(".suggestions").classList.add("hide");
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
    a.href = `${window.location.origin}/hero/${linkArr[i]}`;
    div.setAttribute("class", "hero-suggestion");
    a.setAttribute("class", "suggestion-link");
    document.querySelector("ul").appendChild(a).appendChild(div);
    document.querySelector(".suggestions").classList.remove("hide");
    if (document.getElementById(linkArr[i])) {
      document.getElementById(linkArr[i]).classList.remove("hide");
      document.querySelector(".hero-grid").classList.add("right");
    }
  }
  if (document.getElementById("search").value === "") {
    document.querySelector("ul").innerHTML = "";
    for (let hero of heroGrid) {
      hero.classList.remove("hide");
      document.querySelector(".hero-grid").classList.remove("right");
    }
  }
};
const hideHeroes = () => {
  for (let hero of heroGrid) {
    hero.classList.add("hide");
  }
};
