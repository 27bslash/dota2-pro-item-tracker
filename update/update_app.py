import json
import time
from pymongo import UpdateOne
import requests
from colours.contrast import compute_contrast
from helper_funcs.accounts.download_acount_ids import update_pro_accounts
from helper_funcs.helper_imports import db, delete_old_urls, hero_list
from update.convert_from_d2vpk import generate_opendota_items
from update.update_abilities.update_abilities import update_hero_stats, update_talents
from update.update_abilities.update_facets import (
    add_deprecated_facets,
    update_facet_colours,
)
from update.update_heroes import update_hero_list, update_minimap_icon
from update.update_items import update_item_ids, update_json_data

import re


def update_app(delete_urls=False, force_update=False):
    old_hero_list = db["hero_list"].find_one()["heroes"]
    current_patch = db["current_patch"].find_one()
    if not current_patch:
        return
    req = requests.get(
        "https://www.dota2.com/datafeed/patchnoteslist?language=english"
    ).json()
    new_patch = req["patches"][-1]
    patch = new_patch["patch_number"]
    patch_time = new_patch["patch_timestamp"]

    print("updating hero list")
    hero_list = update_hero_list()
    print('updating minimap icons')
    update_minimap_icon(hero_list=hero_list['heroes'])
    if len(hero_list['heroes']) != len(old_hero_list):
        print('new hero found updating all')
    else:
        print('no new hero')
    print(patch, current_patch["patches"][-1]["patch_number"])
    all_items, datamined_abilities, facets_json = update_item_json()
    if (
        new_patch["patch_number"] != current_patch["patches"][-1]["patch_number"]
        or len(hero_list['heroes']) != len(old_hero_list)
        or force_update
    ):
        # delete all urls older than patch ignore sub patches

        with open(
            f"D:\\projects\\python\\pro-item-builds\\update\\test_files\\{patch}_abilities.json",
            "w",
        ) as f:
            json.dump(datamined_abilities, f, indent=4)
        if delete_urls:
            delete_old_urls(int(time.time()) - int(patch_time))
        print("updating json....")
        update_item_ids()
        print("downloading abilities...")
        update_hero_stats(True, facets_json, datamined_abilities)
        # print("updating_talents...")
        # update_talents()
        print("updating hero colours....")
        compute_contrast()
        if not re.search(r"[a-z]", new_patch["patch_number"]):
            print("updating facet colours....")
            update_facet_colours(new_patch['patch_number'])
        print("updating account ids")
        # update_pro_accounts(testing=False, read_site=True)
        req["patch"] = patch
        req["patch_timestamp"] = patch_time
        db["current_patch"].find_one_and_update({}, {"$set": req}, upsert=True)
    print("fini")


def update_item_json():
    # TODO
    # check instead of item_ids check for all_items_ids
    # all_items = db["all_items"].find_one()
    new_all_items, datamined_abilities, facets_json = generate_opendota_items()
    old_items = db['all_items'].find_one({'items': {'$exists': True}})
    all_item_hash = hash(str(old_items['items'])) if old_items else 'no hash'
    new_all_hash = hash(str(new_all_items))
    print('old hash', all_item_hash, 'new hash', new_all_hash)
    if all_item_hash != new_all_hash:
        version = db['all_items'].find_one({"version": {"$exists": True}})
        if version:
            current_version = version["version"]
            new_version = current_version + 1
            result = db['all_items'].find_one_and_update(
                {"version": current_version},
                {"$set": {"version": new_version}},
                return_document=True,
            )
            print(f"updated version to: {new_version}{result}")
            db["all_items"].find_one_and_update(
                {"items": {"$exists": True}},
                {"$set": {"items": new_all_items}},
                upsert=True,
            )
        else:
            db['all_items'].insert_one({"version": 0})

    return new_all_items, datamined_abilities, facets_json


def weekly_update():
    update_hero_list()
    update_json_data()
    update_item_ids()


if __name__ == "__main__":
    strt = time.perf_counter()
    # add_deprecated_facets()
    update_app(force_update=True)
    # new_all_items, datamined_abilities, facets_json = generate_opendota_items()
    # add_deprecated_facets(hero_list, facets_json=facets_json)
    # all_items, datamined_abilities, facets_json = update_item_json("7.37d")
    # add_deprecated_facets(hero_list, facets_json=facets_json)
    # with open('update/test_files/726_item.txt','r') as f:
    #     data = f.read()
    #     json.loads(data)
    # patch_time = 64800
    # delete_old_urls(64800)
    # update_item_ids()
    print(time.perf_counter() - strt)
