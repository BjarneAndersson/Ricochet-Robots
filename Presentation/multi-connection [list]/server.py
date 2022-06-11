import socket
import netifaces

import time

# AF_INET = IPv4
# SOCK_STREAM = TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get the IPv4-address of the local machine
server_ip: str = netifaces.ifaddresses(netifaces.interfaces()[0])[netifaces.AF_INET][0]['addr']

server_socket.bind((server_ip, 0))  # connect to local ip with port 0 -> socket will search for a free port

server_socket.listen()  # enable socket to listen to incoming connection requests

port: int = server_socket.getsockname()[1]

print(f'Server Started\nIP: {server_ip} | Port: {port}\n')

clients: list[socket] = []
while True:
    client_socket, address = server_socket.accept()  # accept new connection from a client
    print(f"Connection from {address} has been established.")
    clients.append(client_socket)

    for client in clients:
        try:
            client_request: str = client.recv(1024).decode()  # receive client request

            if client_request == 'GET time':
                # send client the encoded current time
                client.send(str(time.time()).encode())
        except ConnectionResetError:  # detect if client closed connection
            print("Client closed connection")
            client.close()
            continue

# Only performs for-loop if new connection happens
