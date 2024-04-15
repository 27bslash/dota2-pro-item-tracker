import time

import requests


def net_test(retries=500):
    time.sleep(60)
    for i in range(retries):
        try:
            req = requests.get("https://www.google.co.uk/")
            if req.status_code == 200:
                print("connected to the internet")
                return True
            else:
                time.sleep(1)
                continue
        except Exception as e:
            time.sleep(1)
    return False
