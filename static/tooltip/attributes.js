import Tooltip from "./tooltip.js";
class TooltipAttributes extends Tooltip {
  attributeGen(dmgType = "") {
    const attribute_obj = [];
    const attributes = document.createElement("div");
    attributes.setAttribute("class", "attributes");
    switch (dmgType) {
      case 1:
        dmgType = "red";
        break;
      case 2:
        dmgType = "#a3dcee";
        break;
      case 3:
        dmgType = "#a3dcee";
        break;
      case 4:
        dmgType = "#FBDC98";
    }
    if (this.base["attrib"]) {
      this.base["attrib"].forEach((x) => {
        if (x["footer"]) {
          attribute_obj.push(`${x["header"]} ${x["value"]} ${x["footer"]}`);
        } else {
          const operator = x["header"].replace(/[^+-]/g, "");
          attribute_obj.push(
            `${operator} ${x["value"]} ${x["header"].replace(operator, "")}`
          );
        }
      });
    } else {
      this.base["special_values"].forEach((x) => {
        let heading = x["heading_loc"],
          float = x["values_float"].map((el) => parseFloat(el.toFixed(2)));
        if (heading.length > 0) {
          if (x["is_percentage"]) {
            float = float.map((el) => (el += "%"));
          }
          if (float) {
            float = float.join("/");
          }
          attribute_obj.push(heading + " " + float);
        }
      });
    }
    attribute_obj.forEach((x) => {
      const attribute = document.createElement("p");
      attribute.setAttribute("class", "attribute");
      let label = x.split(":")[0];
      let value = x.split(":")[1];
      let color = "white";
      if (label.includes("DAMAGE")) {
        // console.log(label, value);
        color = dmgType;
      }
      let htmlString = `${label}: `;
      if (value) {
        const spl = value.split("/");
        spl.forEach((el, i) => {
          htmlString += `<strong><span class='tooltip-text-highlight' style='color:${color}'>${el}</span></strong>`;
          if (i < spl.length - 1) {
            htmlString += "/";
          }
        });
        attribute.innerHTML = super.highlight_numbers(x);
      } else {
        attribute.innerHTML = super.highlight_numbers(x);
      }
      attributes.appendChild(attribute);
    });
    return attributes;
  }
  singleAttribute(attribute) {
    const shrtAttr = attribute.substring(0, 3);
    const attrWrapper = document.createElement("div");
    attrWrapper.setAttribute("class", `attribute-wrapper`);
    const attrImg = document.createElement("img");
    attrImg.setAttribute(
      "src",
      `https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/icons/hero_${attribute}.png`
    );
    attrImg.setAttribute("class", "attrImg");
    const baseAttr = document.createElement("p");
    baseAttr.setAttribute("class", "baseAttr");
    baseAttr.textContent = this.base[`${shrtAttr}_base`];
    const attrGain = document.createElement("p");
    attrGain.setAttribute("class", "attrGain");
    attrGain.textContent =
      "+" + parseFloat(this.base[`${shrtAttr}_gain`]).toFixed(2);
    attrWrapper.appendChild(attrImg);
    attrWrapper.appendChild(baseAttr);
    attrWrapper.appendChild(attrGain);
    return attrWrapper;
  }
  heroAttributes() {
    const attributes = document.createElement("div");
    attributes.setAttribute("class", "hero-attributes");
    const str = this.singleAttribute("strength");
    const agi = this.singleAttribute("agility");
    const int = this.singleAttribute("intelligence");

    attributes.appendChild(str);
    attributes.appendChild(agi);
    attributes.appendChild(int);
    return attributes;
  }
}
export default TooltipAttributes;
