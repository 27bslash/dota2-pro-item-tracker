import json
from pprint import pprint
import re

import requests

from update.update_items import create_item_description, update_item_attributes
from helper_funcs.helper_imports import db, switcher


extraStrings = {
    "DOTA_ABILITY_BEHAVIOR_NONE": "None",
    "DOTA_ABILITY_BEHAVIOR_PASSIVE": "Passive",
    "DOTA_ABILITY_BEHAVIOR_UNIT_TARGET": "Unit Target",
    "DOTA_ABILITY_BEHAVIOR_CHANNELLED": "Channeled",
    "DOTA_ABILITY_BEHAVIOR_POINT": "Point Target",
    "DOTA_ABILITY_BEHAVIOR_ROOT_DISABLES": "Root",
    "DOTA_ABILITY_BEHAVIOR_AOE": "AOE",
    "DOTA_ABILITY_BEHAVIOR_NO_TARGET": "No Target",
    "DOTA_ABILITY_BEHAVIOR_AUTOCAST": "Autocast",
    "DOTA_ABILITY_BEHAVIOR_ATTACK": "Attack Modifier",
    "DOTA_ABILITY_BEHAVIOR_IMMEDIATE": "Instant Cast",
    "DOTA_ABILITY_BEHAVIOR_HIDDEN": "Hidden",
    "DAMAGE_TYPE_PHYSICAL": "Physical",
    "DAMAGE_TYPE_MAGICAL": "Magical",
    "DAMAGE_TYPE_PURE": "Pure",
    "SPELL_IMMUNITY_ENEMIES_YES": "Yes",
    "SPELL_IMMUNITY_ENEMIES_NO": "No",
    "SPELL_IMMUNITY_ALLIES_YES": "Yes",
    "SPELL_IMMUNITY_ALLIES_NO": "No",
    "SPELL_DISPELLABLE_YES": "Yes",
    "SPELL_DISPELLABLE_NO": "No",
    "DOTA_UNIT_TARGET_TEAM_BOTH": "Both",
    "DOTA_UNIT_TARGET_TEAM_ENEMY": "Enemy",
    "DOTA_UNIT_TARGET_TEAM_FRIENDLY": "Friendly",
    "DOTA_UNIT_TARGET_HERO": "Hero",
    "DOTA_UNIT_TARGET_BASIC": "Basic",
    "DOTA_UNIT_TARGET_BUILDING": "Building",
    "DOTA_UNIT_TARGET_TREE": "Tree",
}

ignoreStrings = set(
    [
        "DOTA_ABILITY_BEHAVIOR_ROOT_DISABLES",
        "DOTA_ABILITY_BEHAVIOR_DONT_RESUME_ATTACK",
        "DOTA_ABILITY_BEHAVIOR_DONT_RESUME_MOVEMENT",
        "DOTA_ABILITY_BEHAVIOR_IGNORE_BACKSWING",
        "DOTA_ABILITY_BEHAVIOR_TOGGLE",
        "DOTA_ABILITY_BEHAVIOR_IGNORE_PSEUDO_QUEUE",
        "DOTA_ABILITY_BEHAVIOR_SHOW_IN_GUIDES",
    ]
)

badNames = set(
    [
        "Version",
        "npc_dota_hero_base",
        "npc_dota_hero_target_dummy",
        "npc_dota_units_base",
        "npc_dota_thinker",
        "npc_dota_companion",
        "npc_dota_loadout_generic",
        "npc_dota_techies_remote_mine",
        "npc_dota_treant_life_bomb",
        "npc_dota_lich_ice_spire",
        "npc_dota_mutation_pocket_roshan",
        "npc_dota_scout_hawk",
        "npc_dota_greater_hawk",
    ]
)

extraAttribKeys = [
    "AbilityCastRange",
    "AbilityChargeRestoreTime",
    "AbilityDuration",
    "AbilityChannelTime",
    "AbilityCastPoint",
    "AbilityCharges",
    "AbilityManaCost",
    "AbilityCooldown",
]

