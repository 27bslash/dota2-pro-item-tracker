const pickSort = (x) => {
  picksArr = [];
  heroCell = "";
  if (x != null) {
    for (let cell of cells) {
      let picks = +cell.children[1].children[x].textContent.replace("%", ""),
        hero = cell.children[0].children[0].id,
        obj = { hero: [hero], picks: [picks] };
      console.log(cell.children[1].children[2].textContent, x);
      picksArr.push(obj);
      picksArr.sort((a, b) => b.picks - a.picks);
    }
    heroCounter = 0;
    for (let i = 1; i < 25; i++) {
      for (let j = 1; j < 19; j++) {
        heroCounter++;
        if (heroCounter < 119) {
          // console.log(
          //   heroCounter,
          //   document.getElementById(picksArr[heroCounter].hero[0])
          // );
          document.getElementById(
            picksArr[heroCounter - 1].hero[0]
          ).parentNode.parentNode.style.gridColumn = j;
          document.getElementById(
            picksArr[heroCounter - 1].hero[0]
          ).parentNode.parentNode.style.gridRow = i;
        }
      }
    }
  } else {
    document.querySelector(".buttons").style.display = 'none';
    for (let cell of cells) {
      cell.style.gridArea = null;
    }
  }
};
pickSort(1);
