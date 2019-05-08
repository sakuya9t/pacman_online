import threading
import json
import time

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
STATUS_READY = 'ready'
STATUS_NOT_READY = 'not_ready'
SEQUENCER = "B1"

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
                        # todo: disconnect with corresponding node.
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

                elif msg_type == MESSAGE_TYPE_HOLDBACK:
                    msg = msg['msg']  # text
                    self.logger.info("{message}".format(message=msg))
                    agent, msg_count, direction = msg['agent'], msg['msg_count'], msg['direction']
                    msg_id = (agent, msg_count)
                    self.holdback_queue.update({msg_id: direction})
                    if self.server.role == SEQUENCER:
                        time_left = msg['time_left']
                        priority = - time_left
                        self.seq_queue.push(msg_id, priority)

                elif msg_type == MESSAGE_TYPE_CONTROL_AGENT:
                    msg = msg['msg']
                    msg_id = msg['msg_id']
                    g_seq = msg['group_sequence']
                    self.logger.info("{message}".format(message=msg))
                    msg_id = tuple(msg_id)
                    self.arrived_g_seq.update({g_seq: msg_id})
                    self.deliver()

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
