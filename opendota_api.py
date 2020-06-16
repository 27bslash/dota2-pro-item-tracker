import re
import json
import asyncio
import aiohttp
import datetime
import traceback
from collections import OrderedDict
from operator import itemgetter
# def get_hero_name(name):
#     global hero_name
#     hero_name = name
#     print(hero_name)


output = []


async def async_get(url, hero_name):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                resp = await response.json()
                print("Successfully got url {}.".format(url))
                with open('opendota_output.json', 'w') as outfile:
                    match_id = str(resp['match_id'])
                    for i in range(10):
                        # 10 players
                        p = resp['players'][i]
                        hero_id = p['hero_id']
                        if hero_id == get_id(hero_name):
                            # check if one of the players matches search
                            purchase_log = p['purchase_log']
                            if purchase_log:
                                final_items = []
                                backpack = []
                                starting_items = []
                                for purchase in purchase_log:
                                    if purchase['time'] <= 0:
                                        starting_items.append(
                                            {'key': purchase['key'], 'time': 0})
                                rev = purchase_log.copy()[::-1]
                                main_items = get_most_recent_items(
                                    rev, 6, final_items, p)
                                bp_items = get_most_recent_items(
                                    rev, 4, backpack, p)
                    output.append(
                        {'hero': hero_name, 'id': resp['match_id'], 'starting_items': starting_items, 'final_items': main_items, 'backpack': bp_items, 'items': purchase_log})
                    json.dump(output, outfile, indent=4)
    except Exception as e:
        print("Unable to get url {} due to {}.".format(
            url, traceback.format_exc()))


async def main(urls, hero_name):
    ret = await asyncio.gather(*[async_get(url, hero_name) for url in urls])


def sort_dict(items):
    newlist = sorted(
        items, key=itemgetter('time'))
    for item in newlist:
        if item['time'] > 0:
            item['time'] = str(datetime.timedelta(
                seconds=item['time']))
            item['time'] == ['time']
        else:
            item['time'] = 0
    return newlist


def get_most_recent_items(arr, l, out, p):
    done = set()
    for j in range(l):
        if l == 6:
            item_str = 'item_'+str(j)
        else:
            item_str = 'backpack_'+str(j)
        item = get_item_name(p[item_str])
        for purchase in arr:
            if purchase['key'] == item and purchase['key'] not in done:
                if len(out) < 10:
                    done.add(purchase['key'])
                    out.append(
                        {'key': item, 'time': purchase['time']})
    return sort_dict(out)


def delete_output():
    global output
    output = []


def delete_dupes(d):
    done = set()
    result = []
    for item in d:
        if item['key'] not in done:
            done.add(item['key'])  # note it down for further iterations
            result.append(item)
    return result


def get_urls(amount):
    urls = []
    with open("test.json") as json_file:
        data = json.load(json_file)
        for i in range(amount):
            try:
                m_id = data[i][0]['id']
                m_id = re.sub(r"www", 'api', m_id)
                m_id = re.sub(r"/matches/", '/api/matches/', m_id)
                urls.append(m_id)
                urls.reverse()
            except Exception as e:
                print(e, e.__class__)
        return urls


def get_id(name):
    if name:
        with open('hero_ids.json') as json_file:
            data = json.load(json_file)
            for i in range(len(data['heroes'])):
                name = name.lower()
                name = name.replace(' ', '_')
                if name in data['heroes'][i]['name']:
                    return data['heroes'][i]['id']
            return False
    else:
        return False


def get_item_name(item_id):
    with open('items.json')as json_file:
        data = json.load(json_file)
        for item in data['items']:
            if item_id == item['id']:
                return item['name']
