let hero_colors;
const hero_name = window.location.href.split("/").pop();
let files_downloaded = false;
const file_set = new Set();
let files_len = 0;
let abilities = {},
  stats = {};
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
  collection = document.getElementsByClassName("abilities");
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
window.addEventListener("mouseover", (event) => {
  fetch_ability_json();

  let tooltipType;
  let result;
  if (
    event.target.className === "item-img" ||
    event.target.className === "table-img" ||
    event.target.className === "hero-img"
  ) {
    if (event.target.className == "hero-img") {
      result = stats["result"]["data"]["heroes"][0];
      tooltipType = "hero";
    } else if (
      event.target.className === "item-img" &&
      event.target.id !== "aghanims-shard" &&
      event.target.alt !== "ultimate_scepter"
    ) {
      result = items;
      tooltipType = "item";
    } else {
      tooltipHero =
        event.target.parentNode.parentNode.getAttribute("data-hero") ||
        event.target.getAttribute("data-hero");
      result = abilities[tooltipHero];
      tooltipType = "ability";
    }
    let tooltip, _id, imgSrc, aghanim_ability;
    for (let element of event.target.parentNode.children) {
      if (element.className === "tooltip") tooltip = element;
      _id = event.target.getAttribute("data_id");
      if (_id == "5631") _id = "5625";
      imgSrc = event.target.getAttribute("src");
    }
    if (tooltip.id === "shard-tooltip" || tooltip.id === "scepter-tooltip") {
      aghanim_ability = extract_aghanim(
        result,
        tooltip.id.replace("-tooltip", "")
      );
    }
    if (
      tooltipType == "ability" ||
      tooltip.id == "shard-tooltip" ||
      tooltip.id == "scepter-tooltip"
    ) {
      hero = event.target.getAttribute("data-hero");
      tooltip.style.background = `linear-gradient(137deg, rgba(35 35 35), rgb(60,60,60) )`;
      for (const i of hero_colors.colors) {
        if (imgSrc.includes("launch_fire_spirit")) {
          // phoenix edge case
          imgSrc = "phoenix_fire_spirits";
        }
        if (imgSrc.includes(i.ability)) {
          tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, #182127 160px)`;
          break;
        } else {
          if (tooltip.id === "shard-tooltip") {
            tooltipType = "aghanim-shard";
          } else if (tooltip.id === "scepter-tooltip") {
            tooltipType = "aghanim-scepter";
          }
          if (aghanim_ability && i.ability.includes(aghanim_ability["name"])) {
            tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, #182127 160px)`;
            break;
          }
        }
      }
    } else if (tooltipType == "item") {
      tooltip.style.background = `#182127`;
    }

    tooltip_method = new Tooltip(tooltip);
    tooltip.style.display = "block";
    if (tooltip.id === "talent-tooltip") {
      tooltip_method.generateLineOne(event.target, "talent");
      return;
    }
    if (tooltip.id === "hero-tooltip") {
      tooltip_method.generateLineOne(result, "hero");
      tooltip_method.generateHeroContent(result, tooltipType);
      const color = document.getElementById("hero-name").style.color;
      tooltip.style.background = `radial-gradient(circle at top left, ${color}, #182127 190px)`;
      return;
    }
    let base = aghanim_ability || result[_id];
    if (tooltip.id === "item-tooltip") {
      for (let i = 0; i < result["items"].length; i++) {
        if (result["items"][i]["id"] === +_id) {
          base = result["items"][i];
        }
      }
    }

    tooltip_method.generateLineOne(base, tooltipType);
    tooltip_method.generateContent(base, tooltipType);
    tooltip_method.generateFooter(base, tooltipType);

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
  }
});
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

