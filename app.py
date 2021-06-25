import asyncio
import datetime
import itertools
import json
import math
import time
from operator import itemgetter

import timeago
from flask import (Flask, after_this_request, redirect, render_template,
                   request, url_for)
from flask_caching import Cache
from flask_compress import Compress

from accounts.download_acount_ids import update_pro_accounts
from helper_funcs.helper_imports import *
from opendota_api import main

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


@app.route('/', methods=['GET'])
@cache.cached(timeout=600)
def index():
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        links = sorted(
            data['heroes'], key=itemgetter('name'))
        img_names = [switcher(i['name']) for i in links]
        win_data = db['wins'].find_one({})
        wins = [item for item in win_data['stats'] if 'stats' in win_data]
        total_games = hero_output.count_documents({})
        print(total_games)
    return render_template('index.html', hero_imgs=img_names, links=links, wins=wins, total_games=total_games)


@app.route('/', methods=['POST'])
def index_post():
    if request.method == 'POST':
        text = request.form.get('search')
        if db['account_ids'].find_one({'name': text}):
            return redirect('/player/'+text)
        if hero_methods.get_hero_name(text):
            suggestion = hero_methods.get_hero_name(text)
            suggestion = sorted(suggestion)
            return redirect('/hero/'+suggestion[0])
        else:
            return redirect('/')


@app.route('/hero/<hero_name>/starter_items', methods=['POST'])
@app.route('/hero/<hero_name>', methods=['POST'])
def item_post(hero_name):
    if request.method == 'POST':
        starter = ''
        if 'starter_items' in request.url:
            starter = '/starter_items'
        text = request.form.get('search')
        if db['account_ids'].find_one({'name': text}):
            return redirect('/player/'+text)
        if hero_methods.get_hero_name(text):
            suggestion = hero_methods.get_hero_name(text)
            suggestion = sorted(suggestion)
            return redirect('/hero/'+suggestion[0])
        else:
            return redirect(f'/hero/{hero_name}{starter}')


@app.route('/player/<player_name>/starter_items', methods=['POST'])
@app.route('/player/<player_name>', methods=['POST'])
def player_post(player_name):
    print('p', player_name)
    if request.method == 'POST':
        starter = ''
        if 'starter_items' in request.url:
            starter = '/starter_items'
        text = request.form.get('search')
        if db['account_ids'].find_one({'name': text}):
            return redirect('/player/'+text)
        if hero_methods.get_hero_name(text):
            suggestion = hero_methods.get_hero_name(text)
            suggestion = sorted(suggestion)
            return redirect('/hero/'+suggestion[0])
        else:
            return redirect(f'/hero/{player_name}{starter}')


@app.route('/hero/<hero_name>/starter_items', methods=['GET'])
@app.route('/hero/<hero_name>', methods=['GET'])
@app.route('/hero/<hero_name>/starter_items/table', methods=['GET'])
@app.route('/hero/<hero_name>/table', methods=['GET'])
def hero_get(hero_name):
    start = time.perf_counter()
    match_data = []
    best_games = []
    display_name = hero_name.replace('_', ' ').capitalize()
    total = 0
    template = 'final_items.html'
    if 'starter_items' in request.url:
        template = 'starter_items.html'
    if 'table' in request.url:
        return generate_table(hero_get.__name__, hero_name, template)
    r_start = time.perf_counter()
    roles_db = db['hero_picks'].find_one({'hero': hero_name})
    roles = roles_db['roles']
    print('roles: ', time.perf_counter() - r_start)
    # print('roloe', roles, hero_name)
    check_response_time = time.perf_counter()
    # print(hero_output.find({'hero': hero_name}).explain()['executionStats'])
    check_response = hero_output.find_one({'hero': hero_name})
    print('chk_time: ', time.perf_counter() - check_response_time)
    if check_response:
        # string = json.dumps(urllib.parse.parse_qs(request.args))
        if request.args:
            role = request.args.get('role').replace('%20', ' ').title()
            data = hero_output.find(
                {'hero': hero_name, 'role': role})
            # print(hero_output.find(
            #     {'hero': hero_name, 'role': role}).sort('unix_time', -1).explain()['executionStats'])
            match_data = [hero for hero in data]
            best_games = [match for match in db['best_games'].find(
                {'hero': hero_name, 'display_role': role})]
        else:
            match_data = find_hero('hero', hero_name)
            best_games = [match for match in db['best_games'].find(
                {'hero': hero_name, 'display_role': None})]
        total = roles_db['total_picks']
        most_used = item_methods.pro_items(match_data)
        most_used = dict(itertools.islice(most_used.items(), 10))
        max_val = list(most_used.values())[0]
        talents = talent_methods.get_talent_order(match_data, hero_name)
        misc = time.perf_counter()
        hero_colour = get_hero_name_colour(hero_name)
        print('misc Time: ', time.perf_counter()-misc)
        print('total Time: ', time.perf_counter()-start)
        template_time = time.perf_counter()
        r_t = render_template(template, max=max_val, most_used=most_used, hero_img=clean_name(hero_name), display_name=display_name, hero_name=hero_name, data=match_data,
                              time=time.time(), total=total, talents=talents, hero_colour=hero_colour, roles=roles, best_games=best_games)
        print('template time: ', time.perf_counter()-template_time)
        return r_t
    else:
        return render_template(template, hero_name=hero_name, hero_img=clean_name(hero_name), display_name=display_name, data=[], time=time.time(), total=0, hero_colour=get_hero_name_colour(hero_name), roles=roles)


