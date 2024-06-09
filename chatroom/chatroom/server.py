import socket
import threading

clients = []

def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            # Handle clients that have disconnected
            clients.remove(client)

def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                break  # Client has closed the connection
            print(f'Received message: {message}')
            broadcast(message)  # Broadcast the received message to all clients
        except ConnectionResetError:
            break  # Handle client disconnecting abruptly
    client.close()  # Close the client socket
    clients.remove(client)  # Remove the client from the list

# Server setup
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 55555))
serversocket.listen(5)
print('Server is listening on port 55555')

try:
    while True:
        clientsocket, addr = serversocket.accept()
        print(f'Connection from {addr}')
        clients.append(clientsocket)  # Add the new client to the list
        thread = threading.Thread(target=handle, args=(clientsocket,))
        thread.start()
except KeyboardInterrupt:
    print('Server is shutting down...')
finally:
    serversocket.close()
