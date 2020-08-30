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

cluster = MongoClient(
    'mongodb://dbuser:a12345@ds211774.mlab.com:11774/pro-item-tracker', retryWrites=False)
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
# minify(app=app, html=True, js=True, cssless=True)


@app.route('/', methods=['GET'])
@cache.cached(timeout=600)
def index():
    query = request.args.get('query')
    hero_winrate = {}
    wins = []
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        img_names = []
        # for hero in data['heroes']:
        #     wins = hero_output.count_documents(
        #         {'hero': hero['name'], 'win': 1, 'role': 'Offlane'})
        #     print(hero['name'], wins)
        links = sorted(
            data['heroes'], key=itemgetter('name'))
        for i in links:
            img_names.append(switcher(i['name']))
        win_data = db['wins'].find_one({})
        for item in win_data['stats']:
            wins.append(item)
            # print(wins, type(wins))
        wins = sorted(wins, key=itemgetter('hero'))
    return render_template('index.html', hero_imgs=img_names, links=links, wins=wins)


@app.route('/', methods=['POST'])
def ind_post():
    if request.method == 'POST':
        text = request.form.get('search')

        if get_hero_name(text):
            suggestion = get_hero_name(text)
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
        if get_hero_name(text):
            suggestion = get_hero_name(text)
            suggestion = sorted(suggestion)
            return redirect('/hero/'+suggestion[0])
        else:
            return redirect(f'/hero/{hero_name}{starter}')


@app.route('/hero/<hero_name>/starter_items', methods=['GET'])
@app.route('/hero/<hero_name>', methods=['GET'])
def item_get(hero_name):
    start = time.perf_counter()
    match_data = []
    display_name = hero_name.replace('_', ' ').capitalize()
    total = 0
    template = 'final_items.html'
    r_start = time.perf_counter()
    if 'starter_items' in request.url:
        template = 'starter_items.html'
    roles = {'Safelane': hero_output.count_documents(
        {'hero': hero_name, 'role': 'Safelane'}),
        'Midlane': hero_output.count_documents({'hero': hero_name, 'role': 'Midlane'}),
        'Offlane': hero_output.count_documents({'hero': hero_name, 'role': 'Offlane'}),
        'Support': hero_output.count_documents({'hero': hero_name, 'role': 'Support'}),
        'Roaming': hero_output.count_documents({'hero': hero_name, 'role': 'Roaming'}),
        'Hard Support': hero_output.count_documents({'hero': hero_name, 'role': 'Hard Support'})
    }
    print('roles: ', time.perf_counter() - r_start)
    check_response_time = time.perf_counter()
    check_response = hero_output.find_one({'hero': hero_name})
    if check_response:
        if request.args:
            role = request.args.get('role').replace('%20', ' ').title()
            data = hero_output.find(
                {'hero': hero_name, 'role': role}).sort('unix_time', -1)
            match_data = [hero for hero in data]
            roles = {k: v for k, v in sorted(
                roles.items(), key=lambda item: item[1], reverse=True)}
        else:
            match_data = find_hero(hero_name)
        for k in list(roles.keys()):
            if roles[k] <= 0:
                del roles[k]
        total = hero_output.count_documents({'hero': hero_name})
        print('chk_response: ', time.perf_counter() - check_response_time)
        most_used = pro_items(match_data)
        most_used = dict(itertools.islice(most_used.items(), 10))
        max_val = list(most_used.values())[0]
        talents = get_talent_order(match_data, hero_name)
        hero_colour = get_hero_name_colour(hero_name)
        print('total Time: ', time.perf_counter()-start)
        return render_template(template, max=max_val, most_used=most_used, hero_img=clean_name(hero_name), display_name=display_name, hero_name=hero_name, data=match_data,
                               time=time.time(), total=total, role_total=len(match_data), talents=talents, hero_colour=hero_colour, roles=roles)
    else:
        return render_template(template, hero_name=hero_name, hero_img=clean_name(hero_name), display_name=display_name, data=[], time=time.time(), total=0, hero_colour=get_hero_name_colour(hero_name), roles=roles)


def find_hero(hero):
    data = hero_output.find({'hero': hero}).sort('unix_time', -1)
    match_data = []
    for hero in data:
        match_data.append(hero)
    return match_data


def get_winrate():
    print('running....')
    d = {}
    output = []
    db['wins'].delete_many({})
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
        # print(output)
        db['wins'].insert_one({'stats': output})
    except Exception as e:
        print(traceback.format_exc())
    # print(json.dumps(output, indent=2))
    # return output


