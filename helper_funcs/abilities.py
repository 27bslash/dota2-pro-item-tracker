import json
import time
import traceback
from helper_funcs.hero import Hero
from helper_funcs.database.collection import hero_stats
import re


hero_methods = Hero()
# def get_hero_name_from_ability(ability_list):
#     for ability in ability_list:
#         with open('json_files/stratz_abilities.json', 'r') as f:
#             data = json.load(f)
#             if 'uri' in data[str(ability)]:
#                 return data[str(ability)]['uri']


def convert_special_values(key, file):
    for k in file:
        values_int = file[0]["values_int"]
        values_float = file[0]["values_float"]
        if len(values_int) == 0:
            values_int = 0
        else:
            values_int = values_int[0]
        if len(values_float) == 0:
            values_float = 0
        else:
            values_float = round(values_float[0], 2) * 1
        special_value = values_int + values_float
        key = key.replace("{s:value}", str(special_value))
        return key


def detailed_ability_info(ability_list, hero_id, key=None):
    """takes a list of ability ids and a hero id and generates more info returns updated ability list"""
    output = []
    if key:
        ability_list = [ability[key] for ability in ability_list]
    talents = []
    hero_name = hero_methods.hero_name_from_hero_id(hero_id)
    st_count = 0
    temp_st_count = 0
    gap = 0
    data = [doc for doc in hero_stats if doc["hero"] == hero_name][0]
    # data = db['hero_stats'].find_one({'hero': hero_name})
    abilities = data["abilities"]
    talents = data["talents"]
    hero_abilities = {**abilities, **talents}
    for i, _id in enumerate(ability_list):
        _id = convert_for_kez(str(_id))
        if int(_id) == 730:
            # print(i,gap)
            st_count += 1
            temp_st_count += 1
            continue
        elif _id in hero_abilities:
            try:
                d = {}
                d["img"] = hero_abilities[_id]["name"]
                d["key"] = hero_abilities[_id]["name_loc"]
                d["id"] = _id

                if _id in talents:
                    d["type"] = "talent"
                    d["key"] = extract_special_values(hero_abilities[_id])
                    for k in talents:
                        if _id == k:
                            d["slot"] = talents[k]["slot"]
                            break
                else:
                    d["type"] = "ability"
                if hero_id != 74:
                    gap = skill_gap(gap, _id, temp_st_count, st_count, i + 1, d["type"])
                d["level"] = i + 1 + gap
                output.append(d)
                if hero_id != 74:
                    # invoker edge case
                    output = output[slice(0, 19)]
            except Exception as e:
                print(_id, traceback.format_exc())
    return output


def skill_gap(gap, _id, temp_st_count, st_count, level, type):
    if level + gap == 17:
        if temp_st_count == 0:
            gap += 1
        else:
            temp_st_count -= 1
    if level + gap == 19:
        if temp_st_count == 0:
            gap += 1
        else:
            temp_st_count -= 1
    if level + gap == 20:
        pass
    if level + gap > 20:
        if type == "talent" and st_count > 0:
            gap += 25 - level
        if 25 - level + gap == temp_st_count:
            if type == "talent":
                gap += temp_st_count
        if st_count == 0:
            gap += 4
    return gap


def extract_special_values(talent):
    regex = r"{s:value}"
    val = ""
    for lst in talent["special_values"]:
        if len(lst["values_float"]) > 0:
            val = round(lst["values_float"][0], 2) * 1
        else:
            val = lst["values_int"][0]
    return talent["name_loc"].replace(regex, str(val))


def convert_for_kez(key: str):
    # d = {
    #     "kez_falcon_rush": "kez_echo_slash",
    #     "kez_talon_toss": "kez_grappling_claw",
    #     "kex_shodo_sai": "kez_kazurai_katana",
    #     "kez_ravens_veil": "kez_raptor_dance",
    # }
    d = {
        "1502": "1498",
        "1503": "1499",
        "1504": "1500",
        "1506": "1501",
    }
    try:
        return d[key]
    except Exception:
        return key


ab_arr = [
    # jugg start stats
    [
        5297,
        5299,
        5297,
        5298,
        5300,
        5297,
        5298,
        5298,
        5298,
        5996,
        5297,
        5300,
        5299,
        5299,
        5299,
        6661,
        5300,
        6064,
    ]
]
# no stats
if __name__ == "__main__":
    # insert_player_picks()
    # get_hero_name('jakiro')
    # get_id('lih')
    # get_talent_order('jakiro')
    for lst in ab_arr:
        detailed_ability_info(lst, 64)

    # loop_test()
    # parse_request()
    pass
