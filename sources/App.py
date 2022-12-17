from Server import Server
from Client import Client
from threading import Thread
import threading
import socket
import os


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
        self.filename = ""
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
        self.server_socket.settimeout(2)
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
            get_message_thread = Thread(target=self.get_message_from_peer, args=(
                self.lock, self.in_bound[-1])).start()
        except:
            return

    def connect_to(self, ip_port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
            get_message_thread = Thread(target=self.get_message_from_peer, args=(
                self.lock, self.out_bound[-1])).start()
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

    def send_to_peer(self, peer_name, content, type):
        if type == "text":
            for item in self.in_bound:
                if item[0][0] == peer_name:
                    item[1].send(content.encode("utf-8"))
                    return
            for item in self.out_bound:
                if item[0][0] == peer_name:
                    item[1].send(content.encode("utf-8"))
                    return
        elif type == "file":
            for item in self.in_bound:
                if item[0][0] == peer_name:
                    item[1].sendall(content)
                    return
            for item in self.out_bound:
                if item[0][0] == peer_name:
                    item[1].sendall(content)
                    return
        return

    def get_message_from_peer(self, lock, peer):
        while not self.terminate:
            peer[1].settimeout(3)
            try:
                message = peer[1].recv(1024).decode("utf-8")
                if message:
                    if message == "<START>":
                        get_filename_thread = Thread(
                            target=self.get_filename_from_peer(peer))
                        get_filename_thread.start()

                        get_file_thread = Thread(
                            target=self.get_file_from_peer(peer))
                        get_file_thread.start()
                    else:
                        display_content = "[ " + str(peer[0][0]) + " ]  " + \
                            str(message) + "\n\n"
                        lock.acquire()
                        self.message_history.append(display_content)
                        lock.release()
                else:
                    try:
                        self.in_bound.remove(peer)
                        self.out_bound.remove(peer)
                    except Exception as error:
                        pass

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

    def get_filename_from_peer(self, peer):
        peer[1].settimeout(1)

        try:
            self.filename = peer[1].recv(1024).decode("utf-8")
            print(self.filename)

        except Exception as e:
            print(e)
        return

    def get_file_from_peer(self, peer):
        file_byte = b""
        done = False
        peer[1].settimeout(1)

        while not done:
            try:
                data = peer[1].recv(1024)
                print(data)
                file_byte += data
                if file_byte[-5:] == b"<END>":
                    done = True

            except Exception as e:
                if file_byte[-5:] == b"<END>":
                    done = True
                print(e)
                continue
        file_byte = file_byte[:-5]
        print(peer[0][0])
        file = open(os.path.join(self.host_name, self.filename), "wb")
        file.write(file_byte)
        file.close()
        return

    def debug(self):
        print("in_bound: " + str(self.in_bound))
        print("out_bound: " + str(self.out_bound))

    def run(self):
        while not self.terminate:
            self.get_connection()
        print("exit")
        return
