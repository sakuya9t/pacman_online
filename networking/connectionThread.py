import threading
import time


class connectionThread(threading.Thread):
    def __init__(self, conn_id, connection, server, logger):
        super(connectionThread, self).__init__()
        self.connection = connection
        self.recv_queue = server.recv_queue
        self.send_queue = server.send_queue
        self.node_map = server.node_map
        self.id = conn_id
        self.client_ip, self.client_port = self.connection.getpeername()
        self.logger = logger

    def run(self):
        # do something
        while True:
            try:
                message = self.connection.recv(4096)
                if not message:
                    break
                self.recv_queue.push({"ip": self.client_ip, "port": self.client_port,
                                      "message": message})
            except Exception as e:
                self.logger.error("Error in connection thread with {ip}:{port}: {err}"
                                  .format(ip=self.client_ip, port=self.client_port, err=str(e)))
                break
        self.complete_callback()
        self.connection.close()

    def send(self, message):
        self.connection.sendall(message)

    def complete_callback(self):
        nodes = list(filter(
            lambda x: (x['client']['ip'] == self.client_ip and x['client']['port'] == self.client_port) or
                      (x['server']['ip'] == self.client_ip and x['server']['port'] == self.client_port),
            self.node_map))
        for node in nodes:
            try:
                self.node_map.remove(node)
                self.logger.info("Node map changed: {node_map}".format(node_map=self.node_map))
            except:
                continue
        self.logger.warning("Connection with {ip}:{port} terminated."
                            .format(ip=self.client_ip, port=self.client_port))
