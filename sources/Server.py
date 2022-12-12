import socket
import threading

class Server(threading.Thread):
    def __init__(self, host_addr):
        threading.Thread.__init__(self)
        self.in_bound = [] # list of node send us connection request
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(host_addr)
        self.server_socket.listen()

    def get_connection(self):
        while True:
            self.server_socket.settimeout(1)
            try:
                conn, addr = self.server_socket.accept()
            except socket.error as error:
                continue

            try:
                init_connection_sequence_recieve = str(
                    conn.recv(1024).decode("utf-8"))
                init_connection_sequence_recieve = eval(init_connection_sequence_recieve)
                peer_name = init_connection_sequence_recieve["host_name"]
                peer_ip = init_connection_sequence_recieve["host_ip"]
                peer_port = init_connection_sequence_recieve["host_port"]
                self.in_bound.append(((peer_name, peer_ip, peer_port), conn))
                #print("get from client " + str(self.in_bound))
            except socket.error as error:
                print(error)
                continue
    def handle_client(self):
        while True:
            for item in self.in_bound:
                item[1].settimeout(1)
                try:
                    request = str(item[1].recv(1).decode("utf-8"))
                    if request == "o":
                        online_list = []
                        for i in self.in_bound:
                            if i[0] != item[0]:
                                online_list.append(i[0])
                        online_list = str(online_list)
                        item[1].send(online_list.encode("utf-8"))
                    if request == "e":
                        self.in_bound.remove(item)
                except socket.error as error:
                    continue

    def run(self):
        self.get_connection()