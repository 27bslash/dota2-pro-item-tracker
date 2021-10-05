from .database.collection import db
import traceback
from collections import Counter
import json
import re


class Talents():

    def count_talents(self, data):
        # print(data)
        try:
            data = json.loads(data)
            talents = [ability['key']
                       for item in data for ability in item['abilities'] if 'special_bonus' in ability['img']]
            return dict(Counter(talents))
        except Exception as e:
            print('y', traceback.format_exc())

    def get_talent_order(self, match_data, hero):
        all_talents = []
        count = self.count_talents(match_data)
        if count is None:
            return False
        talents = db['individual_abilities'].find_one({'hero': hero})
        for x in talents['talents']:
            d = {}
            talent = talents['talents'][x]
            talent_name = self.extract_special_values(talent)
            d['img'] = talent['name']
            d['key'] = talent_name
            d['id'] = talent['id']
            d['type'] = 'talent'
            d['slot'] = talent['slot']

            if talent['name_loc'] in count:
                d['talent_count'] = count[talent['name_loc']]
            else:
                d['talent_count'] = 0
            all_talents.append(d)
        level = 10
        for i in range(0, 8, 2):
            if i < 8:
                picks = all_talents[i]['talent_count'] + \
                    all_talents[i+1]['talent_count']
                all_talents[i]['total_pick_count'] = picks
                all_talents[i+1]['total_pick_count'] = picks
                all_talents[i]['level'] = level
                all_talents[i+1]['level'] = level
                level += 5
        return list(reversed(all_talents))

    def extract_special_values(self, talent):
        regex = r"{s:value}"
        val = None
        for lst in talent['special_values']:
            if len(lst['values_float']) > 0:
                val = lst['values_float'][0]
            else:
                val = lst['values_int'][0]
        return talent['name_loc'].replace(regex, str(val))
