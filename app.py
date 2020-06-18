import os
import requests
from flask import Flask, render_template, request, url_for, redirect
from flask_caching import Cache
from opendota_api import *
from parsel import Selector
import time
import string
app = Flask(__name__)
cache = Cache(config={
    'CACHE_TYPE': 'simple'
})
cache.init_app(app)


@app.route('/', methods=['GET'])
def hello():
    query = request.args.get('query')
    print(query)
    with open('hero_ids.json', 'r') as f:
        data = json.load(f)
        img_names = []
        for i in data['heroes']:
            img_names.append(switcher(i['name']))
    return render_template('index.html', hero_imgs=img_names, links=data['heroes'])


@app.route('/', methods=['POST'])
def post_req():
    if request.method == 'POST':
        text = request.form.get('t')
        vale = request.form.get('toggle_start')
        print(text, get_id(text))
        if get_id(text):
            # print('hero', get_id(text))
            return redirect('/hero/'+text)
        else:
            print('invalid hero')
            return render_template('index.html')


@app.route('/hero/<hero_name>')
@cache.cached(timeout=60)
def show_items(hero_name):
    do_everything(hero_name)
    with open('opendota_output.json', 'r') as f:
        data = json.load(f)
        h_name = clean_name(hero_name)
        # print('show-items', hero_name, h_name)
        return render_template('final_items.html', hero_img=h_name, hero_name=hero_name, data=data, time=90)


@app.route('/hero/<hero_name>/starter_items')
@cache.cached(timeout=60)
def show_starter_items(hero_name):
    # print('starter_naem', hero_name)
    with open('opendota_output.json', 'r') as f:
        data = json.load(f)
        h_name = clean_name(hero_name)
        # print('starter-items', h_name)
        return render_template('starter_items.html', hero_img=h_name, hero_name=hero_name, data=data)


@app.route('/hero/<hero_name>/starter_items', methods=['POST', 'GET'])
@app.route('/hero/<hero_name>', methods=['POST', 'GET'])
def redirect_page(hero_name):
    if request.method == 'POST':
        text = request.form.get('t')
        vlaue = request.form
        end = ''
        # print('s', request.url, type(request.url))
        if 'starter' in request.url:
            end = '/starter_items'
        if get_id(text):
            # print('hero', get_id(text))
            return redirect('/hero/'+text)
        else:
            # print('invalid hero')
            return redirect('/hero/'+hero_name+end)


@app.route('/files/hero_ids')
def returnJson():
    with open('hero_ids.json', 'r') as f:
        data = json.load(f)
        return data


def do_everything(hero_name):
    output = []
    amount = 10
    asyncio.run(pro_request(hero_name, output, amount))
    start = time.time()
    asyncio.run(main(get_urls(amount), hero_name))
    end = time.time()
    delete_output()
    print("Took {} seconds to pull {} websites.".format(end - start, amount))


def clean_name(h_name):
    h_name = h_name.replace(' ', '_')
    h_name = h_name.lower()
    h_name = switcher(h_name)
    # print('ty', h_name)
    return h_name


def switcher(h):
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
        'vengeful_spirit': 'vengefulspirit'
    }
    # print(h, switch.get(h))
    if switch.get(h):
        return switch.get(h)
    else:
        return h


async def request_shit(hero_name, output, amount):
    start = time.time()
    hero_name = " ".join(w.capitalize() for w in hero_name.split())
    # hero_name = hero_name.replace(' ', '%20')
    print(hero_name)
    if 'Anti' in hero_name:
        hero_name = 'Anti-Mage'
    if 'Queen' in hero_name:
        hero_name = "Queen%20of%20Pain"
    url = 'http://www.dota2protracker.com/hero/'+hero_name
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            req = await response.text()
            text = req
            selector = Selector(text=text)
            table = selector.xpath('//*[@class="display compact"]//tbody//tr')
            for row in table:
                match_id = row.css('a::attr(href)').re(r".*opendota.*")[0]
                mmr = row.xpath('td')[4].css('::text').extract()[0]
                if match_id and len(output) < amount:
                    print(match_id, mmr)
                    o = [{'id': match_id}, {'mmr': mmr}]
                    output.append(o)
                with open('test.json', 'w') as outfile:
                    json.dump(output, outfile)
            end = time.time()
            print('protracker', end-start, 'seconds')


async def pro_request(hero_name, output, amount):
    ret = await asyncio.gather(request_shit(hero_name, output, amount))


if __name__ == '__main__':
    app.run(debug=True)
