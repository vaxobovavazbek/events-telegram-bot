import logging
from typing import List, Union

import requests
from requests.adapters import HTTPAdapter, Retry

from bot.settings import NOTIFIER_HOST
from models.event import Event
from models.webhook import Webhook

http = requests.Session()
http.mount('http', HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1)))


def add_notifier_webhook(name: str, url: str) -> None:
    try:
        r = requests.post(url=f'{NOTIFIER_HOST}/v1/webhooks', json=Webhook(name=name, url=url).__dict__)
        r.raise_for_status()

    except requests.exceptions.ConnectionError:
        logging.warning('Failed to connect to notifier API')
        return None

    except Exception:
        logging.error('Notifier API request failed')
        return None

    logging.info(f'Notifier webhook with name={name} added successfully')


def get_today_events() -> Union[List[Event], None]:
    try:
        r = requests.get(url=f'{NOTIFIER_HOST}/v1/events/today')
        r.raise_for_status()

    except requests.exceptions.ConnectionError:
        logging.warning('Failed to connect to notifier API')
        return None

    except Exception:
        logging.error('Notifier API request failed')
        return None

    events = list(map(lambda raw_event: Event.from_raw(raw_event), r.json()))
    logging.info('Retrieved today\'s events successfully')
    return events
