from threading import Thread
from apscheduler.schedulers.background import BlockingScheduler
import datetime
import time
import requests
from helper_funcs.helper_imports import *
from hero_guides.update_builds.update_builds import update_builds
from update.update import weekly_update
import asyncio
from opendota_api import Api_request
from update.update_abilities import dl_dota2_abilities

scheduler = BlockingScheduler()


def odota_bulk_request(hero, start_time):
    urls = get_urls(hero)
    sleep = len(urls)
    print('urls: ', sleep)
    # tasks = asyncio.async(Api_request().opendota_call(urls[slice(0, 60)], hero))
    # loop.run_until_complete(
    #     Api_request().opendota_call(urls[slice(0, 60)], hero))

    asyncio.run(Api_request().opendota_call(urls[slice(0, 60)], hero))
    end_time = time.perf_counter()
    print(end_time-start_time)
    sleep = len(urls) - end_time - start_time
    if len(urls) - end_time - start_time < 0:
        sleep = 0
    print('urls: ', len(urls))
    if len(urls) >= 60:
        return odota_bulk_request(hero, start_time)
    print('sleeping for: ', sleep)
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


def daily_update():
    os.system('cls')
    start = time.time()
    check_last_day()
    data = db['hero_list'].find_one({}, {'_id': 0})
    today = datetime.datetime.today().weekday()
    hour = datetime.datetime.now().hour
    # print(today)
    # ret = {'heroes': [], 'dead_games': [], 'non-pro': [], 'parse': []}
    # ret['dead_games'] = list(db['dead_games'].find({}, {'_id': 0}))
    # ret['parse'] = list(db['parse'].find({}, {'_id': 0}))
    if today == 3 and hour == 14:
        weekly_update()
        update_pro_accounts()
    for hero in data['heroes']:
        hero = hero['name']
        seen_urls = []
        # urls = get_urls(hero, ret, seen_urls=seen_urls)
        start_time = time.perf_counter()
        # if len(urls) == 0:
        #     print(hero)
        #     continue
        odota_bulk_request(hero, start_time)

        # if len(urls) > 0:
        #     break
    # insrt_all(ret)
    delete_old_urls()
    database_methods.insert_all()
    parse_request()
    print('end', (time.time()-start)/60, 'minutes')


def insrt_all(data):
    for k, v in data.items():
        print(k, v)
        if k == 'parse' and v:
            for i, match in enumerate(v):
                print(match['id'], f"{i}/{len(v)}")
                url = f"https://api.opendota.com/api/request/{match['id']}"
                req = requests.post(url)
                parse.delete_many({'id': match['id']})
        if k == 'dead_games' and v:
            for match in v:
                if isinstance(v, int):
                    db['dead_games'].insert_one(
                        {'id': match['id'], 'count': 20})
        elif k == 'heroes' and v:
            db[k].insert_many(v)

        # db[k].insert_many(v)
    pass


def back_up():
    db['backup_heroes'].delete_many({})
    db['backup_heroes'].insert_many(list(db['heroes'].find({}, {'_id': 0})))


def update_all_hero_guides():
    update_builds()


if __name__ == '__main__':
    # database_methods.detailed(hero_list, 'hero', 'th')
    # hero_output.delete_many({'hero': 'monkey_king', 'id': 6970533384})
    # odota_bulk_request('monkey_king')
    # parse_request()
    # daily_update()
    # db['heroes'].aggregate([{'$match': {}}, {'$out': db['backup_heroers']}])
    # dl_dota2_abilities(True)
    back_up_thread = Thread(target=back_up)
    back_up_thread.start()
    build_thread = Thread(target=update_all_hero_guides)
    build_thread.start()
    # data_heroes = db['heroes'].find({})

    # database_methods.insert_all()

    # time.sleep(10000)
    try:
        scheduler.add_job(daily_update, 'cron', timezone='Europe/London',
                          start_date=datetime.datetime.now(), hour='*', minute='*/30', day_of_week='mon-sun')
        scheduler.start()
        pass
    except Exception as e:
        print(e, e.__class__)
