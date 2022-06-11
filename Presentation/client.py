import socket

import time

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address: dict = {
    'ip': input("IP-Server: "),
    'port': int(input("Port-Server: "))
}

client_socket.connect((server_address['ip'], server_address['port']))

for _ in range(10):
    client_socket.send(str.encode("GET time"))  # send server request: GET time
    msg: str = client_socket.recv(1024).decode("utf-8")  # receive server response

    print(msg)
    time.sleep(1)

client_socket.close()