@app.route('/player/<player_name>/starter_items', methods=['GET'])
@app.route('/player/<player_name>', methods=['GET'])
@app.route('/player/<player_name>/starter_items/table', methods=['GET'])
@app.route('/player/<player_name>/table', methods=['GET'])
def player_get(player_name):
    start = time.perf_counter()
    total = 0
    template = 'player_final_items.html'
    if 'starter_items' in request.url:
        template = 'player_starter_items.html'
    if 'table' in request.url:
        return generate_table(player_get.__name__, player_name, template)
    display_name = player_name.replace('%20', ' ')
    roles_db = db['player_picks'].find_one({'name': display_name})
    roles = roles_db['roles']
    check_response_time = time.perf_counter()
    check_response = hero_output.find_one({'name': display_name})
    print('chk_time: ', time.perf_counter() - check_response_time)
    if check_response:
        if request.args:
            role = request.args.get('role').replace('%20', ' ').title()
            data = hero_output.find(
                {'name': display_name, 'role': role}).sort('unix_time', -1)
            match_data = [hero for hero in data]
        else:
            match_data = find_hero('name', display_name)
        total = len(match_data)
        print('total Time: ', time.perf_counter()-start)
        return render_template(template, display_name=display_name, data=match_data, time=time.time(), total=total, role_total=len(match_data), roles=roles)
    else:
        return render_template(template, display_name=display_name, data=[], time=time, roles=roles, total=0)


@app.route('/matchups')
def matchups_get():

    return render_template('index.html')


