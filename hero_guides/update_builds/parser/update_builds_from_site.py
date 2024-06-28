import json
import logging
import time
import traceback

import requests
from hero_guides.update_builds.parser.parse_abilities import AbilityParser
from hero_guides.update_builds.parser.parse_items import ItemParser
from hero_guides.update_builds.parser.data_fetcher import DataFetcher

from hero_guides.write_guide import write_build_to_remote


import requests
from helper_funcs.database.collection import hero_list, db
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

logging.basicConfig(
    filename="D:\\projects\\python\\pro-item-builds\\hero_guides\\update_builds\\logging\\log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s:%(message)s",
    filemode="w",
)


class Update_builds(ItemParser, AbilityParser, DataFetcher):
    def __init__(self, debug=False) -> None:
        super().__init__()
        self.debug = debug
        self.chrome = self.setup_chrome_driver()

    def setup_chrome_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("log-level=3")
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=chrome_options
        )
        return driver

    def reset_chrome_driver(self):
        self.chrome = self.setup_chrome_driver()

    def parse_all(self, site_data, role: str):
        item_build = self.parse_items(site_data[role])
        starting_items = self.parse_starting_items(build_data=site_data[role])
        neutral_tooltips, neutral_item_build = self.parse_neutrals(
            build_data=site_data[role]
        )
        item_build["tooltip"] = item_build["tooltip"] | neutral_tooltips
        item_build["ItemBuild"] = item_build["ItemBuild"] | neutral_item_build
        facet_build = site_data[role]["facet_builds"]
        ability_build = self.parse_abilities(site_data[role])
        o = {
            "starting_items": starting_items,
            "items": item_build,
            "abilities": ability_build,
            "facets": facet_build,
        }
        return o

    def update_all_guides_from_site(self):
        strt = time.perf_counter()
        req = requests.get(
            "https://www.dota2.com/datafeed/patchnoteslist?language=english"
        ).json()
        patch = req["patches"][-1]["patch_number"]

        for i, hero in enumerate(hero_list):
            doc_count = db["non-pro"].count_documents({"hero": hero["name"]})
            print(hero["name"], doc_count)
            if doc_count < 10:
                print("not enough data")
                continue
            try:
                all_builds = self.filter_guides_by_role(i, hero)
                if not all_builds:
                    continue
                else:
                    write_build_to_remote(all_builds, hero["name"], patch, self.debug)
                pass
            except Exception as e:
                logging.warn(hero["name"], e)
                continue
        print("update builds time taken: ", time.perf_counter() - strt)

    def filter_guides_by_role(self, i, hero):
        ret = {}
        data = self.fetch_guide_data(self.chrome, hero["name"])
        if not data:
            print("no data", hero["name"])
            self.reset_chrome_driver()
            return False
        seen_roles = []
        for role in data:
            print(f"{i}/{len(hero_list)}", hero["name"], role)
            if (
                role == "Support"
                and "Roaming" in seen_roles
                or role == "Roaming"
                and "Support" in seen_roles
            ):
                continue
            seen_roles.append(role)
            ret[role] = self.parse_all(data, role)
        return ret

    def main(self):
        self.update_all_guides_from_site()


if __name__ == "__main__":
    Update_builds(debug=False).main()
