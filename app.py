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
        if is_num(get_id(text)):
            return redirect('/hero/'+text)


@app.route('/hero/<hero_name>')
def show_items(hero_name):
    do_everything(hero_name)
    return render_template('hero.html')


@app.route('/hero/<hero_name>', methods=['POST', 'GET'])
def redirect_page(hero_name):
    if request.method == 'POST':
        text = request.form.get('t')
        print('id test', get_id(text))
        if get_id(text):
            return redirect('/hero/'+text)


def do_everything(hero_name):
    output = []
    request_shit(hero_name, output)
    start = time.time()
    asyncio.run(main(get_urls(3),hero_name))
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
    url = 'https://www.dota2protracker.com/hero/'+hero_name
    text = requests.get(url).text
    selector = Selector(text=text)
    table = selector.xpath('//*[@class="display compact"]//tbody//tr')
    for row in table:
        match_id = row.css('a::attr(href)').re(r".*opendota.*")[0]
        print(match_id)
        mmr = row.xpath('td')[4].css('::text').extract()[0]
        if match_id:
            o = [{'id': match_id}, {'mmr': mmr}]
            output.append(o)
    with open('test.json', 'w') as outfile:
        json.dump(output, outfile)


if __name__ == '__main__':
    app.run(debug=True)
