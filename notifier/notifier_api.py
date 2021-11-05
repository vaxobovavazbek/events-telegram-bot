import logging

import requests
from requests.adapters import HTTPAdapter, Retry

from bot.settings import NOTIFIER_URL
from models.webhook import Webhook

http = requests.Session()
http.mount("http", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1)))


def add_notifier_webhook(name: str, url: str) -> None:
    try:
        r = requests.post(url=NOTIFIER_URL, json=Webhook(name=name, url=url).__dict__)
        r.raise_for_status()

    except Exception:
        logging.error('Notifier API request failed')
        return

    logging.info(f'Notifier webhook with name={name} added successfully')
