from mongoengine import connect

from bot.settings import MONGODB_URI
from models.user import User

db = connect(host=MONGODB_URI)


def register_user(user_id: str, username: str, first_name: str, last_name: str) -> None:
    User.objects(user_id=user_id).update_one(upsert=True, username=username, first_name=first_name, last_name=last_name,
                                             is_active=True)


def unregister_user(user_id: str) -> None:
    User.objects(user_id=user_id).update_one(is_active=False)
