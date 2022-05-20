import pickle
import socket


class Network:

    def __init__(self, server_ip: str, server_port: int):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address: tuple = (server_ip, server_port)
        self.player_id = int(self.connect())

        self.amount_data_send, self.amount_data_recv = 0, 0

    def get_player_id(self):
        return self.player_id

    def connect(self):
        try:
            self.client.connect(self.address)
            return self.client.recv(2048 * 1).decode()
        except Exception as e:
            print(e)

    def send(self, data):
        try:
            self.amount_data_send += len(str(data).encode())
            self.client.send(str.encode(data))

            data = self.client.recv(4096 * 8)
            self.amount_data_recv += len(data)

            try:
                return pickle.loads(data)
            except pickle.UnpicklingError as e:
                return data.decode()

        except OSError as e:
            print(e)
