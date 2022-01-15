from mongoengine import Document, StringField


class Venue(Document):
    display_name = StringField()
    venue_id = StringField()

    def __eq__(self, obj):
        return isinstance(obj, Venue) and obj.venue_id == self.venue_id
