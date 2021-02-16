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
    let parent, tooltip, _id, imgSrc;
    if (event.target.parentNode.className == "circle") {
      parent = event.target.parentNode.parentNode;
      child = parent.children[0].children[0];
      tooltip = parent.children[1];
      _id = parent.children[0].children[0].getAttribute("data_id");
      imgSrc = parent.children[0].children[0].getAttribute("src");
      tooltip.style.background = `linear-gradient(137deg, rgba(15 15 15), rgb(30,30,30) )`;
    } else if (event.target.parentNode.className == "ability-img-wrapper") {
      parent = event.target.parentNode;
      _id = parent.children[1].getAttribute("data_id");
      hero = parent.children[1].getAttribute("data-hero");
      imgSrc = parent.children[1].getAttribute("src");
      tooltip = parent.children[2];
      tooltip.style.background = `linear-gradient(137deg, rgba(35 35 35), rgb(60,60,60) )`;
      for (const i of hero_colors.colors) {
        if (parent.children[1].getAttribute("src").includes(i.ability)) {
          tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, rgba(19,18,18,1) 160px)`;
        }
      }
    } else {
      parent = event.target.parentNode;
      child = parent.children[0];
      tooltip = parent.children[2];
      _id = parent.children[0].getAttribute("data_id");
      imgSrc = parent.children[0].src;
      tooltip.style.background = `linear-gradient(137deg, rgba(15 15 15), rgb(30,30,30) )`;
    }
    const base = result[_id]["language"];
    itemText = base["displayName"];
    tooltip.style.display = "block";
    tooltipLineOne = document.createElement("div");
    tooltipLineOne.setAttribute("class", "tooltip-title");
    tooltipHeader = document.createElement("div");
    tooltipHeader.setAttribute(
      "class",
      "item-tooltip-line-one tooltip-line-one"
    );
    itemImg = document.createElement("img");
    itemImg.setAttribute("class", "tooltip-img");
    itemImg.setAttribute("src", imgSrc);
    headerText = document.createElement("h3");
    headerText.textContent = itemText;

    costWrapper = document.createElement("div");
    costWrapper.setAttribute("class", "cost-wrapper");
    costImg = document.createElement("img");
    costImg.setAttribute("class", "gold-img");
    costImg.setAttribute(
      "src",
      "https://steamcdn-a.akamaihd.net/apps/dota2/images/tooltips/gold.png"
    );
    costText = document.createElement("h4");
    costText.setAttribute("class", "cost-text");
    costText.textContent = result[_id]["stat"]["cost"];
    costWrapper.appendChild(costImg);
    costWrapper.appendChild(costText);

    tooltipLineOne.appendChild(itemImg);
    tooltipLineOne.appendChild(headerText);
    tooltipHeader.appendChild(tooltipLineOne);
    if (result[_id]["stat"]["cost"] > 0) tooltipHeader.appendChild(costWrapper);

    tooltipContent = document.createElement("div");
    tooltipContent.setAttribute("class", "tooltip-content");
    let attributesBody, descriptionBody;
    if (parent == "item-cell")
      tooltipContent.setAttribute(
        "class",
        "item-tooltip-content tooltip-content"
      );
    if ("attributes" in base) {
      attributes = document.createElement("div");
      attributes.setAttribute("class", "attributes");
      htmlString = "";
      attributesBody = base["attributes"]
        .join("<br>")
        .replace(
          /([^h]\d*\.?\d+%?)(\s\/)?/gi,
          `<strong><span class='tooltip-text-highlight'>$1$2</span></strong>`
        );
      attributes.innerHTML = attributesBody;
    }
    if ("description" in base) {
      htmlString = base["description"].join(",");
      description = document.createElement("div");
      description.setAttribute("class", "tooltip-description");
      descriptionBody = base["description"]
        .join("")
        .replace(
          /([^h]\d*\.?\d+%?)(\s\/)?/gi,
          `<strong><span class='tooltip-text-highlight'>$1$2</span></strong>`
        )
        .replace(/<h1>/g, "<h3 class='tooltip-text-highlight'>");
      description.innerHTML = descriptionBody;
      tooltipContent.appendChild(description);
    }

    if (event.target.className == "table-img") {
      // tooltipContent.reverse();
      tooltipContent.appendChild(description);
      tooltipContent.appendChild(attributes);
    } else {
      tooltipContent.appendChild(attributes);
      tooltipContent.appendChild(description);
    }

    tooltipFooter = document.createElement("div");
    tooltipFooter.setAttribute("class", "tooltip-footer");
    stat = result[_id]["stat"];
    if ("manaCost" in stat && stat["manaCost"] > 0) {
      mcWrapper = document.createElement("div");
      mcWrapper.setAttribute("class", "mana-costs");
      manaCosts = document.createElement("img");
      manaCosts.setAttribute("class", "tooltip-footer-img");
      manaCosts.setAttribute(
        "src",
        "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/tooltips/mana.png"
      );
      mcText = document.createElement("p");
      mcText.setAttribute("class", "footer-text");
      mcText.textContent = stat["manaCost"].join("/");
      mcWrapper.appendChild(manaCosts);
      mcWrapper.appendChild(mcText);
      tooltipFooter.appendChild(mcWrapper);
    }
    if ("cooldown" in stat && stat["cooldown"] > 0) {
      cdWrapper = document.createElement("div");
      cdWrapper.setAttribute("class", "cooldowns");
      cooldowns = document.createElement("img");
      cooldowns.setAttribute("class", "tooltip-footer-img");
      cooldowns.setAttribute(
        "src",
        "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/tooltips/cooldown.png"
      );
      cdText = document.createElement("p");
      cdText.setAttribute("class", "footer-text");
      cdText.textContent = stat["cooldown"].join("/");
      cdWrapper.appendChild(cooldowns);
      cdWrapper.appendChild(cdText);
      tooltipFooter.appendChild(cdWrapper);
    }
    if (tooltipFooter.children.length == 0) {
      tooltipFooter.style.padding = "0px";
      tooltipFooter.style.borderTop = "0px";
    }
    components = document.createElement("div");
    components.setAttribute("class", "tooltip-components");
    if ("components" in result[_id]) {
      componentArray = [];
      result[_id]["components"].forEach((x) => {
        componentId = x["componentId"];
        componentObj = result[componentId];
        componentImg = document.createElement("img");
        componentImg.setAttribute("class", "component-img");
        componentImg.setAttribute(
          "src",
          `https://ailhumfakp.cloudimg.io/v7/https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/${componentObj["shortName"]}_lg.png`
        );
        components.appendChild(componentImg);
      });
    }
    if (!tooltip.children[0]) {
      tooltip.appendChild(tooltipHeader);
      tooltip.appendChild(tooltipContent);
      tooltip.appendChild(tooltipFooter);
      // tooltip.appendChild(components);
    }
    let tooltipHeight = tooltip.offsetHeight;
    let tooltipTop = tooltip.getBoundingClientRect().top;
    console.log(tooltipHeight);
    tooltip.style.top = `-${tooltipHeight / 2}px`;
    tooltip.style.left = "50px";
    if (tooltip.getBoundingClientRect().bottom > window.innerHeight) {
      tooltip.style.top = `-${tooltipHeight}px`;
      tooltip.style.left = `-0px`;
      console.log(tooltipHeight / 2 + tooltipTop, window.innerHeight);
    }
  }
});
