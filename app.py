import timeago
import datetime
import os
import re
import threading
import time
from operator import itemgetter
import pymongo
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, redirect, render_template, request, url_for, after_this_request
from flask_caching import Cache
from flask_compress import Compress
from parsel import Selector
from pymongo import MongoClient
from helper_funcs.helper_functions import *
from opendota_api import *
from test import *
import itertools
import gzip
import functools
from io import BytesIO as IO
from flask_minify import minify, decorators
import urllib.parse
# TODO
# add intermediate items
# add item tooltips
# redesign ability tooltips
# add bans
# redesign scroll bar
# make tooltips not load off screen
#

cluster = pymongo.MongoClient(
    'mongodb+srv://dbuser:a12345@pro-item-tracker.ifybd.mongodb.net/pro-item-tracker?retryWrites=true&w=majority')
db = cluster['pro-item-tracker']
hero_urls = db['urls']
hero_output = db['heroes']

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
hero_methods = Hero()
item_methods = Items()
database_methods = Db_insert()
talent_methods = Talents()


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
    return render_template('index.html', hero_imgs=img_names, links=links, wins=wins)


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
    if 'table' in request.url:
        return generate_table(player_get.__name__, player_name, template)
    if 'starter_items' in request.url:
        template = 'player_starter_items.html'
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


