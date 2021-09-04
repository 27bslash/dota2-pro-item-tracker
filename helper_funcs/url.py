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
    try:
        urls = [match['id'] for match in data if hero_output.find_one(
            {'hero': hero_name, 'id': match['id']}) is None and parse.find_one(
            {'hero': hero_name, 'id': match['id']}) is None and dead_games.find_one(
            {'hero': hero_name, 'id': match['id']}) is None]
    except Exception as e:
        pass
    return list(reversed(urls[slice(0, 60)]))


def delete_old_urls():
    data = hero_output.find({}).sort('unix_time', 1)
    for d in data:
        # print(d['id'])
        time_since = time.time() - d["unix_time"]
        # 8 days old
        if time_since > 690000:
            collections = db.list_collection_names()
            for collection in collections:
                db[collection].delete_many(
                    {'id': {"$lte": int(d["id"])}})
            print(f"Deleted: {d['id']}")


def parse_request():
    data = parse.find({})
    for match in data:
        url = f"https://api.opendota.com/api/request/{match['id']}"
        try:
            req = requests.post(url)
        except Exception as e:
            print(e)
        print('parse', match['id'])
        parse.delete_one({'id': match['id']})


if __name__ == "__main__":
    delete_old_urls()
