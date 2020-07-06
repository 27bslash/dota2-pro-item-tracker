import json
from helper_funcs.helper_functions import *
import time
import pymongo
from pymongo import MongoClient


cluster = pymongo.MongoClient(
    'mongodb://dbuser:a12345@ds211774.mlab.com:11774/pro-item-tracker', retryWrites=False)
db = cluster['pro-item-tracker']
hero_urls = db['urls']
hero_output = db['heroes']


def opendota_call():
    names = []
    out = []
    print('input')
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i in data['heroes']:
            names.append(i['name'])
        for i, e in enumerate(names):
            print('first', i)
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i, e in enumerate(names):
            # delete_output()
            print('second')
    print('end')


# opendota_call()
def opendota_call():
    names = []
    out = []
    print('input')
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i in data['heroes']:
            names.append(i['name'])
        # for name in names:
        #     pass
            # asyncio.run(pro_request(name, out, 100))
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for name in names:
            # asyncio.run(main(get_urls(20, name, name)))
            delete_output()
            # time.sleep(60)
            print('second')
    time.sleep(3)
    print('end')


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
    ret = hero_urls.aggregate(pipeline)
    result = list(ret)
    lst = []
    ids = []
    for x in result:
        o = {'hero': x['_id']['hero'], 'id': x['_id']
             ['id'], 'count': x['count']}
        lst.append(o)
    for x in lst:
        limit_test = hero_urls.find(
            {'hero': x['hero'], 'id': x['id']}).limit(x['count'])
        for l in limit_test:
            ids.append(l)
            hero_urls.delete_one({'_id': l['_id']})


def update_mmr():
    urls = hero_urls.find()
    for item in urls:
        hero_output.find_one_and_update({'hero': item['hero'], 'id': item['id']}, {
                                        '$set': {'mmr': item['mmr']}})

