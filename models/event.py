from datetime import datetime


class Event:
    def __init__(self, description: str, event_time: str):
        self.description = description
        self.event_time = datetime.fromisoformat(event_time)

    @classmethod
    def from_raw(cls, raw):
        return cls(raw['description'], raw['eventTime'])

    def __str__(self) -> str:
        return f'Event {self.description} happening today at {self.event_time.strftime("%H:%M")}'
