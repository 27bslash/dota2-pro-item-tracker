from apscheduler.schedulers.background import BlockingScheduler
import datetime
import time
from helper_funcs.helper_imports import *
from update import weekly_update
import asyncio
from opendota_api import opendota_call

scheduler = BlockingScheduler()


def odota_bulk_request(hero):
    urls = get_urls(hero)
    sleep = len(urls)
    asyncio.run(opendota_call(urls[slice(0, 60)], hero))
    if sleep >= 60:
        sleep = 60
        time.sleep(sleep)
        return odota_bulk_request(hero)
    print('sleeping for: ', sleep)
    time.sleep(sleep)


def daily_update():
    start = time.time()
    check_last_day()
    data = db['hero_list'].find_one({}, {'_id': 0})
    today = datetime.datetime.today().weekday()
    hour = datetime.datetime.now().hour
    # print(today)
    if today == 3 and hour == 12:
        weekly_update()
        update_pro_accounts()
    for hero in data['heroes']:
        hero = hero['name']
        urls = get_urls(hero)
        if len(urls) == 0:
            print(hero)
            continue
        odota_bulk_request(hero)
    delete_old_urls()
    database_methods.insert_all()
    parse_request()
    print('end', (time.time()-start)/60, 'minutes')


if __name__ == '__main__':
    # daily_update()
    try:
        scheduler.add_job(daily_update, 'cron', timezone='Europe/London',
                          start_date=datetime.datetime.now(), hour='*', minute='10', day_of_week='mon-sun')
        scheduler.start()
    except Exception as e:
        print(e, e.__class__)
