import json
from os.path import exists
from pprint import pprint

import requests
from bs4 import BeautifulSoup

from helper_funcs.helper_imports import db, switcher
from helper_funcs.database.collection import db, hero_list


def update_hero_list():
    data = json.loads(
        requests.get("https://www.dota2.com/datafeed/herolist?language=english").text
    )
    hero_dict = {"heroes": []}
    for dic in data["result"]["data"]["heroes"]:
        hero_name = switcher(dic["name_loc"].lower().replace(" ", "_"))
        hero_id = int(dic["id"])
        hero_dict["heroes"].append({"name": hero_name, "id": hero_id})

    db["hero_list"].find_one_and_update({}, {"$set": hero_dict}, upsert=True)
    return hero_dict


def update_minimap_icon(hero_list=[]):
    text = requests.get("https://dota2.fandom.com/wiki/Minimap").text
    curr_list = []
    for hero_name in hero_list:
        curr = switcher(hero_name["name"])
        curr_list.append(curr)
    curr_list = sorted(curr_list)
    soup = BeautifulSoup(text, "html.parser")
    second_row = soup.find_all("tr")[1]
    # print(first_row)
    sprite_sheet = second_row.find("p")
    # print(sprite_sheet)
    fin = []
    for i, img in enumerate(sprite_sheet.find_all("img")):
        d = {}
        # print(img['data-src'])
        d["link"] = img["data-src"]
        # print(d)
        fin.append(d)
        if not exists(f"static/images/minimap_icons/{switcher(curr_list[i])}.jpg"):
            with open(
                f"static/images/minimap_icons/{switcher(curr_list[i])}.jpg", "wb"
            ) as o:
                o.write(requests.get(f"{img['data-src']}").content)
