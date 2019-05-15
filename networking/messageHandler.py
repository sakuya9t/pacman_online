# COMP90020 Distributed Algorithms project
# Author: Zijian Wang 950618, Nai Wang 927209, Leewei Kuo 932975, Ivan Chee 736901

import threading
import json
import time
import graphicsUtils

from util import Queue, PriorityQueue

MESSAGE_TYPE_CONNECT_TO_SERVER = 'cli_conn'
MESSAGE_TYPE_CONTROL_AGENT = 'game_ctl'
MESSAGE_TYPE_NORMAL_MESSAGE = 'normal_message'
MESSAGE_TYPE_CONNECT_CONFIRM = 'cli_conn_ack'
MESSAGE_TYPE_START_GAME = 'start_game'
MESSAGE_TYPE_GET_READY = 'get_ready'
MESSAGE_TYPE_EXISTING_NODES = 'nodes_list'
MESSAGE_TYPE_HOLDBACK = 'holdback'
MESSAGE_TYPE_NO_ORDER_CONTROL = 'no_order_control'
MESSAGE_TYPE_GAME_STATE = 'sync_game_state'
MESSAGE_TYPE_VOTE_STATE = 'vote_state'
MESSAGE_TYPE_COORDINATOR = 'coordinator'
MESSAGE_TYPE_ELECTION = 'election'
MESSAGE_TYPE_REJECT_ELECTION = 'reject_election'
STATUS_READY = 'ready'
STATUS_NOT_READY = 'not_ready'