def get_hero_name_colour(hero_name):
    colours = []
    with open('json_files/hero_colours.json', 'r') as f:
        data = json.load(f)
        for item in data:
            if item['hero'] == hero_name:
                # colours.append(tuple(item['color']))

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


@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    print(response.cache_control)
    response.cache_control.max_age = 300
    return response


def gzipped(f):
    print(f)

    @functools.wraps(f)
    def view_func(*args, **kwargs):
        print('test')

        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')
            print('3rd')
            if 'gzip' not in accept_encoding.lower():
                return response
            print(accept_encoding)
            response.direct_passthrough = False

            if (response.status_code < 200 or
                response.status_code >= 300 or
                    'Content-Encoding' in response.headers):
                return response
            gzip_buffer = IO()
            gzip_file = gzip.GzipFile(mode='wb',
                                      fileobj=gzip_buffer)
            gzip_file.write(response.data)
            gzip_file.close()

            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func


@gzipped
def get_data():
    return response


def do_everything(hero_name):
    output = []
    amount = 100
    start = time.time()
    asyncio.run(single_request(hero_name))
    asyncio.run(main(get_urls(hero_name), hero_name))
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
    base = 'http://www.dota2protracker.com/hero/'
    hero_name = pro_name(hero_name)
    url = 'http://www.dota2protracker.com/hero/'+hero_name
    print(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            req = await response.text()
            text = req
            selector = Selector(text=text)
            table = selector.xpath(
                '//*[@class="display compact"]//tbody//tr')
            for i in reversed(range(len(table))):
                row = table[i]
                match_id = row.css('a::attr(href)').re(
                    r".*opendota.*")[0]
                m_id = re.sub(r"\D", '', match_id)
                mmr = row.xpath('td')[5].css('::text').extract()[0]
                name = row.xpath('td')[1].css('::text').extract()[1]
                lane_select = row.xpath('td')[6].css(
                    'img::attr(src)').extract()[0]
                role_select = row.xpath('td')[7].css(
                    'img::attr(src)').extract()[0]
                lane = clean_img(lane_select)
                role = clean_img(role_select)
                # print(mmr)
                lanes = {'safelane': '1', 'mid': '2', 'roaming': '4',
                         'offlane': '3', 'unknown': '0', 'jungle': 'jungle'}
                roles = {'1': 'Safelane', '2': 'Midlane',
                         '3': 'Offlane', '4': 'Support', '5': 'Hard Support', 'roaming': 'roaming', 'jungle': 'jungle', 'unknown': []}
                if role == 'core':
                    lane = lanes[lane]
                    role = roles[lane]
                else:
                    role = roles[role]
                if match_id:
                    delete_old_urls()
                    print(hero_name, match_id, mmr, role)
                    o = {'id': m_id, 'hero': db_hero_name,
                         'name': name, 'mmr': mmr, 'role': role}
                    # print(o)
                    if hero_urls.find_one({'hero': db_hero_name, 'id': m_id}) is None:
                        # print(o)
                        hero_urls.insert_one(o)
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
    names = []
    start = time.time()
    # delete_old_urls()
    # loop = asyncio.get_event_loop()
    db['most-common-items'].delete_many({'hero': 'anti-mage'})
    print('input')
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i in data['heroes']:
            names.append(i['name'])
            # talent_order(i['name'])
        strt = time.perf_counter()
        # asyncio.run(pro_request(names))
        print('1st', time.perf_counter() - strt)
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for name in names:
            sleep = len(get_urls(name))
            asyncio.run(main(get_urls(name), name))
            # loop.run_until_complete(
            #     test(steam_api_test(name), name))
            # sync(steam_api_test(name),name)
            if sleep >= 60:
                sleep = 60
            print(sleep)
            time.sleep(sleep)
            # break
            # delete_output()
            pass
    parse_request()
    get_winrate()
    print('end', (time.time()-start)/60, 'minutes')


def manual_hero_update(name):
    hero_output.delete_many({'hero': name})
    # hero_urls.delete_many({'hero': name})
    # asyncio.run(single_request(name))
    asyncio.run(main(get_urls(name), name))
    # get_winrate()


# scheduler = BackgroundScheduler()
if __name__ == '__main__':
    # opendota_call()
    # delete_old_urls()
    # manual_hero_update('anti-mage')
    # get_winrate()
    app.run(debug=False)
