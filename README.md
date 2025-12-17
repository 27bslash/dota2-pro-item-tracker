Data‑driven system that automatically updates Dota 2 Steam guides using high‑MMR match data. The project continuously tracks top‑skill games, adapts to new patches, and refreshes guides on a fixed schedule so builds and recommendations stay relevant without manual upkeep.

---

## How it works

1. **Match discovery**
   High‑MMR games are scraped directly from the Dota 2 Watch tab using `valvePython`.

2. **Replay parsing**
   Match replays and metadata are processed via the OpenDota and Stratz APIs.

3. **Data aggregation**
   Item builds, skill orders, timings, and trends are aggregated across recent high‑skill matches.

4. **Guide generation**
   Processed results are converted into Steam‑compatible guide content.

5. **Automated publishing**
   Guides are updated on a scheduled basis, with special handling for new Dota 2 patches.

---

## Features

* **Automatic patch detection**
  Detects Dota 2 game patches and refreshes datasets to prevent outdated builds.

* **Weekly Steam guide updates**
  Guides are regenerated once per week using only high‑MMR matches to reduce noise.

* **High‑skill data only**
  Filters matches to focus on competitive‑level decision making.

* **Fully automated pipeline**
  No manual intervention required once configured.

---

## Architecture overview

```
Dota 2 Watch Tab
        ↓
Match / Replay IDs
        ↓
OpenDota & Stratz APIs
        ↓
Data Processing & Aggregation
        ↓
Steam Guide Generator
        ↓
Scheduled Updates
```

---

## Tech stack

* **Python** – core orchestration and data processing
* **valvePython** – scraping live high‑MMR matches
* **OpenDota API** – replay and match statistics
* **Stratz API** – supplementary match and hero data
* **Steam Guides** – automated publishing target

---

## Setup

> This project assumes familiarity with Python and Steam / Dota 2 APIs.

### Requirements

* Python 3.10+
* Steam API key
* OpenDota API access
* Stratz API access

## Example output

<img width="838" height="923" alt="image" src="https://github.com/user-attachments/assets/729f0cd5-2d11-4a40-9d97-5743a5cbf0cd" />