class Tooltip {
  constructor(tooltip) {
    this.tooltip = tooltip;
  }
  generateLineOne(base, tooltipType) {
    let tooltipHeaderText, imgSrc;
    if (tooltipType == "talent") {
      tooltipHeaderText = event.target.alt;
    } else if (tooltipType == "item") {
      tooltipHeaderText = base["displayName"];
    } else {
      tooltipHeaderText = base["name_loc"];
    }
    if (!tooltipType.includes("aghanim")) {
      imgSrc = event.target.src;
    } else {
      const ability_base =
        "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/abilities/";
      imgSrc = `${ability_base}${base["name"]}.png`;
    }

    let tooltipTitle = document.createElement("div");
    tooltipTitle.setAttribute("class", "tooltip-title");
    this.tooltip.style.border = "3px solid black";
    let tooltipLineOne = document.createElement("div");
    tooltipLineOne.setAttribute("class", "tooltip-line-one");

    const tooltipHeaderImg = document.createElement("img");
    tooltipHeaderImg.setAttribute("class", "tooltip-img");
    tooltipHeaderImg.setAttribute("src", imgSrc);
    let headerText = document.createElement("h3");
    headerText.textContent = tooltipHeaderText;
    if (tooltipType === "hero") {
      const imgWrapper = document.createElement("div");
      imgWrapper.setAttribute("class", "hero-img-wrapper");
      const hpBar = this.statBar(base, "health");
      const manaBar = this.statBar(base, "mana");
      tooltipHeaderImg.setAttribute("class", "tooltip-hero-img");
      imgWrapper.appendChild(tooltipHeaderImg);
      imgWrapper.appendChild(hpBar);
      imgWrapper.appendChild(manaBar);
      tooltipTitle.appendChild(imgWrapper);
    } else {
      tooltipTitle.appendChild(tooltipHeaderImg);
    }
    tooltipTitle.appendChild(headerText);
    tooltipLineOne.appendChild(tooltipTitle);
    let aghanimText = "";
    if (tooltipType.includes("aghanim")) {
      if (tooltipType === "aghanim-shard") {
        aghanimText = "SHARD ABILITY UPGRADE";
      } else {
        aghanimText = "SCEPTER ABILITY UPGRADE";
      }
      let aghanimWrapper = document.createElement("div");
      aghanimWrapper.setAttribute("class", "aghanim-wrapper");
      let aghanimTitle = document.createElement("div");
      aghanimTitle.setAttribute("class", "aghanim-title");
      aghanimTitle.innerHTML = aghanimText;
      aghanimWrapper.appendChild(aghanimTitle);
      tooltipLineOne.appendChild(aghanimWrapper);
      tooltipLineOne.style.flexDirection = "column";
      tooltipLineOne.style.padding = "20px 20px 0px 20px";
    }
    if (this.tooltip.id === "item-tooltip") {
      tooltipLineOne.classList.add("item-tooltip-line-one");
      let costWrapper = document.createElement("div");
      costWrapper.setAttribute("class", "cost-wrapper");
      let costImg = document.createElement("img");
      costImg.setAttribute("class", "gold-img");
      costImg.setAttribute(
        "src",
        "https://steamcdn-a.akamaihd.net/apps/dota2/images/tooltips/gold.png"
      );
      let costText = document.createElement("h4");
      costText.setAttribute("class", "cost-text");
      costText.textContent = base["stat"]["cost"];
      costWrapper.appendChild(costImg);
      costWrapper.appendChild(costText);
      if (costText.textContent > 0) {
        tooltipLineOne.appendChild(costWrapper);
      }
    }
    if (!this.tooltip.children[0]) {
      this.tooltip.appendChild(tooltipLineOne);
    }
  }
  statBar(base, stat) {
    const statBar = document.createElement("div");
    statBar.setAttribute("class", `stat-bar`);
    statBar.setAttribute("id", `${stat}-bar`);
    const statMax = document.createElement("p");
    statMax.setAttribute("class", "max-stat");
    statMax.innerHTML = parseInt(base[`max_${stat}`]);
    const statRegen = document.createElement("p");
    statRegen.setAttribute("class", "stat-regen");
    statRegen.innerHTML = "+" + parseFloat(base[`${stat}_regen`]).toFixed(2);
    statBar.appendChild(statMax);
    statBar.appendChild(statRegen);
    return statBar;
  }

