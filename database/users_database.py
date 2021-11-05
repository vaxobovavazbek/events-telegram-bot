from typing import List

from mongoengine import connect

from bot.settings import MONGODB_URI
from models.user import User

db = connect(host=MONGODB_URI)


def add_user(user_id: str, username: str, first_name: str, last_name: str, venue_id: str) -> None:
    User(user_id=user_id, username=username, first_name=first_name, last_name=last_name).save()
    add_venue_to_user(user_id=user_id, venue_id=venue_id)


def retrieve_users_by_venue(venue_id: str) -> List[User]:
    return User.objects.filter(venues__in=[venue_id])


def user_exists(user_id: str) -> bool:
    return User.objects(user_id=user_id).count() == 1


def add_venue_to_user(user_id: str, venue_id: str) -> None:
    user = User.objects(user_id=user_id).get()
    user.update(add_to_set__venues=venue_id)


def remove_venue_from_user(user_id: str, venue_id: str) -> None:
    user = User.objects(user_id=user_id).get()
    user.update(pull__venues=venue_id)
