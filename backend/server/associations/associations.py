from ..config import db

contacts = db.Table('contacts',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('uid', db.Integer, db.ForeignKey('users.uid'), primary_key = True),
    db.Column('fid', db.Integer, db.ForeignKey('users.uid'), primary_key = True)
)
userChats = db.Table('userChats',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('uid', db.Integer, db.ForeignKey('users.uid'), primary_key = True),
    db.Column('cid', db.Integer, db.ForeignKey('chats.cid'), primary_key = True),
)