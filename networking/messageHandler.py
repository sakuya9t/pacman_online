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

        # holdback queue
        self.r1_hold_q = Queue()
        self.r2_hold_q = Queue()
        self.b1_hold_q = Queue()
        self.b2_hold_q = Queue()
        self.p_seq = 0  # process sequence number

    def run(self):
        while True:
            time.sleep(0.1)
            if self.recv_buf.isEmpty():
                continue
            msg = self.recv_buf.pop()
            try:
                source_ip, source_port = msg['ip'], msg['port']
                msg = json.loads(msg['message'])

                command = ""
                if 'command' in msg:
                    command = msg['command']
                if command == "holdback":
                    key = msg['key']
                    agent, msg_count = msg['msg_id']
                    if agent == 'R1':
                        self.r1_hold_q.push((msg_count, key))
                    elif agent == 'B1':
                        self.b1_hold_q.push((msg_count, key))
                    elif agent == 'R2':
                        self.r2_hold_q.push((msg_count, key))
                    elif agent == 'B2':
                        self.b2_hold_q.push((msg_count, key))
                elif command == "order":
                    agent, msg_count = msg['msg_id']
                    g_seq = msg['group_sequence']
                    # assume the messages from sequencer are ordered for now
                    if self.p_seq == g_seq:
                        self.order(agent, msg_count)
                        self.p_seq += 1
                    else:
                        pass

                else:
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

    def order(self, agent, msg_count):
        if agent == 'R1':
            id, key = self.r1_hold_q.pop()
            # delete garbage msg
            while id != msg_count:
                id, key = self.r1_hold_q.pop()
            # deliver msg
            if id == msg_count:
                self.r1_queue.push(key)
            else:
                self.logger.error("messageHandler error: message not in queue")
            self.logger.info("send agent:" + str(agent) + " id:" + str(id) + " key:" + str(key))
        if agent == 'B1':
            id, key = self.b1_hold_q.pop()
            while id != msg_count:
                id, key = self.b1_hold_q.pop()
            if id == msg_count:
                self.b1_queue.push(key)
            else:
                self.logger.error("messageHandler error: message not in queue")
            self.logger.info("send agent:" + str(agent) + " id:" + str(id) + " key:" + str(key))
        if agent == 'R2':
            id, key = self.r2_hold_q.pop()
            while id != msg_count:
                id, key = self.r2_hold_q.pop()
            if id == msg_count:
                self.r2_queue.push(key)
            else:
                self.logger.error("messageHandler error: message not in queue")
            self.logger.info("send agent:" + str(agent) + " id:" + str(id) + " key:" + str(key))
        if agent == 'B2':
            id, key = self.b2_hold_q.pop()
            while id != msg_count:
                id, key = self.b2_hold_q.pop()
            if id == msg_count:
                self.b2_queue.push(key)
            else:
                self.logger.error("messageHandler error: message not in queue")
            self.logger.info("send agent:" + str(agent) + " id:" + str(id) + " key:" + str(key))
