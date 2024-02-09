import json
import re

import requests

from helper_funcs.helper_imports import *


def update_item_ids():
    items = db["all_items"].find_one({})
    if not items:
        return
    item_ids = {"items": []}
    for item in items["items"]:
        _id = items["items"][item]["id"]
        item_ids["items"].append({"name": item, "id": int(_id)})
    req = requests.get("https://www.dota2.com/datafeed/itemlist?language=english")
    json_items = req.json()["result"]["data"]["itemabilities"]
    cleaned_items = [
        {
            "name": re.sub("item_", "", item["name"]),
            "id": item["id"],
            "tier": item["neutral_item_tier"],
        }
        for item in json_items
    ]
    db["item_ids"].find_one_and_update(
        {}, {"$set": {"items": cleaned_items}}, upsert=True
    )


def update_basic_id_json(input_collection, output_collection, dic_name):
    dictionary = {dic_name: []}
    data = db[input_collection].find_one({}, {"_id": 0})
    if not data:
        return
    for _id in data:
        dictionary[dic_name].append(
            {"name": data[_id]["shortName"], "id": data[_id]["id"]}
        )
    db[output_collection].find_one_and_update({}, {"$set": dictionary}, upsert=True)


def create_item_description(desc:list, datamined_items, key:str):
    # datamined_items_url = 'https://raw.githubusercontent.com/dotabuff/d2vpkr/master/dota/scripts/npc/items.json'
    # datamined_items = json.loads(requests.get(datamined_items_url).text)

    # desc = ["Active: Swift Blink Teleport to a target point up to %blink_range%%% units away.After teleportation, you gain %bonus_movement%%% phased movement speed and +%bonus_agi_active% Agility for %duration% seconds. Swift Blink cannot be used for %blink_damage_cooldown% seconds after taking damage from an enemy hero or Roshan."]
    res = []
    generic_mods = ["AbilityCastRange", "AbilityChannelTime", "AbilityDuration"]
    lowercase_mods = [mod.lower() for mod in generic_mods]

    if key == "item_force_staff":
        pass
    for string in desc:
        string = re.sub(r"(?<=[a-z!])([A-Z]\S)", "-- \\1", string, 1)
        if not re.search("--", string):
            string = re.sub(r"([A-Z][a-z]+\s(?=[a-z0-9%]))", "-- \\1", string, 1)
        # re.sub('(?<=[a-z])(?<!^)[A-Z]', r' \1', s
        item = datamined_items["DOTAAbilities"][key]
        if "AbilitySpecial" in item:
            special_values = item["AbilitySpecial"]
        hint_vals = re.findall(r"(?<=%)\w+_?(?=%)", string)

        for word in hint_vals:
            if word.lower() in lowercase_mods:
                idx = lowercase_mods.index(word.lower())
                try:
                    item_atrib = item[generic_mods[idx]]
                except:
                    item_atrib = item["AbilityValues"][generic_mods[idx]]
                if item_atrib:
                    string = re.sub(rf"%+{word}%+", item_atrib, string)
            if "AbilityValues" in item:
                special_values = item["AbilityValues"]
                lowercase_vals = [val.lower() for val in item["AbilityValues"]]
                if word and word.lower() in lowercase_vals:
                    word_idx = lowercase_vals.index(word)
                    d_key = list(item["AbilityValues"])[word_idx]
                    repl = (
                        special_values[d_key]
                        if type(special_values[d_key]) == str
                        else special_values[d_key]["value"]
                    )
                    string = re.sub(rf"%+{word}%?%", repl, string)
        res.append(string)
    return res if res else desc


