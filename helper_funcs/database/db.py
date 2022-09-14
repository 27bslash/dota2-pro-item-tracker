import json
import os
import re
import time
import traceback
from datetime import datetime
from operator import itemgetter

from ..abilities import detailed_ability_info
from ..hero import Hero
from ..switcher import switcher
from .collection import db, hero_output

class Db_insert:
    def __init__(self):
        pass

    def insert_player_picks(self):
        data = db['account_ids'].find({})
        print('inserting player picks')
        for player in data:
            if re.search(r"\(smurf.*\)", player['name']):
                print('smurf name', player['name'])
                continue
            # change this back to player picks
            self.insert_total_picks(
                'name', player['name'], 'player_picks')

    def insert_total_picks(self, key, val, collection):
        regex = {"$regex": fr"{val}?\b"}
        roles = {'Safelane': hero_output.count_documents(
            {key: regex, 'role': 'Safelane'}),
            'Midlane': hero_output.count_documents(
            {key: regex, 'role': 'Midlane'}),
            'Offlane': hero_output.count_documents(
            {key: regex, 'role': 'Offlane'}),
            'Support': hero_output.count_documents(
            {key: regex, 'role': 'Support'}),
            'Roaming': hero_output.count_documents(
            {key: regex, 'role': 'Roaming'}),
            'Hard Support': hero_output.count_documents(
            {key: regex, 'role': 'Hard Support'}),
        }
        roles = {k: v for k, v in sorted(
            roles.items(), key=lambda item: item[1], reverse=True)}
        for k in list(roles.keys()):
            if roles[k] <= 0:
                del roles[k]
        cleaned = re.sub(r"\(smurf.*\)", '', val).strip()
        if key == 'bans':
            db[collection].find_one_and_update(
                {'hero': val}, {"$set": {'total_bans': hero_output.count_documents({key: val})}}, upsert=True)
        else:
            db[collection].find_one_and_replace({key: cleaned},
                                                {key: cleaned, 'total_picks': hero_output.count_documents({key: regex}), 'roles': roles}, upsert=True)

    def insert_bans(self, val):
        db['hero_picks'].find_one_and_replace(
            {'hero': val}, {'total_bans': hero_output.count_documents({'bans': val})}, upsert=True)

    def insert_talent_order(self, hero_id):
        hero_methods = Hero()
        hero = hero_methods.hero_name_from_hero_id(hero_id)
        data_talents = db['hero_stats'].find_one(
            {'hero': hero})['talents']
        talents = [detailed_ability_info(
            [_id], hero_id)[0] for _id in data_talents]
        db['talents'].find_one_and_update(
            {'hero': hero}, {'$set': {'talents': talents}}, upsert=True)

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
        # db['chappie'].delete_many({})
        roles = ['Midlane', 'Safelane', 'Offlane']
        for doc in data:
            if doc['win'] == 1:
                continue
            items = [item['key']
                     for item in doc['final_items']]
            times = [item['time']
                     for item in doc['final_items']]
            if 'shadow_amulet' not in items:
                continue
            duration = doc['duration']
            duration = self.convert_to_seconds(doc['duration'])
            amulet_time = self.get_time(items, times, 'shadow_amulet')
            if 'blink' in items:
                blink_time = self.get_time(items, times, 'blink')
                if abs(blink_time - amulet_time) < 60:
                    db['chappie'].find_one_and_update(
                        {'hero': doc['hero'], "id": doc['id']}, {"$set": {'data': doc}}, upsert=True)
            if items.index('shadow_amulet') != 5:
                continue
            if 'shadow_amulet' in items and len(items) < 3 or 'shadow_amulet' in items and doc['role'] in roles and duration - amulet_time > 120 or 'shadow_amulet' in items and len(items) == 1 or len(items) == 0:
                db['chappie'].find_one_and_update(
                    {'hero': doc['hero'], "id": doc['id']}, {"$set": {'data': doc}}, upsert=True)

    def get_time(self, items, times, item_name):
        item_idx = items.index(item_name)
        item_datetime = datetime.strptime(times[item_idx], "%H:%M:%S").time()
        return self.convert_to_seconds(item_datetime)

    def convert_to_seconds(self, time):
        time = str(time)
        hours = time.split(':')[0]
        minutes = time.split(':')[1]
        seconds = time.split(':')[2]
        return int(hours) * 3600 + int(minutes)*60 + int(seconds)

    def insert_winrates(self):
        start = time.perf_counter()
        print('insert winrate...')
        output = []
        roles = ['Hard Support', 'Support', 'Safelane',
                 'Offlane', 'Midlane', 'Roaming']
        data = db['hero_list'].find_one({})
        for hero in data['heroes']:
            picks = hero_output.count_documents({'hero': hero['name']})
            total_wins = hero_output.count_documents(
                {'hero': hero['name'], 'win': 1})
            total_bans = hero_output.count_documents(
                {'bans': hero['name']})
            if total_wins == 0 or picks == 0:
                total_winrate = 0
            else:
                total_winrate = (total_wins / picks) * 100
                total_winrate = self.clean_winrate(total_winrate)
            role_dict = {'hero': hero['name'],
                         'picks': picks, 'wins': total_wins, 'winrate': total_winrate, 'bans': total_bans}
            for role in roles:
                wins = hero_output.count_documents(
                    {'hero': hero['name'], 'win': 1, 'role': role})
                losses = hero_output.count_documents(
                    {'hero': hero['name'], 'win': 0, 'role': role})
                picks = wins+losses
                if picks == 0:
                    winrate = 0
                else:
                    winrate = wins/picks*100
                    winrate = self.clean_winrate(winrate)
                    role_dict[f"{role}_picks"] = picks
                    role_dict[f"{role}_wins"] = wins
                    role_dict[f"{role}_losses"] = losses
                    role_dict[f"{role}_winrate"] = winrate
            output.append(role_dict)
            db['wins'].find_one_and_replace({'hero': hero['name']},
                                            role_dict, upsert=True)
        print('time taken: ',time.perf_counter()-start)

    def clean_winrate(self, winrate):
        winrate = f'{winrate:.2f}'
        winrate = f'{float(winrate):g}'
        winrate = float(winrate) if '.' in winrate else int(winrate)
        return winrate

    def insert_all(self):
        self.insert_worst_games()
        self.insert_best_games()
        self.insert_player_picks()
        self.insert_winrates()


if __name__ == '__main__':
    # Db_insert.insert_talent_order('self', 1)
    Db_insert.insert_worst_games()
