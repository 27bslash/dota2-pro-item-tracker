import Tooltip from "./tooltip.js";

class TooltipDescription extends Tooltip {
  description() {
    const description = document.createElement("div");
    description.setAttribute("class", "tooltip-description");
    const activeDiv = document.createElement("div");
    const passiveDiv = document.createElement("div");
    const useDiv = document.createElement("div");
    activeDiv.setAttribute("class", "active");
    passiveDiv.setAttribute("class", "passive");
    useDiv.setAttribute("class", "use");
    this.base["language"]["description"].forEach((x) => {
      let activeText = super.highlight_numbers(x.match(/.*<h1>Active:.*/g));
      let toggleText = super.highlight_numbers(x.match(/.*<h1>Toggle:.*/g));
      let passiveText = super.highlight_numbers(x.match(/.*<h1>Passive:.*/g));
      let useText = super.highlight_numbers(x.match(/.*<h1>Use:.*/g));
      if (activeText || toggleText) {
        const activeHeader = x.replace(/<h1>(.*)<\/h1>.*/g, "$1");
        const activeTxt = x.replace(/.*<\/h1>(.*)/g, "$1");
        const headWrapper = document.createElement("div");
        const head = document.createElement("h3");
        const desc = document.createElement("p");
        headWrapper.setAttribute("class", "test");
        head.textContent = activeHeader;
        desc.setAttribute("class", "description-text");
        desc.innerHTML = super.highlight_numbers(activeTxt);
        let statWrapper = document.createElement("div");
        statWrapper.setAttribute("class", "statWrapper");
        headWrapper.appendChild(head);
        const mc = this.statTextGen(
          this.base["stat"]["manaCost"],
          "mana",
          statWrapper
        );
        const cd = this.statTextGen(
          this.base["stat"]["cooldown"],
          "cooldown",
          statWrapper
        );

        headWrapper.appendChild(cd);
        headWrapper.appendChild(mc);
        activeDiv.appendChild(headWrapper);
        activeDiv.appendChild(desc);
      }
      if (passiveText) {
        const useWrapper = this.descText(passiveText, "passive");
        passiveDiv.appendChild(useWrapper);
      }
      if (useText) {
        const useWrapper = this.descText(useText, "use");
        useDiv.appendChild(useWrapper);
      }
      if (activeDiv.children.length > 0) description.appendChild(activeDiv);
      if (passiveDiv.children.length > 0) description.appendChild(passiveDiv);
      if (useDiv.children.length > 0) description.appendChild(useDiv);
    });
    return description;
  }
  descText(text, classText) {
    text = text.replace(/(\/h3>)(.*)/g, `$1<p class='description-text'>$2</p>`);
    const textWrapper = document.createElement("div");
    textWrapper.setAttribute("class", `${classText}-description`);
    textWrapper.innerHTML = text;
    return textWrapper;
  }
  statTextGen(txt, stat, statWrapper) {
    let img = document.createElement("img");
    img.setAttribute(
      "src",
      `https://cdn.cloudflare.steamstatic.com/apps/dota2/images/tooltips/${stat}.png`
    );
    let statText = document.createElement("p");
    if (txt) {
      statText.textContent = txt[0];
      statWrapper.appendChild(img);
      statWrapper.appendChild(statText);
    }
    return statWrapper;
  }
}
export default TooltipDescription;
