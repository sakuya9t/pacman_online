import json
SRC_IP = "ip"
SRC_PORT = "port"

MESSAGE_TYPE = "message_type"
MESSAGE_TYPE_CONNECT_TO_SERVER = 'cli_conn'
MESSAGE_TYPE_CONTROL_AGENT = 'game_ctl'
MESSAGE_TYPE_NORMAL_MESSAGE = 'normal_message'
MESSAGE_TYPE_CONNECT_CONFIRM = 'cli_conn_ack'
MESSAGE_TYPE_START_GAME = 'start_game'
MESSAGE_TYPE_HOLDBACK = 'holdback'
MESSAGE_TYPE_NO_ORDER_CONTROL = 'no_order_control'
MESSAGE_TYPE_GET_READY = 'get_ready'
MESSAGE_TYPE_EXISTING_NODES = 'nodes_list'

MESSAGE_BODY = "message_body"
SENDER_ROLE = "sender_role"

STATUS_READY = 'ready'
STATUS_NOT_READY = 'not_ready'
SEQUENCER = "B1"

class message ():
    def __init__ (self, from_ip, from_port, msg_type, sender_role, msg_body):
        self.msg = {}
        self.msg.update({SRC_IP, from_ip})
        self.msg.update({SRC_PORT, int(from_port)})
        self.msg.update({MESSAGE_TYPE: msg_type})
        self.msg.update({SENDER_ROLE: sender_role})
        self.msg.update({MESSAGE_BODY: msg_body})

    def __init__ (self, from_ip, from_port, msg_type, msg_body):
        self.msg = {}
        self.msg.update({SRC_IP, from_ip})
        self.msg.update({SRC_PORT, int(from_port)})
        self.msg.update({MESSAGE_TYPE: msg_type})
        self.msg.update({MESSAGE_BODY: msg_body})


    def __init__ (self, recv_string):
        self.msg = json.loads(recv_string)

    def toSendString(self):
        return json.dumps(self.msg)

    def updateMsgContent (self, key, value):
        self.msg.update({key, value})

    def getMsgContent (self, key):
        return self.msg[key]
