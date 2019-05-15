# COMP90020 Distributed Algorithms project
# Author: Zijian Wang 950618, Nai Wang 927209, Leewei Kuo 932975, Ivan Chee 736901

import random
import socket
import threading
import time
from logger import logger
import json

MESSAGE_TYPE_CONNECT_TO_SERVER = 'cli_conn'
MESSAGE_TYPE_CONTROL_AGENT = 'game_ctl'


class socketClient(threading.Thread):
    """
    client class for socket connections
    """
    def __init__(self, send_buf, recv_buf, server_ip, server_port, agent_id):
        super(socketClient, self).__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.send_buf = send_buf
        self.recv_buf = recv_buf
        self.agent_id = agent_id
        self.conn = None
        self.alive = True
        self.connect()

    def run(self):
        while self.alive:
            try:
                dir = random.choice(['up', 'down', 'left', 'right'])
                logger.info(json.dumps({"type": MESSAGE_TYPE_CONTROL_AGENT, "agent": self.agent_id, "direction": dir}))
                self.sendAgentControl(dir)
                data = self.conn.recv(1024)
                logger.info("Client received data from {server_ip}:{server_port}: {msg}"
                            .format(server_ip=self.server_ip, server_port=self.server_port, msg=data))
                time.sleep(1)
            except Exception as e:
                print(e)
                break
        self.terminate()

    def join(self, timeout=None):
        # self.terminate()
        self.alive = False

    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.server_ip, self.server_port))

    def sendMsg(self, msg):
        self.conn.sendall(json.dumps({'msg': msg}))

    def sendAgentControl(self, dir):
        self.conn.sendall(json.dumps({"type": MESSAGE_TYPE_CONTROL_AGENT, "agent": self.agent_id, "direction": dir}))

    def terminate(self):
        self.conn.close()


if __name__ == "__main__":
    client = socketClient(None, None, '127.0.0.1', 8081, 'B1')
    client.start()
    client.sendMsg({'type': MESSAGE_TYPE_CONNECT_TO_SERVER, 'agent_id': 'B1', 'ip': "testip", 'port': "testport"})