def generate_table(func_name, query, template):
    # print(request.args)
    display_name = query.replace('_', ' ').capitalize()
    key = 'name' if func_name == 'player_get' else 'hero'
    check_response = hero_output.find_one({key: query})
    match_data = None
    item_data = ''
    img_cache = 'https://ailhumfakp.cloudimg.io/v7/'
    columns = {'0': 'win', '1': None, '2': 'unix_time', '3': 'name', '4': None, '5': 'role', '6': 'lvl', '7': 'kills', '8': 'deaths', '9': 'assists',
               '10': 'last_hits', '11': 'gold', '12': 'gpm', '13': 'xpm', '14': 'hero_damage', '15': 'tower_damage', '16': 'duration', '17': 'mmr'}
    sort_direction = -1 if request.args['order[0][dir]'] == 'desc' else 1
    column = columns[request.args['order[0][column]']]
    searchable = request.args['search[value]']
    search_value = mongo_search(searchable)
    records_to_skip = int(request.args['start'])
    length = int(request.args['length'])
    total_entries = []
    if 'start' in template and column == 'gold':
        column = 'lane_efficiency'
    if check_response:
        if 'role' in request.args:
            role = request.args.get('role').replace('%20', ' ').title()
            data = hero_output.find(
                {key: query, 'role': role}).sort(column, sort_direction).limit(length).skip(records_to_skip)
            match_data = [match for match in data]
            total_entries = [entry for entry in hero_output.find(
                {key: query, 'role': role})]
        else:
            if len(searchable) > 0 and len(search_value) > 0:
                aggregate = {key: query, 'hero': {"$in": search_value}}
            else:
                aggregate = {key: query}
            data = hero_output.find(
                aggregate).sort(column, sort_direction).limit(length).skip(records_to_skip)
            match_data = [match for match in data]
            total_entries = [
                entry for entry in hero_output.find({key: query})]
    result = {"draw": request.args['draw'],
              "recordsTotal": len(total_entries), "recordsFiltered": len(total_entries), "data": []}
    if len(total_entries) == 0:
        return result
    for match in match_data:
        row_string = []
        html_string = f"<a href=https://www.opendota.com/matches/{match['id']}>"
        if 'start' in template:
            html_string += "<div class='starting_items'>"
            for item in match['starting_items']:
                item_key = item['key']
                item_id = item_methods.get_item_id(item_key)
                image = f"<img class='item-img' src='https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/{item['key']}_lg.png' data_id='{item_id}' alt='{item_key}'>"
                html_string += "<div class='item-cell'>"
                html_string += image
                html_string += "<div class='tooltip' id='item-tooltip'></div>"
                html_string += "</div>"
            html_string += "</div>"
            html_string += "<div class='intermediate_items'>"
            for item in match['items']:
                intermediate_items = ['bottle', 'vanguard', 'hood_of_defiance', 'orb_of_corrosion',
                                      'soul_ring', 'buckler', 'urn', 'fluffy_hat', 'wind_lace', 'infused_raindrop', 'crown', 'bracer', 'null_talisman', 'wraith_band',
                                      'ring_of_basilius', 'headress', 'magic_wand']
                consumables = ['tango', 'flask', 'ward_observer',
                               'ward_sentry', 'smoke_of_deceit', 'enchanted_mango', 'clarity', 'tpscroll', 'dust']
                item_key = item['key']
                item_id = item_methods.get_item_id(item_key)
                # print('ty', match['id'], item['time'], item)
                if type(item['time']) is not int or item['time'] > 600:
                    break
                if item['key'] not in consumables and item['time'] < 600 and item['time'] > 0:
                    image = f"<img class='item-img' src='https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/{item['key']}_lg.png' data_id='{item_id}' alt='{item_key}'>"
                    overlay = f"<div class='overlay'>{str(datetime.timedelta(seconds=item['time']))}</div>"
                    html_string += "<div class='item-cell'>"
                    html_string += image
                    html_string += overlay
                    html_string += "<div class='tooltip' id='item-tooltip'></div>"
                    html_string += "</div>"
            html_string += "</div></a>"

        else:
            html_string += "<div class='purchases'>"
            for item in match['final_items']:
                item_key = item['key']
                image = f"<img class='item-img' src='https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/{item['key']}_lg.png' data_id='{item['id']}' alt='{item_key}'data-hero=\"{match['hero']}\">"
                overlay = f"<div class='overlay'>{item['time']}</div>"
                html_string += "<div class='item-cell'>"
                html_string += image
                html_string += overlay
                if item['key'] == 'ultimate_scepter':
                    html_string += "<div class='tooltip' id='scepter-tooltip'></div>"
                    print('asdff')
                else:
                    html_string += "<div class='tooltip' id='item-tooltip'></div>"
                html_string += "</div>"

            for item in match['backpack']:
                image = f"<img class='item-img' src='https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/{item['key']}_lg.png' data_id='{item['id']}' alt='{item_key}'data-hero=\"{match['hero']}\">"
                overlay = f"<div class='overlay'>{item['time']}</div>"
                html_string += "<div class='item-cell'>"
                html_string += image
                html_string += overlay
                if item['key'] == 'ultimate_scepter':
                    html_string += "<div class='tooltip' id='scepter-tooltip'></div>"
                else:
                    html_string += "<div class='tooltip' id='item-tooltip'></div>"
                html_string += "</div>"

            if match['item_neutral']:
                item_key = match['item_neutral']
                item_id = item_methods.get_item_id(item_key)
                html_string += "<div class='neutral-cell'>"
                html_string += f"<div class='circle'>"
                html_string += f"<img class='item-img' id='neutral-item' src='https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/{item_key}_lg.png' data_id='{item_id}' alt='{item_key}'>"
                html_string += "<div class='tooltip' id='item-tooltip'></div></div></div>"

            if match['aghanims_shard']:
                image = f"<img class='item-img' id='aghanims-shard' src='https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/aghanims_shard_lg.png' data_id='609' data-hero=\"{match['hero']}\" alt='aghanims_shard'>"
                shard_time = match['aghanims_shard'][0]['time']
                overlay = f"<div class='overlay' id='shard-overlay'>{shard_time}</div>"
                html_string += f"<div class='item-cell' id='aghanims-shard-cell'>"
                html_string += image
                html_string += overlay
                html_string += "<div class='tooltip' id='shard-tooltip'></div>"
                html_string += "</div>"

            html_string += "</div></a>"
        html_string += f"<div class='abilities' data-hero=\"{match['hero']}\">"

        for ability in match['abilities']:
            ability_img = f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/abilities/{ability['img']}.png"
            ability_id = ability['id']
            ability_key = ability['key']
            html_string += "<div class='ability-img-wrapper'>"

            if ability['type'] == 'talent':
                image = f"<img class='table-img' src='/static/talent_img.png' data_id='{ability_id}'alt='{ability_key}'>"
                html_string += f"<strong><p style='color:white; text-align:center;'>{ability['level']}</p></strong>"
                html_string += image
                html_string += "<div class='tooltip' id='talent-tooltip'></div>"
                html_string += "</div>"
            else:
                image = f"<img class='table-img' src='{ability_img}' data_id='{ability_id}' data-tooltip='{ability_key}' alt='{ability_key}'>"
                html_string += f"<strong><p style='color:white; text-align:center;'>{ability['level']}</p></strong>"
                html_string += image
                html_string += "<div class='tooltip' id='ability-tooltip'></div>"
                html_string += "</div>"

        html_string += "</div>"
        html_string += "<div class='draft'>"
        html_string += "<div class='radiant_draft'>"

        for hero in match['radiant_draft']:
            rep = hero.replace("'", '')
            highlight = ''
            if hero == query:
                highlight = 'icon-highlight'
            html_string += f"<a href='/hero/{hero}'><i class='d2mh {rep} {highlight}'></i></a>"

        html_string += "</div>"
        html_string += "<div class='dire_draft'>"
        for hero in match['dire_draft']:
            rep = hero.replace("'", '')
            highlight = ''
            if hero == query:
                highlight = 'icon-highlight'
            html_string += f"<a href='/hero/{hero}'><i class='d2mh {rep} {highlight}'></i></a>"
        html_string += "</div>"

        role_file_path = f"/static/icons/{match['role']}.png"
        role_img = f"<img src='{role_file_path}'"
        if match['win'] == 0:
            row_string.append("<div id='loss-cell'></div>")
        else:
            row_string.append("<div id='win-cell'></div>")

        row_string.append(html_string)
        row_string.append(timeago.format(
            match['unix_time'], datetime.datetime.now()))
        if func_name != 'player_get':
            row_string.append(
                f"<a href='/player/{match['name']}'><p class='stats'>{match['name']}</p></a>")
        else:
            row_string.append(
                f"<a href='/hero/{match['hero']}'><i class='d2mh {match['hero']}'></i></a>")
        row_string.append(f"<i class='fas fa-copy' id='{match['id']}'></i>")
        row_string.append(
            f"<a href=\'?role={match['role']}\'><img src='{role_file_path}'/></a>")
        row_string.append(f"<p class='stats' id='level'>{match['lvl']}</p>")
        row_string.append(f"<p class='stats' id='kills'>{match['kills']}</p>")
        row_string.append(
            f"<p class='stats' data-sort={match['deaths']} id='deaths'>{match['deaths']}</p>")
        row_string.append(
            f"<p class='stats' id='assists'>{match['assists']}</p>")
        row_string.append(
            f"<p class='stats' id='last-hits'>{match['last_hits']}</p>")
        if 'start' not in template:
            row_string.append(
                f"<p class='stats' id='gold'>{match['gold']}</p>")
        else:
            row_string.append(
                f"<p class='stats' id='gold'>{match['lane_efficiency']}%</p>")
        row_string.append(f"<p class='stats' id ='gpm'>{match['gpm']}</p>")
        row_string.append(f"<p class='stats' id ='xpm'>{match['xpm']}</p>")
        row_string.append(
            f"<p class='stats' id ='hero-d'>{match['hero_damage']}</p>")
        row_string.append(
            f"<p class='stats' id ='tower-d'>{match['tower_damage']}</p>")
        row_string.append(
            f"<p class='stats' id ='duration'>{match['duration']}</p>")
        row_string.append(f"<p class='stats' id ='mmr'>{match['mmr']}</p>")

        result['data'].append(row_string)
    return result


