import os
import PyInstaller.__main__
from swinlnk.swinlnk import SWinLnk


def create_exe(pyfile: str, noconsole=False):
    if noconsole:
        PyInstaller.__main__.run([
            pyfile,
            '--onefile', '--noconsole'
        ])
    else:
        PyInstaller.__main__.run([
            pyfile,
            '--onefile'
        ])


def shrtcut(shortcut_name, exe_name):
    import os
    from win32com.client import Dispatch
    startup = os.path.expandvars(
        r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup')
    shortcut_path = f"{startup}\\{shortcut_name}"

    path = shortcut_path  # Path to be saved (shortcut)
    # The shortcut target file or folder
    target = f"{os.path.abspath(f'./dist/{exe_name}')}"
    work_dir = f"{os.path.abspath('./dist')}"  # The parent folder of your file

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = work_dir
    shortcut.save()


if __name__ == '__main__':
    try:
        PyInstaller.__main__.run([
            'clock.py',
            '--onefile',
        ])
        # create_exe('clock.py')
        shrtcut('pro-item-tracker.lnk', 'clock.exe')
    except Exception as e:
        import traceback
        print(traceback.format_exc())
    try:
        create_exe('hero_guides/update_builds/update_builds.py')
        shrtcut('update_hero_guides.lnk', 'update_builds.exe')
    except Exception as e:
        import traceback
        print(traceback.format_exc())
    create_exe()
    shrtcut()
    # move_to_startup()
    # print('done')
    # sys.exit(0)
