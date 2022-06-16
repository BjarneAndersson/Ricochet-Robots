import pickle
import socket
import timeit


class Network:

    def __init__(self, server_ip: str, server_port: int):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address: tuple = (server_ip, server_port)
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.address)
        except Exception as e:
            print(e)

    def send(self, data):
        send_data = data
        try:
            self.client.send(str.encode(send_data))
            t_recv_s = timeit.default_timer()
            recv_data = self.client.recv(4096 * 8)
            t_recv_e = timeit.default_timer()
            print(f"Time | recv: {t_recv_e - t_recv_s}")
            print(f"Data: {recv_data}")

            try:
                return pickle.loads(recv_data)
            except pickle.UnpicklingError as e:
                return recv_data.decode()

        except OSError as e:
            print(e)
