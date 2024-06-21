import pymongo
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
import tensorflow as tf
import socket
import pickle
import os


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["chatroomDB"]
collection = db["messages"]
signup_collection = db['signup']

# Load the model
with open(r'C:\Projects\Python projects\Chatroom\chatroom\models\tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

model = tf.keras.models.load_model(r'C:\Projects\Python projects\Chatroom\chatroom\models\model.h5')

@csrf_exempt
def register(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        name = signup_collection.find_one({'username':username})
        if not name:
            signup_collection.insert_one({'username': username})
        request.session['username'] = username
        return redirect('join')

    return render(request, 'register.html')


def str_split(s, n):
    result = ""
    for i in range(0, len(s), n):
        result += s[i:i+n] + '\n'
    return result.rstrip('\n')


@csrf_exempt
def room(request, room_id):
    if not request.session.get('username'):
        return redirect('register')

    if request.method == 'POST':
        username = request.session['username']
        message = request.POST.get('chat')
        is_ok = True
        input_text = [message]

        sequences = tokenizer.texts_to_sequences(input_text)

        X = tf.keras.preprocessing.sequence.pad_sequences(sequences, maxlen=400)

        predictions = model.predict(X)

        if predictions[0][1] > 0.50 and predictions[0][0] > 0.30 :
            is_ok = False
            return HttpResponse(f'You entered an offensive word,{predictions}')

        if username and message and is_ok:
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsocket.connect(('localhost', 55555))
            if len(message) > 30:
                message = str_split(message, 30)
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
