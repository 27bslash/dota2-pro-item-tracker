from functools import reduce
import operator
from pprint import pprint
import statistics
import time


def group_abilities(data):
    abilities = []
    a_count = {}

    for match in data:
        if "abilities" in match and len(match["abilities"]) > 9:
            ability_array = [
                ability["img"]
                for ability in match["abilities"]
                if ability["type"] != "talent"
            ][:9]
            abilities.append(ability_array)

            key = "__".join(
                [
                    ability["img"]
                    for ability in match["abilities"]
                    if ability["type"] != "talent"
                ][:9]
            )
            a_count[key] = a_count.get(key, 0) + 1

    return {"a_count": a_count}


def ability_medians(data):
    abilities = []
    all_abilities = [
        ability["img"]
        for match in data
        for ability in match["abilities"]
        if ability["type"] == "ability"
    ]

    second_occurance = {}
    for match in data:
        d = {}
        for ability in match["abilities"]:
            if ability["type"] != "ability":
                continue
            d[ability["img"]] = (
                {"count": d[ability["img"]]["count"] + 1, "level": ability["level"]}
                if ability["img"] in d
                else {"count": 1, "level": ability["level"]}
            )
            if d[ability["img"]]["count"] == 2:
                if ability["img"] in second_occurance:
                    level_list = second_occurance[ability["img"]]["level"]
                    level_list.append(ability["level"])
                    second_occurance[ability["img"]] = {
                        "count": second_occurance[ability["img"]]["count"] + 1,
                        "level": level_list,
                    }
                else:
                    second_occurance[ability["img"]] = {
                        "count": 1,
                        "level": [ability["level"]],
                    }
    medians = [
        {k: statistics.median(second_occurance[k]["level"])} for k in second_occurance
    ]
    medians = reduce(operator.ior, medians, {})

    # print(count)
    # print(talent_build)
    # ret = fill_abilities(count, talent_build, build_data=build_data)
    return medians


def count_occurences(list):
    count = {}
    for str in list:
        count[str] = count[str] + 1 if str in count else 1
    # type: ignore
    return sorted(count.items(), key=lambda x: x[1], reverse=True)


# def ultimate_ability(data, all_abilities):
#     non_ults = set()
#     min_ult_level = 5 if "meepo" not in all_abilities[0] else 3
#     for ability in [
#         ability
#         for match in data
#         for ability in match["abilities"]
#         if ability["type"] == "ability"
#     ]:
#         # print(ability['img'], ability['level'])
#         d = {}
#         if ability["level"] < min_ult_level:
#             non_ults.add(ability["img"])
#     ult = None
#     ability_count = count_occurences(all_abilities)
#     if len(ability_count) > 3:
#         try:
#             ult = [
#                 ability[0] for ability in ability_count if ability[0] not in non_ults
#             ][0]
#         except Exception as e:
#             ult = ability_count[3][0]
#     return ult


def fill_abilities(count: tuple, talents: list, site_data, build_data):
    spli = count[0].split("__")
    ret = [None for x in range(30)]
    # print(ret)
    # pprint(talents)
    ult = site_data["ultimate_ability"] if "ultimate_ability" in site_data else None

    avoid_levels = [int(list(talent.keys())[0]) - 1 for talent in talents]
    if avoid_levels[-1] > 30:
        avoid_levels[-1] = 24
    max_level = 4
    if "invoker" in spli[0]:
        max_level = 7
    ability_count = count_occurences(spli)
    for i in range(len(spli)):
        ret[i] = spli[i]
    ult_levels = [11, 17] if "meepo" not in spli[0] else [10, 17]
    # try:
    #     if spli[idx] in non_ults:
    #         pass
    # except Exception as e:
    #     spli.insert(idx, ult[0])
    #     ret.insert(idx,  ult[0])
    #     pass
    medians = build_data["abilities"]["ability_medians"]
    for k in medians:
        if k not in count[0]:
            ability_count.append((k, 0))
    for i, idx in enumerate(avoid_levels):
        if ret[idx]:
            spli.insert(idx, talents[i][str(idx + 1)])
            ret.insert(idx, talents[i][str(idx + 1)])
        else:
            ret[idx] = talents[i][str(idx + 1)]

    if ult:
        for idx in ult_levels:
            if ret[idx] and ret[idx] != ult:
                spli.insert(idx, ult)
                ret.insert(idx, ult)
                if not ret[idx + 2]:
                    del ret[idx + 2]
            else:
                ret[idx] = ult

    _i = 0
    ability_count = [
        ability for ability in ability_count if ability[0] in list(medians.keys())
    ]
    while True:
        for i, ability in enumerate(ability_count):
            ability = list(ability)
            if ability[0] not in list(medians.keys()):
                continue
            if (
                ability[1] < max_level
                and ability[0] != ult
                and _i + 1 > medians[ability[0]] - 1
            ):
                if not ret[_i]:
                    ability[1] += 1
                    ability_count[i] = ability  # type: ignore
                    spli.append(ability[0])
                    ret[_i] = ability[0]

        non_ult_count = all(x[1] >= max_level for x in ability_count if x[0] != ult)
        if non_ult_count:
            # print('re', non_ult_count, spli)
            break
        _i += 1
        time.sleep(0.01)
        # try:
        #     if spli[idx] in non_ults:
        #         spli.insert(idx, talents[i][str(idx)])
        #         ret.insert(idx,  talents[i][str(idx)])
        #         pass
        # except Exception as e:
        #     spli.insert(idx, talents[i][str(idx)])
        #     ret.insert(idx,  talents[i][str(idx)])
        #     pass
    # pprint(spli)
    filled_abilities = [{str(i + 1): x} for i, x in enumerate(ret) if x]
    return filled_abilities


def main():
    # talents = [{'15': 'special_bonus_unique_void_spirit_dissimilate_outerring'}, {'16': 'special_bonus_unique_void_spirit_2'}, {
    #     '20': 'special_bonus_unique_void_spirit_4'}, {'25': 'special_bonus_unique_void_spirit_8'}]
    # fill_abilities(('void_spirit_resonant_pulse__void_spirit_aether_remnant__void_spirit_resonant_pulse__void_spirit_aether_remnant__void_spirit_resonant_pulse__void_spirit_astral_step__void_spirit_resonant_pulse__void_spirit_dissimilate__void_spirit_dissimilate__void_spirit_dissimilate', 14),
    #                talents, 'void_spirit_astral_step')
    pass


if __name__ == "__main__":
    # t()
    pass
