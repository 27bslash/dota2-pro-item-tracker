import json
import traceback
from collections import Counter, OrderedDict

from helper_funcs.hero import Hero, db

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
                # invoker edge case
                if hero_id != 74:
                    gap = skill_gap(gap, _id, temp_st_count,
                                    st_count, level=i+1)
                d['level'] = i+1+gap
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
                if hero_id != 74:
                    output = output[slice(0, 19)]
            except Exception as e:
                print(_id, traceback.format_exc())
    return output


def skill_gap(gap, _id, temp_st_count, st_count, level):
    if level+gap == 17:
        if temp_st_count == 0:
            gap += 1
        else:
            temp_st_count -= 1
    if level+gap == 19:
        if temp_st_count == 0:
            gap += 1
        else:
            temp_st_count -= 1
    if level+gap == 20:
        pass
    if level+gap > 20:
        if 'special_bonus' in all_abilities[_id]['name'] and st_count > 0:
            gap += 25 - level
        if 25 - level + gap == temp_st_count:
            if 'special_bonus' in all_abilities[_id]['name']:
                gap += temp_st_count
        if st_count == 0:
            gap += 4
    return gap


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
        return list(reversed(talents['talents']))


ab_arr = [
    # jugg start stats
    [5297, 5299, 5297, 5298, 5300, 5297, 5298, 5298, 5298, 5996, 5297, 5300, 5299, 5299, 5299, 6661, 5300, 6064]]
# no stats
if __name__ == "__main__":
    # insert_player_picks()
    # get_hero_name('jakiro')
    # get_id('lih')
    # get_talent_order('jakiro')
    for lst in ab_arr:
        detailed_ability_info(lst, 64)

    # loop_test()
    # parse_request()
    pass
