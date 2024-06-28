from pprint import pprint
import re
import statistics
from typing import Dict, List

from hero_guides.item_builds.filter_components import filter_components
from hero_guides.item_builds.group_by_time import group_by_time


def human_to_unix(time):
    if isinstance(time, int):
        return 0
    split = time.split(":")
    hours = int(split[0]) * 3600
    mins = int(split[1]) * 60
    secs = int(split[2])
    return hours + mins + secs


def count_items(data, item_data):
    # TODO
    # implement double bracer
    # implement neutral items
    consumables = [
        "tango",
        "flask",
        "branches",
        "blood_grenade",
        "ward_observer",
        "ward_sentry",
        "smoke_of_deceit",
        "enchanted_mango",
        "clarity",
        "tpscroll",
        "dust",
        "tome_of_knowledge",
        "gem",
        "faerie_fire",
        "great_famango",
        "famango",
        "dagon_2",
        "dagon_3",
        "dagon_4",
    ]

    items: List[Dict[str, int]] = []
    seen_items = set()

    for match in data:
        dupe_counter: List[str] = []
        for i, item in enumerate(match["items"]):
            if item["key"] in consumables or item["key"] not in item_data:
                continue
            if item["key"] in dupe_counter and item["key"] not in [
                "aghanims_shard",
                "ultimate_scepter",
            ]:
                item_count = len(
                    [x for x in match["items"][:i] if x["key"] == item["key"]]
                )
                key = f"{item['key']}__{item_count}"
                dupe_counter.append(f"{item['key']}_{item_count}")
            else:
                dupe_counter.append(item["key"])
                key = item["key"]

            time = (
                human_to_unix(item["time"])
                if isinstance(item["time"], str)
                else item["time"]
            )
            if time <= 0:
                continue

            items.append({key: time})
            seen_items.add(key)

    # map_ = [(item[0], {
    #     'value': (item[1]['value'] / len(data)) * 100,
    #     'adjustedValue': (filtered_data / (filtered_data + count) * 100 if filtered_data > 0 else (item[1]['value'] / len(data)) * 100),
    #     'time': item[1]['time']
    # }) for item in item_values.items() if (filtered_data := len([match for match in data if item[0] not in [i['key'] for i in match['items']] and
    #
    # pprint(item_values.items())

    item_values: Dict[str, Dict[str, float]] = {}
    # print(seen_items)
    for key in seen_items:
        filtered_item_times = [
            list(item.values())[0] for item in items if list(item.keys())[0] == key
        ]
        if filtered_item_times:
            median_time = statistics.median(filtered_item_times)
            avg_time = sum(filtered_item_times) / len(filtered_item_times)
            time = min(median_time, avg_time)
            if not re.match(r"__\d+", key) or (
                re.match(r"__\d+", key) and avg_time <= 800
            ):
                item_values[key] = {"value": len(filtered_item_times), "time": time}

    filtered_item_values = []
    for item in item_values.items():
        if (item[1]["value"] / len(data)) * 100 > 1:
            count = 0
            filtered_data = []
            for match in data:
                last_time = match["items"][-1]["time"]
                cleaned_key = re.sub(r"__\d+", "", item[0])
                dupe_count = 0
                item_num = re.findall(r"\d+", item[0])
                # for item_obj in match["items"]:
                #     if (
                #         item_num
                #         and dupe_count != +item_num[0] + 1
                #         and item_obj.key == cleaned_key
                #     ):
                #         dupe_count += 1
                #     if (
                #         item_num and dupe_count == int(item_num[0]) + 1
                #     ) or not item_num:
                #         return item_obj.key == cleaned_key
                in_items = False
                for item_obj in match["items"]:
                    if (
                        item_num
                        and dupe_count != int(item_num[0]) + 1
                        and item_obj["key"] == cleaned_key
                    ):
                        dupe_count += 1
                    if (
                        item_num and dupe_count == int(item_num[0]) + 1
                    ) or not item_num:
                        if item_obj["key"] == cleaned_key:
                            in_items = True
                            break
                    elif in_items:
                        in_items = True
                        break
                # in_items = any(
                #     item_obj["key"] == cleaned_key
                #     and (not item_num or dupe_count == int(item_num[0]) + 1)
                #     for item_obj in match["items"]
                #     if (item_num and (dupe_count := dupe_count + 1))
                # )
                if not in_items and last_time - 300 > item[1]["time"]:
                    count += 1
                elif in_items:
                    filtered_data.append(match)
            if not filtered_data:
                continue
            adjusted_value = (len(filtered_data) / (len(filtered_data) + count)) * 100
            if adjusted_value < 15:
                continue
            filtered_item_values.append(
                {
                    "key": item[0],
                    "value": (item[1]["value"] / len(data)) * 100,
                    "adjustedValue": adjusted_value,
                    "time": item[1]["time"],
                },
            )

    map = sorted(filtered_item_values, key=lambda x: x["time"])
    return map


def boots_filter(data):
    boots = ["tranquil_boots", "arcane_boots", "power_treads", "phase_boots"]
    bootsCount = len([x for x in data if x[0] in boots])
    filtered = [
        x
        for x in data
        if (
            x[0] in boots
            and round(100 / x[1]["value"]) < bootsCount
            or int(100 / x[1]["value"]) == 1
        )
        or x[0] not in boots
    ]
    return filtered


def filter_items(data, itemData, starting_items):
    data = count_items(data, itemData)
    data = filter_components(data, itemData)
    data = boots_filter(data)
    data = group_by_time(data, itemData, starting_items)
    return data
