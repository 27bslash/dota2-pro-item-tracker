from .abilities import Talents, detailed_ability_info
from .database.collection import *
from .database.db import Db_insert, db
from .hero import Hero
from .items import Items
from .switcher import switcher
from .url import delete_old_urls, get_urls, parse_request

hero_methods = Hero()
item_methods = Items()
database_methods = Db_insert()
talent_methods = Talents()
