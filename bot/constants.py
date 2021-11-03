STATES = {
    'START':
        ['SUBSCRIBE', 'UNSUBSCRIBE', 'HELP'],
    'VENUE':
        ['SAMMY']
}

HELP_CALLBACK = 'START_HELP'
SUBSCRIBE_CALLBACK = 'START_SUBSCRIBE'
UNSUBSCRIBE_CALLBACK = 'START_UNSUBSCRIBE'

CB_VENUE_SAMMY = 'VENUE_SAMMY'
UNSUB = '_UNSUB'

WELCOME_MESSAGE = '''Events Notifier Bot -

The bot that will notify you of upcoming events in your favorite stadiums or venues.

How to use the bot: 

Use the /subscribe command to subscribe to updates.
Use the /unsubscribe command to unsubscribe from updates.
Use the /help command to show this help message.

For any questions or issues, please go to - https://github.com/oriash93/events-telegram-bot'''
