import time
import traceback
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from helper_funcs.database.collection import db
from helper_funcs.switcher import switcher
import json


class DataFetcher:
    def fetch_guide_data(self, chrome, hero_name):
        build_data = db["builds"].find_one({"hero": hero_name})
        hero_name = switcher(hero_name)
        retries = 0
        max_retries = 3
        while retries < max_retries:
            try:
                if not build_data:
                    continue
                # chrome.get(f"https://dota2itemtracker.vercel.app/api/{hero['name']}/build")
                chrome.get(f"https://dota2itemtracker.vercel.app/api/{hero_name}/build")
                strt = time.perf_counter()
                element = WebDriverWait(chrome, 40).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "data"))
                )
                print(f"data fetched for {hero_name} in: {time.perf_counter() - strt}")
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
                print("scrape error", traceback.format_exc())
                retries += 5
                chrome.quit()
                return None

        chrome.quit()
