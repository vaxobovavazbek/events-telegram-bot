import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from bot.settings import BOT_TOKEN, USERS_COLLECTION_NAME
from database.mongo import remove_from_collection, insert_to_collection, exists_in_collection


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Hi!')


def help(update: Update, context: CallbackContext):
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)


def subscribe(update: Update, context: CallbackContext) -> None:
    user_id, username = str(update.message.from_user.id), update.message.from_user.username
    logging.info(f"Subscribing user with id={user_id} and username = {username}")
    if register_user(user_id, username):
        update.message.reply_text("You have been subscribed!")
    else:
        update.message.reply_text("You are already subscribed...")


def unsubscribe(update: Update, context: CallbackContext) -> None:
    user_id, username = str(update.message.from_user.id), update.message.from_user.username
    logging.info(f"Unsubscribing user with id={user_id} and username = {username}")
    if unregister_user(user_id):
        update.message.reply_text("You have been unsubscribed!")
    else:
        update.message.reply_text("You are not subscribed...")


def register_user(user_id: str, username: str):
    query = {"user_id": user_id, "username": username}
    if exists_in_collection(USERS_COLLECTION_NAME, query):
        return False
    insert_to_collection(USERS_COLLECTION_NAME, query)
    return True


def unregister_user(user_id: str):
    query = {"user_id": user_id}
    if exists_in_collection(USERS_COLLECTION_NAME, query):
        remove_from_collection(USERS_COLLECTION_NAME, query)
        return True
    return False


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)


class EventsBot:
    def __init__(self):
        self.updater = Updater(BOT_TOKEN, use_context=True)

        # Get the dispatcher to register handlers
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
        # Start the Bot
        self.updater.start_webhook(listen=WEBAPP_HOST,
                                   port=WEBAPP_PORT,
                                   url_path=BOT_TOKEN,
                                   webhook_url=WEBHOOK_URL)

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()
