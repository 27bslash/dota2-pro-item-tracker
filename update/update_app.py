import json
import time
import requests
from colours.contrast import compute_contrast
from helper_funcs.accounts.download_acount_ids import update_pro_accounts
from helper_funcs.helper_imports import *
from update.convert_from_d2vpk import generate_opendota_items
from update.update_abilities.update_abilities import dl_dota2_abilities, update_talents
from update.update_abilities.update_facets import update_facet_colours
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

    print(patch, current_patch["patches"][-1]["patch_number"])
    all_items, datamined_abilities = update_item_json(patch)

    with open(
        f"D:\\projects\\python\\pro-item-builds\\update\\test_files\\{patch}_abilities.json",
        "w",
    ) as f:
        json.dump(datamined_abilities, f, indent=4)
    if (
        new_patch["patch_number"] != current_patch["patches"][-1]["patch_number"]
        or force_update
    ):
        # delete all urls older than patch ignore sub patches
        if delete_urls:
            delete_old_urls(int(time.time()) - int(patch_time))
        print("uploading hero list")
        hero_list = update_hero_list()
        print("updating json....")
        update_item_ids()
        print("downloading abilities...")
        dl_dota2_abilities(True, datamined_abilities)
        # print("updating_talents...")
        update_talents()
        print("updating hero colours....")
        compute_contrast()
        if not re.search(r"[a-z]", new_patch["patch_number"]):
            print("updating facet colours....")
            update_facet_colours()
            pass
        print("updating minimap icons...")
        if len(old_hero_list) < len(hero_list):
            update_minimap_icon(hero_list=hero_list)
        print("updating account ids")
        update_pro_accounts()
        req["patch"] = patch
        req["patch_timestamp"] = patch_time
        db["current_patch"].find_one_and_update({}, {"$set": req}, upsert=True)
    print("fini")


def update_item_json(patch: str):
    # TODO
    # check instead of item_ids check for all_items_ids
    all_items = db["all_items"].find_one()
    new_all_items, datamined_abilities = generate_opendota_items()
    all_item_hash = hash(str(all_items["items"]))
    new_all_hash = hash(str(new_all_items))
    if all_item_hash != new_all_hash:
        version = patch
        db["all_items"].find_one_and_update(
            {}, {"$set": {"items": new_all_items, "version": version}}, upsert=True
        )
    return all_items, datamined_abilities


def weekly_update():
    update_hero_list()
    update_json_data()
    update_item_ids()


if __name__ == "__main__":
    strt = time.perf_counter()
    update_app()
    # with open('update/test_files/726_item.txt','r') as f:
    #     data = f.read()
    #     json.loads(data)
    # patch_time = 64800
    # delete_old_urls(64800)
    # update_item_ids()
    print(time.perf_counter() - strt)
