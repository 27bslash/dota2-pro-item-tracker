let elm;
const changePickCounter = async () => {
  //   if (!filterItem) return;
  res = await el();
  if (!res) return;
  res = res[0].trim();

  let pickCounter = document.querySelector(".pick-counter");
  const newPickCounter = document.createElement("div");
  newPickCounter.classList.add("pick-counter");
  const matchData = await get_json_data(`match-data/${heroName}`);
  const totalEntries = matchData.length;
  boldName = pickCounter.children[0];
  newPickCounter.appendChild(boldName);
  //   const searchResults = document.createElement("p");
  //   searchResults.innerText = filterItem["winrate"];
  //   let winrate = calculate_wr();
  //   newPickCounter.appendChild(searchResults);
  const itemJson = await get_json("items");
  
  const searchVal = searchEl.value.replace(/\s|\-/g, "_").toLowerCase();
  const itemArr = itemSearch(itemJson, searchVal);

  let wins = 0;
  let fields = [
    "hero",
    "name",
    "final_items.key",
    "item_neutral",
    "aghanims_shard.key",
    "backpack.key",
    "radiant_draft",
    "dire_draft",
  ];
  let ids = new Set();
  for (let match of matchData) {
    let added = false;
    // go through every match in dataset
    for (let field of fields) {
      //   if (!match[field]) continue;
      // fo through all fields
      spl = field.split(".");
      let queryField = match[field] || match[spl[0]];
      if (!queryField) continue;
      if (added) continue;
      if (spl[1]) {
        // console.log(field, queryField);
        for (let item of queryField) {
          if (item.key.match(searchVal)) {
            // console.log("break", item, field, res);
            ids.add(match["id"]);
            added = true;
            if (match["win"] === 1) {
              wins += 1;
            }
            break;
          }

          for (let jtem of itemArr) {
            const m = jtem.match(item.key);
            if (m) {
              ids.add(match["id"]);
              added = true;
              if (match["win"] === 1) {
                wins += 1;
              }
              break;
            }
          }
        }
      } else if (Array.isArray(match[field])) {
        for (let item of match[field]) {
          //   console.log(item, searchVal, field);
          if (item.match(searchVal) || item.match(heroSwitcher(searchVal))) {
            // console.log(match, item);
            ids.add(match["id"]);
            added = true;
            if (match["win"] === 1) {
              wins += 1;
            }
            break;
          }
        }
      } else {
        // console.log(match, field);
        if (match[field].match(searchVal)) {
          ids.add(match["id"]);
          added = true;
          if (match["win"] === 1) {
            wins += 1;
          }
        }
      }
    }
  }
  let winRate = (wins / ids.size) * 100;
  const winrateEl = document.createElement("span");
  winrateEl.innerText = `(${winRate.toFixed(2)}%)`;
  colour_wins(winrateEl, winRate);
  let textString = `was picked ${ids.size} times, with a winrate of `;
  te = document.createElement("p");
  te.innerText = textString;
  te.appendChild(winrateEl);
  te.style = "color: white";
  newPickCounter.appendChild(te);
  pickCounter.replaceWith(newPickCounter);
};
const calculate_wr = () => {};
const el = async () => {
  elm = await waitForElm("#DataTables_Table_0_info");
  return elm.innerText.match(/\d+ (?=entries)/gm);
};
searchEl = document.querySelector("input[type=search]");
const addEventListenerIfExists = async () => {
  elm = await waitForElm("input[type=search]");
  searchEl = elm;
  elm.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      changePickCounter();
    }
  });
};
function waitForElm(selector) {
  return new Promise((resolve) => {
    if (document.querySelector(selector)) {
      return resolve(document.querySelector(selector));
    }

    const observer = new MutationObserver((mutations) => {
      if (document.querySelector(selector)) {
        resolve(document.querySelector(selector));
        observer.disconnect();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  });
}


const itemSearch = (itemsArr, search) => {
  l = new Set();
  for (let item of itemsArr["items"]) {
    if (
      item["name"].includes(search) ||
      item["displayName"].toLowerCase().includes(search.replace(/_-/g, " "))
    ) {
      l.add(item["name"]);
    }
  }
  return l;
};
const heroSwitcher = (key) => {
  const heroes = {
    necrophos: "necrolyte",
    clockwerk: "rattletrap",
    "nature's_prophet": "furion",
    timbersaw: "shredder",
    io: "wisp",
    queen_of_pain: "queenofpain",
    doom: "doom_bringer",
    shadow_fiend: "nevermore",
    wraith_king: "skeleton_king",
    magnus: "magnataur",
    underlord: "abyssal_underlord",
    "anti-mage": "antimage",
    outworld_destroyer: "obsidian_destroyer",
    outworld_devourer: "obsidian_destroyer",
    lifestealer: "life_stealer",
    windranger: "windrunner",
    zeus: "zuus",
    vengeful_spirit: "vengefulspirit",
    treant_protector: "treant",
    centaur_warrunner: "centaur",
  };
  if (key in heroes) {
    return heroes[key];
  }
  return key;
};
addEventListenerIfExists();
const colour_wins = (el, val) => {
  if (+val < 50 && +val > 30) {
    el.style.color = `hsl(0, 100%, ${val}%)`;
  } else if (+val <= 30) {
    el.style.color = "hsl(0,100%, 30%)";
  } else if (+val > 80) {
    el.style.color = "rgb(120 255 152)";
  } else {
    el.style.color = `hsl(134, 100%,${val}%)`;
  }
};
