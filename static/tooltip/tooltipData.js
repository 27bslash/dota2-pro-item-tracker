async function get_json_data(hero_name) {
  if (hero_name) {
    abilities[hero_name] = await get_json("abilities", hero_name);
    stats = await get_json("stats", hero_name);
  } else {
    items = await get_json("items");
    hero_colors = await get_json("ability_colours");
  }
}
const download_limiter = (p, start) => {
  if (!files_downloaded) {
    for (let i = start; i < p.size; i++) {
      get_json_data([...p][i]);
    }
    files_downloaded = true;
  }
};
const fetch_ability_json = () => {
  const collection = document.getElementsByClassName("abilities");
  let start_point;
  for (let item of collection) {
    file_set.add(item.getAttribute("data-hero"));
    if (file_set.size > files_len) {
      files_downloaded = false;
      start_point = files_len;
    }
  }
  files_len = file_set.size;
  download_limiter(file_set, start_point);
};
export { fetch_ability_json, get_json_data };
