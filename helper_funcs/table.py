import timeago
import datetime
from .database.collection import hero_output, item_ids, all_items, hero_list
from .items import Items
from .switcher import switcher
import time
item_methods = Items()


def generate_table(func_name, query, template, request):
    # print(request.args)
    total_time = time.perf_counter()
    start = time.perf_counter()
    query = switcher(query)
    key = 'name' if func_name == 'player' else 'hero'
    img_cache = 'https://ailhumfakp.cloudimg.io/v7/'
    columns = {'0': 'win', '1': None, '2': 'unix_time', '3': 'name', '4': None, '5': 'role', '6': 'lvl', '7': 'kills', '8': 'deaths', '9': 'assists',
               '10': 'last_hits', '11': 'gold', '12': 'gpm', '13': 'xpm', '14': 'hero_damage', '15': 'tower_damage', '16': 'duration', '17': 'mmr'}
    sort_direction = -1 if request.args['order[0][dir]'] == 'desc' else 1
    column = columns[request.args['order[0][column]']]
    searchable = request.args['search[value]']
    start = time.perf_counter()
    records_to_skip = int(request.args['start'])
    length = int(request.args['length'])

    total_entries = 0
    aggregate = ''
    role = None
    search_query = None

    if 'start' in template:
        if column == 'gold':
            column = 'lane_efficiency'
        elif column == 'kills':
            column = 'kills_ten'
        elif column == 'deaths':
            column = 'deaths_ten'
        elif column == 'lvl':
            column = 'lvl_at_ten'
        elif column == 'last_hits':
            column = 'last_hits_ten'
        elif column == 'xpm':
            column = 'xpm_ten'
        elif column == 'gpm':
            column = 'gpm_ten'
    if 'role' in request.args:
        role = request.args.get('role').replace('%20', ' ').title()
    if len(searchable) > 0 and func_name == 'player':
        search_query = atlas_search_query('name', query, searchable, role, column=column,
                                          sort_direction=sort_direction, records_to_skip=records_to_skip, limit=length)
        total_entries_query = atlas_search_query(
            'name', query, searchable, role, count=True)
    elif len(searchable) > 0 and func_name == 'hero':
        search_query = atlas_search_query('hero', query, searchable, role, column=column,
                                          sort_direction=sort_direction, records_to_skip=records_to_skip, limit=length)
        total_entries_query = atlas_search_query(
            'hero', query, searchable, role, count=True)
    else:
        if role:
            aggregate = {key: query, 'role': role}
        else:
            regex = fr"{query}?\b"
            aggregate = {key: {"$regex": regex}}
    print('if block: ', time.perf_counter()-start)
    start = time.perf_counter()
    if search_query:
        data = hero_output.aggregate(search_query)
        agg_result = list(hero_output.aggregate(total_entries_query))
        if agg_result:
            total_entries = list(agg_result)[0]['total_entries']
    else:
        data = hero_output.find(
            aggregate).sort(column, sort_direction).limit(length).skip(records_to_skip)
        total_entries = hero_output.count_documents(aggregate)

    print('find query: ', time.perf_counter()-start)
    match_data = list(data)
    print('cursor conversion:', time.perf_counter()-start)
    start = time.perf_counter()
    print('count documents: ', time.perf_counter() - start, total_entries)
    result = {"draw": request.args['draw'],
              "recordsTotal": total_entries, "recordsFiltered": total_entries, "data": []}
    if total_entries == 0:
        return result
    start = time.perf_counter()
    res = append_table_string(func_name, match_data, template, result)
    print('tabel tr', time.perf_counter()-total_time)
    return res


def append_table_string(func_name, match_data, template, result):
    img_host = 'https://ailhumfakp.cloudimg.io/v7/https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/'
    srt = time.perf_counter()
    for match in match_data:
        row_string = []
        html_string = f"<a href=https://www.opendota.com/matches/{match['id']}>"
        html_string += append_item_string(template, img_host, match)
        # ability
        html_string += append_ability_string(match, img_host)
        html_string += append_draft_string(match)
        role_file_path = f"/static/icons/{match['role']}.png"
        role_img = f"<img src='{role_file_path}'"
        large = ''
        if 'start' in template:
            large = ' large'
        if match['win'] == 0:
            row_string.append(f"<div class='loss-cell{large}'></div>")
        else:
            row_string.append(f"<div class='win-cell{large}'></div>")
        row_string.append(html_string)
        row_string.append(timeago.format(
            match['unix_time'], datetime.datetime.now()))
        if func_name != 'player':
            row_string.append(
                f"<a href=\"/player/{match['name']}\"><p class='stats'>{match['name']}</p></a>")
        else:
            row_string.append(
                f"<a href='/hero/{switcher(match['hero'])}'><i class='d2mh {match['hero']}'></i></a>")
        row_string.append(f"<i class='fas fa-copy' id='{match['id']}'></i>")
        row_string.append(
            f"<a href=\'?role={match['role']}\'><img src='{role_file_path}'/></a>")
        row_string += stats(match, template)
        result['data'].append(row_string)
    return result


