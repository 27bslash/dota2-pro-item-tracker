import json
import asyncio
import aiohttp
import traceback
from helper_funcs.helper_functions import *
import pymongo
from pymongo import MongoClient
output = []

cluster = MongoClient(
    'mongodb://dbuser:a12345@ds211774.mlab.com:11774/pro-item-tracker', retryWrites=False)
db = cluster['pro-item-tracker']
hero_output = db['heroes']


async def async_get(url, hero_name):
    print('url', url)
    try:
        res = hero_urls.delete_many({'hero': hero_name})
    except Exception as e:
        print(traceback.format_exc())
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                resp = await response.json()
                with open(f'json_files/hero_output/{hero_name}.json', 'w') as outfile:
                    print(f"Successfully got url {url}.", outfile)
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
                        if hero_id == get_id(hero_name):
                            abilities = p['ability_upgrades_arr']
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
                                hero_output.insert_one(
                                    {'time_started': get_time(p['start_time']), 'unix_time': p['start_time'], 'hero': hero_name, 'duration': p['duration'],
                                     'name': get_info(resp['match_id'], 'name'), 'mmr': get_info(resp['match_id'], 'mmr'),
                                     'lvl': p['level'], 'gold': p['gold_t'].copy()[::-1][0], 'hero_damage': p['hero_damage'],
                                     'tower_damage': p['tower_damage'], 'gpm': p['gold_per_min'], 'xpm': p['xp_per_min'],
                                     'kills': p['kills'], 'deaths': p['deaths'], 'assists': p['assists'], 'last_hits': p['last_hits'],
                                     'role': p['lane'], 'win': p['win'], 'id': resp['match_id'],
                                     'starting_items': starting_items,
                                     'final_items': main_items, 'backpack': bp_items, 'item_neutral': get_item_name(p['item_neutral']),
                                        'abilities': get_ability_name(abilities), 'items': purchase_log})
    except Exception as e:
        print("Unable to get url {} due to {}.".format(
            url, traceback.format_exc()))


async def main(urls, hero_name):
    ret = await asyncio.gather(*[async_get(url, hero_name) for url in urls])


async def test(urls, hero_name):
    urls = get_urls_from()
    await asyncio.gather(*[async_get(url, hero_name) for url in urls])


def get_info(m_id, search):
    output = []
    print('get_info', m_id, type(m_id))
    try:
        data = hero_urls.find_one({'id': str(m_id)})
        print(data)
    except Exception as e:
        print(traceback.format_exc())
    return data[search]


def delete_output():
    global output
    output = []
