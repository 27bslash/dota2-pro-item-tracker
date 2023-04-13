
import json
import os
from pprint import pprint
import re
import time
import glob
from helper_funcs.switcher import switcher


def write_build_to_remote(data, hero, patch):
    # "AbilityBuild"
    # 	{
    # 		"AbilityOrder"
    # 		{
    # 			"1"		"jakiro_dual_breath"
    # 		}}

    role_conversion = {'Safelane': 'Core', 'Offlane': 'Offlane',
                       'Hard Support': 'Support', 'Support': 'Support', 'Roaming': 'Roamer', 'Midlane': 'Core'}
    for role in data:

        guide_template = {}
        # starting items
        itemBuild = {'ItemBuild': {}}
        itemBuild['ItemBuild']['Starting Items'] = data[role]['starting_items']
        abilities = data[role]['abilities']
        itemBuild = itemBuild['ItemBuild'] | data[role]['items']['ItemBuild']
        item_tooltips = data[role]['items']['tooltip']
        timestamp = int(time.time())

        # role = 'Offlane'
        dota_role = f"#DOTA_HeroGuide_Role_{role_conversion[role]}"
        guide_template = {"guidedata": {"Hero": f"{hero}",  "Title": f"{re.sub('_', ' ', switcher(hero).title())} {role} Build", "GameplayVersion": patch,
                                        "GuideRevision": "1", "Role": dota_role, "AssociatedWorkshopItemID": "0x0000000000000000",
                                        "OriginalCreatorID": "0x0000000005550372",
                                        'TimeUpdated': hex(timestamp),
                                        "ItemBuild": {"Items": itemBuild, "ItemTooltips": item_tooltips},
                                        "AbilityBuild": {"AbilityOrder": abilities['ability_build'], 'AbilityTooltips': abilities['abilityTooltips']}
                                        }
                          }
        # guide_template = {"guidedata": {"Hero": f"{hero}",  "Title": f"{re.sub('_', ' ', switcher(hero).title())} {role} Build",
        #                                 "GuideRevision": "1", "Role": dota_role, "AssociatedWorkshopItemID": "0x0000000000000000",
        #                                 "OriginalCreatorID": "0x0000000005550372",
        #                                 'TimeUpdated': hex(timestamp),
        #                                 "ItemBuild": {"Items": itemBuild}
        #                                 }
        #                   }

        role_path = f'hero_guides/builds/{hero}_{role}'

        role_path = f'D:\\projects\\python\\pro-item-builds\\hero_guides\\builds/{hero}_{role}'
        guide_file_path = f'C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote\\guides\\{hero}_{role.lower()}'

        if os.path.exists(f"{role_path}.json"):
            with open(f"{role_path}.json", 'r') as f:
                json_data = json.load(f)
                timestamp = int(json_data['guidedata']['TimeUpdated'], 16)
                # if json_data['guidedata']['AssociatedWorkshopItemID'] == "0x0000000000000000":
                #     print('in')
                #     break
                workshop_id = get_value_from_build_file(
                    guide_file_path, 'AssociatedWorkshopItemID')
                time_published = get_value_from_build_file(
                    guide_file_path, 'TimePublished')
                # timestamp = f.read()

                if json_data['guidedata']['ItemBuild'] == guide_template['guidedata']['ItemBuild'] and \
                        json_data['guidedata']['AbilityBuild'] == json_data['guidedata']['AbilityBuild']:
                    print('true equal')
                    continue
                guide_template['guidedata']['TimePublished'] = time_published
                guide_template['guidedata']['AssociatedWorkshopItemID'] = workshop_id

                guide_template['guidedata']['GuideRevision'] = str(
                    int(json_data['guidedata']['GuideRevision']) + 1)

        with open(f"{role_path}.json", 'w') as f:
            json.dump(guide_template, f, indent=4)

        add_to_build_file(
            guide_template, path=f"{guide_file_path}", timestamp=timestamp)


def add_to_build_file(guide_template, path, timestamp):
    guide_template = str(json.dumps(guide_template, indent=8))
    cleaned = re.sub(r'(?<="):(?!\d)', '\t\t', guide_template)
    cleaned = re.sub(r",", '', cleaned)
    cleaned = re.sub(r"(?<=item)_\d+", '', cleaned)
    files = glob.glob(f"{path}_*.build")

    for file in files:
        # if file != target_file:
        # delete content of all cloud files
        os.remove(file)

    # os.remove(f)
    # # print(f)
    # with open(f, 'w') as file:
    with open(f'{path}_{timestamp}.build', 'w') as buildFile:
        buildFile.write(cleaned[1:len(cleaned)-1].strip())
        pass


def item_builder(itemBuild, items):
    for i, entry in enumerate(items):
        for k, v in entry.items():
            item_build = {}
            j = 0
            for itemDict in v:
                itemKeys = itemDict.keys()
                for item_key in itemKeys:
                    item_build[f'item_{j}'] = f"item_{item_key}"
                    # print(i, j, k, item_key)
                j += 1
            timing = 'Late'
            if i == 0:
                timing = 'Early'
            elif i == 1:
                timing = 'Mid'
            field_title = f"{timing} {k}"
            itemBuild[field_title] = item_build
    return itemBuild


def get_value_from_build_file(file_path, key):
    for file in glob.glob(f"{file_path}_*.build"):
        with open(file, 'r') as build_file:
            for line in build_file:
                if key in line:
                    value = re.search(
                        r'0x.*\"', line)
                    if value:
                        value = value.group().replace('"', '')
                        return value


def unpublished_guides():
    for file in glob.glob(f'C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote\\guides\\*.build'):
        with open(file, 'r') as f:
            published = False
            for line in f:
                if published:
                    break
                if 'TimePublished' in line:
                    published = True
                    value = re.search(
                        r'0x.*\"', line)
                    if value:
                        value = value.group().replace('"', '')
            if not published:
                print(file)

    pass


if __name__ == '__main__':
    # write_build_to_remote({'json_data'}, 'drow_ranger', '7.32e')
    unpublished_guides()
