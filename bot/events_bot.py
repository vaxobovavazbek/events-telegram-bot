import logging
import logging.config
import os
from typing import List

import emoji
import i18n
from flask import Flask, request
from telebot import TeleBot, apihelper
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Update

import notifier.notifier_api as notifier_api
from bot import settings, constants
from bot.i18n_utils import translate as _, set_locale
from database import users_database as users
from database import venues_database as venues
from models.event import Event
from models.venue import Venue

apihelper.ENABLE_MIDDLEWARE = True

bot = TeleBot(settings.BOT_TOKEN)
server = Flask(__name__)


@bot.middleware_handler(update_types=['message'])
def user_management_middleware(bot_instance: TeleBot, message: Message):
    user_id = str(message.chat.id)
    if not users.user_exists(user_id):
        users.add_user(user_id=user_id, username=message.chat.username,
                       first_name=message.chat.first_name, last_name=message.chat.last_name)


@bot.middleware_handler(update_types=['message'])
def locale_middleware(bot_instance: TeleBot, message: Message):
    user_id = str(message.chat.id)
    set_locale(users.retrieve_user_language(user_id))


def send_message(message: Message, **kwargs) -> None:
    if message.from_user.is_bot:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, **kwargs)
    else:
        bot.send_message(chat_id=message.chat.id, **kwargs)


def build_venues_keyboard(subscribe: bool, venue_list: List[Venue] = None) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for venue in venue_list:
        markup.add(build_venue_keyboard_button(subscribe, venue))
    return markup


def build_venue_keyboard_button(subscribe: bool, venue: Venue):
    callback_data = f'{constants.VENUE_PREFIX}'
    if subscribe:
        callback_data = f'{callback_data}_{constants.SUBSCRIBE_POSTFIX}'
    else:
        callback_data = f'{callback_data}_{constants.UNSUBSCRIBE_POSTFIX}'
    callback_data = f'{callback_data}_{venue.venue_id}'
    return InlineKeyboardButton(text=_(venue.venue_id), callback_data=callback_data)


def build_language_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for language_code, display_name in settings.SUPPORTED_LOCALES.items():
        callback_data = f'{constants.LANGUAGE_PREFIX}_{language_code}'
        markup.add(InlineKeyboardButton(text=display_name, callback_data=callback_data))
    return markup


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith(constants.MENU_PREFIX))
def main_menu_callback_handler(callback_query: CallbackQuery) -> None:
    if callback_query.data == constants.SUBSCRIBE_CALLBACK:
        subscribe_handler(message=callback_query.message)
    elif callback_query.data == constants.UNSUBSCRIBE_CALLBACK:
        unsubscribe_handler(message=callback_query.message)
    elif callback_query.data == constants.EVENTS_TODAY_CALLBACK:
        events_today_handler(message=callback_query.message)
    elif callback_query.data == constants.HELP_CALLBACK:
        help_handler(message=callback_query.message)
    elif callback_query.data == constants.SETTINGS_CALLBACK:
        settings_handler(message=callback_query.message)
    else:
        raise Warning(f'Failed to handle {callback_query.data} callback')

    bot.answer_callback_query(callback_query_id=callback_query.id)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith(constants.SETTINGS_PREFIX))
def settings_callback_handler(callback_query: CallbackQuery) -> None:
    if callback_query.data == constants.LANGUAGE_CALLBACK:
        language_handler(message=callback_query.message)
    else:
        raise Warning(f'Failed to handle {callback_query.data} callback')

    bot.answer_callback_query(callback_query_id=callback_query.id)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith(constants.LANGUAGE_PREFIX))
