
import operator
from functools import reduce
from hero_guides.ability_build.ability_filtering import ability_filter
from hero_guides.ability_build.talent_levels import most_used_talents
from hero_guides.item_builds.filter_items import filter_items

from hero_guides.item_builds.starting_items import starting_items_filter
from helper_funcs.database.collection import all_items


def clean_strings(tup):
    spli = tup[0].split('__')
    return (spli, tup[1])


def update_build(hero: str, role: str, data: list):
    ret = {}
    combined_roles = ['Support', 'Roaming']
    filtered_data = [match for match in data if match['role'] ==
                     role or match['role'] in combined_roles and role in combined_roles]

    # filtered_data = list(data)

    starting_items = clean_strings(
        starting_items_filter(filtered_data, all_items, role))
    starting_items = [{f'item_{i}': item}
                      for i, item in enumerate(starting_items[0])]
    starting_items = reduce(operator.ior, starting_items, {})
    item_build = filter_items(filtered_data, all_items, starting_items)
    talents = most_used_talents(filtered_data, hero)
    talent_build = [{str((i+2) * 5): talent[0]} if int(talent[1]['level']) < (i+2) * 5 else {str(int((talent[1]['level']))): talent[0]}
                    for i, talent in enumerate(talents)]
    seen_levels = []
    for i, d in enumerate(talent_build):
        k = list(d.keys())[0]
        if k in seen_levels:
            new_key = str(int(k) + 1)
            d = {new_key: d[k]}
            talent_build[i] = d
        seen_levels.append(k)

    ability_build = ability_filter(filtered_data, talent_build)
    # ability_build = [{str(i+1): ability}
    #                  for i, ability in enumerate(ability_build[0])]
    talent_tooltips = [
        {talent[0]:f"Pick rate: {talent[1]['perc']}%"} for talent in talents]
    talent_tooltips = reduce(operator.ior, talent_tooltips, {})
    ability_build = ability_build
    ability_build = reduce(operator.ior, ability_build, {})
    ability_build = {'ability_build': ability_build,
                     'abilityTooltips': talent_tooltips}
    # pprint.pprint(item_build)
    return {'starting_items': starting_items, 'items': item_build,
            'abilities': ability_build}
