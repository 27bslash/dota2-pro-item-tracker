import re
import time
import traceback
from datetime import datetime

import requests
from helper_funcs.database.collection import db, hero_output
from helper_funcs.database.collection import hero_list as backup_hero_list


class Db_insert:
    def __init__(self, hero_list: list = [], update_trends: bool = False):
        self.update_trends = update_trends
        self.hero_list = hero_list if hero_list else backup_hero_list
        self.updated_version = False
        pass

    def insert_player_picks(self):
        data = db["account_ids"].find({})
        print("inserting player picks")
        for player in data:
            if re.search(r"\(smurf.*\)", player["name"], re.IGNORECASE):
                continue
            self.insert_total_picks("name", player["name"], "player_picks")

    @staticmethod
    def insert_total_picks(key, val, collection):
        regex = r"(\W)"
        subst = "\\\\\\1"
        v = re.sub(regex, subst, val)
        regex = f"{v}"
        regex = {"$regex": regex}
        roles = {
            "Safelane": hero_output.count_documents({key: regex, "role": "Safelane"}),
            "Midlane": hero_output.count_documents({key: regex, "role": "Midlane"}),
            "Offlane": hero_output.count_documents({key: regex, "role": "Offlane"}),
            "Support": hero_output.count_documents({key: regex, "role": "Support"}),
            "Roaming": hero_output.count_documents({key: regex, "role": "Roaming"}),
            "Hard Support": hero_output.count_documents(
                {key: regex, "role": "Hard Support"}
            ),
        }
        roles = {
            k: v
            for k, v in sorted(roles.items(), key=lambda item: item[1], reverse=True)
        }
        for k in list(roles.keys()):
            if roles[k] <= 0:
                del roles[k]
        cleaned = re.sub(r"\(smurf.*\)", "", val, re.IGNORECASE).strip()
        if cleaned == "y'":
            print(val, cleaned, roles)

            pass
        if key == "bans":
            db[collection].find_one_and_update(
                {"hero": val},
                {"$set": {"total_bans": hero_output.count_documents({key: val})}},
                upsert=True,
            )
            pass
        else:
            db[collection].find_one_and_replace(
                {key: cleaned},
                {
                    key: cleaned,
                    "total_picks": hero_output.count_documents({key: regex}),
                    "roles": roles,
                },
                upsert=True,
            )
            pass

    @staticmethod
    def insert_bans(val):
        db["hero_picks"].find_one_and_replace(
            {"hero": val},
            {"total_bans": hero_output.count_documents({"bans": val})},
            upsert=True,
        )

    # def insert_talent_order(self, hero_id):
    #     hero_methods = Hero()
    #     hero = hero_methods.hero_name_from_hero_id(hero_id)
    #     data_talents = db['hero_stats'].find_one(
    #         {'hero': hero})['talents']
    #     talents = [detailed_ability_info(
    #         [_id], hero_id)[0] for _id in data_talents]
    #     db['talents'].find_one_and_update(
    #         {'hero': hero}, {'$set': {'talents': talents}}, upsert=True)

    def insert_best_games(self):
        print("INSERT BEST GAMES")
        start = time.perf_counter()
        db["best_games"].delete_many({})

        for hero in self.hero_list:
            roles = [
                "Hard Support",
                "Roaming",
                "Support",
                "Offlane",
                "Midlane",
                "Safelane",
            ]
            # for hero in hero_data['heroes']:
            data = hero_output.find({"hero": hero["name"]})
            sd = sorted(self.sum_benchmarks(data), key=lambda k: k["sum"], reverse=True)
            self.add_best_games_to_db(sd, hero["name"], None)
            for role in roles:
                data = hero_output.find({"hero": hero["name"], "role": role})
                queried = self.sum_benchmarks(data)
                sd = sorted(queried, key=lambda k: k["sum"], reverse=True)
                self.add_best_games_to_db(sd, hero["name"], role)

    @staticmethod
    def sum_benchmarks(data):
        current_highest = 0
        benchmarks = []
        for match in data:
            dic = {}
            summed_benchmarks = 0
            if "benchmarks" in match:
                for k in match["benchmarks"]:
                    percentile = match["benchmarks"][k]["pct"]
                    # print(k, match['benchmarks'][k]['pct'])
                    if k != "lhten":
                        summed_benchmarks += float(percentile)
                    # print(match['id'], sum_benchmarks)
                dic["id"] = match["id"]
                dic["sum"] = summed_benchmarks
                benchmarks.append(dic)
                if summed_benchmarks >= current_highest:
                    current_highest = summed_benchmarks
        return benchmarks

    @staticmethod
    def add_best_games_to_db(data, hero, display_role):
        if len(data) < 2:
            return
        for match in data[slice(0, 2)]:
            # print(match)
            base = hero_output.find_one({"hero": hero, "id": match["id"]})
            if not base:
                print("no hero doc")
                return
            benchmarks = base["benchmarks"]
            player = base["name"]
            db["best_games"].insert_one(
                {
                    "id": match["id"],
                    "hero": hero,
                    "name": base["name"],
                    "role": base["role"],
                    "display_role": display_role,
                    "benchmarks": base["benchmarks"],
                }
            )

    def insert_worst_games(self):
        data = hero_output.find({})
        # db['chappie'].delete_many({})
        roles = ["Midlane", "Safelane", "Offlane"]
        data = list(data)
        for i, doc in enumerate(data):
            if doc["win"] == 1:
                continue
            items = [item["key"] for item in doc["final_items"]]
            times = [item["time"] for item in doc["final_items"]]
            if "shadow_amulet" not in items:
                continue
            duration = doc["duration"]
            if type(duration) == str:
                duration = self.convert_to_seconds(doc["duration"])
            amulet_time = self.get_time(items, times, "shadow_amulet")
            if "blink" in items:
                blink_time = self.get_time(items, times, "blink")
                if abs(blink_time - amulet_time) < 60:
                    db["chappie"].find_one_and_update(
                        {"hero": doc["hero"], "id": doc["id"]},
                        {"$set": {"data": doc}},
                        upsert=True,
                    )
            if items.index("shadow_amulet") != 5:
                continue
            if (
                "shadow_amulet" in items
                and len(items) < 3
                or "shadow_amulet" in items
                and "role" in doc
                and doc["role"] in roles
                and duration - amulet_time > 120
                or "shadow_amulet" in items
                and len(items) == 1
                or len(items) == 0
            ):
                db["chappie"].find_one_and_update(
                    {"hero": doc["hero"], "id": doc["id"]},
                    {"$set": {"data": doc}},
                    upsert=True,
                )

    def get_time(self, items: list, times: list, item_name: str):
        item_idx = items.index(item_name)
        if times[item_idx] == 0:
            times[item_idx] = "00:00:00"
        item_datetime = datetime.strptime(times[item_idx], "%H:%M:%S").time()
        return self.convert_to_seconds(item_datetime)

    @staticmethod
    def convert_to_seconds(time):
        time = str(time)
        hours = time.split(":")[0]
        minutes = time.split(":")[1]
        seconds = time.split(":")[2]
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

    def detailed(self, collection):
        output = []
        current_patch = db["current_patch"].find_one()
        req = requests.get(
            "https://www.dota2.com/datafeed/patchnoteslist?language=english"
        ).json()
        new_patch = req["patches"][-1]
        patch = new_patch["patch_number"]
        for i, hero_dict in enumerate(self.hero_list):
            if re.search(r"\(smurf.*\)", hero_dict["name"], re.IGNORECASE):
                continue
            hero_name = hero_dict["name"]
            print(f"{i} / {len(self.hero_list)} {hero_name}")
            self.insert_hero_pickstats(collection, patch, hero_name)

    def insert_hero_pickstats(self, collection: str, patch: str, hero_name):
        role_dict = self.total_picks(patch, hero_name)
        role_dict = self.insert_roles_pick_stats(hero_name, role_dict, patch)
        if self.update_trends:
            trends = self.insert_pickrate_trends(hero_name, role_dict)
            role_dict["trends"] = trends
        else:
            role_dict["trends"] = db[collection].find_one({"hero": hero_name})["trends"]
        old_role_dict = db[collection].find_one({"hero": hero_name}, {"_id": 0})
        old_hash = hash(str(old_role_dict))
        new_hash = hash(str(role_dict))
        if old_hash != new_hash and not self.updated_version:
            version = db[collection].find_one({"version": {"$exists": True}})
            if version:
                new_version = version["version"] + 1
                db[collection].find_one_and_replace(
                    {"version": version}, {"version": new_version}
                )
            else:
                db[collection].insert_one({"version": 0})
            self.updated_version = True
            # if old_hash != new_hash:
            #     version = db[collection].find_one({"hero": hero_name})['version']
            #     if version:
            #         version = version["version"] + 1
            #     else:
            #         version = 0
            #     role_dict['version'] = version

        db[collection].find_one_and_replace({"hero": hero_name}, role_dict, upsert=True)

    def total_picks(self, patch: str, hero_name: str):
        # regex = r"(\W)"
        # subst = "\\\\\\1"
        # v = re.sub(regex, subst, hero_name)
        # regex = f"{v}"
        # regex = {"$regex": regex}
        # cleaned = re.sub(r"\(smurf.*\)", "", hero_name, re.IGNORECASE).strip()
        picks = hero_output.count_documents({"hero": hero_name})
        total_wins = hero_output.count_documents({"hero": hero_name, "win": 1})
        total_bans = hero_output.count_documents({"bans": hero_name})
        patch_picks = hero_output.count_documents({"hero": hero_name, "patch": patch})
        patch_total_wins = hero_output.count_documents(
            {"hero": hero_name, "win": 1, "patch": patch}
        )
        if total_wins == 0 or picks == 0:
            total_winrate = 0
        else:
            total_winrate = (total_wins / picks) * 100
            total_winrate = self.clean_winrate(total_winrate)
        role_dict = {
            "hero": hero_name,
            "patch": patch,
            "patch_picks": patch_picks,
            "patch_wins": patch_total_wins,
            "picks": picks,
            "wins": total_wins,
            "winrate": total_winrate,
            "bans": total_bans,
        }

        return role_dict

    def insert_roles_pick_stats(self, hero_name, role_dict, patch):
        roles = ["Hard Support", "Support", "Safelane", "Offlane", "Midlane", "Roaming"]
        for role in roles:
            wins = hero_output.count_documents(
                {
                    "hero": hero_name,
                    "win": 1,
                    "role": role,
                }
            )
            losses = hero_output.count_documents(
                {"hero": hero_name, "win": 0, "role": role}
            )
            patch_wins = hero_output.count_documents(
                {"hero": hero_name, "win": 1, "role": role, "patch": patch}
            )
            patch_losses = hero_output.count_documents(
                {"hero": hero_name, "win": 0, "role": role, "patch": patch}
            )
            role_picks = wins + losses
            patch_role_picks = patch_wins + patch_losses
            if role_picks == 0:
                winrate = 0
            else:
                winrate = wins / role_picks * 100
                winrate = self.clean_winrate(winrate)
                role_dict[role] = {
                    "picks": role_picks,
                    "wins": wins,
                    "losses": losses,
                    "patch_picks": patch_role_picks,
                    "patch_wins": patch_wins,
                    "patch_losses": patch_losses,
                    "winrate": winrate,
                }
        return role_dict

    def insert_winrates(self, key):
        start = time.perf_counter()
        print("insert winrate...")
        output = []
        roles = ["Hard Support", "Support", "Safelane", "Offlane", "Midlane", "Roaming"]

        for hero in self.hero_list:
            picks = hero_output.count_documents({key: hero["name"]})
            total_wins = hero_output.count_documents(
                {key: hero["name"], "$or": [{"win": 1}, {"win": True}]}
            )
            total_bans = hero_output.count_documents({"bans": hero["name"]})
            if total_wins == 0 or picks == 0:
                total_winrate = 0
            else:
                total_winrate = (total_wins / picks) * 100
                total_winrate = self.clean_winrate(total_winrate)
            role_dict = {
                key: hero["name"],
                "picks": picks,
                "wins": total_wins,
                "bans": total_bans,
            }
            for role in roles:
                wins = hero_output.count_documents(
                    {
                        key: hero["name"],
                        "$or": [{"win": 1}, {"win": True}],
                        "role": role,
                    }
                )
                losses = hero_output.count_documents(
                    {
                        key: hero["name"],
                        "$or": [{"win": 0}, {"win": False}],
                        "role": role,
                    }
                )
                if picks == 0:
                    winrate = 0
                else:
                    winrate = wins / picks * 100
                    winrate = self.clean_winrate(winrate)
                    if wins + losses > 0:
                        role_dict[f"{role}_picks"] = wins + losses
                        # role_dict[f"{role}_winrate"] = winrate
                    if wins:
                        role_dict[f"{role}_wins"] = wins
                    elif losses:
                        role_dict[f"{role}_losses"] = losses
            if role_dict:
                output.append(role_dict)
            db["wins"].find_one_and_replace({key: hero["name"]}, role_dict, upsert=True)
        print("time taken insert_winrate: ", time.perf_counter() - start)

    @staticmethod
    def clean_winrate(winrate):
        winrate = f"{winrate:.2f}"
        winrate = f"{float(winrate):g}"
        winrate = float(winrate) if "." in winrate else int(winrate)
        return winrate

    @staticmethod
    def insert_pickrate_trends(hero, role_dict):
        threshold_length = 7
        # Use the Aggregation Framework to push a value to the beginning of the array and remove entries if array length is greater than a threshold
        pipeline = [
            {"$match": {"hero": hero}},
            {
                "$project": {
                    "trends": {
                        "$concatArrays": [
                            [role_dict],
                            {
                                "$cond": {
                                    "if": {
                                        "$gte": [
                                            {"$size": "$trends"},
                                            threshold_length,
                                        ]
                                    },
                                    "then": {
                                        "$slice": ["$trends", threshold_length - 1]
                                    },
                                    "else": "$trends",
                                }
                            },
                        ]
                    }
                }
            },
        ]

        result = list(db["test_hero_picks"].aggregate(pipeline))
        return result[0]["trends"]
        # db["t_hero_picks"].find_one_and_update(
        #     {"hero": hero}, {"$set": {"trends": result[0]["trends"]}}, upsert=True
        # )

    def insert_all(self):
        # print("insert worst games")
        # self.insert_worst_games()
        # print("insert best games")

        # self.insert_best_games()
        print("insert hero picks")
        self.detailed(collection="test_hero_picks")
        print("insert player picks")
        self.insert_player_picks()
        # self.insert_winrates("hero")


if __name__ == "__main__":
    # Db_insert.insert_talent_order('self', 1)
    strt = time.perf_counter()
    # Db_insert().detailed("test_hero_picks")
    # Db_insert().insert_roles_pick_stats("viper", {}, "7.35b")

    Db_insert().insert_all()
    # print(picks ,patch_wins,losses)
    # db["test_hero_picks"].update_many({}, {"$set": {"trends": []}})
    # for _ in range(0, 7):
    #     Db_insert(update_trends=True).detailed("hero", "test_hero_picks")
    role_dict = {
        "Hard Support_picks": 1,
        "Hard Support_wins": 4,
        "Offlane_picks": 3,
        "Offlane_wins": 1,
        "Support_picks": 1,
        "Support_wins": 1,
        "bans": 73,
        "hero": "elder_titan",
        "picks": 15,
        "wins": 6,
    }
    # Db_insert().insert_pickrate_trends("jakiro", role_dict)
    print(time.perf_counter() - strt)
