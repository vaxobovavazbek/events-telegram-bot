import os

# general settings
BOT_TOKEN = os.getenv('BOT_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.environ.get('PORT', '8443'))

# mongodb settings
DATABASE_NAME = 'eventsNotifier'
MONGODB_URI = os.environ.get('MONGODB_URI', f'mongodb://localhost:27017/{DATABASE_NAME}')
