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
                with open('json_files/opendota_output.json', 'w') as outfile:
                    print(f"Successfully got url {url}.")
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
                        # print(hero_id)
                        if hero_id == get_id(hero_name):
                            abilities = p['ability_upgrades_arr']
                            # print('id-check', hero_id, get_id(hero_name))
                            # check if one of the players matches search
                            purchase_log = p['purchase_log']
                            if purchase_log:
                                print(f"{hero_name} should reach here.")
                                for purchase in purchase_log:
                                    if purchase['time'] <= 0:
                                        starting_items.append(
                                            {'key': purchase['key'], 'time': 0})
                                rev = purchase_log.copy()[::-1]
                                main_items = get_most_recent_items(
                                    rev, 6, p)
                                bp_items = get_most_recent_items(
                                    rev, 4, p)
                                if p['duration'] > 0:
                                    p['duration'] = str(datetime.timedelta(
                                        seconds=p['duration']))
                                else:
                                    p['duration'] = 0
                                output.append(
                                    {'hero': hero_name, 'duration': p['duration'], 'name': get_info('name', resp['match_id'], hero_name), 'mmr': get_info('mmr', resp['match_id'], hero_name),
                                     'kills': p['kills'], 'deaths': p['deaths'], 'assists': p['assists'], 'last_hits': p['last_hits'],
                                     'role': p['lane'], 'win': p['win'], 'id': resp['match_id'],
                                     'starting_items': starting_items,
                                     'final_items': main_items, 'backpack': bp_items, 'item_neutral': get_item_name(p['item_neutral']),
                                        'abilities': get_ability_name(abilities), 'items': purchase_log})
                    json.dump(output, outfile, indent=4)
    except Exception as e:
        print("Unable to get url {} due to {}.".format(
            url, traceback.format_exc()))


async def main(urls, hero_name):
    ret = await asyncio.gather(*[async_get(url, hero_name) for url in urls])


def get_info(x, m_id, hero_name):
    hero_name = pro_name(hero_name)
    output = []
    with open(f'json_files/hero_urls/{hero_name}.json', 'r') as f:
        data = json.load(f)
        for i in data:
            if str(m_id) in i['id']:
                return i[x]


def delete_output():
    global output
    output = []
