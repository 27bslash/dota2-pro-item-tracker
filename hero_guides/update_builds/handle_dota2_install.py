import os
import time

from pynput import mouse

from hero_guides.update_builds.handle_steam import open_program
from hero_guides.update_builds.publish_guides import move_group

# from hero_guides.update_builds.update_builds import update_all_hero_guides


game_location = [153, 234]
# game_location = [135, 482]


def install_dota2():
    open_program("C:\\Program Files (x86)\\Steam\\Steam.exe")
    instructions = [
        (183, game_location[1], "primary"),
        # click steam install button
        (375, 418, "primary"),
        # click drive choice
        (915, 675, "primary"),
        # click confirm button
        (901, 767, "primary"),
    ]
    move_group(instructions)
    pass


def uninstall_dota2():
    instructions = [
        (180, 51, "primary"),
        (103, 240, "secondary"),
        (209, 362, "primary"),
        (359, 352, ""),
        (338, 505, "primary"),
        # finally click uninstall button
        (1050, 611, "primary"),
    ]
    # instructions = [
    #     # library lcoation
    #     (200, 49, 'primary'),
    #     # steam options menu
    #     (191, game_location[1], 'secondary'),
    #     # click manage option
    #     (387, game_location[1] + 222, 'primary'),
    #     # click uninstall in menu
    #     (1055, game_location[1] + 120, 'primary')]
    for x, y, z in instructions:
        print(x, y, z)
    move_group(instructions, delay=0.1)
    pass


sequence = []


def on_click(x, y, button, pressed):
    if button == mouse.Button.left and pressed:
        # print('{} at {}'.format(
        #     'Pressed Left Click' if pressed else 'Released Left Click', (x, y)))
        sequence.append((x, y, "primary"))
        # Returning False if you need to stop the program when Left clicked.
    elif button == mouse.Button.right and pressed:
        sequence.append((x, y, "secondary"))
        # print('{} at {}'.format(
        #     'Pressed Right Click' if pressed else 'Released Right Click', (x, y)))
    elif button == mouse.Button.middle:
        print(sequence)
        return False


def check_if_installed():
    """loops until target file exists"""
    fpath = (
        "F:\\SteamLibrary\\steamapps\\common\\dota 2 beta\\game\\bin\\win64\\dota2.exe"
    )
    e = os.path.exists(fpath)
    if e:
        return True
    print("not installed")
    time.sleep(10)


if __name__ == "__main__":
    # try:
    #     listener = mouse.Listener(on_click=on_click)
    #     listener.start()
    #     listener.join()
    # except Exception as e:
    #     raise Exception
    # uninstall_dota2()
    # install_dota2()
    move_group([(375, 418, "primary")])
    move_group([(915, 675, "primary")])
    move_group([(901, 767, "primary")])
