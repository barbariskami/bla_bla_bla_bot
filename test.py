import json

FILE_WITH_GAMES = 'games.json'
tokens_in_use = json.loads(open(FILE_WITH_GAMES, mode='r', encoding='utf8').read())
print(tokens_in_use)