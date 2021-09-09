import json
import asyncio
import aiohttp
import traceback
from helper_funcs.hero import Hero
from helper_funcs.abilities import Talents, detailed_ability_info
from helper_funcs.items import Items
from helper_funcs.database.db import db
import datetime
import pymongo

hero_urls = db['urls']
hero_output = db['heroes']
acc_ids = db['account_ids']


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
    dupe_check = hero_output.find_one({'hero': hero_name, 'id': m_id})
    bad_id_check = db['dead_games'].find_one(
        {'id': m_id, 'count': {"$gt": 10}})
    if dupe_check is not None or bad_id_check is not None:
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                hero_methods = Hero()
                item_methods = Items()
                resp = await response.json()
                match_id = int(resp['match_id'])
                print(f"successfully got {match_id}")
                hero_ids = [player['hero_id'] for player in resp['players']]
                rad_draft = [hero_methods.hero_name_from_hero_id(
                    player['hero_id']) for player in resp['picks_bans'] if player['is_pick'] and player['team'] == 0 and player['hero_id'] in hero_ids]
                dire_draft = [hero_methods.hero_name_from_hero_id(
                    player['hero_id']) for player in resp['picks_bans'] if player['is_pick'] and player['team'] == 1 and player['hero_id'] in hero_ids]
                hero_bans = [hero_methods.hero_name_from_hero_id(
                    ban['hero_id']) for ban in resp['picks_bans'] if ban['is_pick'] == False]
                for i in range(10):
                    p = resp['players'][i]
                    hero_id = p['hero_id']
                    if p['randomed'] and p['isRadiant']:
                        rad_draft.append(
                            hero_methods.hero_name_from_hero_id(hero_id))
                    if p['randomed'] and not p['isRadiant']:
                        dire_draft.append(
                            hero_methods.hero_name_from_hero_id(hero_id))
                for i in range(10):
                    p = resp['players'][i]
                    hero_id = p['hero_id']
                    roles_arr = [(p['lane'], p['gold_per_min'],  p['lane_efficiency'], p['sen_placed'],
                                  p['player_slot'], p['is_roaming'], p['benchmarks']['lhten']['raw']) for p in resp['players'] if 'lane_efficiency' in p and 'lane' in p]
                    if hero_id == hero_methods.get_id(hero_name):
                        abilities = p['ability_upgrades_arr']
                        # check if one of the players matches search
                        purchase_log = p['purchase_log']
                        if purchase_log:
                            role = roles(roles_arr, p['player_slot'])
                            aghanims_shard = None
                            starting_items = []
                            purchase_log = item_methods.bots(
                                purchase_log, p['purchase'])
                            for purchase in purchase_log:
                                purchase['id'] = item_methods.get_item_id(
                                    purchase['key'])
                                if purchase['time'] <= 0:
                                    starting_items.append(purchase)
                                if purchase['key'] == 'aghanims_shard':
                                    temp = purchase.copy()
                                    aghanims_shard = item_methods.convert_time([
                                                                               temp])
                            # starting_items = [
                            #     purchase for purchase in purchase_log if purchase['time'] <= 0]
                            starting_items = item_methods.clean_items(
                                starting_items)
                            rev = purchase_log.copy()[:: -1]
                            main_items = item_methods.get_most_recent_items(
                                rev, 6, p)
                            bp_items = item_methods.get_most_recent_items(
                                rev, 4, p)
                            if p['duration'] < 600:
                                db['dead_games'].insert_one(
                                    {'id': match_id, 'count': 20})
                                return
                            for k in p['benchmarks']:
                                # round benchmarks to 2 decimal places add 0 to make it same length
                                p['benchmarks'][k]['pct'] = f"{round(p['benchmarks'][k]['pct']*100, 2):.2f}"
                                p['benchmarks'][k]['raw'] = f"{round(p['benchmarks'][k]['raw'], 2):.2f}"
                            if p['duration'] > 0:
                                p['duration'] = str(datetime.timedelta(
                                    seconds=p['duration']))
                            else:
                                p['duration'] = 0
                            hero_output.insert_one(
                                {'unix_time': p['start_time'], 'hero': hero_name, 'duration': p['duration'],
                                 'radiant_draft': rad_draft, 'dire_draft': dire_draft, 'bans': hero_bans,
                                 'name': get_info(match_id, 'name', hero_name), 'account_id': p['account_id'], 'role': role, 'mmr': get_info(match_id, 'mmr', hero_name),
                                 'lvl': p['level'], 'gold': p['gold_t'].copy()[::-1][0], 'hero_damage': p['hero_damage'],
                                 'tower_damage': p['tower_damage'], 'gpm': p['gold_per_min'], 'xpm': p['xp_per_min'],
                                 'kills': p['kills'], 'deaths': p['deaths'], 'assists': p['assists'], 'last_hits': p['last_hits'], 'lane_efficiency': round(p['lane_efficiency'] * 100, 2),
                                 'win': p['win'], 'id': match_id,
                                 'starting_items': starting_items, 'benchmarks': p['benchmarks'], 'gold_adv': resp['radiant_gold_adv'][-1],
                                 'final_items': main_items, 'backpack': bp_items, 'item_neutral': item_methods.get_item_name(p['item_neutral']), 'aghanims_shard': aghanims_shard,
                                 'abilities': detailed_ability_info(abilities, hero_id), 'items': purchase_log})

                            print(f"{hero_name} should reach here.")
                        else:
                            add_to_dead_games(m_id)

    except Exception as e:
        print("Unable to get url: ", m_id, traceback.format_exc())
        add_to_dead_games(m_id)