  heroAghanimSubImg(imgSrc, type) {
    let baseImg = document.createElement("div");
    baseImg.setAttribute("class", "tooltip-aghanim-img");
    baseImg.style.backgroundImage = `url(${imgSrc})`;
    let subImg = document.createElement("img");
    subImg.setAttribute("class", "scepter-subicon");
    const subImgUrl = `https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/stats/aghs_${type}.png`;
    subImg.style.cssText += `background-image:url(${subImgUrl})`;
    // const subImg = document.createElement("div");
    // subImg.setAttribute("class", "scepter-subicon");
    // subImg.setAttribute(
    //   "src",
    //   "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/stats/aghs_scepter.png"
    // );
    baseImg.appendChild(subImg);
    baseImg.style.position = "relative";
    return baseImg;
  }
  heroaghanim(base, type) {
    const aghanim = extract_aghanim(base["abilities"], type);
    const wrapper = document.createElement("div");
    wrapper.setAttribute("class", "hero-aghanim-wrapper");
    wrapper.setAttribute("id", `hero-${type}`);
    const imgSrc = `https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/abilities/${aghanim["name"]}.png`;
    const spellImg = this.heroAghanimSubImg(imgSrc, type);
    const spellDesc = document.createElement("p");
    spellDesc.style.fontSize = "13px";
    spellDesc.innerHTML = this.highlight_numbers(aghanim[`${type}_loc`]);
    if (aghanim[`${type}_loc`].length == 0) {
      spellDesc.innerHTML = this.extract_hidden_values(
        aghanim,
        aghanim["desc_loc"]
      );
    }
    wrapper.appendChild(spellImg);
    wrapper.appendChild(spellDesc);
    return wrapper;
  }
  baseStats(base, stat) {
    const statWrapper = document.createElement("div");
    statWrapper.setAttribute("class", "stat-wrapper");
    const statImg = document.createElement("img");
    statImg.setAttribute("class", "stat-img");
    statImg.setAttribute(
      "src",
      `https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react//heroes/stats/icon_${stat}.png`
    );
    const statText =
      stat === "damage"
        ? `${base["damage_min"]}-${base["damage_max"]}`
        : parseInt(base[stat]);
    const text = document.createElement("p");
    text.innerHTML = statText;
    statWrapper.appendChild(statImg);
    statWrapper.appendChild(text);
    return statWrapper;
  }
  generateHeroContent(base) {
    let tooltipContent = document.createElement("div");
    tooltipContent.setAttribute("class", "tooltip-content");
    const attributes = new TooltipAttributes().heroAttributes(base);
    let stats = document.createElement("div");
    stats.setAttribute("class", "stats");
    const aghanimWrapper = document.createElement("div");
    aghanimWrapper.setAttribute("class", "hero-aghanim-upgrades");
    const shard = this.heroaghanim(base, "shard");
    const scepter = this.heroaghanim(base, "scepter");
    aghanimWrapper.appendChild(shard);
    aghanimWrapper.appendChild(scepter);

    //stats
    const statAttrWrapper = document.createElement("div");
    statAttrWrapper.setAttribute("class", "stats-container");
    const statsWrapper = document.createElement("div");
    statsWrapper.setAttribute("class", "stats-wrapper");
    const damage = this.baseStats(base, "damage");
    const armor = this.baseStats(base, "armor");
    const movementSpeed = this.baseStats(base, "movement_speed");
    statsWrapper.appendChild(damage);
    statsWrapper.appendChild(armor);
    statsWrapper.appendChild(movementSpeed);

    statAttrWrapper.appendChild(attributes);
    statAttrWrapper.appendChild(statsWrapper);

    tooltipContent.appendChild(statAttrWrapper);
    tooltipContent.appendChild(aghanimWrapper);
    if (!this.tooltip.children[1]) {
      this.tooltip.appendChild(tooltipContent);
    }
  }

