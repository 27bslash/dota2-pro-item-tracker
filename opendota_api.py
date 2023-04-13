import asyncio
import time
import aiohttp
import traceback
from helper_funcs.hero import Hero
from helper_funcs.abilities import detailed_ability_info
from helper_funcs.items import Items
from helper_funcs.database.db import db
import datetime

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
                                {'name': get_info_from_url_db(
                                    resp['match_id'], 'name', hero_name), 'account_id': p['account_id']}
                            )
    except Exception as e:
        print("Unable to get url {} due to {}.".format(
            url, traceback.format_exc()))


class Api_request():
    def __init__(self) -> None:
        self.item_methods = Items()
        self.hero_methods = Hero()

    async def async_get(self, m_id, hero_name, testing=False):
        if testing:
            global hero_output
            hero_output = db['test_heroes']
        url = f'https://api.opendota.com/api/matches/{m_id}'
        # dupe_check = hero_output.find_one({'hero': hero_name, 'id': m_id})
        # bad_id_check = db['dead_games'].find_one(
        #     {'id': m_id, 'count': {"$gte": 20}})
        # parse_check = db['parse'].find_one({'id': m_id})
        ret = {}
        # if dupe_check is not None or bad_id_check is not None or parse_check is not None:
        #     return 'Bad Id'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url) as response:
                    if response.status != 200:
                        if response.status == 404:
                            # game not over yet
                            ret['parse'] = [{'id': m_id}]

                            return db['parse'].find_one_and_update(
                                {'id': m_id}, {"$set": {'id': m_id}}, upsert=True)
                        if response.status == 429:
                            # rate liimt
                            time.sleep(1)

                        if response.status == 500:
                            # server error
                            ret['dead_games'] = m_id

                            return self.add_to_dead_games(m_id)
                    resp = await response.json()
                    match_id = int(resp['match_id'])
                    print(f"successfully got {match_id}")
                    if resp['duration'] < 600:
                        ret['dead_games'] = m_id

                        return db['dead_games'].insert_one(
                            {'id': match_id, 'count': 20})

                    rad_draft = self.draft(resp, 0)
                    dire_draft = self.draft(resp, 1)
                    hero_bans = [self.hero_methods.hero_name_from_hero_id(
                        ban['hero_id']) for ban in resp['picks_bans'] if ban['is_pick'] == False]
                    deaths_ten = 0
                    non_pro_games = []
                    for i in range(10):
                        p = resp['players'][i]
                        if p['duration'] < 600:
                            print('under 10 mins: ', m_id)
                            db['dead_games'].insert_one(
                                {'id': match_id, 'count': 20})
                            ret['dead_games'] = m_id

                        hero_id = p['hero_id']
                        if p['randomed'] and p['isRadiant']:
                            rad_draft.append(
                                self.hero_methods.hero_name_from_hero_id(hero_id))
                        if p['randomed'] and not p['isRadiant']:
                            dire_draft.append(
                                self.hero_methods.hero_name_from_hero_id(hero_id))
                        if p['kills_log']:
                            for kill in p['kills_log']:
                                if kill['time'] <= 600 and hero_name in kill['key']:
                                    deaths_ten += 1
                    for i in range(10):
                        p = resp['players'][i]
                        hero_id = p['hero_id']
                        abilities = p['ability_upgrades_arr']
                        # check if one of the players matches search
                        purchase_log = p['purchase_log']
                        if not purchase_log:
                            print('add to parse: ', m_id)
                            ret['parse'] = [{'id': m_id}]

                            return db['parse'].find_one_and_update(
                                {'id': m_id}, {"$set": {'id': m_id}}, upsert=True)
                        roles_arr = [(p['lane'], p['gold_per_min'],  p['lane_efficiency'], p['sen_placed'],
                                      p['player_slot'], p['is_roaming'], p['benchmarks']['lhten']['raw']) for p in resp['players'] if 'lane_efficiency' in p and 'lane' in p]
                        role = self.roles(roles_arr, p['player_slot'])
                        non_pro_games.append(self.insert_non_pro_games(
                            p, hero_id, match_id, role))
                        if hero_id != self.hero_methods.get_id(hero_name):
                            continue

                        if p['kills_log']:
                            kills_ten = self.calulate_kills_at_ten(
                                p['kills_log'])
                        else:
                            kills_ten = 0
                        lvl_at_ten = self.calculate_level_at_ten(p['xp_t'][9])
                        xpm_at_ten = int(float(p['xp_t'][9]/10))
                        gpm_at_ten = int(float(p['gold_t'][9]/10))

                        role = self.roles(roles_arr, p['player_slot'])
                        starting_items = []
                        aghanims_shard = None
                        purchase_log = self.item_methods.bots(
                            purchase_log, p['purchase'])
                        for purchase in purchase_log:
                            purchase['id'] = self.item_methods.get_item_id(
                                purchase['key'])
                            if purchase['time'] <= 0:
                                starting_items.append(purchase)
                            if purchase['key'] == 'aghanims_shard':
                                temp = purchase.copy()
                                aghanims_shard = self.item_methods.convert_time([
                                    temp])

                        starting_items = self.item_methods.clean_items(p,
                            starting_items)
                        rev = purchase_log.copy()[:: -1]
                        main_items = self.item_methods.get_most_recent_items(
                            rev, 6, p)
                        bp_items = self.item_methods.get_most_recent_items(
                            rev, 4, p)

                        for k in p['benchmarks']:
                            # round benchmarks to 2 decimal places add 0 to make it same length
                            p['benchmarks'][k]['pct'] = f"{round(p['benchmarks'][k]['pct']*100, 2):.2f}"
                            p['benchmarks'][k]['raw'] = f"{round(p['benchmarks'][k]['raw'], 2):.2f}"
                        if p['duration'] > 0:
                            p['duration'] = str(datetime.timedelta(
                                seconds=p['duration']))
                        else:
                            p['duration'] = 0
                        o = {
                            # match information
                            'unix_time': p['start_time'], 'hero': hero_name, 'duration': p['duration'],
                            'radiant_draft': rad_draft, 'dire_draft': dire_draft, 'bans': hero_bans, 'gold_adv': resp['radiant_gold_adv'][-1],
                            # player information
                            'name': self.get_info_from_url_db(match_id, 'name', hero_name, testing), 'account_id': p['account_id'],
                            'role': role, 'mmr': self.get_info_from_url_db(match_id, 'mmr', hero_name, testing),
                            # game stats
                            'lvl': p['level'], 'gold': p['gold_t'].copy()[::-1][0], 'hero_damage': p['hero_damage'],
                            'tower_damage': p['tower_damage'], 'gpm': p['gold_per_min'], 'xpm': p['xp_per_min'],
                            'kills': p['kills'], 'deaths': p['deaths'], 'assists': p['assists'], 'last_hits': p['last_hits'], 'lane_efficiency': round(p['lane_efficiency'] * 100, 2),
                            'win': p['win'], 'id': match_id,
                            # laning phase stats
                            'starting_items': starting_items, 'benchmarks': p['benchmarks'], 'kills_ten': kills_ten, 'deaths_ten': deaths_ten, 'lvl_at_ten': lvl_at_ten,
                            'last_hits_ten': int(float(p['benchmarks']['lhten']['raw'])), 'gpm_ten': gpm_at_ten, 'xpm_ten': xpm_at_ten,
                            # final items
                            'final_items': main_items, 'backpack': bp_items, 'item_neutral': self.item_methods.get_item_name(p['item_neutral']), 'aghanims_shard': aghanims_shard,
                            'abilities': detailed_ability_info(abilities, hero_id), 'items': purchase_log}
                        db['heroes'].insert_one(o)
                        ret['heroes'] = [o]
                    print(f"{hero_name} should reach here.")
                    db['dead_games'].delete_many({'id': m_id})

        except Exception as e:
            print("Unable to get url: ", m_id, traceback.format_exc())
            # ret['dead_games'] = m_id
            self.add_to_dead_games(m_id)

    def insert_non_pro_games(self, p, hero_id, match_id, role):
        hero_name = self.hero_methods.hero_name_from_hero_id(hero_id)
        purchase_log = self.item_methods.bots(
            p['purchase_log'], p['purchase'])
        starting_items = []
        for purchase in purchase_log:
            purchase['id'] = self.item_methods.get_item_id(
                purchase['key'])
            if purchase['time'] <= 0:
                starting_items.append(purchase)
            if purchase['key'] == 'aghanims_shard':
                temp = purchase.copy()
        starting_items = self.item_methods.clean_items(p,
            starting_items)
        o = {'hero': hero_name, 'id': match_id, 'role': role, 'items': purchase_log, 'starting_items': starting_items,
             'abilities': detailed_ability_info(p['ability_upgrades_arr'], hero_id)}
        db['non-pro'].find_one_and_update({'hero': hero_name,
                                          'id': match_id}, {"$set": o}, upsert=True)
        return o
        pass

    def add_to_dead_games(self, m_id):
        if db['dead_games'].find_one({'id': m_id}) is None:
            db['dead_games'].insert_one(
                {'id': m_id, 'count': 0})
        else:
            db['dead_games'].find_one_and_update(
                {'id': m_id}, {"$inc": {'count': +1}})
        if db['dead_games'].find_one({'id': m_id})['count'] < 20:
            db['parse'].find_one_and_update(
                {'id': m_id}, {"$set": {'id': m_id}}, upsert=True)

    def calculate_level_at_ten(self, exp):
        level_table = [0,  230,  600, 1080,  1660,
                       2260,  2980,  3730,  4620,  5550, 6520, 7530, 8580]
        for i, level in enumerate(level_table):
            if exp > level:
                continue
            return i

    def calulate_kills_at_ten(self, kills_log):
        kills = 0
        for kill in kills_log:
            if kill['time'] < 600:
                kills += 1
        return kills

    def draft(self, resp, side):
        hero_ids = [player['hero_id'] for player in resp['players']]
        self.hero_methods = Hero()
        return [self.hero_methods.hero_name_from_hero_id(
            player['hero_id']) for player in resp['picks_bans'] if player['is_pick'] and player['team'] == side and player['hero_id'] in hero_ids]

    def roles(self, s, p_slot):
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
            lhten = float(s[i][6])
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
            if p_slot == sen[0][2] and role != 'core':
                return 'Hard Support'
            elif p_slot == slot and is_roaming:
                return 'Roaming'
            elif p_slot == slot and lane == 2 and role == 'core':
                return 'Midlane'
            elif lane == 3 and p_slot == slot and role == 'core':
                return 'Offlane'
            elif p_slot == slot and lane == 1 and role == 'core':
                return 'Safelane'
            elif lane == 3 and p_slot == slot and role != 'core':
                return 'Support'
        return 'Hard Support'

    async def opendota_call(self, urls, hero_name, testing=False):
        print(f"{hero_name}: {urls}")
        ret = await asyncio.gather(*[self.async_get(url, hero_name, testing) for url in urls])

    async def get_acc_ids(self, urls, hero_name):
        ret = await asyncio.gather(*[account_id(url, hero_name) for url in urls])

    def get_info_from_url_db(self, m_id, search, hero, testing=False):
        if testing:
            return 0
        data = hero_urls.find_one({'id': m_id, 'hero': hero})
        return data[search]


# asyncio.run(main('x', 'zeus'))
if __name__ == '__main__':
    data = [(1, 668, 0.7677849636216654, 1, 0, False, '47.00'), (3, 381, 0.5252627324171383, 6, 1, False, 11), (1, 371, 0.3504446240905416, 19, 2, False, 8), (3, 649, 0.8425626515763945, 0, 3, False, 51), (2, 746, 0.849232012934519, 0, 4,
                                                                                                                                                                                                              False, 51), (1, 453, 0.5519401778496362, 0, 128, False, 28), (3, 530, 0.7162489894907034, 1, 129, False, 61), (2,
                                                                                                                                                                                                                                                                                                                             531, 0.5772029102667745, 1, 130, False, 32), (3, 257, 0.32841552142279706, 5, 131, True, 5), (1, 280, 0.36782538399353276, 19, 132, False, 9)]
    res = Api_request().roles(data, 1)
    print(res)