def find_hero(query, hero):
    data = hero_output.find({query: hero})
    s = time.perf_counter()
    match_data = [hero for hero in data]
    print('data time', time.perf_counter() - s)
    return match_data


def get_winrate():
    print('get winrate...')
    output = []
    roles = ['Hard Support', 'Support', 'Safelane',
             'Offlane', 'Midlane', 'Roaming']
    try:
        with open('json_files/hero_ids.json', 'r') as f:
            data = json.load(f)
            for i, hero in enumerate(data['heroes']):
                picks = hero_output.count_documents({'hero': hero['name']})
                total_wins = hero_output.count_documents(
                    {'hero': hero['name'], 'win': 1})
                total_bans = hero_output.count_documents(
                    {'bans': hero['name']})
                if total_wins == 0 or picks == 0:
                    total_winrate = 0
                else:
                    total_winrate = (total_wins / picks) * 100

                role_dict = {'hero': hero['name'],
                             'picks': picks, 'wins': total_wins, 'winrate': total_winrate, 'bans': total_bans}
                for role in roles:
                    wins = hero_output.count_documents(
                        {'hero': hero['name'], 'win': 1, 'role': role})
                    losses = hero_output.count_documents(
                        {'hero': hero['name'], 'win': 0, 'role': role})
                    picks = wins+losses
                    if picks > 0:
                        winrate = math.floor(wins/picks*100)
                    else:
                        winrate = 0
                    role_dict[f"{role}_picks"] = picks
                    role_dict[f"{role}_wins"] = wins
                    role_dict[f"{role}_losses"] = losses
                    role_dict[f"{role}_winrate"] = winrate
                output.append(role_dict)
                wins = sorted(output, key=itemgetter('hero'))
            # db['wins'].insert_one({'stats': wins})
            db['wins'].find_one_and_replace(
                {}, {'stats': wins}, None, None, True)
    except Exception as e:
        print(e, e.__class__)


