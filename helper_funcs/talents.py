from .database.collection import db
import traceback
from collections import Counter

class Talents():

    def count_talents(self, data):
        try:
            talents = [ability['key']
                       for item in data for ability in item['abilities'] if 'special_bonus' in ability['img']]
            # print('counter',talents,dict(Counter(talents)))
            return dict(Counter(talents))
        except Exception as e:
            print('y', traceback.format_exc())

    def get_talent_order(self, match_data, hero):
        talents = []
        count = self.count_talents(match_data)
        if count is None:
            return False
        talents = db['talents'].find_one({'hero': hero})
        for x in talents['talents']:
            if x['key'] in count:
                x['talent_count'] = count[x['key']]
            else:
                x['talent_count'] = 0
        level = 10
        for i in range(0, 8, 2):
            if i < 8:
                picks = talents['talents'][i]['talent_count'] + \
                    talents['talents'][i+1]['talent_count']
                talents['talents'][i]['total_pick_count'] = picks
                talents['talents'][i+1]['total_pick_count'] = picks
                talents['talents'][i]['level'] = level
                talents['talents'][i+1]['level'] = level
                level += 5
        return list(reversed(talents['talents']))
