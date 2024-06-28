import json
import os
from pprint import pprint
import re
import time
import glob
import traceback

import requests
from helper_funcs.switcher import switcher

from bs4 import BeautifulSoup

from hero_guides.update_builds.remote.handle_remote import cut_folder
from helper_funcs.database.collection import hero_stats


def facet_name(facets: list, hero_data):
    srted = sorted(facets, key=lambda k: k["count"], reverse=True)[0]
    key = srted["key"]
    return hero_data["facets"][key - 1]["title_loc"]


def write_build_to_remote(data, hero, patch, debug=False):
    # "AbilityBuild"
    # 	{
    # 		"AbilityOrder"
    # 		{
    # 			"1"		"jakiro_dual_breath"
    # 		}}

    role_conversion = {
        "Safelane": "Core",
        "Offlane": "Offlane",
        "Hard Support": "Support",
        "Support": "Support",
        "Roaming": "Roamer",
        "Midlane": "Core",
    }
    hero_data = [doc for doc in hero_stats if doc["hero"] == hero][0]
    for role in data:
        facet_title = facet_name(data[role]["facets"], hero_data)
        guide_template = {}
        # starting items
        itemBuild = {"ItemBuild": {}}
        itemBuild["ItemBuild"]["Starting Items"] = data[role]["starting_items"]
        abilities = data[role]["abilities"]
        itemBuild = itemBuild["ItemBuild"] | data[role]["items"]["ItemBuild"]
        item_tooltips = data[role]["items"]["tooltip"]
        timestamp = int(time.time())
        guide_title = (
            f"{re.sub('_', ' ', switcher(hero).title())} {role} {facet_title} Build"
        )

        # role = 'Offlane'
        dota_role = f"#DOTA_HeroGuide_Role_{role_conversion[role]}"
        guide_template = {
            "guidedata": {
                "Hero": f"{hero}",
                "Title": guide_title,
                "GameplayVersion": patch,
                "GuideRevision": "1",
                "Role": dota_role,
                "AssociatedWorkshopItemID": "0x0000000000000000",
                "OriginalCreatorID": "0x0000000005550372",
                "TimeUpdated": pad_hex(timestamp),
                "ItemBuild": {"Items": itemBuild, "ItemTooltips": item_tooltips},
                "AbilityBuild": {
                    "AbilityOrder": abilities["ability_build"],
                    "AbilityTooltips": abilities["abilityTooltips"],
                },
            }
        }
        # guide_template = {"guidedata": {"Hero": f"{hero}",  "Title": f"{re.sub('_', ' ', switcher(hero).title())} {role} Build",
        #                                 "GuideRevision": "1", "Role": dota_role, "AssociatedWorkshopItemID": "0x0000000000000000",
        #                                 "OriginalCreatorID": "0x0000000005550372",
        #                                 'TimeUpdated': hex(timestamp),
        #                                 "ItemBuild": {"Items": itemBuild}
        #                                 }
        #                   }

        role_path = f"hero_guides/builds/{hero}_{role}"
        if debug:
            # TEST FOLDER
            role_path = f"D:\\projects\\python\\pro-item-builds\\hero_guides\\test_builds\\json_builds/{hero}_{role}"
            guide_file_path = f"D:\\projects\\python\\pro-item-builds\\hero_guides\\test_builds\\builds/{hero}_{role.lower()}"
        else:
            role_path = f"D:\\projects\\python\\pro-item-builds\\hero_guides\\builds/{hero}_{role}"
            guide_file_path = f"D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\backup\\remote\\guides/{hero}_{role.lower()}"

        if os.path.exists(f"{role_path}.json"):
            with open(f"{role_path}.json", "r") as f:
                json_data = json.load(f)
                timestamp = int(json_data["guidedata"]["TimeUpdated"], 16)
                # if json_data['guidedata']['AssociatedWorkshopItemID'] == "0x0000000000000000":
                #     print('in')
                #     break
                workshop_id = get_value_from_build_file(
                    guide_file_path, "AssociatedWorkshopItemID"
                )
                time_published = get_value_from_build_file(
                    guide_file_path, "TimePublished"
                )
                # timestamp = f.read()
                current_revision = get_value_from_build_file(
                    guide_file_path, "GuideRevision"
                )
                if current_revision:
                    current_revision = re.search(r"\d+", current_revision).group()
                    if (
                        guide_title == json_data["guidedata"]["Title"]
                        and json_data["guidedata"]["ItemBuild"]
                        == guide_template["guidedata"]["ItemBuild"]
                        and json_data["guidedata"]["AbilityBuild"]
                        == json_data["guidedata"]["AbilityBuild"]
                        and json_data["guidedata"]["GuideRevision"] == current_revision
                    ):
                        print("true equal")
                        continue

                guide_template["guidedata"]["TimePublished"] = time_published
                guide_template["guidedata"]["AssociatedWorkshopItemID"] = workshop_id
                guide_template["guidedata"]["GuideRevision"] = str(
                    int(json_data["guidedata"]["GuideRevision"]) + 1
                )

        with open(f"{role_path}.json", "w") as f:
            json.dump(guide_template, f, indent=4)
        # add builds to backup folder
        if not debug:
            add_to_build_file(
                guide_template, path=f"{guide_file_path}", timestamp=timestamp
            )

            # update build in steam guide folder
            add_to_build_file(
                guide_template=guide_template,
                path=f"C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote\\guides\\{hero}_{role.lower()}",
                timestamp=timestamp,
            )