def generate_table(func_name, search, template):
    print('generate table')
    display_name = search.replace('_', ' ').capitalize()
    check_response = hero_output.find_one({'hero': search})
    match_data = None
    key = ''
    # print('tet', request.args['draw'], request.args)
    columns = {'0': 'win', '1': None, '2': 'unix_time', '3': 'name', '4': None, '5': 'role', '6': 'lvl', '7': 'kills', '8': 'deaths', '9': 'assists',
               '10': 'last_hits', '11': 'gold', '12': 'gpm', '13': 'xpm', '14': 'hero_damage', '15': 'tower_damage', '16': 'duration', '17': 'mmr'}
    sort_direction = -1 if request.args['order[0][dir]'] == 'desc' else 1
    column = columns[request.args['order[0][column]']]
    records_to_skip = int(request.args['start'])
    length = int(request.args['length'])
    key = 'name' if func_name == 'player_get' else 'hero'
    if 'start' in template:
        if column == 'gold':
            column = 'lane_efficiency'
    if check_response:
        if 'role' in request.args:
            role = request.args.get('role').replace('%20', ' ').title()
            data = hero_output.find(
                {key: search, 'role': role}).sort(column, sort_direction).limit(length).skip(records_to_skip)
            match_data = [match for match in data]
            total_entries = [entry for entry in hero_output.find(
                {key: search, 'role': role})]
        else:
            data = hero_output.find(
                {key: search}).sort(column, sort_direction).limit(length).skip(records_to_skip)
            match_data = [match for match in data]
            total_entries = [
                entry for entry in hero_output.find({key: search})]
    result = {"draw": request.args['draw'],
              "recordsTotal": len(total_entries), "recordsFiltered": len(total_entries), "data": []}
    img_cache = 'https://ailhumfakp.cloudimg.io/v7/'
    for match in match_data:
        row_string = []
        html_string = f"<a href=https://www.opendota.com/matches/{match['id']}>"
        html_string += "<div class='purchases'>"
        if 'start' in template:
            for item in match['starting_items']:
                image = f"<img class='item-img' src={img_cache}https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/{item['key']}_lg.png>"
                html_string += "<div class='item-cell'>"
                html_string += image
                html_string += "</div>"
        else:
            for item in match['final_items']:
                image = f"<img class='item-img' src={img_cache}https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/{item['key']}_lg.png>"
                overlay = f"<div class='overlay'>{item['time']}</div>"
                html_string += "<div class='item-cell'>"
                html_string += image
                html_string += overlay
                html_string += "</div>"
            for item in match['backpack']:
                image = f"<img class='item-img' src={img_cache}https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/{item['key']}_lg.png>"
                overlay = f"<div class='overlay'>{item['time']}</div>"
                html_string += "<div class='item-cell'>"
                html_string += image
                html_string += overlay
                html_string += "</div>"
            if match['item_neutral']:
                html_string += "<div class='neutral-cell'>"
                html_string += f"<div class='circle'><img class='item-img' id='neutral-item' src={img_cache}https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/{match['item_neutral']}_lg.png>/></div></div>"
            if match['aghanims_shard']:
                image = f"<img class='item-img' id='aghanims-shard' src={img_cache}https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/aghanims_shard_lg.png>"
                overlay = f"<div class='overlay' id='shard-overlay'>{item['time']}</div>"
                html_string += "<div class='aghanims-shard-cell'>"
                html_string += image
                html_string += overlay
                html_string += "</div>"
        html_string += "</div></a>"
        html_string += "<div class='abilities'>"
        for ability in match['abilities']:
            ability_img = f"{img_cache}https://cdn.cloudflare.steamstatic.com/apps/dota2/images/abilities/{ability['img']}_hp1.png?v=5933967"
            ability_id = ability['id']
            ability_key = ability['key']
            html_string += "<div class='ability-img-wrapper'>"
            if ability['type'] == 'talent':
                image = f"<img class='table-img' src='/static/talent_img.png' alt = '{ability_key}'/>"
                html_string += f"<strong><p style='color:white; text-align:center;'>{ability['level']}</p></strong>"
                html_string += image
                html_string += "<div class='tooltip' id='talent-tooltip' style='display:none'>"
                html_string += "<div class='tooltip-line-one'>"
                html_string += f"<img src='/static/talent_img.png' height='55'><h3>{ability_key}</div></div></div>"
            else:
                image = f"<img class='table-img' src='{ability_img}' data_id='{ability_id}' data-tooltip='{ability_key}' alt='{ability_key}'>"
                html_string += f"<strong><p style='color:white; text-align:center;'>{ability['level']}</p></strong>"
                html_string += image
                html_string += "<div class='tooltip'></div>"
                html_string += "</div>"
        html_string += "</div>"
        html_string += "<div class='draft'>"
        html_string += "<div class='radiant_draft'>"
        for item in match['radiant_draft']:
            rep = item.replace("'", '')
            if item == search:
                highlight = 'icon-highlight'
            else:
                highlight = ''
            html_string += f"<a href='/hero/{item}'><i class='d2mh {rep} {highlight}'></i></a>"
        html_string += "</div>"
        html_string += "<div class='dire_draft'>"
        for item in match['dire_draft']:
            rep = item.replace("'", '')
            if item == search:
                highlight = 'icon-highlight'
            else:
                highlight = ''
            html_string += f"<a href='/hero/{item}'><i class='d2mh {rep} {highlight}'></i></a>"
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
        row_string.append(f"<p class='stats'>{match['name']}</p>")
        row_string.append(f"<i class='fas fa-copy' id='{match['id']}'></i>")
        row_string.append(f"<img src='{role_file_path}'/>")
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
                f"<p class='stats' id='gold'>{match['lane_efficiency']*100}%</p>")
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
    print('running....')
    d = {}
    output = []
    roles = ['Hard Support', 'Support', 'Safelane',
             'Offlane', 'Midlane', 'Roaming']
    try:
        with open('json_files/hero_ids.json', 'r') as f:
            data = json.load(f)
            for i, hero in enumerate(data['heroes']):
                print(hero)
                picks = hero_output.count_documents({'hero': hero['name']})
                total_wins = hero_output.count_documents(
                    {'hero': hero['name'], 'win': 1})
                if total_wins == 0 or picks == 0:
                    print('hero')
                    total_winrate = 0
                else:
                    total_winrate = (total_wins / picks) * 100

                role_dict = {'hero': hero['name'],
                             'picks': picks, 'wins': total_wins, 'winrate': total_winrate}
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
            print(db['wins'])
            db['wins'].find_one_and_replace(
                {}, {'stats': wins}, None, None, True)
    except Exception as e:
        print(traceback.format_exc())


def switcher(name):
    switch = {
        'necrophos': 'necrolyte',
        'clockwerk': 'rattletrap',
        "nature's_prophet": 'furion',
        'timbersaw': 'shredder',
        'io': 'wisp',
        'queen_of_pain': 'queenofpain',
        'doom': 'doom_bringer',
        'shadow_fiend': 'nevermore',
        'wraith_king': 'skeleton_king',
        'magnus': 'magnataur',
        'underlord': 'abyssal_underlord',
        'anti-mage': 'antimage',
        'outworld_devourer': 'obsidian_destroyer',
        'windranger': 'windrunner',
        'zeus': 'zuus',
        'vengeful_spirit': 'vengefulspirit',
        'treant_protector': 'treant',
        'centaur_warrunner': 'centaur'
    }
    # print(h, switch.get(h))
    if switch.get(name):
        return switch.get(name)
    else:
        return name


