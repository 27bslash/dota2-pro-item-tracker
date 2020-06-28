import os
import requests
from flask import Flask, render_template, request, url_for, redirect
from flask_caching import Cache
from opendota_api import *
from parsel import Selector
import time
from operator import itemgetter
from helper_funcs.helper_functions import *
import threading

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
    # return render_template('index.html', hero_imgs=img_names, links=d)
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
    file = f"json_files/hero_output/{f_name}.json"
    with open(file, 'r') as f:
        d = json.load(f)
        h_name = clean_name(hero_name)
        if len(d) < 1 or os.stat(file).st_size == 0:
            do_everything(hero_name)
        with open(file, 'r') as f:
            data = json.load(f)
            return render_template('final_items.html', hero_img=h_name, hero_name=hero_name, data=data, time=90)


@app.route('/hero/<hero_name>/starter_items', methods=['POST', 'GET'])
# @cache.cached(timeout=600)
def redirect_page(hero_name):
    print('get', request.referrer)
    if request.method == 'POST':
        text = request.form.get('t')
        f_name = hero_name.replace(' ', '_').replace('-', '_')
        f_name = hero_name.lower()
    with open(f'json_files/hero_output/{hero_name}.json', 'r') as f:
        data = json.load(f)
        return render_template('starter_items.html', hero_img=clean_name(hero_name), hero_name=hero_name, data=data)


@app.route('/files/hero_ids')
def returnJson():
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        return data


def do_everything(hero_name):
    output = []
    amount = 100
    # asyncio.run(pro_request(hero_name, output, amount))
    asyncio.run(main(get_urls(20, hero_name), hero_name))
    delete_output()
    start = time.time()
    names = []
    end = time.time()
    print("Took {} seconds to pull {} websites.".format(end - start, amount))


def clean_name(h_name):
    h_name = h_name.replace(' ', '_')
    h_name = h_name.lower()
    h_name = switcher(h_name)
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
        'vengeful_spirit': 'vengefulspirit',
        'treant_protector': 'treant',
        'centaur_warrunner': 'centaur'
    }
    # print(h, switch.get(h))
    if switch.get(h):
        return switch.get(h)
    else:
        return h


async def request_shit(hero_name, output, amount):
    start = time.time()
    output = []
    print(output)
    names = ['Anti-Mage', 'timbersaw']
    base = 'http://www.dota2protracker.com/hero/'
    hero_name = pro_name(hero_name)
    url = 'http://www.dota2protracker.com/hero/'+hero_name
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            with open(f'json_files/hero_urls/{hero_name}.json', 'w') as outfile:
                req = await response.text()
                text = req
                selector = Selector(text=text)
                table = selector.xpath(
                    '//*[@class="display compact"]//tbody//tr')
                for i in reversed(range(len(table))):
                    row = table[i]
                    match_id = row.css('a::attr(href)').re(
                        r".*opendota.*")[0]
                    mmr = row.xpath('td')[4].css('::text').extract()[0]
                    name = row.xpath('td')[1].css('::text').extract()[1]
                    if match_id:
                        print(hero_name, match_id, mmr)
                        o = {'id': match_id, 'name': name, 'mmr': mmr}
                        output.append(o)
                end = time.time()
                print('protracker', end-start, 'seconds')
                json.dump(output, outfile, indent=4)
                output = []


async def pro_request(hero_name, output, amount):
    ret = await asyncio.gather(request_shit(hero_name, output, amount))


def opendota_call():
    names = []
    out = []
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i in data['heroes']:
            names.append(i['name'])
        asyncio.gather(*[request_shit(h, out, 100) for h in names])
        for i, e in enumerate(data['heroes']):
            asyncio.run(main(get_urls(20, e['name']), e['name']))
            delete_output()
            print(i)
            time.sleep(60)
    time.sleep(604800)

# opendota_call()


def run1():
    return 't'


if __name__ == '__main__':
    thread1 = threading.Thread(target=opendota_call)
    # thread1.start()
    app.run(debug=False)
