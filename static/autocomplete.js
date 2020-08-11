// sort out this fetch request
async function get_hero_data() {
  let url = `${window.location.origin}/files/hero_ids`;
  let res = await fetch(url);
  let data = await res.json();
  return data;
}
arr = [];
let cells = document.querySelectorAll(".col"),
  search = document.getElementById("search"),
  heroGrid = document.querySelector(".hero-grid"),
  statText = document.querySelectorAll(".win-stats"),
  ul = document.querySelector("ul");

const autocomplete = () => {
  data = get_hero_data();
  data.then((result) => {
    search.addEventListener("input", (e) => {
      if (e.target.value.length > 1) {
        hideHeroes();
        sort = result.heroes.sort(compWrap(1));
        arr = sort.filter((x) =>
          x.name
            .toLowerCase()
            .replace(/_/g, " ")
            .includes(e.target.value.toLowerCase())
        );
      }
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
  for (let hero of heroes) {
    str = "";
    if (hero.length > 1) {
      for (let char of hero) {
        str += char[0];
      }
      if (str.includes(e.toLowerCase())) {
        for (let entry of result) {
          if (entry.name === hero.join("_").toLowerCase()) {
            arr.unshift({ id: entry.id, name: entry.name });
          } else if (entry.name === hero.join("-").toLowerCase()) {
            arr.unshift({ id: entry.id, name: entry.name });
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
    console.log(displayArr.length);
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
      reset();
    }
  }
};

const hideHeroes = () => {
  pickSort(null);
  for (let hero of cells) {
    hero.classList.add("hide");
  }
};
const compWrap = (n) => {
  return function compare(a, b) {
    let heroA = a.name,
      heroB = b.name,
      comparison = 0;
    if (heroA > heroB) {
      comparison = 1;
    } else if (heroA < heroB) {
      comparison = -1;
    }
    return n == 1 ? comparison : (comparison *= -1);
  };
};
const autoFocus = (event) => {
  let keyCodes = [13, 27, 40, 38, 39, 37, 9];
  // focus search on keypress
  if (!keyCodes.includes(event.keyCode)) {
    search.focus();
  }
};

let x = 0,
  count = 0;
window.addEventListener("keydown", (event) => {
  let suggestionList = document.querySelector("#suggestion-list");
  autoFocus(event);
  if (event.keyCode == 27 || search.value.length < 1) {
    // esc clears search
    search.value = "";
    reset();
  }
  if (suggestionList.children.length) {
    // arrow key selection of autocomplete suggestions
    if (event.keyCode == 40) {
      count++;
      x = x < suggestionList.children.length - 1 && count > 1 ? x + 1 : 0;
    } else if (event.keyCode == 38) {
      count++;
      x = x > 0 && count > 1 ? x - 1 : suggestionList.children.length - 1;
    } else if (event.keyCode == 13) {
      search.value = suggestionList.children[x].children[0].textContent;
    }
    suggestionList.children[x].children[0].style.backgroundColor =
      "rgb(65, 65, 65)";
    for (let i = 0; i < suggestionList.children.length; i++) {
      if (i != x) {
        suggestionList.children[i].children[0].style.backgroundColor =
          "inherit";
      }
    }
  }
});

const reset = () => {
  x = 0;
  if (search.value === "") {
    ul.innerHTML = "";
    for (let hero of cells) {
      hero.classList.remove("hide");
      heroGrid.classList.remove("right");
      heroGrid.classList.remove("hide");
      hero.classList.remove("first");
      document.querySelector(".buttons").style.display = "flex";
    }
    for (let stat of statText) {
      stat.classList.remove("hide");
    }
  }
};

window.addEventListener("mouseover", (event) => {
  // console.log(event.target);
});
autocomplete();
