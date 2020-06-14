import re
import json
import asyncio
import aiohttp
import datetime
import traceback

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
                                for item in purchase_log:
                                    # change item purchase time to readable time
                                    if item['time'] > 0:
                                        item['time'] = str(datetime.timedelta(
                                            seconds=item['time']))
                                        item['time'] == ['time']
                                    else:
                                        item['time'] = 0
                                final_items = []
                                sorted_final_items = []

                                backpack = []
                                rev = purchase_log.copy()[::-1]
                                for j in range(6):
                                    # main items
                                    item_str = 'item_'+str(j)
                                    item = get_item_name(p[item_str])
                                    for purchase in rev:
                                        if purchase['key'] == item:
                                            if len(final_items) < 10:
                                                final_items.append(
                                                    {'key': item, 'time': purchase['time']})
                                for j in range(4):
                                    # back pack items
                                    item_str = 'backpack_'+str(j)
                                    item = get_item_name(p[item_str])
                                    for purchase in rev:
                                        if purchase['key'] == item:
                                            if len(final_items) < 10:
                                                final_items.append(
                                                    {'key': item, 'time': purchase['time']})

                                
                                # sorting reeeeeeeeeeeeeeeeeeeeeeeee
                                # for j in range(len(final_items)):
                                #     for k in sorted(final_items[j]):
                                #         print(k ,final_items[j][k])
                    output.append(
                        {'hero': hero_name, 'id': resp['match_id'], 'final_items': final_items, 'items': purchase_log})
                    json.dump(output, outfile, indent=4)
    except Exception as e:
        print("Unable to get url {} due to {}.".format(
            url, traceback.format_exc()))


async def main(urls, hero_name):
    ret = await asyncio.gather(*[async_get(url, hero_name) for url in urls])


def delete_output():
    global output
    output = []


def get_urls(amount):
    urls = []
    with open("test.json") as json_file:
        data = json.load(json_file)
        for i in range(10):
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
    with open('hero_ids.json') as json_file:
        data = json.load(json_file)
        for i in range(len(data['heroes'])):
            name = name.lower()
            name = name.replace(' ', '_')
            # print(name)
            if name in data['heroes'][i]['name']:
                return data['heroes'][i]['id']


def get_item_name(item_id):
    with open('items.json')as json_file:
        data = json.load(json_file)
        for item in data['items']:
            if item_id == item['id']:
                return item['name']
