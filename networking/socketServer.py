import threading
import socket
import time
import json

from logger import logger
from connectionThread import connectionThread
from networking.messageHandler import messageHandler
from networking.inputHandler import inputHandler
from util import Queue

RECEIVE_BUFFER = 0
SEND_BUFFER = 1
CONTROL_BUFFER = 2


class socketServer(threading.Thread):
    def __init__(self, serverID, bind_ip, port):
        super(socketServer, self).__init__()
        self.serverID = serverID
        self.ip = bind_ip
        self.port = port
        self.connection_pool = []
        self.send_queue = Queue()
        self.send_queue_thread = messageQueueThread(
            self.send_queue, SEND_BUFFER, self.connection_pool)
        self.recv_queue = Queue()
        self.message_handler = messageHandler(
            recv_buf=self.recv_queue, send_buf=self.send_queue, logger=logger)
        self.input_queue = Queue()
        # self.input_handler = inputHandler(self)
        self.conn_recycle_thread = connectionRecycleThread(self.connection_pool)
        self.conn_id = 0
        self.alive = True
        self.logger = logger

    def run(self):
        self.message_handler.start()
        self.send_queue_thread.start()
        # self.input_handler.start()
        self.conn_recycle_thread.start()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, self.port))
        server.listen(5)
        logger.info("Server listening on {ip}:{port}".format(ip=self.ip, port=self.port))
        while self.alive:
            connection, addr = server.accept()
            client_ip, client_port = addr
            logger.info("Detected connection from {ip}:{port}.".format(
                ip=client_ip, port=client_port))
            connection_thread = connectionThread(
                self.conn_id, connection, self.recv_queue, self.send_queue, logger)
            connection_thread.start()
            self.conn_id += 1
            self.connection_pool.append(connection_thread)

    def join(self, timeout=None):
        self.alive = False
        self.message_handler.join()
        for conn in self.connection_pool:
            conn.join()
        self.conn_recycle_thread.join()
        threading.Thread.join(self, timeout)


class connectionRecycleThread(threading.Thread):
    def __init__(self, pool):
        super(connectionRecycleThread, self).__init__()
        self.pool = pool
        self.alive = True

    def run(self):
        while self.alive:
            time.sleep(0.05)
            for thread in self.pool:
                if not thread.isAlive():
                    logger.info("Recycled thread for connection.")
                    thread.join()
                    self.pool.remove(thread)
            time.sleep(1)

    def join(self, timeout=None):
        self.alive = False


class messageQueueThread(threading.Thread):
    def __init__(self, queue, buf_type, pool):
        super(messageQueueThread, self).__init__()
        self.queue = queue
        self.type = buf_type
        self.pool = pool
        self.alive = True

    def run(self):
        while self.alive:
            time.sleep(0.05)
            if self.queue.isEmpty():
                continue
            msg = self.queue.pop()
            target_addr = (msg['ip'], msg['port'])
            target_conn = list(
                filter(lambda x: (x.client_ip, x.client_port).__eq__(target_addr), self.pool))
            if len(target_conn) == 1:
                target_conn[0].send(json.dumps(msg))
            logger.info("Send message: {msg}".format(msg=msg))

    def join(self, timeout=None):
        self.alive = False


def generateServerID(port_num):
    timestamp = str(int(time.time()))
    return "{port},{timestamp}".format(port=port_num, timestamp=timestamp)


if __name__ == '__main__':
    from networking.inputHandler import inputHandler
    server = socketServer(0, "0.0.0.0", 8080)
    input_handler = inputHandler(server)
    server.start()
    input_handler.start()
