import time
import requests
from helper_funcs.database.collection import db, hero_list
from hero_guides.update_builds.handle_steam import handle_steam
from hero_guides.update_builds.update_build import update_build
from hero_guides.write_guide import write_build_to_remote


def calc_common_roles(data):
    dict = {}
    for match in data:
        dict[match['role']] = dict[match['role']] + \
            1 if match['role'] in dict else 1
    max_value = max(dict.values())
    roles = [x[0] for x in dict.items() if x[1] > max_value * 0.2 and x[1] > 1]
    return roles


def update_builds():
    strt = time.perf_counter()
    req = requests.get(
        'https://www.dota2.com/datafeed/patchnoteslist?language=english').json()
    patch = req['patches'][-1]['patch_number']
    for i, hero in enumerate(hero_list):
        ret = {}
        data = list(db['non-pro'].find({'hero': hero['name']}))
        # data = list(db['non-pro'].find({'hero': 'earthshaker'}))
        roles = calc_common_roles(data)
        seen_roles = []
        for role in roles:
            print(i, hero['name'], role)
            if role == 'Support' and 'Roaming' in seen_roles or role == 'Roaming' and 'Support' in seen_roles:
                continue
            seen_roles.append(role)
            ret[role] = update_build(hero['name'], role, data)

        write_build_to_remote(ret, hero['name'], patch)
    print('update builds time taken: ', time.perf_counter() - strt)


def main():
    # hero_list = [["primal_beast", 'Offlane']]
    # for pair in hero_list:
    #     data = list(
    #         db['non-pro'].find({'hero': pair[0], 'role': pair[1]}))
    #     res = update_build(pair[0], pair[1], data)
    update_builds()
    handle_steam()


if __name__ == '__main__':
    main()
