from apscheduler.schedulers.background import BlockingScheduler
import datetime
import time
from helper_funcs.helper_imports import *
from update import weekly_update
import asyncio
from opendota_api import opendota_call

scheduler = BlockingScheduler()


def daily_update():
    start = time.time()
    check_last_day()
    data = db['hero_list'].find_one({}, {'_id': 0})
    today = datetime.datetime.today().weekday()
    if today == 3:
        weekly_update()
    for hero in data['heroes']:
        hero = hero['name']
        sleep = len(get_urls(hero))
        if sleep == 0:
            print(hero)
            continue
        asyncio.run(opendota_call(get_urls(hero), hero))
        if sleep >= 60:
            sleep = 60
        print('sleeping for: ', sleep)
        time.sleep(sleep)
    delete_old_urls()
    database_methods.insert_all()
    parse_request()
    update_pro_accounts()
    print('end', (time.time()-start)/60, 'minutes')


if __name__ == '__main__':
    try:
        scheduler.add_job(daily_update, 'cron', timezone='Europe/London',
                          start_date=datetime.datetime.now(), hour='12', minute='10', day_of_week='mon-sun')
        scheduler.start()
    except Exception as e:
        print(e, e.__class__)
