from collections import Counter
from helper_funcs.talents import Talents

import re


def most_used_talents(match_data, hero):
    # talent_methods = Talents()
    # talents = talent_methods.get_talent_order(match_data, hero)
    # print(talents)
    count = {}
    # talents = [(ability['img'], ability['level'])
    #            for match in match_data for ability in match['abilities'] if ability['type'] == 'talent']
    # print(talents)
    talents = []
    for match in match_data:
        for ability in match['abilities']:
            if ability['type'] == 'talent':
                talents.append(
                    (ability['img'], ability['level'], ability['slot']))
    for talent in talents:
        # print(talent,count)
        # m = re.search(
        #     r"special_bonus_unique_earthshaker$", talent[0])
        # if m:
        #     print(talent,count)
        if talent[0] in count:
            count[talent[0]] = {'level': count[talent[0]]['level']+talent[1],
                                'count': count[talent[0]]['count']+1, 'slot': talent[2]}
        else:
            count[talent[0]] = {'level': talent[1],
                                'count': 1, 'slot': talent[2]}
    for key in count:
        count[key]['level'] = count[key]['level'] / count[key]['count']

    srt = sorted(count.items(), key=lambda x: x[1]['slot'])
    for i in range(0, 7):
        try:
            slot = srt[i][1]['slot']
            if i != slot:
                srt.insert(i, ('null', {'level': 0, 'count': 0, 'slot': i}))
        except:
            pass

    pairs = []
    for i in range(0, len(srt), 2):
        pair = srt[i:i+2]

        pairs.append(pair)
    for i, pair in enumerate(pairs):
        min_count_pair = min(pair, key=lambda x: x[1]['count'])
        total_count = sum([x[1]['count'] for x in pair])
        if len(pair) > 1:
            pair.remove(min_count_pair)
            perc = (pair[0][1]['count'] / total_count) * 100
            pair[0][1]['perc'] = round(perc, 2)
            pairs[i] = pair[0]
        else:
            pair[0][1]['perc'] = 100
            pairs[i] = pair[0]

    return pairs
    # count = dict(Counter(talents))
    # print(count)
    # return count
