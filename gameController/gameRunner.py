import json
import thread
import threading
import time
from sequencer import Sequencer

MESSAGE_TYPE_CONNECT_TO_SERVER = 'cli_conn'
MESSAGE_TYPE_CONTROL_AGENT = 'game_ctl'
MESSAGE_TYPE_NORMAL_MESSAGE = 'normal_message'
MESSAGE_TYPE_CONNECT_CONFIRM = 'cli_conn_ack'
MESSAGE_TYPE_START_GAME = 'start_game'
MESSAGE_TYPE_HOLDBACK = 'holdback'
MESSAGE_TYPE_NO_ORDER_CONTROL = 'no_order_control'


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
        self.role = options['myrole']
        self.server.role = self.role
        self.server.input_handler.setEnabled(not options['keyboard_disabled'])
        self.delOption('keyboard_disabled')
        self.delOption('myrole')
        self.msg_count = 0  # used as message id
        # make B1 the sequencer
        if self.server.role == "B1":
            print "I am sequencer"
            self.sequencer = Sequencer(server.message_handler.r1_hold_q, server.message_handler.r2_hold_q,
                                       server.message_handler.b1_hold_q, server.message_handler.b2_hold_q,
                                       server)
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

    def handleMessage(self, msg):
        try:
            if msg == 'gamestart':
                # >gamestart
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
            elif 'setrole' in msg:
                # >setrole B1
                args = msg.split(' ')
                self.role = args[1]
                self.server.role = self.role
            elif 'send' in msg:
                # >send 127.0.0.1 8080 "You are a pacman."
                args = msg.split(' ')
                self.server.sendMsg((args[1], args[2]), MESSAGE_TYPE_NORMAL_MESSAGE, args[3])
        except Exception as e:
            self.logger.error("Input parsing error: {msg}".format(msg=e.message))

    def handleArrowControl(self, key):
        if not self.started:
            return
        try:

            # only work when 4 players are connected (synchronize)
            # message = {"agent": self.role, "direction": key,
            #             "server_info": {"ip": self.server.ip, "port": self.server.port},
            #             "msg_count": self.msg_count}
            # self.server.recv_queue.push(self.makeFakeControlMessage(message))
            # self.server.sendToAllOtherPlayers(MESSAGE_TYPE_HOLDBACK, message)

            # send direction directly (not synchronize)
            message = {"agent": self.role, "direction": key,
                        "server_info": {"ip": self.server.ip, "port": self.server.port}}
            self.server.recv_queue.push( {'ip': 'me', 'port': 'me', 'message': json.dumps({'type': MESSAGE_TYPE_NO_ORDER_CONTROL, 'msg': message})})
            self.server.sendToAllOtherPlayers(MESSAGE_TYPE_NO_ORDER_CONTROL, message)

            # use this for testing
            # self.makeAllFakeMessage(key)

            self.msg_count += 1
        except Exception as e:
            self.logger.error("Error in handle arrow control event: {msg}".format(msg=e.message))

    def connect(self, ip, port):
        self.server.activeConnect(ip, port)
        # First send a message to tell the target server our server info
        my_ip, my_port = self.server.ip, self.server.port
        self.server.sendMsg((ip, port), MESSAGE_TYPE_CONNECT_TO_SERVER, {'ip': my_ip, 'port': my_port,
                                                                         'agent_id': self.role})

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
