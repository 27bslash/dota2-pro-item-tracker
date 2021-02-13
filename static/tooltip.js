const hero_name = window.location.href.split("/").pop();
let hero_colors;
let h_id;
if (hero_name.length > 0) {
  hero_colors = get_json("ability_colours");
  abilities = get_json("abilities");
  items = get_json("items");
}
// closeAllTooltips();
window.addEventListener("mouseover", (event) => {
  if (event.target.className === "item-img") {
    items.then((result) => {
      let parent, tooltip, item_id;
      if (event.target.parentNode.className == "circle") {
        parent = event.target.parentNode.parentNode;
        child = parent.children[0].children[0];
        tooltip = parent.children[1];
        item_id = parent.children[0].children[0].getAttribute("data_id");
        itemImage = parent.children[0].children[0].getAttribute("src");
      } else {
        parent = event.target.parentNode;
        child = parent.children[0];
        tooltip = parent.children[2];
        item_id = parent.children[0].getAttribute("data_id");
        itemImage = parent.children[0].src;
      }
      const base = result[item_id]["language"];
      itemText = base["displayName"];
      tooltip.style.background = `linear-gradient(137deg, rgba(15 15 15), rgb(30,30,30) )`;
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
      itemImg.setAttribute("src", itemImage);
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
      costText.textContent = result[item_id]["stat"]["cost"];
      costWrapper.appendChild(costImg);
      costWrapper.appendChild(costText);
      tooltipLineOne.appendChild(itemImg);
      tooltipLineOne.appendChild(headerText);
      tooltipHeader.appendChild(tooltipLineOne);
      if (result[item_id]["stat"]["cost"] > 0)
        tooltipHeader.appendChild(costWrapper);
      tooltipContent = document.createElement("div");
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
            /([^h]\d*\.?\d+%?)/gi,
            `<strong><span class='tooltip-text-highlight'>$1</span></strong>`
          );
        attributes.innerHTML = attributesBody;
        tooltipContent.appendChild(attributes);
      }
      if ("description" in base) {
        htmlString = base["description"].join(",");
        description = document.createElement("div");
        description.setAttribute("class", "tooltip-description");
        descText = document.createElement("p");
        newStr = "";
        descriptionBody = base["description"]
          .join("")
          .replace(
            /([^h]\d*\.?\d+%?)/gi,
            `<strong><span class='tooltip-text-highlight'>$1</span></strong>`
          )
          .replace(/<h1>/g, "<h3 class='tooltip-text-highlight'>");
        description.innerHTML = descriptionBody;
        tooltipContent.appendChild(description);
      }

      tooltipFooter = document.createElement("div");
      tooltipFooter.setAttribute("class", "tooltip-footer");
      stat = result[item_id]["stat"];
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
      if ("components" in result[item_id]) {
        componentArray = [];
        result[item_id]["components"].forEach((x) => {
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
    });
  }
  if (event.target.className === "table-img") {
    abilities.then((result) => {
      parent = event.target.parentNode;
      a_id = parent.children[1].getAttribute("data_id");
      hero = parent.children[1].getAttribute("data-hero");
      tooltip = parent.children[2];
      tooltip.style.background = `linear-gradient(137deg, rgba(35 35 35), rgb(60,60,60) )`;
      hero_colors.then((res) => {
        for (const i of res.colors) {
          if (parent.children[1].getAttribute("src").includes(i.ability)) {
            tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, rgba(19,18,18,1) 160px)`;
          }
        }
      });
      skillImage = parent.children[1].src;
      skillText = parent.children[1].alt;
      //tHeader
      if (a_id && "language" in result[a_id]) {
        const base = result[a_id]["language"];
        tooltipHeader = document.createElement("div");
        tooltipHeader.setAttribute("class", "tooltip-line-one");
        headerImg = document.createElement("img");
        headerImg.setAttribute("class", "tooltip-img");
        headerImg.setAttribute("src", skillImage);
        headerText = document.createElement("h3");
        headerText.textContent = skillText;
        tooltipHeader.appendChild(headerImg);
        tooltipHeader.appendChild(headerText);

        tooltipContent = document.createElement("div");
        tooltipContent.setAttribute("class", "tooltip-content");
        if ("description" in base) {
          description = document.createElement("div");
          description.setAttribute("class", "tooltip-description");
          descText = document.createElement("p");
          descText.textContent = base["description"].join(",");
          description.appendChild(descText);
          tooltipContent.appendChild(description);
        }
        if ("attributes" in base) {
          attributes = document.createElement("div");
          attributes.setAttribute("class", "attributes");
          base["attributes"].forEach((x) => {
            attrText = document.createElement("p");
            attrText.textContent = x;
            attributes.appendChild(attrText);
          });
          tooltipContent.appendChild(attributes);
        }
        if ("aghanmimDescription" in base) {
          aghanims = document.createElement("div");
          aghanims.setAttribute("class", "aghanimDescription");
          aghsText = document.createElement("p");
          base["aghanimsDescription"].forEach((x) => {
            aghsText.textContent = x;
          });
          aghanims.appendChild(aghsText);
          tooltipContent.appendChild(aghanims);
        }

        //footer

        tooltipFooter = document.createElement("div");
        tooltipFooter.setAttribute("class", "tooltip-footer");
        stat = result[a_id]["stat"];
        if (!"manaCost" in stat && !"cooldown" in stat) {
        }
        if ("manaCost" in stat) {
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
        if ("cooldown" in stat) {
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
        if (!tooltip.children[0]) {
          tooltip.appendChild(tooltipHeader);
          tooltip.appendChild(tooltipContent);
          tooltip.appendChild(tooltipFooter);
        }
        let tooltipHeight = tooltip.offsetHeight;
        let tooltipTop = tooltip.getBoundingClientRect().top;
        tooltip.style.top = `-${tooltipHeight / 2}px`;
        tooltip.style.left = "50px";
        if (tooltip.getBoundingClientRect().bottom > window.innerHeight) {
          imgHeight = parent.children[1].clientHeight;
          tooltip.style.top = `-${tooltipHeight - imgHeight + imgHeight / 2.5}px`;
          tooltip.style.left = `-0px`;
          console.log(tooltipHeight / 2 + tooltipTop, window.innerHeight);
        }
      }
    });
  }
});
