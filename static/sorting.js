const pickSort = (x) => {
  picksArr = [];
  amountOfHeroes = 119;
  for (let cell of cells) {
    let picks = +cell.children[1].children[x].textContent.replace("%", ""),
      hero = cell.children[0].children[0].id,
      obj = { hero: [hero], picks: [picks] };
    picksArr.push(obj);
  }
  picksArr.sort((a, b) => b.picks - a.picks);
  heroCounter = 0;
  for (let i = 1; i < 25; i++) {
    for (let j = 1; j < 17; j++) {
      //do this based on width of users screen
      heroCounter++;
      if (heroCounter < amountOfHeroes) {
        currCell = document.getElementById(picksArr[heroCounter - 1].hero[0])
          .parentNode.parentNode;
        currCell.style.gridRow = i;
        currCell.style.gridColumn = j;
      }
    }
  }
};
// pickSort(1);
