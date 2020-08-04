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


def sort_dict(items):
    newlist = sorted(
        items, key=itemgetter('time'))
    return newlist


def switcher(h):
    switch = {
        'necrophos': 'necrolyte',
        'clockwerk': 'rattletrap',
        "nature's_prophet": 'furion',
        'timbersaw': 'shredder',
        'io': 'wisp',
        'queen_of_pain': 'queenofpain',
        'doom': 'doom_bringer',
        'shadow_fiend': 'nevermore',
        'wraith_king': 'skeleton_king',
        'magnus': 'magnataur',
        'underlord': 'abyssal_underlord',
        'anti-mage': 'antimage',
        'outworld_devourer': 'obsidian_destroyer',
        'windranger': 'windrunner',
        'zeus': 'zuus',
        'vengeful_spirit': 'vengefulspirit',
        'treant_protector': 'treant',
        'centaur_warrunner': 'centaur'
    }
    # print(h, switch.get(h))
    if switch.get(h):
        return switch.get(h)
    else:
        return h


def convert_time(lst):
    for item in lst:
        if item['time'] > 0:
            item['time'] = str(datetime.timedelta(
                seconds=item['time']))
        else:
            item['time'] = 0
    return lst


def get_most_recent_items(arr, l,  p):
    done = set()
    output = []
    for j in range(l):
        if l == 6:
            item_str = 'item_'+str(j)
        else:
            item_str = 'backpack_'+str(j)
        item = get_item_name(p[item_str])
        for purchase in arr:
            if purchase['key'] == item and purchase['key'] not in done:
                if len(output) < 10:
                    done.add(purchase['key'])
                    output.append(
                        {'key': item, 'time': purchase['time']})
    return convert_time(sort_dict(output))


def delete_dupes(d):
    done = set()
    result = []
    for item in d:
        if item['key'] not in done:
            done.add(item['key'])  # note it down for further iterations
            result.append(item)
    return result


def get_urls(hero_name):
    urls = []
    data = hero_urls.find({'hero': hero_name})
    for match in data:
        try:
            m_id = match['id']
            urls.append(m_id)
            urls.reverse()
        except Exception as e:
            pass
    print(urls)
    return urls


def pro_items(match_data):
    item_lst = []
    sd = []
    data = match_data
    black_lst = ['ward_sentry', 'ward_observer', 'clarity', 'tpscroll',
                 'enchanted_mango', 'smoke_of_deceit', 'tango', 'faerie_fire', 'tome_of_knowledge', 'healing_salve', None]
    print('smoke_of_deceit' in black_lst)
    for i, x in enumerate(data):
        # print(i,x)
        for item in x['final_items']:
            if item not in black_lst:
                item_lst.append(item['key'])
                counter = dict(Counter(item_lst))
                sd = dict(sorted(counter.items(),
                                 key=itemgetter(1), reverse=True))
    print('pro', sd)
    return sd


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
    data = hero_output.find().sort("unix_time")
    for d in data:
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
        else:
            break


def pro_name(hero_name):
    hero_name = hero_name.replace('_', ' ')
    hero_name = " ".join(w.capitalize() for w in hero_name.split())
    # print('initial name', hero_name)
    if 'Anti' in hero_name:
        hero_name = 'Anti-Mage'
    if 'Queen' in hero_name:
        hero_name = "Queen%20of%20Pain"
    return hero_name


def get_time(x):
    print(x)
    seconds = time.time() - x  # seconds
    minutes = seconds / 60  # mins
    hours = minutes / 60  # hours
    days = hours / 24  # days
    time_since = ''
    if math.floor(hours) <= 24 and math.floor(hours) > 1:
        return f"{math.floor(hours)} hours ago"
    if math.floor(hours) == 1:
        return f"{math.floor(hours)} hour ago"
    elif math.floor(days) > 1:
        return f"{math.floor(days)} days ago"
    elif math.floor(days) == 1:
        return f"{math.floor(days)} day ago"
    else:
        return 'Just Now'


def get_id(name):
    if name:
        name = name.lower()
        name = name.replace(' ', '_')
        with open('json_files/hero_ids.json') as json_file:
            data = json.load(json_file)
            for hero in data['heroes']:
                if name == hero['name']:
                    return hero['id']
            return False
    return False


def get_hero_name(name):
    heroes = []
    if name:
        name = name.lower()
        name = name.replace(' ', '_')
        with open('json_files/hero_ids.json') as json_file:
            data = json.load(json_file)
            for hero in data['heroes']:
                if name in hero['name']:
                    heroes.append(hero['name'])
            print(heroes)
            return heroes
    return False


# def get_ability_name(arr):
#     abilityArr = []
#     for a_id in arr:
#         with open('json_files/ability_ids.json', 'r')as f:
#             data = json.load(f)
#             key = str(a_id)
#             with open('json_files/final.json', 'r') as f:
#                 mData = json.load(f)
#             abilityArr.append(
#                 {'key': mData[data[key]], 'img': data[key]})
#             sli = slice(0, 19)
#             abilityArr = abilityArr[sli]
#         return abilityArr


def get_ability_name(arr):
    abilityArr = []
    try:
        for a_id in arr:
            with open('json_files/ability_ids.json', 'r')as f:
                data = json.load(f)
                key = str(a_id)
                with open('json_files/final.json', 'r') as f:
                    mData = json.load(f)
                    if key in data.keys():
                        ability_name = mData[data[key]]
                        ability_img = data[key]
                        o = {'key': ability_name, 'img': ability_img}
                        abilityArr.append(
                            {'key': mData[data[key]], 'img': data[key]})
                    else:
                        abilityArr.append(
                            {'key': '', 'img': 'null'})
                sli = slice(0, 19)
                abilityArr = abilityArr[sli]
        return abilityArr
    except Exception as e:
        print(arr)


def get_item_name(item_id):
    with open('json_files/items.json') as json_file:
        data = json.load(json_file)
        for item in data['items']:
            if item_id == item['id']:
                return item['name']
