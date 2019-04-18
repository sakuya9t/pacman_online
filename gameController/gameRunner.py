import thread
import threading
import time


class gameRunner(threading.Thread):
    def __init__(self, server, options):
        super(gameRunner, self).__init__()
        self.server = server
        self.alive = True
        self.options = options
        self.control_queue = server.input_queue
        self.logger = server.logger

    def run(self):
        while self.alive:
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
                thread.start_new_thread(self.runGame, ())
            elif 'connect' in msg:
                connection_args = msg.split(' ')
                ip_addr = connection_args[1]
                port = connection_args[2]
                print("connect to {ip}:{port}".format(ip=ip_addr, port=port))
        except Exception as e:
            self.logger.error("Input parsing error: {msg}".format(msg=e.message))

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
