import pymongo
import json
import time
from helper_funcs.hero import Hero
from helper_funcs.abilities import detailed_ability_info
import traceback
import os

from dotenv import load_dotenv
load_dotenv()
connection = os.environ['DB_CONNECTION']

cluster = pymongo.MongoClient(
    f"{connection}?retryWrites=true&w=majority")
db = cluster['pro-item-tracker']

hero_urls = db['urls']
hero_output = db['heroes']
parse = db['parse']
dead_games = db['dead_games']


class Db_insert:
    def __init__(self):
        pass

    def insert_player_picks(self):
        data = db['account_ids'].find({})
        print('inserting player picks')
        for player in data:
            self.insert_total_picks('name', player['name'], 'player_picks')

    def insert_total_picks(self, key, val, collection):
        roles = {'Safelane': hero_output.count_documents(
                {key: val, 'role': 'Safelane'}),
            'Midlane': hero_output.count_documents(
            {key: val, 'role': 'Midlane'}),
            'Offlane': hero_output.count_documents(
            {key: val, 'role': 'Offlane'}),
            'Support': hero_output.count_documents(
            {key: val, 'role': 'Support'}),
            'Roaming': hero_output.count_documents(
            {key: val, 'role': 'Roaming'}),
            'Hard Support': hero_output.count_documents(
            {key: val, 'role': 'Hard Support'}),
        }
        roles = {k: v for k, v in sorted(
            roles.items(), key=lambda item: item[1], reverse=True)}
        for k in list(roles.keys()):
            if roles[k] <= 0:
                del roles[k]
        if key == 'bans':
            db[collection].find_one_and_update(
                {'hero': val}, {"$set": {'total_bans': hero_output.count_documents({key: val})}}, upsert=True)
        else:
            db[collection].find_one_and_replace({key: val},
                                                {key: val, 'total_picks': hero_output.count_documents({key: val}), 'roles': roles}, upsert=True)

    def insert_bans(self, val):
        db['hero_picks'].find_one_and_replace(
            {'hero': val}, {'total_bans': hero_output.count_documents({'bans': val})}, upsert=True)

    def insert_talent_order(self, hero_id):
        with open('json_files/stratz_talents.json', 'r', encoding='utf8') as f:
            data = json.load(f)
            hero_methods = Hero()
            data_talents = data[str(hero_id)]['talents']
            start = time.perf_counter()
            talents = [detailed_ability_info(
                [x['abilityId']], hero_id)[0] for x in data_talents]
            hero = hero_methods.hero_name_from_hero_id(hero_id)
            db['talents'].find_one_and_update(
                {'hero': hero}, {'$set': {'hero': hero, 'talents': talents}}, upsert=True)

    def insert_best_games(self):
        print('INSERT BEST GAMES')
        start = time.perf_counter()
        db['best_games'].delete_many({})
        with open('json_files/hero_ids.json', 'r') as f:
            hero_data = json.load(f)
            for hero in hero_data['heroes']:
                roles = ['Hard Support', 'Roaming', 'Support',
                         'Offlane', 'Midlane', 'Safelane']
                # for hero in hero_data['heroes']:
                data = hero_output.find({'hero': hero['name']})
                sd = sorted(self.sum_benchmarks(data),
                            key=lambda k: k['sum'], reverse=True)
                self.add_best_games_to_db(sd, hero['name'], None)
                for role in roles:
                    data = hero_output.find(
                        {'hero': hero['name'], 'role': role})
                    queried = self.sum_benchmarks(data)
                    sd = sorted(queried, key=lambda k: k['sum'], reverse=True)
                    self.add_best_games_to_db(sd, hero['name'], role)

    def sum_benchmarks(self, data):
        current_highest = 0
        benchmarks = []
        for match in data:
            dic = {}
            summed_benchmarks = 0
            if 'benchmarks' in match:
                for k in match['benchmarks']:
                    percentile = match['benchmarks'][k]['pct']
                    # print(k, match['benchmarks'][k]['pct'])
                    if k != 'lhten':
                        summed_benchmarks += float(percentile)
                    # print(match['id'], sum_benchmarks)
                dic['id'] = match['id']
                dic['sum'] = summed_benchmarks
                benchmarks.append(dic)
                if summed_benchmarks >= current_highest:
                    current_highest = summed_benchmarks
        return benchmarks

    def add_best_games_to_db(self, data, hero, display_role):
        if len(data) < 2:
            return
        for match in data[slice(0, 2)]:
            # print(match)
            base = hero_output.find_one(
                {'hero': hero, 'id': match['id']})
            benchmarks = base['benchmarks']
            player = base['name']
            db['best_games'].insert_one(
                {'id': match['id'], 'hero': hero, 'name': base['name'], 'role': base['role'], 'display_role': display_role, 'benchmarks': base['benchmarks']})

    def add_accouts(self):
        with open('json_files/account_ids.json'):
            pass


if __name__ == '__main__':
    Db_insert.insert_talent_order('self', 1)