def add_to_dead_games(m_id):
    if db['dead_games'].find_one({'id': m_id}) is None:
        db['dead_games'].insert_one(
            {'id': m_id, 'count': 0})
    else:
        db['dead_games'].find_one_and_update(
            {'id': m_id}, {"$inc": {'count': +1}})
    if db['dead_games'].find_one({'id': m_id})['count'] < 10:
        db['parse'].insert_one({'id': m_id})


def roles(s, p_slot):
    # use lane_role with lane
    # radiant safe lane is always lane 1 for dire it's lane 3
    # take eff arr top 3 are core then label according to lane
    # convert dire lanes 1 to 3
    # print('sssssss',s,p_slot)
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
        try:
            lane = s[i][0]
        except:
            return None
        if not is_radiant:
            if lane == 1:
                lane = 3
            elif lane == 3:
                lane = 1
        sen_placed = s[i][3]
        slot = s[i][4]
        is_roaming = s[i][5]
        lhten = s[i][6]
        roles = [lane, sen_placed, slot, is_roaming, lhten]
        p_roles.append(roles)
    side.append(p_roles)
    # print('side',is_radiant,side)
    eff = sorted(side[0], key=lambda x: x[4], reverse=True)
    sen = sorted(side[0], key=lambda x: x[1], reverse=True)
    # print(sen[0][4])
    for i, player in enumerate(eff):
        # print('pro_player slot: ', p_slot, player[4], 'lane: ',player[0], i)
        # print('p', player[0], i)
        role = ''
        lane = player[0]
        slot = player[2]
        is_roaming = player[3]
        if i < 3:
            role = 'core'
        if p_slot == sen[0][2]:
            return 'Hard Support'
        elif p_slot == slot and is_roaming:
            return 'Roaming'
        elif p_slot == slot and lane == 2 and role == 'core':
            return 'Midlane'
        elif lane == 3 and p_slot == slot and role == 'core':
            return 'Offlane'
        elif p_slot == slot and lane == 1 and role == 'core':
            return 'Safelane'
        elif lane == 3 and p_slot == slot and role is not 'core':
            return 'Support'


async def main(urls, hero_name):
    # urls = ['5527705678']
    print(f"{hero_name}: {urls}")
    ret = await asyncio.gather(*[async_get(url, hero_name) for url in urls])


async def get_acc_ids(urls, hero_name):
    ret = await asyncio.gather(*[account_id(url, hero_name) for url in urls])


def get_info(m_id, search, hero):
    data = hero_urls.find_one({'id': m_id, 'hero': hero})
    return data[search]


# asyncio.run(main('x', 'zeus'))
