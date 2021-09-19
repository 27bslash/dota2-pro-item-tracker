from helper_funcs.switcher import switcher
from helper_funcs.hero import Hero
from helper_funcs.database.collection import db
hero_methods = Hero()


def handle_redirect(request):
    if request.method == 'POST':
        text = request.form.get('search')
        if db['account_ids'].find_one({'name': text}):
            return '/player/'+text
        if hero_methods.get_hero_name(text):
            suggestion = hero_methods.get_hero_name(text)
            suggestion = sorted(suggestion)
            return '/hero/'+switcher(suggestion[0])
        else:
            return request.url
