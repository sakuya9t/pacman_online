import json
import thread
import threading
import time
import os
from sequencer import Sequencer

MESSAGE_TYPE_CONNECT_TO_SERVER = 'cli_conn'
MESSAGE_TYPE_CONTROL_AGENT = 'game_ctl'
MESSAGE_TYPE_NORMAL_MESSAGE = 'normal_message'
MESSAGE_TYPE_CONNECT_CONFIRM = 'cli_conn_ack'
MESSAGE_TYPE_START_GAME = 'start_game'
MESSAGE_TYPE_HOLDBACK = 'holdback'
MESSAGE_TYPE_NO_ORDER_CONTROL = 'no_order_control'
MESSAGE_TYPE_GET_READY = 'get_ready'
MESSAGE_TYPE_EXISTING_NODES = 'nodes_list'
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
        self.server.input_handler.setEnabled(not options['keyboard_disabled'])
        self.delOption('keyboard_disabled')
        self.delOption('myrole')
        self.sequencer = None
        self.msg_count = 0  # used as message id
        # make B1 the sequencer
        if self.server.role == SEQUENCER:
            print "I am sequencer"
            self.sequencer = Sequencer(server.message_handler.seq_queue, server)
            self.sequencer.start()

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
            if msg == 'gamestart':
                if self.started:
                    return
                thread.start_new_thread(self.runGame, ())
                message = {"agent": self.role}
                self.server.sendToAllOtherPlayers(MESSAGE_TYPE_START_GAME, message)
                self.started = True

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

            # End the game and kill all threads.
            # >exit
            elif 'exit' == msg:
                self.server.join()
                if self.sequencer is not None:
                    self.sequencer.exit()
                self.alive = False
        except Exception as e:
            self.logger.error("Input parsing error: {msg}".format(msg=e.message))

    # TODO global_state is still None when gameStart
    def handleArrowControl(self, key):
        if not self.started:
            print str(self.server.global_state)
            return
        try:
            time_left = 9999 if self.server.global_state is None else self.server.global_state.data.timeleft
            print str(time_left)
            # only work when 4 players are connected (synchronize)
            message = {"agent": self.role, "direction": key, "time_left": time_left,
                       "server_info": {"ip": self.server.ip, "port": self.server.port},
                       "msg_count": self.msg_count}
            self.server.recv_queue.push(self.makeFakeControlMessage(message))
            self.server.sendToAllOtherPlayers(MESSAGE_TYPE_HOLDBACK, message)

            # send direction directly (not synchronize)
            # message = {"agent": self.role, "direction": key,
            #            "server_info": {"ip": self.server.ip, "port": self.server.port}}
            # self.server.recv_queue.push({'ip': 'me', 'port': 'me',
            #                             'message': json.dumps({'type': MESSAGE_TYPE_NO_ORDER_CONTROL,
            #                                                    'msg': message})})
            # self.server.sendToAllOtherPlayers(MESSAGE_TYPE_NO_ORDER_CONTROL, message)

            # use this for testing
            # self.makeAllFakeMessage(key)

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
        games = runGames(**self.options)
        self.started = False
        save_score(games[0])

    def makeFakeControlMessage(self, message):
        # return {'ip': 'me', 'port': 'me', 'message': json.dumps({'type': MESSAGE_TYPE_CONTROL_AGENT, 'msg': message})}
        return {'ip': 'me', 'port': 'me', 'message': json.dumps({'type': MESSAGE_TYPE_HOLDBACK, 'msg': message})}

    # test usage only
    def makeAllFakeMessage(self, key):
        message1 = {"agent": "R1", "direction": key,
                    "server_info": {"ip": self.server.ip, "port": self.server.port},
                    "msg_count": self.msg_count}
        message2 = {"agent": "R2", "direction": key,
                    "server_info": {"ip": self.server.ip, "port": self.server.port},
                    "msg_count": self.msg_count}
        message3 = {"agent": "B1", "direction": key,
                    "server_info": {"ip": self.server.ip, "port": self.server.port},
                    "msg_count": self.msg_count}
        message4 = {"agent": "B2", "direction": key,
                    "server_info": {"ip": self.server.ip, "port": self.server.port},
                    "msg_count": self.msg_count}
        self.server.recv_queue.push(self.makeFakeControlMessage(message1))
        self.server.recv_queue.push(self.makeFakeControlMessage(message2))
        self.server.recv_queue.push(self.makeFakeControlMessage(message3))
        self.server.recv_queue.push(self.makeFakeControlMessage(message4))
        self.server.sendToAllOtherPlayers(MESSAGE_TYPE_HOLDBACK, message1)
        self.server.sendToAllOtherPlayers(MESSAGE_TYPE_HOLDBACK, message2)
        self.server.sendToAllOtherPlayers(MESSAGE_TYPE_HOLDBACK, message3)
        self.server.sendToAllOtherPlayers(MESSAGE_TYPE_HOLDBACK, message4)
        print "makeAllFakeMessage"
