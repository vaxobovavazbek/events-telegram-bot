import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from bot.settings import BOT_TOKEN, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL
from database.users_database import register_user, unregister_user


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Hi!')


def help(update: Update, context: CallbackContext):
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)


def subscribe(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    logging.info(f"Subscribing user with id={user_id}")
    register_user(user_id=user_id, username=update.message.from_user.username,
                  first_name=update.message.from_user.first_name, last_name=update.message.from_user.last_name)
    update.message.reply_text("You have been subscribed!")


def unsubscribe(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    logging.info(f"Unsubscribing user with id={user_id}")
    unregister_user(user_id)
    update.message.reply_text("You have been unsubscribed!")


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)


class EventsBot:
    def __init__(self):
        self.updater = Updater(BOT_TOKEN, use_context=True)
        self.dp = self.updater.dispatcher
        self._register_handlers()

    def _register_handlers(self):
        # on different commands - answer in Telegram
        self.dp.add_handler(CommandHandler('start', start))
        self.dp.add_handler(CommandHandler('help', help))
        self.dp.add_handler(CommandHandler('subscribe', subscribe))
        self.dp.add_handler(CommandHandler('unsubscribe', unsubscribe))

        # on non-command i.e message - echo the message on Telegram
        self.dp.add_handler(MessageHandler(Filters.text, echo))

        # log all errors
        self.dp.add_error_handler(error)

    def start(self):
        self._start_webhook()
        self.updater.idle()

    def _start_webhook(self):
        self.updater.start_webhook(listen=WEBAPP_HOST,
                                   port=WEBAPP_PORT,
                                   url_path=BOT_TOKEN,
                                   webhook_url=WEBHOOK_URL)
