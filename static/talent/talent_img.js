const getTalents = async (search) => {
  const url = `${window.location.origin}/files/${search}${window.location.search}`;
  const req = await fetch(url);
  data = await req.json();
  return data;
};
const talents = getTalents(`talent-data/${heroName}`);
const order_talents = (arr, n) => {
  let temp = 0;
  let ret = null;
  for (let tal of arr) {
    if (tal["level"] == n) {
      if (tal["talent_count"] > temp) {
        temp = tal["talent_count"];
        let side = tal["slot"] % 2 != 0 ? "l-talent" : "r-talent";
        ret = `lvl${n} ${side}`;
      } else if (tal["talent_count"] == temp) {
        return "EQUAL";
      }
    }
  }
  return ret;
};
window.addEventListener("load", (e) => {
  createTalentImg();
});
const createTalentImg = async () => {
  const talent_img = [];
  let tals = await talents;
  for (let i = 10; i < 30; i += 5) {
    talent_img.push(order_talents(tals, i));
  }
  const container = document.querySelector(".big-talent");
  for (let [i, talent] of talent_img.entries()) {
    if (talent === "EQUAL") {
      const left = document.createElement("div");
      left.setAttribute("class", `lvl${(i + 2) * 5} l-talent`);
      const right = document.createElement("div");
      right.setAttribute("class", `lvl${(i + 2) * 5} r-talent`);
      container.appendChild(left);
      container.appendChild(right);
    } else {
      const tal = document.createElement("div");
      tal.setAttribute("class", talent);
      container.appendChild(tal);
    }
  }
};
