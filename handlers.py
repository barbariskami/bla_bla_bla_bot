from cards import hand_out, send_sets, send_card_in_group, send_set, give_cards, get_one_card, send_last_card
import traceback
from work_with_game import generate_token, new_game, check_token, get_game_by_token, get_game_by_group_id, update_game
from work_with_game import get_game_by_user, delete_game, get_game_by_admin_id
import random
from telegram import ParseMode
from exceptions import WrongChatException
from enums import ChatTypes

""" create_game relates to a homonymous command of a bot 
This function creates a game object using  new_game func and also checks if a user has already created a game and 
hasn't finished it. Also it checks the situation """


def create_game(update, context):
    try:
        if update.effective_chat.id < 0:
            raise WrongChatException(ChatTypes.Group)
        if 'game is running' in context.user_data.keys() and context.user_data['game is running']:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='You haven\'t finished the previous game. '
                                          'To do this use the command /end_game')
            return
        token = generate_token()
        new_game(token, update.effective_user.id)
        context.bot.send_message(chat_id=update.effective_user.id, text='The game is created: ' + str(token))
        context.user_data['game is running'] = True
    except WrongChatException as ex:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=ex.message)
    except Exception:
        traceback.print_exc()


def end_game(update, context):
    try:
        if update.effective_chat.id < 0:
            game = get_game_by_group_id(update.effective_chat.id)
            if not game:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='There is no game started in this group')
                return
            elif update.effective_user.id != game['admin_id']:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='You are not an admin. You are not aloud to finish the game.')
                return
        if update.effective_chat.id > 0:
            game = get_game_by_admin_id(update.effective_chat.id)
            if not game:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='You haven\'t started any game as an admin. There is nothing to '
                                              'finish :) Use the command /create_game to start playing')
                return
        context.user_data['game is running'] = False
        game = get_game_by_admin_id(update.effective_chat.id)
        delete_game(game['token'])
        context.bot.send_message(chat_id=update.effective_user.id, text='The game is now finished.')
        return
    except Exception:
        traceback.print_exc()


def attach_group(update, context):
    try:
        if update.effective_chat.id > 0:
            raise WrongChatException(ChatTypes.Private)

        if not context.user_data['game is running']:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='You haven\'t started the game (this command should be sent by that person, '
                                          'who has created the token)')
            return

        if get_game_by_group_id(update.effective_chat.id):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='There is already a game started in this chat. It could be ended by '
                                          'it\'s admin (that one, who has created it) or it will be ended automatically'
                                          '24 hours after creating')
            return

        if not context.args:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='You should write a game token after the function, '
                                          'like "/attach_group 000000"')
            return

        token = context.args[0]

        if (not token.isdigit()) or len(token) != 6:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='The token is a 6 number integer, that was sent to your '
                                          'fprivate chat with me.')
            return

        token = int(token)

        if not check_token(token):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Your token is invalid, check if you haven\'t finished the game.')
            return

        game = get_game_by_token(token)

        if update.effective_user.id != game['admin_id']:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='You are not an admin of this game. Please, ask the admin to '
                                          'register the game')
            return

        game['group_id'] = update.effective_chat.id
        update_game(game)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='The group is successfully attached! '
                                      'Now all the players, who want to play, should send a command '
                                      '/enter_game here (in this group). The admin is already in the game. '
                                      '\nThen go to a private chat with me @blablabla_with_friends_bot and press start '
                                      'or make sure, that our dialog has already been started. If not, you won\'t be able '
                                      'to get cards.'
                                      '\nAfter everybody have entered, rut the command /begin and the game will start \n'
                                      '(ATTENTION: after beginning no other players won\'t be able to join)')
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='If you don\'t want to '
                                      'play any more, run the command /quit_game')
    except WrongChatException as ex:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=ex.message)
    except Exception:
        traceback.print_exc()


def enter_game(update, context):
    try:
        if update.effective_chat.id > 0:
            raise WrongChatException(ChatTypes.Private)

        game = get_game_by_user(update.effective_user.id)
        if game:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='User {} already takes part in a game. Quit that game to enter '
                                          'this one.'.format(update.effective_user.username))
            return

        game = get_game_by_group_id(update.effective_chat.id)
        if not game:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='There is no games attached to this chat. Make sure that you use the right '
                                          'chat and that the admin of a game has run the command /attach_group')
            return

        if game['is started']:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='The game has already started, unfortunately you cannot join it now')
            return

        if len(game['players']) == 8:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='I\'m sorry, there are already too many players, maybe next time')
            return

        if update.effective_user.id in game['players']:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='The user {} is already in the game'.format(update.effective_user.username))
            return

        print(update.effective_user.id)
        game['players'].append(update.effective_user.id)
        if game['is started']:
            new_set = list()
            for i in range(5):
                card = random.choice(game['free cards'])
                new_set.append(card)
                game['free cards'].remove(card)
            game['players sets'][str(update.effective_user.id)] = new_set

        update_game(game)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='The user {} has successfully entered the game'.format(
                                     update.effective_user.username))
    except WrongChatException as ex:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=ex.message)
    except Exception:
        traceback.print_exc()


