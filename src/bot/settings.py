import os

# general settings
BOT_TOKEN = os.getenv('BOT_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', '8443'))

# webhook settings
if not HEROKU_APP_NAME:
    WEBHOOK_HOST = f'http://localhost:{WEBAPP_PORT}'
else:
    WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# mongodb settings
DATABASE_NAME = 'eventsNotifier'
MONGODB_URI = os.getenv('MONGODB_URI', f'mongodb://localhost:27017/{DATABASE_NAME}')

# notifier settings
NOTIFIER_HOST = os.getenv('NOTIFIER_HOST', 'http://localhost:3800')
NOTIFIER_PATH = f'/v1/webhooks'
NOTIFIER_URL = f'{NOTIFIER_HOST}{NOTIFIER_PATH}'
