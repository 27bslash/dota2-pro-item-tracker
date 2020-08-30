// <!-- <div class="tooltip"style='background: radial-gradient(circle at top left, rgba{{hero_colour}} 0%, rgba(19,18,18,1) 37%);'>
//                   <div class="tooltip-line-one"'>
//                     <img
//                     class='tooltip-img'
//                     src="https://cdn.cloudflare.steamstatic.com/apps/dota2/images/abilities/{{item.img}}_hp1.png?v=5933967"
//                     width ='40'
//                     height="40"
//                     title="{{item.key}}"
//                     onerror="this.onerror=null;this.src='../static/talent_img.png';"
//                     />
//                     <h3>{{item.key}}</h3>
//                   </div>
//                   <div class="tooltip-content">
//                     {%if item.description%}
//                     <div class="tooltip-description">
//                       <p>{{item.description|join(',')}}<p>
//                     </div>
//                     {%endif%}
//                     {%if item.attributes%}
//                     <div class="attributes">
//                     {%for attribute in item.attributes%}
//                     <div class="attribute">
//                       <p>{{attribute}}</p>
//                     </div>
//                     {%endfor%}
//                     </div>
//                     {%endif%}
//                     {%if item.aghanimDescription%}
//                     <div class="aghanimDescription" style='display:flex'>
//                       <img src='https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/ultimate_scepter_lg.png'
//                       width='26.5'
//                       height="20"
//                       />
//                       <p style='margin: 0'>{{item.aghanimDescription}}</p>
//                     </div>
//                     {%endif%}
//                     <div class="notes">
//                     {%for note in item.notes%}
//                       <p>{{note}}</p>
//                     {%endfor%}
//                     </div>
//                   </div>
//                   <div class="tooltip-footer">
//                     {%if item.manacost%}
//                     <div class="mana-costs">
//                       <img src='https://cdn.cloudflare.steamstatic.com/apps/dota2/images/tooltips/mana.png'
//                       height='13'
//                       width="13">
//                       <p class='footer-text'>{{item.manacost|join('/ ')}}</p>
//                     </div>
//                     {%endif%}
//                     {%if item.cooldown%}
//                     <div class="cooldowns">
//                       <img
//                       src='https://cdn.cloudflare.steamstatic.com/apps/dota2/images/tooltips/cooldown.png'
//                       height='13'
//                       width="13">
//                       <p class='footer-text'>{{item.cooldown|join('/ ')}}</p>
//                     </div>
//                     {%endif%}
//                   </div>
//                 </div>
//                 {%endif%}
//               </div> -->
//               <!-- {% endfor %} --></div>
async function stratz_abilities() {
  console.time();
  const url = `${window.location.origin}/files/abilities`;
  const res = await fetch(url);
  const data = await res.json();
  console.timeEnd();
  return data;
}
const hero_ids = get_hero_data();
const hero_name = window.location.href.split("/").pop();
let h_id;
// hero_ids.then((result) => {
//   console.log(result.heroes);
//   for (let hero of result.heroes) {
//     if (hero.name == hero_name) {
//       console.log(hero.id);
//       h_id = hero.id;
//       return h_id;
//     }
//   }
// });

const abilities = stratz_abilities();
window.addEventListener("mouseover", (event) => {
  if (event.target.className === "table-img") {
    abilities.then((result) => {
      parent = event.target.parentNode;
      a_id = parent.children[1].getAttribute("data_id");
      tooltip = parent.children[2];
      skillImage = parent.children[1].src;
      skillText = parent.children[1].alt;
      // div = document.createElement("div");
      // tooltip = div;
      // tooltip.setAttribute("class", "tooltip");
      //tHeader
      if ("language" in result[a_id]) {
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
