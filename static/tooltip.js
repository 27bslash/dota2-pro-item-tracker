async function stratz_abilities() {
  console.time();
  const url = `${window.location.origin}/files/abilities`;
  const res = await fetch(url);
  const data = await res.json();
  console.timeEnd();
  return data;
}
async function hero_color() {
  console.time();
  const url = `${window.location.origin}/files/colors`;
  const res = await fetch(url);
  const data = await res.json();
  console.timeEnd();
  return data;
}
const hero_ids = get_hero_data();
const hero_name = window.location.href.split("/").pop();
let h_id;

const abilities = stratz_abilities();
const hero_colors = hero_color();
window.addEventListener("mouseover", (event) => {
  if (event.target.className === "table-img") {
    abilities.then((result) => {
      parent = event.target.parentNode;
      a_id = parent.children[1].getAttribute("data_id");
      hero = parent.children[1].getAttribute("data-hero");
      tooltip = parent.children[2];
      hero_colors.then((res) => {
        for (let i of res.colors) {
          if (i.hero == hero) {
            tooltip.style.background = `radial-gradient(circle at top left, rgba(${i.color[0]}, ${i.color[1]}, ${i.color[2]}) 0%, rgba(19,18,18,1) 37%)`;
          }
        }
      });
      skillImage = parent.children[1].src;
      skillText = parent.children[1].alt;
      // div = document.createElement("div");
      // tooltip = div;
      // tooltip.setAttribute("class", "tooltip");

      //tHeader
      if (a_id && "language" in result[a_id]) {
        let base = result[a_id]["language"];
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
        if (!tooltip.children[0]) {
          tooltip.appendChild(tooltipHeader);
          tooltip.appendChild(tooltipContent);
          tooltip.appendChild(tooltipFooter);
        }
      }
    });
  }
});
