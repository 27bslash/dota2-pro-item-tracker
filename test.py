import json


def test():
    with open('opendota_output.json', 'r') as f:
        data = json.load(f)
        for item in data[0]['items']:
            print(item['key'], item['time'])


test()
