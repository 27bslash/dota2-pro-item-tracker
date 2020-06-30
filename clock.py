from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from app import *
from opendota_api import *
from helper_funcs.helper_functions import *

scheduler = BackgroundScheduler()
scheduler.add_job(opendota_call, 'cron', timezone='Europe/London',
                  start_date=datetime.datetime.now(), hour='16', minute='40', day_of_week='tue')
scheduler.start()


def opendota_call():
    names = []
    out = []
    print('input')
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i in data['heroes']:
            names.append(i['name'])
        for name in names:
            asyncio.run(pro_request(name, out, 100))
            print('1st')
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for name in names:
            asyncio.run(main(get_urls(100, name), name))
            delete_output()
            time.sleep(60)
            print('second')
    print('end', datetime.datetime.now())
