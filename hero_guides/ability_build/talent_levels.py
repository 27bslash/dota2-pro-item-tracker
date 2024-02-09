from collections import Counter
import statistics
from helper_funcs.talents import Talents
from helper_funcs.database.collection import db
import re


def most_used_talents(match_data, hero):
    # talent_methods = Talents()
    # talents = talent_methods.get_talent_order(match_data, hero)
    # print(talents)
    count = {}
    # talents = [(ability['img'], ability['level'])
    #            for match in match_data for ability in match['abilities'] if ability['type'] == 'talent']
    # print(talents)
    talents = []
    # hero_talents = db['hero_stats'].find_one({'hero': hero})
    # if hero_talents:
    #     hero_talents = hero_talents['talents']
    #     t = [x['name'] for x in hero_talents]
    for match in match_data:
        for ability in match["abilities"]:
            if ability["type"] == "talent":
                if ability["level"] > 30:
                    ability["level"] = 25
                talents.append((ability["img"], ability["level"], ability["slot"]))
    talent_level_lookup_table = talent_levels(talents)
    for talent in talents:

        # print(talent,count)
        # m = re.search(
        #     r"special_bonus_unique_earthshaker$", talent[0])
        # if m:
        #     print(talent,count)
        level = lookup_talent_level(talent_level_lookup_table, talent[0])
        if talent[0] in count:
            count[talent[0]] = {
                "level": level,
                "count": count[talent[0]]["count"] + 1,
                "slot": talent[2],
            }
        else:
            count[talent[0]] = {"level": level, "count": 1, "slot": talent[2]}

    srt = sorted(count.items(), key=lambda x: x[1]["slot"])
    # print(srt)
    # for i in range(0, 7):
    #     try:
    #         slot = srt[i][1]['slot']
    #         if i != slot:
    #             srt.insert(i, ('null', {'level': 0, 'count': 0, 'slot': i}))
    #     except:
    #         pass

    # pairs = []
    # for i in range(0, len(srt), 2):
    #     pair = srt[i:i+2]

    #     pairs.append(pair)
    # for i, pair in enumerate(pairs):
    #     min_count_pair = min(pair, key=lambda x: x[1]['count'])
    #     total_count = sum([x[1]['count'] for x in pair])
    #     if len(pair) > 1:
    #         pair.remove(min_count_pair)
    #         if total_count == 0:
    #             total_count = 1
    #         perc = (pair[0][1]['count'] / total_count) * 100
    #         pair[0][1]['perc'] = round(perc, 2)
    #         pairs[i] = pair[0]
    #     else:
    #         pair[0][1]['perc'] = 100
    #         pairs[i] = pair[0]
    return filter_talents(srt)
    # count = dict(Counter(talents))
    # print(count)
    # return count


def talent_levels(talents):
    ret = []
    checked_talents = set()
    for talent in talents:
        talent_name = talent[0]
        same_talents = []
        if talent_name in checked_talents:
            continue
        for other in talents:
            if other[0] == talent_name:
                same_talents.append(other)
                checked_talents.add(talent_name)
        isolated_levels = [l[1] for l in same_talents]
        most_common_level = statistics.mode(isolated_levels)

        ret.append({"talent": talent_name, "level": most_common_level})
    return ret


def lookup_talent_level(talents, talent_name):
    for talent_dict in talents:
        if talent_dict["talent"] == talent_name:
            return talent_dict["level"]


def filter_talents(data):
    ret = []
    for i in range(0, 7, 2):
        pair = None
        total_count = sum(
            [x[1]["count"] for x in data if x[1]["slot"] == i or x[1]["slot"] == i + 1]
        )
        for x in data:
            if x[1]["slot"] == i or x[1]["slot"] == i + 1:
                perc = (x[1]["count"] / total_count) * 100
                x[1]["perc"] = round(perc, 2)
                if perc >= 50:
                    pair = x
                # pair = x
                # max = x[1]['count']
        if pair:
            ret.append(pair)
    # print(ret)
    return ret


# ('special_bonus_unique_void_spirit_2', {'level': 13.453333333333333, 'count': 75, 'slot': 1, 'perc': 87.21})
if __name__ == "__main__":
    data = [
        ("special_bonus_attack_damage_20", {"level": 10.125, "count": 8, "slot": 0}),
        (
            "special_bonus_unique_lina_1",
            {"level": 11.826086956521738, "count": 23, "slot": 1},
        ),
        ("special_bonus_hp_250", {"level": 15.0, "count": 4, "slot": 2}),
        ("special_bonus_hp_275", {"level": 15.0, "count": 2, "slot": 2}),
        (
            "special_bonus_unique_lina_3",
            {"level": 15.047619047619047, "count": 21, "slot": 3},
        ),
        ("special_bonus_spell_amplify_11", {"level": 20.0, "count": 16, "slot": 4}),
        ("special_bonus_unique_lina_2", {"level": 20.0, "count": 4, "slot": 5}),
        ("special_bonus_unique_lina_6", {"level": 25.0, "count": 1, "slot": 6}),
        ("special_bonus_unique_lina_7", {"level": 25.0, "count": 8, "slot": 7}),
    ]
    res = filter_talents(data)
    print(res)
