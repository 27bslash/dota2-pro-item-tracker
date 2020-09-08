let winData;

const pickSort = (role, x) => {
  picksArr = [];
  amountOfHeroes = 119;
  pickBox = document.getElementById("pick-box");
  winBox = document.getElementById("win-box");
  winrateBox = document.getElementById("win-rate-box");
  stats = get_json("win-stats");
  stats.then((data) => {
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
      data = filtered.sort((a, b) => b[`${role}_${x}`] - a[`${role}_${x}`]);
    } else {
      console.log("false");
      data.sort((a, b) => b[`${x}`] - a[`${x}`]);
    }
    heroCounter = 0;
    grid_position(data, role);
  });
};

function grid_position(data, role) {
  document.querySelectorAll(".hero-cell").forEach((x) => {
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
function uncheck(x) {
  const check_boxes = document.querySelector(".control-right");
  for (let chk of check_boxes.children) {
    if (chk.children[1].textContent != x) {
      chk.children[0].checked = false;
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
  statText = document.querySelectorAll(".win-stats");
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
