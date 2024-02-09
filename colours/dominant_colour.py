import json
import os
from colorthief import ColorThief
from helper_funcs.database.collection import db,hero_list


def get_dominant_hero_color():
    pass


def get_dominant_colours():
    hero_colours_output = {'colors': []}
    ability_colours_output = {'colors': []}
    data = db['hero_list'].find_one({}, {'_id': 0})
    for hero in hero_list:
        hero_name = hero['name']
        avg_r = 0
        avg_b = 0
        avg_g = 0
        count = 0
        print(hero_name)
        for i, filename in enumerate(os.listdir(f'D:\\projects\\python\\pro-item-builds\\colours\\ability_images\\{hero_name}')):
            try:
                c_t = ColorThief(
                    f"D:\\projects\\python\\pro-item-builds\\colours\\ability_images\\{hero_name}\\{filename}")
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
                print('dir err: ', filename, hero_name, e)
        # print([sum(i) for i in avg_color])
            try:
                rgb = (r, g, b)
                o = {'ability': filename.replace(
                    '.jpg', ''), 'color': rgb}
                ability_colours_output['colors'].append(o)
            except Exception as e:
                print('output error: ', hero_name, e)
        avg_r /= count
        avg_g /= count
        avg_b /= count
        hero_rgb = (avg_r, avg_g, avg_b)
        o = {'hero': hero_name, 'color': list(
            hero_rgb), 'uncontrasted': list(hero_rgb)}
        hero_colours_output['colors'].append(o)
    # with open('colours/ability_colours.json', 'w') as outfile:
    #     json.dump(ability_colours_output, outfile, indent=4)
    # with open('colours/hero_colours.json', 'w') as outfile:
    #     json.dump(hero_colours_output, outfile, indent=4)
    return hero_colours_output


if __name__ == '__main__':
    get_dominant_colours()
