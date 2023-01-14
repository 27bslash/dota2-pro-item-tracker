import datetime
import json
import mimetypes
import re
from collections import Counter
from operator import itemgetter

from flask import Flask, jsonify, make_response, redirect, render_template, request
from flask_cors import CORS
from flask_caching import Cache
from flask_compress import Compress
import time

from helper_funcs.helper_imports import *
from helper_funcs.table import generate_table
from route_logic.hero_view import HeroView
from route_logic.player_view import PlayerView
from route_logic.redirect import handle_redirect
from helper_funcs.database.collection import player_names, hero_list, all_items
# TODO
# show alex ads

COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml',
                      'application/json', 'application/javascript']
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 500
compress = Compress()
app = Flask(__name__)
CORS(app)
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

def hero_get(hero_name):
    hv = HeroView()
    template = hv.templateSelector(request, '')
    if 'table' in request.url:
        return generate_table('hero', hero_name, template, request)
    kwargs = hv.hero_view(hero_name, request)
    return render_template(template, **kwargs)


@app.route('/hero/<hero_name>/react-test', methods=['GET'])
def react_hero_test(hero_name):
    st = time.perf_counter()
    count = 0
    roles = ['Hard Support', 'Support',
             'Roaming', 'Offlane', 'Midlane', 'Safelane']
    role_picks = {}
    pick_data = db['test_hero_picks'].find_one({'hero': hero_name}, {'_id': 0})
    # for role in roles:
    #     c = list(hero_output.find({'hero': hero_name, 'role': role}))
    #     # wins = hero_output.count_documents(
    #     #     {'hero': hero_name, 'role': role, 'win': 1})
    #     wins = [0 for match in c if match['win'] == 1]
    #     role_picks[role] = {'picks': len(c), 'wins': len(wins)}

    # print(role_picks)
    length = request.args.get('length')
    skip = request.args.get('skip')
    role = request.args.get('role')
    query = {'hero': hero_name}
    if role:
        query = {'hero': hero_name, 'role': role}
    if length or skip:
        length = int(length)
        skip = int(skip)
        o = list(hero_output.find(query,
                                  {'_id': 0}).sort('unix_time', -1).limit(length).skip(skip))
    else:
        o = list(hero_output.find(query,
                                  {'_id': 0}).sort('unix_time', -1))

    # print(d)
    print(time.perf_counter() - st)
    res = jsonify({'data': o, 'picks': pick_data})
    res.cache_control.max_age = 1000
    res.cache_control.public = True
    print(res.cache_control)
    return res


@ app.route('/player/<player_name>/react-test')
def react_player_test(player_name):
    display_name = player_name.replace('%20', ' ')
    print('in')
    regex = r"(\W)"
    subst = "\\\\\\1"
    val = re.sub(regex, subst, display_name)
    regex = f"{val}"
    roles_db = db['tpp'].find_one(
        {'name': player_name}, {'_id': 0})
    length = request.args.get('length')
    skip = request.args.get('skip')
    role = request.args.get('role')
    query = {'name': {"$regex": regex}}
    if role:
        query = {'name': {"$regex": regex}, 'role': role}
    if length or skip:
        length = int(length)
        skip = int(skip)
        o = list(hero_output.find(query,
                                  {'_id': 0}).sort('unix_time', -1).limit(length).skip(skip))
    else:
        o = list(hero_output.find(query,
                                  {'_id': 0}).sort('unix_time', -1))
    # pick_data = db['player_picks'].find_one(
    #     {'name': player_name}, {'_id': 0})
    # print(roles_db)
    res = jsonify({'data': o, 'picks': roles_db})
    res.cache_control.max_age = 1000
    return res

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
@cache.cached()
def hero_json():
    data = hero_list
    print('hero_list len', len(hero_list))
    hero_ids = [{'name': switcher(i['name']), 'id': i['id']}
                for i in data]
    data = json.dumps({'heroes': hero_ids})
    res = make_response(json.dumps({'heroes': hero_ids}))
    res.cache_control.max_age = 602000
    res.add_etag()
    return res


@ app.route('/files/abilities/<hero_name>')
@ cache.cached(timeout=602000)
def hero_ability_json(hero_name):
    data = db['hero_stats'].find_one(
        {'hero': hero_name})['abilities']
    res = make_response(data)
    res.cache_control.max_age = 602000
    res.add_etag()
    return res


@ app.route('/files/items')
def items_json():
    data = all_items
    res = make_response({'items': data})
    res.cache_control.max_age = 602000
    res.add_etag()
    return res


@ app.route('/files/colors')
def color_json():
    with open('colours/hero_colours.json', 'r') as f:
        data = json.load(f)
        res = make_response(data)
        res.cache_control.max_age = 602000
        res.add_etag()
        return res


@ app.route('/files/<hero_name>/best-games')
def best_games(hero_name):
    if request.args:
        role = request.args.get('role').replace('%20', ' ').title()
        best_games = [match for match in db['best_games'].find(
            {'hero': hero_name, 'display_role': role}, {'_id': 0})]
        print(best_games)
    else:
        best_games = [match for match in db['best_games'].find(
            {'hero': hero_name, 'display_role': None}, {'_id': 0})]
    return {'best_games': best_games}
@ app.route('/files/ability_colours')
@cache.cached(timeout=602000)
def ability_color_json():
    with open('colours/ability_colours.json', 'r') as f:
        data = json.load(f)
        return data


@ app.route('/files/accounts')
def acc_json():
    # data = db['account_ids'].find({})
    # players = [player['name'] for player in data]
    # print(accounts)
    se = set()
    for name in player_names:
        match = re.search(r".+(?=\()", name)
        if match:
            name = match.group(0).strip()
        se.add(name)
    data = json.dumps(list(se))
    res = jsonify(data)
    res.cache_control.max_age = 602000
    return res


@ app.route('/files/win-stats')
# @cache.cached(timeout=86400)
def wins_json():
    data = db['wins'].find({}, {'_id': 0})
    wins = [item for item in data]
    for win in wins:
        win['hero'] = switcher(win['hero'])
    resp = jsonify(wins)
    resp.cache_control.max_age = 1000
    return resp


@ app.route('/files/hero-data/<hero_name>')
def hero_data(hero_name):
    req = db['hero_stats'].find_one({'hero': hero_name}, {'_id': 0})
    res = make_response(req)
    res.cache_control.max_age = 602000
    res.add_etag()
    return res


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
    res = make_response(data)
    res.cache_control.max_age = 1000
    res.add_etag()
    return res


@ app.route('/files/talent-data/<hero_name>')
def talent_data(hero_name):
    role = request.args.get('role')
    m_data = match_data(hero_name, role=None)
    if 'role' in request.args:
        m_data = match_data(hero_name, role=role)
    talents = talent_methods.get_talent_order(m_data, switcher(hero_name))
    return json.dumps(talents)




def main():
    app.run(debug=True)


if __name__ == '__main__':
    # update_one_entry('jakiro', 6288052800)
    # manual_hero_update('jakiro')
    main()
