
from pprint import pprint
import statistics

from hero_guides.item_builds.filter_components import filter_components
from hero_guides.item_builds.group_by_time import group_by_time


def human_to_unix(time):
    if isinstance(time, int):
        return 0
    split = time.split(':')
    hours = int(split[0]) * 3600
    mins = int(split[1]) * 60
    secs = int(split[2])
    return hours + mins + secs


def count_items(data, item_data):
    consumables = [
        "tango",
        "flask",
        "ward_observer",
        "ward_sentry",
        "smoke_of_deceit",
        "enchanted_mango",
        "clarity",
        "tpscroll",
        "dust",
        "tome_of_knowledge",
        "gem",
        'faerie_fire'
    ]

    items = []
    for match in data:
        seen_items = set()
        for item in match['items']:
            time = item['time'] if isinstance(
                item['time'], int) else human_to_unix(item['time'])
            time = 0 if time < 0 else time
            key = item['key']
            if key not in consumables and key not in seen_items:
                items.append({key: time})
                seen_items.add(key)

    item_values = {}
    for i, x in enumerate(items):
        key = list(x.keys())[0]
        filtered_item_times = [item[key]
                               for item in items if list(item.keys())[0] == key]

        if filtered_item_times:
            median_time = statistics.median(filtered_item_times)
            avg_time = sum(filtered_item_times) / len(filtered_item_times)
            # if median_time != avg_time:
            # print(x, median_time, avg_time)
            time = min(median_time, avg_time)
            item_values[key] = {'value': len(
                filtered_item_times), 'time': time}

    # map_ = [(item[0], {
    #     'value': (item[1]['value'] / len(data)) * 100,
    #     'adjustedValue': (filtered_data / (filtered_data + count) * 100 if filtered_data > 0 else (item[1]['value'] / len(data)) * 100),
    #     'time': item[1]['time']
    # }) for item in item_values.items() if (filtered_data := len([match for match in data if item[0] not in [i['key'] for i in match['items']] and
    #
    # pprint(item_values.items())
    item_values = [value for value in item_values.items() if (
        int(value[1]['value'] / len(data) * 100)) > 0]
    for i, item in enumerate(item_values):
        games_without_item = 0
        games_with_item = 0
        for match in data:
            lastTime = match['items'][-1]['time']
            in_items = [x for x in match['items']
                        if x['key'] == item[0]]
            if not in_items and lastTime - 100 > item[1]['time']:
                games_without_item += 1
            elif in_items:
                games_with_item += 1

        adjusted_value = games_with_item / \
            (games_with_item + games_without_item) * 100
        item_obj = [item[0], {
            'value': (item[1]['value'] / len(data)) * 100,
            'adjustedValue': adjusted_value, 'time': item[1]['time']
        }]
        # print(item_obj)
        item_values[i] = item_obj  # type: ignore

 # # item_values = [[item[0], {"value": (item[1]['value'] / len(data)) *
    #                           100, "adjustedValue": (item[1]['value'] / len(data)) *
    #                           100, 'time': item[1]['time']}] for item in item_values.items()]
    item_values = sorted(item_values, key=lambda x: x[1]['time'])
    # pprint(item_values)

    return item_values


def boots_filter(data):
    boots = ['tranquil_boots', 'arcane_boots', 'power_treads', 'phase_boots']
    bootsCount = len([x for x in data if x[0] in boots])
    filtered = [x for x in data if (x[0] in boots and round(
        100 / x[1]['value']) < bootsCount or int(100 / x[1]['value']) == 1) or x[0] not in boots]
    return filtered


def filter_items(data, itemData, starting_items):
    data = count_items(data, itemData)
    data = filter_components(data, itemData)
    data = boots_filter(data)
    data = group_by_time(data, itemData, starting_items)
    return data
