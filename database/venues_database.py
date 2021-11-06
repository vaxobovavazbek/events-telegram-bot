from typing import List

from mongoengine import connect

from bot.settings import MONGODB_URI
from models.venue import Venue

db = connect(host=MONGODB_URI)


def retrieve_all_venues() -> List[Venue]:
    return Venue.objects()


def retrieve_display_name_by_venue_id(venue_id: str) -> str:
    venue = retrieve_venue_by_venue_id(venue_id=venue_id)
    return venue.display_name


def retrieve_venue_by_venue_id(venue_id: str) -> Venue:
    venues = Venue.objects(venue_id=venue_id)
    if venues.count() != 1:
        raise ValueError
    return venues[0]
