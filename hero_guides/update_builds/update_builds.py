import datetime
import logging
import time
import traceback
import pyautogui
import requests
from hero_guides.update_builds.handle_dota2_install import (
    check_if_installed,
    install_dota2,
    uninstall_dota2,
)
from hero_guides.update_builds.remote.handle_remote import (
    cut_folder,
    modify_remote,
    handle_remote_folder,
)
from hero_guides.update_builds.handle_steam import (
    check_if_program_running,
    close_program,
    open_program,
)
from hero_guides.update_builds.publish_guides import (
    publish_guides,
    snapshot_pixel_colour,
)
from hero_guides.update_builds.parser.update_builds_from_site import Update_builds
from hero_guides.write_guide import get_all_guides_from_steam, write_build_to_remote
import os
import requests
from helper_funcs.database.collection import db, hero_list

logging.basicConfig(
    filename="D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\logging\\log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s:%(message)s",
    filemode="w",
)


class DotaManager:
    def __init__(self, backup=True, run_on_date=True, handle_install=True):
        self.backup = backup
        self.run_on_date = run_on_date
        self.handle_install = handle_install
        self.steam_path = "C:\\Program Files (x86)\\Steam\\Steam.exe"
        self.BACKED_UP = False
        self.image_log_path = "D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\logging\\images"

    @staticmethod
    def is_monday_710():
        return (
            datetime.datetime.now().hour == 19
            and 10 <= datetime.datetime.now().minute < 20
        )

    def dota_playable(self):
        if not check_if_installed():
            time.sleep(60)
            return False
        logging.info("Dota 2 installed!")
        pyautogui.screenshot(f"{self.image_log_path}/still_uninstalled_dota.jpg")
        self.check_validating()
        close_program("steam.exe", 10)
        return True

    @staticmethod
    def check_validating():
        """loops until play button is green"""
        pyautogui.moveTo(416, 439)
        while True:
            if snapshot_pixel_colour(2, 130):
                print("in color band blue, validating")
                time.sleep(60)
            elif snapshot_pixel_colour(1, 180):
                print("in color band green, dota is playable")
                return True

    def handle_installed(self):
        while True:
            if not self.dota_playable():
                continue
            logging.info("Updating builds...")
            Update_builds().main()
            logging.info("Restoring Steam remote folders and Dota 2 CFG folders...")
            handle_remote_folder(backup=False)
            time.sleep(10)
            self.manage_steam()
            publish_guides()
            logging.info("Published guides")
            return

    def manage_steam(self):
        logging.info("Opening Steam")
        open_program(self.steam_path, 10)
        close_program("steam.exe", 10)
        open_program(self.steam_path, 60)

    def backup_logic(self):
        print("Backing up folders...")
        handle_remote_folder(backup=True)
        close_program("steam.exe", 5)
        open_program(self.steam_path, 5)
        self.BACKED_UP = True

    def install_logic(self):
        logging.info("Uninstalling Dota 2...")
        uninstall_dota2()
        time.sleep(5)
        pyautogui.screenshot(f"{self.image_log_path}/uninstalled_dota.jpg")
        if check_if_installed():
            pyautogui.screenshot(f"{self.image_log_path}/still_installed.jpg")
            return False
        install_dota2()
        logging.info("Installing Dota 2...")
        self.handle_installed()
        return True

    @staticmethod
    def clear_logs():
        directory = "D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\logging\\images"
        files = os.listdir(directory)
        for file in files:
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def main(self):
        running = False
        self.clear_logs()
        while True:
            if self.run_on_date and not running:
                if datetime.date.today().weekday() != 0:
                    return
                elif not self.is_monday_710():
                    print("Sleeping until Monday 7:10 PM")
                    time.sleep(60)
                    continue
                else:
                    running = True

            if self.backup and not self.BACKED_UP:
                self.backup_logic()
            if self.handle_install:
                if not self.install_logic():
                    continue
                else:
                    return


