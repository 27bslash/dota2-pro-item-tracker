import datetime
import json
import mimetypes
import re
from collections import Counter
from operator import itemgetter

import requests
import timeago
from flask import (Flask, after_this_request, redirect, render_template,
                   request, url_for)
from flask_caching import Cache
from flask_compress import Compress

from helper_funcs.helper_imports import *
from helper_funcs.table import generate_table
from route_logic.hero_view import HeroView
from route_logic.player_view import PlayerView
from route_logic.redirect import handle_redirect
# TODO
# show alex ads

COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml',
                      'application/json', 'application/javascript']
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 500
compress = Compress()
app = Flask(__name__)
cache = Cache(config={
    'CACHE_TYPE': 'simple'
})
cache.init_app(app)
compress.init_app(app)
# minify(app=app, html=True, js=False, cssless=False)

# classes
mimetypes.add_type('application/javascript', '.js')


@app.route('/', methods=['GET'])
def index():
    data = db['hero_list'].find_one({}, {'_id': 0})
    links = [{'name': switcher(i['name']), 'id':i['id']}
             for i in data['heroes']]
    links = sorted(
        links, key=itemgetter('name'))
    img_names = [switcher(i['name']) for i in links]
    win_data = db['wins'].find()
    wins = [item for item in win_data]
    for entry in wins:
        entry['hero'] = switcher(entry['hero'])
    wins = sorted(wins, key=lambda k: k['hero'])
    total_games = hero_output.count_documents({})
    return render_template('index.html', hero_imgs=img_names, links=links, wins=wins, total_games=total_games)


@app.route('/', methods=['POST'])
@app.route('/chappie', methods=['POST'])
@app.route('/hero/<query>/starter_items', methods=['POST'])
@app.route('/hero/<query>', methods=['POST'])
@app.route('/player/<query>/starter_items', methods=['POST'])
@app.route('/player/<query>', methods=['POST'])
def item_post(query=''):
    return redirect(handle_redirect(request))


@app.route('/hero/<hero_name>/starter_items', methods=['GET'])
@app.route('/hero/<hero_name>', methods=['GET'])
@app.route('/hero/<hero_name>/starter_items/table', methods=['GET'])
@app.route('/hero/<hero_name>/table', methods=['GET'])
@cache.cached(timeout=86400, query_string=True)
def hero_get(hero_name):
    hv = HeroView()
    template = hv.templateSelector(request, '')
    if 'table' in request.url:
        return generate_table('hero', hero_name, template, request)
    kwargs = hv.hero_view(hero_name, request)
    return render_template(template, **kwargs)


@app.route('/player/<player_name>/starter_items', methods=['GET'])
@app.route('/player/<player_name>', methods=['GET'])
@app.route('/player/<player_name>/starter_items/table', methods=['GET'])
@app.route('/player/<player_name>/table', methods=['GET'])
@cache.cached(timeout=86400, query_string=True)
def player_get(player_name):
    pv = PlayerView()
    template = pv.templateSelector(request, 'player_')
    if 'table' in request.url:
        return generate_table('player', player_name, template, request)
    kwargs = pv.player_view(player_name, request)
    return render_template(template, **kwargs)


@app.route('/chappie')
@cache.cached(timeout=86400)
def chappie_get():
    data = [match['data'] for match in db['chappie'].find({})]
    replaced = [re.sub(r"\(smurf \d\)", '', doc['name'])for doc in data]
    times = [timeago.format(
        match['unix_time'], datetime.datetime.now()) for match in data]
    d = dict(Counter(replaced))
    count = {k: d[k] for k in sorted(d, key=d.get, reverse=True) if d[k] > 1}
    return render_template('chappie.html', data=data, count=count, times=times, unix_times=[match['unix_time'] for match in data])


@ app.route('/cron')
def cron():
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@ app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /"


@ app.route('/files/hero_ids')
@cache.cached(timeout=602000)
def hero_json():
    data = db['hero_list'].find_one({}, {'_id': 0})
    data = [{'name': switcher(i['name']), 'id': i['id']}
            for i in data['heroes']]
    return json.dumps({'heroes': data})


@ app.route('/files/abilities/<hero_name>')
@cache.cached(timeout=602000)
def hero_ability_json(hero_name):
    data = db['individual_abilities'].find_one(
        {'hero': hero_name})['abilities']
    return json.dumps(data)


@ app.route('/files/items')
@cache.cached(timeout=602000)
def items_json():
    data = db['all_items'].find_one({}, {'_id': 0, 'items': 1})
    return json.dumps(data)


@ app.route('/files/colors')
@cache.cached(timeout=602000)
def color_json():
    with open('colours/hero_colours.json', 'r') as f:
        data = json.load(f)
        return data


@ app.route('/files/ability_colours')
@cache.cached(timeout=602000)
def ability_color_json():
    with open('colours/ability_colours.json', 'r') as f:
        data = json.load(f)
        return data


@ app.route('/files/accounts')
@cache.cached(timeout=86400)
def acc_json():
    data = db['account_ids'].find({})
    players = [player['name'] for player in data]
    return json.dumps(players)


@ app.route('/files/win-stats')
# @cache.cached(timeout=86400)
def wins_json():
    data = db['wins'].find({}, {'_id': 0})
    wins = [item for item in data]
    for win in wins:
        win['hero'] = switcher(win['hero'])
    return json.dumps(wins)


@ app.route('/files/hero-data/<hero_name>')
@cache.cached(timeout=602000)
def hero_data(hero_name):
    url = f'https://www.dota2.com/datafeed/herodata?language=english&hero_id={hero_methods.get_id(hero_name)}'
    req = requests.get(url)
    return req.json()


@ app.route('/files/match-data/<hero_name>')
@cache.cached(timeout=86400, query_string=True)
def match_data(hero_name, role=None):
    hero_name = switcher(hero_name)
    if 'role' in request.args:
        role = request.args.get('role').replace('%20', ' ').title()
    if role:
        data = hero_output.find(
            {'hero': hero_name, 'role': role}, {'_id': 0})
    else:
        data = hero_output.find({'hero': hero_name}, {'_id': 0})
    data = [entry for entry in data]
    return json.dumps(data)


@ app.route('/files/talent-data/<hero_name>')
@cache.cached(timeout=86400, query_string=True)
def talent_data(hero_name):
    m_data = match_data(hero_name, role=None)
    if 'role' in request.args:
        m_data = match_data(hero_name, role=request.args.get(
            'role').replace('%20', ' ').title())
    talents = talent_methods.get_talent_order(m_data, switcher(hero_name))
    return json.dumps(talents)


@ app.after_request
def add_header(response):
    response.cache_control.max_age = 602000
    response.add_etag()
    return response




def main():
    app.run(debug=True)


if __name__ == '__main__':
    # update_one_entry('jakiro', 6288052800)
    # manual_hero_update('jakiro')
    main()
