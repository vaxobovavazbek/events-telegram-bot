from typing import List

from mongoengine import connect

from bot.settings import MONGODB_URI
from models.user import User

db = connect(host=MONGODB_URI)


def add_user(user_id: str, username: str, first_name: str, last_name: str, venue: str) -> None:
    User.objects(user_id=user_id).update_one(upsert=True, username=username, first_name=first_name, last_name=last_name,
                                             is_active=True, venues=[venue])


def remove_user(user_id: str) -> None:
    User.objects(user_id=user_id).update_one(is_active=False)


def retrieve_all_active_users() -> List[User]:
    return User.objects.filter(is_active=True)


def user_exists(user_id: str) -> bool:
    return User.objects(user_id=user_id).count() == 1


def add_venue_to_user(user_id: str, venue: str) -> None:
    user = User.objects(user_id=user_id).get()
    if venue not in user.venues:
        user.venues.append(venue)
        user.save()


def remove_venue_from_user(user_id: str, venue: str) -> None:
    user = User.objects(user_id=user_id).get()
    if venue in user.venues:
        user.venues.remove(venue)
        user.save()
