import json
import os
import time
from pprint import pprint

from google.oauth2 import service_account
from googleapiclient import discovery

from helper_funcs.database.db import db


def reset_instance():
    print('resetting compute engine instance')
    credentials = service_login()
    service = discovery.build('compute', 'v1', credentials=credentials)
    project = 'eastern-rain-283917'
    zone = 'us-central1-a'
    instance = 'instance-1'
    request = service.instances().reset(project=project, zone=zone, instance=instance)
    response = request.execute()
    pprint(response)

def service_login():
    json_str = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    json_data = json.loads(json_str)
    json_data['private_key'] = json_data['private_key'].replace('\\n', '\n')
    credentials = service_account.Credentials.from_service_account_info(
        json_data)
    return credentials


def check_last_day():
    sort = db['urls'].find({}).sort('time_stamp', -1)
    time_since = time.time() - sort[0]['time_stamp']
    if time_since > 3600:
        reset_instance()
        
if __name__ == "__main__":
    check_last_day()