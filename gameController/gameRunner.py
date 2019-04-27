import json
import thread
import threading
import time
import os
import graphicsUtils

MESSAGE_TYPE_CONNECT_TO_SERVER = 'cli_conn'
MESSAGE_TYPE_CONTROL_AGENT = 'game_ctl'
MESSAGE_TYPE_NORMAL_MESSAGE = 'normal_message'
MESSAGE_TYPE_CONNECT_CONFIRM = 'cli_conn_ack'
MESSAGE_TYPE_START_GAME = 'start_game'
MESSAGE_TYPE_GET_READY = 'get_ready'


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

    def run(self):
        while self.alive:
            time.sleep(0.01)
            if self.control_queue.isEmpty():
                continue
            msg = self.control_queue.pop()
            # self.logger.info("Keyboard input: {msg}".format(msg=msg))
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

                # Changed to call runGame in main thread
                graphicsUtils.runGame()
                # thread.start_new_thread(self.runGame, ())

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
            message = {"agent": self.role, "direction": key,
                       "server_info": {"ip": self.server.ip, "port": self.server.port}}
            self.server.sendToAllOtherPlayers(MESSAGE_TYPE_CONTROL_AGENT, message)
            self.server.recv_queue.push(self.makeFakeControlMessage(message))
        except Exception as e:
            self.logger.error("Error in handle arrow control event: {msg}".format(msg=e.message))

    def connect(self, ip, port):
        self.server.activeConnect(ip, port)
        # First send a message to tell the target server our server info
        self.server.sendMsg((ip, port), MESSAGE_TYPE_CONNECT_TO_SERVER, {'agent_id': self.role})

    def join(self, timeout=None):
        self.alive = False

    def setOption(self, key, value):
        self.options[key] = value

    def delOption(self, key):
        if key in list(self.options.keys()):
            del self.options[key]

    # def runGame(self):
    #     from capture import runGames, save_score
    #     games = runGames(**self.options)
    #     self.started = False
    #     save_score(games[0])

    def stopGame(self):
        self.started = False

    def makeFakeControlMessage(self, message):
        return {'ip': 'me', 'port': 'me', 'message': json.dumps({'type': MESSAGE_TYPE_CONTROL_AGENT, 'msg': message})}
