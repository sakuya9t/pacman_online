import datetime
import threading

from util import Queue


class logger(threading.Thread):
    def __init__(self):
        super(logger, self).__init__()
        self.buffer = Queue()
        self.alive = True

    def run(self):
        while self.alive:
            if self.buffer.isEmpty():
                continue
            else:
                message = self.buffer.pop()
                print(message)

    def info(self, message):
        time = str(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"))
        message = str(message)
        self.buffer.push("\033[0m (INFO) {time} {message}".format(time=time, message=message))

    def error(self, message):
        time = str(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"))
        message = str(message)
        self.buffer.push("\033[91m (ERROR) {time} {message}".format(time=time, message=message))

    def warning(self, message):
        time = str(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"))
        message = str(message)
        self.buffer.push("\033[93m (WARNING) {time} {message}".format(time=time, message=message))

    def join(self, timeout=None):
        self.alive = False

logger = logger()
logger.start()
