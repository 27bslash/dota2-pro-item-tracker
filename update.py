import os
import json
from helper_funcs.helper_imports import *
from colours.contrast import compute_contrast
from helper_funcs.accounts.download_acount_ids import update_pro_accounts
import shutil
import requests
import traceback
import re
hero_list = db['hero_list'].find_one({}, {'_id': 0})


def update_hero_list():
    data = json.loads(requests.get(
        'https://www.dota2.com/datafeed/herolist?language=english').text)
    hero_dict = {'heroes': []}
    for dic in data['result']['data']['heroes']:
        hero_name = switcher(dic['name_loc'].lower().replace(' ', '_'))
        hero_id = int(dic['id'])
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
        hero_talents = {}
        print(hero['name'])
        for ability in ability_json['abilities']:
            hero_abilities[str(ability['id'])] = ability
            get_ability_img(ability['name'], hero['name'])
        for i, talent in enumerate(ability_json['talents']):
            talent['slot'] = i
            hero_talents[str(talent['id'])] = talent
        db['individual_abilities'].find_one_and_update(
            {'hero': hero['name']}, {"$set": {"abilities": hero_abilities, 'talents': hero_talents}}, upsert=True)
        # json.dump(hero_abilities, o, indent=4)


def get_ability_img(ability_name, hero_name):
    if ability_name.replace('_', '').startswith(hero_name.replace('_', '')):
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
    req = requests.get(url)
    db_data = db[collection].find_one({}, {'_id': 0})
    # print(req.status_code)
    if req.status_code != 200:
        print(f"request failed  {req.status_code} {url}")
    if not db_data or not req.json() == db_data and len(req.json()) > len(db_data):
        db[collection].find_one_and_update(
            {}, {"$set": req.json()}, upsert=True)


def graphql():
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJodHRwczovL3N0ZWFtY29tbXVuaXR5LmNvbS9vcGVuaWQvaWQvNzY1NjExOTgwNDk3MjMyNTAiLCJ1bmlxdWVfbmFtZSI6IkFkZHJlc3MgbWUgYnkgbXkgaHVzYmFuZCdzIHJhbmsiLCJTdWJqZWN0IjoiMzIyMzFkMDgtNzk0NS00YzNhLTg5ZGItMzc0NzFiMTg4NGYxIiwiU3RlYW1JZCI6Ijg5NDU3NTIyIiwibmJmIjoxNjMwODUwNzM1LCJleHAiOjE2NjIzODY3MzUsImlhdCI6MTYzMDg1MDczNSwiaXNzIjoiaHR0cHM6Ly9hcGkuc3RyYXR6LmNvbSJ9.DLh7iVwaTemZIo1BQ1o6ApGS-5AoYKBewCCqP4lDWa4'
    query = """
    query {
        constants{
            items {
            id
            name
            displayName
            language {
                description
                lore
            }
            
            stat {
                cost
                cooldown
                manaCost
            }
            attributes {
                name
                value
            }
            }
        }
    }
    """
    url = 'https://api.stratz.com/graphql'
    headers = {'Authorization': 'Bearer ' +token}
    r = requests.post(url, headers=headers, json={'query': query})
    if r.status_code == 200:
        return r.json()['data']['constants']
    else:
        print(f"query failed {r.status_code} {r.text}")


def insert_all_items():
    stratz_data = graphql()
    if not stratz_data:
        return
    opend = requests.get('https://api.opendota.com/api/constants/items').json()
    srt = dict(sorted(opend.items(), key=lambda k: k[1]['id']))
    for k, v in srt.items():
        _id = v['id']
        for item in stratz_data['items']:
            if item['id'] == _id:
                item['attrib'] = v['attrib']
                break
    db['all_items'].find_one_and_update(
        {}, {"$set": stratz_data}, upsert=True)


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
    subprocess.check_call('npm install dota2-minimap-hero-sprites', shell=True)
    shutil.copy('node_modules/dota2-minimap-hero-sprites/assets/images/minimap_hero_sheet.png',
                'static/minimap_icons/images/minimap_hero_sheet.png')
    shutil.copy('node_modules/dota2-minimap-hero-sprites/assets/stylesheets/dota2minimapheroes.css',
                'static/minimap_icons/stylesheets/dota2minimapheroes.css')
    shutil.rmtree('node_modules')


def update_talent_names():
    hero_list = db['hero_list'].find_one()['heroes']
    for hero in hero_list:
        talents = db['individual_abilities'].find_one(
            {'hero': hero['name']})['talents']
        extract_special_values(talents, hero['name'])
        # break


def extract_special_values(talents, hero):
    for talent in talents:
        try:
            special_values = talents[talent]['special_values']
            test_string = talents[talent]['name_loc']

            clean = val(test_string, special_values)

            talents[talent]['name_loc'] = clean
            db['individual_abilities'].find_one_and_update(
                {'hero': hero},
                {'$set': {'talents': talents}
                 }, upsert=True)
        except Exception as e:
            print('Exception: ', hero, talent,
                  talents[talent]['name_loc'], traceback.format_exc())


def val(text, special_values):
    # print(text)
    pattern = re.compile("s:(\w*)")
    result = ''
    for value in special_values:
        special_val = ''
        if len(result) > 0:
            text = result
        if 's:' not in text:
            return text
        match = pattern.search(text).group(1)
        if value['name'] == match:
            if len(value['values_float']) > 0:
                special_val += f"{round(value['values_float'][0], 2)}"
            else:
                special_val += str(value['values_int'][0])
            if value['is_percentage']:
                special_val += '%'
            regex = '{s:' + value['name'] + '}'
            result = re.sub(regex, special_val, text)
    return result


def update_app():
    print('uploading hero list')
    update_hero_list()
    print('updating json....')
    insert_all_items()
    update_stratz_json(
        'https://api.stratz.com/api/v1/Ability', 'all_abilities')
    print('downloading abilities...')
    dl_dota2_abilities()
    print('updating_talents...')
    update_talents()
    update_talent_names()
    print('updating hero colours....')
    compute_contrast()
    print('updating minimap icons...')
    update_minimap_icons()
    print('updating account ids')
    update_pro_accounts()
    print('fini')


def weekly_update():
    insert_all_items()
    # update_stratz_json(
    #     'https://api.stratz.com/api/v1/Ability', 'all_abilities')
    # update_talents()


if __name__ == '__main__':
    # update_stratz_json('https://api.stratz.com/api/v1/Item', 'all_items')
    # update_stratz_json('https://api.stratz.com/api/v1/Hero', 'all_talents')
    # update_stratz_json(
    #     'https://api.stratz.com/api/v1/Ability', 'all_abilities')
    # db_methods = Db_insert()
    # db_methods.insert_talent_order(66)
    update_app()
    # dl_dota2_abilities()
    # chunk_stratz_abilites()
    # update_hero_list()
    # upload_hero_list()
