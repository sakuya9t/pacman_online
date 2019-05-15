# COMP90020 Distributed Algorithms project
# Author: Zijian Wang 950618, Nai Wang 927209, Leewei Kuo 932975, Ivan Chee 736901

import threading
import keyboard
import time


class inputHandler(threading.Thread):
    """
    This thread is used to handle user inputs
    """
    def __init__(self, server):
        super(inputHandler, self).__init__()
        self.gameStarted = False
        self.buffer = server.input_queue
        keyboard.on_press(self.key_press)
        self.msgbuffer = ""
        self.alive = True

    def run(self):
        while self.alive:
            try:
                message = raw_input()
                self.buffer.push({'msg': message})
            except:
                pass

    def key_press(self, key):
        try:
            key_name = str(key.name)
        except Exception:
            return
        if key_name.lower() in ['up', 'down', 'left', 'right']:
            self.buffer.push({'key': key_name})

    def setEnabled(self, enabled):
        self.enabled = enabled

    def join(self, timeout=None):
        self.alive = False
        keyboard.unhook_all()
