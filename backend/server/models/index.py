from ..config import db
from sqlalchemy.orm import relationship
from sqlalchemy import select
from ..associations.associations import userChats
from ..associations.associations import contacts
from sqlalchemy.dialects.mysql import JSON

class User(db.Model):
    __tablename__ = "users"
    uid = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    email = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255))
    createdAt = db.Column(db.DateTime, server_default=db.func.now())
    friends = relationship('User', secondary = contacts,
    primaryjoin=(uid == contacts.c.uid),
    secondaryjoin=(uid == contacts.c.fid),
    )
    chats = relationship("Chat", secondary=userChats, back_populates='users')

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self
    
    def befriend(self, friend):
        if friend not in self.friends:
            self.friends.append(friend)
            friend.friends.append(self)
    
    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class Chat(db.Model):
    __tablename__ = "chats"
    cid = db.Column(db.Integer, primary_key=True)
    progressUsers = db.Column(JSON)
    createdAt = db.Column(db.DateTime, server_default=db.func.now())
    users = relationship("User", secondary='userChats', back_populates='chats')
    messages = db.relationship("Message", backref="chats")

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}




class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    cid = db.Column(db.Integer, db.ForeignKey('chats.cid'))
    content = db.Column(JSON)
    createdAt = db.Column(db.DateTime, server_default=db.func.now())
    chat = db.relationship('Chat')
    user = db.relationship('User')

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self

    def as_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d['user'] = self.user.as_dict()
        return d