from typing import List, Dict, Any, Tuple
from pprint import pprint
from hero_guides.ability_build.ability_filtering import count_occurences
from helper_funcs.database.collection import db, hero_list


def starting_items_filter(match_data, all_items, role):
    starting_items_list = []
    wards = ["ward_observer", "ward_sentry", "smoke_of_deceit"]
    for match in match_data:
        if not "starting_items" in match or not match["starting_items"]:
            continue
        starting_items = "__".join(
            sorted([f"item_{item['key']}" for item in match["starting_items"] if item])
        )
        if "tango" in starting_items:
            starting_items_list.append(starting_items)
    if not starting_items_list:
        starting_items_list = [
            "__".join(
                sorted(
                    [f"item_{item['key']}" for item in match["starting_items"] if item]
                )
            )
            for match in match_data
            if "starting_items" in match and match["starting_items"]
        ]
    if role != "Midlane":
        starting_items_list = fill_out_items(starting_items_list, all_items)
    # for item in starting_items_list:
    #     item_cost = all_items[item.replace('item_', '')]['cost']
    #     print(item, item_cost)
    return starting_items_list


def fill_out_items(item_list, all_items):
    lst = [item.split("__") for item in item_list]
    items = {
        "item_enchanted_mango": all_items["enchanted_mango"]["cost"],
        "item_tango": all_items["tango"]["cost"],
    }
    for i, item_lst in enumerate(lst):
        filtered_items = [item for item in item_lst if item != ""]
        if not filtered_items:
            continue

        total_cost = sum(
            [all_items[item.replace("item_", "")]["cost"] for item in item_lst]
        )
        tango_count = len([item for item in item_lst if item == "item_tango"])
        while total_cost < 600:
            if tango_count == 1 and total_cost + items["item_tango"] <= 600:
                tango_count += 1
                total_cost += items["item_tango"]
                item_lst.append("item_tango")
                continue
                # print(i, 'add tango', item_lst, total_cost)
            elif (
                total_cost + items["item_enchanted_mango"] <= 600
                and "item_enchanted_mango" in item_lst
            ):
                item_lst.append("item_enchanted_mango")
                total_cost += items["item_enchanted_mango"]
                continue
                # print(i, 'add mango', item_lst, total_cost)
            elif (
                tango_count == 0 or tango_count == 2
            ) and "item_enchanted_mango" not in item_lst:
                break
            elif (
                total_cost + items["item_tango"] >= 600
                and tango_count < 2
                or "item_enchanted_mango" in item_lst
                and total_cost + items["item_enchanted_mango"] >= 600
            ):
                # print('break', total_cost, item_lst)
                break
            else:
                break
        if total_cost < 535:
            # pprint(item_lst)
            # print(total_cost)
            pass
        lst[i] = "__".join(sorted(item_lst))

    return lst


def count_starting_items(data: List[Dict[str, Any]]) -> List[Tuple[str, int]]:
    wards = []

    combo_count = {}
    for match in data:
        starting_items = [
            item["key"] for item in match["starting_items"] if item["key"] not in wards
        ]
        key = "__".join(sorted(starting_items))
        combo_count[key] = combo_count.get(key, 0) + 1

    if not combo_count:
        test = []
        for match in data:
            starting_items = [item["key"] for item in match["starting_items"]]
            sorted_items = sorted(starting_items)
            key = "__".join(sorted_items)
            test.append(key)

        for key in test:
            combo_count[key] = combo_count.get(key, 0) + 1

    count = sorted(combo_count.items(), key=lambda item: item[1], reverse=True)[:2]
    return count


if __name__ == "__main__":
    lst = [
        "item_branches__item_branches__item_circlet__item_faerie_fire__item_flask__item_tango"
    ]
    res = fill_out_items(lst, all_items)
    print(res)