class messageHandler(threading.Thread):
    """
    this thread is responsible for dealing with the messages received
    from the socket.
    """
    def __init__(self, server, recv_buf, send_buf, logger):
        super(messageHandler, self).__init__()
        self.server = server
        self.recv_buf = recv_buf
        self.send_buf = send_buf

        # action queues
        # when control messages are ready to deliver, they will
        # be pushed into the corresponding agent's queue.
        self.r1_queue = Queue()
        self.r2_queue = Queue()
        self.b1_queue = Queue()
        self.b2_queue = Queue()
        self.logger = logger
        self.alive = True

        # sequencer hold back queue
        self.seq_queue = PriorityQueue()
        # key is msg_id, value is direction
        self.holdback_queue = {}
        self.arrived_g_seq = {}
        self.p_seq = 0  # process sequence number

    def run(self):
        while self.alive:
            time.sleep(0.1)
            if self.recv_buf.isEmpty():
                continue
            msg = self.recv_buf.pop()

            try:
                source_ip, source_port = msg['ip'], msg['port']
                msg = json.loads(msg['message'])
                msg_type = msg['type']
                node_map = self.server.node_map
                my_serverip, my_serverport, my_role = self.server.ip, self.server.port, self.server.role

                if msg_type == MESSAGE_TYPE_CONNECT_TO_SERVER:
                    self.logger.info("Received connection request from {ip}:{port}: {message}."
                                     .format(ip=source_ip, port=source_port, message=msg['msg']))

                    # connect to source_ip:source_port
                    msg = msg['msg']

                    # if there is already a player claiming he is R1, don't let another R1 get online.
                    if node_map.exists_agent(msg['agent_id']):
                        self.logger.info("Player {role} already exists, rejected connection."
                                         .format(role=msg['agent_id']))
                        continue

                    # if there are already other nodes existing, send their server address to new node.
                    existing_server_list = node_map.get_all_servers()
                    self.server.sendMsg(addr=(source_ip, source_port),
                                        msg_type=MESSAGE_TYPE_EXISTING_NODES,
                                        msg=existing_server_list)

                    self.server.appendNodeMap(ip=source_ip, port=source_port,
                                              server_ip=msg['server_ip'], server_port=msg['server_port'],
                                              role=msg['agent_id'], status=STATUS_NOT_READY)
                    self.logger.info("Node map changed: {node_map}".format(node_map=node_map))
                    self.server.sendMsg(addr=(source_ip, source_port),
                                        msg_type=MESSAGE_TYPE_CONNECT_CONFIRM,
                                        msg={'server_ip': my_serverip, 'server_port': my_serverport,
                                             'agent_id': my_role})

                elif msg_type == MESSAGE_TYPE_CONNECT_CONFIRM:
                    self.logger.info("Received connection confirmation from {ip}:{port}: {message}."
                                     .format(ip=source_ip, port=source_port, message=msg['msg']))
                    msg = msg['msg']
                    if not node_map.exists_server(msg['server_ip'], server_port=msg['server_port']):
                        self.server.appendNodeMap(ip=source_ip, port=source_port,
                                                  server_ip=msg['server_ip'], server_port=msg['server_port'],
                                                  role=msg['agent_id'], status=STATUS_NOT_READY)
                        self.logger.info("Node map changed: {node_map}".format(node_map=node_map))

                elif msg_type == MESSAGE_TYPE_EXISTING_NODES:
                    # Some nodes are already existed, I get this message because I am connecting to one of them.
                    # Then I am required to connect to all the rest ones.
                    # Used for when 3rd or 4th node joins in.
                    server_list = msg['msg']
                    self.logger.info("Received a request to connect to the following servers: {servers}"
                                     .format(servers=server_list))
                    for server in server_list:
                        ip, port = server['server_ip'], server['server_port']
                        if not node_map.exists_server(ip, port):
                            self.connect(ip, port)
                            self.server.appendNodeMap(ip=ip, port=port,
                                                      server_ip=ip, server_port=port,
                                                      role=server['agent_id'], status=STATUS_NOT_READY)
                    self.logger.info("Node map changed: {node_map}".format(node_map=node_map))

                # For every processes, put the message into the holdback queue.
                # For sequencer process, also put the message into sequencer queue.
                elif msg_type == MESSAGE_TYPE_HOLDBACK:
                    msg = msg['msg']  # text
                    # self.logger.info("{message}".format(message=msg))
                    agent, msg_count, direction = msg['agent'], msg['msg_count'], msg['direction']
                    msg_id = (agent, msg_count)
                    self.holdback_queue.update({msg_id: direction})
                    if self.server.sequencer is not None:
                        time_left = msg['time_left']
                        priority = - time_left
                        self.seq_queue.push(msg_id, priority)

                # Put the message in the arrived queue and deliver acoording to
                # group sequence number.
                elif msg_type == MESSAGE_TYPE_CONTROL_AGENT:
                    msg = msg['msg']
                    msg_id = msg['msg_id']
                    g_seq = msg['group_sequence']
                    # self.logger.info("{message}".format(message=msg))
                    msg_id = tuple(msg_id)
                    self.arrived_g_seq.update({g_seq: msg_id})
                    self.deliver()

                # a control message not organized by the sequencer
                elif msg_type == MESSAGE_TYPE_NO_ORDER_CONTROL:
                    msg = msg['msg']
                    agent = msg['agent'].upper()
                    if agent == 'R1':
                        self.r1_queue.push(msg['direction'])
                    if agent == 'B1':
                        self.b1_queue.push(msg['direction'])
                    if agent == 'R2':
                        self.r2_queue.push(msg['direction'])
                    if agent == 'B2':
                        self.b2_queue.push(msg['direction'])

                elif msg_type == MESSAGE_TYPE_GAME_STATE:
                    # If received game state sent from p*, send (vi, pj) for pj != p*
                    msg = msg['msg']
                    data = json.loads(msg)
                    timestamp = data['timeleft']
                    self.logger.info("Received game state data from general, timestamp: {timestamp}."
                                     .format(timestamp=timestamp))
                    # add decision from p* to votes
                    lock = self.server.vote_map_lock
                    vote_map = self.server.vote_map
                    lock.acquire()
                    try:
                        if timestamp not in vote_map.keys():
                            vote_map[timestamp] = []
                        vote_map[timestamp].append(data)
                    finally:
                        lock.release()
                    # b-multicast (vi, pj) from p* to all other non-coordinators
                    self.server.multicastToNonSequencer(MESSAGE_TYPE_VOTE_STATE,
                                                        {'data': msg, 'agent': self.server.role})

                elif msg_type == MESSAGE_TYPE_NORMAL_MESSAGE:
                    self.logger.info("Received normal message from {ip}:{port}: {message}."
                                     .format(ip=source_ip, port=source_port, message=msg['msg']))

                elif msg_type == MESSAGE_TYPE_VOTE_STATE:
                    msg = msg['msg']
                    data = json.loads(msg['data'])
                    lock = self.server.vote_map_lock
                    vote_map = self.server.vote_map
                    self.logger.info("Received vote state data from {peer} for timestamp {timestamp}."
                                     .format(peer=msg['agent'], timestamp=data['timeleft']))
                    timestamp = data['timeleft']
                    lock.acquire()
                    try:
                        if timestamp not in vote_map.keys():
                            vote_map[timestamp] = []
                        vote_map[timestamp].append(data)
                    finally:
                        lock.release()

                elif msg_type == MESSAGE_TYPE_START_GAME:
                    # another player requires to start the game.
                    control_buf = self.server.input_queue
                    control_buf.push({'msg': 'gamestart'})

                # record the elected sequencer
                elif msg_type == MESSAGE_TYPE_COORDINATOR:
                    msg = msg['msg']
                    agent = msg['agent']
                    self.server.sequencer_role = agent
                    self.logger.info("New elected sequencer: {agent}".format(agent=self.server.sequencer_role))

                # this is received when a lower id process wants to bid for the sequencer.
                # Reject it and starts an election ourselves.
                elif msg_type == MESSAGE_TYPE_ELECTION:
                    msg = msg['msg']
                    agent = msg['agent']
                    self.logger.info("{agent} starts election.".format(agent=str(agent)))
                    message = {'agent': my_role}
                    if my_role > agent:
                        self.server.sendMsg((source_ip, source_port), MESSAGE_TYPE_REJECT_ELECTION, message)
                        self.server.electSequencer()

                # this is received when our election is rejected.
                # Stop the timer (not implemented) and wait for COORDINATOR message
                elif msg_type == MESSAGE_TYPE_REJECT_ELECTION:
                    msg = msg['msg']
                    agent = msg['agent']
                    self.logger.info("Election rejected by {agent}.".format(agent=agent))

                else:
                    print 'a'
                    self.logger.info(msg)

            except Exception as e:
                print(msg)
                self.logger.error(str(e))

    def join(self, timeout=None):
        self.alive = False
        threading.Thread.join(self, timeout)

    # deliver the message when process sequence number equals to group sequence number.
    # If the group sequence number does not arrive, break and wait for the next message.
    def deliver(self):
        while self.p_seq in self.arrived_g_seq:
            msg_id = self.arrived_g_seq[self.p_seq]
            if msg_id in self.holdback_queue:
                self.arrived_g_seq.pop(self.p_seq)
                agent, _ = msg_id
                direction = self.holdback_queue.pop(msg_id)
                if agent == 'R1':
                    self.r1_queue.push(direction)
                if agent == 'B1':
                    self.b1_queue.push(direction)
                if agent == 'R2':
                    self.r2_queue.push(direction)
                if agent == 'B2':
                    self.b2_queue.push(direction)
                self.p_seq += 1
            else:
                break

    def connect(self, ip, port):
        self.server.activeConnect(ip, port)
        # First send a message to tell the target server our server info
        my_serverip, my_serverport, my_role = self.server.ip, self.server.port, self.server.role
        self.server.sendMsg((ip, port), MESSAGE_TYPE_CONNECT_TO_SERVER,
                            {'server_ip': my_serverip, 'server_port': my_serverport, 'agent_id': my_role})

    def resetGames(self):
        del self.r1_queue.list[:]
        del self.r2_queue.list[:]
        del self.b1_queue.list[:]
        del self.b2_queue.list[:]
        del self.seq_queue.heap[:]
        self.holdback_queue.clear()
        self.arrived_g_seq.clear()
        self.p_seq = 0