def language_callback_handler(callback_query: CallbackQuery) -> None:
    prefix, locale = callback_query.data.split('_', maxsplit=1)
    if locale in settings.SUPPORTED_LOCALES.keys():
        user_id = str(callback_query.message.chat.id)
        users.update_user_language(user_id, locale)
        settings.CURRENT_LOCALE = locale
        send_message(message=callback_query.message, text=_('LANGUAGE_SETTINGS_UPDATED'))
        logging.info(f'User with id={user_id} updated language settings to {locale}')
    else:
        raise Warning(f'Language {locale} not supported')

    bot.answer_callback_query(callback_query_id=callback_query.id)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith(constants.VENUE_PREFIX))
def venue_callback_handler(callback_query: CallbackQuery) -> None:
    prefix, subscription, venue_id = callback_query.data.split('_', maxsplit=2)
    if subscription == constants.SUBSCRIBE_POSTFIX:
        subscribe_user_to_venue(callback_query.message, venue_id=venue_id)
    elif subscription == constants.UNSUBSCRIBE_POSTFIX:
        unsubscribe_user_from_venue(callback_query.message, venue_id=venue_id)
    else:
        raise Warning(f'Failed to handle {callback_query.data} callback')

    bot.answer_callback_query(callback_query_id=callback_query.id)


@bot.message_handler(commands=['start', 'menu'])
def main_menu_handler(message: Message) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.add(
        InlineKeyboardButton(text=_('SUBSCRIBE_MENU_ITEM') + ' ' + emoji.emojize(':bell:'),
                             callback_data=constants.SUBSCRIBE_CALLBACK),
        InlineKeyboardButton(text=_('UNSUBSCRIBE_MENU_ITEM') + ' ' + emoji.emojize(':bell_with_slash:'),
                             callback_data=constants.UNSUBSCRIBE_CALLBACK),
        InlineKeyboardButton(text=_('EVENTS_TODAY_MENU_ITEM') + ' ' + emoji.emojize(':calendar:'),
                             callback_data=constants.EVENTS_TODAY_CALLBACK),
        InlineKeyboardButton(text=_('SETTINGS_MENU_ITEM') + ' ' + emoji.emojize(':gear:'),
                             callback_data=constants.SETTINGS_CALLBACK),
        InlineKeyboardButton(text=_('HELP_MENU_ITEM') + ' ' + emoji.emojize(':red_question_mark:'),
                             callback_data=constants.HELP_CALLBACK)
    )
    send_message(message=message, text=_('MAIN_MENU_PROMPT'), reply_markup=keyboard)


@bot.message_handler(commands=['today'])
def events_today_handler(message: Message) -> None:
    events = notifier_api.get_today_events()
    if events is None or len(events) == 0:
        send_message(message=message, text=_('NO_EVENTS_TODAY'))
    for event in events:
        notify_users(event=event, user_id=str(message.chat.id))


