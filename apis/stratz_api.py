#     unparsed_match_result = {
#         # match information
#         'hero': kwargs['hero_name'],
#         'parsed': False,
#         # player information
#         'name': self.get_info_from_url_db(kwargs['match_id'], 'name', kwargs['hero_name'], kwargs['testing']), 'account_id': p['account_id'],
#         'mmr': self.get_info_from_url_db(kwargs['match_id'], 'mmr', kwargs['hero_name'], kwargs['testing']),
#         # game stats
#         'lvl': p['level'],  'hero_damage': p['hero_damage'], 'gold': p['total_gold'],
#         'tower_damage': p['tower_damage'], 'gpm': p['gold_per_min'], 'xpm': p['xp_per_min'],
#         'kills': p['kills'], 'deaths': p['deaths'], 'assists': p['assists'], 'last_hits': p['last_hits'],
#         'win': p['win'], 'id': kwargs['match_id'],
#         # laning phase stats
#         'benchmarks': p['benchmarks'],
#         # final items
#         'final_items': main_items, 'backpack': bp_items, 'item_neutral': self.item_methods.get_item_name(p['item_neutral']), 'aghanims_shard': aghanims_shard,
#         'abilities': detailed_ability_info(abilities, kwargs['hero_id'])}

# parsed_match_result = {'gold_adv': resp['radiant_gold_adv'][-1], 'final_items': main_items, 'backpack': bp_items, 'additional_units': additional_units, 'aghanims_shard': aghanims_shard, 'parsed': True, 'items': purchase_log,
#                            # laning stats
#                            'starting_items': starting_items, 'kills_ten': kills_ten, 'deaths_ten': deaths_ten, 'lvl_at_ten': lvl_at_ten, 'role': role,
#                            'last_hits_ten': int(float(p['benchmarks']['lhten']['raw'])), 'gpm_ten': gpm_at_ten,
#                            'xpm_ten': xpm_at_ten, 'lane_efficiency': round(p['lane_efficiency'] * 100, 2)}
import asyncio
import datetime
import logging
import statistics
import time
import traceback
from helper_funcs.abilities import detailed_ability_info
from helper_funcs.database.db import db
from helper_funcs.database.collection import current_patch
import json
import aiohttp
import requests
from apis.opendota_api import Api_request
from asyncio_throttle import Throttler

from logs.logger_config import configure_logging

throttler = Throttler(rate_limit=15, period=1)

configure_logging()


def graphql():
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJodHRwczovL3N0ZWFtY29tbXVuaXR5LmNvbS9vcGVuaWQvaWQvNzY1NjExOTgwNDk3MjMyNTAiLCJ1bmlxdWVfbmFtZSI6IkFkZHJlc3MgbWUgYnkgbXkgaHVzYmFuZCdzIHJhbmsiLCJTdWJqZWN0IjoiMzIyMzFkMDgtNzk0NS00YzNhLTg5ZGItMzc0NzFiMTg4NGYxIiwiU3RlYW1JZCI6Ijg5NDU3NTIyIiwibmJmIjoxNjY4MDM2NDQ4LCJleHAiOjE2OTk1NzI0NDgsImlhdCI6MTY2ODAzNjQ0OCwiaXNzIjoiaHR0cHM6Ly9hcGkuc3RyYXR6LmNvbSJ9.nycCBnzcNICIsBwoS7nBfap6swBJYPUA0wtaUG7nJsc"
    headers = {"content-type": "application/json", "Authorization": f"Bearer {api_key}"}
    id = "test"
    query = """query ($id: Long!){
  match(id: $id)
  {
    id
    durationSeconds
    startDateTime
    pickBans {
      isPick
      heroId
      isRadiant
      bannedHeroId
      wasBannedSuccessfully
      playerIndex
    }

    players {
      isRandom
      steamAccountId
      networth
      heroId
      isVictory
      level
      kills
      deaths
      assists
      numLastHits
      goldPerMinute
      playerSlot
      isRadiant
      heroId
      experiencePerMinute
      goldPerMinute
      heroDamage
      role
      lane
      towerDamage
      item0Id
      item1Id
      item2Id
      item3Id
      item4Id
      item5Id
      backpack0Id
      backpack1Id
      backpack2Id
      neutral0Id
      abilities {
        abilityId
      }

      stats {
        steamAccountId
        matchPlayerBuffEvent {
          abilityId
          itemId
          stackCount
        }
  	    level
        experiencePerMinute
        goldPerMinute
        lastHitsPerMinute
        killEvents {
          time
          target
        }
        itemPurchases {
          time
          itemId
        }
        spiritBearInventoryReport {
          item0Id
          item1Id
          item2Id
          item3Id
          item4Id
          item5Id
          backPack0Id
          backPack1Id
          backPack2Id
          neutral0Id
        }
				level
        inventoryReport {
        	item0 {
        	  charges
            itemId
        	  secondaryCharges
        	}
          item1 {
            charges
            itemId
            secondaryCharges
          }
          item2 {
            charges
            itemId
            secondaryCharges
          }
          item3 {
            charges
            itemId
            secondaryCharges
          }
          item4 {
            charges
            itemId
            secondaryCharges
          }
          item5 {
            charges
            itemId
            secondaryCharges
          }
          backPack0 {
            charges
            itemId
            secondaryCharges
          }
          backPack1 {
            charges
            itemId
            secondaryCharges
          }
          backPack2 {
            charges
            itemId
            secondaryCharges
          }
          neutral0 {
            charges
            itemId
            secondaryCharges
          }
        }
      }
    }
  }
}
"""

    variables = {"id": 7368619088}
    requst_data = {"query": query, "variables": variables}
    url = "https://api.stratz.com/graphql"
    r = requests.post(url, headers=headers, json=requst_data)
    # print(r.request.body)
    # print(r.request.headers)
    if r.status_code == 200:
        print("nice")
        with open("stratz_api_req.json", "w") as f:
            json.dump(obj=r.json()["data"], fp=f, indent=4)
    else:
        print(f"query failed {r.status_code} ")


