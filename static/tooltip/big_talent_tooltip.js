const bigTalent = async () => {
  const container = document.querySelector("#talents");
  let tals = await talents;
  for (let [i, talent] of tals.entries()) {
    let center, barContainer, clss, col;
    const slot = talent.slot;
    if (slot % 2 === 0 || slot === 0) {
      col = 3;
      clss = "talent-right";
    } else {
      col = 1;
      clss = "talent-left";
    }
    if ((i + 1) % 2 === 0) {
      // center tooltip
      center = document.createElement("div");
      center.setAttribute("class", "talent-center");
      level = document.createElement("div");
      level.setAttribute("class", "talent-level");
      levelText = document.createElement("p");
      levelText.innerText = talent.level;
      level.appendChild(levelText);
      picks = document.createElement("div");
      picks.setAttribute("class", "talent-picks");
      picksText = document.createElement("p");
      picksText.innerText = "Pick";
      picks.appendChild(picksText);

      center.appendChild(level);
      center.appendChild(picks);
    }
    barContainer = document.createElement("div");
    barContainer.setAttribute("class", clss);
    barContainer.style.gridColumn = col;
    let width = 0;
    if (talent.total_pick_count > 0) {
      width = (talent.talent_count / talent.total_pick_count) * 100;
    }
    talentText = document.createElement("p");
    talentText.innerText = talent.key;
    talentText.setAttribute("class", "talent-text");
    talentBar = document.createElement("div");
    talentBar.setAttribute("class", "talent-bar");
    talentBar.style.width = width + "%";
    talentBar.style.height = "45px";
    valueTxt = document.createElement("p");
    valueTxt.innerText = parseInt(Math.floor(width)) + "%";
    barContainer.appendChild(talentText);
    barContainer.appendChild(talentBar);
    barContainer.appendChild(valueTxt);
    if (center) {
      container.appendChild(center);
    }
    if (barContainer) {
      container.appendChild(barContainer);
    }
  }
};
window.addEventListener("load", (e) => {
  bigTalent();
});
