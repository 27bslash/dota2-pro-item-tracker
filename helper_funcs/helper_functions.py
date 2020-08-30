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
    try:
        urls = [match['id'] for match in data if hero_output.find_one(
            {'hero': hero_name, 'id': match['id']}) is None and parse.find_one(
            {'hero': hero_name, 'id': match['id']}) is None]
    except Exception as e:
        pass
    return list(reversed(urls))


def pro_items(match_data):
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
        # print(name)
        name = name.lower()
        name = name.replace(' ', '_')
        with open('json_files/hero_ids.json') as json_file:
            data = json.load(json_file)
            try:
                return [hero['id']
                        for hero in data['heroes'] if name == hero['name']][0]
            except Exception as e:
                return False
        return False


def get_hero_name(name):
    heroes = []
    if name:
        name = name.lower()
        name = name.replace(' ', '_')
        with open('json_files/hero_ids.json') as json_file:
            data = json.load(json_file)
            heroes = [hero['name']
                      for hero in data['heroes'] if name in hero['name']]
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
    # print(item_id)
    if not item_id:
        return
    with open('json_files/items.json') as json_file:
        data = json.load(json_file)
        item = [item['name']
                for item in data['items'] if item_id == item['id']]
        return item[0]


def stratz_abillity_test(arr, h_id):
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
    # print(end-start)
    # print(output)
    return output


def talent_order(hero):
    with open('json_files/stratz_talents.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        data_talents = data[str(get_id(hero))]['talents']
        start = time.perf_counter()
        talents = [stratz_abillity_test(
            [x['abilityId']], get_id(hero))[0] for x in data_talents]
        if db['talents'].find_one({'hero': hero}) is None:
            db['talents'].insert_one({'hero': hero, 'talents': talents})


def get_talent_order(match_data, hero):
    talents = []
    count = count_talents(match_data)
    # print('coutn', count)
    if count is None:
        return False
    talents = db['talents'].find_one({'hero': hero})
    start = time.perf_counter()
    # talents = [stratz_abillity_test(
    #     [x['abilityId']], get_id(hero))[0] for x in data_talents]
    # print(item)
    # print(data[str(get_id(hero))])
    # print(data[item]['talents'])
    d = {}
    # print('time.ti/,', time.perf_counter() - start, talents)
    # print('copmprehe', talents)
    for x in talents['talents']:
        if x['key'] in count:
            x['talent_count'] = count[x['key']]
        else:
            x['talent_count'] = 0
    # total picks for talents is both choices added together, this can be done easily if you're not retarded
    # print(talents)
    c = []
    level = 10
    for i in range(0, 8, 2):
        # print(i)
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


def count_talents(data):
    try:
        talents = [ability['key']
                   for item in data for ability in item['abilities'] if 'special_bonus' in ability['img']]
        # print('counter',talents,dict(Counter(talents)))
        return dict(Counter(talents))
    except Exception as e:
        print('y', traceback.format_exc())


def get_talets():
    output = []
    ids = []
    ten = []
    fifteen = []
    twenty = []
    twenty_five = []
    data = hero_output.find({'hero': 'jakiro'})
    for i, item in enumerate(data):
        temp = {}
        ids.append(item['id'])
        for ability in item['abilities']:
            if ability['type'] == 'talent':
                if ability['level'] >= 10 and ability['level'] < 15:
                    temp['id'] = item['id']
                    temp['name'] = ability['key']
                    temp['level'] = 10
                    # m.append(item['id'])
                    ten.append(ability['key'])
                    # m.append(10)
                    # print(item['id'], 10, i, ability['level'], ability['key'])
                elif ability['level'] >= 15 and ability['level'] < 20:
                    temp['id'] = item['id']
                    temp['name'] = ability['key']
                    temp['level'] = 15
                    # m.append(item['id'])
                    if ability['key'] not in ten:
                        # print(ability['key'], ten)
                        fifteen.append(ability['key'])
                    # m.append(15)
                elif ability['level'] >= 20 and ability['level'] < 25:
                    temp['id'] = item['id']
                    temp['name'] = ability['key']
                    temp['level'] = 20
                    # m.append(item['id'])
                    twenty.append(ability['key'])
                    # m.append(20)
                elif ability['level'] >= 25:
                    # print(25, ability['level'], ability['key'])
                    temp['id'] = item['id']
                    temp['name'] = ability['key']
                    temp['level'] = 25
                    # m.append(item['id'])
                    twenty_five.append(ability['key'])
                    # m.append(25)
                    # print(20, i, ability['level'], ability['key'])
                    # print(15, i, ability['level'], ability['key'])
                # print(ten, fifteen, twenty, twenty_five)
    output.append(dict(Counter(ten)))
    output.append(dict(Counter(fifteen)))
    output.append(dict(Counter(twenty)))
    output.append(dict(Counter(twenty_five)))
    print(output)
    for i, item in enumerate(reversed(output)):
        # print('y',i, output[i])
        if i < 3:
            for x in output[i+1]:
                print(x, item)
                if x in item:
                    pass
                    # print('test', i, x)
                    # print(output)
    return output

    # print(m)
    # print(json.dumps(output, indent=2))


def t(lst):
    rev = list(reversed(lst))
    for i, e in enumerate(rev):
        print(i)
        if i < len(rev) - 1:
            for spell in e:
                # print('spell',spell)
                # print('testing: ', i, rev[i], rev[i+1])
                if spell in rev[i+1]:
                    print('ninenene', spell, i+1)
                    rev[i] = None
    # print(rev)
    test = [x for x in rev if x]
    print(test)


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

    # get_hero_name('jakiro')
    # get_id('lih')
    # get_talent_order('jakiro')
    # stratz_abillity_test(ab_arr, 'clockwerk')
    # loop_test()
    pass
