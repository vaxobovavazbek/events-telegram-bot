from typing import List

from mongoengine import connect

from bot.settings import MONGODB_URI
from models.venue import Venue

db = connect(host=MONGODB_URI)


def retrieve_all_venues() -> List[Venue]:
    return Venue.objects()


def retrieve_display_name_by_id(venue_id: str) -> str:
    venues = Venue.objects.filter(venue_id=venue_id)
    if venues.count() != 1:
        raise ValueError

    return venues[0].display_name
