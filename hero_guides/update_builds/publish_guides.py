import time
from random import randint, uniform

import pyautogui
import pygetwindow as gw
from pyclick import HumanClicker

from hero_guides.update_builds.handle_steam import close_program, open_program


def publish_guides():
    hc = HumanClicker()
    open_dota2(debug=False)
    activate_window("Dota 2")
    hc.move((randint(0, 1920), randint(0, 1080)), uniform(0.1, 0.4))
    hc.click()
    time.sleep(uniform(4, 9))
    # open heroes tab on dota 2
    hc.move((randint(2325 - 1920, 2450 - 1920), randint(10, 55)), uniform(0.1, 0.4))
    hc.click()
    time.sleep(uniform(1, 2))
    # open guides tab
    hc.move((randint(2457 - 1920, 2589 - 1920), randint(87, 98)), uniform(0.05, 0.18))
    time.sleep(uniform(1, 2))
    hc.click()
    # click publish all button
    hc.move((randint(3204 - 1920, 3388 - 1920), randint(897, 929)), uniform(0.05, 0.6))
    time.sleep(uniform(1, 3))
    hc.click()
    print("publishing guides...")
    i = 0
    while i < 300:
        pyautogui.screenshot(
            f"D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\logging\\images\\publish_guides_{i}.jpg"
        )
        time.sleep(100)
        i += 50
    pyautogui.screenshot(
        "D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\logging\\images\\published_guides_dota.jpg"
    )
    spam_close(condition=lambda: close_program("dota2.exe"))
    time.sleep(5)
    spam_close(condition=lambda: close_program("steam.exe"))


def activate_window(window):
    all_title = gw.getAllTitles()
    print(all_title)
    while True:
        try:
            win = gw.getWindowsWithTitle(window)[0]
            win.activate()
            active_window = gw.getActiveWindow()
            if active_window and active_window.title == window:
                print(win, active_window.title, window)
                return True
            else:
                time.sleep(1)
                continue
        except Exception as e:
            print("exception", e)
            time.sleep(1)
            continue


def spam_close(condition):
    attempts = 0
    while attempts < 15:
        bool = condition()
        if bool:
            break
        time.sleep(1)
        attempts += 1


def curr_pos():
    hc = HumanClicker()
    while True:
        print(pyautogui.position())
        x, y = pyautogui.position()
        px = pyautogui.pixel(x, y)
        print(px)
        time.sleep(0.1)


def snapshot_pixel_colour(colour_idx: int, min_val: int):
    x, y = pyautogui.position()
    px = pyautogui.pixel(int(x), int(y))
    return px[colour_idx] > min_val


def open_dota2(debug=False):
    open_program("C:\\Program Files (x86)\\Steam\\Steam.exe")
    if not debug:
        print("sleep")
        time.sleep(15)
    print("steam open")
    open_program(
        "F:\\SteamLibrary\\steamapps\\common\\dota 2 beta\\game\\bin\\win64\\dota2.exe"
    )
    # open steam library
    # move_group([(233, 46), (109, 244)])
    # move_group([(418, 429)], click=True)
    # while True:
    #     if snapshot_pixel_colour(1, 180):
    #         move_group([(418, 429)], click=True)
    #         print('click dota 2 play button')
    #         # pyautogui.click()
    #         break
    #     time.sleep(3)
    # time.sleep(10)
    print("switch to dota 2 window")
    # activate_window('Dota 2')
    time.sleep(15)


def move_group(coords: list, delay=0.5):
    # 56 156
    # 613 473
    # 785 358
    # 1161 839
    # toggles steam cloud
    # delete remote
    # 220 53
    # 409 671
    # 532 448
    # 775 664
    # 809 787
    # overwrite cloud save with local save
    for x, y, mouse_button in coords:
        pyautogui.moveTo(x, y, delay)
        if mouse_button:
            pyautogui.click(button=mouse_button)


if __name__ == "__main__":
    # pyautogui.screenshot(
    #     'D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\logging\\images\\publish_guides.jpg')
    publish_guides()
    # curr_pos()
    # curr_pos()
    # open_dota2(debug=True)
    # spam_close('steam.exe')
    # close_program('steam.exe')

    # 56 156
    # 613 473
    # 785 358
    # 1161 839
    # toggles steam cloud
    # delete remote
    # 220 53
    # 409 671
    # 532 448
    # 775 664
    # 809 787

    # load save from local
    # 545 444
    # 961 671
    # 823 781
    # overwrite cloud save with local save
