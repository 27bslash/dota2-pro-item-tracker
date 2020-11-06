const hero_name = window.location.href.split("/").pop();
let hero_colors;
let h_id;
if (hero_name.length > 0) {
  hero_colors = get_json("colors");
  abilities = get_json("abilities");
}
closeAllTooltips()
window.addEventListener("mouseover", (event) => {
  if (event.target.className === "table-img") {
    abilities.then((result) => {
      parent = event.target.parentNode;
      a_id = parent.children[1].getAttribute("data_id");
      hero = parent.children[1].getAttribute("data-hero");
      tooltip = parent.children[2];
      hero_colors.then((res) => {
        for (const i of res.colors) {
          if (i.hero == hero) {
            tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, rgba(19,18,18,1) 37%)`;
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
          attrText = document.createElement("p");
          attrText.textContent = base["attributes"].join(",");
          attributes.appendChild(attrText);
          tooltipContent.appendChild(attributes);
        }
        if ("aghanmimDescription" in base) {
          aghanims = document.createElement("div");
          aghanims.setAttribute("class", "aghanimDescription");
          aghsText = document.createElement("p");
          aghsText.textContent = base["aghanimsDescription"].join(",");
          aghanims.appendChild(aghsText);
          tooltipContent.appendChild(aghanims);
        }
        if ("notes" in base) {
          notes = document.createElement("div");
          notes.setAttribute("class", "notes");
          noteText = document.createElement("p");
          noteText.textContent = base["notes"].join(",");
          notes.appendChild(noteText);
          tooltipContent.appendChild(notes);
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
      }
    });
  }
});
