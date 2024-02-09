import shutil
import time


def cut_folder(src, dst):
    try:
        shutil.copytree(src, dst, dirs_exist_ok=True)
    except FileExistsError as exc:  # python >2.5
        print('exists')
        shutil.rmtree(dst)
        shutil.copytree(src, dst)


def modify_remote(delete=False):
    src = 'D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\backup\\remote'
    dst = 'C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote'
    try:
        # delete remote guides folder
        shutil.rmtree(dst)
        # copy modified remote folder to steam guide location
        if not delete:
            cut_folder(src, dst)
    except FileNotFoundError as e:
        print('file not found', e)


def handle_remote_folder(backup=True):
    backup_remote_folder_path = 'D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\backup\\remote'
    steam_remote_path = 'C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote'
    backup_cfg_path = 'D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\backup_cfg'
    steam_cfg_folder_path = 'F:\\SteamLibrary\\steamapps\\common\\dota 2 beta\\game\\dota\\cfg'
    if backup:
        cut_folder(steam_remote_path, backup_remote_folder_path)
        cut_folder(steam_cfg_folder_path, backup_cfg_path)
    else:
        # restore game settings
        cut_folder(backup_remote_folder_path, steam_remote_path)
        cut_folder(backup_cfg_path, steam_cfg_folder_path)


if __name__ == '__main__':
    backup_folder = 'D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\backup\\remote'
    steam_guides = 'C:\\Program Files (x86)\\Steam\\userdata\\89457522\\570\\remote'
    # copyanything(src, dst)
    # copy steam guides to backup location
    cut_folder(backup_folder, steam_guides)
    # modify_remote()
    srt = time.perf_counter()

    # handle_remote_folder()
    # move_group([(233, 46), (109, 244),(345, 427)])
    # publish_guides()
    # publish_guides()

    # close_program('steam.exe')
    # open_program('C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta\\game\\bin\\win64\\dota2.exe')
    # time.sleep(30)
    # close_program('dota.exe')
    # backup_remote(backup_folder, steam_guides)
