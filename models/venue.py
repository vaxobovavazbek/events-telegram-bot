from mongoengine import Document, StringField


class Venue(Document):
    display_name = StringField()
    venue_id = StringField()
