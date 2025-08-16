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
from helper_funcs.database.collection import hero_stats, current_patch
from logs.log_config import update_builds_logger


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
    print("writing to remote", hero)
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
            guide_file_path = f"C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote\\guides/{hero}_{role.lower()}"

        try:
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
                if time_published:
                    guide_template["guidedata"]["TimePublished"] = time_published
                guide_template["guidedata"]["AssociatedWorkshopItemID"] = workshop_id
                guide_template["guidedata"]["GuideRevision"] = str(
                    int(json_data["guidedata"]["GuideRevision"]) + 1
                )
        except FileNotFoundError:
            update_builds_logger.error(
                f"File not found: {role_path}.json , build file: {guide_file_path}"
            )
            return
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
            print("added to steam folder")


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


def add_value_to_build_file(file_path, key, value):
    for file in glob.glob(f"{file_path}_*.build"):
        with open(file, "r") as build_file:
            lines = build_file.readlines()
        with open(file, "w") as build_file:
            for line in lines:
                if key in line:
                    line = f'"{key}" "{value}"\n'
                build_file.write(line)


def unpublished_guides():
    files = []
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
                update_builds_logger.info(f"unpublished guide: {file}")
                files.append(file)
    pass


def delete_obsolete_guides():
    delete_files = []

    with os.scandir(
        "D:\\projects\\python\\pro-item-builds\\hero_guides\\builds"
    ) as entries:
        for file in entries:
            with open(file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    r = ''.join(
                        re.findall(
                            r"\d+",
                            current_patch['patches'][-1]['patch_number'],
                        )
                    )
                    g = ''.join(
                        re.findall(r"\d+", data['guidedata']['GameplayVersion'])
                    )
                    workshop_id_check = (
                        data['guidedata']['AssociatedWorkshopItemID']
                        != "0x0000000000000000"
                    )
                    number_patch_equal = r == g
                    if (
                        workshop_id_check
                        or number_patch_equal
                        or int(data['guidedata']['GuideRevision']) >= 10
                    ):
                        continue
                    update_builds_logger.info(
                        f"{file.name} workshop id check: {workshop_id_check} patch check: {number_patch_equal} guide revisions: {int(data['guidedata']['GuideRevision']) >= 10}"
                    )
                    delete_files.append(file)

                    # "C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote\\guides\\"
                except Exception:
                    update_builds_logger.error(
                        f"error in file {file.name} {traceback.format_exc()}"
                    )
                    # print(file.name, traceback.format_exc())
                    delete_files.append(file)

            pass
    # print(delete_files)

    for file in delete_files:
        with os.scandir(
            "C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote\\guides"
        ) as guide_entries:
            for f in guide_entries:
                clean_json_name = file.name.replace('.json', '').lower()
                if f.name.replace(r"_\d+.build", '').lower() == clean_json_name:
                    delete_files.append(f)
                    os.remove(f)
                    os.remove(file)
    print(len(delete_files), len(list(entries)))
    pass


def update_from_json():
    backup_folder = "D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\backup\\remote"
    steam_guides = "C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote"
    # copyanything(src, dst)
    # copy steam guides to backup location
    for filename in glob.glob(
        "D:\\projects\\python\\pro-item-builds\\hero_guides\\builds/*"
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
                except Exception:
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
        lst.append({"title": title, "workshop_id": padded_hex, "link": link})
    return lst
    # print(titles)


def pad_hex(num=0):
    hex_num = hex(int(num))
    padded_hex = "{:#018X}".format(int(hex_num, base=16)).replace("0X", "0x")
    return padded_hex


def add_workhop_id_to_guides(guide_list=[]):
    dic = {}
    print('dfjk')
    for steam_guide in guide_list:
        for filename in glob.glob(
            f"D:\\projects\\python\\pro-item-builds\\hero_guides\\builds/*"
        ):
            try:
                with open(filename, "r") as f:
                    strt = time.perf_counter()
                    data = json.load(f)
                    if time.perf_counter() - strt > 1:
                        print(filename, "time taken: ", time.perf_counter() - strt)

                    guide_title = data["guidedata"]["Title"]
                    roles = [
                        'Hard Support',
                        'Support',
                        'Offlane',
                        'Safelane',
                        'Midlane',
                        'Roaming',
                    ]
                    regex = fr"\b{switcher(data['guidedata']['Hero'].lower()).replace('_' , ' ')}\b"

                    if not re.search(
                        regex,
                        steam_guide['title'].lower(),
                    ):
                        # print('not found', d['title'].lower(), regex)
                        continue
                    # print(d['title'], data['guidedata']['Hero'])
                    role_replaced = re.sub(r"\(.*\)", '', steam_guide['title'])

                    for role in roles:
                        found_role = re.search(role, role_replaced, re.IGNORECASE)
                        if found_role:
                            found_role = found_role.group()

                            break
                    if found_role == 'Support' and 'Hard Support' in f.name:
                        continue
                    role_file_search = re.search(found_role, f.name, re.IGNORECASE)
                    if (found_role and not role_file_search) or not found_role:
                        continue
                    # print('rr', role_replaced,found_role)

                    curr_workshop_id = data["guidedata"]["AssociatedWorkshopItemID"]
                match = re.search(r"\\builds[\\/](.+).json$", filename)
                if match:
                    guide_name = match.group(1)
                    build_name = f"C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote\\guides\\{guide_name}"
                    build_file_id = get_value_from_build_file(
                        build_name, 'AssociatedWorkshopItemID'
                    )
                if (
                    curr_workshop_id == steam_guide["workshop_id"]
                    and build_file_id == steam_guide["workshop_id"]
                    or not build_file_id
                ):
                    continue
                update_builds_logger.info(
                    f"{role_replaced}\n{filename} id in guide file: {curr_workshop_id} steam ID: {steam_guide['workshop_id']} link {steam_guide['link']}"
                )
                # print(d['title'])
                data["guidedata"]["AssociatedWorkshopItemID"] = steam_guide[
                    "workshop_id"
                ]
                with open(filename, "w", encoding="utf-8") as o:
                    # print(filename)
                    json.dump(data, o, indent=4)
                add_value_to_build_file(
                    file_path=build_name,
                    key="AssociatedWorkshopItemID",
                    value=steam_guide["workshop_id"],
                )
            except Exception as e:
                print(filename, e)
                pass
    pprint(dic)


def build_stats(page_num):
    req = requests.get(
        f"https://steamcommunity.com/id/27bslash/myworkshopfiles/?section=guides&p={page_num}&numperpage=30"
    )
    soup = BeautifulSoup(req.text, "html.parser")
    els = soup.find_all("a", "workshopItemCollection")
    lst = []
    print("build_stats", "page_num=", page_num)
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
                d["subscribers"] = float(cells.text.replace(',', ''))
            if i == 2:
                d["favs"] = float(cells.text.replace(',', ''))
        lst.append(d)
        time.sleep(0.3)
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
    chunked_guides = len([i for i in range(0, total_guides, 30)])
    workshop_ids = []
    dl_stats = []
    pages = {}
    for i in range(1, chunked_guides + 1):
        workshop_ids += get_workshop_ids_of_page(i)
        pages[i % 30] = workshop_ids
        if build_subs:
            dl_stats += build_stats(i)
    add_workhop_id_to_guides(guide_list=workshop_ids)
    sorted_data = sorted(dl_stats, key=lambda x: int(x["subscribers"]), reverse=True)
    hero_titles = [re.search(r"\) (.*)", x['title']).group(1) for x in workshop_ids]
    hero_titles.sort()
    print(sorted_data[0:10], sum([x['subscribers'] for x in sorted_data]))


if __name__ == "__main__":
    # modify_remote()
    # update_from_json()
    # modify_remote()
    # while True:
    #     time.sleep(1)
    # delete_obsolete_guides()
    # print(pad_hex(2970840466))
    get_all_guides_from_steam()
    # get_all_guides_from_steam()
    # update_from_json()
    # unpublished_guides()
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
