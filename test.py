import json
from helper_funcs.helper_functions import *
import time


def test():
    with open('opendota_output.json', 'r') as f:
        data = json.load(f)
        for item in data[0]['items']:
            print(item['key'], item['time'])


# test()

def flen():
    with open('json_files/hero_output/io.json', 'r') as f:
        data = json.load(f)
        print(len(data))


flen()


def get_urls_from():
    names = []
    urls = []
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i in data['heroes']:
            names.append(i['name'])
    for name in names:
        name = pro_name(name)
        with open(f"json_files/hero_urls/{name}.json") as f:
            data = json.load(f)
            data = sorted(data, key=lambda i: i['mmr'], reverse=True)
            for i in range(6):
                try:
                    m_id = data[i]['id']
                    m_id = re.sub(r"www", 'api', m_id)
                    m_id = re.sub(r"/matches/", '/api/matches/', m_id)
                    urls.append(m_id)
                    urls.reverse()
                except Exception as e:
                    print(e, e.__class__)
            print(name, urls)
            urls = []


def opendota_call():
    names = []
    out = []
    print('input')
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i in data['heroes']:
            names.append(i['name'])
        for i, e in enumerate(names):
            print('first', i)
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i, e in enumerate(names):
            # delete_output()
            print('second')
    print('end')


# opendota_call()
def opendota_call():
    names = []
    out = []
    print('input')
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for i in data['heroes']:
            names.append(i['name'])
        # for name in names:
        #     pass
            # asyncio.run(pro_request(name, out, 100))
    with open('json_files/hero_ids.json', 'r') as f:
        data = json.load(f)
        for name in names:
            # asyncio.run(main(get_urls(20, name, name)))
            delete_output()
            # time.sleep(60)
            print('second')
    time.sleep(3)
    print('end')