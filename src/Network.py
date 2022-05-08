import pickle
import socket
import sys


class Network:

    def __init__(self, ip_server: str, port_server: int):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = ip_server
        self.port = port_server
        self.address = (self.server, self.port)
        self.player_id = int(self.connect())

    def get_player_id(self):
        return self.player_id

    def connect(self):
        try:
            self.client.connect(self.address)
            return self.client.recv(2048 * 1).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))

            data = self.client.recv(4096 * 8)

            try:
                return pickle.loads(data)
            except pickle.UnpicklingError as e:
                return data.decode()

        except OSError as e:
            print(e)
