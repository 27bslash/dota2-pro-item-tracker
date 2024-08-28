import re
import time
import traceback
from typing import List
from pymongo import UpdateMany, UpdateOne
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from seleniumbase import SB, BaseCase
from thefuzz import fuzz
from helper_funcs.database.collection import hero_list, hero_stats, db
from helper_funcs.switcher import switcher


def update_facets(ability_json):
    hero_facets = []
    for i, facet in enumerate(ability_json["facets"]):
        facet_found = False
        facet["notes"] = facet_notes(ability_json, i)
        facet_ability = ability_json['facet_abilities'][i]['abilities']
        if facet_ability:
            ability_facet_desc = facet_ability[0]["desc_loc"]
            facet["description_loc"]
            facet_desc = facet_values(facet_ability[0], facet["description_loc"])
            facet["ability"] = facet_ability[0]["id"]
            facet["ability_loc"] = " ".join(
                facet_values(facet_ability[0], ability_facet_desc)
            )
            hero_facets.append(facet)
            facet_found = True
        else:
            for ability in ability_json["abilities"]:
                if "facets_loc" in ability and ability["facets_loc"][i]:
                    try:
                        ability_facet_desc = ability["facets_loc"][i]
                        facet["ability"] = ability["id"]
                        facet["ability_loc"] = " ".join(
                            facet_values(ability, ability_facet_desc)
                        )
                        hero_facets.append(facet)
                        facet_found = True
                        break
                    except Exception:
                        print(traceback.format_exc(), facet_desc)
                        pass
        if not facet_found:
            hero_facets.append(facet)
    return hero_facets


def add_deprecated_facets(hero_list, facets_json):
    updates = []
    for hero_idx, hero in enumerate(hero_list):
        for j, facet_key in enumerate(
            facets_json['all_hero_facets'][hero_idx]['Facets']
        ):
            if (
                "Deprecated"
                in facets_json['all_hero_facets'][hero_idx]['Facets'][facet_key]
            ):
                individual_stats = [x for x in hero_stats if x['hero'] == hero['name']][
                    0
                ]
                facets = individual_stats['facets']
                facets.insert(
                    j, facets_json['all_hero_facets'][hero_idx]['Facets'][facet_key]
                )
                update_op = UpdateOne(
                    {'hero': hero['name']}, {'$set': {'facets': facets}}
                )
                updates.append(update_op)
    db['hero_stats'].bulk_write(updates)
    return updates


def update_facet_colours(patch: str) -> None:
    sorted_heroes = sorted(hero_list, key=lambda k: k["name"])

    with SB() as sb:
        try:
            sb: BaseCase = sb
            xpath = "//div[contains(@style, 'ripple')]"
            hero_xpath = "//a[contains(@href, '/hero/')]"
            "//a[contains(@href, '/hero/')]/..//div[contains(@style, 'ripple')]"
            # //div[contains(@style, 'ripple')]/following-sibling::div
            sb.get(f"https://www.dota2.com/patches/{patch}")
            time.sleep(3)
            hero_notes: List[WebElement] = sb.find_elements(
                by=xpath, selector="//a[contains(@href, '/hero/')]/.."
            )
            facet_updates = []
            for el in hero_notes:
                hero_link: WebElement = el.find_element(
                    By.XPATH, ".//a[contains(@href, '/hero/')]"
                )
                if not hero_link:
                    continue
                facet_filters = el.find_elements(
                    By.XPATH, ".//div[contains(@style, 'ripple')]"
                )
                f = [x.value_of_css_property("filter") for x in facet_filters]
                hero_name = re.search(
                    r"(?<=\/hero\/).*", hero_link.get_attribute("href")
                ).group()
                best_score = 0
                h_name = None
                for hero in sorted_heroes:
                    ratio = fuzz.ratio(
                        hero_name, switcher(hero["name"]).replace("_", "")
                    )
                    if ratio == 100:
                        h_name = hero["name"]
                        best_score = ratio
                        break
                    if ratio > best_score:
                        best_score = ratio
                        h_name = hero["name"]
                if best_score != 100:
                    print(f, hero_name, h_name, best_score)
                if not f:
                    continue
                for doc in hero_stats:
                    if doc["hero"] == h_name and f:
                        for i in range(len(f)):
                            facet_text = (
                                facet_filters[i]
                                .find_element(By.XPATH, "./..")
                                .text.lower()
                            )
                            facet_content_text = (
                                facet_filters[i]
                                .find_element(By.XPATH, "./../following-sibling::div")
                                .text.lower()
                            )
                            if 'facet removed' in facet_content_text.lower():
                                print('fct', h_name, facet_content_text)
                                continue
                            target_facet = [
                                fac
                                for fac in doc['facets']
                                if fac['title_loc'].lower() == facet_text
                            ][0]
                            target_facet["filter"] = f[i]
                        facet_updates.append(
                            UpdateMany(
                                {"hero": doc["hero"]},
                                {"$set": {"facets": doc["facets"]}},
                            )
                        )
        except Exception as e:
            print(e, h_name)
            sb.driver.quit()
        db["hero_stats"].bulk_write(facet_updates)


