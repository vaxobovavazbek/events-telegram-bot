from typing import List

from mongoengine import connect

from bot.settings import MONGODB_URI
from database import venues_database as venues
from models.user import User
from models.venue import Venue

db = connect(host=MONGODB_URI)


def add_user(user_id: str, username: str, first_name: str, last_name: str, venue_id: str) -> None:
    User(user_id=user_id, username=username, first_name=first_name, last_name=last_name).save()
    add_venue_to_user(user_id=user_id, venue_id=venue_id)


def retrieve_users_by_venue(venue_id: str) -> List[User]:
    venue = venues.retrieve_venue_by_venue_id(venue_id=venue_id)
    return User.objects.filter(venues__in=[venue])


def retrieve_user_venues(user_id: str) -> List[Venue]:
    return User.objects(user_id=user_id).get().venues


def user_exists(user_id: str) -> bool:
    return User.objects(user_id=user_id).count() == 1


def add_venue_to_user(user_id: str, venue_id: str) -> None:
    user = User.objects(user_id=user_id).get()
    venue = venues.retrieve_venue_by_venue_id(venue_id=venue_id)
    user.update(add_to_set__venues=venue)


def remove_venue_from_user(user_id: str, venue_id: str) -> None:
    user = User.objects(user_id=user_id).get()
    venue = venues.retrieve_venue_by_venue_id(venue_id=venue_id)
    user.update(pull__venues=venue)


def update_user_language(user_id: str, language: str) -> None:
    user = User.objects(user_id=user_id).get()
    user.update(language=language)