# Use standardized names for base attributes
generatedHeaders = {
    "abilitycastrange": "CAST RANGE",
    "abilitycastpoint": "CAST TIME",
    "abilitycharges": "MAX CHARGES",
    "max_charges": "MAX CHARGES",
    "abilitychargerestoretime": "CHARGE RESTORE TIME",
    "charge_restore_time": "CHARGE RESTORE TIME",
    "abilityduration": "DURATION",
    "abilitychanneltime": "CHANNEL TIME",
}


# Already formatted for mc and cd
excludeAttributes = set(["abilitymanacost", "abilitycooldown"])

# Some attributes we remap, so keep track of them if there's dupes
remapAttributes = {
    "abilitychargerestoretime": "charge_restore_time",
    "abilitycharges": "max_charges",
}

notAbilities = set(
    ["Version", "ability_base", "default_attack", "attribute_bonus", "ability_deward"]
)

itemQualOverrides = {
    "fluffy_hat": "component",
    "ring_of_health": "secret_shop",
    "void_stone": "secret_shop",
    "overwhelming_blink": "artifact",
    "swift_blink": "artifact",
    "arcane_blink": "artifact",
    "moon_shard": "common",
    "aghanims_shard": "consumable",
    "kaya": "artifact",
    "helm_of_the_dominator": "common",
    "helm_of_the_overlord": "common",
    "desolator": "epic",
    "mask_of_madness": "common",
    "orb_of_corrosion": "common",
    "falcon_blade": "common",
    "mage_slayer": "artifact",
    "revenants_brooch": "epic",
}


def parse_text():
    with open("update/test_files/test.txt", "r") as f:
        parse_text_content(f.read())
        # for line in f:
        #     if '//' in line:
        #         continue
        #     print(line)


def contains_any(string, substrings):
    return any(substring in string for substring in substrings)


def parse_text_content(content: str):
    item_data = {}
    current_key = None
    # print(content)
    # Split the content into lines and process each line
    lines = content.split("\n")
    # for i, line in enumerate(lines):
    #     if line.strip() == "{":
    #         lines[i - 1] = lines[i - 1].strip() + "{"
    #     pass
    ret = []
    for i, line in enumerate(lines):
        # Split each line into key and value
        parsed_line = parse_line(line, ret)
        if parsed_line == "break":
            break
        elif not parsed_line:
            continue
        # parts = line.split('"')
        # if len(parts) >= 4:
        #     key = parts[1].strip()
        #     value = parts[3].strip()
        # elif len(parts) >= 3:
        #     key = parts[1].strip()
        # else:
        #     continue
        #     # print(key, value)
        #     # Handle nested keys
        # if key.endswith("{"):
        #     current_key = key[:-1].strip()
        #     item_data[current_key] = {}
        # elif key.endswith("}"):
        #     current_key = None
        # else:
        #     # Add key-value pair to the dictionary
        #     if current_key:
        #         item_data[current_key][key] = value
        #     else:
        #         item_data[key] = value
        # else:
        #     for key in parts:
        #         if key and key.strip() not in ["{", "}", ","]:
        #             print(i, parts)
    joined = "".join(ret)
    joined = re.sub(r'""', '","', joined)
    joined = re.sub(r'}"', '},"', joined)
    wrapped = f"{{{joined}}}"
    # pprint(ret)
    json_data = json.loads(wrapped)
    return json_data


def parse_line(line, ret):
    bad_keys = ["ItemAliases"]
    if "//" in line:
        return False

    if "ItemAliases" in line:
        return False
    # remove spaces between quotes leave data untouched
    line = re.sub(r"\s+(?=\W+)", "", line)
    line = re.sub(r'""', '":"', line)
    line = re.sub(r':""', f"0", line)
    line = re.sub(r"\t", "", line)
    line = line.strip()
    parts = "".join(
        [f'"{x}"' if x not in [":", "{", "}"] else x for x in line.split('"') if x]
    )
    parts = re.sub(r'""', '":"', parts)
    parts = re.sub(r"\\\'", "twat", parts)
    parts = re.sub(r'=":"', '="', parts)
    if parts == "{":
        parts = ":{"

    ret.append(parts)
    return ret


