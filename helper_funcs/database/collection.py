import pymongo
from dotenv import load_dotenv
import os

load_dotenv()
connection = os.environ['DB_CONNECTION']

cluster = pymongo.MongoClient(
    f"{connection}?retryWrites=true&w=majority")

db = cluster['pro-item-tracker']

hero_urls = db['urls']
hero_output = db['heroes']
acc_ids = db['account_ids']
parse = db['parse']
dead_games = db['dead_games']
hero_list = db['hero_list'].find_one({}, {'_id': 0})['heroes']
all_items = db['all_items'].find_one({})['items']
item_ids = db['item_ids'].find_one({})['items']
accounts = db['accounts_ids'].find({})
player_names = [player['name'] for player in accounts]
