import asyncio
import time
import aiohttp
import traceback
from helper_funcs.hero import Hero
from helper_funcs.abilities import detailed_ability_info
from helper_funcs.items import Items
from helper_funcs.database.db import db
from helper_funcs.database.collection import current_patch
import datetime
from logs.log_config import pro_item_logger

hero_urls = db["urls"]
hero_output = db["heroes"]
acc_ids = db["account_ids"]


class Api_request:
    def __init__(self) -> None:
        self.item_methods = Items()
        self.hero_methods = Hero()
        self.match = None

    async def async_get(self, m_id, heroid, testing=False):
        if testing:
            global hero_output
            hero_output = db["test_heroes"]
        url = f"https://api.opendota.com/api/matches/{m_id}"
        # dupe_check = hero_output.find_one({'hero': hero_name, 'id': m_id})
        # bad_id_check = db['dead_games'].find_one(
        #     {'id': m_id, 'count': {"$gte": 20}})
        # parse_check = db['parse'].find_one({'id': m_id})
        ret = {}
        # if dupe_check is not None or bad_id_check is not None or parse_check is not None:
        #     return 'Bad Id'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url) as response:
                    if response.status != 200:
                        if response.status == 404:
                            # game not over yet
                            ret["parse"] = [{"id": m_id}]

                            return db["parse"].find_one_and_update(
                                {"id": m_id}, {"$set": {"id": m_id}}, upsert=True
                            )
                        if response.status == 429:
                            # rate liimt
                            time.sleep(1)

                        if response.status == 500:
                            # server error
                            ret["dead_games"] = m_id

                            return self.add_to_dead_games(m_id)
                    resp = await response.json()
                    match_id = int(resp["match_id"])
                    print(
                        f"successfully got {match_id}",
                        "remaining: ",
                        response.headers["X-Rate-Limit-Remaining-Day"],
                    )
                    if resp["duration"] < 600:
                        ret["dead_games"] = m_id

                        return db["dead_games"].insert_one(
                            {"id": match_id, "count": 20}
                        )
                    self.match = resp
                    rad_draft = self.draft(resp, 0)
                    dire_draft = self.draft(resp, 1)
                    hero_bans = [
                        self.hero_methods.hero_name_from_hero_id(ban["hero_id"])
                        for ban in resp["picks_bans"]
                        if ban["is_pick"] == False
                    ]
                    deaths_ten = 0
                    non_pro_games = []

                    if not current_patch:
                        return "no patch"
                    for p_o in current_patch['patches'][::-1]:
                        if resp['start_time'] >= p_o['patch_timestamp']:
                            self.patch = p_o['patch_number']
                            break

                    unparsed_match_result = {
                        "unix_time": resp["start_time"],
                        "patch": self.patch,
                        "duration": resp["duration"],
                        "radiant_draft": rad_draft,
                        "dire_draft": dire_draft,
                        "radiant_team": (
                            resp['radiant_team'] if 'radiant_team' in resp else None
                        ),
                        "dire_team": resp['dire_team'] if 'dire_team' in resp else None,
                        "bans": hero_bans,
                    }
                    for i in range(10):
                        p = resp["players"][i]
                        if p["duration"] < 600:
                            print("under 10 mins: ", m_id)
                            db["dead_games"].insert_one({"id": match_id, "count": 20})
                            ret["dead_games"] = m_id
                            return
                        hero_id = p["hero_id"]
                        if "randomed" in p and p["randomed"] and p["isRadiant"]:
                            rad_draft.append(
                                self.hero_methods.hero_name_from_hero_id(hero_id)
                            )
                        if "randomed" in p and p["randomed"] and not p["isRadiant"]:
                            dire_draft.append(
                                self.hero_methods.hero_name_from_hero_id(hero_id)
                            )

                    parsed_replay = self.parse_replay(
                        unparsed_match_result, resp, testing
                    )
                    if parsed_replay[0]:
                        for dict in parsed_replay[0]:
                            db["heroes"].find_one_and_update(
                                {"id": match_id, "hero": dict['hero']},
                                {"$set": dict},
                                upsert=True,
                            )
                        # try:
                        #     db["non-pro"].insert_many(parsed_replay[1], ordered=False)
                        # except Exception as e:
                        #    # Handle duplicate key errors or other write errors
                        #     pass
                        # db["dead_games"].delete_many({"id": m_id})
                        # print(f"{hero_name} should reach here")
                        # db["heroes"].find_one_and_update(
                        #     {"id": match_id, "hero": hero_name},
                        #     {"$set": match_data},
                        #     upsert=True,
                        # )
                        ret["heroes"] = [unparsed_match_result]

                    if parsed_replay[0]:
                        db["dead_games"].delete_many({"id": m_id})
                        print(
                            f"{self.hero_methods.hero_name_from_hero_id(heroid)} should reach here."
                        )
                    if int(response.headers["X-Rate-Limit-Remaining-Day"]) < 900:
                        return "use_strats"

        except Exception as e:
            print("Unable to get url: ", m_id, traceback.format_exc())
            # ret['dead_games'] = m_id
            pro_item_logger.error(f"Unable to get url: {m_id} {traceback.format_exc()}")
            self.add_to_dead_games(m_id)

    def parse_replay(self, unparsed_match_result, resp, testing):
        non_pro_games = []
        parsed_matches = []
        match_data = None
        m_id = int(resp["match_id"])
        matching_match_ids = list(db['urls'].find({"id": resp['match_id']}))
        try:
            hero_ids = [doc['hero'] for doc in matching_match_ids]
        except KeyError:
            hero_ids = [p['hero_id'] for p in resp['players']]
        added_to_parse = False
        purchase_log_check = all(
            ['purchase_log' in player for player in resp['players']]
        )
        pro_game = any(
            [self.get_info_from_url_db(m_id, "pro", hero_id) for hero_id in hero_ids]
        )
        for i in range(10):
            p = resp["players"][i]
            hero_id = p["hero_id"]
            player_hero = self.hero_methods.hero_name_from_hero_id(hero_id)

            unparsed_match_result = unparsed_match_result | self.unparsed(
                p=p,
                hero_id=hero_id,
                hero_name=player_hero,
                match_id=resp["match_id"],
                testing=testing,
            )
            # ret["parse"] = [{"id": m_id}]
            # check if one of the players matches search
            if not purchase_log_check:
                db["heroes"].find_one_and_update(
                    {
                        "id": m_id,
                        "hero": player_hero,
                    },
                    {"$set": unparsed_match_result},
                    upsert=True,
                )
                if not added_to_parse and not pro_game:
                    print("add to parse: ", m_id, hero_id)
                    self.add_to_dead_games(m_id)
                    db["parse"].find_one_and_update(
                        {"id": m_id}, {"$set": {"id": m_id}}, upsert=True
                    )
                    added_to_parse = True
                continue
            if purchase_log_check:
                roles_arr = [
                    (
                        p["lane"],
                        p["gold_per_min"],
                        p["lane_efficiency"],
                        p["sen_placed"],
                        p["player_slot"],
                        p["is_roaming"],
                        p["lh_t"][9],
                    )
                    for p in resp["players"]
                    if "lane_efficiency" in p and "lane" in p
                ]
                role = self.roles(roles_arr, p["player_slot"])
                # non_pro_games.append(self.insert_non_pro_games(p, hero_id, m_id, role))
                if hero_id not in hero_ids:
                    continue
                parsed_match_result = self.parsed(
                    p=p, hero_name=player_hero, role=role, resp=resp
                )
                match_data = unparsed_match_result | parsed_match_result
                parsed_matches.append(match_data)
        return parsed_matches, non_pro_games

    def unparsed(self, **kwargs):
        p = kwargs["p"]
        abilities = p["ability_upgrades_arr"]
        main_items = [
            {"key": key, "time": 0, "id": p[f"item_{i}"]}
            for i in range(6)
            if p[f"item_{i}"]
            and (key := self.item_methods.get_item_name(p[f"item_{i}"]))
            and "recipe" not in key
        ]
        bp_items = [
            {"key": key, "time": 0, "id": p[f"backpack_{i}"]}
            for i in range(3)
            if p[f"backpack_{i}"]
            and (key := self.item_methods.get_item_name(p[f"backpack_{i}"]))
            and "recipe" not in key
        ]
        aghanims_shard = None
        if "permanent_buffs" in p:
            buffs = p["permanent_buffs"]
            if buffs:
                for buff in buffs:
                    if buff["permanent_buff"] != 12:
                        continue
                    else:
                        temp = {"key": "aghanims_shard", "time": buff["grant_time"]}
                        aghanims_shard = self.item_methods.convert_time([temp])
        elif p["aghanims_shard"] == 1:
            aghanims_shard = [{"key": "aghanims_shard", "time": 0}]

        for k in p["benchmarks"]:
            # round benchmarks to 2 decimal places add 0 to make it same length
            if k != "lhten":
                p["benchmarks"][k][
                    "pct"
                ] = f"{round(p['benchmarks'][k]['pct'] if p['benchmarks'][k]['pct'] else 50, 2):.2f}"
                p["benchmarks"][k]["raw"] = f"{round(p['benchmarks'][k]['raw'], 2):.2f}"

        if p["duration"] > 0:
            p["duration"] = str(datetime.timedelta(seconds=p["duration"]))
        else:
            p["duration"] = 0
        additional_units = p["additional_units"] if "additional_units" in p else None
        if additional_units:
            additional_units = [
                {"key": key, "time": 0, "id": additional_units[0][k]}
                for k in additional_units[0]
                if (key := self.item_methods.get_item_name(additional_units[0][k]))
            ]
        name = self.get_info_from_url_db(
            kwargs["match_id"], "name", kwargs["hero_id"], kwargs["testing"]
        )
        mmr = self.get_info_from_url_db(
            kwargs["match_id"], "mmr", kwargs["hero_id"], kwargs["testing"]
        )
        pro = self.get_info_from_url_db(
            kwargs["match_id"], "pro", kwargs["hero_id"], kwargs["testing"]
        )
        if not mmr:
            pro_item_logger.error(
                f"MMR not found for match {kwargs['match_id']} and hero {kwargs['hero_name']}"
            )
            raise Exception
        unparsed_match_result = {
            # match information
            "hero": kwargs["hero_name"],
            "parsed": False,
            "pro": pro,
            # player information
            "account_id": p["account_id"] if "account_id" in p else None,
            "mmr": mmr,
            "name": (
                name if name else p["personaname"] if 'personaname' in p else 'unknown'
            ),
            # game stats
            "lvl": p["level"],
            "hero_damage": p["hero_damage"],
            "gold": p["total_gold"],
            "tower_damage": p["tower_damage"],
            "gpm": p["gold_per_min"],
            "xpm": p["xp_per_min"],
            "kills": p["kills"],
            "deaths": p["deaths"],
            "assists": p["assists"],
            "last_hits": p["last_hits"],
            "win": p["win"],
            "id": kwargs["match_id"],
            # laning phase stats
            "benchmarks": p["benchmarks"],
            # final items
            "final_items": main_items,
            "backpack": bp_items,
            "additional_units": additional_units,
            "item_neutral": self.item_methods.get_item_name(p["item_neutral"]),
            "aghanims_shard": aghanims_shard,
            "variant": p['hero_variant'],
            "abilities": detailed_ability_info(abilities, kwargs["hero_id"]),
        }
        return unparsed_match_result

    def parsed(self, **kwargs):
        p = kwargs["p"]
        hero_name = kwargs["hero_name"]
        purchase_log = p["purchase_log"]
        role = kwargs["role"]
        resp = kwargs["resp"]
        if p["kills_log"]:
            kills_ten, deaths_ten = self.calulate_kills_at_ten(
                p["kills_log"], hero_name
            )
        else:
            kills_ten = 0
            deaths_ten = 0
        lvl_at_ten = self.calculate_level_at_ten(p["xp_t"][9])
        xpm_at_ten = int(float(p["xp_t"][9] / 10))
        gpm_at_ten = int(float(p["gold_t"][9] / 10))

        starting_items = []
        aghanims_shard = None
        purchase_log = self.item_methods.bots(purchase_log, p["purchase"])
        for purchase in purchase_log:
            purchase["id"] = self.item_methods.get_item_id(purchase["key"])
            if purchase["time"] <= 0:
                starting_items.append(purchase)
            if purchase["key"] == "aghanims_shard":
                temp = purchase.copy()
                aghanims_shard = self.item_methods.convert_time([temp])
        player_randomed = "randomed" in p and p["randomed"]
        starting_items = self.item_methods.clean_items(starting_items, player_randomed)
        rev = purchase_log.copy()[::-1]
        main_items = self.item_methods.get_most_recent_items(rev, 6, p)
        bp_items = self.item_methods.get_most_recent_items(rev, 3, p)
        additional_units = p["additional_units"] if "additional_units" in p else None
        if additional_units:
            additional_units = self.item_methods.get_most_recent_items(
                rev, 6, additional_units[0]
            )
        parsed_match_result = {
            "gold_adv": resp["radiant_gold_adv"][-1],
            "final_items": main_items,
            "backpack": bp_items,
            "additional_units": additional_units,
            "aghanims_shard": aghanims_shard,
            "parsed": "opendota",
            "items": purchase_log,
            "neutral_item_history": p['neutral_item_history'],
            # laning stats
            "starting_items": starting_items,
            "kills_ten": kills_ten,
            "deaths_ten": deaths_ten,
            "lvl_at_ten": lvl_at_ten,
            "role": role,
            "last_hits_ten": p["lh_t"][9],
            "gpm_ten": gpm_at_ten,
            "xpm_ten": xpm_at_ten,
            "lane_efficiency": round(p["lane_efficiency"] * 100, 2),
        }
        return parsed_match_result

    def missing_item(self, item_used, purchase_log):
        purchase_ids = [purchase["id"] for purchase in purchase_log]
        for i, use in enumerate(item_used):
            item_id = use["itemId"]
            if item_id in purchase_ids:
                continue
            item_key = self.item_methods.get_item_name(item_id)
            item_idx = None
            lowest_idx = 9999
            for j in range(len(purchase_ids)):
                filtered = [
                    k
                    for k, u in enumerate(item_used)
                    if purchase_ids[j] == u["itemId"] and k > i
                ]
                if filtered and j < lowest_idx:
                    lowest_idx = filtered[0]
                    print(item_key, filtered)

            for j in range(len(item_used) - 1):
                if item_idx:
                    break
                for k, _id in enumerate(purchase_ids):
                    if j >= i and _id == item_used[j + 1]["itemId"]:
                        item_idx = k
                        break

            # item_idx = [
            #     j
            #     for j, purchase in enumerate(purchase_log)
            #     if purchase["id"] == item_used[j + 1]["itemId"]
            # ]
            if item_idx:
                o = {
                    "key": item_key,
                    "time": purchase_log[item_idx]["time"] - 1,
                    "id": item_id,
                }
                purchase_log.insert(item_idx, o)

    # def add_missing_items(self, p, purchase_log):
    #     for i, timing in enumerate(p["stats"]["inventoryReport"]):
    #         for slot in timing:
    #             item_list = timing[slot]
    #             if not item_list or "neutral" in slot:
    #                 continue
    #             if item_list["itemId"] in [purchase["id"] for purchase in purchase_log]:
    #                 continue
    #             item_key = self.item_methods.get_item_name(item_list["itemId"])
    #             for j, purchase in enumerate(purchase_log):
    #                 if purchase["time"] < (i - 2) * 60:
    #                     continue
    #                 if "recipe" in item_key:
    #                     continue
    #                 previous_purchase_time = purchase_log[j - 1]["time"] - 1
    #                 o = {
    #                     "key": item_key,
    #                     "time": previous_purchase_time,
    #                     "id": item_list["itemId"],
    #                 }
    #                 purchase_log.insert(j, o)
    #                 break

    def add_missing_items(self, invent_report, purchase_log):
        for i, report in enumerate(invent_report):
            report_item_ids = [
                report[slot]["itemId"] for slot in report if report[slot]
            ]
            purchase_log_ids = [purchase["id"] for purchase in purchase_log]
            contains_integer = any(
                item not in purchase_log_ids for item in report_item_ids
            )

            if not contains_integer:
                continue

            for item_slot in report:
                item_dict = report[item_slot]
                if not item_dict:
                    continue
                item_id = item_dict["itemId"]
                if item_id != 41:
                    continue
                timing = (i - 2) * 60
                if item_id in purchase_log_ids:
                    continue
                for j, purchase in enumerate(purchase_log):
                    if purchase["time"] > timing:
                        o = {
                            "key": self.item_methods.get_item_name(item_id),
                            "time": purchase["time"] - 1,
                            "id": item_id,
                        }
                        purchase_log.insert(j, o)
                        break
                        # return purchase
        return purchase_log

    def insert_non_pro_games(
        self, p, hero_id, match_id, role, opendota=True, patch=None
    ):
        hero_name = self.hero_methods.hero_name_from_hero_id(hero_id)

        if opendota:
            purchase_log = self.item_methods.bots(p["purchase_log"], p["purchase"])
        else:
            purchase_log = p["stats"]["itemPurchases"]
            purchase_log = [
                {"id": purchase["itemId"], "key": key, "time": purchase["time"]}
                for purchase in purchase_log
                if "recipe"
                not in (key := self.item_methods.get_item_name(purchase["itemId"]))
            ]
            self.add_missing_items(p['stats']['inventoryReport'], purchase_log)
        starting_items = []
        for purchase in purchase_log:
            purchase["id"] = self.item_methods.get_item_id(purchase["key"])
            if purchase["time"] <= 0:
                starting_items.append(purchase)
            if purchase["key"] == "aghanims_shard":
                temp = purchase.copy()
        if opendota:
            main_items = [
                {"key": key, "time": 0, "id": p[f"item_{i}"]}
                for i in range(6)
                if p[f"item_{i}"]
                and (key := self.item_methods.get_item_name(p[f"item_{i}"]))
                and "recipe" not in key
            ]
            player_randomed = "randomed" in p and p["randomed"]
            starting_items = self.item_methods.clean_items(
                starting_items, player_randomed
            )
            account_name = self.get_info_from_url_db(match_id, "name", hero_name)
            o = {
                "hero": hero_name,
                "name": account_name if account_name else p.personaname,
                "id": match_id,
                "role": role,
                "win": p["win"],
                "patch": self.patch,
                "final_items": main_items,
                "items": purchase_log,
                "starting_items": starting_items,
                "variant": p['hero_variant'],
                "abilities": detailed_ability_info(p["ability_upgrades_arr"], hero_id),
                "item_neutral": self.item_methods.get_item_name(p["item_neutral"]),
                "neutral_item_history": p['neutral_item_history'],
            }
        else:
            main_items = [
                {"key": key, "time": 0, "id": p[f"item{i}Id"]}
                for i in range(6)
                if p[f"item{i}Id"]
                and (key := self.item_methods.get_item_name(p[f"item{i}Id"]))
                and "recipe" not in key
            ]
            starting_items = [
                {
                    "id": value["itemId"],
                    "time": 0,
                    "key": self.item_methods.get_item_name(value["itemId"]),
                }
                for k in p["stats"]["inventoryReport"][0]
                if (value := p["stats"]["inventoryReport"][0][k])
            ]
            o = {
                "hero": hero_name,
                "name": self.get_info_from_url_db(match_id, "name", hero_name),
                "id": match_id,
                "role": role,
                "win": 1 if p["isVictory"] else 0,
                "patch": patch,
                "items": purchase_log,
                "final_items": main_items,
                "starting_items": starting_items,
                "variant": p['variant'],
                "item_neutral": self.item_methods.get_item_name(p["neutral0Id"]),
                "abilities": detailed_ability_info(
                    p["abilities"], hero_id, key="abilityId"
                ),
            }
        # db["non-pro"].find_one_and_update(
        #     {"hero": hero_name, "id": match_id}, {"$set": o}, upsert=True
        # )
        return o
        pass

    def add_to_dead_games(self, m_id, stratz=False):
        dead_game = db["dead_games"].find_one({"id": m_id})
        if dead_game is None:
            return db["dead_games"].find_one_and_update(
                {"id": m_id}, {"$set": {"id": m_id, "count": 0}}, upsert=True
            )
        else:
            db["dead_games"].find_one_and_update({"id": m_id}, {"$inc": {"count": +1}})
        if dead_game["count"] < 20 and not stratz:
            db["parse"].find_one_and_update(
                {"id": m_id}, {"$set": {"id": m_id}}, upsert=True
            )
        if dead_game:
            print(m_id, dead_game)

    def calculate_level_at_ten(self, exp):
        level_table = [
            0,
            230,
            600,
            1080,
            1660,
            2260,
            2980,
            3730,
            4620,
            5550,
            6520,
            7530,
            8580,
        ]
        for i, level in enumerate(level_table):
            if exp > level:
                continue
            return i

    def calulate_kills_at_ten(self, kills_log, hero_name):
        kills = 0
        deaths = 0
        for kill in kills_log:
            if kill["time"] < 600:
                kills += 1
            if hero_name in kill["key"]:
                deaths += 1
        return kills, deaths

    def draft(self, resp, side):
        hero_ids = [player["hero_id"] for player in resp["players"]]
        self.hero_methods = Hero()
        return [
            self.hero_methods.hero_name_from_hero_id(player["hero_id"])
            for player in resp["picks_bans"]
            if player["is_pick"]
            and player["team"] == side
            and player["hero_id"] in hero_ids
        ]

    def roles(self, s, p_slot):
        # use lane_role with lane
        # radiant safe lane is always lane 1 for dire it's lane 3
        # take eff arr top 3 are core then label according to lane
        # convert dire lanes 1 to 3
        # print('sssssss',s,p_slot)
        start = 5
        end = 10
        side = []
        p_roles = []
        is_radiant = False
        if p_slot < 5:
            start = 0
            end = 5
            is_radiant = True
        for i in range(start, end, 1):
            try:
                lane = s[i][0]
            except:
                return None
            if not is_radiant:
                if lane == 1:
                    lane = 3
                elif lane == 3:
                    lane = 1
            sen_placed = s[i][3]
            slot = s[i][4]
            is_roaming = s[i][5]
            lhten = float(s[i][6])
            roles = [lane, sen_placed, slot, is_roaming, lhten]
            p_roles.append(roles)
        side.append(p_roles)
        # print('side',is_radiant,side)
        eff = sorted(side[0], key=lambda x: x[4], reverse=True)
        sen = sorted(side[0], key=lambda x: x[1], reverse=True)
        # print(sen[0][4])
        for i, player in enumerate(eff):
            # print('pro_player slot: ', p_slot, player[4], 'lane: ',player[0], i)
            # print('p', player[0], i)
            role = ""
            lane = player[0]
            slot = player[2]
            is_roaming = player[3]
            if i < 3:
                role = "core"
            if p_slot == sen[0][2] and role != "core":
                return "Hard Support"
            elif p_slot == slot and is_roaming:
                return "Roaming"
            elif p_slot == slot and lane == 2 and role == "core":
                return "Midlane"
            elif lane == 3 and p_slot == slot and role == "core":
                return "Offlane"
            elif p_slot == slot and lane == 1 and role == "core":
                return "Safelane"
            elif lane == 3 and p_slot == slot and role != "core":
                return "Support"
        return "Hard Support"

    def new_roles(self, player_data, p_slot: int):
        # use lane_role with lane
        # radiant safe lane is always lane 1 for dire it's lane 3
        # take eff arr top 3 are core then label according to lane
        # convert dire lanes 1 to 3
        start = 5
        end = 10
        side = []
        p_roles = []
        is_radiant = False
        if p_slot < 5:
            start = 0
            end = 5
            is_radiant = True
        for i in range(start, end, 1):
            try:
                lane = player_data[i][0]
            except:
                return None
            if not is_radiant:
                if lane == 1:
                    lane = 3
                elif lane == 3:
                    lane = 1
            sen_placed = player_data[i][3]
            slot = player_data[i][4]
            is_roaming = player_data[i][5]
            lhten = float(player_data[i][6])
            roles = {
                "lane": lane,
                "sen_placed": sen_placed,
                "slot": slot,
                "is_roaming": is_roaming,
                "lhten": lhten,
            }
            p_roles.append(roles)
        side.append(p_roles)
        # print('side',is_radiant,side)
        lane_efficiency = sorted(side[0], key=lambda x: x["lhten"], reverse=True)
        sentries_bought = sorted(side[0], key=lambda x: x["sen_placed"], reverse=True)
        # print(sen[0][4])
        seen_lanes = set()
        sentry_rank = (
            4 - [k for k, x in enumerate(sentries_bought) if x["slot"] == p_slot][0]
        )
        for i, player in enumerate(lane_efficiency):
            # print('pro_player slot: ', p_slot, player[4], 'lane: ',player[0], i)
            # print('p', player[0], i)
            role = ""
            lane = player["lane"]
            slot = player["slot"]
            is_roaming = player["is_roaming"]
            player_role = ""
            core_lanes = [lane_efficiency[j]["lane"] for j in range(3)]
            player_lane_count = [x for x in core_lanes if x == lane]
            hard_sup_score = 0
            support_score = 0
            roaming_score = 0
            offlane_score = 0
            midlane_score = 0
            safelane_score = 0
            if p_slot != slot:
                continue
            if i < 3 and sentry_rank >= 1:
                role = "core"
            elif i == 3 and sentry_rank <= 1:
                role = "support"
            elif i == 4 and sentry_rank >= 2:
                role = "core"
            print(p_slot, role, sentry_rank)
            if (
                p_slot == sentries_bought[0]["slot"] and role != "core" and lane == 1
            ) or (
                len(player_lane_count) >= 2
                and p_slot == sentries_bought[0]["slot"]
                and lane == 1
            ):
                player_role = "Hard Support"
                seen_lanes.add(player_role)
                return "Hard Support"
            elif is_roaming:
                player_role = "Roaming"
                seen_lanes.add(player_role)

                return "Roaming"
            elif lane == 2:
                player_role = "Midlane"
                seen_lanes.add(player_role)

                return "Midlane"
            elif lane == 1 and role == "core":
                player_role = "Safelane"
                seen_lanes.add(player_role)
                return "Safelane"
            elif lane == 3 and (
                sentries_bought[1]["slot"] == p_slot
                or sentries_bought[0]["slot"] == p_slot
            ):
                player_role = "Support"
                seen_lanes.add(player_role)
                return "Support"
            elif lane == 3:
                player_role = "Offlane"
                seen_lanes.add(player_role)

                return "Offlane"
        return "Hard Support"

    async def opendota_call(self, urls, hero_id, testing=False):
        print(f"{Hero().hero_name_from_hero_id(hero_id)}: {urls}")
        ret = await asyncio.gather(
            *[self.async_get(url, hero_id, testing) for url in urls]
        )
        return ret

    # async def get_acc_ids(self, urls, hero_name):
    #     ret = await asyncio.gather(*[account_id(url, hero_name) for url in urls])

    def get_info_from_url_db(self, m_id, search, hero, testing=False):
        if testing:
            return 0
        try:
            data = hero_urls.find_one(
                {"id": m_id, "$or": [{"hero": hero}, {"heroes": hero}]}
            )
            return data[search]
        except Exception:
            return None

    def lone_druid_bear_items(self, purchase_log, final_items):
        return self.item_methods.get_most_recent_items(purchase_log, 6, final_items)


# asyncio.run(main('x', 'zeus'))
if __name__ == "__main__":
    data = [
        (1, 680, 0.8144704931285368, 0, 0, False, 47),
        (3, 376, 0.40379951495553756, 6, 1, True, 1),
        (2, 545, 0.9763540824575586, 1, 2, False, 54),
        (1, 391, 0.33124494745351657, 6, 3, False, 9),
        (3, 431, 0.5628536782538399, 1, 4, False, 31),
        (3, 528, 0.6493532740501212, 15, 128, False, 33),
        (1, 427, 0.3672190784155214, 5, 129, False, 7),
        (2, 689, 0.7714227970897333, 0, 130, False, 40),
        (1, 569, 0.6154001616814875, 2, 131, False, 29),
        (3, 873, 0.8872271624898949, 0, 132, False, 65),
    ]
    player_slots = [0, 1, 2, 3, 4, 128, 129, 130, 131, 132]
    for slot in player_slots:
        # res = Api_request().roles(data, slot)
        # print(slot, res)
        pass
    ret = Api_request().async_get(7509842608, "puck", testing=True)
