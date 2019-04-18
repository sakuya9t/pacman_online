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
            if msg['msg'] == 'gamestart':
                thread.start_new_thread(self.runGame, ())

    def join(self, timeout=None):
        self.alive = False

    def runGame(self):
        from capture import runGames, save_score
        games = runGames(**self.options)
        save_score(games[0])
