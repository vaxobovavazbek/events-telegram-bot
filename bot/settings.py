import os

# general settings
PORT = os.getenv('PORT', '8443')
HOST = os.getenv('HOST', f'http://localhost:{PORT}')
BOT_TOKEN = os.getenv('BOT_TOKEN')
UPDATE_MODE = os.getenv('UPDATE_MODE', 'polling')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# web settings
BOT_WEBHOOK_PATH = f'/{BOT_TOKEN}'
BOT_WEBHOOK_URL = f'{HOST}{BOT_WEBHOOK_PATH}'
PING_PATH = '/v1/ping'

# mongodb settings
DATABASE_NAME = os.getenv('DATABASE_NAME', 'eventsNotifier')
MONGODB_URI = os.getenv('MONGODB_URI', f'mongodb://localhost:27017/{DATABASE_NAME}')

# notifier settings
NOTIFIER_HOST = os.getenv('NOTIFIER_HOST', 'http://localhost:3800')
NOTIFIER_PATH = '/v1/webhooks'
NOTIFIER_URL = f'{NOTIFIER_HOST}{NOTIFIER_PATH}'
NOTIFIER_WEBHOOK_PATH = '/v1/notify'
NOTIFIER_WEBHOOK_URL = f'{HOST}{NOTIFIER_WEBHOOK_PATH}'

DEFAULT_LANGUAGE_CODE = 'HE_IL'
SUPPORTED_LANGUAGES = {
    'HE_IL': 'עברית',
    'EN_US': 'English'
}
