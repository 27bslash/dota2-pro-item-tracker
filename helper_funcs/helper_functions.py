import json
import re
from collections import OrderedDict
from operator import itemgetter
import datetime


def sort_dict(items):
    newlist = sorted(
        items, key=itemgetter('time'))
    return newlist


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


def get_urls(amount, hero_name):
    urls = []
    hero_name = pro_name(hero_name)
    print(hero_name)
    with open(f"json_files/hero_urls/{hero_name}.json", 'r') as json_file:
        data = json.load(json_file)
        data = sorted(data, key=lambda i: i['mmr'],reverse=True)
        for i in range(amount):
            try:
                print(data[i]['id'])
                m_id = data[i]['id']
                m_id = re.sub(r"www", 'api', m_id)
                m_id = re.sub(r"/matches/", '/api/matches/', m_id)
                urls.append(m_id)
                urls.reverse()
            except Exception as e:
                print(e, e.__class__)
        return urls


def pro_name(hero_name):
    hero_name = hero_name.replace('_', ' ')
    hero_name = " ".join(w.capitalize() for w in hero_name.split())
    # print('initial name', hero_name)
    if 'Anti' in hero_name:
        hero_name = 'Anti-Mage'
    if 'Queen' in hero_name:
        hero_name = "Queen%20of%20Pain"
    return hero_name


def get_id(name):
    if name:
        name = name.lower()
        name = name.replace(' ', '_')
        with open('json_files/hero_ids.json') as json_file:
            data = json.load(json_file)
            for i in range(len(data['heroes'])):
                if name == data['heroes'][i]['name']:
                    return data['heroes'][i]['id']
            return False
    else:
        return False


def get_ability_name(arr):
    abilityArr = []
    for a_id in arr:
        with open('json_files/ability_ids.json', 'r')as f:
            data = json.load(f)
            key = str(a_id)
            with open('json_files/final.json', 'r') as f:
                mData = json.load(f)
            abilityArr.append(
                {'key': mData[data[key]], 'img': data[key]})
    return abilityArr


def get_item_name(item_id):
    with open('json_files/items.json') as json_file:
        data = json.load(json_file)
        for item in data['items']:
            if item_id == item['id']:
                return item['name']
