from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify, make_response
import json
import redis
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
import datetime, time
import socketio
import requests

# dictionaries to maintain in redis
# map email to sid - for keeping a track of heartbeats
# map sid to email - for keeping a track of whether the user if offline or not
# map sid to email - for keeping a track of which user is currently selected


sio = socketio.Server()
app = Flask(__name__)
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")
r = redis.Redis(host='localhost', port=6379, db=0)


if __name__ == '__main__':
    app.run()


@socketio.on('store-session')
def storeSession(email):
    print("Client connected - " + request.sid)
    #map the connected users sid to email - for keeping a track of user's online status
    if r.exists('mapIdEmail'):
        d = json.loads(r.get('mapIdEmail'))
        d[request.sid] = email
        r.set('mapIdEmail', json.dumps(d))
    else:
        d = {
            request.sid: email
        }
        r.set('mapIdEmail', json.dumps(d))

    # map the connected users email to sid
    if r.exists('sessions-sockets'):
        d = json.loads(r.get('sessions-sockets'))
        if(email in d):
            d[email].append(request.sid);
        else:
            d[email] = [request.sid]
        r.set('sessions-sockets', json.dumps(d))
    else:
        d = {
            email: [request.sid]
        }
        r.set('sessions-sockets', json.dumps(d))
    
    #store heartbeat
    while(r.exists('mapIdEmail') and request.sid in json.loads(r.get('mapIdEmail'))):
        if not(r.exists('heartbeats')):
            d = {
            email: {
                'timestamp': str(datetime.datetime.now()),
                'online': True 
            }}
            r.set('heartbeats', json.dumps(d))
        else:
            d = json.loads(r.get('heartbeats'))
            d[email] = {
                'timestamp': str(datetime.datetime.now()),
                'online': True 
            }
            r.set('heartbeats', json.dumps(d))
        time.sleep(5);
    
    print("storing heartbeat for " + email)


@socketio.on('lastSeen')
def handle_lastseen(body):
    body = json.loads(body)
    # map the connected users email to sid - for closing the previous chat channel 
    if r.exists('lastSeenRequests'):
        d = json.loads(r.get('lastSeenRequests'))
        if (request.sid in d):
            d[request.sid].append(body['recipientEmail'])
        else:
            d[request.sid] = [body['recipientEmail']]
        r.set('lastSeenRequests', json.dumps(d))
    else:
        d = {
            request.sid : [body['recipientEmail']]
        }
        r.set('lastSeenRequests', json.dumps(d))
    
    while(request.sid in json.loads(r.get('lastSeenRequests')) and body['recipientEmail'] in json.loads(r.get('lastSeenRequests'))[request.sid]):
        # print("This one should keep happening every second")
        print("getting heartbeat for " + body['recipientEmail'])
        print(json.loads(r.get('heartbeats'))[body['recipientEmail']])
        emit('new-message', json.loads(r.get('heartbeats'))[body['recipientEmail']], json=True)
        req = requests.post('http://localhost:5000/getUserLastProgress', json={"cid": body['cid'], "email": body['recipientEmail']})
        emit('read-receipt', req.json(), json=True)
        time.sleep(10)

@app.route('/sendMessage', methods = ['POST'])
def sendMessage():
    data = request.get_json()
    if not('email' in data) or not ('message' in data) or not ('cid' in data) or not ('recipientEmail' in data):
        return jsonify({"message" : "incorrect format"})
    
    email = data['email']
    
    message = data['message']

    req = requests.post('http://localhost:5000/sendMessage', json={"cid": data['cid'], "userEmail": data['email'], "message": data['message']})
    sid1 = json.loads(r.get('sessions-sockets'))[email]
    sid2 = json.loads(r.get('sessions-sockets'))[data['recipientEmail']]
    socketio.emit('message', req.json(), room=sid1)
    socketio.emit('message', req.json(), room=sid2)

    return make_response(jsonify({"message" : "success"}))
    

@socketio.on('disconnect')
def test_disconnect():
    sessionId  = request.sid
    print("Client disconnected - " + sessionId)
    if(r.exists('mapIdEmail')):
        d = json.loads(r.get('mapIdEmail'))
        email = d[request.sid]
        d.pop(request.sid, None) 
        r.set('mapIdEmail', json.dumps(d))

        # update the heartbeat
        if(email is not None):
            heartbeatMap = json.loads(r.get('heartbeats'))
            heartbeatMap[email] = {
            'timestamp': str(datetime.datetime.now()),
            'online': False 
            }
            r.set('heartbeats', json.dumps(heartbeatMap))
    
    if(request.sid in json.loads(r.get('lastSeenRequests'))):
        d = json.loads(r.get('lastSeenRequests'))
        d.pop(request.sid, None)
        r.set('lastSeenRequests', json.dumps(d))

@socketio.on('closePrevChat')
def closePreviousChatChannel(message):
    # print('channel being closed is ' + message)
    if(request.sid in json.loads(r.get('lastSeenRequests'))):
        d = json.loads(r.get('lastSeenRequests'))
        print('previous chat .... ', d[request.sid])
        d[request.sid] = []
        r.set('lastSeenRequests', json.dumps(d))   


@app.route('/updateChatTimestamp', methods=['POST'])
def updateChatTimestamp():
    data = request.get_json()
    req = requests.post('http://localhost:5000/updateChatTimestamp', json={"cid": data['cid'], "userEmail": data['userEmail']})

    return make_response(jsonify({"message" : req.json()}))

if __name__ == '__main__':
    socketio.run(app) 