import mimetypes
import asyncio
import datetime
import itertools
import json
import re
import time
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
from opendota_api import opendota_call
from route_logic.hero_view import HeroView
from route_logic.player_view import PlayerView
from route_logic.redirect import handle_redirect
# TODO
# show alex ads
# make levels accurate

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
@cache.cached(timeout=600)
def index():
    data = db['hero_list'].find_one({}, {'_id': 0})
    links = [{'name': switcher(i['name']), 'id':i['id']}
             for i in data['heroes']]
    links = sorted(
        links, key=itemgetter('name'))
    img_names = [switcher(i['name']) for i in links]
    win_data = db['wins'].find_one({})
    wins = [item for item in win_data['stats'] if 'stats' in win_data]
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
def hero_get(hero_name):
    hv = HeroView()
    template = hv.templateSelector(request, '')
    if 'table' in request.url:
        return generate_table('hero', hero_name, template, request)
    arggs = hv.hero_view(hero_name, request)
    return render_template(template, **arggs)


@app.route('/player/<player_name>/starter_items', methods=['GET'])
@app.route('/player/<player_name>', methods=['GET'])
@app.route('/player/<player_name>/starter_items/table', methods=['GET'])
@app.route('/player/<player_name>/table', methods=['GET'])
def player_get(player_name):
    pv = PlayerView()
    template = pv.templateSelector(request, 'player_')
    if 'table' in request.url:
        return generate_table('player', player_name, template, request)
    arggs = pv.player_view(player_name, request)
    return render_template(template, **arggs)


@app.route('/chappie')
def chappie_get():
    data = [match['data'] for match in db['chappie'].find({})]
    replaced = [re.sub(r"\(smurf \d\)", '', doc['name'])for doc in data]
    times = [timeago.format(
        match['unix_time'], datetime.datetime.now()) for match in data]
    d = dict(Counter(replaced))
    count = {k: d[k] for k in sorted(d, key=d.get, reverse=True)}
    return render_template('chappie.html', data=data, count=count, times=times, unix_times=[match['unix_time'] for match in data])


@ app.route('/cron')
def cron():
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@ app.route('/files/hero_ids')
def hero_json():
    data = db['hero_list'].find_one({}, {'_id': 0})
    data = [{'name': switcher(i['name']), 'id': i['id']}
            for i in data['heroes']]
    return json.dumps({'heroes': data})


@ app.route('/files/abilities/<hero_name>')
def hero_ability_json(hero_name):
    data = db['individual_abilities'].find_one(
        {'hero': hero_name})['abilities']
    return json.dumps(data)


@ app.route('/files/items')
def items_json():
    data = db['all_items'].find_one({}, {'_id': 0, 'items': 1})
    return json.dumps(data)


@ app.route('/files/colors')
def color_json():
    with open('colours/hero_colours.json', 'r') as f:
        data = json.load(f)
        return data


@ app.route('/files/ability_colours')
def ability_color_json():
    with open('colours/ability_colours.json', 'r') as f:
        data = json.load(f)
        return data


@ app.route('/files/accounts')
def acc_json():
    data = db['account_ids'].find({})
    players = [player['name'] for player in data]
    return json.dumps(players)


@ app.route('/files/win-stats')
def wins_json():
    data = db['wins'].find_one({})
    return json.dumps(data['stats'])


@ app.route('/files/hero-data/<hero_name>')
def hero_data(hero_name):
    url = f'https://www.dota2.com/datafeed/herodata?language=english&hero_id={hero_methods.get_id(hero_name)}'
    req = requests.get(url)
    return req.json()


@ app.after_request
def add_header(response):
    response.cache_control.max_age = 244800
    response.add_etag()
    return response


def manual_hero_update(hero):
    hero_output.delete_many({'hero': hero})
    asyncio.run(opendota_call(get_urls(hero), hero))
    database_methods.insert_total_picks('hero', hero, 'hero_picks')
    database_methods.insert_winrates()
    parse_request()


def update_one_entry(hero, id):
    hero_output.delete_many({'hero': hero, 'id': id})
    # hero_output.find_one_and_delete(
    #     {'hero': hero, 'id': id})
    asyncio.run(opendota_call([id], hero))


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
    # database_methods.insert_winrates()
    # manual_hero_update('hoodwink')
    # app.run(debug=True)
    # update_one_entry('windrunner', 6171594476)
    # delete_old_urls()
    # database_methods.insert_all()
    # parse_request()
    # get_winrate()
    # update_pro_accounts()
    # database_methods.insert_worst_games()
    # print(hero_methods.hero_name_from_hero_id(39))
    # manual_hero_update('jakiro')
