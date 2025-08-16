import os
import psutil
from steam.client import SteamClient
from dota2.client import Dota2Client
import logging
import time
from pymongo import MongoClient
import json
import sys
import traceback

from logs.log_config import pro_item_logger
client = SteamClient()
dota = Dota2Client(client)


db = cluster['pro-item-tracker']
hero_output = db['heroes']
account_ids_db = db['account_ids']
urlmodel = db['urls']
non_pro = db['non-pro']
hero_ids = db['hero_list']
modified_docs = 0

pro_accounts = list(account_ids_db.find())
pro_account_ids: list[str] = [doc['account_id'] for doc in pro_accounts]


@client.on('logged_on')
def start_dota():
    dota.launch()


@client.on('disconnected')
def exit():
    print('exit1')
    sys.exit()


@dota.on('ready')
def request_games():
    print('request')
    try:
        jobid = dota.request_top_source_tv_games(start_game=90)
        resp = dota.wait_event(jobid, timeout=5)
        if not resp:
            print('no resp timeout')
            return

    except Exception:
        print(traceback.format_exc())
        return


target_account_ids = [
    # me
    89457522,
    # alex
    53660917,
    # matt
    86292608,
    # jack
    80114075,
    # jake
    76409646,
]


@dota.on('top_source_tv_games')
def insert_games(matches) -> None:
    strt = time.perf_counter()

    for game in matches.game_list:
        if len(game.players) != 10:
            print(f'player length {len(game.players)}')
            continue
        override = False
        account_ids_in_game: list[int] = [player.account_id for player in game.players]
        manual_acc_id_override = [
            x for x in account_ids_in_game if x in target_account_ids
        ]
        pro_game = (
            game.league_id != 0
            and len(
                [
                    acc_id
                    for acc_id in account_ids_in_game
                    if str(acc_id) in pro_account_ids
                ]
            )
            >= 1
        )

        pro_game = handle_pro_game(game, account_ids_in_game)
        if (game.average_mmr < 7500 and len(manual_acc_id_override) == 0) or pro_game:
            continue
        result = db['urls'].update_one(
            {'id': int(game.match_id)},
            {
                '$set': {
                    'id': int(game.match_id),
                    'time_stamp': time.time(),
                    'mmr': str(game.average_mmr),
                    'heroes': [player.hero_id for player in game.players],
                }
            },
            upsert=True,
        )
        if result.upserted_id:
            pro_item_logger.warning(
                f"insert normie game {game.match_id} {game.average_mmr}"
            )

    client.logout()


def handle_pro_game(game, account_ids_in_game):
    pro_game = (
        game.league_id != 0
        and len(
            [acc_id for acc_id in account_ids_in_game if str(acc_id) in pro_account_ids]
        )
        >= 1
    )
    if not pro_game:
        return False
    for player in game.players:
        url_check = db['urls'].find_one(
            {'id': int(game.match_id), 'hero': player.hero_id}
        )
        account_check = account_ids_db.find_one({'account_id': str(player.account_id)})
        if url_check is None:
            db['urls'].insert_one(
                {
                    'pro': True,
                    'time_stamp': time.time(),
                    'id': int(game.match_id),
                    'account_id': int(player.account_id),
                    'hero': player.hero_id,
                    'name': (account_check['name'] if account_check else 'unknown'),
                    'mmr': str(50000),
                }
            )
            pro_item_logger.warning(
                f"insert pro game {game.match_id} {game.average_mmr} {player.hero_id} {account_check['name'] if account_check else 'unknown'}"
            )
    return True


try:
    client.cli_login(username='27bslash', password='iucSGq#kJYCtHN3')
    client.run_forever()
except Exception:
    print(traceback.format_exc())

current_pid = os.getpid()
script_name = "source_games.py"

for proc in psutil.process_iter(['pid', 'cmdline']):
    try:
        if proc.info['pid'] != current_pid and script_name in " ".join(
            proc.info['cmdline']
        ):
            proc.terminate()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue
# client.cli_login(username='source_py_bot',
#                  password='!4#18fAS36jO&DugerhRw')
# client.run_forever()
