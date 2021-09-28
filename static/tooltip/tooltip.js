class Tooltip {
  constructor(tooltip, tooltipType, base) {
    this.tooltip = tooltip;
    this.tooltipType = tooltipType;
    this.base = base;
  }
  gentooltipHeaderText(text = "") {
    let tooltipHeaderText;
    if (this.tooltipType === "talent") {
      tooltipHeaderText = text || event.target.parentNode.dataset.name;
    } else if (this.tooltipType == "item") {
      tooltipHeaderText = this.base["displayName"];
    } else {
      tooltipHeaderText = this.base["name_loc"];
    }
    return tooltipHeaderText;
  }
  getImgSrc() {
    let imgSrc;
    if (this.tooltipType !== "shard" && this.tooltipType !== "scepter") {
      imgSrc = event.target.src;
    } else {
      const ability_base =
        "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/abilities/";
      imgSrc = `${ability_base}${this.base["name"]}.png`;
    }
    return imgSrc;
  }
  generateLineOne(text = "") {
    const tooltipLineOne = document.createElement("div");
    tooltipLineOne.setAttribute("class", "tooltip-line-one");
    const tooltipHeaderText = this.gentooltipHeaderText(text);
    const headerText = document.createElement("h3");
    headerText.textContent = tooltipHeaderText;
    const tooltipTitle = document.createElement("div");
    tooltipTitle.setAttribute("class", "tooltip-title");

    const imgSrc = this.getImgSrc() || `/static/images/empty_talent.png`;
    const tooltipHeaderImg = document.createElement("img");
    tooltipHeaderImg.setAttribute("class", "tooltip-img");
    tooltipHeaderImg.setAttribute("src", imgSrc);
    this.tooltip.style.border = "3px solid black";
    tooltipTitle.appendChild(tooltipHeaderImg);
    tooltipTitle.appendChild(headerText);
    tooltipLineOne.appendChild(tooltipTitle);
    if (this.tooltipType === "talent") {
      if (!this.tooltip.children[0]) {
        this.tooltip.appendChild(tooltipLineOne);
      }
      this.tooltip.style.display = "block";
    }
    return tooltipLineOne;
  }
  genLore() {
    const lore = document.createElement("div");
    lore.setAttribute("class", "tooltip-lore");
    let loreText;
    if ("language" in this.base) {
      loreText =
        typeof this.base["language"]["lore"][0] === "string"
          ? this.base["language"]["lore"]
          : this.base["language"]["lore"][0] || null;
    } else {
      loreText = this.base["lore_loc"];
    }
    if (loreText) {
      let loreTextEl = document.createElement("p");
      loreTextEl.textContent = loreText;
      lore.appendChild(loreTextEl);
    }
    return lore;
  }
  appendToContent(description = [], attributes = [], lore = []) {
    let tooltipContent = document.createElement("div");
    tooltipContent.setAttribute("class", "tooltip-content");
    if (this.tooltipType === "shard" || this.tooltipType === "scepter") {
      tooltipContent.appendChild(description);
    } else if (this.tooltipType === "ability") {
      tooltipContent.appendChild(description);
      tooltipContent.appendChild(attributes);
      tooltipContent.appendChild(lore);
    } else {
      tooltipContent.appendChild(attributes);
      tooltipContent.appendChild(description);
      tooltipContent.appendChild(lore);
    }
    if (!this.tooltip.children[1]) {
      this.tooltip.appendChild(tooltipContent);
    }
  }
  highlight_numbers(text) {
    if (typeof text == "object" && text != null) text = text.join("");
    return text
      ? text
          .replace(/<font(.*?)>/g, "")
          .replace(/font/g, "")
          .replace(
            /([^a-z>]\d*\.?\d+%?)(\s\/)?/gm,
            `<strong><span class='tooltip-text-highlight'>$1$2</span></strong>`
          )
          .replace(/<h1>/g, "<h3 class='tooltip-text-highlight'>")
          .replace(/<\/h1>/g, "</h3>")
      : "";
  }
  extract_hidden_values(text) {
    let sp = text.split("%");
    this.base["special_values"].forEach((x) => {
      if (sp.indexOf(x["name"]) > -1) {
        let float = x["values_float"].map(
            (el) => parseFloat(el).toFixed(2) * 1
          ),
          int = x["values_int"];
        if (x["is_percentage"]) {
          float = float.map((el) => (el += "%"));
          int = int.map((el) => (el += "%"));
        }
        sp[sp.indexOf(x["name"])] = `${float || ""}${int || ""}`;
      }
    });
    return this.highlight_numbers(sp.join(""));
  }
}
export default Tooltip;
