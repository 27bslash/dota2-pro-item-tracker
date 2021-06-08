const search = document.getElementById("search"),
  heroGrid = document.querySelector(".hero-grid"),
  statText = document.querySelectorAll(".win-stats"),
  ul = document.querySelector("ul"),
  heroSuggestionList = document.querySelector("#hero-suggestion-list"),
  playerSuggestionList = document.querySelector("#player-suggestion-list");
let cells = document.querySelectorAll(".hero-cell"),
  arr = [],
  elementsToHide = [],
  order = [],
  titleText,
  orderSet = new Set();

document.querySelector(".suggestions").style.display = "none";
async function get_json(search, hero_name) {
  let url = `${window.location.origin}/files/${search}`;
  if (search === "abilities") {
    url = `${window.location.origin}/files/abilities/${hero_name}`;
  }
  const res = await fetch(url);
  const data = await res.json();
  return data;
}
const hero_data = get_json("hero_ids");
const player_data = get_json("accounts");

const hero_autocomplete = () => {
  hero_data.then((result) => {
    search.addEventListener("input", (e) => {
      if (e.target.value.length < 2) {
        reset();
        return;
      }
      hideHeroes();
      sort = result.heroes.sort(compWrap(1));
      arr = sort.filter((x) =>
        x.name
          .toLowerCase()
          .replace(/_/g, " ")
          .includes(e.target.value.toLowerCase())
      );
      abbreviations(e.target.value, result.heroes.sort(compWrap(0)));
      hero_name_display();
    });
  });
};
const player_autocomplete = () => {
  player_data.then((result) => {
    search.addEventListener("input", (e) => {
      if (e.target.value.length < 2) return;
      document.querySelector(".suggestions").style.display = "grid";
      sort = result.sort();
      player_arr = sort.filter((x) => {
        return x.toLowerCase().includes(e.target.value.toLowerCase());
      });
      player_name_display(player_arr);
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

const player_name_display = (player_arr) => {
  playerSuggestionList.innerHTML = "";
  if (player_arr.length > 20) {
    player_arr = player_arr.slice(0, 15);
  }
  for (let player of player_arr) {
    let div = document.createElement("div"),
      a = document.createElement("a"),
      p = document.createElement("p");
    a.href = `${window.location.origin}/player/${player}`;
    a.setAttribute("class", "suggestion-link");
    div.setAttribute("class", "suggestion");
    div.setAttribute("id", player);
    p.innerHTML = player;
    playerSuggestionList.appendChild(a).appendChild(div).appendChild(p);
    document.querySelector(".suggestions").classList.remove("hide");
  }
};

const hero_name_display = () => {
  let suggestions = document.querySelector(".suggestions"),
    displayArr = [],
    linkArr = [];
  ul.innerHTML = "";
  if (
    !window.location.pathname.includes("hero") &&
    !window.location.pathname.includes("player")
  ) {
    document.querySelector(".sort-title").textContent = "";
    document.querySelector("#controls-arrow").classList.add("search-hide");
    document.querySelector(".info").classList.add("search-hide");
  }
  for (let stat of statText) {
    stat.classList.add("search-hide");
  }
  for (let hero of arr) {
    linkArr.push(hero.name);
    displayArr.push(hero.name.replace(/_/g, " "));
  }
  if (displayArr.length > 20) {
    displayArr = displayArr.slice(0, 15);
    linkArr = linkArr.slice(0, 15);
  }
  displayArr = displayArr.sort();
  for (let i = 0; i < displayArr.length; i++) {
    let div = document.createElement("div"),
      a = document.createElement("a"),
      p = document.createElement("p");
    p.innerHTML = displayArr[i];
    a.href = `${window.location.origin}/hero/${linkArr[i]}`;
    div.setAttribute("class", "suggestion");
    div.setAttribute("id", `suggestion-${linkArr[i]}`);
    a.setAttribute("class", "suggestion-link");
    ul.appendChild(a).appendChild(div).appendChild(p);
    suggestions.classList.remove("hide");
    link = document.getElementById(linkArr[i]);
    if (link && search.value.length > 1) {
      link.classList.remove("hide");
      linkContainer = link.parentNode.parentNode;
      linkContainer.classList.remove("search-hide");
      if (linkContainer.classList.contains("hide")) {
        elementsToHide.push(linkContainer);
      } else {
        _id = linkContainer.children[0].children[0].id;
        if (!orderSet.has(_id)) {
          orderSet.add(_id);
          el_order = linkContainer.style.order;
          order.push({ id: _id, order: el_order });
        }
      }
      linkContainer.style.order = null;
      linkContainer.classList.remove("hide");
      heroGrid.classList.add("right");
    }
  }
  cells.forEach((x) => {
    base = x.children[0].href.split("?")[0];
    if (search.value.length > 1 && !x.classList.contains("search-hide")) {
      x.children[0].href = base;
    }
  });
};

const hideHeroes = () => {
  // check if homepage
  if (
    (window.location.pathname.indexOf("/") + 1) %
      (window.location.pathname.lastIndexOf("/") + 1) ===
    0
  ) {
  }
  for (let hero of cells) {
    hero.classList.add("search-hide");
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
  if (!window.location.pathname.includes("player")) {
    if (!keyCodes.includes(event.keyCode)) {
      search.focus();
      document.querySelector(".suggestions").classList.add("hide");
    }
  }
};

let x = 0,
  count = 0,
  currList = heroSuggestionList;
window.addEventListener("keydown", (event) => {
  autoFocus(event);
  if (event.keyCode == 27 || search.value.length < 1) {
    // esc clears search
    search.value = "";
    reset();
    return;
  }
  if (
    !heroSuggestionList.children.length &&
    !playerSuggestionList.children.length
  )
    return reset();
  if (!heroSuggestionList.children.length) {
    currList = playerSuggestionList;
  }
  // arrow key selection of autocomplete suggestions
  switch (event.keyCode) {
    case 37:
      currList = heroSuggestionList;
      for (let i of playerSuggestionList.children) {
        i.children[0].style.backgroundColor = "inherit";
      }
      break;
    case 39:
      currList = playerSuggestionList;
      for (let i of heroSuggestionList.children) {
        i.children[0].style.backgroundColor = "inherit";
      }
      break;
    case 40:
      count++;
      x = x < currList.children.length - 1 && count > 1 ? x + 1 : 0;
      shownEls = [];
      if (currList === heroSuggestionList) {
        document.querySelectorAll(".hero-cell").forEach((el) => {
          if (!el.classList.contains("search-hide")) {
            shownEls.push(el);
          }
        });
        shownEls.forEach((el, i) => {
          if (i === x) {
            el.classList.add("hero-highlight");
          } else {
            el.classList.remove("hero-highlight");
          }
        });
      }
      break;
    case 38:
      count++;
      x = x > 0 && count > 1 ? x - 1 : currList.children.length - 1;
      shownEls = [];
      if (currList === heroSuggestionList) {
        document.querySelectorAll(".hero-cell").forEach((el) => {
          if (!el.classList.contains("search-hide")) {
            shownEls.push(el);
          }
        });
        shownEls.forEach((el, i) => {
          if (i === x) {
            el.classList.add("hero-highlight");
          } else {
            el.classList.remove("hero-highlight");
          }
        });
      }
      break;
    case 13:
      search.value = currList.children[x].children[0].textContent;
      break;
    default:
      break;
  }
  if (currList.children.length <= x) {
    x = 0;
  }
  if (currList.children.length > 0) {
    // console.log('hero,',currList.children[x].children[0]);
    currList.children[x].children[0].style.backgroundColor = "rgb(65, 65, 65)";
  }
  for (let i = 0; i < currList.children.length; i++) {
    if (i != x)
      currList.children[i].children[0].style.backgroundColor = "inherit";
  }
});

const reset = () => {
  ul.innerHTML = "";
  playerSuggestionList.innerHTML = "";
  if (
    !window.location.pathname.includes("hero") &&
    !window.location.pathname.includes("player")
  ) {
    document.querySelector(".sort-title").textContent =
      document.querySelector(".sort-title").id;
    document.querySelector(".info").classList.remove("search-hide");
    try {
      document.querySelector("#controls-arrow").classList.remove("search-hide");
    } catch (err) {
      console.log(err);
    }
  }
  document.querySelector(".suggestions").style.display = "none";
  for (let el of elementsToHide) {
    // re hide elements
    el.classList.add("hide");
  }
  for (let i of order) {
    // re order elements
    document.getElementById(i["id"]).parentNode.parentElement.style.order =
      i["order"];
  }
  if (heroGrid) {
    heroGrid.classList.remove("right");
    heroGrid.classList.remove("hide");
  }
  for (let hero of cells) {
    hero.classList.remove("search-hide");
    hero.classList.remove("hero-highlight");
  }
  for (let stat of statText) {
    stat.classList.remove("search-hide");
  }
  elementsToHide = [];
  order = [];
  orderSet = new Set();
};

const closeAllTooltips = () => {
  document.querySelectorAll(".tooltip").forEach((x, i) => {
    x.style.display = "none";
  });
};

window.addEventListener("mouseover", (event) => {
  closeAllTooltips();
  if (event.target.id === "main-talent-img") {
    document.getElementById("talents").style.display = "grid";
  }
  if (event.target.className === "table-img") {
    event.target.parentNode.children[2].style.display = "block";
  }
  if (event.target.className === "suggestion") {
    event.target.style.backgroundColor = "rgb(65, 65, 65)";
    for (let suggestion of heroSuggestionList.children) {
      if (suggestion.children[0] != event.target) {
        suggestion.children[0].style.backgroundColor = "inherit";
        // start keypress listener from whers the mouse is
        x = [...event.target.parentElement.parentElement.childNodes].indexOf(
          event.target.parentNode
        );
      }
    }
    for (let suggestion of playerSuggestionList.children) {
      if (suggestion.children[0] != event.target) {
        suggestion.children[0].style.backgroundColor = "inherit";
        x = [...event.target.parentElement.parentElement.childNodes].indexOf(
          event.target.parentNode
        );
      }
    }
  }
});
document.querySelectorAll(".sort-button").forEach((x) => {
  x.addEventListener("click", (event) => {
    cells.forEach((i) => {
      base = i.children[0].href.split("?")[0];
      i.children[0].href = base;
      if (event.target.id)
        i.children[0].href = `${base}?role=${event.target.id}`;
    });
  });
});

hero_autocomplete();
player_autocomplete();
