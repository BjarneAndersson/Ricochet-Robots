import selectors
import types
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

# ----------------------------------------------------------------------------------------------------------------------

selector = selectors.DefaultSelector()
selector.register(server_socket, selectors.EVENT_READ, data=None)


def accept_wrapper(sock):
    connection, address = sock.accept()  # accept new connection from a client
    print(f"Accepted connection from {address}")

    connection.setblocking(False)

    # clear default data of connection
    data = types.SimpleNamespace(addr=address, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE  # declare connection as read and write

    selector.register(connection, events, data=data)  # register connection


def service_connection(key, mask):
    connection = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:  # if connection is registered as read
        recv_data = connection.recv(1024).decode()  # read incoming data
        if recv_data:
            if recv_data == 'GET time':
                # add current time to data that is going to be sent
                data.outb = str(time.time()).encode(encoding='utf-8')
        else:
            print(f"Closing connection to {data.addr}")
            selector.unregister(connection)
            connection.close()
    if mask & selectors.EVENT_WRITE:  # if connection is registered as write
        if data.outb:
            sent = connection.send(data.outb)  # sent a chunk of data to client
            data.outb = data.outb[sent:]  # update the data that still needs to be sent


while True:
    # get all sockets that have changed
    events = selector.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)  # new connection
        else:
            service_connection(key, mask)  # existing connection
