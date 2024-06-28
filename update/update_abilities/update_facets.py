import re
import time
import traceback
from typing import List
from pymongo import UpdateMany
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from seleniumbase import SB, BaseCase
from thefuzz import fuzz
from helper_funcs.database.collection import hero_list, hero_stats
from helper_funcs.switcher import switcher


def update_facets(ability_json):
    hero_facets = []
    for i, facet in enumerate(ability_json["facets"]):
        facet_found = False
        facet["notes"] = facet_notes(ability_json, i)
        for ability in ability_json["abilities"]:
            if "facets_loc" in ability and ability["facets_loc"][i]:
                try:
                    ability_facet_desc = ability["facets_loc"][i]

                    facet["description_loc"]
                    facet_desc = facet_values(ability, facet["description_loc"])
                    facet["ability"] = ability["id"]
                    facet["ability_loc"] = " ".join(
                        facet_values(ability, ability_facet_desc)
                    )
                    hero_facets.append(facet)
                    facet_found = True
                    break
                except Exception as e:
                    print(traceback.format_exc(), facet_desc)
                    pass
        if not facet_found:
            hero_facets.append(facet)
    return hero_facets


def update_facet_colours():
    sorted_heroes = sorted(hero_list, key=lambda k: k["name"])

    with SB() as sb:
        sb: BaseCase = sb
        xpath = "//div[contains(@style, 'ripple')]"
        "https://www.dota2.com/patches/7.36"
        hero_xpath = "//a[contains(@href, '/hero/')]"
        "//a[contains(@href, '/hero/')]/..//div[contains(@style, 'ripple')]"
        # //div[contains(@style, 'ripple')]/following-sibling::div
        sb.get("https://www.dota2.com/patches/7.36")
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
                ratio = fuzz.ratio(hero_name, switcher(hero["name"]).replace("_", ""))
                if ratio == 100:
                    h_name = hero["name"]
                    best_score = ratio
                    break
                if ratio > best_score:
                    best_score = ratio
                    h_name = hero["name"]
            if best_score != 100:
                print(f, hero_name, h_name, best_score)
            for doc in hero_stats:
                if doc["hero"] == h_name:
                    for i in range(len(f)):
                        doc["facets"][i]["filter"] = f[i]
                    facet_updates.append(
                        UpdateMany(
                            {"hero": doc["hero"]},
                            {"$set": {"facets": doc["facets"]}},
                        )
                    )
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
    for value in special_values:
        name = value["name"]
        clean_ability = re.sub(f"%|,", "", target_ability)
        if name == clean_ability:
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
    return target_ability
