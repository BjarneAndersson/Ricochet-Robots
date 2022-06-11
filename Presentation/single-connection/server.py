import socket
import netifaces

import time

# AF_INET = IPv4
# SOCK_STREAM = TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip: str = netifaces.ifaddresses(netifaces.interfaces()[0])[netifaces.AF_INET][0]['addr']  # get local ip

server_socket.bind((server_ip, 0))  # bind to local ip with port 0 -> socket will search for a free port

port: int = server_socket.getsockname()[1]  # get auto assigned port

server_socket.listen()  # enable socket to receive incoming connection requests

print(f'Server Started\nIP: {server_ip} | Port: {port}\n')

while True:
    # accept new connection from a client
    client_socket, address = server_socket.accept()
    print(f"Connection from {address} has been established.")

    while True:
        try:
            # receive client request
            client_request: str = client_socket.recv(1024).decode()

            if client_request == 'GET time':
                # send client the encoded current time
                client_socket.send(str(time.time()).encode())
        except ConnectionResetError:  # detect if client closed connection
            print("Client closed connection")
            break

    client_socket.close()  # close connection to client
