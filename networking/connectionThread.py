# COMP90020 Distributed Algorithms project
# Author: Zijian Wang 950618, Nai Wang 927209, Leewei Kuo 932975, Ivan Chee 736901

import socket
import threading
import time


class connectionThread(threading.Thread):
    """
    connectionThread is the thread used to maintain the socket with a client
    """
    def __init__(self, conn_id, connection, server, logger):
        super(connectionThread, self).__init__()
        self.connection = connection
        self.connection.settimeout(1)
        self.recv_queue = server.recv_queue
        self.send_queue = server.send_queue
        self.id = conn_id
        self.removeNodeMap = server.removeNodeMap
        self.electSequencer = server.electSequencer
        self.setDeath = server.setDeath
        self.client_ip, self.client_port = self.connection.getpeername()
        self.logger = logger
        self.alive = True
        self.crash = False

    def run(self):
        # do something
        while self.alive:
            try:
                message = self.connection.recv(4096)
                if not message:
                    break
                self.recv_queue.push({"ip": self.client_ip, "port": self.client_port,
                                      "message": message})
            except socket.timeout:
                if self.alive:
                    continue
                break
            except Exception as e:
                self.logger.error("Error in connection thread with {ip}:{port}: {err}"
                                  .format(ip=self.client_ip, port=self.client_port, err=str(e)))
                break
        self.connection.close()
        self.complete_callback()

    def send(self, message):
        try:
            self.connection.sendall(message)
        except Exception as e:
            self.logger.err("Send message error: " + str(e))

    def complete_callback(self):
        self.setDeath(self.client_ip, self.client_port)
        self.crash = True
        self.removeNodeMap(self.client_ip, self.client_port)
        if self.crash:
            self.electSequencer()  # start election when process crash
        self.logger.warning("Connection with {ip}:{port} terminated."
                            .format(ip=self.client_ip, port=self.client_port))

    def join(self, timeout=None):
        self.alive = False
        threading.Thread.join(self, timeout)
