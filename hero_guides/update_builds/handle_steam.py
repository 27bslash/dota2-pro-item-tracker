import signal
import psutil
import os


def handle_steam():
    close_steam()
    open_steam()


def close_steam():
    try:
        steam_pid = [pid for pid in psutil.pids(
        ) if psutil.Process(pid).name() == 'steam.exe']
        if steam_pid:
            os.kill(steam_pid[0], signal.SIGTERM)
        return 'steam.exe' in steam_pid
    except Exception as e:
        print(e.__class__)
        return False


def open_steam():
    import subprocess
    subprocess.Popen(['C:\\Program Files (x86)\\Steam\\Steam.exe', '-new-tab'])
