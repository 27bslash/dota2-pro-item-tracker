
// sort out this fetch request
async function t() {
  let res = await fetch("files/hero_ids");
  let data = await res.json();
  return data;
}
arr = [];
function autocomplete() {
  data = t();
  data.then((result) => {
    document.getElementById("search").addEventListener("input", (e) => {
      if (e.target.value.length > 2) {
        arr = result.heroes.filter((x) =>
          x.name
            .toLowerCase()
            .replace(/_/g, " ")
            .includes(e.target.value.toLowerCase())
        );
      }
      display(arr);
    });
  });
}
autocomplete();

const display = () => {
  document.querySelector("ul").innerHTML = "";
  let displayArr = [];
  let linkArr = [];
  for (let h of arr) {
    linkArr.push(h.name);
    displayArr.push(h.name.replace(/_/g, " "));
  }
  for (let i = 0; i < displayArr.length; i++) {
    const div = document.createElement("div");
    div.innerHTML = displayArr[i];
    let a = document.createElement("a");
    a.href = `hero/${linkArr[i]}`;
    div.setAttribute("class", "hero-suggestion");
    a.setAttribute("class", "suggestion-link");
    document.querySelector("ul").appendChild(a).appendChild(div);
  }
  if (document.getElementById("search").value === "") {
    document.querySelector("ul").innerHTML = "";
  }
};
