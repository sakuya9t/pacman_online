import socket
import threading
import time


class connectionThread(threading.Thread):
    def __init__(self, conn_id, connection, server, logger):
        super(connectionThread, self).__init__()
        self.connection = connection
        self.connection.settimeout(1)
        self.recv_queue = server.recv_queue
        self.send_queue = server.send_queue
        self.id = conn_id
        self.removeNodeMap = server.removeNodeMap
        self.client_ip, self.client_port = self.connection.getpeername()
        self.logger = logger
        self.alive = True

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
        self.connection.sendall(message)

    def complete_callback(self):
        self.removeNodeMap(self.client_ip, self.client_port)
        self.logger.warning("Connection with {ip}:{port} terminated."
                            .format(ip=self.client_ip, port=self.client_port))

    def join(self, timeout=None):
        self.alive = False
        threading.Thread.join(self, timeout)
