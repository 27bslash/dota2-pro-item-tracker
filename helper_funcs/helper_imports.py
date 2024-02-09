from .talents import Talents
from .database.collection import *
from .database.db import Db_insert
from .hero import Hero
from .items import Items
from .switcher import switcher
from .url import delete_old_urls, get_urls, parse_request
from .accounts.download_acount_ids import update_pro_accounts
from .compute_engine import check_last_day

hero_methods = Hero()
item_methods = Items()
hero_list = hero_methods.hero_list
database_methods = Db_insert(hero_list, False) # type: ignore
talent_methods = Talents()
