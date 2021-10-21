import os

# general settings
BOT_TOKEN = os.getenv('BOT_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# web settings
WEBAPP_PORT = int(os.getenv('PORT', '8443'))
if not HEROKU_APP_NAME:  # dev
    WEBAPP_HOST = f'localhost:{WEBAPP_PORT}'
    FLASK_HOST = '0.0.0.0'
else:  # prod
    WEBAPP_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
    FLASK_HOST = WEBAPP_HOST
BOT_WEBHOOK_PATH = f'/{BOT_TOKEN}'
BOT_WEBHOOK_URL = f'{WEBAPP_HOST}{BOT_WEBHOOK_PATH}'

# mongodb settings
DATABASE_NAME = os.getenv('DATABASE_NAME', 'eventsNotifier')
MONGODB_URI = os.getenv('MONGODB_URI', f'mongodb://localhost:27017/{DATABASE_NAME}')

# notifier settings
NOTIFIER_HOST = os.getenv('NOTIFIER_HOST', 'http://localhost:3800')
NOTIFIER_PATH = f'/v1/webhooks'
NOTIFIER_URL = f'{NOTIFIER_HOST}{NOTIFIER_PATH}'
NOTIFIER_WEBHOOK_PATH = '/notify'
NOTIFIER_WEBHOOK_URL = f'{WEBAPP_HOST}{NOTIFIER_WEBHOOK_PATH}'
