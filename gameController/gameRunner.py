import thread
import threading
import time

MESSAGE_TYPE_CONNECT_TO_SERVER = 'cli_conn'
MESSAGE_TYPE_CONTROL_AGENT = 'game_ctl'
MESSAGE_TYPE_NORMAL_MESSAGE = 'normal_message'


class gameRunner(threading.Thread):
    def __init__(self, server, options):
        super(gameRunner, self).__init__()
        self.server = server
        self.alive = True
        self.options = options
        self.control_queue = server.input_queue
        self.logger = server.logger
        self.clients = []
        self.keyboard_disabled = options['keyboard_disabled']
        self.role = ''
        self.delOption('keyboard_disabled')

    def run(self):
        while self.alive:
            if self.keyboard_disabled:
                time.sleep(500)
                continue
            time.sleep(0.01)
            if self.control_queue.isEmpty():
                continue
            msg = self.control_queue.pop()
            self.logger.info("Keyboard input: {msg}".format(msg=msg))
            if 'msg' in msg.keys():
                self.handleMessage(msg['msg'])

    def handleMessage(self, msg):
        try:
            if msg == 'gamestart':
                # >gamestart
                thread.start_new_thread(self.runGame, ())
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
            elif 'send' in msg:
                # >send 127.0.0.1 8080 "You are a pacman."
                args = msg.split(' ')
                self.server.sendMsg((args[1], args[2]), MESSAGE_TYPE_NORMAL_MESSAGE, args[3])
        except Exception as e:
            self.logger.error("Input parsing error: {msg}".format(msg=e.message))

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
        save_score(games[0])
