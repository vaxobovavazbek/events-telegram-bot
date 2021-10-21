import logging
from threading import Thread

import requests
from flask import Flask, request, make_response, jsonify
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from bot.handlers import start_handler, subscribe_handler, unsubscribe_handler, help_handler, echo_handler
from bot.settings import BOT_TOKEN, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL, NOTIFIER_URL, NOTIFIER_WEBHOOK_URL, \
    NOTIFIER_WEBHOOK_PATH
from database.users_database import retrieve_all_active_users
from models.event import Event
from models.webhook import Webhook


class EventsBot:
    def __init__(self):
        self.updater = Updater(BOT_TOKEN, use_context=True)
        self.dp = self.updater.dispatcher
        self._register_handlers()

    def _register_handlers(self):
        self.dp.add_handler(CommandHandler('start', start_handler))
        self.dp.add_handler(CommandHandler('help', help_handler))
        self.dp.add_handler(CommandHandler('subscribe', subscribe_handler))
        self.dp.add_handler(CommandHandler('unsubscribe', unsubscribe_handler))

        # on non-command i.e message - echo_handler the message on Telegram
        self.dp.add_handler(MessageHandler(Filters.text, echo_handler))

    def notify_users(self, event_data):
        users = retrieve_all_active_users()
        logging.info(f'Notifying for {len(list(users))} active users')
        for user in users:
            display_name = ''
            if user.first_name:
                display_name = user.first_name
            elif user.username:
                display_name = user.username
            self.updater.bot.send_message(chat_id=user.user_id, text=f'Hey {display_name}, {event_data}')

    def start(self):
        self._start_webhook()
        self._register_notifier_webhook()
        self.updater.idle()

    def _start_webhook(self):
        self.updater.start_webhook(listen=WEBAPP_HOST,
                                   port=WEBAPP_PORT,
                                   url_path=BOT_TOKEN,
                                   webhook_url=WEBHOOK_URL)

    @staticmethod
    def _register_notifier_webhook():
        webhook = Webhook(url=NOTIFIER_WEBHOOK_URL, name='bot')
        requests.post(url=NOTIFIER_URL, json=webhook.__dict__)
        logging.info('Notifier webhook registered successfully')


app = Flask(__name__)
bot = EventsBot()


@app.route(NOTIFIER_WEBHOOK_PATH, methods=["POST"])
def handle_notification():
    data = request.get_json()
    events = list(map(lambda raw_event: Event.from_raw(raw_event), data))
    logging.info(f'Handling notification for {len(events)} events')
    for event in events:
        bot.notify_users(event)
    return make_response(jsonify({}, 200))


def start_flask_app():
    app.run(port=WEBAPP_PORT, host=WEBAPP_HOST)


def main():
    Thread(target=start_flask_app).start()
    bot.start()
