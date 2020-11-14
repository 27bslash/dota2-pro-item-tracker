import json
import re
from collections import OrderedDict
from operator import itemgetter
import datetime
import time
import math
import pymongo
import traceback
import requests
from collections import Counter

cluster = pymongo.MongoClient(
    'mongodb://dbuser:a12345@ds211774.mlab.com:11774/pro-item-tracker', retryWrites=False)
db = cluster['pro-item-tracker']
hero_urls = db['urls']
hero_output = db['heroes']
parse = db['parse']


class Hero:
    def __init__(self):
        with open('json_files/hero_ids.json') as f:
            self.data = json.load(f)

    def sanitise_name(self, name):
        self.name = name.lower()
        self.name = name.replace(' ', '_')
        return self.name

    def get_id(self, name):
        self.sanitise_name(name)
        if self.name is None:
            return False
        return [hero['id'] for hero in self.data['heroes'] if self.name == hero['name']][0]

    def get_hero_name(self, name):
        self.sanitise_name(name)
        if self.name is None:
            return False
        return [hero['name'] for hero in self.data['heroes'] if self.name == hero['name']]

    def hero_name_from_hero_id(self, _id):
        return [hero['name'] for hero in self.data['heroes'] if hero['id'] == _id][0]


def delete_dupes(d):
    done = set()
    result = []
    for item in d:
        if item['key'] not in done:
            done.add(item['key'])  # note it down for further iterations
            result.append(item)
    return result


class Items():
    def __init__(self):
        pass

    def pro_items(self, match_data):
        item_lst = []
        sd = []
        data = match_data
        black_lst = ['ward_sentry', 'ward_observer', 'clarity', 'tpscroll',
                     'enchanted_mango', 'smoke_of_deceit', 'tango', 'faerie_fire', 'tome_of_knowledge', 'healing_salve', None]
        item_lst = [item['key']
                    for x in data for item in x['final_items'] if item not in black_lst]
        counter = dict(Counter(item_lst))
        sd = dict(sorted(counter.items(),
                         key=itemgetter(1), reverse=True))
        return sd

    def get_item_name(self, item_id):
        # print(item_id)
        if not item_id:
            return
        with open('json_files/items.json') as json_file:
            data = json.load(json_file)
            item = [item['name']
                    for item in data['items'] if item_id == item['id']]
            return item[0]

    def convert_time(self, lst):
        for item in lst:
            if item['time'] > 0:
                item['time'] = str(datetime.timedelta(
                    seconds=item['time']))
            else:
                item['time'] = 0
        return lst

    def get_most_recent_items(self, arr, l,  p):
        done = set()
        output = []
        for j in range(l):
            if l == 6:
                item_str = 'item_'+str(j)
            else:
                item_str = 'backpack_'+str(j)
            item = self.get_item_name(p[item_str])
            for purchase in arr:
                if purchase['key'] == item and purchase['key'] not in done:
                    if len(output) < 10:
                        done.add(purchase['key'])
                        output.append(
                            {'key': item, 'time': purchase['time']})
        return self.convert_time(sort_dict(output))

    def remove_buildup_items(self, starting_items):
        item_lst = ['bracer', 'null_talisman', 'wraith_band',
                    'ring_of_basilius', 'buckler', 'headress', 'magic_wand']
        build_up = [{'key': 'magic_wand', 'items': [
            'branches', 'branches', 'magic_stick']},
            {'key': 'wraith_band', 'items': ['circlet', 'slippers']},
            {'key': 'null_talisman', 'items': ['circlet', 'mantle']},
            {'key': 'bracer', 'items': ['circlet', 'gauntlets']},
            {'key': 'ring_of_basilius', 'items': ['sobi_mask']},
            {'key': 'buckler', 'items': ['ring_of_protection']},
            {'key': 'headdress', 'items': ['ring_of_regen']}]

        for item in starting_items:
            item_idx = find_index(build_up, item['key'])
            items = build_up[item_idx]['items']
            if item_idx >= 0:
                for buildup_item in items:
                    del starting_items[find_index(
                        starting_items, buildup_item)]
        return starting_items

    def item_charges(self, starting_items):
        max_charges = 1
        temp = []
        for i, item in enumerate(starting_items):
            temp.append(item)
            if item['key'] == 'tango':
                max_charges = 3
            if 'charges' in item:
                print(item['charges'], max_charges)
                for _ in range(1, round(item['charges']/max_charges)):
                    print(item)
                    temp.insert(i, {'key': item['key'], 'time': item['time']})
        return temp

    def clean_items(self, starting_items):
        starting_items = self.remove_buildup_items(starting_items)
        return sort_dict(self.item_charges(starting_items))


class Talents():
    def __init__(self):
        pass

    def count_talents(self, data):
        try:
            talents = [ability['key']
                       for item in data for ability in item['abilities'] if 'special_bonus' in ability['img']]
            # print('counter',talents,dict(Counter(talents)))
            return dict(Counter(talents))
        except Exception as e:
            print('y', traceback.format_exc())

    def get_talent_order(self, match_data, hero):
        talents = []
        count = self.count_talents(match_data)
        if count is None:
            return False
        talents = db['talents'].find_one({'hero': hero})
        start = time.perf_counter()
        for x in talents['talents']:
            if x['key'] in count:
                x['talent_count'] = count[x['key']]
            else:
                x['talent_count'] = 0
        level = 10
        for i in range(0, 8, 2):
            if i < 8:
                picks = talents['talents'][i]['talent_count'] + \
                    talents['talents'][i+1]['talent_count']
                talents['talents'][i]['total_pick_count'] = picks
                talents['talents'][i+1]['total_pick_count'] = picks
                talents['talents'][i]['level'] = level
                talents['talents'][i+1]['level'] = level
                level += 5
        print('Get_talent_order: ', time.perf_counter()-start)
        return reversed(talents['talents'])


