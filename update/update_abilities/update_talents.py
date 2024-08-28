import re
import traceback

from pymongo import UpdateOne
import requests
from update.update_items import create_item_description

from dotenv import load_dotenv
import os
from helper_funcs.helper_imports import db, hero_list

load_dotenv()

api_key = os.environ.get("STRATZ_API_KEY")
stratz_abilities_constant = None


def parse_talents(datamined_abilities, ability_json):
    hero_talents = {}
    for talent in ability_json["talents"]:
        hint = [talent["name_loc"]]
        try:
            desc = create_item_description(hint, datamined_abilities, talent["name"])
            if desc == hint:
                pass
            talent["name_loc"] = re.sub(r"-- ", "", desc[0])
        except:
            displayName = talents_from_stratz(talent["id"])
            if displayName:
                talent["name_loc"] = displayName
        hero_talents[str(talent["id"])] = talent
    return hero_talents


def talents_from_stratz(_id: int) -> str | None:
    query = """
     {
        constants {
            abilities {
                id
                isTalent
                name
                language {
                    displayName
                }
            }
        }
    }
    """
    request_data = {"query": query}
    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    url = "https://api.stratz.com/graphql"
    global stratz_abilities_constant
    if not stratz_abilities_constant:
        req = requests.post(url=url, headers=headers, json=request_data)
        if req.status_code != 200:
            return None
        print("stratz constants requested")
        stratz_abilities_constant = req.json()
    abilities = stratz_abilities_constant["data"]["constants"]["abilities"]
    for ability in abilities:
        if ability["id"] == _id:
            if not ability["language"]:
                print(ability["name"])
                continue
            return ability["language"]["displayName"]


def update_talents():
    talent_updates = []
    for hero in hero_list:
        print(hero["name"])
        # db_methods.insert_talent_order(hero['id'])

        talents = db["hero_stats"].find_one({"hero": hero["name"]})["talents"]
        for i, talent in enumerate(talents):
            if i % 2 == 0:
                talents[talent]["slot"] = i + 1
            else:
                talents[talent]["slot"] = i - 1
        # 1 0 3 2 5 4 7 6

        # short_talents = update_short_talents(talents)
        # print(short_talents)
        # db["talents"].find_one_and_update(
        #     {"hero": switcher(hero["name"])},
        #     {"$set": {"talents": short_talents}},
        #     upsert=True,
        # )
        # print(talents)
        talent_updates.append(extract_special_values(talents, hero["name"]))
    db['hero_stats'].bulk_write(talent_updates)


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
    return UpdateOne({"hero": hero}, {"$set": {"talents": talents}}, upsert=True)
    


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
    update_talents()
