# COMP90020 Distributed Algorithms project
# Author: Zijian Wang 950618, Nai Wang 927209, Leewei Kuo 932975, Ivan Chee 736901
#
# This file contains the Server class of each nodes in the connections. It maintains
# all the threads and variables necessary for our system. It also is responsible for
# the message passing logic of our system.

import threading
import socket
import time
import json

from gameController.voteStateThread import voteStateThread
from logger import logger
from nodeMap import nodeMap
from connectionThread import connectionThread
from networking.messageHandler import messageHandler
from networking.inputHandler import inputHandler
from util import Queue
from sequencer import Sequencer

RECEIVE_BUFFER = 0
SEND_BUFFER = 1
CONTROL_BUFFER = 2

class socketServer(threading.Thread):
    """
    The server of each process.
    """
    def __init__(self, serverID, bind_ip, port):
        super(socketServer, self).__init__()
        self.serverID = serverID
        self.ip = bind_ip
        self.port = port
        self.global_state = None
        self.display = None
        self.connection_pool = []
        self.node_map = nodeMap()
        self.send_queue = Queue()
        self.send_queue_thread = messageSendingQueueThread(self.send_queue, SEND_BUFFER, self.connection_pool)
        self.recv_queue = Queue()
        self.message_handler = messageHandler(server=self, recv_buf=self.recv_queue, send_buf=self.send_queue, logger=logger)
        self.input_queue = Queue()
        self.input_handler = inputHandler(self)
        self.conn_recycle_thread = connectionRecycleThread(self.connection_pool)
        self.conn_id = 0
        self.alive = True
        self.logger = logger
        self.role = ''
        self.sequencer = None
        self.vote_map = {}
        self.decision_map = {}
        # use lock to keep atomic I/O operations on the vote map.
        self.vote_map_lock = threading.Lock()
        self.vote_thread = voteStateThread(self.vote_map, self.decision_map,
                                           self.node_map, self.vote_map_lock, self.logger)
        self.sequencer_role = ''
        self.game = None
        self.role_map = None    # a dictionary, key is agent_role, value is agent_index
        # when a socket agent crash, change the corresponding life to False
        self.life_map = [True, True, True, True]

    def run(self):
        self.message_handler.start()
        self.send_queue_thread.start()
        self.conn_recycle_thread.start()
        self.input_handler.start()
        self.vote_thread.start()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, self.port))
        server.listen(5)
        logger.info("Server listening on {ip}:{port}".format(ip=self.ip, port=self.port))
        while self.alive:
            connection, addr = server.accept()
            self.passiveConnect(connection, addr)

    def activeConnect(self, ip, port):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.bind((self.ip, 0))
        conn.connect((ip, port))
        logger.info("Establishing active connection to {ip}:{port}.".format(ip=ip, port=port))
        connection_thread = connectionThread(self.conn_id, conn, self, logger)
        connection_thread.start()
        self.conn_id += 1
        self.connection_pool.append(connection_thread)

    def passiveConnect(self, connection, addr):
        client_ip, client_port = addr
        logger.info("Detected connection from {ip}:{port}.".format(ip=client_ip, port=client_port))
        connection_thread = connectionThread(self.conn_id, connection, self, logger)
        connection_thread.start()
        self.conn_id += 1
        self.connection_pool.append(connection_thread)

    def sendMsg(self, addr, msg_type, msg):
        target_ip, target_port = addr
        msg_packet = {'ip': target_ip, 'port': int(target_port), 'type': msg_type, 'msg': msg}
        # print str(self.global_state.getRedFood().list())
        self.send_queue.push(msg_packet)

    def sendToAllOtherPlayers(self, msg_type, msg):
        # logger.info("Send message to all other players: {msg}".format(msg=msg))
        for node in self.node_map.get_all_nodes():
            ip, port = node['ip'], node['port']
            self.sendMsg((ip, port), msg_type, msg)

    def multicastToNonSequencer(self, msg_type, msg):
        for node in self.node_map.get_all_nodes():
            ip, port, role = node['ip'], node['port'], node['agent']
            if role != self.sequencer_role:
                self.sendMsg((ip, port), msg_type, msg)

    def appendNodeMap(self, ip, port, server_ip, server_port, role, status):
        self.node_map.append(ip, port, server_ip, server_port, role, status)

    def updateNodeMap(self, ip, port, server_ip, server_port, role, status):
        self.node_map.update(ip, port, server_ip, server_port, role, status)

    def removeNodeMap(self, ip, port):
        self.node_map.remove(ip, port)

    def join(self, timeout=None):
        self.alive = False
        self.message_handler.join()
        self.input_handler.join()
        for conn in self.connection_pool:
            conn.join()
        self.conn_recycle_thread.join()
        self.logger.exit()
        if self.sequencer is not None:
            self.sequencer.exit()
        self.vote_thread.join()

    def createSequencer(self):
        self.sequencer = Sequencer(self.message_handler.seq_queue, self)
        self.sequencer.start()

    # start an election
    def electSequencer(self):
        self.input_queue.push({'msg': 'elect_sequencer'})

    # if a node crashed, change its corresponding life map to False,
    # so that the game can continue.
    def setDeath(self, ip, port):
        role = self.node_map.get_role(ip, port)
        if role is not None:
            index = self.role_map[role]
            #  TODO when some node reconnect, set it back to True
            self.life_map[index] = False

class connectionRecycleThread(threading.Thread):
    """
    recycle the dead connections
    """
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

    def join(self, timeout=None):
        self.alive = False


class messageSendingQueueThread(threading.Thread):
    """
    the thread responsible for sending messages
    """
    def __init__(self, queue, buf_type, pool):
        super(messageSendingQueueThread, self).__init__()
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
            target_conn = list(filter(lambda x: (x.client_ip, x.client_port).__eq__(target_addr), self.pool))
            if len(target_conn) > 0:
                target_conn[0].send(json.dumps(msg))
            # logger.info("Send message: {msg}".format(msg=msg))

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
