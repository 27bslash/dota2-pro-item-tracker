let winData;

const pickSort = (role, sort_query) => {
  picksArr = [];
  amountOfHeroes = 119;
  pickBox = document.getElementById("pick-box");
  winBox = document.getElementById("win-box");
  winrateBox = document.getElementById("win-rate-box");
  banBox = document.getElementById("win-rate-box");
  stats = get_json("win-stats");
  stats.then((data) => {
    if (pickBox.checked) {
      sort_query = "picks";
    } else if (winBox.checked) {
      sort_query = "wins";
    } else if (winrateBox.checked) {
      sort_query = "winrate";
    } else if (banBox.checked) {
      sort_query = "bans";
    }
    if (role) {
      let filtered = data.filter((item) => item[`${role}_${sort_query}`] > 0);
      data = filtered.sort(
        (a, b) => b[`${role}_${sort_query}`] - a[`${role}_${sort_query}`]
      );
    } else {
      console.log("false");
      data.sort((a, b) => b[sort_query] - a[sort_query]);
    }
    heroCounter = 0;
    grid_position(data, role);
    let titleText = "most";
    if (sort_query === "winrate") titleText = "highest";
    let titleString = `${titleText} ${role || ""} ${sort_query}`;
    document.querySelector(".sort-title").textContent = titleString;
    document.querySelector(".sort-title").id = titleString;
  });
};

function grid_position(data, role) {
  document.querySelectorAll(".hero-cell").forEach((x) => {
    x.classList.add("hide");
  });
  for (let i = 0; i < data.length; i++) {
    if (document.getElementById(data[i].hero)) {
      currCell = document.getElementById(data[i].hero).parentNode.parentNode;
      change_stat_text(data, currCell, role, i);
      currCell.style.order = i;
      currCell.classList.remove("hide");
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