def get_hero_name_colour(hero_name):
    with open('colours/hero_colours.json', 'r') as f:
        data = json.load(f)
        for item in data['colors']:
            if item['hero'] == hero_name:
                return tuple(item['color'])


def mongo_search(query):
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        matches = [hero['name']
                   for hero in data['heroes'] if query in hero['name']]
        return matches


@ app.route('/cron')
def cron():
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@ app.route('/files/hero_ids')
def hero_json():
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        return data


@ app.route('/files/abilities/<hero_name>')
def hero_ability_json(hero_name):
    print(hero_name)
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        with open(f"json_files/detailed_ability_info/{hero_name}.json") as f:
            data = json.load(f)
            return json.dumps(data)


@ app.route('/files/items')
def items_json():
    with open('json_files/stratz_items.json', 'r') as f:
        data = json.load(f)
        return data


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


@ app.after_request
def add_header(response):
    response.cache_control.max_age = 244800
    response.add_etag()
    return response


def clean_name(h_name):
    h_name = h_name.replace(' ', '_')
    h_name = h_name.lower()
    h_name = switcher(h_name)
    return h_name


async def pro_request(names):
    ret = await asyncio.gather(*[request_shit(hero_name) for hero_name in names])


def clean_img(s):
    x = s.split('/')[3]
    x = x.replace('_', '')
    x = x.replace('.png', '')
    x = x.replace('pos', '')
    return x


async def single_request(name):
    ret = await asyncio.gather(request_shit(name))


def opendota_call():
    heroes = []
    start = time.time()
    delete_old_urls()
    strt = time.perf_counter()
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for hero in data['heroes']:
            hero = hero['name']
            sleep = len(get_urls(hero))
            asyncio.run(main(get_urls(hero), hero))
            database_methods.insert_total_picks('hero', hero, 'hero_picks')
            database_methods.insert_total_picks('bans', hero, 'hero_picks')
            if sleep >= 60:
                sleep = 60
            print('sleeping for: ', sleep)
            time.sleep(sleep)
            pass
    parse_request()
    get_winrate()
    database_methods.insert_player_picks()
    database_methods.insert_best_games()
    update_pro_accounts()
    print('end', (time.time()-start)/60, 'minutes')


def manual_hero_update(name):
    hero_output.delete_many({'hero': name})
    # hero_urls.delete_many({'hero': name})
    # hero_output.find_one_and_delete(
    #     {'hero': 'batrider', 'id': 5947766247})
    asyncio.run(main(get_urls(name), name))


def update_one_entry(hero, id):
    hero_output.delete_many({'hero': hero, 'id': id})
    # hero_output.find_one_and_delete(
    #     {'hero': hero, 'id': id})
    asyncio.run(main([id], hero))


if __name__ == '__main__':
    # manual_hero_update('lich')
    # update_one_entry('batrider', 5965228394)
    # manual_hero_update('ancient_apparition')
    # opendota_call()
    # parse_request()
    # get_winrate()
    app.run(debug=False)
    pass