class Stratz_api(Api_request):
    async def stratz_api_request(self, m_id, hero_name, testing=False):
        query = """query ($id: Long!){
    match(id: $id)
    {
        id
        parsedDateTime
        durationSeconds
        startDateTime
        pickBans {
        isPick
        heroId
        isRadiant
        bannedHeroId
        wasBannedSuccessfully
        playerIndex
        }

        players {
        isRandom
        steamAccountId
        networth
        heroId
        isVictory
        level
        kills
        deaths
        assists
        numLastHits
        goldPerMinute
        playerSlot
        isRadiant
        heroId
        experiencePerMinute
        goldPerMinute
        heroDamage
        role
        lane
        towerDamage
        item0Id
        item1Id
        item2Id
        item3Id
        item4Id
        item5Id
        backpack0Id
        backpack1Id
        backpack2Id
        neutral0Id
        abilities {
            abilityId
        }

        stats {
            steamAccountId
            matchPlayerBuffEvent {
            abilityId
            itemId
            stackCount
            }
            level
            experiencePerMinute
            goldPerMinute
            networthPerMinute
            lastHitsPerMinute
            killEvents {
                time
                target
            }
            itemPurchases {
                time
                itemId
            }
            itemUsed {
                itemId
            }
            spiritBearInventoryReport {
            item0Id
            item1Id
            item2Id
            item3Id
            item4Id
            item5Id
            backPack0Id
            backPack1Id
            backPack2Id
            neutral0Id
            }
                    level
            inventoryReport {
                item0 {
                charges
                itemId
                secondaryCharges
                }
            item1 {
                charges
                itemId
                secondaryCharges
            }
            item2 {
                charges
                itemId
                secondaryCharges
            }
            item3 {
                charges
                itemId
                secondaryCharges
            }
            item4 {
                charges
                itemId
                secondaryCharges
            }
            item5 {
                charges
                itemId
                secondaryCharges
            }
            backPack0 {
                charges
                itemId
                secondaryCharges
            }
            backPack1 {
                charges
                itemId
                secondaryCharges
            }
            backPack2 {
                charges
                itemId
                secondaryCharges
            }
            neutral0 {
                charges
                itemId
                secondaryCharges
            }
            }
        }
        }
    }
    }
    """

        variables = {"id": m_id}
        requst_data = {"query": query, "variables": variables}
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiMzIyMzFkMDgtNzk0NS00YzNhLTg5ZGItMzc0NzFiMTg4NGYxIiwiU3RlYW1JZCI6Ijg5NDU3NTIyIiwibmJmIjoxNzAxNjI4NTYwLCJleHAiOjE3MzMxNjQ1NjAsImlhdCI6MTcwMTYyODU2MCwiaXNzIjoiaHR0cHM6Ly9hcGkuc3RyYXR6LmNvbSJ9.s4PxRHlfbBXFYqkPQRHVaSKfgYzXwqL6nc7aJGIArhk"

        headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        url = "https://api.stratz.com/graphql"
        try:
            async with aiohttp.ClientSession() as session:
                async with throttler:
                    async with session.post(
                        url=url, headers=headers, json=requst_data
                    ) as response:
                        resp = await response.json()

                        if response.status == 404:
                            # game not over yet
                            pass
                        if response.status == 429:
                            # rate liimt
                            time.sleep(1)
                        if response.status == 500:
                            # server error
                            return self.add_to_dead_games(m_id, stratz=True)
                        if (
                            "message" in resp
                            and resp["message"] == "API rate limit exceeded"
                        ):
                            print(
                                "second: ",
                                response.headers["X-RateLimit-Remaining-Second"],
                            )
                            print(
                                "minute: ",
                                response.headers["X-RateLimit-Remaining-minute"],
                            )
                            print(
                                "hour: ", response.headers["X-RateLimit-Remaining-Hour"]
                            )
                            time.sleep(5)
                            return
                        if not resp["data"]["match"]:
                            # match not over yet
                            return

                        match_id = int(resp["data"]["match"]["id"])
                        print(
                            f"successfully got {match_id}",
                            "remaining today with stratz: ",
                            response.headers["X-RateLimit-Remaining-Day"],
                        )
                        if resp["data"]["match"]["durationSeconds"] < 600:
                            db["dead_games"].insert_one({"id": match_id, "count": 20})
                            return
                        parsed_replay = self.parse_replay(
                            resp["data"]["match"], match_id, hero_name, testing=False
                        )
                        if parsed_replay and parsed_replay != "no patch":
                            db["heroes"].find_one_and_update(
                                {"id": match_id, "hero": hero_name},
                                {"$set": parsed_replay[0]},
                                upsert=True,
                            )
                            try:
                                db["non-pro"].insert_many(
                                    parsed_replay[1], ordered=False
                                )
                            except Exception as e:
                                # Handle duplicate key errors or other write errors
                                pass
                            db["dead_games"].delete_many({"id": m_id})
                            print(f"{hero_name} should reach here")

        except Exception as e:
            print(m_id, hero_name, traceback.format_exc())
            logging.error(f"{m_id}, {hero_name}, {traceback.format_exc()}")
            pass

    def parse_replay(self, resp, m_id, hero_name, testing=False):
        if resp["durationSeconds"] < 600:
            db["dead_games"].insert_one({"id": m_id, "count": 20})
            return None
        if not current_patch:
            return "no patch"
        match_patch = current_patch["patch"]
        rad_draft = [
            self.hero_methods.hero_name_from_hero_id(p["heroId"])
            for p in resp["players"]
            if p["isRadiant"]
        ]
        dire_draft = [
            self.hero_methods.hero_name_from_hero_id(p["heroId"])
            for p in resp["players"]
            if not p["isRadiant"]
        ]
        unparsed_match_result = {
            "unix_time": resp["startDateTime"],
            "patch": match_patch,
            "duration": resp["durationSeconds"],
            "radiant_draft": rad_draft,
            "dire_draft": dire_draft,
        }
        # this does nothing
        # for i in range(10):
        #     p = resp['players'][i]
        #     hero_id = p['hero_id']
        #     if p['randomed'] and p['isRadiant']:
        #         rad_draft.append(
        #             self.hero_methods.hero_name_from_hero_id(hero_id))
        #     if p['randomed'] and not p['isRadiant']:
        #         dire_draft.append(
        #             self.hero_methods.hero_name_from_hero_id(hero_id))
        non_pro_games = []
        match_data = None
        for i in range(10):
            p = resp["players"][i]
            hero_id = p["heroId"]
            unparsed_match_result = unparsed_match_result | self.stratz_unparsed(
                p=p,
                hero_id=hero_id,
                hero_name=hero_name,
                match_id=m_id,
                testing=testing,
            )
            # check if one of the players matches search
            purchase_log = p["stats"]["itemPurchases"]
            if not purchase_log:
                if hero_id != self.hero_methods.get_id(hero_name):
                    continue
                print("add to parse: ", m_id)
                db["heroes"].find_one_and_update(
                    {"id": m_id, "hero": hero_name},
                    {"$set": unparsed_match_result},
                    upsert=True,
                )
                self.add_to_dead_games(m_id, stratz=True)
                return
                # return db['parse'].find_one_and_update(
                #     {'id': m_id}, {"$set": {'id': m_id}}, upsert=True)

            role = p["role"]
            lane = p["lane"]
            position = None
            if lane == "SAFE_LANE":
                if role == "CORE":
                    position = "Safelane"
                else:
                    position = "Hard Support"
            elif lane == "OFF_LANE":
                if role == "CORE":
                    position = "Offlane"
                else:
                    position = "Support"
            else:
                position = "Midlane"
            non_pro_games.append(
                self.insert_non_pro_games(p, hero_id, m_id, position, opendota=False)
            )
            if hero_id != self.hero_methods.get_id(hero_name):
                continue
            parsed_match_result = self.stratz_parsed(
                p=p, hero_name=hero_name, role=position, resp=resp
            )

            match_data = unparsed_match_result | parsed_match_result
        return match_data, non_pro_games

    def stratz_parsed(self, **kwargs):
        p = kwargs["p"]
        hero_name = kwargs["hero_name"]
        role = kwargs["role"]
        resp = kwargs["resp"]
        stats = p["stats"]
        purchase_log = stats["itemPurchases"]
        rad_draft = self.stratz_draft(resp, True)
        dire_draft = self.stratz_draft(resp, False)

        max_gold_in_laning_phase = 5444

        hero_bans = [
            self.hero_methods.hero_name_from_hero_id(ban["bannedHeroId"])
            for ban in resp["pickBans"]
            if ban["bannedHeroId"] and ban["playerIndex"]
        ]

        if "kills_log" in stats:
            kills_ten, deaths_ten = self.calulate_kills_at_ten(
                stats["kills_log"], hero_name
            )
        else:
            kills_ten = 0
            deaths_ten = 0
        lvls = [i for i, element in enumerate(stats["level"]) if element >= 600]
        lvl_at_ten = lvls[0] if lvls else len(stats["level"])
        xpm_at_ten = int(sum(stats["experiencePerMinute"][:10]) / 10)
        gpm_at_ten = statistics.mean(stats["goldPerMinute"][:10])
        last_hits_at_ten = sum(stats["lastHitsPerMinute"][:10])
        lane_efficiency = round(
            (stats["networthPerMinute"][10]) / max_gold_in_laning_phase * 100, 2
        )
        aghanims_shard = None
        # purchase_log = self.item_methods.bots(
        #     purchase_log, stats['purchase'])
        purchase_log = [
            {"id": purchase["itemId"], "key": key, "time": purchase["time"]}
            for purchase in purchase_log
            if "recipe"
            not in (key := self.item_methods.get_item_name(purchase["itemId"]))
        ]
        for purchase in purchase_log:
            if purchase["key"] == "aghanims_shard":
                temp = purchase.copy()
                aghanims_shard = self.item_methods.convert_time([temp])
        self.add_missing_items(p['stats']['inventoryReport'], purchase_log)
        starting_items = self.stratz_starting_items(stats["inventoryReport"][0])
        rev = purchase_log.copy()[::-1]
        main_items = self.item_methods.get_most_recent_items(rev, 6, p, opendota=False)
        bp_items = self.item_methods.get_most_recent_items(rev, 3, p, opendota=False)
        additional_units = stats["spiritBearInventoryReport"]
        if additional_units:
            additional_units = self.item_methods.get_most_recent_items(
                rev, 6, additional_units[0], opendota=False
            )
        parsed_match_result = {
            "final_items": main_items,
            "backpack": bp_items,
            "additional_units": additional_units,
            "aghanims_shard": aghanims_shard,
            "parsed": True,
            "items": purchase_log,
            # laning stats
            "starting_items": starting_items,
            "kills_ten": kills_ten,
            "deaths_ten": deaths_ten,
            "lvl_at_ten": lvl_at_ten,
            "role": role,
            "last_hits_ten": last_hits_at_ten,
            "gpm_ten": gpm_at_ten,
            "xpm_ten": xpm_at_ten,
            "lane_efficiency": lane_efficiency,
            # draft
            "radiant_draft": rad_draft,
            "dire_draft": dire_draft,
            "bans": hero_bans,
        }
        return parsed_match_result

    

    def stratz_starting_items(self, invent):
        ret = [
            {
                "id": value["itemId"],
                "time": 0,
                "key": self.item_methods.get_item_name(value["itemId"]),
            }
            for k in invent
            if (value := invent[k])
        ]
        return ret

    def stratz_unparsed(self, **kwargs):
        player = kwargs["p"]
        abilities = player["abilities"]
        main_items = [
            {"key": key, "time": 0, "id": player[f"item{i}Id"]}
            for i in range(6)
            if player[f"item{i}Id"]
            and (key := self.item_methods.get_item_name(player[f"item{i}Id"]))
            and "recipe" not in key
        ]
        bp_items = [
            {"key": key, "time": 0, "id": player[f"backpack{i}Id"]}
            for i in range(3)
            if player[f"backpack{i}Id"]
            and (key := self.item_methods.get_item_name(player[f"backpack{i}Id"]))
            and "recipe" not in key
        ]
        # buffs = player['matchPlayerBuffEvent']
        aghanims_shard = None
        # if buffs:
        #     for buff in buffs:
        #         if buff['matchPlayerBuffEvent']['itemId'] != 609:
        #             continue
        #         else:
        #             temp = {'key': 'aghanims_shard',
        #                     'time': buff['time']}
        #             aghanims_shard = self.item_methods.convert_time([
        #                 temp])
        unparsed_match_result = {
            # match information
            "hero": kwargs["hero_name"],
            "parsed": False,
            # player information
            "name": self.get_info_from_url_db(
                kwargs["match_id"], "name", kwargs["hero_name"], kwargs["testing"]
            ),
            "account_id": player["steamAccountId"],
            "mmr": self.get_info_from_url_db(
                kwargs["match_id"], "mmr", kwargs["hero_name"], kwargs["testing"]
            ),
            # game stats
            "lvl": player["level"],
            "hero_damage": player["heroDamage"],
            "gold": player["networth"],
            "tower_damage": player["towerDamage"],
            "gpm": player["goldPerMinute"],
            "xpm": player["experiencePerMinute"],
            "kills": player["kills"],
            "deaths": player["deaths"],
            "assists": player["assists"],
            "last_hits": player["numLastHits"],
            "win": 1 if player["isVictory"] else 0,
            "id": kwargs["match_id"],
            # final items
            "final_items": main_items,
            "backpack": bp_items,
            "item_neutral": self.item_methods.get_item_name(player["neutral0Id"]),
            "aghanims_shard": aghanims_shard,
            "abilities": detailed_ability_info(
                abilities, kwargs["hero_id"], key="abilityId"
            ),
        }
        return unparsed_match_result

    def stratz_draft(self, resp, side):
        hero_ids = [player["heroId"] for player in resp["players"]]
        return [
            self.hero_methods.hero_name_from_hero_id(player["heroId"])
            for player in resp["pickBans"]
            if player["isPick"]
            and player["isRadiant"] == side
            and player["heroId"] in hero_ids
        ]

    async def stratz_call(self, urls, hero_name, testing=False):
        print(f"{hero_name}: {urls}")
        ret = await asyncio.gather(
            *[self.stratz_api_request(url, hero_name, testing) for url in urls]
        )


