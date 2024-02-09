import itertools
import json
import time

from helper_funcs.database.collection import db, hero_output
from helper_funcs.items import Items
from helper_funcs.switcher import switcher
from helper_funcs.table import generate_table
from helper_funcs.talents import Talents

from .view import View

item_methods = Items()
talent_methods = Talents()


class HeroView(View):

    def hero_view(self, hero_name: str, request):

        start = time.perf_counter()
        display_name = hero_name.replace('_', ' ').capitalize()
        hero_name = switcher(hero_name)
        template = View.templateSelector(self,
                                         request=request, player='')
        pick_data = db['wins'].find_one({'hero': hero_name}, {'_id': 0, 'Hard Support_picks': 1, 'Support_picks': 1,
                                                              'Roaming_picks': 1, 'Offlane_picks': 1, 'Midlane_picks': 1, 'Safelane_picks': 1})
        wins = db['wins'].find_one({'hero': hero_name})
        roles = {k: pick_data[k] for k in sorted(
            pick_data, key=pick_data.get, reverse=True)}
        total = hero_output.count_documents({'hero': hero_name})
        if total > 0:
            best_games = View.role(self, hero_name, request)['best_games']
            hero_colour = self.get_hero_name_colour(hero_name)
            return {'template': template, 'hero_img': hero_name, 'display_name': display_name, 'hero_name': switcher(hero_name),
                    'time': time.time(), 'total': total, 'hero_colour': hero_colour, 'roles': roles, 'wins': wins, 'best_games': best_games}
        else:
            return {'template': template, 'hero_name': hero_name, 'hero_img': hero_name, 'display_name': display_name, 'data': [], 'time': time.time(), 'total': 0, 'hero_colour': self.get_hero_name_colour(hero_name), 'wins': wins, 'roles': roles}

    def get_hero_name_colour(self, hero_name):
        with open('colours/hero_colours.json', 'r') as f:
            data = json.load(f)
            for item in data['colors']:
                if item['hero'] == hero_name:
                    return tuple(item['color'])


def order_talents(lst, n):
    temp = 0
    ret = None
    for tal in lst:
        if tal['level'] == n:
            if tal['talent_count'] > temp:
                temp = tal['talent_count']
                side = 'l-talent' if tal['slot'] % 2 != 0 else 'r-talent'
                ret = f"lvl{n} {side}"
            elif tal['talent_count'] == temp:
                return 'EQUAL'
    return ret
