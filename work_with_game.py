import json
import random
from datetime import datetime

FILE_WITH_GAMES = 'games.json'


def get_game_by_admin_id(admin_id):
    games = json.load(open(FILE_WITH_GAMES, mode='r', encoding='utf8'))['games']
    token = 0
    for k in games.keys():
        if games[k]['admin_id'] == admin_id:
            token = k
    if token:
        return games[token]
    return


def get_game_by_group_id(group_id):
    games = json.load(open(FILE_WITH_GAMES, mode='r', encoding='utf8'))['games']
    token = 0
    for k in games.keys():
        if games[k]['group_id'] == group_id:
            token = k
    if token:
        return games[token]
    return


def generate_token():
    tokens_in_use = json.load(open(FILE_WITH_GAMES, mode='r', encoding='utf8'))['tokens in use']
    token = random.randint(100000, 999999)
    while token in tokens_in_use:
        token = random.randint(100000, 999999)
    return token


def check_token(token):
    tokens_in_use = json.load(open(FILE_WITH_GAMES, mode='r', encoding='utf8'))['tokens in use']
    return token in tokens_in_use


def delete_game(token):
    data = json.load(open(FILE_WITH_GAMES, mode='r', encoding='utf8'))
    data['tokens in use'].remove(data['tokens in use'].index(token))
    data['game'] = None
    file = open(FILE_WITH_GAMES, mode='w', encoding='utf8')
    json.dump(data, file)
    file.close()


def get_game_by_token(token):
    return json.load(open(FILE_WITH_GAMES, mode='r', encoding='utf8'))['games'][str(token)]


def new_game(token, user_id):
    data = json.load(open(FILE_WITH_GAMES, mode='r', encoding='utf8'))
    data['games'][str(token)] = {'token': token, 'admin_id': user_id, 'group_id': 0, "players": [user_id],
                                 "is started": False, 'creation_time': str(datetime.now())}
    data['tokens in use'].append(token)
    file = open(FILE_WITH_GAMES, mode='w', encoding='utf8')
    json.dump(data, file)
    file.close()


def update_group(token, group_id):
    data = json.dumps(open(FILE_WITH_GAMES, mode='r', encoding='utf8').read())
    data['games'][str(token)]['group_id'] = group_id


def update_game(game):
    data = json.load(open(FILE_WITH_GAMES, mode='r', encoding='utf8'))
    data['games'][str(game['token'])] = game
    if int(game['token']) not in data['tokens in use']:
        data['tokens in use'].append(int(game['token']))
    file = open(FILE_WITH_GAMES, mode='w', encoding='utf8')
    json.dump(data, file)
    file.close()


def get_game_by_user(user_id):
    games = json.load(open(FILE_WITH_GAMES, mode='r', encoding='utf8'))['games']
    token = 0
    for k in games.keys():
        if user_id in games[k]['players']:
            token = k
    if token:
        return games[token]
    return
