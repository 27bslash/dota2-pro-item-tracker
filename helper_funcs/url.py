import time
import traceback
import requests
from helper_funcs.database.db import db

hero_urls = db["urls"]
hero_output = db["heroes"]
parse = db["parse"]
dead_games = db["dead_games"]


def get_urls(hero_name):
    urls = []
    data = hero_urls.find({"hero": hero_name})
    urls = [
        match["id"]
        for match in data
        if hero_output.find_one(
            {"hero": hero_name, "id": match["id"], "parsed": {"$ne": False}}
        )
        is None
        and parse.find_one({"id": match["id"]}) is None
        and (
            dead_games.find_one({"id": match["id"]}) is None
            or dead_games.find_one({"id": match["id"], "count": {"$lte": 20}})
        )
    ]
    # return list(reversed(urls[slice(0, 60)]))
    return list(reversed(urls))


def delete_old_urls(max_age=690000):
    data = hero_urls.find({})
    for d in list(data)[::-1]:
        time_since = time.time() - d["time_stamp"]
        # 8 days old
        if time_since > max_age:
            collections = db.list_collection_names()
            for collection in collections:
                # don't delete hero ids only match ids
                db[collection].delete_many({"id": {"$lte": d["id"], "$gte": 4000}})
            print("deleted: ", d["id"])
            break


def parse_request():
    data = list(parse.find({}))
    for i, match in enumerate(data):
        if "stratz" in match:
            continue
        time.sleep(1)
        print(match["id"], f"{i}/{len(data)}")
        url = f"https://api.opendota.com/api/request/{match['id']}"
        req = requests.post(url)
        if int(req.headers["X-Rate-Limit-Remaining-Minute"]) <= 0:
            time.sleep(60)
        if int(req.headers["X-Rate-Limit-Remaining-Day"]) <= 900:
            parse.delete_many({})
            break
        parse.delete_many({"id": match["id"]})
    parse.delete_many({})


if __name__ == "__main__":
    d = list(hero_output.find({"parsed": {"$ne": False}}))
    print(get_urls("jakiro"), len(d))

    # delete_old_urls()
