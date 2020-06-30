from apscheduler.schedulers.background import BlockingScheduler
import datetime
import time
from app import *
from opendota_api import *
from helper_funcs.helper_functions import *
import asyncio


print('asdf')
scheduler = BlockingScheduler()
if __name__ == '__main__':
    try:
        scheduler.add_job(opendota_call, 'cron', timezone='Europe/London',
                          start_date=datetime.datetime.now(), hour='17', minute='6', day_of_week='tue')
        scheduler.start()
    except Exception as e:
        print(e, e.__class__)
