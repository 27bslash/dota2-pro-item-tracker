import datetime
import json
import time
from collections import Counter, OrderedDict
from operator import itemgetter

from .database.collection import item_ids


class Items:
    def __init__(self):
        # item_lst = db['all_items']
        self.item_lst = item_ids

    def pro_items(self, match_data):
        item_lst = []
        sd = []
        data = match_data
        black_lst = [
            "ward_sentry",
            "ward_observer",
            "clarity",
            "tpscroll",
            "enchanted_mango",
            "smoke_of_deceit",
            "tango",
            "faerie_fire",
            "tome_of_knowledge",
            "healing_salve",
            None,
        ]
        item_lst = [
            item["key"]
            for x in data
            for item in x["final_items"]
            if item not in black_lst
        ]
        counter = dict(Counter(item_lst))
        sd = dict(sorted(counter.items(), key=itemgetter(1), reverse=True))
        return sd

    def get_item_name(self, item_id) -> str:
        data = self.item_lst
        if data:
            item = [item["name"] for item in data if item_id == item["id"]]
            if item:
                return item[0]

    def get_item_id(self, item_name):
        data = self.item_lst
        for item in data:
            if item_name == item["name"]:
                # print(item_name)
                return item["id"]
        print(item_name)
        # return [item['id'] for item in data['items'] if item_name == item['name']][0]

    def convert_time(self, lst):
        for item in lst:
            if item["time"] > 0:
                item["time"] = str(datetime.timedelta(seconds=item["time"]))
            else:
                item["time"] = 0
        return lst

    def get_most_recent_items(self, purchase_log, l: int, p, opendota=True):
        done = set()
        output = []
        for j in range(l):
            if l == 6:
                if opendota:
                    item_str = "item_" + str(j)
                else:
                    item_str = f"item{j}Id"
            else:
                if opendota:
                    item_str = "backpack_" + str(j)
                else:
                    item_str = f"backpack{j}Id"
            item = self.get_item_name(p[item_str])
            if not item:
                continue
            for purchase in purchase_log:
                if purchase["key"] == item and purchase["key"] not in done:
                    if len(output) < 10:
                        done.add(purchase["key"])
                        output.append(
                            {
                                "key": item,
                                "time": purchase["time"],
                                "id": self.get_item_id(purchase["key"]),
                            }
                        )
        return self.convert_time(sort_dict(output))

    def remove_buildup_items(self, starting_items, randomed):
        item_lst = [
            "bracer",
            "null_talisman",
            "wraith_band",
            "ring_of_basilius",
            "buckler",
            "headress",
            "magic_wand",
        ]
        build_up = [
            {"key": "magic_wand", "items": ["branches", "branches", "magic_stick"]},
            {"key": "wraith_band", "items": ["circlet", "slippers"]},
            {"key": "null_talisman", "items": ["circlet", "mantle"]},
            {"key": "bracer", "items": ["circlet", "gauntlets"]},
            {"key": "ring_of_basilius", "items": ["sobi_mask"]},
            {"key": "buckler", "items": ["ring_of_protection"]},
            {"key": "headdress", "items": ["ring_of_regen"]},
        ]
        if randomed:
            starting_items = starting_items[2:]
        for item in starting_items:
            item_idx = find_index(build_up, item["key"])
            if not item_idx:
                continue
            items = build_up[item_idx]["items"]
            for buildup_item in items:
                matching_idx = find_index(starting_items, buildup_item)
                if matching_idx:
                    del starting_items[matching_idx]
        return starting_items

    def bots(self, purchase_log, purchase):
        bots_recipes = {
            "recipe_travel_boots": "travel_boots",
            "recipe_travel_boots_2": "travel_boots_2",
        }
        search_key = self.extract_key(purchase, bots_recipes)
        # print(purchase_log)
        for dic in purchase_log[::-1]:
            if dic["key"] == search_key[0] and search_key[0] is not None:
                bots_time = dic["time"]
                if search_key[1] == 1:
                    bots_time = int(bots_time) - 60
                else:
                    bots_time = int(bots_time) + 60
                bots_entry = {"time": bots_time, "key": search_key[2]}
                purchase_log.append(bots_entry)
        return purchase_log

    def extract_key(self, purchase, bots_recipes):
        search_key = None
        nxt = 0
        boots = None
        for key in list(purchase.keys())[::-1]:
            if key in bots_recipes.keys():
                try:
                    search_key = list(purchase)[list(purchase).index(key) + 1]
                    nxt = 1
                except:
                    search_key = list(purchase)[list(purchase).index(key) - 1]
                    nxt = -1
                boots = bots_recipes[key]
                if purchase[key] > 1:
                    search_key = list(purchase.keys())[-1]
                    nxt = -1
                    boots = "travel_boots_2"
        return (search_key, nxt, boots)

    def item_charges(self, starting_items):
        max_charges = 1
        temp = []
        for i, item in enumerate(starting_items):
            temp.append(item)
            if item["key"] == "tango":
                max_charges = 3
            if "charges" in item:
                for _ in range(1, round(item["charges"] / max_charges)):
                    temp.insert(i, {"key": item["key"], "time": item["time"]})
        return temp

    def clean_items(self, starting_items, randomed):
        starting_items = self.remove_buildup_items(starting_items, randomed=randomed)
        return sort_dict(self.item_charges(starting_items))


def find_index(lst, value):
    for i, dic in enumerate(lst):
        if dic["key"] == value:
            return i
    return None


def sort_dict(items):
    newlist = sorted(items, key=itemgetter("time"))
    return newlist
