import time

import requests


def net_test(retries=500):
    for i in range(retries):
        try:
            req = requests.get("https://www.google.co.uk/")
            print("connected to the internet")
            return True
        except Exception as e:
            time.sleep(1)
    return False