def test_line():
    line = '"DOTA_Tooltip_ability_ad_scepter_grant"      "Scepter grants new ability: <font color="#ffffff"><b>%s1</b></font>"'
    line = '"DOTA_Tooltip_ability_necronomicon_archer_mana_burn_Description"                                 "Launches an arrow that burns away the targeted unit\'s mana, dealing damage equal to the amount of mana burned."'
    parsed_line = parse_line(line, ret=[])
    joined = "".join(parsed_line)
    json_line = f"{{{joined}}}"

    try:
        json.loads(json_line)
    except Exception as e:
        e_dict = vars(e)
        pos = e_dict["pos"]
        split = [*json_line]
        print(split[pos])
        split[pos] = ""
        joined = "".join(split)
        json_ = json.loads(joined)
        print(json_)


# parsed_data = parse_text_content(text_content)
def gen_ability_json(content: str):
    d = {"lang": {"Language": "English", "Tokens": {}}}
    lines = content.split("\n")

    for line in lines:
        # line = re.sub(r"\s+(?=\W+)", "", line)
        line = re.sub(r"//.*", "", line)

        # if (
        #     "description" not in line.lower()
        #     and "lore" not in line.lower()
        #     and "note" not in line.lower()
        # ):
        #     line = re.sub(r"\s+", "", line)
        key = re.search(r"\"\w+\"", line)
        if key:
            key = key.group(0)
            value = line.replace(key, "")
            key = key.replace('"', "")
            key = key.strip()
            key = key.lower()
            value = value.replace('"', "")
            value = value.strip()
            if key and value:
                d["lang"]["Tokens"][key] = value
    return d


def generate_opendota_items():
    item_ids, neutral_items, datamined_items, datamined_abilities = fetch_data()
    odota_items = {}
    for key in datamined_items["DOTAAbilities"]:
        final_key = key.replace("item_", "")
        if key == "Version":
            continue
        if "recipe" in key:
            continue
        item_stats = datamined_items["DOTAAbilities"][key]
        if "IsObsolete" in item_stats and item_stats["IsObsolete"] == "1":
            continue
        filled_out_item_stats = fill_out_item_stats(
            datamined_abilities['lang']['Tokens'], datamined_items, item_ids, neutral_items, key
        )
        if filled_out_item_stats:
            odota_items[final_key] = filled_out_item_stats
        # pprint(dic, indent=4)
    # with open("update/test_files/final_items.json", "w") as f:
    #     json.dump(dic, f, indent=4)
    return odota_items
    db["all_items"].find_one_and_update(
        {}, {"$set": {"items": odota_items}}, upsert=True
    )


def fill_out_item_stats(
    datamined_abilities, datamined_items, item_ids, neutral_items, key
):
    dic = {}
    if f"dota_tooltip_ability_{key}" not in datamined_abilities:
        return False
    clean_name = datamined_abilities[f"dota_tooltip_ability_{key}"]
    dic["dname"] = clean_name
    description_keys = [k for k in datamined_abilities if f"{key}_description" in k]
    lore_keys = [k for k in datamined_abilities if f"{key}_lore" in k]
    notes_keys = [k for k in datamined_abilities if f"{key}_note" in k]
    # initialize default values
    dic["mc"] = False
    dic["cd"] = False
    dic["attrib"] = []
    dic["notes"] = ""
    if description_keys:
        unparsed_descriptions = [datamined_abilities[key] for key in description_keys]
        description = create_item_description(
            unparsed_descriptions, datamined_items, key
        )
        # print('desc: ',datamined_abilities[desciption_key[0]])
        dic["hint"] = description
    if lore_keys:
        lore = ("\n").join([datamined_abilities[k] for k in lore_keys])
        dic["lore"] = lore
        # print('lore: ',datamined_abilities[lore_key[0]])
    if notes_keys:
        notes = ("\n").join([datamined_abilities[k] for k in notes_keys])
        dic["notes"] = notes
        # print('notes: ',datamined_abilities[notes_key[0]])
    attributes = update_item_attributes(datamined_items, datamined_abilities, key)
    dic["attrib"] = attributes
    # print(key, dic)
    datamined_key = datamined_items["DOTAAbilities"][key]
    dic["id"] = int(item_ids["DOTAAbilityIDs"]["ItemAbilities"]["Locked"][key])

    if "AbilityManaCost" in datamined_key:
        dic["mc"] = list(map(float, datamined_key["AbilityManaCost"].split(" ")))
    if "AbilityCooldown" in datamined_key:
        dic["cd"] = list(map(float, datamined_key["AbilityCooldown"].split(" ")))
    if "ItemQuality" in datamined_key:
        dic["qual"] = datamined_key["ItemQuality"]
    if "ItemCost" in datamined_key:
        dic["cost"] = int(datamined_key["ItemCost"])
    if "ItemInitialCharges" in datamined_key:
        dic["charges"] = True
    if (
        "ItemIsNeutralDrop" in datamined_key
        and datamined_key["ItemIsNeutralDrop"] == "1"
    ):
        dic["tier"] = int(get_neutral_item_tier(key, neutral_items))
    components = get_item_components(key, datamined_items)
    if components:
        dic["components"] = components
    return dic
    # print(key, 'attributes: ',attributes)


