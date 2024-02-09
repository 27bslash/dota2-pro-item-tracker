from .database.collection import db, hero_stats
import traceback
from collections import Counter
import json
import re
from .abilities import extract_special_values


class Talents:
    def count_talents(self, data):
        # print(data)
        try:
            talents = [
                ability["img"]
                for item in data
                for ability in item["abilities"]
                if "special_bonus" in ability["img"]
            ]
            return dict(Counter(talents))
        except Exception as e:
            print("y", traceback.format_exc())

    def get_talent_order(self, match_data, hero):
        all_talents = []
        count = self.count_talents(match_data)
        if count is None:
            return False
        talents = [doc for doc in hero_stats if doc["hero"] == hero][0]
        for x in talents["talents"]:
            talent = talents["talents"][x]
            d = {}
            d["img"] = talent["name"]
            d["key"] = extract_special_values(talent)
            d["id"] = talent["id"]
            d["type"] = "talent"
            d["slot"] = talent["slot"]
            d["talent_count"] = count[talent["name"]] if talent["name"] in count else 0
            all_talents.append(d)
        level = 10
        for i in range(0, 8, 2):
            if i < 8:
                picks = (
                    all_talents[i]["talent_count"] + all_talents[i + 1]["talent_count"]
                )
                all_talents[i]["total_pick_count"] = picks
                all_talents[i + 1]["total_pick_count"] = picks
                all_talents[i]["level"] = level
                all_talents[i + 1]["level"] = level
                level += 5
        return list(reversed(all_talents))
