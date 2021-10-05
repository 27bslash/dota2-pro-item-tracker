const getTalents = async (search) => {
  const url = `${window.location.origin}/files/${search}${window.location.search}`;
  const req = await fetch(url);
  data = await req.json();
  return data;
};
const talents = getTalents(`talent-data/${heroName}`);
const order_talents = (arr, n) => {
  let side = "";
  for (let i = 0; i < 7; i += 2) {
    tal = arr[i];
    if (tal["level"] == n) {
      if (tal["talent_count"] || arr[i + 1]["talent_count"] > 0) {
        if (tal["talent_count"] > arr[i + 1]["talent_count"]) {
          side = "l-talent";
        } else if (tal["talent_count"] < arr[i + 1]["talent_count"]) {
          side = "r-talent";
        } else if (
          tal["talent_count"] === arr[i + 1]["talent_count"] &&
          tal["talent_count"] > 0
        ) {
          return "EQUAL";
        }
      } else {
        return null;
      }
    }
  }
  return `lvl${n} ${side}`;
};
const createTalentImg = async () => {
    const talent_img = [];
    let tals = await talents;
    for (let i = 10; i < 30; i += 5) {
        talent_img.push(order_talents(tals, i));
    }
    const container = document.querySelector(".big-talent");
    for (let [i, talent] of talent_img.entries()) {
        if (talent) {
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
    }
};

window.addEventListener("load", (e) => {
  createTalentImg();
});