import threading
import time
import logger


class connectionThread(threading.Thread):
    def __init__(self, conn_id, connection, msg_queue):
        super(connectionThread, self).__init__()
        self.connection = connection
        self.msg_queue = msg_queue
        self.id = conn_id

    def run(self):
        # do something
        while True:
            message = self.connection.recv(4096)
            if not message:
                break
            self.msg_queue.push(message)
        self.complete_callback()
        self.connection.close()

    def complete_callback(self):
        self.msg_queue.push("COMPLETED " + str(self.id))