import threading
import socket
import time

import logger
from connectionThread import connectionThread
from util import Queue


class socketServer(threading.Thread):
    def __init__(self, serverID, port):
        super(socketServer, self).__init__()
        self.serverID = serverID
        self.port = port
        self.connection_pool = []
        self.message_queue = Queue()
        self.message_queue_thread = messageQueueThread(self.message_queue)
        self.conn_recycle_thread = connectionRecycleThread(self.connection_pool)
        self.conn_id = 0

    def run(self):
        self.message_queue_thread.start()
        self.conn_recycle_thread.start()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.port))
        server.listen(5)
        logger.info("Server listening on 0.0.0.0, port " + str(self.port))
        while True:
            connection, addr = server.accept()
            logger.info("connection detected")
            connection_thread = connectionThread(self.conn_id, connection, self.message_queue)
            connection_thread.start()
            self.conn_id += 1
            self.connection_pool.append(connection_thread)


class connectionRecycleThread(threading.Thread):
    def __init__(self, pool):
        super(connectionRecycleThread, self).__init__()
        self.pool = pool

    def run(self):
        while True:
            for thread in self.pool:
                if not thread.isAlive():
                    thread.join()
                    self.pool.remove(thread)
            logger.info(len(self.pool))
            time.sleep(1)


class messageQueueThread(threading.Thread):
    def __init__(self, queue):
        super(messageQueueThread, self).__init__()
        self.queue = queue

    def run(self):
        while True:
            if self.queue.isEmpty():
                continue
            else:
                msg = self.queue.pop()
                logger.info(msg)


if __name__ == '__main__':
    server = socketServer(0, 8080)
    server.start()