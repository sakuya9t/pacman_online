import threading
import keyboard
import time


KEY_PRESS_EVENT_MODE = 0
INPUT_MODE = 1


class inputHandler(threading.Thread):
    def __init__(self, server, enabled):
        super(inputHandler, self).__init__()
        self.gameStarted = False
        self.buffer = server.input_queue
        keyboard.on_press(self.key_press)
        self.msgbuffer = ""
        self.enabled = enabled
        self.alive = True

    def run(self):
        while self.alive:
            message = raw_input()
            self.buffer.push({'msg': message})

    def key_press(self, key):
        if not self.enabled:
            return
        try:
            key_name = str(key.name)
        except Exception:
            return
        if key_name in ['up', 'down', 'left', 'right']:
            self.buffer.push({'key': key_name})

    def setEnabled(self, enabled):
        self.enabled = enabled

    def join(self, timeout=None):
        self.alive = False
        keyboard.unhook_all()
