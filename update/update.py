import time

from colours.contrast import compute_contrast
from helper_funcs.accounts.download_acount_ids import update_pro_accounts
from helper_funcs.helper_imports import *
from update.update_abilities import dl_dota2_abilities, update_talents
from update.update_heroes import update_hero_list, update_minimap_icon
from update.update_items import update_item_ids, update_json_data


def update_app():
    old_hero_list = db['hero_list'].find_one()['heroes']
    print('uploading hero list')
    hero_list = update_hero_list()
    print('updating json....')
    # update_item_ids()
    # insert_all_items()
    update_json_data()
    print('downloading abilities...')
    dl_dota2_abilities(True)
    print('updating_talents...')
    update_talents()
    print('updating hero colours....')
    compute_contrast()
    print('updating minimap icons...')
    if len(old_hero_list) < len(hero_list):
        update_minimap_icon(hero_list=hero_list)
    print('updating account ids')
    update_pro_accounts()
    print('fini')


def weekly_update():
    update_hero_list()
    update_json_data()
    update_item_ids()


if __name__ == '__main__':
    strt = time.perf_counter()
    dl_dota2_abilities(True)
    compute_contrast()
    print(time.perf_counter() - strt)