@bot.message_handler(commands=['settings'])
def settings_handler(message: Message) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.add(
        InlineKeyboardButton(text=_('LANGUAGE_MENU_ITEM') + ' ' + emoji.emojize(':globe_with_meridians:'),
                             callback_data=constants.LANGUAGE_CALLBACK),
    )
    send_message(message=message, text=_('CHOOSE_SETTING'), reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def help_handler(message: Message) -> None:
    send_message(message=message, text=_('HELP_MESSAGE'), disable_web_page_preview=True)


@bot.message_handler(commands=['subscribe'])
def subscribe_handler(message: Message) -> None:
    user_id = str(message.chat.id)
    user_venues = users.retrieve_user_venues(user_id=user_id)
    all_venues = venues.retrieve_all_venues()
    if user_venues is None or len(user_venues) == 0:
        available_venues = all_venues
    else:
        if len(user_venues) == len(all_venues):
            send_message(message=message, text=_('ALL_SUBSCRIBED'))
            return
        else:
            available_venues = [venue for venue in all_venues if venue not in user_venues]

    send_message(message=message, text=_('CHOOSE_VENUE') + ' ' + emoji.emojize(':stadium:'),
                 reply_markup=build_venues_keyboard(subscribe=True, venue_list=available_venues))


def subscribe_user_to_venue(message: Message, venue_id: str) -> None:
    user_id = str(message.chat.id)
    logging.info(f'Subscribing user with id={user_id} to venue={venue_id}')
    users.add_venue_to_user(user_id=user_id, venue_id=venue_id)
    logging.info(f'User with id={user_id} subscribed successfully to venue={venue_id}')
    send_message(message=message, text=_('SUBSCRIPTION_COMPLETED_FORMAT', venue=_(venue_id)))


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe_handler(message: Message) -> None:
    user_id = str(message.chat.id)
    user_venues = users.retrieve_user_venues(user_id=user_id)
    if user_venues is None or len(user_venues) == 0:
        send_message(message=message, text=_('NO_SUBSCRIPTION'))
    else:
        send_message(message=message, text=_('CHOOSE_VENUE') + ' ' + emoji.emojize(':stadium:'),
                     reply_markup=build_venues_keyboard(subscribe=False, venue_list=user_venues))


def unsubscribe_user_from_venue(message: Message, venue_id: str) -> None:
    user_id = str(message.chat.id)
    logging.info(f'Unsubscribing user with id={user_id} from venue={venue_id}')
    users.remove_venue_from_user(user_id=user_id, venue_id=venue_id)
    logging.info(f'User with id={user_id} unsubscribed successfully from venue={venue_id}')
    send_message(message=message, text=_('UNSUBSCRIPTION_COMPLETED_FORMAT', venue=_(venue_id)))


def language_handler(message: Message) -> None:
    send_message(message=message, text=_('CHOOSE_LANGUAGE'), reply_markup=build_language_keyboard())


@bot.message_handler(commands=['ping'])
def ping_handler(message: Message) -> None:
    send_message(message=message, text=_('PING_RESPONSE'))


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_handler(message: Message) -> None:
    send_message(message=message, text=_('UNKNOWN_COMMAND') + ' ' + emoji.emojize(':thinking_face:'))


@server.route(settings.PING_PATH, methods=['GET'])
def ping():
    return {'status': 'UP'}, 200


@server.route(settings.BOT_WEBHOOK_PATH, methods=['POST'])
def bot_webhook():
    json_string = request.get_data().decode('utf-8')
    update = Update.de_json(json_string)
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


def notify_users(event: Event, user_id: str = None) -> None:
    event_data = str(event)
    if user_id is not None:
        venue_users = list(users.retrieve_user_by_user_id(user_id=user_id))
    else:
        venue_users = users.retrieve_users_by_venue(venue_id=event.venue_id)
    logging.info(f'Notifying {len(list(venue_users))} users')
    for user in venue_users:
        bot.send_message(chat_id=user.user_id, text=event_data)


def register_notifier_webhook() -> None:
    logging.info('Registering notifier webhook')
    notifier_api.add_notifier_webhook(name='events_bot', url=settings.NOTIFIER_WEBHOOK_URL)


def main():
    register_notifier_webhook()
    bot.remove_webhook()

    if settings.UPDATE_MODE == 'webhook':
        bot.set_webhook(url=settings.BOT_WEBHOOK_URL)
        logging.info(f'Start webhook mode on port {settings.PORT}')
        server.run(host='0.0.0.0', port=settings.PORT)
    elif settings.UPDATE_MODE == 'polling':
        logging.info(f'Start polling mode')
        bot.infinity_polling()
    else:
        logging.info('bot created, not recieving updates')
        logging.info(f'settings {settings.HOST} {settings.PORT}')


def _setup_logging() -> None:
    logging.basicConfig(format=settings.LOG_FORMAT, level=settings.LOG_LEVEL)


def _setup_i18n() -> None:
    i18n.set('locale', settings.DEFAULT_LOCALE)
    locale_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    i18n.load_path.append(locale_dir)
    i18n.set('filename_format', '{locale}.{format}')


if __name__ == '__main__':
    _setup_logging()
    _setup_i18n()

    main()
