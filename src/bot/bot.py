import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from bot.settings import BOT_TOKEN, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Hi!')


def help(update: Update, context: CallbackContext):
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)


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
