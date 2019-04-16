import threading
import json

from util import Queue


class messageHandler(threading.Thread):
    def __init__(self, recv_buf, send_buf, logger):
        super(messageHandler, self).__init__()
        self.recv_buf = recv_buf
        self.send_buf = send_buf
        self.r1_queue = Queue()
        self.r2_queue = Queue()
        self.b1_queue = Queue()
        self.b2_queue = Queue()
        self.logger = logger

    def run(self):
        while True:
            if self.recv_buf.isEmpty():
                continue
            msg = self.recv_buf.pop()
            try:
                source_ip, source_port = msg['ip'], msg['port']
                msg = msg['message']
                msg = json.loads(msg)
                self.logger.info(msg)
            except Exception as e:
                self.logger.error(str(e))
