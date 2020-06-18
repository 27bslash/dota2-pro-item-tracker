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
      console.log(e.target.value.length);
      if (e.target.value.length > 2) {
          arr = result.heroes.filter((x) => x.name.includes(e.target.value));
      }
      display(arr);
    });
  });
}
autocomplete();
const display = () => {
  let displayArr = [];
  for (let h of arr) {
    console.log(h);
    displayArr.push(h.name);
  }
  const html = displayArr.join("");
  document.querySelector("h1").innerHTML = html;
};
