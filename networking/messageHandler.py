import threading
import json
import time

from util import Queue

MESSAGE_TYPE_CONNECT_TO_SERVER = 'cli_conn'
MESSAGE_TYPE_CONTROL_AGENT = 'game_ctl'
MESSAGE_TYPE_NORMAL_MESSAGE = 'normal_message'
MESSAGE_TYPE_CONNECT_CONFIRM = 'cli_conn_ack'
MESSAGE_TYPE_START_GAME = 'start_game'
MESSAGE_TYPE_GET_READY = 'get_ready'
STATUS_READY = 'ready'
STATUS_NOT_READY = 'not_ready'
MESSAGE_TYPE_HOLDBACK = 'holdback'
MESSAGE_TYPE_NO_ORDER_CONTROL = 'no_order_control'

class messageHandler(threading.Thread):
    def __init__(self, server, recv_buf, send_buf, logger):
        super(messageHandler, self).__init__()
        self.server = server
        self.recv_buf = recv_buf
        self.send_buf = send_buf
        self.r1_queue = Queue()
        self.r2_queue = Queue()
        self.b1_queue = Queue()
        self.b2_queue = Queue()
        self.logger = logger
        self.alive = True

        # holdback queue
        self.r1_hold_q = Queue()
        self.r2_hold_q = Queue()
        self.b1_hold_q = Queue()
        self.b2_hold_q = Queue()
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

                if msg_type == MESSAGE_TYPE_CONNECT_TO_SERVER:
                    self.logger.info("Received connection request from {ip}:{port}: {message}."
                                     .format(ip=source_ip, port=source_port, message=msg['msg']))
                    # connect to source_ip:source_port
                    msg = msg['msg']
                    # if there is already a player claiming he is R1, don't let another R1 get online.
                    if len(list(filter(lambda x: x['agent'].__eq__(msg['agent_id']), node_map))):
                        continue
                    my_role = self.server.role
                    self.server.appendNodeMap(ip=source_ip, port=source_port,
                                              role=msg['agent_id'], status=STATUS_NOT_READY)
                    self.logger.info("Node map changed: {node_map}".format(node_map=self.server.node_map))
                    self.server.sendMsg(addr=(source_ip, source_port),
                                        msg_type=MESSAGE_TYPE_CONNECT_CONFIRM,
                                        msg={'agent_id': my_role})

                elif msg_type == MESSAGE_TYPE_CONNECT_CONFIRM:
                    self.logger.info("Received connection confirmation from {ip}:{port}: {message}."
                                     .format(ip=source_ip, port=source_port, message=msg['msg']))
                    msg = msg['msg']
                    self.server.appendNodeMap(ip=source_ip, port=source_port,
                                              role=msg['agent_id'], status=STATUS_NOT_READY)
                    self.logger.info("Node map changed: {node_map}".format(node_map=self.server.node_map))

                elif msg_type == MESSAGE_TYPE_HOLDBACK:
                    msg = msg['msg']
                    agent = msg['agent'].upper()
                    self.logger.info("{message}".format(message=msg))
                    if agent == 'R1':
                        self.r1_hold_q.push((msg['msg_count'], msg['direction']))
                    if agent == 'B1':
                        self.b1_hold_q.push((msg['msg_count'], msg['direction']))
                    if agent == 'R2':
                        self.r2_hold_q.push((msg['msg_count'], msg['direction']))
                    if agent == 'B2':
                        self.b2_hold_q.push((msg['msg_count'], msg['direction']))

                elif msg_type == MESSAGE_TYPE_CONTROL_AGENT:
                    msg = msg['msg']
                    agent = msg['agent'].upper()
                    msg_count = msg['msg_count']
                    g_seq = msg['group_sequence']
                    self.logger.info("{message}".format(message=msg))

                    # assume the messages from sequencer are ordered for now
                    if self.p_seq == g_seq:
                        self.deliver(agent, msg_count)
                        self.p_seq += 1
                    else:
                        pass

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

                # elif msg_type == MESSAGE_TYPE_CONTROL_AGENT:
                #     msg = msg['msg']
                #     agent = msg['agent'].upper()
                #     if agent == 'R1':
                #         self.r1_queue.push(msg['direction'])
                #     if agent == 'B1':
                #         self.b1_queue.push(msg['direction'])
                #     if agent == 'R2':
                #         self.r2_queue.push(msg['direction'])
                #     if agent == 'B2':
                #         self.b2_queue.push(msg['direction'])

                elif msg_type == MESSAGE_TYPE_NORMAL_MESSAGE:
                    self.logger.info("Received normal message from {ip}:{port}: {message}."
                                     .format(ip=source_ip, port=source_port, message=msg['msg']))

                elif msg_type == MESSAGE_TYPE_START_GAME:
                    # another player requires to start the game.
                    # todo: currently anyone requires gamestart causes game start, but we should wait until all ready.
                    print msg
                    control_buf = self.server.input_queue
                    control_buf.push({'msg': 'gamestart'})

                else:
                    self.logger.info(msg)

            except Exception as e:
                print(msg)
                self.logger.error(str(e))

    def join(self, timeout=None):
        self.alive = False
        threading.Thread.join(self, timeout)
        
    def deliver(self, agent, msg_count):
        if agent == 'R1':
            self.deliver_msg_in_q(self.r1_queue, self.r1_hold_q, msg_count)
        if agent == 'B1':
            self.deliver_msg_in_q(self.b1_queue, self.b1_hold_q, msg_count)
        if agent == 'R2':
            self.deliver_msg_in_q(self.r2_queue, self.r2_hold_q, msg_count)
        if agent == 'B2':
            self.deliver_msg_in_q(self.b2_queue, self.b2_hold_q, msg_count)

    def deliver_msg_in_q(self, q, hold_q, msg_count):
        id, key = hold_q.pop()
        # delete garbage msg
        while id != msg_count:
            id, key = hold_q.pop()
        # deliver msg
        if id == msg_count:
            q.push(key)
        else:
            self.logger.error("messageHandler error: message not in queue")
