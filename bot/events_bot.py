import logging
import logging.config
from typing import List

import telebot
from flask import Flask, request
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import bot.constants as constants
import bot.settings as settings
import bot.utils as utils
import database.users_database as users
import database.venues_database as venues
from models.event import Event
from models.venue import Venue
from notifier import notifier_api

bot = telebot.TeleBot(settings.BOT_TOKEN)
server = Flask(__name__)


def build_venues_keyboard(subscribe: bool, venue_list: List[Venue] = None) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for venue in venue_list:
        markup.add(build_venue_keyboard_button(subscribe, venue))
    return markup


def build_venue_keyboard_button(subscribe: bool, venue: Venue):
    callback_data = f'{constants.VENUE_PREFIX}_{venue.venue_id}_'
    if subscribe:
        callback_data = callback_data + constants.SUBSCRIBE_POSTFIX
    else:
        callback_data = callback_data + constants.UNSUBSCRIBE_POSTFIX
    return InlineKeyboardButton(venue.display_name, callback_data=callback_data)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith(constants.MENU_PREFIX))
def main_menu_callback_handler(callback_query: CallbackQuery) -> None:
    if callback_query.data == constants.SUBSCRIBE_CALLBACK:
        subscribe_handler(message=callback_query.message)
    elif callback_query.data == constants.UNSUBSCRIBE_CALLBACK:
        unsubscribe_handler(message=callback_query.message)
    elif callback_query.data == constants.HELP_CALLBACK:
        help_handler(message=callback_query.message)
    elif callback_query.data == constants.SETTINGS_CALLBACK:
        settings_handler(message=callback_query.message)
    else:
        raise ValueError

    bot.answer_callback_query(callback_query_id=callback_query.id)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith(constants.SETTINGS_PREFIX))
def settings_callback_handler(callback_query: CallbackQuery) -> None:
    if callback_query.data == constants.LANGUAGE_CALLBACK:
        language_handler(message=callback_query.message)
    else:
        raise ValueError

    bot.answer_callback_query(callback_query_id=callback_query.id)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith(constants.LANGUAGE_PREFIX))
def language_callback_handler(callback_query: CallbackQuery) -> None:
    prefix, language = callback_query.data.split('_', maxsplit=1)
    if language in settings.SUPPORTED_LANGUAGES:
        users.update_user_language(str(callback_query.message.chat.id), language)
        bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.id,
                              text='Language updated')
    else:
        raise ValueError

    bot.answer_callback_query(callback_query_id=callback_query.id)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith(constants.VENUE_PREFIX))
def venue_callback_handler(callback_query: CallbackQuery) -> None:
    prefix, venue_id, subscription = callback_query.data.split('_')
    if subscription == constants.SUBSCRIBE_POSTFIX:
        subscribe_user_to_venue(callback_query.message, venue_id=venue_id)
    elif subscription == constants.UNSUBSCRIBE_POSTFIX:
        unsubscribe_user_from_venue(callback_query.message, venue_id=venue_id)
    else:
        raise ValueError

    bot.answer_callback_query(callback_query_id=callback_query.id)


@bot.message_handler(commands=['start', 'menu'])
def main_menu_handler(message: Message) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.add(
        InlineKeyboardButton(text='Subscribe to updates', callback_data=constants.SUBSCRIBE_CALLBACK),
        InlineKeyboardButton(text='Unsubscribe from updates', callback_data=constants.UNSUBSCRIBE_CALLBACK),
        InlineKeyboardButton(text='Settings', callback_data=constants.SETTINGS_CALLBACK),
        InlineKeyboardButton(text='Help', callback_data=constants.HELP_CALLBACK)
    )
    bot.send_message(message.chat.id, 'What would you like to do?', reply_markup=keyboard)


@bot.message_handler(commands=['settings'])
def settings_handler(message: Message) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.add(
        InlineKeyboardButton(text='Language', callback_data=constants.LANGUAGE_CALLBACK),
    )
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                          text='Choose a setting', reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def help_handler(message: Message) -> None:
    bot.send_message(chat_id=message.chat.id,
                     text=constants.WELCOME_MESSAGE, disable_web_page_preview=True)


@bot.message_handler(commands=['subscribe'])
def subscribe_handler(message: Message) -> None:
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                          text='Choose a venue to subscribe',
                          reply_markup=build_venues_keyboard(subscribe=True, venue_list=venues.retrieve_all_venues()))


def subscribe_user_to_venue(message: Message, venue_id: str) -> None:
    user_id = str(message.chat.id)
    logging.info(f'Subscribing user with id={user_id} to venue={venue_id}')
    if users.user_exists(user_id=user_id):
        users.add_venue_to_user(user_id=user_id, venue_id=venue_id)
    else:
        users.add_user(user_id=user_id, username=message.chat.username,
                       first_name=message.chat.first_name, last_name=message.chat.last_name,
                       venue_id=venue_id)
    logging.info(f'User with id={user_id} subscribed successfully to venue={venue_id}')
    bot.send_message(chat_id=message.chat.id, text='You have been subscribed!')


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe_handler(message: Message) -> None:
    user_id = str(message.chat.id)
    user_venues = users.retrieve_user_venues(user_id=user_id)
    if user_venues is None or len(user_venues) == 0:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                              text='You\'re not subscribed to any updates')
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                              text='Choose a venue to unsubscribe from',
                              reply_markup=build_venues_keyboard(subscribe=False, venue_list=user_venues))


def unsubscribe_user_from_venue(message: Message, venue_id: str) -> None:
    user_id = str(message.chat.id)
    logging.info(f'Unsubscribing user with id={user_id} from venue={venue_id}')
    users.remove_venue_from_user(user_id=user_id, venue_id=venue_id)
    logging.info(f'User with id={user_id} unsubscribed successfully from venue={venue_id}')
    bot.send_message(chat_id=message.chat.id, text='You have been unsubscribed!')


def language_handler(message: Message) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.add(
        InlineKeyboardButton(text='עברית', callback_data=constants.HEBREW_CALLBACK),
        InlineKeyboardButton(text='English', callback_data=constants.ENGLISH_CALLBACK),
    )
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                          text='Choose a language', reply_markup=keyboard)


@bot.message_handler(commands=['ping'])
def ping_handler(message: Message) -> None:
    bot.send_message(chat_id=message.chat.id, text='I\'m alive!')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_handler(message: Message) -> None:
    bot.reply_to(message, text=message.text)


@server.route(settings.PING_PATH, methods=['GET'])
def ping():
    return {'status': 'UP'}, 200


@server.route(settings.BOT_WEBHOOK_PATH, methods=['POST'])
def bot_webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return {}, 200


@server.route(settings.NOTIFIER_WEBHOOK_PATH, methods=['POST'])
def notify_webhook():
    data = request.get_json()
    events = list(map(lambda raw_event: Event.from_raw(raw_event), data))
    logging.info(f'Handling notification for {len(events)} events in total')
    for event in events:
        notify_users(event)
    return {}, 200


def notify_users(event: Event) -> None:
    event_data = str(event)
    venue_users = users.retrieve_users_by_venue(event.venue_id)
    logging.info(f'Notifying {len(list(venue_users))} users')
    for user in venue_users:
        bot.send_message(chat_id=user.user_id, text=f'Hey {utils.get_display_name(user)}, {event_data}')


def register_notifier_webhook() -> None:
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
    logging.basicConfig(format=settings.LOG_FORMAT, level=settings.LOG_LEVEL)
    logger = logging.getLogger(__name__)

    main()
