const hero_name = window.location.href.split("/").pop();
let hero_colors;
let h_id;
async function get_json_data() {
  if (hero_name.length > 0) {
    hero_colors = await get_json("ability_colours");
    abilities = await get_json("abilities");
    items = await get_json("items");
  }
}
// closeAllTooltips();
get_json_data();
window.addEventListener("mouseover", (event) => {
  if (
    event.target.className === "item-img" ||
    event.target.className === "table-img"
  ) {
    let result;
    if (event.target.className === "item-img") {
      result = items;
    } else {
      result = abilities;
    }

    let tooltip, _id, imgSrc;
    for (let element of event.target.parentNode.children) {
      if (element.className === "tooltip") tooltip = element;
      _id = event.target.getAttribute("data_id");
      imgSrc = event.target.getAttribute("src");
    }
    if (event.target.parentNode.className == "ability-img-wrapper") {
      hero = event.target.getAttribute("data-hero");
      tooltip.style.background = `linear-gradient(137deg, rgba(35 35 35), rgb(60,60,60) )`;
      for (const i of hero_colors.colors) {
        if (imgSrc.includes(i.ability)) {
          tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, #182127 160px)`;
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
    if (!(_id in result) || tooltip.id === "talent-tooltip") {
      tooltip_method.generateLineOne(event.target);
      return;
    }
    const base = result[_id]["language"];
    const headerTextContent = base["displayName"];
    tooltip_method.generateLineOne(base);
    tooltip_method.generateContent(base);
    tooltip_method.generateFooter(base);
    let tooltipHeight = tooltip.offsetHeight;
    if (tooltip.id != "talent-tooltip") {
      tooltip.style.top = `-${tooltipHeight / 2}px`;
      tooltip.style.left = `${event.target.clientWidth}px`;
      if (tooltip.getBoundingClientRect().bottom > window.innerHeight) {
        tooltip.style.top = `-${tooltipHeight}px`;
        tooltip.style.left = `-0px`;
      }
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

class Tooltip {
  constructor(tooltip, parentNode, result, id) {
    this.tooltip = tooltip;
    this.parent = parentNode;
    this.result = result;
    this.id = id;
  }
  generateLineOne(base) {
    const tooltipHeaderText = base["displayName"] || event.target.alt;
    const imgSrc = event.target.src;
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
  generateContent(base) {
    let _id = this.id,
      result = this.result;
    let tooltipContent = document.createElement("div");
    tooltipContent.setAttribute("class", "tooltip-content");
    let attributesBody, descriptionBody, attributes, description, lore;
    if ("attributes" in base) {
      attributes = document.createElement("div");
      attributes.setAttribute("class", "attributes");
      attributesBody = base["attributes"]
        .join("<br>")
        .replace(
          /([^h]\d*\.?\d+%?)(\s\/)?/gi,
          `<strong><span class='tooltip-text-highlight'>$1$2</span></strong>`
        );
      attributes.innerHTML = `<p>${attributesBody}</p>`;
      tooltipContent.appendChild(attributes);
    }
    if ("description" in base) {
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

      base["description"].forEach((x) => {
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

      descriptionBody = highlight_numbers(base["description"]);
      if (activeDiv.children.length > 0) description.appendChild(activeDiv);
      if (passiveDiv.children.length > 0) description.appendChild(passiveDiv);
      if (useDiv.children.length > 0) description.appendChild(useDiv);
      if (event.target.className === "table-img") {
        description.innerHTML = descriptionBody;
      }
      lore = document.createElement("div");
      lore.setAttribute("class", "tooltip-lore");
      if (base["lore"]) {
        let loreText =
          typeof base["lore"][0] === "string"
            ? base["lore"]
            : base["lore"][0] || null;
        if (loreText) {
          let loreTextEl = document.createElement("p");
          loreTextEl.textContent = loreText;
          lore.appendChild(loreTextEl);
        }
      }
      if (event.target.className === "table-img") {
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

  generateFooter(tooltipType) {
    let tooltipFooter = document.createElement("div");
    tooltipFooter.setAttribute("class", "tooltip-footer");
    let _id = this.id;
    let stat = this.result[_id]["stat"];
    if ("manaCost" in stat && stat["manaCost"].some((x) => x > 0)) {
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
      mcText.textContent = stat["manaCost"].join("/");
      mcWrapper.appendChild(manaCosts);
      mcWrapper.appendChild(mcText);
      if (event.target.className == "table-img") {
        tooltipFooter.appendChild(mcWrapper);
      }
    }
    if ("cooldown" in stat && stat["cooldown"].some((x) => x > 0)) {
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
      cdText.textContent = stat["cooldown"].join("/");
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
