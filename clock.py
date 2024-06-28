from concurrent.futures import ThreadPoolExecutor
import logging
from threading import Thread
import traceback
from apscheduler.schedulers.background import BlockingScheduler
import datetime
import time
from pymongo import ReplaceOne, UpdateMany
import requests
from apis.stratz_api import Stratz_api
import os
from helper_funcs.helper_imports import (
    get_urls,
    check_last_day,
    delete_old_urls,
    db,
    Db_insert,
    parse_request,
    hero_list,
    all_items,
)
from hero_guides.ability_build.ability_filtering import group_abilities
from hero_guides.ability_build.talent_levels import most_used_talents
from hero_guides.item_builds.filter_items import count_items
from hero_guides.item_builds.neutral_items import most_used_neutrals
from hero_guides.item_builds.starting_items import (
    count_starting_items,
)
from hero_guides.ability_build.facet_filtering import facet_filter
from logs.logger_config import configure_logging
from helper_funcs.net_test import net_test
from update.update_app import update_app
import asyncio
from apis.opendota_api import Api_request

scheduler = BlockingScheduler()
amount_run = 0
USE_OPENDOTA = True
configure_logging()
db_cache = {}


def bulk_api_request(
    hero, start_time=time.perf_counter(), minute_limit=60, use_odota=False
):
    urls = get_urls(hero)
    sleep = len(urls)
    print("urls: ", sleep)
    # tasks = asyncio.async(Api_request().opendota_call(urls[slice(0, 60)], hero))
    # loop.run_until_complete(
    #     Api_request().opendota_call(urls[slice(0, 60)], hero))
    global USE_OPENDOTA
    try:
        if USE_OPENDOTA or use_odota:
            ret = asyncio.run(
                Api_request().opendota_call(urls[slice(0, minute_limit)], hero)
            )
            if "use_strats" in ret:
                USE_OPENDOTA = False
        else:
            asyncio.run(Stratz_api().stratz_call(urls[slice(0, minute_limit)], hero))
    except Exception as e:
        logging.error(
            f"Api Request failed for {hero} {traceback.format_exc()} use_opendota:{USE_OPENDOTA}"
        )

    end_time = time.perf_counter()
    print("time_taken: ", end_time - start_time)
    sleep = len(urls) - end_time - start_time
    if len(urls) - end_time - start_time < 0:
        sleep = 0
    print("urls: ", len(urls))
    if len(urls) >= minute_limit:
        return bulk_api_request(hero, start_time)
    print("sleeping for: ", sleep)
    time.sleep(sleep)


def merge_dicts(ret, data):
    # ret = {'heroes': [], 'dead_games': [], 'non-pro': [], 'parse': []}
    # data = [{'dead_games': 6964518777}, {
    #     'dead_games': 5}, {'heroes': [{'hero': 'test'}]}]

    for key, value in ret.items():
        for l in data:
            if key not in l:
                continue
            v = l[key]
            if isinstance(v, int):
                v = [l[key]]
            value.extend(v)
    return ret


def daily_update(first_run=False):
    os.system("cls")
    if not net_test(60):
        print("no internet")
        return
    start = time.time()
    check_last_day()
    today = datetime.datetime.today().weekday()
    hour = datetime.datetime.now().hour
    # print(today)
    # ret = {'heroes': [], 'dead_games': [], 'non-pro': [], 'parse': []}
    # ret['dead_games'] = list(db['dead_games'].find({}, {'_id': 0}))
    # ret['parse'] = list(db['parse'].find({}, {'_id': 0}))
    update_app()
    # current day == thursday
    api_health = requests.get("https://api.opendota.com/api/health").json()
    global USE_OPENDOTA
    minute_limit = 60
    global amount_run
    print("times run: ", amount_run)
    if api_health["parseDelay"]["metric"] > api_health["parseDelay"]["threshold"] * 2:
        print("open dota api down")
        minute_limit = 100
        USE_OPENDOTA = False
    if not hero_list:
        print("no hero list")
        return
    for i, hero in enumerate(hero_list):
        hero = hero["name"]
        seen_urls = []
        # urls = get_urls(hero, ret, seen_urls=seen_urls)
        start_time = time.perf_counter()
        # if len(urls) == 0:
        #     print(hero)
        #     continue
        bulk_api_request(hero, start_time, minute_limit)
        print(f"heroes remaining: {len(hero_list) -i+1}")
        # if len(urls) > 0:
        #     break
    # insrt_all(ret)
    delete_old_urls()
    Db_insert(hero_list=hero_list, update_trends=first_run).insert_all()
    if USE_OPENDOTA:
        parse_request()
    compute_builds()
    amount_run += 1
    print("end", (time.time() - start) / 60, "minutes")


