import pymongo
from django.shortcuts import render, redirect
import socket

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["chatroomDB"]
collection = db["messages"]

# Initialize collection with a document containing an empty list for messages
def initialize_collection():
    if collection.count_documents({}) == 0:
        collection.insert_one({'messages': []})

initialize_collection()

# View function to handle chat messages
def room(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        message = request.POST.get('chat')
        if username and message:
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsocket.connect(('localhost', 55555))
            clientsocket.send(f"{username}: {message}".encode('utf-8'))
            clientsocket.close()

            collection.update_one({}, {'$push': {'messages': {'username': username, 'text': message}}})

        return redirect('room')

    # Retrieve messages from the collection
    messages = collection.find_one({})['messages']

    return render(request, 'room.html', {'messages': messages})
