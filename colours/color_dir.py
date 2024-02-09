import os
import shutil
from helper_funcs.database.collection import hero_list


def make_dir():
    path = "D:\\projects\\python\\pro-item-builds\\colours\\ability_images"
    if not os.path.isdir(path):
        os.mkdir(path)
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        try:
            shutil.rmtree(filepath)
        except OSError:
            os.remove(filepath)
    for hero in hero_list:
        hero_name = hero["name"]
        os.mkdir(f"{path}/{hero_name}")


if __name__ == "__main__":
    make_dir()
