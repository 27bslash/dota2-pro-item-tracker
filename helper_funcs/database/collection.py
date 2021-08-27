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
