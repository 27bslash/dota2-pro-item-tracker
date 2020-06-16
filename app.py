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
    # 'CACHE_TYPE': 'NULL'
})
cache.init_app(app)


@app.route('/', methods=['GET'])
def hello():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def post_req():
    if request.method == 'POST':
        text = request.form.get('t')
        vale = request.form.get('toggle_start')
        print(text, get_id(text))
        if get_id(text):
            print('hero', get_id(text))
            return redirect('/hero/'+text)
        else:
            print('invalid hero')
            return render_template('index.html')


@app.route('/hero/<hero_name>')
@cache.cached(timeout=60)
def show_items(hero_name):
    print('g')
    do_everything(hero_name)
    print('afsdg')
    entries = []
    with open('opendota_output.json', 'r') as f:
        data = json.load(f)
        hero_name = hero_name.replace(' ', '_')
        hero_name = hero_name.lower()
        print('show-items', hero_name)
        for data_i in data:
            entries.append(data_i['hero'])
        return render_template('final_items.html', hero_name=hero_name, data=data, time=90)


@app.route('/hero/<hero_name>', methods=['POST', 'GET'])
def redirect_page(hero_name):
    if request.method == 'POST':
        text = request.form.get('t')
        vlaue = request.form
        print('id test', hero_name, get_id(text), False >= 0)
        return redirect('/hero/'+text)


@app.route('/test')
def re():
    return 'sdfakl'


def do_everything(hero_name):
    output = []
    amount = 10
    start = time.time()
    asyncio.run(pro_request(hero_name, output, amount))
    asyncio.run(main(get_urls(amount), hero_name))
    delete_output()
    end = time.time()
    print("Took {} seconds to pull {} websites.".format(end - start, amount))


def is_num(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


async def request_shit(hero_name, output, amount):
    start = time.time()
    hero_name = hero_name.title()
    hero_name = hero_name.replace(' ', '%20')
    url = 'http://www.dota2protracker.com/hero/'+hero_name
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            req = await response.text()
            text = req
            # f = open('test.html', 'w')
            # f.write(text)
            # f.close()
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
            print(end-start, 'seconds')
            


async def pro_request(hero_name, output, amount):
    ret = await asyncio.gather(request_shit(hero_name, output, amount))


if __name__ == '__main__':
    app.run(debug=True)
