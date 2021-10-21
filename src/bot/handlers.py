import logging

from telegram import Update
from telegram.ext import CallbackContext

from database.users_database import add_user, remove_user

WELCOME_MESSAGE = '''Events Notifier Bot -

The bot that will notify you of upcoming events in your favorite stadiums or venues.

How to use the bot: 

Use the /subscribe command to subscribe to updates.
Use the /unsubscribe command to unsubscribe from updates.
Use the /help command to show this help message.

For any questions or issues, please go to - https://github.com/oriash93/events-telegram-bot'''


def start_handler(update: Update, context: CallbackContext):
    update.message.reply_text(text=WELCOME_MESSAGE, disable_web_page_preview=True)


def help_handler(update: Update, context: CallbackContext):
    update.message.reply_text(text=WELCOME_MESSAGE, disable_web_page_preview=True)


def echo_handler(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)


def subscribe_handler(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    logging.info(f"Subscribing user with id={user_id}")
    add_user(user_id=user_id, username=update.message.from_user.username,
             first_name=update.message.from_user.first_name, last_name=update.message.from_user.last_name)
    logging.info(f"User with id={user_id} subscribed successfully")
    update.message.reply_text("You have been subscribed!")


def unsubscribe_handler(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    logging.info(f"Unsubscribing user with id={user_id}")
    remove_user(user_id)
    logging.info(f"User with id={user_id} unsubscribed successfully")
    update.message.reply_text("You have been unsubscribed!")


def error_handler(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error_handler "%s"', update, context.error)
