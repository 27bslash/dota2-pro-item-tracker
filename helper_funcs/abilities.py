import json
import traceback
from collections import Counter, OrderedDict

from .database.collection import db
from .hero import Hero

hero_methods = Hero()
all_abilities = db['all_abilities'].find_one({}, {'_id': 0})
all_talents = db['all_talents'].find_one({}, {'_id': 0})
# def get_hero_name_from_ability(ability_list):
#     for ability in ability_list:
#         with open('json_files/stratz_abilities.json', 'r') as f:
#             data = json.load(f)
#             if 'uri' in data[str(ability)]:
#                 return data[str(ability)]['uri']


def convert_special_values(key, file):
    for k in file:
        values_int = file[0]['values_int']
        values_float = file[0]['values_float']
        if len(values_int) == 0:
            values_int = 0
        else:
            values_int = values_int[0]
        if len(values_float) == 0:
            values_float = 0
        else:
            values_float = round(values_float[0], 2)*1
        special_value = values_int + values_float
        key = key.replace('{s:value}', str(special_value))
        return key


def detailed_ability_info(ability_list, hero_id):
    output = []
    talents = []
    count = 0
    stats_count = [i for i in ability_list[slice(0, 18)] if i == 730]
    hero_name = hero_methods.hero_name_from_hero_id(hero_id)
    # print(len(stat_count))
    st_count = 0
    temp_st_count = 0

    gap = 0
    for i, _id in enumerate(ability_list):
        _id = str(_id)
        if _id in all_abilities:
            if int(_id) == 730:
                # print(i,gap)
                st_count += 1
                temp_st_count += 1
                continue
            # print(i+1,gap,i+1+gap)
            # print(i+1 + gap,i, data[_id]['language']['displayName'])
            try:
                d = {}
                d['img'] = all_abilities[_id]['name']
                d['key'] = all_abilities[_id]['language']['displayName']
                d['id'] = _id
                level = i+1
                if hero_name != 'invoker':
                    if level+gap == 17:
                        # print('17', d['key'], st_count)
                        if temp_st_count == 0:
                            gap += 1
                        else:
                            temp_st_count -= 1
                        # print('17: ',d['key'], level, gap)
                    # print(level+gap, d['key'])
                    if level+gap == 19:
                        if temp_st_count == 0:
                            gap += 1
                        else:
                            temp_st_count -= 1
                            # print('19: ',d['key'], level, gap)
                    # if level > 17:
                    #     stat_count = [
                    #         _ for _ in ability_list[slice(0, i)] if _ == 730]
                    #     # print('17', len(stat_count))
                    #     if len(stat_count) < 1:
                    #         gap += 1
                    if level+gap == 20:
                        # print(level,gap,d['key'])
                        pass
                    if level+gap > 20:
                        # print(level+gap, gap, d['key'], st_count)
                        if 'special_bonus' in all_abilities[_id]['name'] and st_count > 0:
                            # print('llv: ', d['key'],level, temp_st_count, st_count,gap)
                            gap += 25 - level
                        if 25 - level + gap == temp_st_count:
                            # print(d['key'],level+gap,temp_st_count)
                            if 'special_bonus' in all_abilities[_id]['name']:
                                gap += temp_st_count
                        if st_count == 0:
                            # print('gay')
                            gap += 4
                    # if level+gap == 21:
                    #     # print('true')]
                    #     # print(st_count)
                    #     # print(level + gap,d['key'])
                    #     if st_count < 6:
                    #         temp = 4 - 7 - st_count
                    #         # print('gap: ', temp)
                    #         if temp < 0:
                    #             gap += 4
                    #     else:
                    #         pass
                    # if level + gap > 16:
                    # if level >= 19:
                    #     stat_count = [
                    #         _ for _ in ability_list[slice(0, i+1)] if _ == 730]
                    #     # print('18', 'stat_coutn: ',len(stat_count))
                    #     if len(stat_count) < 2:
                    #         gap += 4
                    # if level > 20:
                    #     if len(stat_count) >= 2:
                    #         gap += 4
                    d['level'] = level+gap
                else:
                    # invoker edge case
                    # print('oiv',gap)
                    level = i+1
                    d['level'] = level+gap
                if 'special_bonus' in all_abilities[_id]['name']:
                    d['type'] = 'talent'
                    talent_data = all_talents
                    talents = talent_data[str(hero_id)]['talents']
                    for t in talents:
                        # print(t)
                        if int(_id) in t.values():
                            # print(talent['slot'])
                            d['slot'] = t['slot']
                else:
                    d['type'] = 'ability'
                output.append(d)
                if hero_name != 'invoker':
                    output = output[slice(0, 19)]
            except Exception as e:
                print(_id, traceback.format_exc())

    return output


class Talents():
    def __init__(self):
        self.db = db

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
        talents = self.db['talents'].find_one({'hero': hero})
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
        return reversed(talents['talents'])


ab_arr = [
    # jugg start stats
    [730, 5028, 5028, 5029, 5028, 5030, 5028, 5027, 5029, 5921,
        730, 5030, 5027, 5029, 5906, 5027, 730, 5030, 5027, 5934]]
# no stats
if __name__ == "__main__":
    # insert_player_picks()
    # get_hero_name('jakiro')
    # get_id('lih')
    # get_talent_order('jakiro')
    for lst in ab_arr:
        detailed_ability_info(lst, 8)

    # loop_test()
    # parse_request()
    pass
