import time
import traceback
import requests
from helper_funcs.database.db import db
from helper_funcs.hero import Hero


hero_urls = db["urls"]
hero_output = db["heroes"]
parse = db["parse"]
dead_games = db["dead_games"]


def get_urls(hero_id: int, pro=False):
    query = (
        {"hero": hero_id, "pro": True, 'mmr': {"$gt": 0}}
        if pro
        else {"heroes": hero_id, 'mmr': {"$gt": 0}}
    )
    data = hero_urls.find(query)

    urls = []

    for match in list(data):
        match_id = match["id"]
        hero_name = Hero().hero_name_from_hero_id(hero_id)
        hero_output_search = hero_output.find_one(
            {"hero": hero_name, "id": match_id, "parsed": {"$ne": False}}
        )
        if hero_output_search:
            continue

        if parse.find_one({"id": match_id}):
            continue

        if dead_games.find_one({"id": match_id, "count": {"$gt": 20}}):
            continue

        urls.append(match_id)

    return list(reversed(urls))


def delete_old_urls(max_age=690000):
    data = hero_urls.find({})
    for d in list(data)[::-1]:
        time_since = time.time() - d["time_stamp"]
        # 8 days old
        print(time_since)
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
        print(match["id"], f"{i}/{len(data)}")
        try:
            start = time.perf_counter()
            url = f"https://api.opendota.com/api/request/{match['id']}"
            req = requests.post(url)
            print(time.perf_counter() - start)
            req.raise_for_status()
            time.sleep(1)
        except Exception:
            break
        if i >= 600:
            break
        parse.delete_many({"id": match["id"]})


if __name__ == "__main__":
    # print(get_urls(51, pro=True))
    target = 8379013910
    list = get_urls(47)
    print(list)
    if target in list:
        print("found")