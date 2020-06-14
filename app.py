import os
import requests
from flask import Flask, render_template, request, url_for, redirect
from opendota_api import *
from parsel import Selector
import time
import string
app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def post_req():
    if request.method == 'POST':
        text = request.form.get('t')
        if get_id(text) >= 0:
            print('hero')
            return redirect('/hero/'+text)
        else:
            print('invalid hero')
            return render_template('index.html')


@app.route('/hero/<hero_name>')
def show_items(hero_name):
    do_everything(hero_name)
    entries = []
    with open('opendota_output.json', 'r') as f:
        data = json.load(f)
        hero_name = hero_name.replace(' ', '_')
        hero_name = hero_name.lower()
        print('show-items', hero_name)
        for data_i in data:
            entries.append(data_i['hero'])
        return render_template('final_items.html', hero_name=hero_name, data=data, time=90, entries=entries)


@ app.route('/hero/<hero_name>', methods=['POST', 'GET'])
def redirect_page(hero_name):
    if request.method == 'POST':
        text = request.form.get('t')
        print('id test', get_id(text))
        if get_id(text) >= 0:
            print('sdfg')
            return redirect('/hero/'+text)
        else:
            print('invalid hero')
            return render_template('hero.html.jinja')


def do_everything(hero_name):
    output = []
    # request_shit(hero_name, output)
    get_item_name(50)
    start = time.time()
    asyncio.run(main(get_urls(3), hero_name))
    delete_output()
    end = time.time()
    print("Took {} seconds to pull {} websites.".format(end - start, 5))


def is_num(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def request_shit(hero_name, output):
    hero_name = hero_name.title()
    hero_name = hero_name.replace(' ', '%20')
    url = 'https://www.dota2protracker.com/hero/'+hero_name
    req = requests.get(url)
    print(req.status_code)
    text = req.text
    selector = Selector(text=text)
    table = selector.xpath('//*[@class="display compact"]//tbody//tr')
    for row in table:
        match_id = row.css('a::attr(href)').re(r".*opendota.*")[0]
        mmr = row.xpath('td')[4].css('::text').extract()[0]
        print(match_id, mmr)
        if match_id:
            o = [{'id': match_id}, {'mmr': mmr}]
            output.append(o)
    with open('test.json', 'w') as outfile:
        json.dump(output, outfile)


if __name__ == '__main__':
    app.run(debug=True)
