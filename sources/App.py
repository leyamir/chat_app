from Server import Server
from Client import Client
from threading import Thread
import socket
import os


def content_file(str):
    for i in range(len(str)):
        if str[i] == ":":
            str = str[i+1:]
            return str


class Peer(Server, Client, Thread):
    def __init__(self, host_ip, host_port, host_name, lock):
        self.host_name = host_name
        self.host_ip = host_ip
        self.host_port = host_port
        self.host_addr = (str(host_ip), int(host_port))
        Server.__init__(self, self.host_addr)
        Client.__init__(self)
        Thread.__init__(self)
        self.terminate = False
        self.message_history = []
        self.lock = lock
        self.online_user = []
        self.kind = "message"
        try:
            os.mkdir(host_name)
        except:
            pass

    def debug(self, flag):
        if flag == 1:
            # print("here")
            for item in self.in_bound:
                print(item)
        if flag == 2:
            for item in self.out_bound:
                print(item)

    def get_connection(self):
        self.server_socket.settimeout(1)
        try:
            conn, addr = self.server_socket.accept()
            init_connection_sequence_send = "{" + \
                f"\'host_name\': \'{self.host_name}\', " +  \
                f"\'host_ip\': \'{self.host_ip}\', " +  \
                f"\'host_port\': {self.host_port}" + \
                "}"
            conn.send(init_connection_sequence_send.encode("utf-8"))
            init_connection_sequence_recieve = str(
                conn.recv(1024).decode("utf-8"))
            init_connection_sequence_recieve = eval(
                init_connection_sequence_recieve)
            peer_name = init_connection_sequence_recieve["host_name"]
            peer_ip = init_connection_sequence_recieve["host_ip"]
            peer_port = init_connection_sequence_recieve["host_port"]
            self.in_bound.append(((peer_name, peer_ip, peer_port), conn))
        except:
            return

    def connect_to(self, ip_port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.client_socket.settimeout(4)
        try:
            client_socket.connect(ip_port)
            init_connection_sequence_recieve = str(
                client_socket.recv(1024).decode("utf-8"))
            init_connection_sequence_recieve = eval(
                init_connection_sequence_recieve)
            peer_name = init_connection_sequence_recieve["host_name"]
            peer_ip = init_connection_sequence_recieve["host_ip"]
            peer_port = init_connection_sequence_recieve["host_port"]
            init_connection_sequence_send = "{" + \
                f"\'host_name\': \'{self.host_name}\', " +  \
                f"\'host_ip\': \'{self.host_ip}\', " +  \
                f"\'host_port\': {self.host_port}" + \
                "}"
            client_socket.send(init_connection_sequence_send.encode("utf-8"))
            self.out_bound.append(
                ((peer_name, peer_ip, peer_port), client_socket))
        except:
            client_socket.close()
        return

    def connect_to_server(self, ip_port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            client_socket.connect(ip_port)
            init_connection_sequence_send = "{" + \
                f"\'host_name\': \'{self.host_name}\', " +  \
                f"\'host_ip\': \'{self.host_ip}\', " +  \
                f"\'host_port\': {self.host_port}" + \
                "}"
            client_socket.send(init_connection_sequence_send.encode("utf-8"))
            self.out_bound.append((('SERVER', ip_port), client_socket))
        except:
            client_socket.close()
        return

    def send_to_peer(self, peer_name, content):
        for item in self.in_bound:
            if item[0][0] == peer_name:
                item[1].send(content.encode("utf-8"))
                return
        for item in self.out_bound:
            if item[0][0] == peer_name:
                item[1].send(content.encode("utf-8"))
                return
        return "not found"

    def get_message_from_peer(self, lock):
        for item in self.in_bound:
            item[1].settimeout(1)
            try:
                message = item[1].recv(1024).decode("utf-8")
                if message:
                    if message == "SENDING":
                        self.kind = "txt"
                        item[1].send("RECEIVED SIGNAL")
                    else:
                        content = "[ " + str(item[0][0]) + " ]  " + \
                            str(message) + "\n\n"
                        lock.acquire()
                        self.message_history.append(content)
                        lock.release()
                else:
                    self.in_bound.remove(item)
            except Exception as error:
                pass
        for item in self.out_bound:
            if item[0][0] != "SERVER":
                item[1].settimeout(1)
                try:
                    message = item[1].recv(1024).decode("utf-8")
                    if message:
                        if message == "SENDING":
                            self.kind = "txt"
                            item[1].send("RECEIVED SIGNAL")
                        else:
                            content = "[ " + str(item[0][0]) + \
                                " ]    " + str(message) + "\n\n"
                            lock.acquire()
                            self.message_history.append(content)
                            lock.release()
                    else:
                        self.out_bound.remove(item)
                except Exception as error:
                    pass
        return

    def server_interact(self, command):
        if not self.terminate:
            if command == "online?":
                self.out_bound[0][1].send("o".encode("utf-8"))
                try:
                    recieve = str(self.out_bound[0][1].recv(
                        2048).decode("utf-8"))
                    self.online_user = eval(recieve)
                except:
                    return
        if command == "exit":
            self.out_bound[0][1].send("e".encode("utf-8"))
            return

    def connect_if_not(self, peer_name):
        for item in self.in_bound:
            if peer_name == item[0][0]:
                return True
        for item in self.out_bound:
            if peer_name == item[0][0]:
                return True
        for item in self.online_user:
            if peer_name == item[0]:
                peer_ip = str(item[1])
                peer_port = int(item[2])
                self.connect_to((peer_ip, peer_port))
        for item in self.in_bound:
            if peer_name == item[0][0]:
                return True
        for item in self.out_bound:
            if peer_name == item[0][0]:
                return True
        return False

    def send_file_to_peer(self, peer_name, content):
        content_of_file = content_file(content)
        print(content_file)
        signal = "SENDING"

        for item in self.in_bound:
            if item[0][0] == peer_name:
                item[1].send(signal.encode("utf-8"))
                
        for item in self.out_bound:
            if item[0][0] == peer_name:
                item[1].send(signal.encode("utf-8"))



        return "not found"

    def get_file_from_peer(self, lock):
        for item in self.in_bound:
            item[1].settimeout(1)
            try:
                message = item[1].recv(1024).decode("utf-8")
                if message:
                    content = "[ " + str(item[0][0]) + " ]  " + \
                        str(message) + "\n\n"
                    lock.acquire()
                    self.message_history.append(content)
                    lock.release()
                else:
                    self.in_bound.remove(item)
            except Exception as error:
                pass
        for item in self.out_bound:
            if item[0][0] != "SERVER":
                item[1].settimeout(1)
                try:
                    message = item[1].recv(1024).decode("utf-8")
                    if message:
                        content = "[ " + str(item[0][0]) + \
                            " ]    " + str(message) + "\n\n"
                        lock.acquire()
                        self.message_history.append(content)
                        lock.release()
                    else:
                        self.out_bound.remove(item)
                except Exception as error:
                    pass
        return

    def debug(self):
        print("in_bound: " + str(self.in_bound))
        print("out_bound: " + str(self.out_bound))

    def run(self):
        while not self.terminate:
            self.get_connection()
            if (self.kind == "message"):
                self.get_message_from_peer(lock=self.lock)
            elif (self.kind == "txt"):
                self.get_file_from_peer(lock=self.lock)
                self.kind = "message"
        print("exit")
        return
