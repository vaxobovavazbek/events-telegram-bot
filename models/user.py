from mongoengine import Document, StringField, ReferenceField, ListField

from bot import settings
from models.venue import Venue


class User(Document):
    user_id = StringField(required=True)
    username = StringField(null=True)
    first_name = StringField(null=True)
    last_name = StringField(null=True)
    venues = ListField(ReferenceField(Venue))
    language = StringField(default=settings.DEFAULT_LOCALE)
