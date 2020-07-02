import os
import requests
from flask import Flask, render_template, request, url_for, redirect
from flask_caching import Cache
from parsel import Selector
import time
from operator import itemgetter
import threading
from helper_funcs.helper_functions import *
from opendota_api import *
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import re
import pymongo
from pymongo import MongoClient
from bson.json_util import dumps
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
def hello():
    query = request.args.get('query')
    print(query)
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        img_names = []
        d = sorted(
            data['heroes'], key=itemgetter('name'))
        for i in d:
            img_names.append(switcher(i['name']))
    return render_template('index.html', hero_imgs=img_names, links=d)


@app.route('/', methods=['POST'])
def post_req():
    if request.method == 'POST':
        text = request.form.get('t')
        print(text, get_id(text))
        if get_id(text):
            # print('hero', get_id(text))
            return redirect('/hero/'+text)
        else:
            print('invalid hero')
            return render_template('index.html')


@app.route('/hero/<hero_name>')
@app.route('/hero/<hero_name>', methods=['POST', 'GET'])
@cache.cached(timeout=600)
def show_items(hero_name):
    f_name = hero_name.replace(' ', '_').replace('-', '_')
    f_name = hero_name.lower()
    time = []
    check_response = hero_output.find_one({'hero': f_name})
    if check_response:
        match_data = find_hero(f_name)
    else:
        do_everything(hero_name)
        match_data = find_hero(f_name)
    # print(type(match_data), match_data[0]['unix_time'])
    # try:
    #     newlist = sorted(
    #         match_data, key=itemgetter('unix_time'))
    # except Exception as e:
    #     print(traceback.format_exc())
    print('shw', time)
    return render_template('final_items.html', hero_img=clean_name(hero_name), hero_name=hero_name, data=match_data, time=90)


@app.route('/hero/<hero_name>/starter_items', methods=['POST', 'GET'])
@cache.cached(timeout=600)
def redirect_page(hero_name):
    print('get', request.referrer)
    f_name = hero_name.replace(' ', '_').replace('-', '_')
    f_name = hero_name.lower()
    match_data = []
    data = hero_output.find({'hero': f_name})
    check_response = hero_output.find_one({'hero': f_name})
    if check_response:
        match_data = find_hero(f_name)
    else:
        do_everything(hero_name)
        match_data = find_hero(f_name)
    return render_template('starter_items.html', hero_img=clean_name(hero_name), hero_name=hero_name, data=match_data)


def find_hero(hero):
    data = hero_output.find({'hero': hero}).sort('unix_time', -1)
    check_response = hero_output.find_one({'hero': hero})
    match_data = []
    for hero in data:
        match_data.append(hero)
    return match_data


@app.route('/files/hero_ids')
def returnJson():
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        return data


def do_everything(hero_name):
    output = []
    amount = 100
    start = time.time()
    asyncio.run(pro_request(hero_name, output, amount))
    asyncio.run(main(get_urls(20, hero_name), hero_name))
    delete_output()
    names = []
    end = time.time()
    print("Took {} seconds to pull {} websites.".format(end - start, amount))


def clean_name(h_name):
    h_name = h_name.replace(' ', '_')
    h_name = h_name.lower()
    h_name = switcher(h_name)
    return h_name


async def request_shit(hero_name, output, amount):
    db_hero_name = hero_name.replace(' ', '_').lower()
    try:
        res = hero_urls.delete_many({'hero': db_hero_name})
    except Exception as e:
        print(traceback.format_exc())
    start = time.time()
    output = []
    print(output)
    base = 'http://www.dota2protracker.com/hero/'
    hero_name = pro_name(hero_name)
    url = 'http://www.dota2protracker.com/hero/'+hero_name
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
                mmr = row.xpath('td')[4].css('::text').extract()[0]
                name = row.xpath('td')[1].css('::text').extract()[1]
                if match_id:
                    print(hero_name, match_id, mmr)
                    o = {'id': m_id, 'hero': db_hero_name,
                         'name': name, 'mmr': mmr}
                    hero_urls.insert_one(o)
            end = time.time()
            print('protracker', end-start, 'seconds')


async def pro_request(hero_name, output, amount):
    ret = await asyncio.gather(request_shit(hero_name, output, amount))


def opendota_call():
    names = []
    out = []
    print('input')
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i in data['heroes']:
            names.append(i['name'])
        for name in names:
            asyncio.run(pro_request(name, out, 100))
            print('1st')
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for name in names:
            asyncio.run(main(get_urls(100, name), name))
            delete_output()
            time.sleep(60)
            print('second')
    print('end', datetime.datetime.now())


if __name__ == '__main__':
    # scheduler.add_job(opendota_call, 'cron', timezone='Europe/London',
    #                   start_date=datetime.datetime.now(), hour='16', minute='16', day_of_week='tue')
    # scheduler.start()
    app.run(debug=True)
