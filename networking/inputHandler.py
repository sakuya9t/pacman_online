import threading
import keyboard
import time


KEY_PRESS_EVENT_MODE = 0
INPUT_MODE = 1


class inputHandler(threading.Thread):
    def __init__(self, server):
        super(inputHandler, self).__init__()
        self.gameStarted = False
        self.buffer = server.input_queue
        keyboard.on_press(self.key_press)
        self.msgbuffer = ""
        # how to get the agent?
        self.agent = 'B1'  # hardcode to 'b1' for now
        self.msg_count = 0  # used with agent as message id
        self.recv_q = server.recv_queue

        self.server_ip = server.ip
        self.server_port = server.port

    def run(self):
        # TODO cannot connect.....
        # self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.conn.connect((self.server_ip, self.server_port))
        while True:
            time.sleep(500)

    def key_press(self, key):
        try:
            key_name = str(key.name)
        except Exception:
            return
        if key_name in ['up', 'down', 'left', 'right']:
            self.buffer.push({'key': key_name})
            # multicast to all other players, just send to self for now....
            # logger.info(json.dumps({"command": "holdback", "key": key_name,
            #                         "msg_id": (self.agent, self.msg_count)}))
            # self.conn.sendall(json.dumps(
            #     {"command": "holdback", "key": key_name, "msg_id": (self.agent, self.msg_count)}))
            # self.msg_count += 1
            
        if key.name == u'enter':
            self.buffer.push({'msg': self.msgbuffer})
            self.msgbuffer = ""
        else:
            if key_name == 'space':
                self.msgbuffer += " "
            elif key_name == 'backspace':
                if len(self.msgbuffer) > 0:
                    self.msgbuffer = self.msgbuffer[:-1]
            elif len(key_name) == 1:
                self.msgbuffer += key_name
