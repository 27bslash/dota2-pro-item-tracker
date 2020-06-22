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

arr = []
with open('mega-abilities.json', 'r') as f:
    data = json.load(f)
    for key in data:
        try:
            print(data[key]['dname'])
            arr.append({key: data[key]['dname']})
        except Exception as e:
            print(e, e.__class__)
print(arr)
with open('final.json', 'w') as output:
    json.dump(arr, output, indent=4)
