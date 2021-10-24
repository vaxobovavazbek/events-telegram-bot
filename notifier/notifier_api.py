import logging

import requests

from bot.settings import NOTIFIER_URL
from models.webhook import Webhook


def add_notifier_webhook(name: str, url: str) -> None:
    requests.post(url=NOTIFIER_URL, json=Webhook(name=name, url=url).__dict__)
    logging.info(f'Notifier webhook with name={name} added successfully')


def delete_notifier_webhook(name: str) -> None:
    requests.delete(url=NOTIFIER_URL, params={"name": name})
    logging.info(f'Notifier webhook with name={name} deleted successfully')
