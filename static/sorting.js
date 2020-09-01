let winData;

const pickSort = (role, x, data) => {
  picksArr = [];
  amountOfHeroes = 119;
  pickBox = document.getElementById("pick-box");
  winBox = document.getElementById("win-box");
  winrateBox = document.getElementById("win-rate-box");

  // console.log(pickBox.checked, winBox.checked, winrateBox.checked);
  if (pickBox.checked) {
    x = "picks";
  } else if (winBox.checked) {
    x = "wins";
  } else if (winrateBox.checked) {
    x = "winrate";
  }

  if (role) {
    console.log(`${role}_${x}`);
    let filtered = data.filter((item) => item[`${role}_${x}`] > 0);
    // console.log(filtered);
    data = filtered.sort((a, b) => b[`${role}_${x}`] - a[`${role}_${x}`]);
  } else {
    console.log("false");
    data.sort((a, b) => b[`${x}`] - a[`${x}`]);
  }
  heroCounter = 0;
  // console.log(data);
  grid_position(data, role);
  // document.querySelectorAll(".col").forEach((x) => {
  //   x.style.display = "None";
  //   x.style.gridRow = null;
  //   x.style.gridColumn = null;
  // });
  // console.log(cols);
  // for (let i = 1; i < 2000; i++) {
  //   for (let j = 1; j < cols; j++) {
  //     if (heroCounter < data.length) {
  //       // console.log(data, heroCounter);
  //       currCell = document.getElementById(data[heroCounter].hero).parentNode
  //         .parentNode;
  //       // console.log(i, j);
  //       change_stat_text(data, currCell, role, heroCounter);
  //       currCell.style.display = "block";
  //       currCell.style.gridRow = i;
  //       currCell.style.gridColumn = j;
  //       colour_wins();
  //       heroCounter++;
  //     }
  //   }
  // }
};

function grid_position(data, role) {
  document.querySelectorAll(".col").forEach((x) => {
    x.style.display = "None";
  });
  for (let i = 0; i < data.length; i++) {
    if (document.getElementById(data[i].hero)) {
      currCell = document.getElementById(data[i].hero).parentNode.parentNode;
      change_stat_text(data, currCell, role, i);
      currCell.style.order = i;
      currCell.style.display = "block";
      colour_wins();
    }
  }
}

function change_stat_text(data, currCell, role, heroCounter) {
  stats = currCell.children[1];
  picks = stats.children[0];
  wins = stats.children[1];
  winrate = stats.children[2];
  winText = data[heroCounter][`wins`];
  pickText = data[heroCounter][`picks`];
  winrateText = data[heroCounter][`winrate`];
  if (role) {
    picks.textContent =
      data[heroCounter][`${role}_wins`] + data[heroCounter][`${role}_losses`];
    wins.textContent = data[heroCounter][`${role}_wins`];
    winrate.textContent = data[heroCounter][`${role}_winrate`].toFixed(2) + "%";
    if (+wins.textContent <= 0) {
      // console.log(picks.parentNode.parentNode);
    }
  } else {
    picks.textContent = pickText;
    wins.textContent = winText;
    winrate.textContent = winrateText.toFixed(2) + "%";
  }
}
const colour_wins = () => {
  for (let stat of statText) {
    // console.log(stat.children[2].innerHTML);
    let winrate = stat.children[2].innerHTML.replace("%", "");
    if (+winrate < 50 && +winrate > 30) {
      stat.style.color = `hsl(0, 100%, ${winrate}%)`;
    } else if (+winrate <= 30) {
      stat.style.color = "hsl(0,100%, 30%)";
    } else if (+winrate > 80) {
      stat.style.color = "rgb(120 255 152)";
    } else {
      stat.style.color = `hsl(134, 100%,${winrate}%)`;
    }
  }
};
colour_wins();

function test(x) {
  winData = x;
}