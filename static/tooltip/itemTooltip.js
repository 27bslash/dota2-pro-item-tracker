import Tooltip from "./tooltip.js";
import TooltipAttributes from "./attributes.js";
import TooltipDescription from "./description.js";
class ItemTooltip extends Tooltip {
  itemTooltipLineOne(tooltipLineOne) {
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
    costText.textContent = this.base["stat"]["cost"];
    costWrapper.appendChild(costImg);
    costWrapper.appendChild(costText);
    if (costText.textContent > 0) {
      tooltipLineOne.appendChild(costWrapper);
    }
    if (!this.tooltip.children[0]) {
      this.tooltip.appendChild(tooltipLineOne);
    }
  }
  itemTooltipContent() {
    const attributes = new TooltipAttributes(
      this.tooltip,
      this.tooltipType,
      this.base
    ).attributeGen();
    const description = new TooltipDescription(
      this.tooltip,
      this.tooltipType,
      this.base
    ).description();
    const lore = super.genLore();
    super.appendToContent(description, attributes, lore);
  }
  main() {
    const tooltipLineOne = super.generateLineOne();
    this.itemTooltipLineOne(tooltipLineOne);
    this.itemTooltipContent();
  }
}
export default ItemTooltip;
