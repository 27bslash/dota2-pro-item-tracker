import copy
from pprint import pprint
import re


def convert_timestamp(secs: int):
    minutes = secs // 60  # integer division
    remaining_seconds = int(secs % 60)
    if remaining_seconds < 10:
        remaining_seconds = f'0{remaining_seconds}'
    return f'{int(minutes)}:{remaining_seconds}'


def group_by_time(data: list, item_data, starting_items: dict):
    res = {'Early Core': {}, 'Early Situational': {}, 'Mid Core': {},
           'Mid Situational': {}, 'Late Core': {}, 'Late Situational': {}}
    tooltips = {}
    o = {'value': 48.69109947643979,
         'adjustedValue': 48.94736842105264,
         'time': 649}
    item_data = []
    for i, item in enumerate(data):
        if 'dissassembledComponents' in item[1]:
            d = {'adjustedValue':  item[1]['adjustedValue'],
                 'time': item[1]['time'], 'dissasemble': True}
            item_data.append(['repair_kit', d])
            item_data.append(
                [f'{item[1]["dissassembledComponents"][0][0]}', d])
            item_data.append(item)
            continue
        item_data.append(item)
    for i, item in enumerate(item_data):
        item_key = re.sub(r'__\d+', '', item[0])
        item_time = item[1]['time']
        if f"item_{item[0]}" in starting_items.values():
            continue

        # if item_time <= 0:
        #     continue
        # core = {k: v for k,  v in data if abs(
        #     item_time - v['time']) <= 50 and k not in seen_items and v['adjustedValue'] > 50 and count <= 1}
        # for k in core.keys():
        #     seen_items.add(k)
        #     count += 1
        #     if count > 1:
        #         break
        # situational = {k: v for k, v in data if abs(item_time - v['time']) <= 50 and v['adjustedValue'] <
        #                40 and v['adjustedValue'] > 5 and k not in seen_items and count <= 1}
        # for k in situational.keys():
        #     seen_items.add(k)
        #     count += 1
        #     if count > 1:
        #         break
        # core_length = len(core) != 0

        # if core_length:
        if item[1]['adjustedValue'] < 8:
            continue
        if item[0] != 'repair_kit':
            tooltips[f"item_{item[0]}"
                     ] = f"pick rate: {round(item[1]['adjustedValue'],2)}%, Average purchase time: {convert_timestamp(item_time)}"
        else:
            tooltips[f"item_{item[0]}"] = f'dissasemble {convert_string(item_data[i+1][0])} into {convert_string(item_data[i+2][0])}'
        if item[1]['adjustedValue'] >= 40:
            if item_time < 700:
                res['Early Core'][f"item_{i}"] = f"item_{item[0]}"
            elif item_time < 1800:
                res['Mid Core'][f"item_{i}"] = f"item_{item[0]}"
            else:
                res['Late Core'][f"item_{i}"] = f"item_{item[0]}"
        else:
            if item_time < 700:
                res['Early Situational'][f"item_{i}"] = f"item_{item[0]}"
            elif item_time < 1800:
                res['Mid Situational'][f"item_{i}"] = f"item_{item[0]}"
            else:
                res['Late Situational'][f"item_{i}"] = f"item_{item[0]}"
    return {'ItemBuild': res, 'tooltip': tooltips}


def convert_string(s: str):
    return ' '.join([x.title() if x != 'of' else x for x in s.split('_')])


if __name__ == '__main__':
    print(convert_string('hood_of_def'))
