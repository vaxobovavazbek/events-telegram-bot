import logging
import logging.config

import telebot
from flask import Flask, request, jsonify, make_response, Response
from telebot.types import Message

from bot.settings import LOG_LEVEL, BOT_TOKEN, UPDATE_MODE, PORT, BOT_WEBHOOK_URL, BOT_WEBHOOK_PATH, \
    NOTIFIER_WEBHOOK_PATH, NOTIFIER_WEBHOOK_URL
from bot.utils import get_display_name
from database.users_database import retrieve_all_active_users, add_user, remove_user
from models.event import Event
from notifier import notifier_api

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

WELCOME_MESSAGE = '''Events Notifier Bot -

The bot that will notify you of upcoming events in your favorite stadiums or venues.

How to use the bot: 

Use the /subscribe command to subscribe to updates.
Use the /unsubscribe command to unsubscribe from updates.
Use the /help command to show this help message.

For any questions or issues, please go to - https://github.com/oriash93/events-telegram-bot'''


@bot.message_handler(commands=['start'])
def start_handler(message: Message) -> None:
    bot.reply_to(message, text=f'Hey, please use the /help command :)')


@bot.message_handler(commands=['help'])
def help_handler(message: Message) -> None:
    bot.reply_to(message, text=WELCOME_MESSAGE, disable_web_page_preview=True)


@bot.message_handler(commands=['subscribe'])
def subscribe_handler(message: Message) -> None:
    user_id = str(message.from_user.id)
    logging.info(f"Subscribing user with id={user_id}")
    add_user(user_id=user_id, username=message.from_user.username,
             first_name=message.from_user.first_name, last_name=message.from_user.last_name)
    logging.info(f"User with id={user_id} subscribed successfully")
    bot.reply_to(message, text='You have been subscribed!')


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe_handler(message: Message) -> None:
    user_id = str(message.from_user.id)
    logging.info(f"Unsubscribing user with id={user_id}")
    remove_user(user_id)
    logging.info(f"User with id={user_id} unsubscribed successfully")
    bot.reply_to(message, text='You have been unsubscribed!')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_handler(message: Message):
    bot.reply_to(message, message.text)


@server.route(BOT_WEBHOOK_PATH, methods=['POST'])
def bot_webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route(NOTIFIER_WEBHOOK_PATH, methods=["POST"])
def notify_webhook() -> Response:
    data = request.get_json()
    events = list(map(lambda raw_event: Event.from_raw(raw_event), data))
    logging.info(f'Handling notification for {len(events)} events')
    for event in events:
        notify_users(event)
    return make_response(jsonify({}, 200))


def notify_users(event_data: str) -> None:
    users = retrieve_all_active_users()
    logging.info(f'Notifying {len(list(users))} active users')
    for user in users:
        bot.send_message(chat_id=user.user_id, text=f'Hey {get_display_name(user)}, {event_data}')


def main():
    notifier_api.add_notifier_webhook(name='events_bot', url=NOTIFIER_WEBHOOK_URL)

    if UPDATE_MODE == 'webhook':
        bot.remove_webhook()
        bot.set_webhook(url=BOT_WEBHOOK_URL)
        server.run(host="0.0.0.0", port=PORT)
        logging.info(f"Start webhook mode on port {PORT}")
    else:
        logging.info(f"Start polling mode")
        bot.infinity_polling()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=LOG_LEVEL)

    main()