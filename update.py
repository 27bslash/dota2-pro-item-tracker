import os
import json
from colorthief import ColorThief
from helper_funcs.helper_imports import *
from colours.contrast import compute_contrast
from colours.dominant_colour import get_dominant_colours, get_dominant_color
import shutil
import requests
import traceback


def update_hero_list():
    with open(f"json_files/hero_ids.json", 'w') as f:
        data = json.loads(requests.get(
            'https://api.stratz.com/api/v1/Hero').text)
        hero_dict = {'heroes': []}
        for k in data:
            hero_name = data[k]['shortName']
            hero_id = int(k)
            hero_dict['heroes'].append({'name': hero_name, 'id': hero_id})

        json.dump(hero_dict, f, indent=4)


def make_dir():
    if not os.path.isdir('colours\\ability_images'):
        print('fg')
        os.mkdir('colours\\ability_images')
    for filename in os.listdir("colours\\ability_images"):
        filepath = os.path.join("colours\\ability_images", filename)
        try:
            shutil.rmtree(filepath)
        except OSError:
            os.remove(filepath)
    with open('json_files/hero_ids.json', 'r') as d:
        data = json.load(d)
        for item in data['heroes']:
            hero_name = item['name']
            os.mkdir(f"colours/ability_images/{hero_name}")


def dl_dota2_abilities():
    make_dir()
    datafeed = 'https://www.dota2.com/datafeed/herodata?language=english&hero_id='
    all_abilities = {}
    with open('json_files/hero_ids.json', 'r') as heroes:
        hero_data = json.load(heroes)
        for hero in hero_data['heroes']:
            req = requests.get(f"{datafeed}{hero['id']}")
            with open(f'json_files/detailed_ability_info/{hero["name"]}.json', 'w') as o:
                ability_json = json.loads(
                    req.text)['result']['data']['heroes'][0]
                hero_abilities = {}
                print(hero['name'])
                for ability in ability_json['abilities']:
                    hero_abilities[str(ability['id'])] = ability
                    all_abilities[str(ability['id'])] = ability
                    get_ability_img(ability['name'], hero['name'])
                for talent in ability_json['talents']:
                    hero_abilities[str(talent['id'])] = talent
                    all_abilities[str(talent['id'])] = talent
                json.dump(hero_abilities, o, indent=4)
        with open('json_files/all_abilities.json', 'w') as d:
            json.dump(all_abilities, d, indent=4)


def get_ability_img(ability_name, hero_name):
    if ability_name.replace('_', '').startswith(switcher(hero_name).replace('_', '')):
        with open(f'colours/ability_images/{hero_name}/{ability_name}.jpg', 'wb') as f:
            f.write(requests.get(
                f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/abilities/{ability_name}.png").content)
            print(ability_name)


def get_ability_imgs():
    make_dir()
    with open('json_files/hero_ids.json', 'r') as d:
        data = json.load(d)
        for hero in data['heroes']:
            # print(hero_name)
            hero_name = hero['name']
            # db_out = hero_output.find_one({'hero': hero_name})
            with open('json_files/all_abilities.json', 'r') as f:
                abilities = json.load(f)
                try:
                    for k in abilities:
                        if 'special_bonus' not in abilities[k]['name'] and abilities[k]['name'].replace('_', '').startswith(switcher(hero_name).replace('_', '')):
                            ability_name = abilities[k]['name']
                            with open(f'colours/ability_images/{hero_name}/{ability_name}.jpg', 'wb') as f:
                                f.write(requests.get(
                                    f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/abilities/{ability_name}.png").content)
                                print(ability_name)
                except Exception as e:
                    print('img err', hero_name, traceback.format_exc())


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


def update_stratz_json():
    with open(f"json_files/stratz_talents.json", 'w') as f:
        f.write(json.dumps(json.loads(requests.get(
            'https://api.stratz.com/api/v1/Hero').text), indent=4))
    with open(f"json_files/stratz_abilities.json", 'w') as f:
        f.write(json.dumps(json.loads(requests.get(
            'https://api.stratz.com/api/v1/Ability').text), indent=4))
    with open(f"json_files/stratz_items.json", 'w') as f:
        f.write(json.dumps(json.loads(requests.get(
            'https://api.stratz.com/api/v1/Item').text), indent=4))
    update_basic_id_json('stratz_items', 'items', 'items')


def update_basic_id_json(input, output, dic_name):
    dictionary = {dic_name: []}
    with open(f"json_files/{input}.json", 'r') as f:
        data = json.load(f)
        for _id in data:
            try:
                dictionary[dic_name].append(
                    {'name': data[_id]['shortName'], "id": data[_id]['id']})
            except:
                print(traceback.format_exc(), data[_id]['shortName'])
    with open(f'json_files/{output}.json', 'w') as f:
        json.dump(dictionary, f, indent=2)


def update_app():
    print('updating hero list')
    # update_hero_list()
    print('updating json....')
    update_stratz_json()
    print('downloading abilities...')
    dl_dota2_abilities()
    print('updating_talents...')
    update_talents()
    print('updating hero colours....')
    compute_contrast()
    print('fini')


def update_talents():
    db_methods = Db_insert()
    with open("json_files/hero_ids.json", 'r') as f:
        data = json.load(f)
        for hero in data['heroes']:
            db_methods.insert_talent_order(hero['id'])


if __name__ == '__main__':
    update_app()
    # chunk_stratz_abilites()
    # update_hero_list()
