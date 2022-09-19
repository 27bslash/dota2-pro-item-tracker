import time
import traceback
import requests
from helper_funcs.database.db import db

hero_urls = db['urls']
hero_output = db['heroes']
parse = db['parse']
dead_games = db['dead_games']


def get_urls(hero_name):
    urls = []
    data = hero_urls.find({'hero': hero_name})
    urls = [match['id'] for match in data if hero_output.find_one(
        {'hero': hero_name, 'id': match['id']}) is None and parse.find_one(
        {'id': match['id']}) is None and
        (dead_games.find_one({'id': match['id']}) is None or
         dead_games.find_one({'id': match['id'], 'count': {"$lte": 10}}))]
    # return list(reversed(urls[slice(0, 60)]))
    return list(reversed(urls))


def delete_old_urls():
    data = hero_urls.find({})
    for d in list(data)[:: -1]:
        time_since = time.time() - d["time_stamp"]
        # 8 days old
        if time_since > 690000:
            collections = db.list_collection_names()
            for collection in collections:
                # don't delete hero ids only match ids
                db[collection].delete_many(
                    {'id': {"$lte": d["id"], "$gte": 4000}})
            print('deleted: ', d['id'])
            break


def parse_request():
    data = parse.find({})
    for match in data:
        url = f"https://api.opendota.com/api/request/{match['id']}"
        req = requests.post(url)
        parse.delete_many({'id': match['id']})


if __name__ == "__main__":
    # get_urls('jakiro')
    parse_request()
    # delete_old_urls()