def append_item_string(template, img_host, match):
    html_string = "<div class='purchases'>"
    strt = time.perf_counter()
    if 'start' in template:
        html_string += item_text_str(match['starting_items'],
                                     img_host, 'starter', match['hero'])
        html_string += "</div>"
        html_string += "<div class='intermediate_items'>"
        for item in match['items']:
            intermediate_items = ['bottle', 'vanguard', 'hood_of_defiance', 'orb_of_corrosion',
                                  'soul_ring', 'buckler', 'urn', 'fluffy_hat', 'wind_lace', 'infused_raindrop', 'crown', 'bracer', 'null_talisman', 'wraith_band',
                                  'ring_of_basilius', 'headress', 'magic_wand']
            consumables = ['tango', 'flask', 'ward_observer',
                           'ward_sentry', 'smoke_of_deceit', 'enchanted_mango', 'clarity', 'tpscroll', 'dust']
            item_key = item['key']
            item_id = item_methods.get_item_id(item_key)
            if type(item['time']) is not int or item['time'] > 600:
                break
            if item['key'] not in consumables and item['time'] < 600 and item['time'] > 0:
                image = f"<img class='item-img' src='{img_host}/items/{item['key']}.png' data_id='{item_id}' alt='{item_key}'>"
                overlay = f"<div class='overlay'>{str(datetime.timedelta(seconds=item['time']))}</div>"
                html_string += "<div class='item-cell'>"
                html_string += image
                html_string += overlay
                html_string += "<div class='tooltip' id='item-tooltip'></div>"
                html_string += "</div>"
        html_string += "</div></a>"

    else:
        html_string += item_text_str(match['final_items'],
                                     img_host, None, match['hero'])
        html_string += item_text_str(match['backpack'],
                                     img_host, None, match['hero'])

        if match['item_neutral']:
            item_key = match['item_neutral']
            item_id = item_methods.get_item_id(item_key)
            html_string += "<div class='neutral-cell'>"
            html_string += f"<div class='circle'>"
            html_string += f"<img class='item-img' id='neutral-item' src='{img_host}/items/{item_key}.png' data_id='{item_id}' alt='{item_key}'>"
            html_string += "<div class='tooltip' id='item-tooltip'></div></div></div>"

        if match['aghanims_shard']:
            image = f"<img class='item-img' id='aghanims-shard' src='https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/aghanims_shard_lg.png' data_id='609' data-hero=\"{match['hero']}\" alt='aghanims_shard'>"
            shard_time = match['aghanims_shard'][0]['time']
            overlay = f"<div class='overlay' id='shard-overlay'>{shard_time}</div>"
            html_string += f"<div class='item-cell' id='aghanims-shard-cell'>"
            html_string += image
            html_string += overlay
            html_string += "<div class='tooltip' id='shard-tooltip'></div>"
            html_string += "</div>"

        html_string += "</div></a>"
    # print('item string timeing',time.perf_counter() - strt)
    return html_string


def item_text_str(items, img_host, type, hero):
    html_string = ''
    for item in items:
        overlay = ''
        if type is not 'starter':
            overlay = f"<div class='overlay'>{item['time']}</div>"
            item_id = item['id']
        else:
            item_id = item_methods.get_item_id(item['key'])
        image = f"<img class='item-img' src='{img_host}/items/{item['key']}.png' data_id='{item_id}' alt='{item['key']}'data-hero=\"{hero}\">"
        html_string += "<div class='item-cell'>"
        html_string += image
        html_string += overlay
        if item['key'] == 'ultimate_scepter':
            html_string += "<div class='tooltip' id='scepter-tooltip'></div>"
        else:
            html_string += "<div class='tooltip' id='item-tooltip'></div>"
        html_string += "</div>"
    return html_string


def append_ability_string(match, img_host):
    html_string = f"<div class='abilities' data-hero=\"{match['hero']}\">"
    visited = []
    for ability in match['abilities']:
        talent_wrapper = ''
        html_string += "<div class='ability-img-wrapper'>"
        if ability['type'] == 'talent':
            visited.append(ability)
            key = ability['key']
            talents = f"<div class='talents' data-id =\'{ability['id']}\'  data-name=\"{key}\">"
            for tal in visited:
                talents += talent_img(tal)
            if len(talent_wrapper) == 0:
                talent_wrapper = ''
                talent_wrapper += talents
            html_string += talent_str(ability, talent_wrapper)
        else:
            html_string += ability_str(ability, img_host, 'ability')
    html_string += "</div>"
    return html_string


def ability_str(ability: object, img_host, type):
    ability_img = f"{img_host}/abilities/{ability['img']}.png"
    html_string = ''
    if type == 'talent':
        ability_img = '/static/images/talent_img.png'
    ability_id = ability['id']
    ability_key = ability['key']
    image = f"<img class='table-img' src='{ability_img}' data_id='{ability_id}' data-tooltip='{ability_key}' alt='{ability_key}'>"
    html_string += f"<strong><p style='color:white; text-align:center;'>{ability['level']}</p></strong>"
    html_string += image
    html_string += f"<div class='tooltip' id='{type}-tooltip'></div>"
    html_string += "</div>"
    return html_string


