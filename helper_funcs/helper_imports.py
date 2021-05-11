from helper_funcs.hero import Hero
from helper_funcs.abilities import Talents, detailed_ability_info
from helper_funcs.items import Items
from helper_funcs.database.db import db, Db_insert
from helper_funcs.database.collection import *
from helper_funcs.url import get_urls, delete_old_urls, parse_request
from helper_funcs.switcher import switcher

hero_methods = Hero()
item_methods = Items()
database_methods = Db_insert()
talent_methods = Talents()
