import socket
import threading

clients = []


def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            clients.remove(client)


def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                break
            print(f'Received message: {message}')
            broadcast(message)
        except ConnectionResetError:
            break
    client.close()
    clients.remove(client)


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 55555))
serversocket.listen(5)
print('Server is listening on port 55555')

try:
    while True:
        clientsocket, addr = serversocket.accept()
        print(f'Connection from {addr}')
        clients.append(clientsocket)
        thread = threading.Thread(target=handle, args=(clientsocket,))
        thread.start()
except KeyboardInterrupt:
    print('Server is shutting down...')
finally:
    serversocket.close()