def update_item_attributes( datamined_items, all_abilities, key):
    # desc = ["Active: Swift Blink Teleport to a target point up to %blink_range%%% units away.After teleportation, you gain %bonus_movement%%% phased movement speed and +%bonus_agi_active% Agility for %duration% seconds. Swift Blink cannot be used for %blink_damage_cooldown% seconds after taking damage from an enemy hero or Roshan."]
    # abilityValues = {"blink_range": "1200",
    #                  "blink_damage_cooldown": "3.0",
    #                  "blink_range_clamp": "960",
    #                  "bonus_agility": "25",
    #                  "bonus_movement": "40",
    #                  "bonus_agi_active": "35",
    #                  "duration": "6"}

    #   "key": "bonus_attack_speed",
    # "header": "+",
    # "value": "35",
    # "footer": "Attack Speed"

    # "item_silver_edge": {
    #   "ID": "249",
    #   "AbilityBehavior": "DOTA_ABILITY_BEHAVIOR_IMMEDIATE | DOTA_ABILITY_BEHAVIOR_NO_TARGET | DOTA_ABILITY_BEHAVIOR_IGNORE_CHANNEL",
    #   "FightRecapLevel": "1",
    #   "AbilityCooldown": "20.0",
    #   "AbilitySharedCooldown": "shadow_blade",
    #   "AbilityManaCost": "75",
    #   "ItemCost": "5450",
    #   "ItemShopTags": "damage;attack_speed;movespeed;hard_to_tag",
    #   "ItemQuality": "epic",
    #   "ItemAliases": "sb;invis;shadow blade",
    #   "ItemDeclarations": "DECLARE_PURCHASES_TO_TEAMMATES | DECLARE_PURCHASES_IN_SPEECH | DECLARE_PURCHASES_TO_SPECTATORS",
    #   "ShouldBeSuggested": "1",
    #   "AbilityValues": {
    #     "bonus_damage": "52",
    #     "bonus_attack_speed": "35",
    #     "bonus_strength": "0",
    #     "bonus_intellect": "0",
    #     "bonus_mana_regen": "0",
    #     "windwalk_duration": "14.0",
    #     "windwalk_movement_speed": "25",
    #     "windwalk_fade_time": "0.3",
    #     "windwalk_bonus_damage": "175",
    #     "backstab_duration": "4",
    #     "crit_chance": "30",
    #     "crit_multiplier": "160",
    #     "tooltip_crit_damage": "60"
    #   }
    # }

    if key == "item_force_staff":
        pass
    attributes = []
    attrib_dict = {}
    try:
        item = datamined_items["DOTAAbilities"][key]
    except Exception as e:
        print(key)
        return
    if not "AbilityValues" in item:
        return
    abilityValues = item["AbilityValues"]
    try:
        desc = all_abilities[f"DOTA_Tooltip_ability_{key}_Description"]
        hint_vals = re.findall(r"(?<=%)\w+_?(?=%)", desc)
    except KeyError as e:
        hint_vals = []
        pass
    attrib = [val for val in abilityValues if val not in hint_vals]
    # joined = ''.join(desc)

    for stat in attrib:
        # string = re.sub(
        #     fr"%+{stat}%+", item[generic_mods[idx]], string)
        value = abilityValues[stat]
        if value == "0":
            continue
        converted = convert_variables(key, stat, all_abilities)
        if not converted:
            continue
        if is_percentage(key, stat, all_abilities):
            value += "%"

        footer = converted
        symbol = "+" if not re.search(r"-", value) else "-"
        attrib_dict = {
            "key": stat,
            "header": symbol,
            "value": value,
            "footer": footer,
        }
        attributes.append(attrib_dict)
    return attributes


def convert_variables(key, stat, all_abilities):
    str = f"dota_tooltip_ability_item_{key.replace('item_', '')}_{stat}"
    if str in all_abilities and all_abilities[str]:
        stat_string = all_abilities[str]
        if re.search(r"\$", stat_string):
            stat_string = re.sub(r"[%+$]", "", stat_string)
            var_str = f"dota_ability_variable_{stat_string}"
            return all_abilities[var_str]
        else:
            return re.sub(r"[+-]", "", all_abilities[str])
    else:
        return None
    pass


def is_percentage(key, stat, all_abilities):
    all_abilities_url = "https://raw.githubusercontent.com/dotabuff/d2vpkr/master/dota/resource/localization/abilities_english.json"
    # all_abilities = json.loads(requests.get(all_abilities_url).text)[
    #     'lang']['Tokens']
    # t = {re.sub('DOTA_Tooltip_Ability_', 'DOTA_Tooltip_ability_', k): v
    #      for k, v in all_abilities.items() if 'DOTA_Tooltip_Ability_' in k}
    "dota_tooltip_ability_item_swift_blink_bonus_agility"
    "dota_tooltip_ability_item_swift_blink_bonus_agility"
    str = f"dota_tooltip_ability_item_{key}_{stat}"
    # print(all_abilities)
    stat = all_abilities[str] if str in all_abilities else None
    if stat and re.search(r"^%", stat):
        return True
    return False


def odota_items(odota_items, datamined_items, all_abilities):
    for k in odota_items:
        item = odota_items[k]

        # if 'satanic' not in k:
        #     continue
        hint = []
        if "hint" in item:
            hint = item["hint"]
            desc = create_item_description(hint, datamined_items, f"item_{k}")
            odota_items[k]["description"] = desc

        attributes = update_item_attributes(
            hint, datamined_items, all_abilities, f"item_{k}"
        )
        # print(k, attributes)
        if attributes:
            odota_items[k]["attrib"] = attributes

    # db["all_items"].find_one_and_update(
    #     {}, {"$set": {"items": odota_items}}, upsert=True
    # )


def update_json_data():
    odota_abilites_url = "https://api.opendota.com/api/constants/abilities"
    odota_abilities = json.loads(requests.get(odota_abilites_url).text)
    ab_url = "https://raw.githubusercontent.com/dotabuff/d2vpkr/master/dota/scripts/npc/npc_abilities.json"
    datamined_abilities = json.loads(requests.get(ab_url).text)
    all_abilities_url = "https://raw.githubusercontent.com/dotabuff/d2vpkr/master/dota/resource/localization/abilities_english.json"
    all_abilities = json.loads(requests.get(all_abilities_url).text)["lang"]["Tokens"]
    all_abilities = {
        re.sub("DOTA_Tooltip_Ability_", "DOTA_Tooltip_ability_", k): v
        for k, v in all_abilities.items()
    }

    odota_items_url = "https://api.opendota.com/api/constants/items"
    odota_items_json = json.loads(requests.get(odota_items_url).text)
    datamined_items_url = "https://raw.githubusercontent.com/dotabuff/d2vpkr/master/dota/scripts/npc/items.json"
    with open("update/jft.json", "r") as f:
        datamined_abilities = json.load(f)
        # datamined_items = json.loads(requests.get(datamined_items_url).text)
    with open("update/test_result.json", "r") as f:
        datamined_items = json.load(f)
    odota_items(odota_items_json, datamined_items, datamined_abilities)

if __name__ == '__main__':
    update_json_data()