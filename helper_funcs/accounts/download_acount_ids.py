import json
import requests
import time
import re
import traceback
from helper_funcs.database.db import db
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from seleniumbase import SB

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"
}


def update_pro_accounts(testing=False):
    output = []
    # with open('helper_funcs/accounts/accounts.json', 'r') as f:
    #     data = json.load(f)
    #     data = data['players']
    if testing:
        with open("helper_funcs/accounts/new_accs.json", "r") as f:
            data = json.load(f)["players"]
    else:
        data = get_player_url_list()
    if not data:
        print("pro tracker blocked")
        return
    url = "http://www.dota2protracker.com/player/"
    for doc in data:
        d = {}
        try:
            if type(doc) is dict:
                d["name"] = doc["name"]
                d["account_id"] = doc["account_id"]
            if db["account_ids"].find_one({"name": doc["name"]}):
                continue
            if "account_id" not in d:
                if db["account_ids"].find_one({"name": doc['name']}):
                    continue

                # req = requests.get(f"{url}{doc}", headers=headers)
                # text = req.text
                # soup = BeautifulSoup(text, "html.parser")
                # link = soup.find("a", href=re.compile(r"stratz.com/player/"))
                # if link is None:
                #     print(doc, "not found")
                #     continue
                # acc_id = re.search(r"\d+", link["href"])
                # if acc_id:
                #     acc_id = acc_id.group(0)
                
                d["name"] = doc
                d["account_id"] = str(doc['account_id'])
            print("out db", d["name"], d["account_id"])
            time.sleep(1)
            output.append(d)
            db["account_ids"].find_one_and_update(
                {"account_id": d["account_id"]},
                {"$set": d},
                upsert=True,
            )
        except Exception:
            print(traceback.format_exc(), doc)
    print(output)


# get_account_ids()
def get_player_url_list():
    player_url = get_player_url()
    if not player_url:
        player_url = "https://dota2protracker.com/_get/search"
        print("no url using default")
    req = requests.get(player_url, headers=headers)
    if req.status_code != 200:
        print(f"status:{req.status_code} blocked")
        return None
    if "players" not in req.text:
        print("misc blocked")
        return None
    players = json.loads(req.text)["players"]
    return [k for k in players]


def get_player_url() -> str | None:
    with SB() as sb:
        options = Options()
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        chrome = webdriver.Chrome(options=options)

        # chrome.get('https://dota2itemtracker.vercel.app/')
        chrome.get("http://www.dota2protracker.com")
        button_available = WebDriverWait(chrome, 40).until(
            EC.presence_of_element_located((By.CLASS_NAME, "fc-cta-consent"))
        )
        if button_available:
            time.sleep(3)
            try:
                button_available.click()
            except NoSuchElementException as e:
                print("no cookie consent", e)
        time.sleep(3)
        logs = chrome.get_log("performance")
        for log in logs:
            log = json.loads(log["message"])
            if log["message"]["method"] != "Network.responseReceived":
                continue
            if log["message"]["params"]["response"]["mimeType"] != "application/json":
                continue
            url = log["message"]["params"]["response"]["url"]
            print(url)
            if "search" in url:
                chrome.quit()
                return url
        chrome.quit()
        return None
    # networkScript = """
    #     let performance = window.performance || window.webkitPerformance || {};
    #     let network = performance.getEntries() || {};
    #     return network;
    # """
    # networkRequests = chrome.execute_script(networkScript)
    # URLs = [request['name']
    #         for request in networkRequests if 'json' in request['name']]

    # your logic on what to do if request is found
    # print(URLs)
    # print(networkRequests)

    # time.sleep(10)
    # logs = chrome.get_log('performance')
    # print(logs)
    pass


# def convert_account_str_json():
#     """returns raw accounts string converted to json"""
#     with open('raw_accounts_string.txt', 'r') as f:
#         regex = r"(.*)(\s-\s)(http.*)"
#         subst = "\"\\1\":\"\\3\","
#         result = re.sub(regex, subst, f.read(), 0)
#         result = remove_discord_remnants(result)
#         result = result.rstrip(',')
#         # add curly braces to result
#         result = f"{{{result}}}"
#         # convert to json
#         result = json.loads(result)
#         return result


# def remove_discord_remnants(string):
#     regex = r"\[.*|NEW"
#     return re.sub(regex, '', string)

if __name__ == "__main__":
    update_pro_accounts(False)
