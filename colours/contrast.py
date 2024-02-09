import json
import math
import colorsys
import shutil
from colours.dominant_colour import get_dominant_colours
from helper_funcs.database.collection import db


def compute_contrast():
    output = {'colors': []}
    hero_colors = get_dominant_colours()

    for hero_color in hero_colors['colors']:
        print(hero_color)
        contrast = contrast_ratio(luminance(
            hero_color['color'][0], hero_color['color'][1], hero_color['color'][2]), luminance(41, 38, 38))
        while contrast > 0.847:
            hsl = colorsys.rgb_to_hsv(hero_color['color'][0], hero_color['color']
                                      [1], hero_color['color'][2])
            hsl = list(hsl)
            hsl[2] += 1
            new_rgb = colorsys.hsv_to_rgb(hsl[0], hsl[1], hsl[2])
            new_rgb = list(new_rgb)
            contrast = contrast_ratio(
                luminance(new_rgb[0], new_rgb[1], new_rgb[2]), luminance(41, 38, 38))
            hero_color['uncontrasted'][0] = hero_color['uncontrasted'][0]
            hero_color['uncontrasted'][1] = hero_color['uncontrasted'][1]
            hero_color['uncontrasted'][2] = hero_color['uncontrasted'][2]
            hero_color['color'][0] = new_rgb[0]
            hero_color['color'][1] = new_rgb[1]
            hero_color['color'][2] = new_rgb[2]
        # output['colors'].append({'hero': hero['hero'], 'color': [
        #     hero['color'][0], hero['color'][1], hero['color'][2]]},)
        output['colors'].append(hero_color)
        # break
    with open('D:\\projects\\python\\pro-item-builds\\colours\\hero_colours.json', 'w') as outfile:
        json.dump(output, outfile, indent=4)
        # shutil.rmtree('colours/ability_images')
    db['hero_colors'].find_one_and_update({}, {"$set": output}, upsert=True)


def luminance(r, g, b):
    a = map(lambda v:
            v/255 / 12.92 if v /
            255 <= 0.03928 else math.pow((v/255 + 5) / 1.055, 2.4),
            [r, g, b])
    a = list(a)
    return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722


def contrast_ratio(text_color, base):
    # if a > b:
    #     print('treu', a, b, (b+0.05)/(a+0.05))
    #     return (b+0.05)/(a+0.05)
    # else:
    #     print('b')
    #     return (a+0.05)/(b+0.05)
    return (text_color+0.05) / (base+0.05) if base > text_color else (base+0.05) / (text_color+0.05)


if __name__ == '__main__':
    compute_contrast()
    # print(rgb_to_hsv(25, 0, 213))
