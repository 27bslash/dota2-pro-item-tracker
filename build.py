import os
import PyInstaller.__main__
from swinlnk.swinlnk import SWinLnk


def create_exe():
    PyInstaller.__main__.run([
        'clock.py',
        '--onefile'
    ])




def shrtcut():
    import os
    from win32com.client import Dispatch
    shortcut_name = 'pro-item-tracker.lnk'
    startup = os.path.expandvars(
        r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup')
    shortcut_path = f"{startup}\\{shortcut_name}"
    
    path = shortcut_path  # Path to be saved (shortcut)
    target = f"{os.path.abspath('./dist/clock.exe')}" # The shortcut target file or folder
    work_dir = f"{os.path.abspath('./dist')}"  # The parent folder of your file

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = work_dir
    shortcut.save()


if __name__ == '__main__':
    create_exe()
    shrtcut()
    # move_to_startup()
    # print('done')
    # sys.exit(0)
