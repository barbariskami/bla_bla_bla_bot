from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from handlers import create_game, end_game, begin, enter_game, attach_group, quit_game, card_catcher, current_set
from handlers import give_more_cards, dice, get_card_from_pile, last_card, new_round


def main():
    updater = Updater("1235139693:AAEjKlvPKC3MwotxKRbRVd6ho-WZ5h3qjFo", use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('create_game', create_game))
    dp.add_handler(CommandHandler('end_game', end_game))
    dp.add_handler(CommandHandler('attach_group', attach_group))
    dp.add_handler(CommandHandler('enter_game', enter_game))
    dp.add_handler(CommandHandler('quit_game', quit_game))
    dp.add_handler(CommandHandler('begin', begin))
    dp.add_handler(CommandHandler('current_set', current_set))
    dp.add_handler(CommandHandler('give_more_cards', give_more_cards))
    dp.add_handler(CommandHandler('dice', dice))
    dp.add_handler(CommandHandler('get_card_from_pile', get_card_from_pile))
    dp.add_handler(MessageHandler(Filters.forwarded, card_catcher))
    dp.add_handler(CommandHandler('last_card', last_card))
    dp.add_handler(CommandHandler('new_round', new_round))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
