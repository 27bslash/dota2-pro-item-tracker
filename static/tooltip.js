let hero_colors;
let h_id;
const hero_name = window.location.href.split("/").pop();

async function get_json_data() {
  // have to download files differently or just give up on shards for players
  if (hero_name.length > 0) {
    hero_colors = await get_json("ability_colours");
    abilities = await get_json("abilities", hero_name);
    items = await get_json("items");
  }
}
get_json_data();
window.addEventListener("mouseover", (event) => {
  let tooltipType;
  if (
    event.target.className === "item-img" ||
    event.target.className === "table-img"
  ) {
    let result;
    if (
      event.target.className === "item-img" &&
      event.target.id !== "aghanims-shard"
    ) {
      result = items;
      tooltipType = "item";
    } else {
      result = abilities;
      tooltipType = "ability";
    }
    let tooltip, _id, imgSrc;
    for (let element of event.target.parentNode.children) {
      if (element.className === "tooltip") tooltip = element;
      _id = event.target.getAttribute("data_id");
      imgSrc = event.target.getAttribute("src");
    }
    if (
      event.target.parentNode.className == "ability-img-wrapper" ||
      tooltip.id === "shard-tooltip"
    ) {
      hero = event.target.getAttribute("data-hero");
      tooltip.style.background = `linear-gradient(137deg, rgba(35 35 35), rgb(60,60,60) )`;
      for (const i of hero_colors.colors) {
        if (imgSrc.includes(i.ability)) {
          tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, #182127 160px)`;
        } else if (tooltip.id === "shard-tooltip") {
          for (let ability in result) {
            if (i.ability.includes(result[ability]["name"])) {
              const hasShard = result[ability]["ability_has_shard"] || result[ability]['ability_is_granted_by_shard']
              if (hasShard) {
                tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, #182127 160px)`;
              }
            }
          }
        }
      }
    } else {
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
    let shard_ability;
    if (tooltip.id === "shard-tooltip") {
      tooltipType = "shard";
      for (let ability in result) {
        const newSpell = result[ability]["ability_is_granted_by_shard"];
        if (newSpell) {
          shard_ability = result[ability];
        }
      }
      if (!shard_ability) {
        for (let ability in result) {
          const hasShard = result[ability]["ability_has_shard"];
          if (hasShard) {
            shard_ability = result[ability];
          }
        }
      }

      tooltip.style.display = "block";
    }
    const base = shard_ability || result[_id];

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

function highlight_numbers(text) {
  if (typeof text == "object" && text != null) text = text.join("");
  return text
    ? text
        .replace(
          /([^a-z>]\d*\.?\d+%?)(\s\/)?/gm,
          `<strong><span class='tooltip-text-highlight'>$1$2</span></strong>`
        )
        .replace(/<h1>/g, "<h3 class='tooltip-text-highlight'>")
        .replace(/<\/h1>/g, "</h3>")
    : "";
}
function extract_shards() {
  return;
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
    if (tooltipType !== "shard") {
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

    let tooltipHeaderImg = document.createElement("img");
    tooltipHeaderImg.setAttribute("class", "tooltip-img");
    tooltipHeaderImg.setAttribute("src", imgSrc);

    let headerText = document.createElement("h3");
    headerText.textContent = tooltipHeaderText;

    tooltipTitle.appendChild(tooltipHeaderImg);
    tooltipTitle.appendChild(headerText);
    tooltipLineOne.appendChild(tooltipTitle);
    if (tooltipType === "shard") {
      let shardWrapper = document.createElement("div");
      shardWrapper.setAttribute("class", "shard-wrapper");
      let shardTitle = document.createElement("div");
      shardTitle.innerHTML = "SHARD ABILITY UPGRADE";
      shardTitle.setAttribute("class", "shard-title");
      shardWrapper.appendChild(shardTitle);
      tooltipLineOne.appendChild(shardWrapper);
      tooltipLineOne.style.flexDirection = "column";
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
      lore;
    if (tooltipType == "shard") {
      let shardDescriptionText = highlight_numbers(base["shard_loc"]);
      if (shardDescriptionText.length == 0) {
        shardDescriptionText = base["desc_loc"];
        let sp = shardDescriptionText.split("%");
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
            // console.log(x["values_float"][0]);
          }
          shardDescriptionText = highlight_numbers(sp.join(""));
        });
        // console.log("sp,", sp);
      }
      let shardDescription = document.createElement("div");
      shardDescription.setAttribute("class", "shard-description");
      shardDescription.innerHTML = shardDescriptionText;
      tooltipContent.appendChild(shardDescription);
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
              mcText.textContent = manaCost;
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
              cdText.textContent = cooldown;
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
      descriptionBody = highlight_numbers(base["desc_loc"]);
      if (activeDiv.children.length > 0) description.appendChild(activeDiv);
      if (passiveDiv.children.length > 0) description.appendChild(passiveDiv);
      if (useDiv.children.length > 0) description.appendChild(useDiv);
      if (event.target.className === "table-img") {
        description.innerHTML = descriptionBody;
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
      if (tooltipType === "shard") {
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
  append_tooltip(header, content, Footer) {
    if (!this.tooltip.children[0]) {
      this.tooltip.appendChild(tooltipHeader);
      this.tooltip.appendChild(tooltipContent);
      this.tooltip.appendChild(tooltipFooter);
    }
  }
}
