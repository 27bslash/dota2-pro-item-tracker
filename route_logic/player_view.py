import json
import time

from helper_funcs.database.collection import db
from helper_funcs.switcher import switcher
import re
from .view import View


class PlayerView(View):

    def player_view(self, player_name: str, request):
        template = View.templateSelector(self,
                                         request=request, player='player_')
        display_name = player_name.replace('%20', ' ')
        
        regex = r"(\W)"
        subst = "\\\\\\1"
        val = re.sub(regex, subst, player_name)
        regex = f"{val}"
        roles_db = db['player_picks'].find_one(
            {'name': {"$regex": regex}})
        print('pview', regex)
        print(roles_db['roles'])
        roles = roles_db['roles']
        total = roles_db['total_picks']
        if total > 0:
            return {'template': template, 'display_name': display_name,  'time': time.time(), 'total': total, 'roles': roles}
        else:
            return {'template': template, 'display_name': display_name, 'data': [], 'time': time, 'roles': roles, 'total': 0}
