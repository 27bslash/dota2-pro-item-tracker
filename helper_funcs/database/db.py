import pymongo
import json
import time
from ..hero import Hero
from ..abilities import detailed_ability_info
import traceback
import os
from .collection import db, hero_output
from datetime import datetime

all_talents = db['all_talents'].find_one({}, {'_id': 0})

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
        hero_methods = Hero()
        data_talents = all_talents[str(hero_id)]['talents']
        talents = [detailed_ability_info(
            [x['abilityId']], hero_id)[0] for x in data_talents]
        hero = hero_methods.hero_name_from_hero_id(hero_id)
        db['talents'].find_one_and_update(
            {'hero': hero}, {'$set': {'hero': hero, 'talents': talents}}, upsert=True)

    def insert_best_games(self):
        print('INSERT BEST GAMES')
        start = time.perf_counter()
        db['best_games'].delete_many({})
        hero_data = db['hero_list'].find_one({})
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

    def insert_worst_games(self):
        data = hero_output.find({})
        roles = ['Midlane', 'Safelane', 'Offlane']
        for doc in data:
            items = [item['key']
                     for item in doc['final_items']]
            times = [item['time']
                     for item in doc['final_items']]
            if 'shadow_amulet' in items:
                amulet_idx = items.index('shadow_amulet')
                duration = doc['duration']
                duration = self.convert_to_seconds(doc['duration'])
                amulet_datetime = datetime.strptime(
                    times[amulet_idx], "%H:%M:%S").time()
                amulet_time = self.convert_to_seconds(amulet_datetime)
                if 'shadow_amulet' in items and len(items) < 3 or 'shadow_amulet' in items and doc['role'] in roles and duration - amulet_time > 60:
                    db['chappie'].find_one_and_update(
                        {'hero': doc['hero'], "id": doc['id']}, {"$set": doc}, upsert=True)

    def convert_to_seconds(self, time):
        time = str(time)
        hours = time.split(':')[0]
        minutes = time.split(':')[1]
        seconds = time.split(':')[2]
        return int(hours) * 3600 + int(minutes)*60 + int(seconds)

    def insert_all(self):
        self.insert_worst_games()
        self.insert_best_games()
        self.insert_player_picks()


if __name__ == '__main__':
    # Db_insert.insert_talent_order('self', 1)
    Db_insert.insert_worst_games()
