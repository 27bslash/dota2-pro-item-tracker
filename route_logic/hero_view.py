from .view import View
from helper_funcs.database.collection import db, hero_output
from helper_funcs.switcher import switcher
from helper_funcs.items import Items
from helper_funcs.abilities import Talents
from helper_funcs.table import generate_table
import itertools
import json
import time
from flask import render_template
item_methods = Items()
talent_methods = Talents()


class HeroView(View):

    def hero_view(self, hero_name: str, request):
        display_name = hero_name.replace('_', ' ').capitalize()
        hero_name = switcher(hero_name)
        template = View.templateSelector(self,
                                         request=request, player='')

        roles_db = db['hero_picks'].find_one({'hero': hero_name})
        roles = roles_db['roles']
        total = roles_db['total_picks']
        check_response = hero_output.find_one({'hero': hero_name})
        if check_response:
            best_games = View.role(self, hero_name, request)['best_games']
            match_data = View.role(self, hero_name, request)['match_data']
            total = roles_db['total_picks']
            most_used = item_methods.pro_items(match_data)
            most_used = dict(itertools.islice(most_used.items(), 10))
            max_val = list(most_used.values())[0]
            talents = talent_methods.get_talent_order(match_data, hero_name)
            hero_colour = self.get_hero_name_colour(hero_name)
            return {'template': template, 'max': max_val, 'most_used': most_used, 'hero_img': hero_name, 'display_name': display_name, 'hero_name': switcher(hero_name), 'data': match_data,
                    'time': time.time(), 'total': total, 'talents': talents, 'hero_colour': hero_colour, 'roles': roles, 'best_games': best_games}
        else:
            return {'template': template, 'hero_name': hero_name, 'hero_img': hero_name, 'display_name': display_name, 'data': [], 'time': time.time(), 'total': 0, 'hero_colour': get_hero_name_colour(hero_name), 'roles': roles}

    def get_hero_name_colour(self, hero_name):
        with open('colours/hero_colours.json', 'r') as f:
            data = json.load(f)
            for item in data['colors']:
                if item['hero'] == hero_name:
                    return tuple(item['color'])
