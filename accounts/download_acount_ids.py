import json
import requests
import time
import re
from helper_funcs.database.db import db
from parsel import Selector

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"}


def get_account_ids():
    output = []
    data = get_player_url_list()
    url = 'http://www.dota2protracker.com/player/'
    for player_name in data:
        d = {}
        try:
            req = requests.get(
                f'{url}{player_name}', headers=headers)
            text = req.text
            selector = Selector(text=text)
            acc_id = selector.xpath("//div[@class='player_stats']//a")[0]
            acc_id = acc_id.css('a::attr(href)').extract()[0]
            acc_id = re.sub(r"\D", '', acc_id, 0)
            d['name'] = player_name
            d['account_id'] = acc_id
            time.sleep(1)
            output.append(d)
            db['account_ids'].find_one_and_update({'account_id': d['account_id']}, {"$set": {
                'name': d['name'], 'account_id': d['account_id']}}, upsert=True)
            print(player_name)
        except Exception as e:
            print(e, e.__class__, player_name, player_name)


# get_account_ids()
def get_player_url_list():
    req = requests.get(
        'http://www.dota2protracker.com/static/search_items_595274230.json', headers=headers)
    players = json.loads(req.text)['players']
    return [k for k in players]


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
    get_account_ids()