def quit_game(update, context):
    if update.effective_chat.id > 0:
        raise WrongChatException(ChatTypes.Private)

    game = get_game_by_group_id(update.effective_chat.id)
    if game:
        if update.effective_user.id in game['players']:
            game['players'].remove(update.effective_user.id)
            update_game(game)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='The user {} has successfully quited the game'.format(
                                         update.effective_user.username))
            return


def begin(update, context):
    try:
        if update.effective_chat.id > 0:
            raise WrongChatException(ChatTypes.Private)

        game = get_game_by_group_id(update.effective_chat.id)

        if not game or game['is started']:
            return

        if len(game['players']) < 3:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='There are not enough players in the game. There should be at least 3 people')
            return

        game['is started'] = True
        game['free cards'], game['players sets'] = hand_out(game['players'])
        print(game['players sets'])
        update_game(game)

        send_sets(game, update, context)

        update_game(game)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='The game has STARTED!!!')
        return
    except WrongChatException as ex:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=ex.message)
    except Exception:
        traceback.print_exc()


def card_catcher(update, context):
    try:
        if update.effective_chat.id < 0:
            return

        if (not update.message.photo) or not update.message.caption:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='This is not a card. Please, send me only cards')
            return

        game = get_game_by_user(update.effective_user.id)
        card_number = update.message.caption
        try:
            card_number = int(card_number)
        except ValueError:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='You have forwarded me something that is not a card. Don\'t do this please. '
                                          'You make me sad :(')
            return

        if not game:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='You don\'t take part in any game. Join the game in a group with other '
                                          'players or create your own game using command /create_game (in this case'
                                          'you still need friends to play with)')
            return

        if card_number not in game['players sets'][str(update.effective_chat.id)]:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='There is no such a card in your hand now. May be you cave already used it '
                                          '(or even it isn\'t a card :D)\n'
                                          'To get your current set run a command /current_set or push a button with '
                                          'this command (if available)')
            return

        send_card_in_group(card_number, game['group_id'], context)

        game['players sets'][str(update.effective_user.id)].remove(card_number)
        update_game(game)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='The card is now in a group. Run /current_set to see cards you have now')
    except Exception:
        traceback.print_exc()


def current_set(update, context):
    try:
        if update.effective_chat.id < 0:
            raise WrongChatException(ChatTypes.Group)

        game = get_game_by_user(update.effective_user.id)
        if not game:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='You don\'t take part in any game. Join the game in a group with other '
                                          'players or create your own game using command /create_game (in this case'
                                          'you still need friends to play with)')
            return

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='After this message are cards you have right now\n'
                                      '⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️️')
        send_set(update.effective_user.id, game, context)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Don\'t worry if you have less then 5 cards. You will get missing after the '
                                      'round is finished')
    except WrongChatException as ex:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=ex.message)
    except Exception:
        traceback.print_exc()


def give_more_cards(update, context):
    try:
        if update.effective_chat.id > 0:
            raise WrongChatException(ChatTypes.Private)

        game = get_game_by_group_id(update.effective_chat.id)

        if not game:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='There is no games attached to this chat. Make sure that you use the right '
                                          'chat and that the admin of a game has run the command /attach_group')
            return

        game = give_cards(game, context)
        update_game(game)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Now everyone has 5 cards again')
        for player in game['players']:
            context.bot.send_message(chat_id=player,
                                     text='You\'ve got new cards!')
            context.bot.send_message(chat_id=player,
                                     text='After this message are cards you have right now\n'
                                          '⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️️')
            send_set(player, game, context)
            context.bot.send_message(chat_id=player,
                                     text='Don\'t worry if you have less then 5 cards. You will get missing after the '
                                          'round is finished')

    except WrongChatException as ex:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=ex.message)
    except Exception:
        traceback.print_exc()


def dice(update, context):
    try:
        choice = random.choice(['*Association*', '*Story*', '*Chinese portrait*'])
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='The mode is......')
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=choice,
                                 parse_mode=ParseMode.MARKDOWN)
    except Exception:
        traceback.print_exc()


def get_card_from_pile(update, context):
    try:
        if update.effective_chat.id > 0:
            raise WrongChatException(ChatTypes.Private)

        game = get_game_by_group_id(update.effective_chat.id)

        if not game:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='There is no games attached to this chat. Make sure that you use the right '
                                          'chat and that the admin of a game has run the command /attach_group')
            return

        game = get_one_card(game, context)
        print(game)
        update_game(game)

    except WrongChatException as ex:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=ex.message)
    except Exception:
        traceback.print_exc()


def last_card(update, context):
    try:
        game = None
        if update.effective_chat.id < 0:
            game = get_game_by_group_id(update.effective_chat.id)
            if not game:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='There is no games attached to this chat. Make sure that you use the '
                                              'right chat and that the admin of a game has run the command '
                                              '/attach_group')
                return
        elif update.effective_chat.id > 0:
            game = get_game_by_user(update.effective_user.id)
            if not game:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='You don\t take part in any game.')
                return

        game = send_last_card(game, context)
        update_game(game)
    except Exception:
        traceback.print_exc()


def new_round(update, context):
    give_more_cards(update, context)
    dice(update, context)
