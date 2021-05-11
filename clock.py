from apscheduler.schedulers.background import BlockingScheduler
import datetime
from app import opendota_call
scheduler = BlockingScheduler()
if __name__ == '__main__':
    try:
        scheduler.add_job(opendota_call, 'cron', timezone='Europe/London',
                          start_date=datetime.datetime.now(), hour='12', minute='10', day_of_week='mon-sun')
        scheduler.start()
    except Exception as e:
        print(e, e.__class__)
