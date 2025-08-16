import os
import PyInstaller.__main__
from swinlnk.swinlnk import SWinLnk


# TODO investigate using my own parser to avoid api limits
def create_exe(pyfile: str, noconsole=False):
    if noconsole:
        PyInstaller.__main__.run([pyfile, "--onefile", "--noconsole"])
    else:
        PyInstaller.__main__.run([pyfile, "--onefile"])


def shrtcut(shortcut_name, exe_name):
    from win32com.client import Dispatch

    startup = os.path.expandvars(
        r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
    )
    shortcut_path = f"{startup}\\{shortcut_name}"

    path = shortcut_path  # Path to be saved (shortcut)
    # The shortcut target file or folder
    target = f"{os.path.abspath(f'./dist/{exe_name}')}"
    work_dir = f"{os.path.abspath('./dist')}"  # The parent folder of your file

    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = work_dir
    shortcut.save()


if __name__ == "__main__":
    import traceback

    try:
        PyInstaller.__main__.run(
            [
                "clock.py",
                "--onefile",
            ]
        )
        # create_exe('clock.py')
        shrtcut("pro-item-tracker.lnk", "clock.exe")
    except Exception:
        print(traceback.format_exc())
    try:
        create_exe("hero_guides/update_builds/update_builds.py")
        shrtcut("update_hero_guides.lnk", "update_builds.exe")
    except Exception:
        print(traceback.format_exc())
    try:
        create_exe("parse_personal_matches/get_games.py", noconsole=True)
        shrtcut("opendota_updater.lnk", "get_games.exe")
    except Exception:
        print(traceback.format_exc())
        pass
    # move_to_startup()
    # print('done')
    # sys.exit(0)