def talent_str(talent, talent_wrapper):
    html_string = ''
    html_string += f"<strong><p style='color:white; text-align:center;'>{talent['level']}</p></strong>"
    html_string += talent_wrapper+'</div>'
    html_string += f"<div class='tooltip' id='talent-tooltip'></div>"
    html_string += "</div>"
    return html_string


def talent_img(talent):
    side = 'r-talent' if talent['slot'] % 2 == 0 else 'l-talent'
    if talent['slot'] < 2:
        level = 10
    elif talent['slot'] < 4:
        level = 15
    elif talent['slot'] < 6:
        level = 20
    else:
        level = 25
    return f"<div class=\"lvl{level} {side}\"></div>"


def append_draft_string(match):
    html_string = "<div class='draft'>"
    html_string += draft_string(match, 'radiant', match['hero'])
    html_string += "</div>"
    html_string += draft_string(match, 'dire', match['hero'])
    html_string += "</div>"
    return html_string


def draft_string(match, side, query):
    html_string = f"<div class='{side}_draft'>"
    try:
        for hero in match[f"{side}_draft"]:
            rep = hero.replace("'", '')
            highlight = ''
            if hero == query:
                highlight = 'icon-highlight'
            html_string += f"<a href='/hero/{rep}'><img src='/static/images/minimap_icons/{hero}.jpg' class='{highlight}'></img></a>"
    except Exception as e:
        print(match, side, query)
    return html_string


def stats(match, template):
    row_string = []
    stat_list = ['lvl', 'kills', 'deaths', 'assists', 'last_hits', 'gold',
                 'gpm', 'xpm', 'hero_damage', 'tower_damage', 'duration', 'mmr']
    for stat in stat_list:
        perc = ''
        id = stat
        if 'start' in template:
            if stat == 'gold':
                stat = 'lane_efficiency'
                perc = '%'
            elif stat == 'kills':
                stat = 'kills_ten'
            elif stat == 'deaths':
                stat = 'deaths_ten'
            elif stat == 'lvl':
                stat = 'lvl_at_ten'
            elif stat == 'last_hits':
                stat = 'last_hits_ten'
            elif stat == 'xpm':
                stat = 'xpm_ten'
            elif stat == 'gpm':
                stat = 'gpm_ten'
        row_string.append(
            f"<p class='stats' data-sort='{match[stat]}' id='{id}'>{match[stat]}{perc}</p>")
    return row_string


def atlas_search_query(key: str, value: str, search: str, role=None, **kwargs) -> dict:
    regex = f"{value}?"
    match_query = {'$match': {key: {"$regex": regex}}}
    if role is not None:
        match_query = {'$match': {key: {"$regex": regex}}, 'role': role}

    result_list = item_switcher(search)
    fields = []
    if result_list:
        fields.append('final_items.key')
        fields.append('item_neutral')
        fields.append('aghanims_shard.key')
        fields.append('backpack.key')
    if key == 'name':
        fields.append('hero')
    else:
        fields.append('name')
    hero_resu = hero_search(search)
    if hero_resu:
        fields.append('radiant_draft')
        fields.append('dire_draft')

    result_list += hero_resu
    result_list.append(search)

              'item_neutral.key', 'aghanims_shard.key', 'backpack.key', 'radiant_draft', 'dire_draft']
    search_query = {'$search': {
        'index': 'default',
        'text': {
            'query': result_list,
            'path': fields
        }
    }}
    count_query = [
        search_query,
        match_query,
        {'$count': 'total_entries'},
    ]
    if 'count' in kwargs:
        return count_query

    query = [
        search_query,
        match_query,
        {"$sort": {
            kwargs['column']: kwargs['sort_direction']
        }},
        {"$skip":
            kwargs['records_to_skip']
         },
        {"$limit":
            kwargs['limit']
         }

    ]

    return query


def hero_search(query):
    if query is None:
        print('none')
        return
    data = hero_list
    ret = []
    switched = [{'name': switcher(i['name']), 'id': i['id']}
                for i in data if switcher(i['name']) != i['name']]
    data += switched
    for term in query.split(','):
        term = term.strip()
        if not term or len(term) < 3:
            continue
        matches = [hero['name']
                   for hero in data if term in hero['name'] or term in switcher(hero['name'])]
        ret += matches
    return ret


def item_switcher(query):
    l = set()
    ret = []
    all_searches = query.split(',')
    for search in all_searches:
        search = search.strip()
        if not search or len(search) <= 1:
            continue
        for item in all_items:
            if search in item['name']:
                l.add(item['id'])
            elif search in item['displayName'].lower():
                l.add(item['id'])
        for _id in l:
            for item in item_ids:
                if _id == item['id']:
                    ret.append(item['name'])
    return ret
