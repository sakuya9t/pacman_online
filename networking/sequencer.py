# COMP90020 Distributed Algorithms project
# Author: Zijian Wang 950618, Nai Wang 927209, Leewei Kuo 932975, Ivan Chee 736901

import threading
import time
import json

MESSAGE_TYPE_CONTROL_AGENT = 'game_ctl'


class Sequencer(threading.Thread):
    """
    The Sequencer class is responsible for the total ordering of agent control messages.
    The Sequencer will assign a group sequence number to every control messages and
    the processes will deliver the messages according to the group sequence number.
    """
    def __init__(self, seq_queue, server):
        super(Sequencer, self).__init__()
        self.seq_queue = seq_queue
        self.server = server
        self.g_seq = 0  # group sequence number
        self.alive = True

    def run(self):
        while self.alive:
            time.sleep(0.001)
            if not self.seq_queue.isEmpty():
                value = self.seq_queue.pop()
                self.sendOrderedMessage(value)

    # assign a group sequence to each message
    def sendOrderedMessage(self, value):
        message = {"msg_id": value,
                   "server_info": {"ip": self.server.ip, "port": self.server.port},
                   "group_sequence": self.g_seq}
        self.server.sendToAllOtherPlayers(MESSAGE_TYPE_CONTROL_AGENT, message)
        self.server.recv_queue.push(self.makeFakeControlMessage(message))
        self.g_seq += 1

    def makeFakeControlMessage(self, message):
        return {'ip': 'me', 'port': 'me', 'message': json.dumps({'type': MESSAGE_TYPE_CONTROL_AGENT, 'msg': message})}

    def resetGames(self):
        self.g_seq = 0

    def exit(self):
        self.alive = False