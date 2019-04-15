import threading
import time
import logger


class connectionThread(threading.Thread):
    def __init__(self, conn_id, connection, recv_queue, send_queue):
        super(connectionThread, self).__init__()
        self.connection = connection
        self.recv_queue = recv_queue
        self.send_queue = send_queue
        self.id = conn_id
        self.client_ip, self.client_port = self.connection.getpeername()

    def run(self):
        # do something
        while True:
            try:
                message = self.connection.recv(4096)
                if not message:
                    break
                self.recv_queue.push({"ip": self.client_ip, "port": self.client_port, "message": message})
                self.send_queue.push({"ip": self.client_ip, "port": self.client_port, "message": "I received your message."})
            except Exception as e:
                logger.error(str(e))
                break
        self.complete_callback()
        self.connection.close()

    def send(self, message):
        self.connection.sendall(message)

    def complete_callback(self):
        self.recv_queue.push("Client {ip}:{port} disconnected.".format(ip=self.client_ip, port=self.client_port))