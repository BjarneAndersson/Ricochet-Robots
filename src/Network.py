import pickle
import socket


class Network:

    def __init__(self, server_ip: str, server_port: int):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address: tuple = (server_ip, server_port)
        self.connect()

        self.amount_data_send, self.amount_data_recv = 0, 0

    def connect(self):
        try:
            self.client.connect(self.address)
        except Exception as e:
            print(e)

    def send(self, data):
        send_data = data
        try:
            self.amount_data_send += len(str(send_data).encode())
            self.client.send(str.encode(send_data))

            recv_data = self.client.recv(4096 * 8)
            self.amount_data_recv += len(recv_data)

            try:
                return pickle.loads(recv_data)
            except pickle.UnpicklingError as e:
                return recv_data.decode()

        except OSError as e:
            print(e)
