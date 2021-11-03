import logging
import logging.config

import telebot
from flask import Flask, request
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import bot.constants as constants
import bot.settings as settings
import bot.utils as utils
from database import users_database
from models.event import Event
from notifier import notifier_api

bot = telebot.TeleBot(settings.BOT_TOKEN)
server = Flask(__name__)


def start_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(text='Subscribe to updates', callback_data=constants.SUBSCRIBE_CALLBACK),
        InlineKeyboardButton(text='Unsubscribe from updates', callback_data=constants.UNSUBSCRIBE_CALLBACK),
        InlineKeyboardButton(text='Help', callback_data=constants.HELP_CALLBACK)
    )
    return markup


def venues_keyboard(sub: bool) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    callback_data = constants.CB_VENUE_SAMMY
    if not sub:
        callback_data = callback_data + constants.UNSUB
    markup.add(InlineKeyboardButton('Sammy Ofer', callback_data=callback_data))
    return markup


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith('START'))
def start_callback_handler(callback_query: CallbackQuery):
    if callback_query.data == constants.SUBSCRIBE_CALLBACK:
        subscribe_handler(callback_query.message)

    elif callback_query.data == constants.UNSUBSCRIBE_CALLBACK:
        unsubscribe_handler(callback_query.message)

    elif callback_query.data == constants.HELP_CALLBACK:
        help_handler(message=callback_query.message)

    else:
        raise ValueError

    bot.answer_callback_query(callback_query_id=callback_query.id)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith('VENUE'))
def venue_callback_handler(callback_query: CallbackQuery):
    venue = callback_query.data.split('_')[1]
    if constants.UNSUB in callback_query.data:
        unsubscribe_user_from_venue(callback_query.message, venue=venue)
    else:
        subscribe_user_to_venue(callback_query.message, venue=venue)

    bot.answer_callback_query(callback_query_id=callback_query.id)


@bot.message_handler(commands=['start'])
def start_handler(message: Message) -> None:
    bot.send_message(message.chat.id, 'What would you like to do?', reply_markup=start_keyboard())


@bot.message_handler(commands=['help'])
def help_handler(message: Message) -> None:
    bot.reply_to(message, text=constants.WELCOME_MESSAGE, disable_web_page_preview=True)


@bot.message_handler(commands=['subscribe'])
def subscribe_handler(message: Message) -> None:
    bot.send_message(message.chat.id, 'Choose a venue to subscribe', reply_markup=venues_keyboard(sub=True))


def subscribe_user_to_venue(message: Message, venue: str):
    user_id = str(message.chat.id)
    logging.info(f'Subscribing user with id={user_id} to venue={venue}')
    if users_database.user_exists(user_id=user_id):
        users_database.add_venue_to_user(user_id=user_id, venue=venue)
    else:
        users_database.add_user(user_id=user_id, username=message.chat.username,
                                first_name=message.chat.first_name, last_name=message.chat.last_name,
                                venue=venue)
    logging.info(f'User with id={user_id} subscribed successfully to venue={venue}')
    bot.reply_to(message, text='You have been subscribed!')


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe_handler(message: Message) -> None:
    bot.send_message(message.chat.id, 'Choose a venue to unsubscribe', reply_markup=venues_keyboard(sub=False))


def unsubscribe_user_from_venue(message: Message, venue: str):
    user_id = str(message.chat.id)
    logging.info(f'Unsubscribing user with id={user_id} from venue={venue}')
    users_database.remove_venue_from_user(user_id=user_id, venue=venue)
    logging.info(f'User with id={user_id} unsubscribed successfully from venue={venue}')
    bot.reply_to(message, text='You have been unsubscribed!')


@bot.message_handler(commands=['ping'])
def ping_handler(message: Message) -> None:
    bot.reply_to(message, text='I\'m alive!')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_handler(message: Message):
    bot.reply_to(message, text=message.text)


@server.route(settings.PING_PATH, methods=['GET'])
def ping():
    return {'status': 'UP'}, 200


@server.route(settings.BOT_WEBHOOK_PATH, methods=['POST'])
def bot_webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200


@server.route(settings.NOTIFIER_WEBHOOK_PATH, methods=['POST'])
def notify_webhook():
    data = request.get_json()
    events = list(map(lambda raw_event: Event.from_raw(raw_event), data))
    logging.info(f'Handling notification for {len(events)} events')
    for event in events:
        notify_users(event)
    return {}, 200


def notify_users(event_data: str) -> None:
    users = users_database.retrieve_all_active_users()
    logging.info(f'Notifying {len(list(users))} active users')
    for user in users:
        bot.send_message(chat_id=user.user_id, text=f'Hey {utils.get_display_name(user)}, {event_data}')


def register_notifier_webhook():
    logging.info('Registering notifier webhook')
    notifier_api.add_notifier_webhook(name='events_bot', url=settings.NOTIFIER_WEBHOOK_URL)


def main():
    register_notifier_webhook()

    if settings.UPDATE_MODE == 'webhook':
        bot.remove_webhook()
        bot.set_webhook(url=settings.BOT_WEBHOOK_URL)
        server.run(host='0.0.0.0', port=settings.PORT)
        logging.info(f'Start webhook mode on port {settings.PORT}')
    else:
        logging.info(f'Start polling mode')
        if bot.get_webhook_info().url:
            bot.remove_webhook()
        bot.infinity_polling()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=settings.LOG_LEVEL)
    logger = logging.getLogger(__name__)

    main()
