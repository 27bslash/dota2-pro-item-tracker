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

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"}


def update_pro_accounts():
    output = []
    # with open('helper_funcs/accounts/accounts.json', 'r') as f:
    #     data = json.load(f)
    #     data = data['players']
    data = get_player_url_list()
    if data == None:
        print('pro tracker blocked')
        return
    url = 'http://www.dota2protracker.com/player/'
    for player_name in data:
        d = {}
        try:
            if db['account_ids'].find_one({'name': player_name}) is not None:
                continue
            print('out db', player_name)
            req = requests.get(
                f'{url}{player_name}', headers=headers)
            text = req.text
            with open('test.html', 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(text, 'html.parser')
                link = soup.find('a', href=re.compile(r'stratz.com/player/'))
                if link is None:
                    print(player_name, 'not found')
                    continue
                acc_id = re.search(r"\d+", link['href'])
                if acc_id:
                    acc_id = acc_id.group(0)
            d['name'] = player_name
            d['account_id'] = acc_id
            time.sleep(1)
            output.append(d)
            db['account_ids'].find_one_and_update({'account_id': d['account_id']}, {"$set": {
                'name': d['name'], 'account_id': d['account_id']}}, upsert=True)
        except Exception as e:
            print(traceback.format_exc(), player_name)


# get_account_ids()
def get_player_url_list():
    player_url = get_player_url()
    if not player_url:
        player_url = 'http://www.dota2protracker.com/static/search_items_291022.json'
        print('no url using default')
    req = requests.get(
        'http://www.dota2protracker.com/static/search_items_291022.json', headers=headers)
    if req.status_code != 200:
        print(f'status:{req.status_code} blocked')
        return None
    if 'players' not in req.text:
        print('misc blocked')
        return None
    players = json.loads(req.text)['players']
    return [k for k in players]


def get_player_url() -> str | None:
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {'performance': 'ALL'}
    chrome = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), desired_capabilities=capabilities)

    # chrome.get('https://dota2itemtracker.vercel.app/')
    chrome.get('http://www.dota2protracker.com')

    time.sleep(3)
    logs = chrome.get_log('performance')
    for log in logs:
        log = json.loads(log['message'])
        if log['message']['method'] != 'Network.responseReceived':
            continue
        if log['message']['params']['response']['mimeType'] != 'application/json':
            continue
        url = log['message']['params']['response']['url']
        if 'search_items' in url:
            return url
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

if __name__ == '__main__':
    get_player_url()
