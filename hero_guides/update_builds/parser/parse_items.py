from functools import reduce
import operator

from hero_guides.item_builds.group_by_time import convert_string, convert_timestamp


class ItemParser:
    @staticmethod
    def parse_starting_items(build_data):
        starting_item_string = (
            build_data["starting_items"][0][0] if build_data["starting_items"] else None
        )
        if not starting_item_string:
            return None
        starting_items = starting_item_string.split("__")
        starting_items = [
            {f"item_{i}": f"item_{item}"} for i, item in enumerate(starting_items)
        ]
        starting_items = reduce(operator.ior, starting_items, {})
        return starting_items

    @staticmethod
    def parse_neutrals(build_data):
        neutral_tooltips = {}
        neutral_item_build = {}
        index = 0
        neutral_items = []
        for i, k in enumerate(build_data["neutral_items"]):
            tier_items = []
            tier_str = f"Tier {i+1}"
            itemGroup = build_data["neutral_items"][k]
            for item in itemGroup['neutral_items'][0:4]:
                tier_items.append({f"item_{index}": f"item_{item['key']}"})
                # neutral_items.append({f"item_{index}": f"item_{item[0]}"})
                neutral_tooltips[f"item_{item['key']}"] = (
                    f"pick rate: {round(item['perc'],2)}%"
                )
                index += 1
            neutral_item_build[tier_str] = reduce(operator.ior, tier_items, {})

        return neutral_tooltips, neutral_item_build

    def parse_items(self, build_data):
        item_build = {}
        tooltips = {}
        item_groups = build_data["item_builds"]
        game_stages = ["Early", "Mid", "Late"]
        item_prioritys = ["core", "situational"]

        for i, item_group in enumerate(item_groups):
            for item_priority in item_prioritys:
                for j, item in enumerate(item_group[item_priority]):
                    if "dissassembledComponents" in item:
                        self.parse_components(item_group[item_priority], j, item)
                self.item_tooltips(tooltips, item_group[item_priority])
                core_items = [
                    {f"item_{i}": f"item_{item['key']}"}
                    for i, item in enumerate(item_group[item_priority])
                ]
                # example output:  Early Core = {}
                item_build[f"{game_stages[i]} {convert_string(item_priority)}"] = (
                    reduce(operator.ior, core_items, {})
                )

        return {"ItemBuild": item_build, "tooltip": tooltips}

    @staticmethod
    def item_tooltips(tooltips, data):
        for j, item in enumerate(data):
            if item["key"] == "repair_kit":
                tooltips[f"item_{item['key']}"] = (
                    f"Disassemble {' and '.join([convert_string(s) for s in item['components']])} into {convert_string(item['combination'])}, Average time: {convert_timestamp(item['time'])}"
                )
            else:
                tooltips[f'item_{item["key"]}'] = (
                    f"Pick rate: {round(item['adjustedValue'],2)}%, Average purchase time: {convert_timestamp(item['time'])}"
                )
        return tooltips

    @staticmethod
    def parse_components(data, index, item):
        d = {}
        components = []
        for component in item["dissassembledComponents"]:
            components.append(component[0])
            d = {
                "key": component[0],
                "adjustedValue": item["adjustedValue"],
                "time": item["time"],
                "dissasemble": True,
                "combination": item["key"],
                "components": components,
            }
            data.insert(index, d.copy())
        d["key"] = "repair_kit"
        data.insert(index, d.copy())
        del item["dissassembledComponents"]
        return data


if __name__ == "__main__":
    d = {
        "neutral_items": {
            "tier_0": [
                {"key": "mysterious_hat", "count": 2, "perc": 20, "tier": 1},
                {"key": "seeds_of_serenity", "count": 2, "perc": 20, "tier": 1},
                {"key": "trusty_shovel", "count": 2, "perc": 20, "tier": 1},
                {"key": "arcane_ring", "count": 2, "perc": 20, "tier": 1},
            ],
            "tier_1": [
                {
                    "key": "whisper_of_the_dread",
                    "count": 12,
                    "perc": 36.36363636363637,
                    "tier": 2,
                },
                {
                    "key": "philosophers_stone",
                    "count": 9,
                    "perc": 27.27272727272727,
                    "tier": 2,
                },
                {"key": "bullwhip", "count": 4, "perc": 12.121212121212121, "tier": 2},
                {
                    "key": "gossamer_cape",
                    "count": 3,
                    "perc": 9.090909090909092,
                    "tier": 2,
                },
            ],
            "tier_2": [
                {
                    "key": "ogre_seal_totem",
                    "count": 9,
                    "perc": 25.71428571428571,
                    "tier": 3,
                },
                {
                    "key": "psychic_headband",
                    "count": 8,
                    "perc": 22.857142857142858,
                    "tier": 3,
                },
                {
                    "key": "ceremonial_robe",
                    "count": 8,
                    "perc": 22.857142857142858,
                    "tier": 3,
                },
                {
                    "key": "dandelion_amulet",
                    "count": 5,
                    "perc": 14.285714285714285,
                    "tier": 3,
                },
            ],
            "tier_3": [
                {
                    "key": "trickster_cloak",
                    "count": 7,
                    "perc": 28.000000000000004,
                    "tier": 4,
                },
                {
                    "key": "timeless_relic",
                    "count": 7,
                    "perc": 28.000000000000004,
                    "tier": 4,
                },
                {"key": "ninja_gear", "count": 5, "perc": 20, "tier": 4},
                {"key": "spy_gadget", "count": 4, "perc": 16, "tier": 4},
            ],
            "tier_4": [
                {"key": "pirate_hat", "count": 1, "perc": 50, "tier": 5},
                {"key": "force_boots", "count": 1, "perc": 50, "tier": 5},
            ],
        }
    }
    ItemParser().parse_neutrals(d)
