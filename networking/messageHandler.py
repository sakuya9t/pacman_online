import threading
import json
import time

from util import Queue

MESSAGE_TYPE_CONNECT_TO_SERVER = 'cli_conn'
MESSAGE_TYPE_CONTROL_AGENT = 'game_ctl'
MESSAGE_TYPE_NORMAL_MESSAGE = 'normal_message'
MESSAGE_TYPE_CONNECT_CONFIRM = 'cli_conn_ack'
MESSAGE_TYPE_START_GAME = 'start_game'
MESSAGE_TYPE_HOLDBACK = 'holdback'


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
                msg_type = msg['type']

                if msg_type == MESSAGE_TYPE_CONNECT_TO_SERVER:
                    self.logger.info("Received connection request from {ip}:{port}: {message}."
                                     .format(ip=source_ip, port=source_port, message=msg['msg']))
                    # connect to source_ip:source_port
                    msg = msg['msg']
                    otherserver_ip, otherserver_port = msg['ip'], msg['port']
                    my_ip, my_port, my_role = self.server.ip, self.server.port, self.server.role
                    self.server.node_map.append({'client': {'ip': source_ip, 'port': source_port},
                                                 'server': {'ip': otherserver_ip, 'port': otherserver_port},
                                                 'agent': msg['agent_id']})
                    self.logger.info("Node map changed: {node_map}".format(node_map=self.server.node_map))
                    self.server.activeConnect(msg['ip'], msg['port'])
                    self.server.sendMsg(addr=(otherserver_ip, otherserver_port),
                                        msg_type=MESSAGE_TYPE_CONNECT_CONFIRM,
                                        msg={'ip': my_ip, 'port': my_port, 'agent_id': my_role})

                elif msg_type == MESSAGE_TYPE_CONNECT_CONFIRM:
                    self.logger.info("Received connection confirmation from {ip}:{port}: {message}."
                                     .format(ip=source_ip, port=source_port, message=msg['msg']))
                    msg = msg['msg']
                    self.server.node_map.append({'client': {'ip': source_ip, 'port': source_port},
                                                 'server': {'ip': msg['ip'], 'port': msg['port']},
                                                 'agent': msg['agent_id']})
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
