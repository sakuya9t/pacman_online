import threading
import time
import json


class Sequencer(threading.Thread):
    def __init__(self, r1_hold_q, r2_hold_q, b1_hold_q, b2_hold_q, conn):
        super(Sequencer, self).__init__()
        self.r1_hold_q = r1_hold_q
        self.r2_hold_q = r2_hold_q
        self.b1_hold_q = b1_hold_q
        self.b2_hold_q = b2_hold_q
        self.conn = conn
        self.g_seq = 0
        self.pre_r1_head = ""
        self.pre_r2_head = ""
        self.pre_b1_head = ""
        self.pre_b2_head = ""

    def run(self):
        while True:
            time.sleep(0.1)
            if (len(self.r1_hold_q.list) > 0 and len(self.r2_hold_q.list) > 0 and
                    len(self.b1_hold_q.list) > 0 and len(self.b2_hold_q.list) > 0):
                r1_head = self.r1_hold_q.list[0]    # a tuple (msg_count, key)
                r2_head = self.r2_hold_q.list[0]
                b1_head = self.b1_hold_q.list[0]
                b2_head = self.b2_hold_q.list[0]

                # start new round if all the previous head are pop
                if (self.pre_r1_head != r1_head and self.pre_r2_head != r2_head and
                        self.pre_b1_head != b1_head and self.pre_b2_head != b2_head):
                    self.pre_r1_head = r1_head
                    self.pre_r2_head = r2_head
                    self.pre_b1_head = b1_head
                    self.pre_b2_head = b2_head

                    # clear garbage message
                    self.r1_hold_q.list = [r1_head]
                    self.r2_hold_q.list = [r2_head]
                    self.b1_hold_q.list = [b1_head]
                    self.b2_hold_q.list = [b2_head]

                    # TODO multicast to all other players, just send to one socket for now....
                    self.conn.sendall(json.dumps(
                        {"command": "order", "msg_id": ("R1", r1_head[0]), "group_sequence": self.g_seq}))
                    self.g_seq += 1

                    self.conn.sendall(json.dumps(
                        {"command": "order", "msg_id": ("R2", r2_head[0]), "group_sequence": self.g_seq}))
                    self.g_seq += 1

                    self.conn.sendall(json.dumps(
                        {"command": "order", "msg_id": ("B1", b1_head[0]), "group_sequence": self.g_seq}))
                    self.g_seq += 1

                    self.conn.sendall(json.dumps(
                        {"command": "order", "msg_id": ("B2", b2_head[0]), "group_sequence": self.g_seq}))
                    self.g_seq += 1
