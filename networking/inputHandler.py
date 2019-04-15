import threading
import keyboard
import time

import logger

KEY_PRESS_EVENT_MODE = 0
INPUT_MODE = 1


class inputHandler(threading.Thread):
    def __init__(self, server):
        super(inputHandler, self).__init__()
        self.gameStarted = False
        self.buffer = server.input_queue
        keyboard.on_press(self.key_press)
        self.msgbuffer = ""

    def run(self):
        while True:
            time.sleep(5)

    def key_press(self, key):
        try:
            key_name = str(key.name)
        except Exception:
            return
        if key_name in ['up', 'down', 'left', 'right']:
            self.buffer.push({'key': key_name})
        if key.name == u'enter':
            self.buffer.push({'msg': self.msgbuffer})
            self.msgbuffer = ""
        else:
            if key_name == 'space':
                self.msgbuffer += " "
            elif len(key_name) == 1:
                self.msgbuffer += key_name