class Db_insert:
    def __init__(self):
        pass

    def insert_player_picks(self):
        data = db['account_ids'].find({})
        for player in data:
            print(player['name'])
            self.insert_total_picks('name', player['name'], 'player_picks')

    def insert_total_picks(self, key, val, collection):
        roles = {'Safelane': hero_output.count_documents(
                {key: val, 'role': 'Safelane'}),
            'Midlane': hero_output.count_documents(
            {key: val, 'role': 'Midlane'}),
            'Offlane': hero_output.count_documents(
            {key: val, 'role': 'Offlane'}),
            'Support': hero_output.count_documents(
            {key: val, 'role': 'Support'}),
            'Roaming': hero_output.count_documents(
            {key: val, 'role': 'Roaming'}),
            'Hard Support': hero_output.count_documents(
            {key: val, 'role': 'Hard Support'}),
        }
        roles = {k: v for k, v in sorted(
            roles.items(), key=lambda item: item[1], reverse=True)}
        for k in list(roles.keys()):
            if roles[k] <= 0:
                del roles[k]
        db[collection].find_one_and_replace({key: val},
                                            {key: val, 'total_picks': hero_output.count_documents({key: val}), 'roles': roles})

    def insert_talent_order(self, hero):
        with open('json_files/stratz_talents.json', 'r', encoding='utf8') as f:
            data = json.load(f)
            hero_methods = Hero()
            data_talents = data[str(hero_methods.get_id(hero))]['talents']
            start = time.perf_counter()
            talents = [detailed_ability_info(
                [x['abilityId']], hero_methods.get_id(hero))[0] for x in data_talents]
            if db['talents'].find_one({'hero': hero}) is None:
                db['talents'].insert_one({'hero': hero, 'talents': talents})


def sort_dict(items):
    newlist = sorted(
        items, key=itemgetter('time'))
    return newlist


def get_urls(hero_name):
    urls = []
    data = hero_urls.find({'hero': hero_name})
    try:
        urls = [match['id'] for match in data if hero_output.find_one(
            {'hero': hero_name, 'id': match['id']}) is None and parse.find_one(
            {'hero': hero_name, 'id': match['id']}) is None]
    except Exception as e:
        pass
    return list(reversed(urls))


def find_index(lst, value):
    for i, dic in enumerate(lst):
        if dic['key'] == value:
            return i
    return -1


def parse_request():
    print('run')
    data = parse.find({})
    for match in data:
        print(match)
        url = f"https://api.opendota.com/api/request/{match['id']}"
        try:
            requests.post(url)
            print('hero')
        except Exception as e:
            print(e)
        print('delete', match['id'])
        parse.delete_one({'id': match['id']})


def delete_old_urls():
    data = hero_output.find()
    for d in data:
        # print(d['id'])
        time_since = time.time() - d["unix_time"]
        # 8 days old
        if time_since > 690000:
            try:
                hero_output.delete_many({'id': {"$lte": int(d["id"])}})
                hero_urls.delete_many({'id': {"$lte": int(d["id"])}})
                db['non-pro'].delete_many({'id': {"$lte": int(d["id"])}})
            except Exception as e:
                print(traceback.format_exc())
            print(f"Deleted {d['id']}")


def detailed_ability_info(arr, h_id):
    output = []
    talents = []
    start = time.time()
    count = 0
    # print(arr)
    with open('json_files/stratz_abilities.json', 'r') as f:
        data = json.load(f)
        for i, _id in enumerate(arr):
            _id = str(_id)
            if _id in data:
                # print(_id)
                try:
                    start = time.perf_counter()
                    d = {}
                    d['img'] = data[_id]['name']
                    d['key'] = data[_id]['language']['displayName']
                    d['id'] = _id
                    gap = 0
                    level = i+1
                    if data[_id]['uri'] != 'invoker':
                        if level > 16:
                            gap += 1
                        if level > 17:
                            gap += 1
                        if level > 18:
                            gap += 4
                        d['level'] = i+1+gap
                    else:
                        # invoker edge case
                        level = i+1
                        d['level'] = i+1+gap
                    if 'special_bonus' in data[_id]['name']:
                        d['type'] = 'talent'
                        with open('json_files/stratz_talents.json', 'r', encoding='utf') as f:
                            talent_data = json.load(f)
                            talents = talent_data[str(h_id)]['talents']
                            for t in talents:
                                # print(t)
                                if int(_id) in t.values():
                                    # print(talent['slot'])
                                    d['slot'] = t['slot']
                    else:
                        d['type'] = 'ability'
                    output.append(d)
                    sli = slice(0, 19)
                    output = output[sli]
                except Exception as e:
                    print(traceback.format_exc())
    end = time.time()
    return output


ab_arr = [5239,
          5237,
          5237,
          5238,
          5237,
          5240,
          5237,
          5239,
          5239,
          5931,
          5239,
          5240,
          5238,
          5238,
          502,
          5238,
          5240,
          6364,
          5977
          ]
if __name__ == "__main__":
    # insert_player_picks()
    # get_hero_name('jakiro')
    # get_id('lih')
    # get_talent_order('jakiro')
    # detailed_ability_info(ab_arr, 'clockwerk')
    # loop_test()
    # parse_request()
    pass
