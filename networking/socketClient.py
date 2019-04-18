import random
import socket
import time
from logger import logger
import json


class socketClient:
    def __init__(self, send_buf, recv_buf, server_ip, server_port, agent_id):
        self.server_ip = server_ip
        self.server_port = server_port
        self.send_buf = send_buf
        self.recv_buf = recv_buf
        self.agent_id = agent_id

    def connect(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.server_ip, self.server_port))
        while True:
            try:
                dir = random.choice(['up', 'down', 'left', 'right'])
                logger.info(json.dumps({"agent": self.agent_id, "direction": dir}))
                conn.sendall(json.dumps({"agent": self.agent_id, "direction": dir}))
                data = conn.recv(1024)
                time.sleep(1)
            except Exception as e:
                print(e)
                break
        conn.close()


if __name__ == "__main__":
    client = socketClient(None, None, '127.0.0.1', 8080, 'B1')
    client.connect()