def add_to_build_file(guide_template, path, timestamp):
    guide_template = str(json.dumps(guide_template, indent=8))
    # remove colon between key value pairs
    cleaned = re.sub(r'(?<="):(?!\d)', "\t\t", guide_template)
    # remove commas between entries
    cleaned = re.sub(r",", "", cleaned)
    # remove unique keys from json
    cleaned = re.sub(r"(?<=item)_\d+", "", cleaned)
    # remove unique items from json
    cleaned = re.sub(r"__\d", "", cleaned)
    files = glob.glob(f"{path}_*.build")

    for file in files:
        # if file != target_file:
        # delete content of all cloud files
        os.remove(file)

    # os.remove(f)
    # # print(f)
    # with open(f, 'w') as file:
    with open(f"{path}_{timestamp}.build", "w") as buildFile:
        buildFile.write(cleaned[1 : len(cleaned) - 1].strip())
        pass


def item_builder(itemBuild, items):
    for i, entry in enumerate(items):
        for k, v in entry.items():
            item_build = {}
            j = 0
            for itemDict in v:
                itemKeys = itemDict.keys()
                for item_key in itemKeys:
                    item_build[f"item_{j}"] = f"item_{item_key}"
                    # print(i, j, k, item_key)
                j += 1
            timing = "Late"
            if i == 0:
                timing = "Early"
            elif i == 1:
                timing = "Mid"
            field_title = f"{timing} {k}"
            itemBuild[field_title] = item_build
    return itemBuild


def get_value_from_build_file(file_path, key):
    for file in glob.glob(f"{file_path}_*.build"):
        with open(file, "r") as build_file:
            for line in build_file:
                if key in line:
                    value = re.search(r"0x.*\"", line)
                    if value:
                        value = value.group().replace('"', "")
                        return value
                    elif "0x" not in line:
                        return re.sub(key, "", line).strip()


def unpublished_guides():
    for file in glob.glob(
        f"C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote\\guides\\*.build"
    ):
        with open(file, "r") as f:
            published = False
            for line in f:
                if published:
                    break
                if "AssociatedWorkshopItemID" in line:
                    value = re.search(r"0x.*\"", line)
                    if value and value.group() != '0x0000000000000000"':
                        value = value.group().replace('"', "")
                        published = True
                        break
            if not published:
                print(file)

    pass


def update_from_json():
    backup_folder = "D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\backup\\remote"
    steam_guides = "C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote"
    # copyanything(src, dst)
    # copy steam guides to backup location
    for filename in glob.glob(
        f"D:\\projects\\python\\pro-item-builds\\hero_guides\\builds/*"
    ):
        print(filename)
        with open(filename, "r") as f:
            data = json.load(f)
            regex = r"(?<=hero_guides\\builds).*(?=\.)"

            hero_roels = re.search(regex, filename)
            if hero_roels:
                try:
                    guide_file_path = f"D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\backup\\remote\\guides{hero_roels.group().lower()}"
                    add_to_build_file(data, guide_file_path, int(time.time()))
                except Exception as e:
                    print(traceback.format_exc())
                    cut_folder(backup_folder, steam_guides)


