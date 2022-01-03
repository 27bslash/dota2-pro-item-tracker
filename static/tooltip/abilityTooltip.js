import Tooltip from "./tooltip.js";
import TooltipAttributes from "./attributes.js";
import TooltipDescription from "./description.js";

class AbilityTooltip extends Tooltip {
  abilityTooltipLineOne() {
    const tooltipLineOne = super.generateLineOne();
    if (!this.tooltip.children[0]) {
      this.tooltip.appendChild(tooltipLineOne);
    }
  }
  damageType() {
    const text = document.createElement("p");
    const dmgType = this.convertDamageType();
    text.innerHTML = "DAMAGE TYPE: " + dmgType;
    return text;
  }
  convertDamageType() {
    let dmgType = this.base["damage"];
    switch (dmgType) {
      case 1:
        dmgType = '<span style="color: red">PHYSICAL</span>';
        break;
      case 2:
        dmgType = '<span style="color: #a3dcee">MAGICAL</span>';
        break;
      case 3:
        dmgType = '<span style="color: #a3dcee">MAGICAL</span>';
        break;
      case 4:
        dmgType = '<span style="color: orange">PURE</span>';
        break;
      default:
        break;
    }
    return dmgType;
  }
  //   3 not dispellable
  //   2 is dispellable
  //   1 strong dispellable

  spellImmunity() {
    const text = document.createElement("p");
    const immunity = this.base["immunity"];
    const pierce = immunity === 3 ? "YES" : "NO";
    text.innerHTML =
      "PIERCES SPELL IMMUNITY: " +
      `<strong><span style='color: white'>${pierce}</span></strong>`;
    return text;
  }
  dispellable() {
    const text = document.createElement("p");
    let dispellable = this.base["dispellable"];
    if (dispellable === 3) {
      dispellable = "NO";
    } else if (dispellable === 2) {
      dispellable = "YES";
    } else if (dispellable === 1) {
      dispellable = "STRONG DISPELL ONLY";
    }
    text.innerHTML =
      "DISPELLABLE: " +
      `<strong><span style='color: white'>${dispellable}</span></strong>`;
    return text;
  }
  abilityTooltipContent() {
    let description = document.createElement("div");
    description.setAttribute("class", "tooltip-description");
    const dmgType = this.damageType();
    const tooltipAttributes = new TooltipAttributes(
      this.tooltip,
      this.tooltipType,
      this.base
    );
    description.innerHTML = this.extract_hidden_values(this.base["desc_loc"]);
    const attributes = tooltipAttributes.attributeGen();
    if (!dmgType.innerHTML.includes(0)) {
      attributes.appendChild(dmgType);
      attributes.appendChild(this.spellImmunity());
      attributes.appendChild(this.dispellable());
    }
    const lore = super.genLore();
    super.appendToContent(description, attributes, lore);
  }
  generateFooter() {
    let tooltipFooter = document.createElement("div");
    tooltipFooter.setAttribute("class", "tooltip-footer");
    if (this.tooltipType === "item") {
      return;
    }
    if (
      "mana_costs" in this.base &&
      this.base["mana_costs"].some((x) => x > 0)
    ) {
      this.footerStatContent(tooltipFooter, "mana_costs", "mana");
    }
    if ("cooldowns" in this.base && this.base["cooldowns"].some((x) => x > 0)) {
      this.footerStatContent(tooltipFooter, "cooldowns", "cooldown");
    }
    if (tooltipFooter.children.length == 0) {
      tooltipFooter.style.padding = "0px";
      tooltipFooter.style.borderTop = "0px";
    }
    if (!this.tooltip.children[2]) {
      this.tooltip.appendChild(tooltipFooter);
    }
  }
  footerStatContent(tooltipFooter, classname, img) {
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
    statText.textContent = this.base[classname]
      .map((x) => parseFloat(x).toFixed(1) * 1)
      .join("/");
    statWrapper.appendChild(statImg);
    statWrapper.appendChild(statText);
    tooltipFooter.appendChild(statWrapper);
  }
  main() {
    this.abilityTooltipLineOne();
    this.abilityTooltipContent();
    this.generateFooter();
  }
}
export default AbilityTooltip;
