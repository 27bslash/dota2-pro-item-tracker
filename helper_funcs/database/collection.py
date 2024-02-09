import time
import pymongo
from dotenv import load_dotenv
import os

load_dotenv()
connection = os.environ["DB_CONNECTION"]

cluster = pymongo.MongoClient(
    f"{connection}?retryWrites=true&w=majority"
)


db = cluster["pro-item-tracker"]
db["non-pro"].create_index([("hero", pymongo.ASCENDING), ("id", pymongo.ASCENDING)], unique=True)
hero_urls = db["urls"]
hero_output = db["heroes"]
acc_ids = db["account_ids"]
parse = db["parse"]
dead_games = db["dead_games"]
strt = time.perf_counter()
hero_list = db["hero_list"].find_one({}, {"_id": 0})["heroes"]
# all_items = db["all_items"].find_one({})["items"]
item_ids = db["item_ids"].find_one({})["items"]
hero_stats = list(db["hero_stats"].find({}))
print(time.perf_counter()- strt)
curr_p = db["current_patch"].find_one({})
if curr_p:
    current_patch = curr_p
# accounts = db["account_ids"].find({})
# player_names = [player["name"] for player in accounts]