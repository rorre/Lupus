from umongo import Document, fields

from .Connection import mongo


@mongo.register
class Reminder(Document):
    user_id = fields.IntField(required=True)
    message_id = fields.IntField(required=True)
    channel_id = fields.IntField(required=True)
    content = fields.StringField()
    datetime = fields.DateTimeField()