def facet_notes(ability_json, i):
    facet_notes = None
    if "facet_abilities" in ability_json:
        facet_abilities = ability_json["facet_abilities"][i]["abilities"]
        if facet_abilities:
            facet_ability = facet_abilities[0]
            facet_notes = [
                " ".join(facet_values(facet_ability, entry))
                for entry in facet_ability["notes_loc"]
            ]
    return facet_notes


def facet_values(ability, facet):
    facet_desc = []
    for string in facet.split(" "):
        if "%" in string:
            facet_desc.append(extract_facet_values(ability["special_values"], string))
        else:
            facet_desc.append(string)
    return facet_desc


def extract_facet_values(special_values: list, target_ability: str) -> str:
    clean_ability = re.search(r"%(\w+)%", target_ability).group(1)
    for value in special_values:
        name = value["name"]
        try:
            if name == clean_ability or name == clean_ability.replace('bonus_', ''):
                val = (
                    value["facet_bonus"]["values"]
                    if value["facet_bonus"]["values"]
                    else value["values_float"]
                )
                perc = ""
                if "%%%" in target_ability:
                    perc = "%"
                str_list = [str(v) for v in val]
                return f"{'/'.join(str_list)}{perc}"
        except Exception:
            pass
    return target_ability


if __name__ == '__main__':
    special_values = [
        {
            "bonuses": [],
            "facet_bonus": {"name": "", "operation": 0, "values": []},
            "heading_loc": "",
            "is_percentage": False,
            "name": "buyback_penalty",
            "required_facet": "",
            "values_float": [15],
            "values_scepter": [],
            "values_shard": [],
        },
        {
            "bonuses": [],
            "facet_bonus": {"name": "", "operation": 0, "values": []},
            "heading_loc": "",
            "is_percentage": False,
            "name": "item_sellback_percent",
            "required_facet": "",
            "values_float": [90],
            "values_scepter": [],
            "values_shard": [],
        },
        {
            "bonuses": [],
            "facet_bonus": {"name": "", "operation": 0, "values": []},
            "heading_loc": "",
            "is_percentage": False,
            "name": "AbilityCastRange",
            "required_facet": "",
            "values_float": [0],
            "values_scepter": [],
            "values_shard": [],
        },
        {
            "bonuses": [],
            "facet_bonus": {"name": "", "operation": 0, "values": []},
            "heading_loc": "",
            "is_percentage": False,
            "name": "AbilityChannelTime",
            "required_facet": "",
            "values_float": [0],
            "values_scepter": [],
            "values_shard": [],
        },
        {
            "bonuses": [],
            "facet_bonus": {"name": "", "operation": 0, "values": []},
            "heading_loc": "",
            "is_percentage": False,
            "name": "AbilityDuration",
            "required_facet": "",
            "values_float": [0],
            "values_scepter": [],
            "values_shard": [],
        },
        {
            "bonuses": [],
            "facet_bonus": {"name": "", "operation": 0, "values": []},
            "heading_loc": "",
            "is_percentage": False,
            "name": "AbilityCastPoint",
            "required_facet": "",
            "values_float": [0],
            "values_scepter": [],
            "values_shard": [],
        },
        {
            "bonuses": [],
            "facet_bonus": {"name": "", "operation": 0, "values": []},
            "heading_loc": "",
            "is_percentage": False,
            "name": "AbilityCharges",
            "required_facet": "",
            "values_float": [0],
            "values_scepter": [],
            "values_shard": [],
        },
        {
            "bonuses": [],
            "facet_bonus": {"name": "", "operation": 0, "values": []},
            "heading_loc": "",
            "is_percentage": False,
            "name": "AbilityChargeRestoreTime",
            "required_facet": "",
            "values_float": [0],
            "values_scepter": [],
            "values_shard": [],
        },
        {
            "bonuses": [],
            "facet_bonus": {"name": "", "operation": 0, "values": []},
            "heading_loc": "",
            "is_percentage": False,
            "name": "AbilityManaCost",
            "required_facet": "",
            "values_float": [0],
            "values_scepter": [],
            "values_shard": [],
        },
        {
            "bonuses": [],
            "facet_bonus": {"name": "", "operation": 0, "values": []},
            "heading_loc": "",
            "is_percentage": False,
            "name": "AbilityCooldown",
            "required_facet": "",
            "values_float": [0],
            "values_scepter": [],
            "values_shard": [],
        },
    ]
    ret = extract_facet_values(
        special_values=special_values, target_ability='%bonus_item_sellback_percent%%%'
    )
    print(ret)
