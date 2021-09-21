import Tooltip from "./tooltip.js";


class AghanimTooltip extends Tooltip {
  aghanimTooltipLineOne(tooltipLineOne) {
    let aghanimText = "";
    if (this.tooltipType === "shard") {
      aghanimText = "SHARD ABILITY UPGRADE";
    } else {
      aghanimText = "SCEPTER ABILITY UPGRADE";
    }
    let aghanimWrapper = document.createElement("div");
    aghanimWrapper.setAttribute("class", "aghanim-wrapper");
    let aghanimTitle = document.createElement("div");
    aghanimTitle.setAttribute("class", "aghanim-title");
    aghanimTitle.innerHTML = aghanimText;
    aghanimWrapper.appendChild(aghanimTitle);
    tooltipLineOne.appendChild(aghanimWrapper);
    tooltipLineOne.style.flexDirection = "column";
    tooltipLineOne.style.padding = "20px 20px 0px 20px";
    if (!this.tooltip.children[0]) {
      this.tooltip.appendChild(tooltipLineOne);
    }
  }
  aghanimTooltipContent() {
    let description = document.createElement("div");
    description.setAttribute("class", "tooltip-description");
    let aghanimDescriptionText = "";
    if (this.tooltipType === "shard") {
      aghanimDescriptionText = super.highlight_numbers(this.base["shard_loc"]);
    } else {
      aghanimDescriptionText = super.highlight_numbers(
        this.base["scepter_loc"]
      );
    }
    if (aghanimDescriptionText.length == 0) {
      aghanimDescriptionText = super.extract_hidden_values(
        this.base["desc_loc"]
      );
    }
    description.innerHTML = aghanimDescriptionText;
    super.appendToContent(description);
  }
  main() {
    const tooltipLineOne = super.generateLineOne();
    this.aghanimTooltipLineOne(tooltipLineOne);
    this.aghanimTooltipContent();
  }
}
export default AghanimTooltip;