def get_data_from_db(hero_name, role, doc_len):
    # Check if the result is in the cache
    cache_key = (hero_name, role, doc_len)
    if cache_key in db_cache:
        return db_cache[cache_key]
    # Perform the database call and store the result in the cache
    data = list(db["non-pro"].find({"hero": hero_name, "role": role}))
    db_cache[cache_key] = data
    return data


def compute_builds():
    update_hero_builds = []
    srtr = time.perf_counter()
    with ThreadPoolExecutor() as executor:
        update_hero_builds = list(executor.map(process_hero, hero_list))

    db["builds"].bulk_write(update_hero_builds)
    print("time taken to update builds: ", time.perf_counter() - srtr)


def process_hero(hero):
    roles = ["Hard Support", "Support", "Roaming", "Offlane", "Midlane", "Safelane"]
    d = {"hero": hero["name"]}
    doc_len = db["non-pro"].count_documents({"hero": hero["name"]})
    for role in roles:
        data = get_data_from_db(hero["name"], role, doc_len)
        if not data:
            continue
        print(hero["name"], role)
        if len(data) <= doc_len * 0.1:
            continue
        ret = count_items(data, all_items)
        if not ret:
            continue

        starting_items = count_starting_items(data)
        starting_items_dict = {item[0]: item[1] for item in starting_items}
        abilities = group_abilities(data)
        talents = most_used_talents(data)
        talents = {talent[0]: talent[1] for talent in talents}
        facets = facet_filter(data)
        neutral_items = most_used_neutrals(data, all_items)
        d[role] = {
            "starting_items": starting_items_dict,
            "items": ret,
            "abilities": abilities,
            "talents": talents,
            "facets": facets,
            "neutral_items": neutral_items,
            "length": len(data),
        }

    return ReplaceOne({"hero": hero["name"]}, d, upsert=True)


# def insrt_all(data):
#     for k, v in data.items():
#         print(k, v)
#         if k == "parse" and v:
#             for i, match in enumerate(v):
#                 print(match["id"], f"{i}/{len(v)}")
#                 url = f"https://api.opendota.com/api/request/{match['id']}"
#                 req = requests.post(url)
#                 parse.delete_many({"id": match["id"]})
#         if k == "dead_games" and v:
#             for match in v:
#                 if isinstance(v, int):
#                     db["dead_games"].insert_one({"id": match["id"], "count": 20})
#         elif k == "heroes" and v:
#             db[k].insert_many(v)

#         # db[k].insert_many(v)
#     pass


def back_up():
    db["backup_heroes"].delete_many({})
    db["backup_heroes"].insert_many(list(db["heroes"].find({}, {"_id": 0})))


if __name__ == "__main__":
    # database_methods.insert_all()
    # update_app(delete_urls=True)
    # Db_insert(hero_list=hero_list, update_trends=True).insert_all()

    # time.sleep(10000)

    print("starting up...")
    first_run = False
    if datetime.datetime.now().hour < 16:
        first_run = True
        back_up_thread = Thread(target=back_up)
        back_up_thread.start()
    # data_heroes = db['heroes'].find({})
    print("first run: ", first_run)
    # database_methods.insert_all()

    current_dir = os.getcwd()
    if current_dir == "D:\\projects\\python\\pro-item-builds":
        daily_update(first_run=False)
    else:
        daily_update(first_run=first_run)
    try:
        scheduler.add_job(
            daily_update,
            "cron",
            timezone="Europe/London",
            start_date=datetime.datetime.now(),
            hour="*",
            minute="*/30",
            day_of_week="mon-sun",
        )
        scheduler.start()
        pass
    except Exception as e:
        print(e, e.__class__)
