import json
import thread
import threading
import time
import os


MESSAGE_TYPE_CONNECT_TO_SERVER = 'cli_conn'
MESSAGE_TYPE_CONTROL_AGENT = 'game_ctl'
MESSAGE_TYPE_NORMAL_MESSAGE = 'normal_message'
MESSAGE_TYPE_CONNECT_CONFIRM = 'cli_conn_ack'
MESSAGE_TYPE_START_GAME = 'start_game'
MESSAGE_TYPE_HOLDBACK = 'holdback'
MESSAGE_TYPE_NO_ORDER_CONTROL = 'no_order_control'
MESSAGE_TYPE_GET_READY = 'get_ready'
MESSAGE_TYPE_EXISTING_NODES = 'nodes_list'
MESSAGE_TYPE_GAME_STATE = 'sync_game_state'
MESSAGE_TYPE_COORDINATOR = 'coordinator'
MESSAGE_TYPE_ELECTION = 'election'
STATUS_READY = 'ready'
STATUS_NOT_READY = 'not_ready'
SEQUENCER = "B1"


class gameRunner(threading.Thread):
    def __init__(self, server, options):
        super(gameRunner, self).__init__()
        self.server = server
        self.alive = True
        self.started = False
        self.options = options
        self.control_queue = server.input_queue
        self.logger = server.logger
        self.clients = []
        self.role = options['myrole'] if 'myrole' in options.keys() else ''
        self.server.role = self.role
        self.role_map = options['role_map'] if 'role_map' in options.keys() else None
        self.server.role_map = self.role_map
        self.server.input_handler.setEnabled(not options['keyboard_disabled'])
        self.delOption('keyboard_disabled')
        self.delOption('myrole')
        self.delOption('role_map')
        self.msg_count = 0  # used as message id

    def run(self):
        while self.alive:
            time.sleep(0.01)
            if self.control_queue.isEmpty():
                continue
            msg = self.control_queue.pop()
            self.logger.info("Keyboard input: {msg}".format(msg=msg))
            if 'msg' in msg.keys():
                self.handleMessage(msg['msg'])
            elif 'key' in msg.keys():
                # key control event
                self.handleArrowControl(msg['key'])
        os._exit(0)

    def handleMessage(self, msg):
        try:
            # >gamestart
            if 'gamestart' == msg:
                if self.started:
                    return

                message = {"agent": self.role}

                self.server.electSequencer()
                # make B1 the sequencer
                # if self.server.role == SEQUENCER:
                #     print "I am sequencer"
                #     self.server.createSequencer()
                #     self.server.sequencer_role = self.role
                #     self.server.sendToAllOtherPlayers(MESSAGE_TYPE_COORDINATOR, message)

                thread.start_new_thread(self.runGame, ())
                self.server.sendToAllOtherPlayers(MESSAGE_TYPE_START_GAME, message)
                self.started = True

            # >elect_sequencer    or    after gamestart     or     a process fail
            elif 'elect_sequencer' == msg:
                # TODO when there is a sequencer, and new nodes join, need to tell new nodes who is sequencer
                # TODO add a timer to election, currently just message passing
                sequencer_role = self.server.sequencer_role
                if sequencer_role not in self.server.node_map.get_all_roles() and sequencer_role != self.role:
                    self.logger.info("Start electing sequencer.")
                    self.server.message_handler.resetGames()
                    higher_id_node = self.server.node_map.get_election_nodes(self.role)
                    message = {"agent": self.role}
                    if not higher_id_node:
                        self.logger.info("I am sequencer")
                        self.server.createSequencer()
                        self.server.sequencer_role = self.role
                        self.server.sendToAllOtherPlayers(MESSAGE_TYPE_COORDINATOR, message)
                    else:
                        for address in higher_id_node:
                            self.server.sendMsg(address, MESSAGE_TYPE_ELECTION, message)
                        # self.server.startElectionTimer(5)



            # >connect 127.0.0.1 8080
            elif 'connect' in msg:
                if self.role == '':
                    self.logger.warning("Player role not set.")
                    self.logger.warning("Run 'setrole [R1/B1/R2/B2]' first.")
                    return
                connection_args = msg.split(' ')
                ip_addr, port = connection_args[1], int(connection_args[2])
                self.connect(ip_addr, port)

            # >setrole B1
            elif 'setrole' in msg:
                args = msg.split(' ')
                self.role = args[1]
                self.server.role = self.role

            # >send 127.0.0.1 8080 "You are a pacman."
            elif 'send' in msg:
                args = msg.split(' ')
                self.server.sendMsg((args[1], args[2]), MESSAGE_TYPE_NORMAL_MESSAGE, args[3])

            # > get ready for the game.
            elif 'ready' == msg:
                self.server.sendToAllOtherPlayers(MESSAGE_TYPE_GET_READY, {"agent": self.role})

            # Test: get game state
            elif 'state' == msg:
                data = self.server.game.state.data
                if data is not None:
                    message = data.json()
                    self.server.sendToAllOtherPlayers(MESSAGE_TYPE_GAME_STATE, message)

            # End the game and kill all threads.
            # >exit
            elif 'exit' == msg:
                self.server.join()
                self.alive = False
        except Exception as e:
            self.logger.error("Input parsing error: {msg}".format(msg=e.message))

    def handleArrowControl(self, key):
        if not self.started:
            return
        try:
            time_left = 9999 if self.server.global_state is None else self.server.global_state.data.timeleft

            # synchronized
            message = {"agent": self.role, "direction": key, "time_left": time_left,
                       "server_info": {"ip": self.server.ip, "port": self.server.port},
                       "msg_count": self.msg_count}
            self.server.recv_queue.push(self.makeFakeControlMessage(message))
            self.server.sendToAllOtherPlayers(MESSAGE_TYPE_HOLDBACK, message)

            # unsynchronized
            # message = {"agent": self.role, "direction": key,
            #            "server_info": {"ip": self.server.ip, "port": self.server.port}}
            # self.server.recv_queue.push({'ip': 'me', 'port': 'me',
            #                             'message': json.dumps({'type': MESSAGE_TYPE_NO_ORDER_CONTROL,
            #                                                    'msg': message})})
            # self.server.sendToAllOtherPlayers(MESSAGE_TYPE_NO_ORDER_CONTROL, message)

            self.msg_count += 1
        except Exception as e:
            self.logger.error("Error in handle arrow control event: {msg}".format(msg=e.message))

    def connect(self, ip, port):
        self.server.activeConnect(ip, port)
        existing_server_list = self.server.node_map.get_all_servers()
        # First send a message to tell the target server our server info
        my_serverip, my_serverport, my_role = self.server.ip, self.server.port, self.role
        self.server.sendMsg((ip, port), MESSAGE_TYPE_CONNECT_TO_SERVER,
                            {'server_ip': my_serverip, 'server_port': my_serverport, 'agent_id': my_role})
        # Then send a message to request target server connect to all servers we have connected to.
        self.server.sendMsg(addr=(ip, port),
                            msg_type=MESSAGE_TYPE_EXISTING_NODES,
                            msg=existing_server_list)

    def join(self, timeout=None):
        self.alive = False

    def setOption(self, key, value):
        self.options[key] = value

    def delOption(self, key):
        if key in list(self.options.keys()):
            del self.options[key]

    def runGame(self):
        from capture import runGames, save_score
        self.options['server'] = self.server
        games = runGames(**self.options)
        self.resetGames()
        save_score(games[0])

    def makeFakeControlMessage(self, message):
        # return {'ip': 'me', 'port': 'me', 'message': json.dumps({'type': MESSAGE_TYPE_CONTROL_AGENT, 'msg': message})}
        return {'ip': 'me', 'port': 'me', 'message': json.dumps({'type': MESSAGE_TYPE_HOLDBACK, 'msg': message})}

    def resetGames(self):
        self.started = False
        self.msg_count = 0
        self.server.global_state = None
        self.server.message_handler.resetGames()
        if self.server.sequencer is not None:
            self.server.sequencer.resetGames()
