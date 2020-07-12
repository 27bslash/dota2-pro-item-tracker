import datetime
import os
import re
import threading
import time
from operator import itemgetter
import pymongo
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, redirect, render_template, request, url_for
from flask_caching import Cache
from parsel import Selector
from pymongo import MongoClient
from helper_funcs.helper_functions import *
from opendota_api import *

cluster = MongoClient(
    'mongodb://dbuser:a12345@ds211774.mlab.com:11774/pro-item-tracker', retryWrites=False)
db = cluster['pro-item-tracker']
hero_urls = db['urls']
hero_output = db['heroes']


app = Flask(__name__)
cache = Cache(config={
    'CACHE_TYPE': 'simple'
})
cache.init_app(app)


@app.route('/', methods=['GET'])
def index():
    query = request.args.get('query')
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        img_names = []
        d = sorted(
            data['heroes'], key=itemgetter('name'))
        for i in d:
            img_names.append(switcher(i['name']))
    return render_template('index.html', hero_imgs=img_names, links=d)


@app.route('/', methods=['POST'])
def ind_post():
    if request.method == 'POST':
        text = request.form.get('t')
        if get_hero_name(text):
            suggestion = get_hero_name(text)
            print('yuii', suggestion)
            suggestion = sorted(suggestion)
            print('yu', suggestion)
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
        text = request.form.get('t')
        if get_hero_name(text):
            suggestion = get_hero_name(text)
            suggestion = sorted(suggestion)
            print('shw-items', suggestion)
            return redirect('/hero/'+suggestion[0])
        else:
            return redirect(f'/hero/{hero_name}{starter}')


@app.route('/hero/<hero_name>/starter_items', methods=['GET'])
@app.route('/hero/<hero_name>', methods=['GET'])
# @cache.cached(timeout=600)
def item_get(hero_name):
    match_data = []
    f_name = hero_name.replace(' ', '_').replace('-', '_')
    f_name = hero_name.lower()
    display_name = hero_name.replace('_', ' ').capitalize()
    total = 0
    template = 'final_items.html'
    if 'starter_items' in request.url:
        template = 'starter_items.html'
    roles = {'Safelane': hero_output.count_documents(
        {'hero': f_name, 'role': 'Safelane'}),
        'Midlane': hero_output.count_documents({'hero': f_name, 'role': 'Midlane'}),
        'Offlane': hero_output.count_documents({'hero': f_name, 'role': 'Offlane'}),
        'Support': hero_output.count_documents({'hero': f_name, 'role': 'Support'}),
        'Roaming': hero_output.count_documents({'hero': f_name, 'role': 'roaming'}),
        'Hard Support': hero_output.count_documents({'hero': f_name, 'role': 'Hard Support'})
    }
    data = hero_output.find({'hero': f_name})
    check_response = hero_output.find_one({'hero': f_name})
    if check_response:
        match_data = find_hero(f_name)
        total = len(match_data)
    else:
        do_everything(hero_name)
        match_data = find_hero(f_name)
        total = len(match_data)
    if request.args:
        match_data = []
        role = request.args.get('role').replace('%20', ' ').title()
        data = hero_output.find(
            {'hero': f_name, 'role': role}).sort('unix_time', -1)
        for hero in data:
            match_data.append(hero)
    roles = {k: v for k, v in sorted(
        roles.items(), key=lambda item: item[1], reverse=True)}
    for k in list(roles.keys()):
        if roles[k] <= 0:
            del roles[k]
    get_hero_name_colour(hero_name)
    return render_template(template, hero_img = clean_name(hero_name), display_name = display_name, hero_name = hero_name, data = match_data,
                           time = time.time(), total = total, hero_colour = get_hero_name_colour(hero_name), roles = roles)


def find_hero(hero):
    data=hero_output.find({'hero': hero}).sort('unix_time', -1)
    match_data=[]
    for hero in data:
        match_data.append(hero)
    return match_data


def get_hero_name_colour(hero_name):
    with open('json_files/hero_colours.json', 'r') as f:
        data=json.load(f)
        for item in data:
            if item['hero'] == hero_name:
                return tuple(item['color'])


@ app.route('/cron')
def cron():
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@ app.route('/files/hero_ids')
def returnJson():
    with open('json_files/hero_ids.json', 'r') as f:
        data=json.load(f)
        return data


def do_everything(hero_name):
    output=[]
    amount=100
    start=time.time()
    asyncio.run(single_request(hero_name))
    asyncio.run(main(get_urls(amount, hero_name), hero_name))
    delete_output()
    names=[]
    end=time.time()
    print("Took {} seconds to pull {} websites.".format(end - start, amount))


def clean_name(h_name):
    h_name=h_name.replace(' ', '_')
    h_name=h_name.lower()
    h_name=switcher(h_name)
    return h_name


async def request_shit(hero_name):
    db_hero_name=hero_name.replace(' ', '_').lower()
    start=time.time()
    base='http://www.dota2protracker.com/hero/'
    hero_name=pro_name(hero_name)
    url='http://www.dota2protracker.com/hero/'+hero_name
    print(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url = url) as response:
            req=await response.text()
            text=req
            selector=Selector(text = text)
            table=selector.xpath(
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
    delete_old_urls()
    print('input')
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i in data['heroes']:
            names.append(i['name'])

        strt = time.perf_counter()
        asyncio.run(pro_request(names))
        print('1st', time.perf_counter() - strt)
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for name in names:
            asyncio.run(main(get_urls(100, name), name))
            delete_output()
            time.sleep(60)
    print('end', (time.time()-start)/60, 'minutes')


# scheduler = BackgroundScheduler()
if __name__ == '__main__':
    # scheduler.add_job(opendota_call, 'cron', timezone='Europe/London',
    #                   start_date=datetime.datetime.now(), hour='15', minute='55', second='40', day_of_week='mon-sun')
    # scheduler.start()
    app.run(debug=False)
