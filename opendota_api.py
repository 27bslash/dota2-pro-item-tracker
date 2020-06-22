import json
import asyncio
import aiohttp
import traceback
from app import switcher
from helper_funcs.helper_functions import *
output = []


async def async_get(url, hero_name):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                resp = await response.json()
                print("Successfully got url {}.".format(url))
                with open('json_files/opendota_output.json', 'w') as outfile:
                    match_id = str(resp['match_id'])
                    starting_items = []
                    main_items = []
                    bp_items = []
                    purchase_log = []
                    abilities = []
                    for i in range(10):
                        # 10 players
                        p = resp['players'][i]
                        hero_id = p['hero_id']
                        # print(hero_id)
                        if hero_id == get_id(hero_name):
                            abilities = p['ability_upgrades_arr']
                            # print('id-check', hero_id, get_id(hero_name))
                            # check if one of the players matches search
                            purchase_log = p['purchase_log']
                            if purchase_log:
                                for purchase in purchase_log:
                                    if purchase['time'] <= 0:
                                        starting_items.append(
                                            {'key': purchase['key'], 'time': 0})
                                rev = purchase_log.copy()[::-1]
                                main_items = get_most_recent_items(
                                    rev, 6, p)
                                bp_items = get_most_recent_items(
                                    rev, 4, p)
                                output.append(
                                    {'hero': hero_name, 'duration': p['duration'], 'name': p['personaname'], 'role': p['lane'], 'win': p['win'], 'id': resp['match_id'],
                                     'starting_items': starting_items,
                                     'final_items': main_items, 'backpack': bp_items,
                                        'abilities': get_ability_name(abilities), 'items': purchase_log})
                    json.dump(output, outfile, indent=4)
    except Exception as e:
        print("Unable to get url {} due to {}.".format(
            url, traceback.format_exc()))


async def main(urls, hero_name):
    ret = await asyncio.gather(*[async_get(url, hero_name) for url in urls])


def delete_output():
    global output
    output = []
