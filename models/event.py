from datetime import datetime

from bot.i18n_utils import translate as _


class Event:
    def __init__(self, description: str, venue_id: str, event_time: str):
        self.description = description
        self.venue_id = venue_id
        self.event_time = datetime.fromisoformat(event_time)

    @classmethod
    def from_raw(cls, raw):
        return cls(description=raw['description'], venue_id=raw['venue'], event_time=raw['eventTime'])

    def __str__(self) -> str:
        return _('EVENT_NOTIFICATION_FORMAT',
                 venue=_(self.venue_id), description=self.description, time=self.event_time.strftime("%H:%M"))
