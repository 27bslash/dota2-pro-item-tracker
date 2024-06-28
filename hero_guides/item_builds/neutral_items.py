from typing import Any, Dict, List


def most_used_neutrals(match_data: List[Dict], item_data: Dict):
    tier_count_arr: List[Dict[str, Dict[str, Any]]] = []

    # Iterate over all neutral item tiers
    for i in range(1, 6):
        count: Dict[str, Dict[str, Any]] = {}
        total_game_of_tier = len(
            [
                match
                for match in match_data
                if match.get("item_neutral")
                and item_data.get(match["item_neutral"], {}).get("tier", -1) == i
            ]
        )

        for match in match_data:
            if "item_neutral" in match:
                neutral_item_stats = item_data.get(match["item_neutral"])
                neutral_tier = (
                    neutral_item_stats.get("tier", -1) if neutral_item_stats else -1
                )

                if neutral_tier == i:
                    if match["item_neutral"] in count:
                        item_count = count[match["item_neutral"]]["count"] + 1
                        count[match["item_neutral"]] = {
                            "count": item_count,
                            "tier": neutral_tier,
                            "perc": (item_count / total_game_of_tier) * 100,
                        }
                    else:
                        count[match["item_neutral"]] = {
                            "count": 1,
                            "tier": neutral_tier,
                            "perc": (1 / total_game_of_tier) * 100,
                        }

        tier_count_arr.append(count)

    ret = {}

    for i, tier_arr in enumerate(tier_count_arr):
        sorted_items = sorted(
            tier_arr.items(), key=lambda x: x[1]["count"], reverse=True
        )[:4]
        sorted_list = [
            {
                "key": x[0],
                "count": x[1]["count"],
                "perc": x[1]["perc"],
                "tier": x[1]["tier"],
            }
            for x in sorted_items
        ]
        ret[f"tier_{i+1}"] = sorted_list

    return ret
