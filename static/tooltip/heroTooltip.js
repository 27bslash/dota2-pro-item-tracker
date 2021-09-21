import Tooltip from "./tooltip.js";
import TooltipAttributes from "./attributes.js";
import extract_aghanim from "../tooltip.js";

class HeroTooltip extends Tooltip {
  heroLineOne() {
    const tooltipLineOne = document.createElement("div");
    tooltipLineOne.setAttribute("class", "tooltip-line-one");

    const tooltipHeaderText = super.gentooltipHeaderText();
    const headerText = document.createElement("h3");
    headerText.textContent = tooltipHeaderText;

    const tooltipTitle = document.createElement("div");
    tooltipTitle.setAttribute("class", "tooltip-title");

    const imgWrapper = document.createElement("div");
    imgWrapper.setAttribute("class", "hero-img-wrapper");
    const hpBar = this.statBar("health");
    const manaBar = this.statBar("mana");
    const imgSrc = super.getImgSrc();
    const tooltipHeaderImg = document.createElement("img");
    tooltipHeaderImg.setAttribute("class", "tooltip-img");
    tooltipHeaderImg.setAttribute("src", imgSrc);
    tooltipHeaderImg.setAttribute("class", "tooltip-hero-img");
    imgWrapper.appendChild(tooltipHeaderImg);
    imgWrapper.appendChild(hpBar);
    imgWrapper.appendChild(manaBar);

    tooltipTitle.appendChild(imgWrapper);
    tooltipTitle.appendChild(headerText);
    tooltipLineOne.appendChild(tooltipTitle);
    this.tooltip.style.border = "3px solid black";
    console.log(this.tooltip.style.border);
    if (!this.tooltip.children[0]) {
      this.tooltip.appendChild(tooltipLineOne);
    }
  }
  heroTooltipContent() {
    let tooltipContent = document.createElement("div");
    tooltipContent.setAttribute("class", "tooltip-content");
    const attributes = new TooltipAttributes(
      this.tooltip,
      this.tooltipType,
      this.base
    ).heroAttributes();
    let stats = document.createElement("div");
    stats.setAttribute("class", "stats");
    const aghanimWrapper = document.createElement("div");
    aghanimWrapper.setAttribute("class", "hero-aghanim-upgrades");
    const shard = this.heroaghanim("shard");
    const scepter = this.heroaghanim("scepter");
    aghanimWrapper.appendChild(shard);
    aghanimWrapper.appendChild(scepter);

    //stats
    const statAttrWrapper = document.createElement("div");
    statAttrWrapper.setAttribute("class", "stats-container");
    const statsWrapper = document.createElement("div");
    statsWrapper.setAttribute("class", "stats-wrapper");
    const damage = this.baseStats("damage");
    const armor = this.baseStats("armor");
    const movementSpeed = this.baseStats("movement_speed");
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

  statBar(stat) {
    const statBar = document.createElement("div");
    statBar.setAttribute("class", `stat-bar`);
    statBar.setAttribute("id", `${stat}-bar`);
    const statMax = document.createElement("p");
    statMax.setAttribute("class", "max-stat");
    statMax.innerHTML = parseInt(this.base[`max_${stat}`]);
    const statRegen = document.createElement("p");
    statRegen.setAttribute("class", "stat-regen");
    statRegen.innerHTML =
      "+" + parseFloat(this.base[`${stat}_regen`]).toFixed(2);
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
  heroaghanim(type) {
    const aghanim = extract_aghanim(this.base["abilities"], type);
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
  baseStats(stat) {
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
        ? `${this.base["damage_min"]}-${this.base["damage_max"]}`
        : parseInt(this.base[stat]);
    const text = document.createElement("p");
    text.innerHTML = statText;
    statWrapper.appendChild(statImg);
    statWrapper.appendChild(text);
    return statWrapper;
  }
  main() {
    this.heroLineOne();
    this.heroTooltipContent();
    this.tooltip.style.border = "3px solid black";
    this.tooltip.style.display = "block";
  }
}
export default HeroTooltip;
