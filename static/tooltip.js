let hero_colors;
const hero_name = window.location.href.split("/").pop();
let files_downloaded = false;
const file_set = new Set();
let files_len = 0;
let abilities = {};
async function get_json_data(hero_name) {
  // have to download files differently or just give up on shards for players
  if (hero_name) {
    abilities[hero_name] = await get_json("abilities", hero_name);
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

get_json_data();
window.addEventListener("mouseover", (event) => {
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

  let tooltipType;
  if (
    event.target.className === "item-img" ||
    event.target.className === "table-img"
  ) {
    let result;
    if (
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
    if (
      tooltipType == "ability" ||
      tooltip.id == "shard-tooltip" ||
      tooltip.id == "sceptre-tooltip"
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
        } else {
          for (let ability in result) {
            if (i.ability.includes(result[ability]["name"])) {
              if (tooltip.id === "shard-tooltip") {
                tooltipType = "aghanim-shard";
                aghanim_ability = extract_aghanim(result, "shard");
                if (aghanim_ability) {
                  tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, #182127 160px)`;
                }
              } else if (tooltip.id === "sceptre-tooltip") {
                tooltipType = "aghanim-sceptre";
                aghanim_ability = extract_aghanim(result, "scepter");
                if (aghanim_ability) {
                  tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, #182127 160px)`;
                }
              }
            }
          }
        }
      }
    } else if (tooltipType == "item") {
      tooltip.style.background = `#182127`;
    }

    tooltip_method = new Tooltip(
      tooltip,
      event.target.parentNode.className,
      result,
      _id
    );
    if (tooltip.id === "talent-tooltip") {
      tooltip_method.generateLineOne(event.target, "talent");
      return;
    }
    tooltip.style.display = "block";

    const base = aghanim_ability || result[_id];

    tooltip_method.generateLineOne(base, tooltipType);
    tooltip_method.generateContent(base, tooltipType);
    tooltip_method.generateFooter(base, tooltipType);

    let tooltipHeight = tooltip.offsetHeight;
    tooltip.style.top = `-${tooltipHeight / 2}px`;
    tooltip.style.left = `${event.target.clientWidth}px`;
    if (tooltip.getBoundingClientRect().bottom > window.innerHeight) {
      tooltip.style.top = `-${tooltipHeight}px`;
      tooltip.style.left = `-0px`;
    }
    tooltip.style.display = "block";
  }
});
function extract_aghanim(result, s) {
  for (let ability in result) {
    const shard =
      result[ability][`ability_is_granted_by_${s}`] ||
      result[ability][`ability_has_${s}`];
    if (shard) {
      return result[ability];
    }
  }
}
function highlight_numbers(text) {
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
function extract_hidden_values(base, text) {
  let sp = text.split("%");
  base["special_values"].forEach((x) => {
    if (sp.indexOf(x["name"]) > -1) {
      let float = x["values_float"].map((el) => parseFloat(el).toFixed(2) * 1),
        int = x["values_int"];
      if (x["is_percentage"]) {
        float = float.map((el) => (el += "%"));
        int = int.map((el) => (el += "%"));
      }
      sp[sp.indexOf(x["name"])] = `${float || ""}${int || ""}`;
    }
  });
  return highlight_numbers(sp.join(""));
}


class Tooltip {
  constructor(tooltip, parentNode, result, id) {
    this.tooltip = tooltip;
    this.parent = parentNode;
    this.result = result;
    this.id = id;
  }
  generateLineOne(base, tooltipType) {
    let tooltipHeaderText, imgSrc;
    if (tooltipType == "talent") {
      tooltipHeaderText = event.target.alt;
    } else if (tooltipType == "item") {
      tooltipHeaderText = base["language"]["displayName"];
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

    const _id = this.id;
    let tooltipTitle = document.createElement("div");
    tooltipTitle.setAttribute("class", "tooltip-title");
    this.tooltip.style.border = "3px solid black";
    let tooltipLineOne = document.createElement("div");
    tooltipLineOne.setAttribute("class", "tooltip-line-one");
    let tooltipHeaderImg;
    // if (tooltipType === "aghanim-shard") {
    //   let subImg = document.createElement("div");
    //   subImg.setAttribute("class", "scepter-subicon");
    //   subImg.setAttribute(
    //     "src",
    //     "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/stats/aghs_scepter.png"
    //   );
    //   tooltipHeaderImg.appendChild(subImg);
    //   tooltipHeaderImg.style.position = "relative";
    // } else if (tooltipType === "aghanim-sceptre") {
    //   tooltipHeaderImg = document.createElement("div");
    //   tooltipHeaderImg.setAttribute("class", "tooltip-aghanim-img");
    //   tooltipHeaderImg.style.backgroundImage = `url(${imgSrc})`;
    //   let subImg = document.createElement("img");
    //   subImg.setAttribute("class", "scepter-subicon");
    //   subImg.style.backgroundImage =
    //     'url("https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/stats/aghs_scepter.png")';
    //   tooltipHeaderImg.appendChild(subImg);

    tooltipHeaderImg = document.createElement("img");
    tooltipHeaderImg.setAttribute("class", "tooltip-img");
    tooltipHeaderImg.setAttribute("src", imgSrc);

    let headerText = document.createElement("h3");
    headerText.textContent = tooltipHeaderText;

    tooltipTitle.appendChild(tooltipHeaderImg);
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
      costText.textContent = this.result[_id]["stat"]["cost"];
      costWrapper.appendChild(costImg);
      costWrapper.appendChild(costText);
      tooltipLineOne.appendChild(costWrapper);
    }
    if (!this.tooltip.children[0]) {
      this.tooltip.appendChild(tooltipLineOne);
    }
  }
  generateContent(base, tooltipType) {
    let _id = this.id,
      result = this.result;
    let tooltipContent = document.createElement("div");
    tooltipContent.setAttribute("class", "tooltip-content");
    let attributesBody,
      attribute_obj = [],
      descriptionBody,
      attributes,
      description,
      lore,
      aghanimDescriptionText;
    if (tooltipType.includes("aghanim")) {
      if (tooltipType === "aghanim-shard") {
        aghanimDescriptionText = highlight_numbers(base["shard_loc"]);
      } else {
        aghanimDescriptionText = highlight_numbers(base["scepter_loc"]);
      }
      if (aghanimDescriptionText.length == 0) {
        aghanimDescriptionText = extract_hidden_values(base, base["desc_loc"]);
      }
      let aghanimDescription = document.createElement("div");
      aghanimDescription.setAttribute("class", "shard-description");
      aghanimDescription.innerHTML = aghanimDescriptionText;
      tooltipContent.appendChild(aghanimDescription);
    }
    if ("special_values" in base || "attributes" in base["language"]) {
      attributes = document.createElement("div");
      attributes.setAttribute("class", "attributes");
      if ("language" in base) {
        attribute_obj = base["language"]["attributes"];
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
      attributesBody = attribute_obj
        .join("<br>")
        .replace(
          /([^h]\d*\.?\d+%?)(\s\/)?/gi,
          `<strong><span class='tooltip-text-highlight'>$1$2</span></strong>`
        );
      attributes.innerHTML = `<p>${attributesBody}</p>`;
    }
    if ("desc_loc" in base || "description" in base["language"]) {
      //   htmlString = base["description"].join(",");
      description = document.createElement("div");
      description.setAttribute("class", "tooltip-description");
      let activeText = "",
        passiveText = "",
        useText = "";

      let activeDiv = document.createElement("div");
      let passiveDiv = document.createElement("div");
      let useDiv = document.createElement("div");
      let activeWrapper = document.createElement("div");
      let passiveWrapper = document.createElement("div");
      let useWrapper = document.createElement("div");

      activeDiv.setAttribute("class", "active");
      passiveDiv.setAttribute("class", "passive");
      useDiv.setAttribute("class", "use");
      if ("language" in base && "description" in base["language"]) {
        base["language"]["description"].forEach((x) => {
          let activeText = highlight_numbers(x.match(/.*<h1>Active:.*/g));
          let toggleText = highlight_numbers(x.match(/.*<h1>Toggle:.*/g));
          let passiveText = highlight_numbers(x.match(/.*<h1>Passive:.*/g));
          let useText = highlight_numbers(x.match(/.*<h1>Use:.*/g));
          if (activeText || toggleText) {
            const activeHeader = x.replace(/<h1>(.*)<\/h1>.*/g, "$1");
            const activeTxt = x.replace(/.*<\/h1>(.*)/g, "$1");
            let headWrapper = document.createElement("div");
            let head = document.createElement("h3");
            let desc = document.createElement("p");
            let statWrapper = document.createElement("div");
            headWrapper.setAttribute("class", "test");
            head.textContent = activeHeader;
            desc.setAttribute("class", "description-text");
            desc.innerHTML = highlight_numbers(activeTxt);
            statWrapper.setAttribute("class", "statWrapper");

            let mc = document.createElement("img");
            mc.setAttribute(
              "src",
              "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/tooltips/mana.png"
            );
            headWrapper.appendChild(head);

            let mcText = document.createElement("p");
            let manaCost = this.result[_id]["stat"]["manaCost"] || false;
            if (manaCost) {
              mcText.textContent = manaCost[0];
              statWrapper.appendChild(mc);
              statWrapper.appendChild(mcText);
            }

            let cd = document.createElement("img");
            cd.setAttribute(
              "src",
              "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/tooltips/cooldown.png"
            );
            let cdText = document.createElement("p");
            let cooldown = result[_id]["stat"]["cooldown"] || false;

            if (cooldown) {
              cdText.textContent = cooldown[0];
              statWrapper.appendChild(cd);
              statWrapper.appendChild(cdText);
            }
            headWrapper.appendChild(statWrapper);
            activeDiv.appendChild(headWrapper);
            activeDiv.appendChild(desc);
          }
          if (passiveText) {
            passiveText = passiveText.replace(
              /(\/h3>)(.*)/g,
              `$1<p class='description-text'>$2</p>`
            );
            passiveWrapper = document.createElement("div");
            passiveWrapper.setAttribute("class", "passive-description");
            passiveWrapper.innerHTML = passiveText;
            passiveDiv.appendChild(passiveWrapper);
          }
          if (useText) {
            useText = useText.replace(
              /(\/h3>)(.*)/g,
              `$1<p class='description-text'>$2</p>`
            );
            useWrapper = document.createElement("div");
            useWrapper.setAttribute("class", "use-description");
            useWrapper.innerHTML = useText;
            useDiv.appendChild(useWrapper);
          }
        });
      }
      if (activeDiv.children.length > 0) description.appendChild(activeDiv);
      if (passiveDiv.children.length > 0) description.appendChild(passiveDiv);
      if (useDiv.children.length > 0) description.appendChild(useDiv);
      if (event.target.className === "table-img") {
        description.innerHTML = extract_hidden_values(base, base["desc_loc"]);
      }
      lore = document.createElement("div");
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
      if (tooltipType.includes("aghanim")) {
      } else if (event.target.className === "table-img") {
        tooltipContent.appendChild(description);
        tooltipContent.appendChild(attributes);
        tooltipContent.appendChild(lore);
      } else {
        tooltipContent.appendChild(attributes);
        tooltipContent.appendChild(description);
        tooltipContent.appendChild(lore);
      }
      if (!this.tooltip.children[1]) {
        this.tooltip.appendChild(tooltipContent);
      }
    }
  }

  generateFooter(base) {
    let tooltipFooter = document.createElement("div");
    tooltipFooter.setAttribute("class", "tooltip-footer");
    let _id = this.id;
    let stat = base["stat"];
    if (
      ("mana_costs" in base && base["mana_costs"].some((x) => x > 0)) ||
      ("stat" in base &&
        "manaCost" in base["stat"] &&
        base["stat"]["manaCost"].some((x) => x > 0))
    ) {
      let mcWrapper = document.createElement("div");
      mcWrapper.setAttribute("class", "mana-costs");
      let manaCosts = document.createElement("img");
      manaCosts.setAttribute("class", "tooltip-footer-img");
      manaCosts.setAttribute(
        "src",
        "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/tooltips/mana.png"
      );
      let mcText = document.createElement("p");
      mcText.setAttribute("class", "footer-text");
      if ("stat" in base) {
        mcText.textContent = stat["manaCost"].join("/");
      } else {
        mcText.textContent = base["mana_costs"].join("/");
      }
      mcWrapper.appendChild(manaCosts);
      mcWrapper.appendChild(mcText);
      if (event.target.className == "table-img") {
        tooltipFooter.appendChild(mcWrapper);
      }
    }
    if (
      ("cooldowns" in base && base["cooldowns"].some((x) => x > 0)) ||
      ("stat" in base &&
        "cooldown" in base["stat"] &&
        base["stat"]["cooldown"].some((x) => x > 0))
    ) {
      let cdWrapper = document.createElement("div");
      cdWrapper.setAttribute("class", "cooldowns");
      let cooldowns = document.createElement("img");
      cooldowns.setAttribute("class", "tooltip-footer-img");
      cooldowns.setAttribute(
        "src",
        "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/tooltips/cooldown.png"
      );
      let cdText = document.createElement("p");
      cdText.setAttribute("class", "footer-text");
      if ("stat" in base) {
        cdText.textContent = stat["cooldown"].join("/");
      } else {
        cdText.textContent = base["cooldowns"].join("/");
      }
      cdWrapper.appendChild(cooldowns);
      cdWrapper.appendChild(cdText);
      if (event.target.className == "table-img") {
        tooltipFooter.appendChild(cdWrapper);
      }
    }
    if (tooltipFooter.children.length == 0) {
      tooltipFooter.style.padding = "0px";
      tooltipFooter.style.borderTop = "0px";
    }
    if (!this.tooltip.children[2]) {
      this.tooltip.appendChild(tooltipFooter);
    }
  }
}
