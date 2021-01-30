import os
import json
from colorthief import ColorThief
from helper_funcs.helper_functions import *
from contrast import *


def make_dir():
    for filename in os.listdir("json_files\hero_abilities"):
        filepath = os.path.join("json_files\hero_abilities", filename)
        try:
            shutil.rmtree(filepath)
        except OSError:
            os.remove(filepath)
    with open('json_files/hero_ids.json', 'r') as d:
        data = json.load(d)
        for item in data['heroes']:
            hero_name = item['name']
            os.mkdir(f"json_files/hero_abilities/{hero_name}")


def get_ability_imgs():
    make_dir()
    with open('json_files/hero_ids.json', 'r') as d:
        data = json.load(d)
        for item in data['heroes']:
            # print(hero_name)
            hero_name = item['name']
            db_out = hero_output.find_one({'hero': hero_name})
            try:
                for ability in db_out['abilities']:
                    if 'special_bonus' not in ability['img']:
                        ability_name = ability['img']
                        with open(f'json_files/hero_abilities/{hero_name}/{ability_name}.jpg', 'wb') as f:
                            f.write(requests.get(
                                f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/abilities/{ability_name}_hp1.png?v=5933967").content)
                            print(ability_name)
            except Exception as e:
                print('img err', hero_name)


def chunk_stratz_abilites():
    with open('json_files/hero_ids.json', 'r') as h_f:
        d_heroes = json.load(h_f)
        with open('json_files/stratz_abilities.json', 'r') as f:
            data = json.load(f)
            for hero in d_heroes['heroes']:
                d = {}
                for k in data:
                    if 'name' in data[k]:
                        if hero['name'] == 'hoodwink':
                            print(data[k]['name'])
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
        # print(dictionary)
        json.dump(dictionary, f, indent=2)


def get_dominant_ability_color():
    c_array = []
    output = {'colors': []}
    with open('json_files/ability_colours.json', 'w') as outfile:
        with open('json_files/hero_ids.json', 'r') as f:
            data = json.load(f)
            for item in data['heroes']:
                hero_name = item['name']
                avg_r = 0
                avg_b = 0
                avg_g = 0
                count = 0
                for i, filename in enumerate(os.listdir(f'json_files/hero_abilities/{hero_name}')):
                    try:
                        c_t = ColorThief(
                            f"json_files/hero_abilities/{hero_name}/{filename}")
                        d_c = c_t.get_color(quality=1)
                        r = d_c[0]
                        g = d_c[1]
                        b = d_c[2]
                        # print(hero_name)
                    except Exception as e:
                        print('dir err: ', filename, hero_name, e)

                # print([sum(i) for i in avg_color])
                    try:
                        rgb = (r, g, b)
                        o = {'ability': filename.replace(
                            '.jpg', ''), 'color': rgb}
                        output['colors'].append(o)
                    except Exception as e:
                        print('output error: ', hero_name, e)
        json.dump(output, outfile, indent=4)


def get_dominant_color():
    c_array = []
    output = {'colors': []}
    with open('json_files/hero_colours.json', 'w') as outfile:
        with open('json_files/hero_ids.json', 'r') as f:
            data = json.load(f)
            for item in data['heroes']:
                hero_name = item['name']
                avg_r = 0
                avg_b = 0
                avg_g = 0
                count = 0
                for i, filename in enumerate(os.listdir(f'json_files/hero_abilities/{hero_name}')):
                    try:
                        c_t = ColorThief(
                            f"json_files/hero_abilities/{hero_name}/{filename}")
                        d_c = c_t.get_color(quality=1)
                        r = d_c[0]
                        g = d_c[1]
                        b = d_c[2]
                        avg_r += r
                        avg_g += g
                        avg_b += b
                        count += 1
                        # print(hero_name)
                    except Exception as e:
                        print(filename, hero_name, e)
                # print([sum(i) for i in avg_color])
                try:
                    avg_r /= count
                    avg_g /= count
                    avg_b /= count
                    rgb = (avg_r, avg_g, avg_b)
                    o = {'hero': hero_name, 'color': rgb}
                    output['colors'].append(o)
                except Exception as e:
                    print(hero_name, e)
        json.dump(output, outfile, indent=4)


def update_app():
    print('updating json....')
    update_stratz_json()
    print('updating ability images....')
    get_ability_imgs()
    print('updating hero colours....')
    get_dominant_ability_color()
    get_dominant_color()
    compute_contrast()
    print('chunking abilites....')
    chunk_stratz_abilites()
    print('fini')


def update_talents():
    db_methods = Db_insert()
    with open("json_files/hero_ids.json", 'r') as f:
        data = json.load(f)
        for hero in data['heroes']:
            db_methods.insert_talent_order(hero['name'])


if __name__ == '__main__':
    # update_app()
    get_dominant_color()