def get_hero_name_colour(hero_name):
    with open('json_files/hero_colours.json', 'r') as f:
        data = json.load(f)
        for item in data['colors']:
            if item['hero'] == hero_name:
                return tuple(item['color'])


@ app.route('/cron')
def cron():
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@ app.route('/files/hero_ids')
def hero_json():
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        return data


@ app.route('/files/abilities')
def ability_json():
    with open('json_files/stratz_abilities.json', 'r') as f:
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
    with open('json_files/hero_colours.json', 'r') as f:
        data = json.load(f)
        return data


@ app.route('/files/ability_colours')
def ability_color_json():
    with open('json_files/ability_colours.json', 'r') as f:
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


def do_everything(hero_name):
    output = []
    amount = 100
    start = time.time()
    asyncio.run(single_request(hero_name))
    # asyncio.run(main(get_urls(hero_name), hero_name))
    names = []
    end = time.time()
    print("Took {} seconds to pull {} websites.".format(end - start, amount))


def clean_name(h_name):
    h_name = h_name.replace(' ', '_')
    h_name = h_name.lower()
    h_name = switcher(h_name)
    return h_name


async def request_shit(hero_name):
    db_hero_name = hero_name.replace(' ', '_').lower()
    start = time.time()
    hero_name = hero_name.capitalize()
    base = 'http://www.dota2protracker.com/hero/'
    url = 'http://www.dota2protracker.com/hero/'+hero_name
    print(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            req = await response.text()
            text = req
            selector = Selector(text=text)
            table = selector.xpath(
                '//*[@class="display compact"]//tbody//tr')
            print(table)
            for i in reversed(range(len(table))):
                row = table[i]
                match_id = row.css('a::attr(href)').re(
                    r".*opendota.*")[0]
                m_id = re.sub(r"\D", '', match_id)
                mmr = row.xpath('td')[5].css('::text').extract()[0]
                name = row.xpath('td')[1].css('::text').extract()[1]
                # print(mmr)
                lanes = {'safelane': '1', 'mid': '2', 'roaming': '4',
                         'offlane': '3', 'unknown': '0', 'jungle': 'jungle'}
                roles = {'1': 'Safelane', '2': 'Midlane',
                         '3': 'Offlane', '4': 'Support', '5': 'Hard Support', 'roaming': 'roaming', 'jungle': 'jungle', 'unknown': []}
                print('m_id')
                if match_id:
                    o = {'id': m_id, 'hero': db_hero_name,
                         'name': name, 'mmr': mmr}
                    # print(o)
                    if hero_urls.find_one({'hero': db_hero_name, 'id': m_id}) is None:
                        print(o)
                        # hero_urls.insert_one(o)
            end = time.time()
            print('protracker', end-start, 'seconds')


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
    db['most-common-items'].delete_many({'hero': 'anti-mage'})
    delete_old_urls()
    print('input')
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i in data['heroes']:
            heroes.append(i['name'])
            database_methods.insert_talent_order(i['name'])
        strt = time.perf_counter()
        print('1st', time.perf_counter() - strt)
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for hero in heroes:
            sleep = len(get_urls(hero))

            # hero_output.delete_many({'hero': hero})

            asyncio.run(main(get_urls(hero), hero))
            database_methods.insert_total_picks('hero', hero, 'hero_picks')
            if sleep >= 60:
                sleep = 60
            print(sleep)
            time.sleep(sleep)
            pass
    parse_request()
    get_winrate()
    database_methods.insert_player_picks()
    database_methods.insert_best_games()
    print('end', (time.time()-start)/60, 'minutes')


def manual_hero_update(name):
    hero_output.delete_many({'hero': name})
    # hero_urls.delete_many({'hero': name})
    # asyncio.run(single_request(name))
    asyncio.run(main(get_urls(name), name))
    # get_winrate()


if __name__ == '__main__':
    # delete_old_urls()
    # manual_hero_update('abbadon')
    # get_winrate()
    # opendota_call()
    # do_everything('lich')
    # database_methods.insert_talent_order('hoodwink')
    # database_methods.insert_best_games()
    app.run(debug=False)
    # database_methods.insert_total_picks('hero', 'hoodwink', 'hero_picks')
    pass
