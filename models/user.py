from mongoengine import Document, StringField, BooleanField


class User(Document):
    user_id = StringField(required=True)
    username = StringField(null=True)
    first_name = StringField(null=True)
    last_name = StringField(null=True)
    is_active = BooleanField(default=True)
