import json
import re
import traceback

from pymongo import UpdateOne
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

from update.update_abilities.update_facets import update_facets
from update.update_abilities.update_talents import parse_talents, update_talents
from update.update_items import create_item_description
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ.get('STRATZ_API_KEY')


def dl_dota2_abilities(manual=False, datamined_abilities=None):
    if manual:
        make_dir()
    datafeed = "https://www.dota2.com/datafeed/herodata?language=english&hero_id="

    ab_url = "https://raw.githubusercontent.com/dotabuff/d2vpkr/master/dota/scripts/npc/npc_abilities.json"
    if not datamined_abilities:
        datamined_abilities = json.loads(requests.get(ab_url).text)

    chrome_options = Options()
    chrome_options.add_argument("--window-position=2000,0")
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    if not hero_list:
        return
    hero_stat_updates = []
    for hero in hero_list:
        print(hero["name"])
        # if hero['name'] != 'medusa':
        #     continue
        req = requests.get(f"{datafeed}{hero['id']}")
        ability_json = json.loads(req.text)["result"]["data"]["heroes"][0]
        for facet in ability_json['facet_abilities']:
            try:
                ability_json['abilities'].append(facet['abilities'][0])
            except Exception:
                pass
        hero_abilities = {}
        for ability in ability_json['abilities']:
            hint = [ability["desc_loc"]]
            try:
                desc = create_item_description(
                    hint, datamined_abilities, ability["name"]
                )
                ability["desc_loc"] = re.sub(r"-- ", "", desc[0])
            except Exception:
                pass
            if manual:
                get_ability_img(ability["name"], hero["name"])
            hero_abilities[str(ability["id"])] = ability
        hero_talents = parse_talents(datamined_abilities, ability_json)
        hero_facets = update_facets(ability_json)

        # url = dota_link(hero["name"])
        # driver.get(url)
        # elem = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located(
        #         (By.CSS_SELECTOR, "div[class*='heropage_TalentEntry']")
        #     )
        # )
        # if not elem:
        #     with open("err.html", "w", encoding="utf-8") as f:
        #         f.write(driver.page_source)
        #         print(traceback.format_exc())
        #     break

        # soup = BeautifulSoup(driver.page_source, "html.parser")
        # talents = soup.find_all(
        #     "div", attrs={"class", re.compile("heropage_TalentEntry")}
        # )[0:8:1]
        # # left to right top to bottom
        # talent_text = [talent.text.strip() for talent in talents]
        # if not talent_text:
        #     with open("err.html", "w", encoding="utf-8") as f:
        #         f.write(driver.page_source)
        #     break
        # for i, talent in enumerate(ability_json["talents"]):
        #     talent["slot"] = i
        #     hero_talents[str(talent["id"])] = talent
        #     try:
        #         talent["name_loc"] = talent_text[::-1][i]
        #     except:
        #         # print(hero['name'])
        #         break
        ability_json["abilities"] = hero_abilities
        ability_json["talents"] = hero_talents
        ability_json['facets'] = hero_facets
        hero_stat_updates.append(
            UpdateOne({"hero": hero["name"]}, {"$set": ability_json}, upsert=True)
        )

    db['hero_stats'].bulk_write(hero_stat_updates)
    # driver.quit()
    # json.dump(hero_abilities, o, indent=4)


def create_ability_desc(hint, name, datamined_abilities, type):
    key = ''
    datamined_abilities['lang']['Tokens'][key]
    pass


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


def update_short_talents(talents):
    lst = []
    for k in talents:
        for key in k:
            print(k)
            d = {}
            d["img"] = talents[k]["name"]
            d["key"] = talents[k]["name_loc"]
            d["id"] = k['id']
            d["slot"] = talents[k]["slot"]
            d["type"] = "talent"
            lst.append(d)
    return lst


if __name__ == "__main__":
    with open('update/test_files/7.37_abilities.json', 'r') as f:
        data = json.load(f)
        dl_dota2_abilities(manual=False, datamined_abilities=data)
        update_talents()
        # talents_from_stratz(6607)
