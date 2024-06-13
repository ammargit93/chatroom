import pymongo
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId  # Import ObjectId for converting room_id
import socket

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["chatroomDB"]
collection = db["messages"]
signup_collection = db['signup']


@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        signup_collection.insert_one({'username': username})
        request.session['username'] = username
        return redirect('join')
    return render(request, 'register.html')


@csrf_exempt
def room(request, room_id):
    if not request.session.get('username'):
        return redirect('register')

    if request.method == 'POST':
        username = request.session['username']
        message = request.POST.get('chat')

        if username and message:
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsocket.connect(('localhost', 55555))
            clientsocket.send(f"{username}: {message}".encode('utf-8'))
            clientsocket.close()

            # Convert room_id to ObjectId
            collection.update_one({'_id': ObjectId(room_id)}, {'$push': {'messages': {'username': username, 'text': message}}})

        return redirect('room', room_id=room_id)

    messages = collection.find_one({'_id': ObjectId(room_id)})['messages']
    return render(request, 'room.html', {'messages': messages})


@csrf_exempt
def join(request):
    if request.method == 'POST':
        if 'room_name' in request.POST:
            roomname = request.POST.get('room_name')
            if collection.count_documents({'room_name': roomname}) == 0:
                collection.insert_one({'room_name': roomname, 'messages': []})
                return redirect('room', room_id=str(collection.find_one({'room_name': roomname})['_id']))  # Redirect to the newly created room

    rooms = list(collection.find({}))
    for room in rooms:
        room['id'] = str(room['_id'])
    return render(request, 'join.html', {'rooms': rooms})
