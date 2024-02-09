import time

import pyautogui
import glob
from hero_guides.update_builds.handle_steam import close_program, open_program
from hero_guides.update_builds.publish_guides import activate_window, move_group, snapshot_pixel_colour
from hero_guides.update_builds.remote.handle_remote import modify_remote
from hero_guides.write_guide import update_from_json


def check_for_remote():
    path = 'C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote'
    for file in glob.glob(path):
        return True
    return False
    pass


def hrf(debug=False):
    srt = time.perf_counter()
    open_program('C:\\Program Files (x86)\\Steam\\Steam.exe')
    if not debug:
        time.sleep(15)
    activate_window('Steam')
    print('steam open')
    move_group([(233, 46, 'primary'), (109, 244, 'primary')])
    # toggle steam cloud setting
    move_group([(700, 10, 'primary'), (28, 20, 'primary'),
                (66, 166, 'primary'),
                (613, 473, 'primary'),
                (785, 358, 'primary'),
                (1161, 839, 'primary')])
    print('cloud toggled')
    # delete dota 2 remote folder
    modify_remote(delete=True)
    time.sleep(2)
    print('delete cloud remote')
    # open dota 2
    move_group([(418, 429, 'primary')])
    while True:
        if snapshot_pixel_colour(1, 180):
            move_group([(418, 429, 'primary')])
            pyautogui.click()
            break
        time.sleep(3)
    print('open dota 2')
    spam_close(lambda: check_for_remote())

    time.sleep(15)
    # open_program(
    #     'C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta\\game\\bin\\win64\\dota2.exe')
    spam_close(condition=lambda: close_program('dota2.exe'))

    time.sleep(2)
    # toggle cloud setting back on
    print('toggle cloud')
    move_group([(700, 10, 'primary'), (28, 20, 'primary'),
                (66, 166, 'primary'),
                (613, 473, 'primary'),
                (785, 358, 'primary'),
                (1161, 839)])
    time.sleep(2)
    move_group([(545, 444, 'primary'),
                (961, 671, 'primary'),
                (823, 781, 'primary')])
    time.sleep(10)
    spam_close(condition=lambda: close_program('steam.exe'))
    # overwrite remote folder with new guide data
    print('update guides..')
    update_from_json()
    modify_remote()
    time.sleep(10)
    time.sleep(3)
    print('open steam again')
    open_program('C:\\Program Files (x86)\\Steam\\Steam.exe')
    time.sleep(15)
    # navigate to library and launch dota
    print('launch dota 2..')
    move_group(
        [(233, 46, 'primary'), (109, 244, 'primary'), (418, 429, 'primary')])
    time.sleep(10)
    print('time taken: ', time.perf_counter() - srt)
    pass


def spam_close(condition):
    attempts = 0
    while attempts < 15:
        bool = condition()
        if bool:
            break
        time.sleep(1)
        attempts += 1


if __name__ == '__main__':
    # print(check_for_remote())
    # move_group([(418, 429)])
    # while True:
    #     if snapshot_pixel_colour(1, 180):
    #         move_group([(418, 429)])
    #         break
    #     time.sleep(3)
    # move_group([(545, 444),
    #             (961, 671),
    #             (823, 781)])
    # update_from_json()
    # modify_remote()

    # handle_remote_folder(debug=True)
    # spam_close(condition=lambda: check_for_remote())
    pass
