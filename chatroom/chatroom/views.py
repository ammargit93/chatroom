import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
import socket
import json

def open_json():
    with open('messages.json', 'r') as f:
        data = json.dump(f)


def room(request):
    messages = []
    if request.method == 'POST':
        message = request.POST.get('chat')
        messages.append(message)
        if message:
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsocket.connect(('localhost', 55555))
            clientsocket.send(message.encode('utf-8'))
            clientsocket.close()
    return render(request, 'room.html', {'messages.json' : messages})
