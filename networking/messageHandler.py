import threading
import json
import time

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
            time.sleep(0.1)
            if self.recv_buf.isEmpty():
                continue
            msg = self.recv_buf.pop()
            try:
                source_ip, source_port = msg['ip'], msg['port']
                msg = json.loads(msg['message'])
                agent = msg['agent']
                if agent == 'R1':
                    self.r1_queue.push(msg['direction'])
                if agent == 'B1':
                    self.b1_queue.push(msg['direction'])
                if agent == 'R2':
                    self.r2_queue.push(msg['direction'])
                if agent == 'B2':
                    self.b2_queue.push(msg['direction'])
            except Exception as e:
                self.logger.error(str(e))
