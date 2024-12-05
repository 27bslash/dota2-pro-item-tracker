import json
from os.path import exists
from pprint import pprint
import re

import requests
from bs4 import BeautifulSoup

from helper_funcs.helper_imports import db, switcher


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
    text = requests.get("https://liquipedia.net/dota2/Minimap").text
    curr_list = []
    for hero_name in hero_list:
        curr = switcher(hero_name["name"])
        curr_list.append(curr)
    curr_list = sorted(curr_list)
    soup = BeautifulSoup(text, "html.parser")
    second_row = soup.find_all("tr")[1]
    # print(first_row)
    # print(sprite_sheet)
    fin = []
    for i, img in enumerate(second_row.find_all("img")):
        d = {}
        # print(img['data-src'])
        d["link"] = img["src"]
        hero_img_title = re.sub(r" ", "_", img.parent['title']).lower()
        # print(d)
        fin.append(d)
        frontend_image_path = (
            "D:\\projects\\python\\pro-item-frontend\\public\\images\\minimap_icons"
        )
        if not exists(f"{frontend_image_path}/{switcher(hero_img_title)}.jpg"):
            with open(
                f"{frontend_image_path}/{switcher(hero_img_title)}.jpg", "wb"
            ) as o:
                o.write(requests.get(f"https://liquipedia.net{img['src']}").content)
                pass


if __name__ == "__main__":
    from helper_funcs.database.collection import hero_list

    update_minimap_icon(hero_list=hero_list)
    pass
