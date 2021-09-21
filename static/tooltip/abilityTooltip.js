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
  abilityTooltipContent() {
    let description = document.createElement("div");
    description.setAttribute("class", "tooltip-description");
    const tooltipAttributes = new TooltipAttributes(
      this.tooltip,
      this.tooltipType,
      this.base
    );
    description.innerHTML = this.extract_hidden_values(this.base["desc_loc"]);
    const attributes = tooltipAttributes.attributeGen();
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
    statText.textContent = this.base[classname].join("/");
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
