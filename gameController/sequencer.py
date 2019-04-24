import threading
import time
import json

MESSAGE_TYPE_CONTROL_AGENT = 'game_ctl'


class Sequencer(threading.Thread):
    def __init__(self, r1_hold_q, r2_hold_q, b1_hold_q, b2_hold_q, server):
        super(Sequencer, self).__init__()
        self.r1_hold_q = r1_hold_q
        self.r2_hold_q = r2_hold_q
        self.b1_hold_q = b1_hold_q
        self.b2_hold_q = b2_hold_q

        self.server = server
        self.g_seq = 0
        self.pre_r1_tail = ""
        self.pre_r2_tail = ""
        self.pre_b1_tail = ""
        self.pre_b2_tail = ""

    def run(self):
        while True:

            # try to get the tail of the holdback queue
            try:
                r1_tail = self.r1_hold_q.list[-1]    # a tuple (msg_count, key)
                r2_tail = self.r2_hold_q.list[-1]
                b1_tail = self.b1_hold_q.list[-1]
                b2_tail = self.b2_hold_q.list[-1]
                # start new round if all the previous tail are pop
                if (self.pre_r1_tail != r1_tail and self.pre_r2_tail != r2_tail and
                    self.pre_b1_tail != b1_tail and self.pre_b2_tail != b2_tail):
                    
                    self.pre_r1_tail = r1_tail
                    self.pre_r2_tail = r2_tail
                    self.pre_b1_tail = b1_tail
                    self.pre_b2_tail = b2_tail

                    self.send_ordered_message("R1", self.pre_r1_tail)
                    self.send_ordered_message("B1", self.pre_b1_tail)
                    self.send_ordered_message("R2", self.pre_r2_tail)
                    self.send_ordered_message("B2", self.pre_b2_tail)
            except Exception:
                continue

    def send_ordered_message(self, agent, value):
        message = {"agent": agent, "direction": value[1],
                   "server_info": {"ip": self.server.ip, "port": self.server.port},
                   "msg_count": value[0],
                   "group_sequence": self.g_seq}
        # self.server.sendToAllOtherPlayers(MESSAGE_TYPE_CONTROL_AGENT, message)
        self.server.recv_queue.push(self.makeFakeControlMessage(message))
        self.g_seq += 1

    def makeFakeControlMessage(self, message):
        return {'ip': 'me', 'port': 'me', 'message': json.dumps({'type': MESSAGE_TYPE_CONTROL_AGENT, 'msg': message})}
