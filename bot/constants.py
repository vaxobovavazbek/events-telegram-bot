MENU_PREFIX = 'MENU'
SUBSCRIBE_CALLBACK = f'{MENU_PREFIX}_SUBSCRIBE'
UNSUBSCRIBE_CALLBACK = f'{MENU_PREFIX}_UNSUBSCRIBE'
SETTINGS_CALLBACK = f'{MENU_PREFIX}_SETTINGS'
HELP_CALLBACK = f'{MENU_PREFIX}_HELP'

SETTINGS_PREFIX = 'SETTINGS'
LANGUAGE_CALLBACK = f'{SETTINGS_PREFIX}_LANGUAGE'
TIMEZONE_CALLBACK = f'{SETTINGS_PREFIX}_TZ'

LANGUAGE_PREFIX = 'LANG'
HEBREW_CALLBACK = f'{LANGUAGE_PREFIX}_HE_IL'
ENGLISH_CALLBACK = f'{LANGUAGE_PREFIX}_EN_US'

VENUE_PREFIX = 'VENUE'

SUBSCRIBE_POSTFIX = 'SUBSCRIBE'
UNSUBSCRIBE_POSTFIX = 'UNSUBSCRIBE'

WELCOME_MESSAGE = '''Events Notifier Bot -

The bot that will notify you of upcoming events in your favorite stadiums or venues.

How to use the bot: 

Use the /start or /menu command to show the main menu.
Use the /subscribe command to subscribe to updates.
Use the /unsubscribe command to unsubscribe from updates.
Use the /settings command to configure user settings.
Use the /help command to show this help message.

For any questions or issues, please go to - https://github.com/oriash93/events-telegram-bot'''