if __name__ == "__main__":
    # with open('apis/api_tests/gyrocopter_test.json', 'r') as f:
    #     data = json.load(f)
    #     Stratz_api().parse_replay(
    #         data['data']['match'], 7371420489, 'gyrocopter')
    # with open('apis/api_tests/aa_test.json', 'r') as f:
    #     data = json.load(f)
    #     Stratz_api().parse_replay(
    #         data['data']['match'], 7368619088, 'ancient_apparition')
    ret = asyncio.run(Stratz_api().stratz_call([7517648734], "brewmaster"))
    print(ret)
    # target = 76.02
    # for i in range(1, 5500):
    #     val = (4138 / i) * 100
    #     if val < target:
    #         print(val, i)
    #         break
    # dat = {'item0': {'charges': 3, 'itemId': 44, 'secondaryCharges': None}, 'item1': {'charges': 1, 'itemId': 237, 'secondaryCharges': None}, 'item2': {'charges': None, 'itemId': 16, 'secondaryCharges': None}, 'item3': {'charges': 0, 'itemId': 16,
    # 'secondaryCharges': None}, 'item4': {'charges': 0, 'itemId': 16, 'secondaryCharges': None}, 'item5': {'charges': 1, 'itemId': 42, 'secondaryCharges': None}, 'backPack0': None, 'backPack1': None, 'backPack2': None, 'neutral0': None}
    # Stratz_api().stratz_starting_items(dat)
