let cells = document.querySelectorAll(".col"),
  arr = [],
  search = document.getElementById("search"),
  heroGrid = document.querySelector(".hero-grid"),
  statText = document.querySelectorAll(".win-stats"),
  ul = document.querySelector("ul");

async function get_hero_data() {
  const url = `${window.location.origin}/files/hero_ids`;
  const res = await fetch(url);
  const data = await res.json();
  return data;
}
const autocomplete = () => {
  data = get_hero_data();
  data.then((result) => {
    search.addEventListener("input", (e) => {
      if (e.target.value.length < 2) return;
      hideHeroes();
      sort = result.heroes.sort(compWrap(1));
      arr = sort.filter((x) =>
        x.name
          .toLowerCase()
          .replace(/_/g, " ")
          .includes(e.target.value.toLowerCase())
      );

      abbreviations(e.target.value, result.heroes.sort(compWrap(0)));
      display();
    });
  });
};

const abbreviations = (e, result) => {
  let heroes = [],
    regex = /[\-_\s]/;
  for (let hero of result) {
    split = hero.name.split(regex);
    heroes.push(split);
  }
  for (let splitHero of heroes) {
    str = "";
    if (splitHero.length > 1) {
      for (let char of splitHero) {
        str += char[0];
      }
      if (str.includes(e.toLowerCase())) {
        for (let hero of result) {
          if (
            hero.name === splitHero.join("_").toLowerCase() ||
            hero.name === splitHero.join("-").toLowerCase()
          ) {
            arr.unshift({ id: hero.id, name: hero.name });
          }
        }
      }
    }
  }
};

const display = () => {
  let suggestions = document.querySelector(".suggestions"),
    displayArr = [],
    linkArr = [];
  ul.innerHTML = "";
  suggestions.classList.add("hide");
  for (let stat of statText) {
    stat.classList.add("hide");
  }
  for (let h of arr) {
    linkArr.push(h.name);
    displayArr.push(h.name.replace(/_/g, " "));
  }
  if (displayArr.length > 20) {
    displayArr = displayArr.slice(0, 15);
    linkArr = linkArr.slice(0, 15);
  }
  for (let i = 0; i < displayArr.length; i++) {
    let div = document.createElement("div"),
      a = document.createElement("a");
    div.innerHTML = displayArr[i];
    a.href = `${window.location.origin}/hero/${linkArr[i]}`;
    div.setAttribute("class", "hero-suggestion");
    div.setAttribute("id", `suggestion-${linkArr[i]}`);
    a.setAttribute("class", "suggestion-link");
    ul.appendChild(a).appendChild(div);
    suggestions.classList.remove("hide");
    link = document.getElementById(linkArr[i]);
    if (link && search.value.length > 1) {
      link.classList.remove("hide");
      if (i == 0) {
        link.parentNode.parentNode.classList.add("first");
      }
      link.parentNode.parentNode.classList.remove("hide");
      heroGrid.classList.add("right");
    }
  }
};

const hideHeroes = () => {
  // check if homepage
  if (
    (window.location.pathname.indexOf("/") + 1) %
      (window.location.pathname.lastIndexOf("/") + 1) ===
    0
  )
    document.querySelector(".buttons").style.display = "none";
  for (let hero of cells) {
    hero.classList.add("hide");
    hero.style.gridArea = null;
  }
};
const compWrap = (n) => {
  return function compare(a, b) {
    let heroA = a.name,
      heroB = b.name,
      comparison = 0;
    if (heroA > heroB) {
      comparison = 1;
    } else {
      comparison = -1;
    }
    return n == 1 ? comparison : (comparison *= -1);
  };
};
const autoFocus = (event) => {
  let keyCodes = [13, 27, 40, 38, 39, 37, 9];
  // focus search on keypress
  if (!keyCodes.includes(event.keyCode)) search.focus();
};

let x = 0,
  count = 0;
window.addEventListener("keydown", (event) => {
  let suggestionList = document.querySelector("#suggestion-list");
  autoFocus(event);
  if (!suggestionList.children.length) return;
  if (event.keyCode == 27 || search.value.length < 1) {
    // esc clears search
    reset();
  }
  // arrow key selection of autocomplete suggestions
  switch (event.keyCode) {
    case 40:
      count++;
      x = x < suggestionList.children.length - 1 && count > 1 ? x + 1 : 0;
      break;
    case 38:
      count++;
      x = x > 0 && count > 1 ? x - 1 : suggestionList.children.length - 1;
      break;
    case 13:
      search.value = suggestionList.children[x].children[0].textContent;
      break;
    default:
      break;
  }

  suggestionList.children[x].children[0].style.backgroundColor =
    "rgb(65, 65, 65)";
  for (let i = 0; i < suggestionList.children.length; i++) {
    if (i != x)
      suggestionList.children[i].children[0].style.backgroundColor = "inherit";
  }
});

const reset = () => {
  ul.innerHTML = "";
  search.value = "";
  for (let hero of cells) {
    heroGrid.classList.remove("right");
    heroGrid.classList.remove("hide");
    hero.classList.remove("hide");
    hero.classList.remove("first");
    document.querySelector(".buttons").style.display = "flex";
  }
  for (let stat of statText) {
    stat.classList.remove("hide");
  }
};
const closeAllTooltips = () => {
  document.querySelector(".talents").style.display = "none";
  document.querySelectorAll(".tooltip").forEach((x, i) => {
    x.style.display = "none";
  });
};
window.addEventListener("mouseover", (event) => {
  // console.log(event.target.className);
  closeAllTooltips();
  if (event.target.id === "main-talent-img") {
    document.querySelector(".talents").style.display = "grid";
  }
  if (event.target.className === "table-img") {
    console.log(event.target.parentNode.children[2]);
    event.target.parentNode.children[2].style.display = "block";
  }
});
closeAllTooltips();
autocomplete();
// ability_img = document.querySelectorAll(".table-img");
// for (let img in ability_img) {
//   img.addEventListener("mouseover", (e) => {
//     console.log(e);
//   });
// }
