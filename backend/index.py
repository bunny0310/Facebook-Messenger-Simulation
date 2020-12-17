from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify, make_response
import json
import redis
from flask_socketio import SocketIO, send, emit
import datetime, time
from sqlalchemy.orm.attributes import flag_modified

import importlib.util
from server.config import db

from server.models.index import User, Chat, Message
from server.schemas.index import UserSchema, ChatSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost:3306/db'
CORS(app) 
db.init_app(app)
with app.app_context():
    db.create_all()

# use local cache here
cache = {}

session = db.session
@app.route('/users')
def getUsers():
    if(cache.get('users') != None):
        print("getting from cache")
        return make_response(jsonify(cache['users']))
    users = User.query.all();
    usersSchema = UserSchema(many=True)
    users = usersSchema.dump(users)
    if  not('users' in cache.keys()):
        cache['users'] = []
    
    for user in users:
        cache['users'].append(user)
    
    return make_response(jsonify(users))


@app.route('/addUser', methods = ['POST'])
def addUser():
    users = None
    data = request.get_json()
    userSchema = UserSchema()
    user = userSchema.load(data)
    if cache.__contains__('users') :
        users = cache.get('users')
    
    userSaved = user.create()
    result = userSchema.dump(userSaved)

    if users != None:
        users = json.loads(users)
        print(type(users))
        users.append(userSaved.as_dict())
        cache.set('users', json.dumps(users))

    return make_response(jsonify({"user": result}),200)

@app.route('/getFriends', methods = ['POST'])
def getFriends():
    data = request.get_json()
    email = data['email']
    users = User.query.filter(User.email == email).all()
    if len(users) is not 1:
        return make_response(jsonify({"message": "user not found."}))
    
    user = users[0]
    usersSchema = UserSchema(many=True)
    friends = usersSchema.dump(user.friends)
    # print(type(friends))
    return make_response(jsonify(friends))

@app.errorhandler(401)
def unauthorized():
    response = jsonify({'message':'Invalid login details'})
    return response, 401

@app.route('/login', methods = ['POST'])
def login():
    data = request.get_json()
    user = User.query.filter(User.email == data['email']).filter(User.password == data['password']).all()
    for u in user:
        print(u.as_dict())
    if(len(user) is not 1):
        return unauthorized()
    
    return make_response(jsonify({"authenticated" : True, "email" : data['email']}))


@app.route('/getChats', methods = ['POST'])
def getChats():
    data = request.get_json()
    user = User.query.filter(User.email == data['email']).one()
    chats = user.chats
    chatUsers = []
    for chat in chats:
        usersInvolved = chat.users
        obj = {}
        for userInvolved in usersInvolved:
            if userInvolved.email != data['email']:
                obj['user'] = userInvolved.as_dict()
                break
        
        obj['cid'] = chat.cid
        chatUsers.append(obj)
    
    print(chatUsers)
    return make_response(jsonify(chatUsers))

@app.route('/loadMessages', methods = ['POST'])
def loadMessages():
    data = request.get_json()
    if not ('cid' in data):
        return jsonify({"message": "incorrectly formated data"})

    cid = data['cid']
    chat = Chat.query.get(cid)
    if chat is None:
        return jsonify({"message": "chat not found!"})
    
    messages = [message.as_dict() for message in chat.messages]
    return make_response(jsonify(messages))

@app.route('/sendMessage', methods = ['POST'])
def sendMessage():
    data = request.get_json()
    if not ('cid' in data) or not ('message' in data) or not('userEmail' in data):
        return jsonify({"message": "incorrectly formated data"})
    
    user = User.query.filter(User.email == data['userEmail']).one()
    if user is None:
       return jsonify({"message": "user not found"})

    chat = Chat.query.get(data['cid'])
    if chat is None:
           return jsonify({"message": "chat not found"})
    
    message = Message()
    message.cid = chat.cid
    message.uid = user.uid
    message.content = {"text": data['message']}


    saved = True
    db.session.add(message)
    saved = db.session.commit()

    return make_response(json.dumps({'user': (user.as_dict()), 'content': (message.content), 'createdAt': str(datetime.datetime.now())}))


@app.route('/updateChatTimestamp', methods=['POST'])
def updateChatTimestamp():
    data = request.get_json()
    cid = data['cid']
    chat = Chat.query.get(cid)
    if chat is None:
        return make_response(jsonify({"message" : "chat not found"}))
    
    userEmail = data['userEmail']
    user = User.query.filter(User.email == userEmail).all()
    if len(user) != 1:
        return make_response(jsonify({"message" : "user not found"}))
    
    chat.progressUsers[str(user[0].uid)] = str(datetime.datetime.now())
    flag_modified(chat, "progressUsers")
    db.session.add(chat)
    print(chat.as_dict())
    db.session.commit()

    return make_response(jsonify({"message" : "success"}))

@app.route('/getUserLastProgress', methods=['POST'])
def getUserLastProgress():
    data = request.get_json()
    cid = data['cid']
    email = data['email']
    chat = Chat.query.get(cid)
    if chat is None:
        return make_response(jsonify({"message" : "chat not found"}))

    user = User.query.filter(User.email == email).all()
    if len(user) != 1:
        return make_response(jsonify({"message" : "user not found"}))
    
    return make_response({"timestamp": chat.progressUsers[str(user[0].uid)]})

