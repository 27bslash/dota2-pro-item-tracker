import scrapy
import os
import re
import requests
import json
import ast
from scrapy.crawler import CrawlerProcess


class matchIdSpider(scrapy.Spider):
    name = 'match_ids'
    start_urls = ['http://www.dota2protracker.com/hero/Jakiro']

    os.remove('posts.json')

    def parse(self, response):
        table = response.xpath('//*[@class="display compact"]//tbody//tr')
        rows = table.xpath('//tr')
        for row in table:
            match_id = row.css('a::attr(href)').re(r".*opendota.*")
            mmr = row.xpath('td')[4].css('::text').extract()
            role = row.xpath('td')[6].extract()
            lane = row.xpath('td')[5].extract()
            lane.replace(' ', '7')
            if match_id:
                yield {
                    'id': match_id,
                    'mmr': mmr,
                    'lane': lane,
                    'role': role,
                    'duration': row.xpath('td')[7].css('::text').extract()
                }


output = []


def convertToDict(a):
    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct


def get():
    urls = []
    with open("posts.json") as json_file:
        data = json.load(json_file)
        for i in data:
            m_id = i['id'][0]
            m_id = re.sub(r"www", 'api', m_id)
            m_id = re.sub(r"/matches/", '/api/matches/', m_id)
            urls.append(m_id)
            print(m_id)
            outfile = open('test-out.json', 'w')
            json.dump(data, outfile)
    for i in range(10):
        x = requests.get(urls[i])
        # data = x.json()['players'][0]['purchase_log']
        print(x.status_code == 200)
        with open('opendota_output.json', 'w') as outfile:
            if x.status_code == 200:
                output.append({'id': x.json()['match_id']})
                for i in range(10):
                    print(i)
                    purchase_log = x.json()['players'][i]['purchase_log']
                    # purchase_log
                    if x.json()['players'][i]['hero_id'] == 64:
                        name = x.json()['players'][i]['hero_id']
                        output.append({'hero': name})
                        output.append({'items': purchase_log})
                json.dump(output, outfile)

#  print('erfgljhsdfgsdfgsdf',x.json()['players'][0]['item_0'])


process = CrawlerProcess(settings={
    "FEEDS": {
        "posts.json": {"format": "json"}
    }
})
process.crawl(matchIdSpider)
process.start()

get()
