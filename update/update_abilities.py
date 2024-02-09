import json
import re
import traceback

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from colours.color_dir import make_dir
from helper_funcs.helper_imports import db, switcher
from helper_funcs.database.collection import hero_list

from update.update_items import create_item_description


def dl_dota2_abilities(manual=False):
    if manual:
        make_dir()
    datafeed = "https://www.dota2.com/datafeed/herodata?language=english&hero_id="

    ab_url = "https://raw.githubusercontent.com/dotabuff/d2vpkr/master/dota/scripts/npc/npc_abilities.json"
    datamined_abilities = json.loads(requests.get(ab_url).text)

    chrome_options = Options()
    chrome_options.add_argument("--window-position=2000,0")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    if not hero_list:
        return
    for hero in hero_list:
        req = requests.get(f"{datafeed}{hero['id']}")
        ability_json = json.loads(req.text)["result"]["data"]["heroes"][0]
        hero_abilities = {}
        hero_talents = {}
        print(hero["name"])
        for ability in ability_json["abilities"]:
            hint = [ability["desc_loc"]]
            try:
                desc = create_item_description(
                    hint, datamined_abilities, ability["name"]
                )
                ability["desc_loc"] = re.sub(r"-- ", "", desc[0])
            except:
                pass
            hero_abilities[str(ability["id"])] = ability
            if manual:
                get_ability_img(ability["name"], hero["name"])
        url = dota_link(hero["name"])
        driver.get(url)
        elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class*='heropage_TalentEntry']")
            )
        )
        if not elem:
            with open("err.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
                print(traceback.format_exc())
            break

        soup = BeautifulSoup(driver.page_source, "html.parser")
        talents = soup.find_all(
            "div", attrs={"class", re.compile("heropage_TalentEntry")}
        )[0:8:1]
        # left to right top to bottom
        talent_text = [talent.text.strip() for talent in talents]
        if not talent_text:
            with open("err.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            break
        for i, talent in enumerate(ability_json["talents"]):
            talent["slot"] = i
            hero_talents[str(talent["id"])] = talent
            try:
                talent["name_loc"] = talent_text[::-1][i]
            except:
                # print(hero['name'])
                break
        ability_json["abilities"] = hero_abilities
        ability_json["talents"] = hero_talents
        db["hero_stats"].find_one_and_update(
            {"hero": hero["name"]}, {"$set": ability_json}, upsert=True
        )
    driver.quit()
        # json.dump(hero_abilities, o, indent=4)


def dota_link(url):
    return f'https://www.dota2.com/hero/{re.sub(r"_", "", switcher(url))}'


def get_ability_img(ability_name, hero_name):
    if ability_name.replace("_", "").startswith(hero_name.replace("_", "")):
        with open(
            f"D:\\projects\\python\\pro-item-builds\\colours\\ability_images\\{hero_name}\\{ability_name}.jpg",
            "wb",
        ) as f:
            f.write(
                requests.get(
                    f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/abilities/{ability_name}.png"
                ).content
            )
            print(ability_name)


def update_talents():
    for hero in hero_list:
        print(hero["name"])
        # db_methods.insert_talent_order(hero['id'])

        talents = db["hero_stats"].find_one({"hero": hero["name"]})["talents"]
        short_talents = update_short_talents(talents)
        # print(short_talents)
        db["talents"].find_one_and_update(
            {"hero": switcher(hero["name"])},
            {"$set": {"talents": short_talents}},
            upsert=True,
        )
        # print(talents)
        extract_special_values(talents, hero["name"])


def update_short_talents(talents):
    lst = []
    for k in talents:
        d = {}
        d["img"] = talents[k]["name"]
        d["key"] = talents[k]["name_loc"]
        d["id"] = k
        d["slot"] = talents[k]["slot"]
        d["type"] = "talent"
        lst.append(d)
    return lst


def extract_special_values(talents, hero):
    for k in talents:
        if "{" not in talents[k]["name_loc"]:
            continue
        try:
            special_values = talents[k]["special_values"]
            test_string = talents[k]["name_loc"]
            clean = val(test_string, special_values)
            talents[k]["name_loc"] = clean
        except Exception as e:
            print(
                "Exception: ", hero, k, talents[k]["name_loc"], traceback.format_exc()
            )
    db["hero_stats"].find_one_and_update(
        {"hero": hero}, {"$set": {"talents": talents}}, upsert=True
    )


def val(text, special_values):
    # print(text)
    pattern = re.compile("s:(\w*)")
    result = ""
    if len(special_values) == 0:
        return text.replace(r"{s:.*}", "")
    for value in special_values:
        special_val = ""
        if len(result) > 0:
            text = result
        if "s:" not in text:
            return text
        match = pattern.search(text).group(1)
        if (
            value["name"] == match
            or value["name"] == "value"
            and len(special_values) == 1
        ):
            if len(value["values_float"]) > 0:
                special_val += f"{round(value['values_float'][0], 2)}"
            else:
                special_val += str(value["values_int"][0])
            if value["is_percentage"]:
                special_val += "%"
            regex = "{s:" + match + "}"
            result = re.sub(regex, special_val, text)
    if result == "":
        return re.sub(r"{s:.*}s?%?", "", text)
    return result


if __name__ == "__main__":
    dl_dota2_abilities(True)