def get_workshop_ids_of_page(page_num):
    req = requests.get(
        f"https://steamcommunity.com/id/27bslash/myworkshopfiles/?section=guides&p={page_num}&numperpage=30"
    )
    soup = BeautifulSoup(req.text, "html.parser")
    els = soup.find_all("a", "workshopItemCollection")
    lst = []
    for el in els:
        title = el.find("div", "workshopItemTitle").text.strip()
        link = el.get("href")
        _id = re.search(r"(?<=id=)\d+", link)
        if not _id:
            continue
        padded_hex = pad_hex(int(_id.group()))
        lst.append({"title": title, "workshop_id": padded_hex})
    return lst
    # print(titles)


def pad_hex(num=0):
    hex_num = hex(int(num))
    padded_hex = "{:#018X}".format(int(hex_num, base=16)).replace("0X", "0x")
    return padded_hex


def add_workhop_id_to_guides(list=[]):
    for d in list:
        for filename in glob.glob(
            f"D:\\projects\\python\\pro-item-builds\\hero_guides\\builds/*"
        ):
            try:
                with open(filename, "r") as f:
                    data = json.load(f)
                    guide_title = data["guidedata"]["Title"]
                    curr_workshop_id = data["guidedata"]["AssociatedWorkshopItemID"]
                    if guide_title not in d["title"]:
                        continue
                if curr_workshop_id == d["workshop_id"]:
                    continue
                print(
                    d["title"],
                    "id in guide file: ",
                    curr_workshop_id,
                    "steam ID: ",
                    d["workshop_id"],
                )
                # print(d['title'])
                data["guidedata"]["AssociatedWorkshopItemID"] = d["workshop_id"]
                with open(filename, "w", encoding="utf-8") as o:
                    # print(filename)
                    json.dump(data, o, indent=4)
            except Exception as e:
                print(filename, e)
                pass


def build_stats(page_num):
    req = requests.get(
        f"https://steamcommunity.com/id/27bslash/myworkshopfiles/?section=guides&p={page_num}&numperpage=30"
    )
    soup = BeautifulSoup(req.text, "html.parser")
    els = soup.find_all("a", "workshopItemCollection")
    lst = []
    for el in els:
        title = el.find("div", "workshopItemTitle").text.strip()
        link = el.get("href")
        req = requests.get(link)
        soup = BeautifulSoup(req.text, "html.parser")

        stats = soup.find("table", class_="stats_table").find_all("tr")
        d = {"title": title, "subscribers": 0, "favs": 0}
        for i, stat in enumerate(stats):
            if i == 0:
                continue
            cells = stat.find("td")
            if i == 1:
                d["subscribers"] = float(cells.text)
            if i == 2:
                d["favs"] = float(cells.text)
        lst.append(d)
        time.sleep(1)
    return lst


def get_all_guides_from_steam(build_subs=False):
    total_guides = len(
        [
            filename
            for filename in glob.glob(
                f"D:\\projects\\python\\pro-item-builds\\hero_guides\\builds/*"
            )
        ]
    )
    l = len([i for i in range(0, total_guides, 30)])
    workshop_ids = []
    dl_stats = []
    for i in range(1, l + 1):
        workshop_ids += get_workshop_ids_of_page(i)
        if build_subs:
            dl_stats += build_stats(i)
    add_workhop_id_to_guides(list=workshop_ids)
    sorted_data = sorted(dl_stats, key=lambda x: int(x["subscribers"]), reverse=True)
    print(sorted_data[0:10])


if __name__ == "__main__":
    # modify_remote()
    # update_from_json()
    # modify_remote()
    # while True:
    #     time.sleep(1)
    # print(pad_hex(2970840466))

    # get_all_guides_from_steam()
    # update_from_json()
    unpublished_guides()
    # modify_remote()
    # print(get_workshop_ids_of_page(1))

    # backup_folder = 'D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\backup\\remote'
    # steam_guides = 'C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote'
    # backup_remote(steam_guides, backup_folder)

    # update_from_json()
    # modify_remote()

    # unpublished_guides()
    # get_all_guides_from_steam()
    # get_workshop_ids_of_page(1)
    # update_from_json()
    # modify_remote()
    pass
    # modify_remote(delete=True)
    # modify_remote()
