import re
import json
import asyncio
import aiohttp
import datetime


# def get_hero_name(name):
#     global hero_name
#     hero_name = name
#     print(hero_name)


output = []


async def async_get(url, hero_name):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                resp = await response.json()
                print("Successfully got url {}.".format(url))
                with open('opendota_output.json', 'w') as outfile:
                    output.append({'id': resp['match_id']})
                    for i in range(10):
                        purchase_log = resp['players'][i]['purchase_log']
                        for item in purchase_log:
                            if item['time'] > 0:
                                item['time'] = str(datetime.timedelta(
                                    seconds=item['time']))
                            else:
                                item['time'] = '0'
                        hero_id = resp['players'][i]['hero_id']
                        if hero_id == get_id(hero_name):
                            output.append({'hero': hero_name})
                            output.append({'items': purchase_log})
                    json.dump(output, outfile)
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def main(urls, hero_name):
    ret = await asyncio.gather(*[async_get(url, hero_name) for url in urls])


def delete_output():
    global output
    output = []


def get_urls(amount):
    urls = []
    with open("test.json") as json_file:
        data = json.load(json_file)
        for i in range(len(data)):
            try:
                m_id = data[i][0]['id']
                m_id = re.sub(r"www", 'api', m_id)
                m_id = re.sub(r"/matches/", '/api/matches/', m_id)
                urls.append(m_id)
                urls.reverse()
                print('urls', urls)
            except Exception as e:
                print(e, e.__class__)
        return urls


def get_id(name):
    with open('hero_ids.json') as json_file:
        data = json.load(json_file)
        for i in range(len(data['heroes'])):
            name = name.lower()
            if name in data['heroes'][i]['name']:
                print('name: ', name)
                return data['heroes'][i]['id']
