import timeago
import datetime
from .database.collection import db, hero_output
from .items import Items

item_methods = Items()


def generate_table(func_name, query, template, request):
    # print(request.args)
    display_name = query.replace('_', ' ').capitalize()
    key = 'name' if func_name == 'player' else 'hero'
    check_response = hero_output.find_one({key: query})
    match_data = None
    img_cache = 'https://ailhumfakp.cloudimg.io/v7/'
    columns = {'0': 'win', '1': None, '2': 'unix_time', '3': 'name', '4': None, '5': 'role', '6': 'lvl', '7': 'kills', '8': 'deaths', '9': 'assists',
               '10': 'last_hits', '11': 'gold', '12': 'gpm', '13': 'xpm', '14': 'hero_damage', '15': 'tower_damage', '16': 'duration', '17': 'mmr'}
    sort_direction = -1 if request.args['order[0][dir]'] == 'desc' else 1
    column = columns[request.args['order[0][column]']]
    searchable = request.args['search[value]']
    search_value = mongo_search(searchable)
    records_to_skip = int(request.args['start'])
    length = int(request.args['length'])
    total_entries = []
    if 'start' in template and column == 'gold':
        column = 'lane_efficiency'
    if check_response:
        if 'role' in request.args:
            role = request.args.get('role').replace('%20', ' ').title()
            data = hero_output.find(
                {key: query, 'role': role}).sort(column, sort_direction).limit(length).skip(records_to_skip)
            match_data = [match for match in data]
            total_entries = [entry for entry in hero_output.find(
                {key: query, 'role': role})]
        else:
            if len(searchable) > 0 and len(search_value) > 0:
                aggregate = {key: query, 'hero': {"$in": search_value}}
            else:
                aggregate = {key: query}
            data = hero_output.find(
                aggregate).sort(column, sort_direction).limit(length).skip(records_to_skip)
            match_data = [match for match in data]
            total_entries = [
                entry for entry in hero_output.find({key: query})]
    result = {"draw": request.args['draw'],
              "recordsTotal": len(total_entries), "recordsFiltered": len(total_entries), "data": []}
    if len(total_entries) == 0:
        return result
    img_host = 'https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/'
    for match in match_data:
        row_string = []
        html_string = f"<a href=https://www.opendota.com/matches/{match['id']}>"
        html_string += "<div class='purchases'>"
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
        html_string += f"<div class='abilities' data-hero=\"{match['hero']}\">"

        for ability in match['abilities']:
            html_string += "<div class='ability-img-wrapper'>"
            if ability['type'] == 'talent':
                html_string += ability_str(ability, img_host, 'talent')
            else:
                html_string += ability_str(ability, img_host, 'ability')

        html_string += "</div>"

        html_string += "<div class='draft'>"
        html_string += draft_string(match, 'radiant', match['hero'])
        html_string += "</div>"
        html_string += draft_string(match, 'dire', match['hero'])
        html_string += "</div>"

        role_file_path = f"/static/icons/{match['role']}.png"
        role_img = f"<img src='{role_file_path}'"
        if match['win'] == 0:
            row_string.append("<div id='loss-cell'></div>")
        else:
            row_string.append("<div id='win-cell'></div>")
        row_string.append(html_string)
        row_string.append(timeago.format(
            match['unix_time'], datetime.datetime.now()))
        if func_name != 'player_get':
            row_string.append(
                f"<a href=\"/player/{match['name']}\"><p class='stats'>{match['name']}</p></a>")
        else:
            row_string.append(
                f"<a href='/hero/{match['hero']}'><i class='d2mh {match['hero']}'></i></a>")
        row_string.append(f"<i class='fas fa-copy' id='{match['id']}'></i>")
        row_string.append(
            f"<a href=\'?role={match['role']}\'><img src='{role_file_path}'/></a>")
        row_string += stats(match, template)
        result['data'].append(row_string)
    return result


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


def ability_str(ability: object, img_host, type):
    ability_img = f"{img_host}/abilities/{ability['img']}.png"
    if type == 'talent':
        ability_img = '/static/talent_img.png'
    ability_id = ability['id']
    ability_key = ability['key']
    html_string = ''
    image = f"<img class='table-img' src='{ability_img}' data_id='{ability_id}' data-tooltip='{ability_key}' alt='{ability_key}'>"
    html_string += f"<strong><p style='color:white; text-align:center;'>{ability['level']}</p></strong>"
    html_string += image
    html_string += f"<div class='tooltip' id='{type}-tooltip'></div>"
    html_string += "</div>"
    return html_string


def draft_string(match, side, query):
    html_string = f"<div class='{side}_draft'>"
    for hero in match[f"{side}_draft"]:
        rep = hero.replace("'", '')
        highlight = ''
        if hero == query:
            highlight = 'icon-highlight'
        html_string += f"<a href='/hero/{hero}'><i class='d2mh {rep} {highlight}'></i></a>"
    return html_string


def stats(match, template):
    row_string = []
    stat_list = ['lvl', 'kills', 'deaths', 'assists', 'last_hits', 'gold',
                 'gpm', 'xpm', 'hero_damage', 'tower_damage', 'duration', 'mmr']
    perc = ''
    for stat in stat_list:
        if 'start' in template and stat == 'gold':
            stat = 'lane_efficiency'
            perc = '%'
        row_string.append(
            f"<p class='stats' data-sort='{match[stat]}' id='{stat}'>{match[stat]}{perc}</p>")
    return row_string


def mongo_search(query):
    data = db['hero_list'].find_one({})
    matches = [hero['name']
               for hero in data['heroes'] if query in hero['name']]
    return matches