def get_item_components(key: str, datamined_items):
    if f"item_recipe_{key.replace('item_','')}" in datamined_items["DOTAAbilities"]:
        item_recipe = datamined_items["DOTAAbilities"][
            f"item_recipe_{key.replace('item_','')}"
        ]
        if "ItemRequirements" in item_recipe:
            item_requirements = item_recipe["ItemRequirements"]
            comp = [item_requirements[k] for k in item_requirements]
            return clean_components_list(comp)


def clean_components_list(comp):
    seen_items = []
    for i, item_list in enumerate(comp):
        splt = item_list.split(";")
        comp[i] = [re.sub(r"\W+", "", item).replace("item_", "") for item in splt]
    for items in zip(*comp):
        if all(x == items[0] for x in items):
            seen_items.append(items[0])
        else:
            for item in items:
                seen_items.append(item)
    return seen_items


def get_neutral_item_tier(key: str, data) -> str:
    for tier in data["neutral_items"]:
        for item in data["neutral_items"][tier]["items"]:
            if item == key:
                return tier
    return "0"
    pass


def parse_items(text_file, json_file):
    with open(text_file, "r") as f:
        ret = parse_text_content(f.read())
    with open(json_file, "w") as f:
        json.dump(ret, f, indent=4)


def fetch_data():
    item_ids = requests.get(
        "https://raw.githubusercontent.com/dotabuff/d2vpkr/master/dota/scripts/npc/npc_ability_ids.txt"
    ).text
    neutral_tiers = requests.get(
        "https://raw.githubusercontent.com/dotabuff/d2vpkr/master/dota/scripts/npc/neutral_items.txt"
    ).text
    item_data = requests.get(
        "https://raw.githubusercontent.com/dotabuff/d2vpkr/master/dota/scripts/npc/items.txt"
    ).text
    all_abilities = requests.get(
        "https://raw.githubusercontent.com/dotabuff/d2vpkr/master/dota/resource/localization/abilities_english.txt"
    ).text

    item_ids_json = parse_text_content(item_ids)
    neutral_tiers_json = parse_text_content(neutral_tiers)
    item_data_json = parse_text_content(item_data)
    all_abilities_json = gen_ability_json(all_abilities)
    return item_ids_json, neutral_tiers_json, item_data_json, all_abilities_json
    pass


if __name__ == "__main__":
    # parse_text()
    # update_abilities()
    # s = """{"key":"Launches an arrow that burns away the targeted unit\\'s mana, dealing damage equal to the amount of mana burned."}"""
    # try:
    #     json.loads(s)
    # except Exception as e:
    #     e_dict=vars(e)
    #     pos = e_dict["pos"]
    #     split = [*s]
    #     split[pos] = ''
    #     joined=''.join(split)
    #     json_ = json.loads(joined)
    #     print(json_)

    # text_file = "update/test_files/item_data.txt"
    # json_file = "update/test_files/item_data.json"
    # parse_items(text_file, json_file)
    # text_file = "update/test_files/neutral.txt"
    # json_file = "update/test_files/neutral.json"
    # parse_items(text_file, json_file)
    # text_file = "update/test_files/item_ids.txt"
    # json_file = "update/test_files/item_ids.json"
    # parse_items(text_file, json_file)
    # json_from_test()

    generate_opendota_items()
    # test_line()
    pass