d = '{"Hard Support":[[{"core":[[{"wind_lace":{"value":49.06832298136646,"adjustedValue":50.314465408805034,"time":345}},{"boots":{"value":100,"adjustedValue":100,"time":375}},{"magic_wand":{"value":89.44099378881988,"adjustedValue":90,"time":378.5}},{"arcane_boots":{"value":87.5776397515528,"adjustedValue":88.67924528301887,"time":658}}]],"situational":[[{"infused_raindrop":{"value":29.19254658385093,"adjustedValue":29.375,"time":333}},{"quelling_blade":{"value":9.316770186335404,"adjustedValue":12.578616352201259,"time":356.8666666666667}}]]},{"core":[[{"aether_lens":{"value":77.01863354037268,"adjustedValue":83.22147651006712,"time":1226.3548387096773}}]],"situational":[[{"force_staff":{"value":11.801242236024844,"adjustedValue":18.627450980392158,"time":1555}},{"glimmer_cape":{"value":26.08695652173913,"adjustedValue":37.83783783783784,"time":1555.2142857142858}}]]},{"core":[[{"blink":{"value":26.08695652173913,"adjustedValue":51.21951219512195,"time":1897.357142857143}},{"ultimate_scepter":{"value":32.91925465838509,"adjustedValue":74.64788732394366,"time":2048}}]],"situational":[[{"travel_boots":{"value":2.484472049689441,"adjustedValue":11.76470588235294,"time":2221}},{"aeon_disk":{"value":1.8633540372670807,"adjustedValue":16.666666666666664,"time":2513.6666666666665}}]]}],[[["bane_enfeeble__bane_nightmare__bane_enfeeble__bane_nightmare__bane_enfeeble__bane_fiends_grip__bane_enfeeble__bane_nightmare__bane_nightmare",27,[["bane_nightmare__bane_enfeeble__bane_enfeeble__bane_nightmare__bane_enfeeble__bane_fiends_grip__bane_enfeeble__bane_nightmare__bane_nightmare",1]]],["bane_enfeeble__bane_brain_sap__bane_brain_sap__bane_nightmare__bane_nightmare__bane_fiends_grip__bane_nightmare__bane_nightmare__bane_enfeeble",19,[["bane_brain_sap__bane_enfeeble__bane_brain_sap__bane_nightmare__bane_nightmare__bane_fiends_grip__bane_nightmare__bane_nightmare__bane_enfeeble",6],["bane_enfeeble__bane_brain_sap__bane_brain_sap__bane_nightmare__bane_nightmare__bane_fiends_grip__bane_nightmare__bane_nightmare__bane_brain_sap",2],["bane_enfeeble__bane_brain_sap__bane_nightmare__bane_brain_sap__bane_nightmare__bane_fiends_grip__bane_nightmare__bane_nightmare__bane_enfeeble",2]]]],[{"bane_enfeeble":97},{"bane_brain_sap":60},{"bane_brain_sap":73},{"bane_nightmare":118},{"bane_enfeeble":68},{"bane_fiends_grip":151},{"bane_enfeeble":59},{"bane_nightmare":109},{"bane_nightmare":77}]],[["blood_grenade__branches__circlet__magic_stick__tango",13],["blood_grenade__branches__branches__branches__circlet__tango__tango",11]]],"Support":[[{"core":[[{"boots":{"value":100,"adjustedValue":100,"time":307}},{"magic_wand":{"value":85.5072463768116,"adjustedValue":88.40579710144928,"time":421}},{"arcane_boots":{"value":82.6086956521739,"adjustedValue":82.6086956521739,"time":632,"disassemble":true}}]],"situational":[[{"quelling_blade":{"value":7.246376811594203,"adjustedValue":17.391304347826086,"time":13}},{"bracer":{"value":11.594202898550725,"adjustedValue":11.594202898550725,"time":279.5}},{"infused_raindrop":{"value":18.84057971014493,"adjustedValue":19.11764705882353,"time":440}},{"wind_lace":{"value":34.78260869565217,"adjustedValue":38.23529411764706,"time":468}}]]},{"core":[[{"aether_lens":{"value":76.81159420289855,"adjustedValue":85.48387096774194,"time":1120.3962264150944,"dissassembledComponents":[["arcane_boots","energy_booster"]]}}]],"situational":[[{"force_staff":{"value":13.043478260869565,"adjustedValue":22.5,"time":1603}},{"glimmer_cape":{"value":23.18840579710145,"adjustedValue":39.02439024390244,"time":1621}}]]},{"core":[[{"ultimate_scepter":{"value":33.33333333333333,"adjustedValue":69.6969696969697,"time":1934}},{"blink":{"value":23.18840579710145,"adjustedValue":61.53846153846154,"time":2000.5}},{"octarine_core":{"value":1.4492753623188406,"adjustedValue":50,"time":3444}},{"travel_boots":{"value":1.4492753623188406,"adjustedValue":100,"time":4682}}]],"situational":[[{"black_king_bar":{"value":4.3478260869565215,"adjustedValue":15,"time":2108}},{"invis_sword":{"value":2.898550724637681,"adjustedValue":10.526315789473683,"time":2153}}]]}],[[["bane_enfeeble__bane_nightmare__bane_enfeeble__bane_nightmare__bane_enfeeble__bane_fiends_grip__bane_enfeeble__bane_nightmare__bane_nightmare",16,[["bane_nightmare__bane_enfeeble__bane_enfeeble__bane_nightmare__bane_enfeeble__bane_fiends_grip__bane_enfeeble__bane_nightmare__bane_nightmare",3],["bane_enfeeble__bane_nightmare__bane_enfeeble__bane_nightmare__bane_enfeeble__bane_fiends_grip__bane_nightmare__bane_enfeeble__bane_nightmare",2]]]],[{"bane_enfeeble":39},{"bane_nightmare":34},{"bane_enfeeble":34},{"bane_nightmare":46},{"bane_enfeeble":35},{"bane_fiends_grip":62},{"bane_nightmare":31},{"bane_nightmare":42},{"bane_enfeeble":18}]],[["blood_grenade__branches__branches__magic_stick__tango__tango",6],["blood_grenade__branches__circlet__magic_stick__tango",5]]]}'
if __name__ == "__main__":
    # with open("hero_guides/update_builds/site_guide_json/anti-mage.json", "r") as f:
    #     data = json.load(f)
    #     parse_all(data, "Offlane")
    # with open("hero_guides/update_builds/write_guide_test.json", "r") as f:
    #     ret = {"Offlane": json.load(f)}
    #     write_build_to_remote(ret, "doom_bringer", "6.43")
    current_dir = os.getcwd()
    if current_dir == "D:\\projects\\python\\pro-item-builds":
        print("Running from current dir: ", current_dir)
        DotaManager().handle_installed()
        # DotaManager(backup=True, run_on_date=False, handle_install=True).main()

        # DotaManager(backup=False, run_on_date=False, handle_install=True).main()
    else:
        DotaManager().main()
