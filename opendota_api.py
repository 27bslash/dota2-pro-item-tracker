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
acc_ids = db['account_ids']
parse = db['parse']


async def account_id(m_id, hero_name):
    url = f'https://api.opendota.com/api/matches/{m_id}'
    print(url)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                resp = await response.json()
                print(str(resp['match_id']))
                for i in range(10):
                    # 10 players
                    p = resp['players'][i]
                    hero_id = p['hero_id']
                    if hero_id == get_id(hero_name):
                        # check if one of the players matches search
                        check = acc_ids.find_one(
                            {'account_id': p['account_id']})
                        if check is None:
                            acc_ids.insert_one(
                                {'name': get_info(
                                    resp['match_id'], 'name', hero_name), 'account_id': p['account_id']}
                            )
    except Exception as e:
        print("Unable to get url {} due to {}.".format(
            url, traceback.format_exc()))


async def async_get(m_id, hero_name):
    url = f'https://api.opendota.com/api/matches/{m_id}'
    check = hero_output.find_one({'hero': hero_name, 'id': m_id})
    if check is None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url) as response:
                    resp = await response.json()
                    match_id = int(resp['match_id'])
                    print(f"successfully got {match_id}")
                    starting_items = []
                    main_items = []
                    bp_items = []
                    purchase_log = []
                    abilities = []
                    roles_arr = []
                    all_roles = []
                    for i in range(10):
                        try:
                            p = resp['players'][i]
                            lane = p['lane']
                            gpm = p['gold_per_min']
                            lane_eff = p['lane_efficiency']
                            sen_placed = p['sen_placed']
                            slot = p['player_slot']
                            arr = [lane, gpm,
                                   lane_eff, sen_placed, slot, p['is_roaming']]
                            roles_arr.append(arr)
                        except Exception as e:
                            print(m_id, traceback.format_exc())
                            pass
                    all_roles.append(roles_arr)
                    for i in range(10):
                        # 10 players
                        p = resp['players'][i]
                        hero_id = p['hero_id']
                        if hero_id == get_id(hero_name):
                            abilities = p['ability_upgrades_arr']
                            # check if one of the players matches search
                            purchase_log = p['purchase_log']
                            if purchase_log:
                                role = roles(all_roles[0], p['player_slot'])
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
                                     'name': get_info(match_id, 'name', hero_name), 'account_id': p['account_id'], 'role': role, 'mmr': get_info(match_id, 'mmr', hero_name),
                                     'lvl': p['level'], 'gold': p['gold_t'].copy()[::-1][0], 'hero_damage': p['hero_damage'],
                                     'tower_damage': p['tower_damage'], 'gpm': p['gold_per_min'], 'xpm': p['xp_per_min'],
                                     'kills': p['kills'], 'deaths': p['deaths'], 'assists': p['assists'], 'last_hits': p['last_hits'],
                                     'win': p['win'], 'id': match_id,
                                     'starting_items': starting_items,
                                     'final_items': main_items, 'backpack': bp_items, 'item_neutral': get_item_name(p['item_neutral']),
                                     'abilities': get_ability_name(abilities), 'items': purchase_log})
                            else:
                                parse.insert_one({'id': m_id})
        except Exception as e:
            print("Unable to get url", traceback.format_exc())


def roles(s, p_slot):
    # use lane_role with lane
    # radiant safe lane is always lane 1 for dire it's lane 3
    # take eff arr top 3 are core then label according to lane
    # convert dire lanes 1 to 3
    sen_count = [0, 0]
    start = 5
    end = 10
    side = []
    p_roles = []
    is_radiant = False
    # print(p_slot, s)
    if p_slot < 5:
        start = 0
        end = 5
        is_radiant = True
    for i in range(start, end, 1):
        lane = s[i][0]
        # print(lane)
        if not is_radiant:
            # print('dire', lane)
            if lane == 1:
                # print('off')
                lane = 3
            elif lane == 3:
                # print('safe')
                lane = 1
        gpm = s[i][1]
        lane_eff = s[i][2]
        sen_placed = s[i][3]
        slot = s[i][4]
        roles = [lane, gpm, lane_eff, sen_placed, slot, s[i][5]]
        p_roles.append(roles)
    side.append(p_roles)
    # print('side',is_radiant,side)
    eff = sorted(side[0], key=lambda x: x[2], reverse=True)
    sen = sorted(side[0], key=lambda x: x[3], reverse=True)
    for i, player in enumerate(eff):
        # print('pro_player slot: ', p_slot, player[4], 'lane: ',player[0], i)
        # print('p', player[0], i)
        role = ''
        lane = player[0]
        slot = player[4]
        is_roaming = player[5]
        lane_eff = player[2]
        if i < 3:
            role = 'core'
        if p_slot == sen[0][4]:
            return 'Hard Support'
        elif p_slot == slot and is_roaming:
            return 'Roaming'
        elif p_slot == slot and lane == 2 and role == 'core':
            return 'Midlane'
        elif lane == 3 and p_slot == slot and role == 'core':
            return 'Offlane'
        elif p_slot == slot and lane == 1 and role == 'core':
            return 'Safelane'
        elif lane == 3 and p_slot == player[4] and role is not 'core':
            return 'Support'


async def main(urls, hero_name):
    # urls = ['5527705678']
    ret = await asyncio.gather(*[async_get(url, hero_name) for url in urls])


async def get_acc_ids(urls, hero_name):
    ret = await asyncio.gather(*[account_id(url, hero_name) for url in urls])


def get_info(m_id, search, hero):
    print(m_id, search, hero)
    data = hero_urls.find_one({'id': m_id, 'hero': hero})
    return data[search]





# asyncio.run(main('x', 'zeus'))