  generateContent(base, tooltipType) {
    let attributes, lore, aghanimDescriptionText;
    let description = document.createElement("div");
    description.setAttribute("class", "tooltip-description");
    const tooltipAttributes = new TooltipAttributes();
    if (tooltipType.includes("aghanim")) {
      if (tooltipType === "aghanim-shard") {
        aghanimDescriptionText = this.highlight_numbers(base["shard_loc"]);
      } else {
        aghanimDescriptionText = this.highlight_numbers(base["scepter_loc"]);
      }
      if (aghanimDescriptionText.length == 0) {
        aghanimDescriptionText = this.extract_hidden_values(
          base,
          base["desc_loc"]
        );
      }
      description.innerHTML = aghanimDescriptionText;
    }
    if (tooltipType === "item") {
      attributes = tooltipAttributes.attributeGen(base);
      description = new TooltipDescription().description(base);
    } else if (tooltipType === "ability") {
      description.innerHTML = this.extract_hidden_values(
        base,
        base["desc_loc"]
      );
      attributes = tooltipAttributes.attributeGen(base, null);
    }
    lore = this.genLore(base);
    this.appendToContent(tooltipType, description, attributes, lore);
  }
  genLore(base) {
    const lore = document.createElement("div");
    lore.setAttribute("class", "tooltip-lore");
    let loreText;
    if ("language" in base) {
      loreText =
        typeof base["language"]["lore"][0] === "string"
          ? base["language"]["lore"]
          : base["language"]["lore"][0] || null;
    } else {
      loreText = base["lore_loc"];
    }
    if (loreText) {
      let loreTextEl = document.createElement("p");
      loreTextEl.textContent = loreText;
      lore.appendChild(loreTextEl);
    }
    return lore;
  }
  appendToContent(tooltipType, description = [], attributes = [], lore = []) {
    let tooltipContent = document.createElement("div");
    tooltipContent.setAttribute("class", "tooltip-content");
    if (tooltipType.includes("aghanim")) {
      tooltipContent.appendChild(description);
    } else if (event.target.className === "table-img") {
      tooltipContent.appendChild(description);
      tooltipContent.appendChild(attributes);
      tooltipContent.appendChild(lore);
    } else {
      console.log(attributes);
      tooltipContent.appendChild(attributes);
      tooltipContent.appendChild(description);
      tooltipContent.appendChild(lore);
    }
    if (!this.tooltip.children[1]) {
      this.tooltip.appendChild(tooltipContent);
    }
  }
  generateFooter(base, tooltipType) {
    let tooltipFooter = document.createElement("div");
    tooltipFooter.setAttribute("class", "tooltip-footer");
    if (tooltipType === "item") {
      return;
    }
    if ("mana_costs" in base && base["mana_costs"].some((x) => x > 0)) {
      this.footerContent(tooltipFooter, base, "mana_costs", "mana");
    }
    if ("cooldowns" in base && base["cooldowns"].some((x) => x > 0)) {
      this.footerContent(tooltipFooter, base, "cooldowns", "cooldown");
    }
    if (tooltipFooter.children.length == 0) {
      tooltipFooter.style.padding = "0px";
      tooltipFooter.style.borderTop = "0px";
    }
    if (!this.tooltip.children[2]) {
      this.tooltip.appendChild(tooltipFooter);
    }
  }
  footerContent(tooltipFooter, base, classname, img) {
    const statWrapper = document.createElement("div");
    statWrapper.setAttribute(`class`, `${classname.replace("_", "-")}`);
    const statImg = document.createElement("img");
    statImg.setAttribute("class", "tooltip-footer-img");
    statImg.setAttribute(
      "src",
      `https://cdn.cloudflare.steamstatic.com/apps/dota2/images/tooltips/${img}.png`
    );
    const statText = document.createElement("p");
    statText.setAttribute("class", "footer-text");
    console.log(base);
    statText.textContent = base[classname].join("/");
    statWrapper.appendChild(statImg);
    statWrapper.appendChild(statText);
    if (event.target.className == "table-img") {
      tooltipFooter.appendChild(statWrapper);
    }
  }
  highlight_numbers(text) {
    if (typeof text == "object" && text != null) text = text.join("");
    return text
      ? text
          .replace(/<font(.*?)>/g, "")
          .replace(/font/g, "")
          .replace(
            /([^a-z>]\d*\.?\d+%?)(\s\/)?/gm,
            `<strong><span class='tooltip-text-highlight'>$1$2</span></strong>`
          )
          .replace(/<h1>/g, "<h3 class='tooltip-text-highlight'>")
          .replace(/<\/h1>/g, "</h3>")
      : "";
  }
  extract_hidden_values(base, text) {
    let sp = text.split("%");
    base["special_values"].forEach((x) => {
      if (sp.indexOf(x["name"]) > -1) {
        let float = x["values_float"].map(
            (el) => parseFloat(el).toFixed(2) * 1
          ),
          int = x["values_int"];
        if (x["is_percentage"]) {
          float = float.map((el) => (el += "%"));
          int = int.map((el) => (el += "%"));
        }
        sp[sp.indexOf(x["name"])] = `${float || ""}${int || ""}`;
      }
    });
    return this.highlight_numbers(sp.join(""));
  }
}

