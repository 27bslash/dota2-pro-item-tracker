import os
import json
from colorthief import ColorThief
from helper_funcs.helper_imports import *
from colours.contrast import compute_contrast
from colours.dominant_colour import get_dominant_colours, get_dominant_color
from accounts.download_acount_ids import update_pro_accounts
import shutil
import requests
import traceback

hero_list = db['hero_list'].find_one({}, {'_id': 0})


def update_hero_list():
    data = json.loads(requests.get(
        'https://api.stratz.com/api/v1/Hero').text)
    hero_dict = {'heroes': []}
    for k in data:
        hero_name = data[k]['shortName']
        hero_id = int(k)
        hero_dict['heroes'].append({'name': hero_name, 'id': hero_id})

    db['hero_list'].find_one_and_update(
        {}, {"$set": hero_dict}, upsert=True)


# def upload_hero_list():
#     with open('json_files/hero_ids.json', 'r') as f:
#         data = json.load(f)
#         db['hero_list'].find_one_and_update(
#             {}, {"$set": {'heroes': data['heroes']}})


def make_dir():
    if not os.path.isdir('colours\\ability_images'):
        os.mkdir('colours\\ability_images')
    for filename in os.listdir("colours\\ability_images"):
        filepath = os.path.join("colours\\ability_images", filename)
        try:
            shutil.rmtree(filepath)
        except OSError:
            os.remove(filepath)
    for hero in hero_list['heroes']:
        hero_name = hero['name']
        os.mkdir(f"colours/ability_images/{hero_name}")


def dl_dota2_abilities():
    make_dir()
    datafeed = 'https://www.dota2.com/datafeed/herodata?language=english&hero_id='
    for hero in hero_list['heroes']:
        req = requests.get(f"{datafeed}{hero['id']}")
        ability_json = json.loads(
            req.text)['result']['data']['heroes'][0]
        hero_abilities = {}
        print(hero['name'])
        for ability in ability_json['abilities']:
            hero_abilities[str(ability['id'])] = ability
            get_ability_img(ability['name'], hero['name'])
        for talent in ability_json['talents']:
            hero_abilities[str(talent['id'])] = talent
        db['individual_abilities'].find_one_and_update(
            {'hero': hero['name']}, {"$set": {"abilities": hero_abilities}}, upsert=True)
        # json.dump(hero_abilities, o, indent=4)


def get_ability_img(ability_name, hero_name):
    if ability_name.replace('_', '').startswith(switcher(hero_name).replace('_', '')):
        with open(f'colours/ability_images/{hero_name}/{ability_name}.jpg', 'wb') as f:
            f.write(requests.get(
                f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/abilities/{ability_name}.png").content)
            print(ability_name)


def chunk_stratz_abilites():
    with open('json_files/hero_ids.json', 'r') as h_f:
        d_heroes = json.load(h_f)
        with open('json_files/stratz_abilities.json', 'r') as f:
            data = json.load(f)
            for hero in d_heroes['heroes']:
                d = {}
                for k in data:
                    if 'name' in data[k]:
                        if switcher(hero['name']) in data[k]['name'] or hero['name'].lower() in data[k]['name']:
                            d[k] = data[k]
                with open(f'json_files/detailed_ability_info/{hero["name"]}.json', 'w') as w:
                    # print(hero['name'])
                    json.dump(d, w, indent=4)


def update_stratz_json(url, collection):
    req = requests.get(url).json()
    db_data = db[collection].find_one({}, {'_id': 0})
    if not db_data or not req == db_data and len(req) > len(db_data):
        db[collection].find_one_and_update(
            {}, {"$set": req}, upsert=True)

    update_basic_id_json('all_items', 'item_ids', 'items')
    # req = requests.get('https://api.stratz.com/api/v1/Hero').json()
    # b = req == json.load(open('json_files/stratz_talents.json'))
    # if not b and len(req) > 2000:
    #     db[collection].find_one_and_update(
    #         {}, {"$set": {'talents': req}}, upsert=True)

    # req = requests.get('https://api.stratz.com/api/v1/Item').json()
    # b = req == json.load(open('json_files/stratz_abilities.json'))
    # if not b and len(req) > 2000:
    #     db['all_items'].find_one_and_update(
    #         {}, {"$set": {'items': req}}, upsert=True)
    # with open(f"json_files/stratz_talents.json", 'w') as f:
    #     f.write(json.dumps(json.loads(requests.get(
    #         'https://api.stratz.com/api/v1/Hero').text), indent=4))
    # with open(f"json_files/stratz_abilities.json", 'w') as f:
    #     f.write(json.dumps(json.loads(requests.get(
    #         'https://api.stratz.com/api/v1/Ability').text), indent=4))
    # with open(f"json_files/stratz_items.json", 'w') as f:
    #     f.write(json.dumps(json.loads(requests.get(
    #         'https://api.stratz.com/api/v1/Item').text), indent=4))


def update_basic_id_json(input_collection, output_collection, dic_name):
    dictionary = {dic_name: []}
    data = db[input_collection].find_one({}, {'_id': 0})
    for _id in data:
        dictionary[dic_name].append(
            {'name': data[_id]['shortName'], "id": data[_id]['id']})
    db[output_collection].find_one_and_update(
        {}, {"$set": dictionary}, upsert=True)


def update_talents():
    db_methods = Db_insert()
    for hero in hero_list['heroes']:
        db_methods.insert_talent_order(hero['id'])


def update_minimap_icons():
    import subprocess
    import shutil
    subprocess.check_call('npm install dota2-minimap-hero-sprites', shell=True)
    shutil.copy('node_modules/dota2-minimap-hero-sprites/assets/images/minimap_hero_sheet.png',
                'static/minimap_icons/images/minimap_hero_sheet.png')
    shutil.copy('node_modules/dota2-minimap-hero-sprites/assets/stylesheets/dota2minimapheroes.css',
                'static/minimap_icons/stylesheets/dota2minimapheroes.css')
    shutil.rmtree('node_modules')


def update_app():
    print('uploading hero list')
    update_hero_list()
    print('updating json....')
    update_stratz_json('https://api.stratz.com/api/v1/Item', 'all_items')
    update_stratz_json('https://api.stratz.com/api/v1/Hero', 'all_talents')
    update_stratz_json(
        'https://api.stratz.com/api/v1/Ability', 'all_abilities')
    print('downloading abilities...')
    dl_dota2_abilities()
    print('updating_talents...')
    update_talents()
    print('updating hero colours....')
    compute_contrast()
    print('updating minimap icons...')
    update_minimap_icons()
    print('updating account ids')
    update_pro_accounts()
    print('fini')


def weekly_update():
    update_stratz_json('https://api.stratz.com/api/v1/Item', 'all_items')
    update_stratz_json('https://api.stratz.com/api/v1/Hero', 'all_talents')
    update_stratz_json(
        'https://api.stratz.com/api/v1/Ability', 'all_abilities')
    update_talents()


if __name__ == '__main__':
    # update_stratz_json('https://api.stratz.com/api/v1/Item', 'all_items')
    # update_stratz_json('https://api.stratz.com/api/v1/Hero', 'all_talents')
    # update_stratz_json(
    #     'https://api.stratz.com/api/v1/Ability', 'all_abilities')
    # dl_dota2_abilities()
    update_app()
    # chunk_stratz_abilites()
    # update_hero_list()
    # upload_hero_list()
