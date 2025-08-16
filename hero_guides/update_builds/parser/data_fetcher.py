import time
import traceback
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from helper_funcs.database.collection import db
from helper_funcs.switcher import switcher
import json
from logs.log_config import update_builds_logger


class DataFetcher:
    def __init__(self) -> None:
        self.var = 'df'

    def fetch_guide_data(self, chrome, hero_name):

        build_data = db["builds"].find_one({"hero": hero_name})
        hero_name = switcher(hero_name)
        retries = 0
        max_retries = 3
        while retries < max_retries:
            try:
                if not build_data:
                    update_builds_logger.warning(
                        f"no build data for {hero_name}, skipping"
                    )
                    continue
                # chrome.get(f"https://dota2itemtracker.vercel.app/api/{hero['name']}/build")
                chrome.get(f"https://dota2itemtracker.vercel.app/api/{hero_name}/build")
                strt = time.perf_counter()
                element = WebDriverWait(chrome, 120).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "data"))
                )
                update_builds_logger.info(
                    f"data fetched for {hero_name} in: {time.perf_counter() - strt}"
                )
                # soup = BeautifulSoup(chrome.page_source, "html.parser")
                # print(element.text)
                json_data = json.loads(element.text)
                # with open(
                #     f"hero_guides/update_builds/site_guide_json/{hero_name}.json", "w"
                # ) as f:
                #     json.dump(json_data, f, indent=4)
                retries += 1
                return json_data, build_data
            except Exception as e:
                update_builds_logger.error("scrape error", traceback.format_exc())
                retries += 5
                chrome.quit()
                return None

        chrome.quit()
