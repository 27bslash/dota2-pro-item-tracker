import logging
from threading import Thread
import traceback
from apscheduler.schedulers.background import BlockingScheduler
import datetime
import time
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
)
from logs.logger_config import configure_logging
from update.update_app import update_app
import asyncio
from apis.opendota_api import Api_request

scheduler = BlockingScheduler()
amount_run = 0
USE_OPENDOTA = True
configure_logging()


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
    start = time.time()
    check_last_day()
    data = db["hero_list"].find_one({}, {"_id": 0})
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
    if not data:
        print("no data")
        return
    for i, hero in enumerate(data["heroes"]):
        hero = hero["name"]
        seen_urls = []
        # urls = get_urls(hero, ret, seen_urls=seen_urls)
        start_time = time.perf_counter()
        # if len(urls) == 0:
        #     print(hero)
        #     continue
        bulk_api_request(hero, start_time, minute_limit)
        print(f"heroes remaining: {len(data['heroes']) -i+1}")
        # if len(urls) > 0:
        #     break
    # insrt_all(ret)
    delete_old_urls()
    Db_insert(hero_list=data["heroes"], update_trends=first_run).insert_all()
    if USE_OPENDOTA:
        parse_request()
    amount_run += 1
    print("end", (time.time() - start) / 60, "minutes")


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
