import random
import os


def hand_out(players):
    free_cards = [i for i in range(236)]
    sets = {}
    for player in players:
        sets[str(player)] = list()
        for i in range(5):
            card = random.choice(free_cards)
            sets[str(player)].append(card)
            free_cards.remove(card)
    return free_cards, sets


def upload_photo(number):
    path = os.getcwd() + '/Cards'
    name = path + '/' + str(number).rjust(4, '0') + '.jpg'
    file = open(name, mode='rb')
    return file


def send_sets(game, update, context):
    for player in game['players']:
        for im in game['players sets'][str(player)]:
            context.bot.send_photo(chat_id=player,
                                   photo=upload_photo(im),
                                   caption=str(im),
                                   disable_notification=True)
        context.bot.send_message(chat_id=player,
                                 text='These are your cards. Only you could see them. To "show" other player your card,'
                                      ' resend me a message with this picture',
                                 disable_notification=True)


def send_set(player, game, context):
    if player in game['players'] and game['is started']:
        for im in game['players sets'][str(player)]:
            context.bot.send_photo(chat_id=player,
                                   photo=upload_photo(im),
                                   caption=str(im),
                                   disable_notification=True)


def send_card_in_group(card_number, group_id, context):
    card = upload_photo(card_number)
    context.bot.send_photo(chat_id=group_id,
                           photo=card,
                           caption=str(card_number),
                           disable_notification=False)


def give_cards(game, context):
    for player in game['players']:
        while len(game['players sets'][str(player)]) < 5:
            if not game['free cards']:
                context.bot.send_message(chat_id=game['chat_id'],
                                         text='There are no cards any more. We have reloaded the pile so now it has '
                                              'all the cards from discard pile in random order. \nBut if you want to,'
                                              'you can finish the game by running /end_game (can be run only by admin)')
                game['free cards'] = reload_pile(game)
            card = random.choice(game['free cards'])
            game['players sets'][str(player)].append(card)
            game['free cards'].remove(card)
    return game


def reload_pile(game):
    pile = [i for i in range(236)]
    for player in game['players']:
        for i in game['players sets'][str(player)]:
            pile.remove(i)
    return pile


def get_one_card(game, context):
    card_number = random.choice(game['free cards'])
    game['free cards'].remove(card_number)
    context.bot.send_photo(chat_id=game['group_id'],
                           photo=upload_photo(card_number),
                           caption=str(card_number),
                           disable_notification=False)
    for i in game['players']:
        print(i)
        context.bot.send_photo(chat_id=i,
                               photo=upload_photo(card_number),
                               caption='карточка от ведущего',
                               disable_notification=False)

    game['last card'] = card_number
    print(card_number)
    return game


def send_last_card(game, context):
    if 'last card' in game.keys():
        context.bot.send_photo(chat_id=game['group_id'],
                               photo=upload_photo(game['last card']),
                               caption=str(game['last card']),
                               disable_notification=False)

    return game
