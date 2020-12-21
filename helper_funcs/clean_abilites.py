import json
# arr = []
# with open('clean_talents.json', 'r') as first:
#     fData = json.load(first)
#     with open('a.json', 'r') as second:
#         sData = json.load(second)
#         fin = {**fData, **sData}
#         with open('clean_skills.json', 'w') as outfile:
#             json.dump(fin, outfile, indent=4)

# with open('ability_ids.json', 'r') as f:
#     every = json.load(f)
#     with open('clean_skills.json', 'r') as f:
#         some = json.load(f)
#         for key in every:
#             if key not in some:
#                 arr.append({key: every[key]})
#     with open('missing_skills.json', 'w') as outfile:
#         json.dump(arr, outfile, indent=4)


def opendota_abilities():
    arr = []
    d = {}
    with open('json_files/mega-abilities.json', 'r') as f:
        data = json.load(f)
        for key in data:
            # print(key)
            try:
                # print(data[key]['language']['displayName'])
                arr.append({data[key]['name']: data[key]
                            ['language']['displayName']})
                d.update({data[key]['name']: data[key]
                          ['language']['displayName']})
            except Exception as e:
                print(e, e.__class__)
    print(arr)
    with open('json_files/final.json', 'w') as output:
        json.dump(arr, output, indent=4)

# stratz version


def abilities_stratz():
    arr = []
    d = {}
    with open('json_files/stratz_abilities.json', 'r') as f:
        data = json.load(f)
        for key in data:
            # print(key)
            try:
                # print(data[key]['language']['displayName'])
                arr.append({data[key]['name']: data[key]
                            ['language']['displayName']})
                d[data[key]['name']] = data[key]['language']['displayName']
            except Exception as e:
                print(e, e.__class__)
    with open('json_files/stratz.json', 'w') as output:
        json.dump(d, output, indent=4)


def get_ordred_talents():
    output = []
    with open('json_files/stratz_abilities.json', 'r') as f:
        data = json.load(f)
        for key in data:
            try:
                if data[key]['language']['gameVersionId'] == 135 and data[key]['uri'] == 'jakiro' and 'special' in data[key]['name']:
                    output.append(data[key]['language']['displayName'])
            except Exception as e:
                pass
                # print(e)
    print(output)


if __name__ == '__main__':
    get_ordred_talents()
