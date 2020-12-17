from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from ..config import db
from ..models.index import User, Chat


class UserSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = User
        sqla_session = db.session
    firstName = fields.String(required=True)
    lastName = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)

class ChatSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Chat
        sqla_session = db.session
    progressUsers = fields.String(required=True)