import Tooltip from "./tooltip/tooltip.js";
import AbilityTooltip from "./tooltip/abilityTooltip.js";
import HeroTooltip from "./tooltip/heroTooltip.js";
import ItemTooltip from "./tooltip/itemTooltip.js";
import AghanimTooltip from "./tooltip/aghanimTooltip.js";

let files_downloaded = false;
const file_set = new Set();
let files_len = 0;
let abilities = {},
  stats = {},
  hero_colors,
  items;
async function get_json_data(hero_name) {
  if (hero_name) {
    abilities[hero_name] = await get_json("abilities", hero_name);
    stats = await get_json("stats", hero_name);
  } else {
    items = await get_json("items");
    hero_colors = await get_json("ability_colours");
  }
}
const download_limiter = (p, start) => {
  if (!files_downloaded) {
    for (let i = start; i < p.size; i++) {
      get_json_data([...p][i]);
    }
    files_downloaded = true;
  }
};
const fetch_ability_json = () => {
  const collection = document.getElementsByClassName("abilities");
  let start_point;
  for (let item of collection) {
    file_set.add(item.getAttribute("data-hero"));
    if (file_set.size > files_len) {
      files_downloaded = false;
      start_point = files_len;
    }
  }
  files_len = file_set.size;
  download_limiter(file_set, start_point);
};
get_json_data();
const styleBackground = (tooltip, imgSrc, aghanim_ability) => {
  //   tooltip.style.background = `linear-gradient(137deg, rgba(35 35 35), rgb(60,60,60) )`;
  for (const i of hero_colors.colors) {
    if (imgSrc.includes("launch_fire_spirit")) {
      // phoenix edge case
      imgSrc = "phoenix_fire_spirits";
    }
    if (imgSrc.includes(i.ability)) {
      tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, #182127 160px)`;
      return;
    } else {
      if (aghanim_ability && i.ability.includes(aghanim_ability["name"])) {
        tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, #182127 160px)`;
        return;
      }
    }
  }
  tooltip.style.background = `#182127`;
};
const getTooltipType = (tooltip) => {
  return tooltip.id.replace("-tooltip", "");
};

window.addEventListener("mouseover", (event) => {
  fetch_ability_json();
  if (
    event.target.className !== "item-img" &&
    event.target.className !== "table-img" &&
    event.target.className !== "hero-img"
  )
    return;
  let tooltip, _id, imgSrc, aghanim_ability;
  for (let element of event.target.parentNode.children) {
    if (element.className === "tooltip") tooltip = element;
    _id = event.target.getAttribute("data_id");
    if (_id == "5631") _id = "5625";
    imgSrc = event.target.getAttribute("src");
  }
  const tooltipType = getTooltipType(tooltip);
  const hero =
    event.target.parentNode.parentNode.getAttribute("data-hero") ||
    event.target.getAttribute("data-hero");
  const result = getResult(tooltipType, hero);
  if (tooltipType === "shard" || tooltipType === "scepter") {
    aghanim_ability = extract_aghanim(result, tooltipType);
  }
  styleBackground(tooltip, imgSrc, aghanim_ability);

  let base = aghanim_ability || result[_id] || result;
  if (tooltip.id === "item-tooltip") {
    for (let i = 0; i < result["items"].length; i++) {
      if (result["items"][i]["id"] === +_id) {
        base = result["items"][i];
      }
    }
  }
  const tooltip_method = new Tooltip(tooltip, tooltipType, base);
  if (tooltip.id === "talent-tooltip") {
    tooltip_method.generateLineOne();
    return;
  } else if (tooltipType === "hero") {
    const heroTooltip = new HeroTooltip(tooltip, tooltipType, base);
    heroTooltip.main();
    const color = document.getElementById("hero-name").style.color;
    tooltip.style.background = `radial-gradient(circle at top left, ${color}, #182127 190px)`;
    return;
  } else if (tooltipType === "shard" || tooltipType === "scepter") {
    const aghanimTooltip = new AghanimTooltip(tooltip, tooltipType, base);
    aghanimTooltip.main();
  } else if (tooltipType === "item") {
    const itemTooltip = new ItemTooltip(tooltip, tooltipType, base);
    itemTooltip.main();
  } else {
    const abilityTooltip = new AbilityTooltip(tooltip, tooltipType, base);
    abilityTooltip.main();
  }
  positionTooltip(tooltip, event);
});
const positionTooltip = (tooltip, event) => {
  let tooltipHeight = tooltip.offsetHeight;
  tooltip.style.top = `-${tooltipHeight / 2}px`;
  tooltip.style.left = `${event.target.clientWidth}px`;
  if (tooltip.getBoundingClientRect().bottom > window.innerHeight) {
    tooltip.style.top = `-${tooltipHeight}px`;
    tooltip.style.left = `-0px`;
  } else if (tooltip.getBoundingClientRect().top < 0) {
    tooltip.style.top = 0;
  }
  tooltip.style.display = "block";
};

function extract_aghanim(result, s) {
  for (let ability in result) {
    const aghanim =
      result[ability][`ability_is_granted_by_${s}`] ||
      result[ability][`ability_has_${s}`];
    if (aghanim || result[ability][`${s}_loc`].length > 0) {
      return result[ability];
    }
  }
}

const getResult = (tooltipType, hero) => {
  let result = [];
  if (tooltipType === "hero") {
    result = stats["result"]["data"]["heroes"][0];
  } else if (tooltipType === "item") {
    result = items;
  } else if (
    tooltipType === "ability" ||
    tooltipType === "shard" ||
    tooltipType === "scepter"
  ) {
    result = abilities[hero];
  }
  return result;
};
export default extract_aghanim;