class TooltipAttributes extends Tooltip {
  attributeGen(base) {
    const attribute_obj = [];
    const attributes = document.createElement("div");
    attributes.setAttribute("class", "attributes");
    if (base["attrib"]) {
      base["attrib"].forEach((x) => {
        attribute_obj.push(`${x["header"]} ${x["value"]} ${x["footer"]}`);
      });
    } else {
      base["special_values"].forEach((x) => {
        let heading = x["heading_loc"],
          float = x["values_float"].map((el) => parseFloat(el).toFixed(2)),
          int = x["values_int"];
        if (heading.length > 0) {
          if (x["is_percentage"]) {
            float = float.map((el) => (el += "%"));
            int = int.map((el) => (el += "%"));
          }
          float = float.join("/");
          int = int.join("/");
          attribute_obj.push(heading + " " + float + int);
        }
      });
    }
    const attributesBody = attribute_obj
      .join("<br>")
      .replace(
        /([^h]\d*\.?\d+%?)(\s\/)?/gi,
        `<strong><span class='tooltip-text-highlight'>$1$2</span></strong>`
      );
    attributes.innerHTML = `<p>${attributesBody}</p>`;
    return attributes;
  }
  singleAttribute(base, attribute) {
    const shrtAttr = attribute.substring(0, 3);
    const attrWrapper = document.createElement("div");
    attrWrapper.setAttribute("class", `attribute-wrapper`);
    const attrImg = document.createElement("img");
    attrImg.setAttribute(
      "src",
      `https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/icons/hero_${attribute}.png`
    );
    attrImg.setAttribute("class", "attrImg");
    const baseAttr = document.createElement("p");
    baseAttr.setAttribute("class", "baseAttr");
    baseAttr.textContent = base[`${shrtAttr}_base`];
    const attrGain = document.createElement("p");
    attrGain.setAttribute("class", "attrGain");
    attrGain.textContent =
      "+" + parseFloat(base[`${shrtAttr}_gain`]).toFixed(2);
    attrWrapper.appendChild(attrImg);
    attrWrapper.appendChild(baseAttr);
    attrWrapper.appendChild(attrGain);
    return attrWrapper;
  }
  heroAttributes(base) {
    const attributes = document.createElement("div");
    attributes.setAttribute("class", "hero-attributes");
    const str = this.singleAttribute(base, "strength");
    const agi = this.singleAttribute(base, "agility");
    const int = this.singleAttribute(base, "intelligence");

    attributes.appendChild(str);
    attributes.appendChild(agi);
    attributes.appendChild(int);
    return attributes;
  }
}
class TooltipDescription extends Tooltip {
  description(base) {
    const description = document.createElement("div");
    description.setAttribute("class", "tooltip-description");
    const activeDiv = document.createElement("div");
    const passiveDiv = document.createElement("div");
    const useDiv = document.createElement("div");
    activeDiv.setAttribute("class", "active");
    passiveDiv.setAttribute("class", "passive");
    useDiv.setAttribute("class", "use");
    base["language"]["description"].forEach((x) => {
      let activeText = super.highlight_numbers(x.match(/.*<h1>Active:.*/g));
      let toggleText = super.highlight_numbers(x.match(/.*<h1>Toggle:.*/g));
      let passiveText = super.highlight_numbers(x.match(/.*<h1>Passive:.*/g));
      let useText = super.highlight_numbers(x.match(/.*<h1>Use:.*/g));
      if (activeText || toggleText) {
        const activeHeader = x.replace(/<h1>(.*)<\/h1>.*/g, "$1");
        const activeTxt = x.replace(/.*<\/h1>(.*)/g, "$1");
        const headWrapper = document.createElement("div");
        const head = document.createElement("h3");
        const desc = document.createElement("p");
        headWrapper.setAttribute("class", "test");
        head.textContent = activeHeader;
        desc.setAttribute("class", "description-text");
        desc.innerHTML = super.highlight_numbers(activeTxt);
        let statWrapper = document.createElement("div");
        statWrapper.setAttribute("class", "statWrapper");
        headWrapper.appendChild(head);
        const mc = this.statTextGen(
          base["stat"]["manaCost"],
          "mana",
          statWrapper
        );
        const cd = this.statTextGen(
          base["stat"]["cooldown"],
          "cooldown",
          statWrapper
        );

        headWrapper.appendChild(cd);
        headWrapper.appendChild(mc);
        activeDiv.appendChild(headWrapper);
        activeDiv.appendChild(desc);
      }
      if (passiveText) {
        const useWrapper = this.descText(passiveText, "passive");
        passiveDiv.appendChild(useWrapper);
      }
      if (useText) {
        const useWrapper = this.descText(useText, "use");
        useDiv.appendChild(useWrapper);
      }
      if (activeDiv.children.length > 0) description.appendChild(activeDiv);
      if (passiveDiv.children.length > 0) description.appendChild(passiveDiv);
      if (useDiv.children.length > 0) description.appendChild(useDiv);
    });
    return description;
  }
  descText(text, classText) {
    text = text.replace(/(\/h3>)(.*)/g, `$1<p class='description-text'>$2</p>`);
    const textWrapper = document.createElement("div");
    textWrapper.setAttribute("class", `${classText}-description`);
    textWrapper.innerHTML = text;
    return textWrapper;
  }
  statTextGen(txt, stat, statWrapper) {
    let img = document.createElement("img");
    img.setAttribute(
      "src",
      `https://cdn.cloudflare.steamstatic.com/apps/dota2/images/tooltips/${stat}.png`
    );
    let statText = document.createElement("p");
    if (txt) {
      statText.textContent = txt[0];
      statWrapper.appendChild(img);
      statWrapper.appendChild(statText);
    }
    return statWrapper;
  }
}
