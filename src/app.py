import logging

from bot.bot import EventsBot

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    bot = EventsBot()
    bot.start()


if __name__ == '__main__':
    main()
