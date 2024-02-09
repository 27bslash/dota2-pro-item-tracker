import signal
import time
import psutil
import os


def check_if_program_running(exe: str):
    target_pid = [pid for pid in psutil.pids() if psutil.Process(pid).name() == exe]
    if target_pid:
        print(target_pid)
        return target_pid


def close_program(exe: str, sleep=0):
    try:
        target_pid = check_if_program_running(exe)
        if target_pid:
            os.kill(target_pid[0], signal.SIGTERM)
            time.sleep(sleep)
            return exe not in target_pid
    except Exception as e:
        print(e.__class__)
        time.sleep(sleep)
        return False


def open_program(path, sleep=0):
    import subprocess

    subprocess.Popen([path, "-new-tab", "-novid", "-gamestateintegration"])
    time.sleep(sleep)


if __name__ == "__main__":
    open_program("C:\\Program Files (x86)\\Steam\\Steam.exe")
    pass
