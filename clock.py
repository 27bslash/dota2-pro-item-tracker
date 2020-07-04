from apscheduler.schedulers.background import BlockingScheduler
import datetime
import time
from app import *
from opendota_api import *
from helper_funcs.helper_functions import *
import asyncio


scheduler = BlockingScheduler()
if __name__ == '__main__':
    try:
        scheduler.add_job(opendota_call, 'cron', timezone='Europe/London',
                          start_date=datetime.datetime.now(), hour='10', minute='1', day_of_week='mon-sun')
        scheduler.start()
    except Exception as e:
        print(e, e.__class__)
