import json
from helper_funcs.helper_functions import *
import time
import pymongo
from pymongo import MongoClient
import requests
from app import *
from colorthief import ColorThief
from opendota_api import *
from parsel import Selector
from collections import Counter, OrderedDict

cluster = pymongo.MongoClient(
    'mongodb://dbuser:a12345@ds211774.mlab.com:11774/pro-item-tracker', retryWrites=False)
db = cluster['pro-item-tracker']
hero_urls = db['urls']
hero_output = db['heroes']
account_ids = db['account_ids']
most_common = db['most-common-items']


def get_imgs():
    with open('json_files/hero_ids.json', 'r') as d:
        data = json.load(d)
        for item in data['heroes']:
            # print(hero_name)
            hero_name = item['name']
            with open(f'json_files/hero_imgs/{hero_name}.jpg', 'wb') as f:
                f.write(requests.get(
                    f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/heroes/{clean_name(hero_name)}_hphover.png?v=5926546").content)


def get_ability_imgs():
    with open('json_files/hero_ids.json', 'r') as d:
        data = json.load(d)
        for item in data['heroes']:
            # print(hero_name)
            hero_name = item['name']
            db_out = hero_output.find_one({'hero': hero_name})
            try:
                for ability in db_out['abilities']:
                    if 'special_bonus' not in ability['img']:
                        ability_name = ability['img']
                        with open(f'json_files/hero_abilities/{hero_name}/{ability_name}.jpg', 'wb') as f:
                            f.write(requests.get(
                                f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/abilities/{ability_name}_hp1.png?v=5933967").content)
            except Exception as e:
                print(hero_name, ability)


# get_ability_imgs()


def make_dir():
    with open('json_files/hero_ids.json', 'r') as d:
        data = json.load(d)
        for item in data['heroes']:
            hero_name = item['name']
            os.mkdir(f"json_files/hero_abilities/{hero_name}")


def get_dominant_color():
    c_array = []
    output = []
    with open('json_files/hero_colours.json', 'w') as outfile:
        with open('json_files/hero_ids.json', 'r') as f:
            data = json.load(f)
            for item in data['heroes']:
                hero_name = item['name']
                avg_r = 0
                avg_b = 0
                avg_g = 0
                count = 0
                for i, filename in enumerate(os.listdir(f'json_files/hero_abilities/{hero_name}')):
                    try:
                        c_t = ColorThief(
                            f"json_files/hero_abilities/{hero_name}/{filename}")
                        d_c = c_t.get_color(quality=1)
                        r = d_c[0]
                        g = d_c[1]
                        b = d_c[2]
                        avg_r += r
                        avg_g += g
                        avg_b += b
                        count += 1
                        # print(hero_name)
                    except Exception as e:
                        print(filename, hero_name, e)
                # print([sum(i) for i in avg_color])
                try:
                    avg_r /= count
                    avg_g /= count
                    avg_b /= count
                    rgb = (avg_r, avg_g, avg_b)
                    o = {'hero': hero_name, 'color': rgb}
                    output.append(o)
                except Exception as e:
                    print(hero_name, e)
        json.dump(output, outfile, indent=4)

    #             d_c = c_t.get_color(quality=1)
    #             c_array.append({'hero': hero_name, 'colour': d_c})
    # print(c_array)


# get average color
def get_player_names():
    p_names = set()
    al = hero_urls.find()
    for item in al:
        p_names.add(item['name'])
    print(p_names, len(p_names))


def get_account_ids():
    ids = set()
    hero_output.delete_many({'hero': 'jakiro'})
    asyncio.run(main(get_urls(100, 'jakiro'), 'jakiro'))
    acc_ids = hero_output.find({'hero': 'jakiro'})
    for item in acc_ids:
        try:
            ids.add(item['account_id'])
        except Exception as e:
            print(e)
    for idd in ids:
        print(idd)
        try:
            player = hero_output.find_one({'account_id': idd})
            name = player['name']
            account_ids.insert_one({'account_id': idd, 'name': name})
        except Exception as e:
            print(traceback.format_exc())


# get_account_ids()


# def opne():
#     with open('json_files/hero_ids.json', 'r') as f:
#         data = json.load(f)
#         for name in names:
#             asyncio.run(main(get_urls(100, name), name))
#             time.sleep(60)


def get_info(m_id):
    output = []
    data = hero_urls.find_one({'id': m_id})
    print(data['id'])


# get_info('https://www.opendota.com/matches/5493328261')


def t():
    arr = [{'id': "5491385955"}, {'id': "5493042226"}, {
        'id': "5492841514"}, {'id': "5492071872"}, {'id': "0"}]
    for x in arr:
        if hero_output.find_one(x):
            print('hero')


def delete_py_dupes():
    done = set()
    result = []
    pipeline = [
        {
            "$group": {
                "_id": {"hero": "$hero", 'id': '$id'},
                "uniqueIds": {"$addToSet": "$_id"},
                "count": {"$sum": 1}
            }
        },
        {"$match": {"count": {"$gt": 1}}}
    ]
    ret = hero_output.aggregate(pipeline)
    result = list(ret)
    lst = []
    ids = []
    for x in result:
        o = {'hero': x['_id']['hero'], 'id': x['_id']
             ['id'], 'count': x['count']}
        lst.append(o)
    for x in lst:
        limit_test = hero_output.find(
            {'hero': x['hero'], 'id': x['id']}).limit(x['count'])
        for l in limit_test:
            ids.append(l)
            hero_output.delete_one({'_id': l['_id']})


def update_db():
    urls = hero_urls.find()
    for item in urls:
        hero_output.find_one_and_update({'hero': item['hero'], 'id': item['id']}, {
                                        '$set': {'role': item['role']}})


print('try')


def get_account_id(name):
    url = f'http://dota2protracker.com/player/{name}'
    res = requests.get(url)
    text = res.text
    selector = Selector(text=text)
    link = selector.css('a::attr(href)').re(r".*opendota.*")[0]
    acc_id = re.sub(r"\D*", '', link)
    print(acc_id)
    return acc_id


def a_ids():
    with open('accs_to_check.json', 'r') as f:
        data = json.load(f)
        for k, v in data.items():
            account_ids.insert_one(
                {'name': k, 'account_id': get_account_id(k)})


def rename_id():
    hero_urls.update_many({}, {"$rename": {'match_id': 'id'}})


def fix_roles():
    data = hero_urls.delete_many({'mmr': "0"})





def count_occurences():
    item_lst = []
    data = hero_output.find({'hero': 'undying'})
    for d in data:
        # dic = [k['key'] for k in d['items'] if k.get('key')]
        for item in d['final_items']:
            if item['key'] not in consumable_lst:
                item_lst.append(item['key'])
    print(Counter(item_lst))


# count_occurences()
def steam_api_test(name):
    non_pro = db['non-pro']
    data = non_pro.find({'hero': name})
    urls = []
    for d in data:
        url = f'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/?match_id={d["id"]}&key=7AB24C983C1696305C8D6CF64EF4EB43'
        urls.append(url)
    return urls


sem = asyncio.Semaphore(64)


async def get_steam(url, hero_name, final_items, total):
    # print(url,hero_name)
    try:
        if most_common.find_one({'hero': hero_name}) is None:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url) as response:
                    resp = await response.json()
                    m_id = resp['result']['match_id']
                    # print(response.status)
                    if m_id:
                        players = resp['result']['players']
                        for player in players:
                            hero_id = player['hero_id']
                            # print(hero_id,get_id(hero_name))
                            if hero_id == get_id(hero_name):
                                final_items.append(
                                    get_item_name(player['item_0']))
                                final_items.append(
                                    get_item_name(player['item_1']))
                                final_items.append(
                                    get_item_name(player['item_2']))
                                final_items.append(
                                    get_item_name(player['item_3']))
                                final_items.append(
                                    get_item_name(player['item_4']))
                                final_items.append(
                                    get_item_name(player['item_5']))
                                sd = list(filter(
                                    lambda x: x not in black_lst, final_items))
            if most_common.find_one({'hero': hero_name}):
                counter = dict(Counter(sd))
                srt = dict(sorted(counter.items(), reverse=True))
                sd = dict(sorted(counter.items(),
                                 key=itemgetter(1), reverse=True))
                most_common.find_one_and_update(
                    {'hero': hero_name}, {'$set': {'total': total, 'final_items': sd}})
            else:
                print('insert')
                try:
                    most_common.insert_one(
                        {'hero': hero_name, 'total': total, 'final_items': sd})
                    print('inserted')
                except Exception as e:
                    print(e, 'insertion err')
    except Exception as e:
        # print(traceback.format_exc())
        pass


async def limit_download(url, hero_name, final_items, total):
    async with sem:
        return await get_steam(url, hero_name, final_items, total)


async def test(urls, name):
    print('urllen', len(urls))
    final_items = []
    # await asyncio.gather(*tasks)
    await asyncio.gather(*[limit_download(url, name, final_items, len(urls))for url in urls])


def convert_to_int():
    data = hero_urls.find({})
    for x in data:
        hero_urls.find_one_and_update(
            {'id': x['id']}, {"$set": {'id': int(x['id'])}})


def sync(urls, name):
    print(len(urls))
    for i, url in enumerate(urls):
        res = requests.get(url)
        print(res.status_code, i)




def uptime_tester():
    names = []
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for hero in data['heroes']:
            names.append(hero['name'])
    for name in names:
        try:
            res = requests.get(f'https://dota2-item-tracker.herokuapp.com/hero/{name}')
            if res.status_code != 200:
                print(res.status_code, name)
        except Exception as e:
            print(e, 'err')


if __name__ == '__main__':
    # pro_items()
    fix_roles()
    # uptime_tester()