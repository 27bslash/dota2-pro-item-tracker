let matchData,
  appended = false,
  heroName = window.location.pathname
    .replace("/starter_items", "")
    .replace(/.+\//, ""),
  filterItem = "";
const itemSet = new Set();

async function get_json_data(search) {
  const url = `${window.location.origin}/files/${search}${window.location.search}`;
  const req = await fetch(url);
  matchData = await req.json();
  return matchData;
}

const pro_items = async () => {
  sorted = [];
  const black_lst = [
    "ward_sentry",
    "ward_observer",
    "clarity",
    "tpscroll",
    "enchanted_mango",
    "smoke_of_deceit",
    "tango",
    "faerie_fire",
    "tome_of_knowledge",
    "healing_salve",
    null,
  ];
  const output = [];
  for (let x of matchData) {
    for (let item of x["final_items"]) {
      if (!black_lst.includes(item["key"])) {
        output.push(item["key"]);
      }
    }
  }
  const counter = output.reduce(function (obj, item) {
    obj[item] = (obj[item] || 0) + 1;
    return obj;
  }, {});
  sorted = Object.entries(counter).sort((a, b) => b[1] - a[1]);
  return sorted;
};

const populate_most_used = () => {
  pro_items().then((res) => {
    const container = document.querySelector(".most-used");
    const max = res[0][1];

    for (let arr of res) {
      const key = arr[0];
      const value = arr[1];
      if (itemSet.has(key)) {
        break;
      }
      if (value < 2) break;
      const s = (value / max) * 100;
      const saturation = parseInt(Math.round(s));
      const row = document.createElement("div");
      row.setAttribute("class", "most-used-row");
      const img = document.createElement("img");
      img.setAttribute(
        "src",
        `//ailhumfakp.cloudimg.io/v7/https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/${key}_lg.png`
      );
      img.setAttribute("class", "most-used-item");
      const bar = document.createElement("div");
      bar.setAttribute("class", "bar");
      bar.style.cssText = `background-color: hsl(120,100%,25%, ${saturation}%); width: ${
        (value / max) * 80
      }%`;
      const barValue = document.createElement("p");
      barValue.setAttribute("class", "bar-value");
      barValue.innerText = value;

      bar.appendChild(barValue);
      row.appendChild(img);
      row.appendChild(bar);
      row.addEventListener("click", (e) => {
        searchEl = document.querySelector("input[type=search]");
        searchEl.value = key;
        searchEl.focus();
        filterItem = { key: key, winrate: value };
      });
      if (container.childElementCount === 10) {
        break;
      } else if (row) {
        container.appendChild(row);
        itemSet.add(key);
      }
    }
  });
};
document.addEventListener("DOMContentLoaded", () => {
  matchData = get_json_data(`match-data/${heroName}`);
  document.addEventListener("click", function (e) {
    console.log("clikc", e.target.className);
    if (
      e.target.className === "arrow-button" ||
      e.target.className === "fas fa-caret-up"
    ) {
      populate_most_used();
    }
  });
});
