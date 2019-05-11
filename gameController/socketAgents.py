import thread
import time

from game import Agent
from game import Directions


class SocketAgent(Agent):
    """
    An agent controlled by the socket.
    """

    def __init__(self, command_buffer, index, server):
        Agent.__init__(self, index)
        self.buffer = command_buffer
        self.lastMove = Directions.STOP
        self.recvDirection = ""
        self.index = index
        self.server = server
        self.keys = []
        self.state = None
        self.ready = False
        thread.start_new_thread(self.constantReceiver, ())

    def constantReceiver(self):
        while True:
            if self.buffer.isEmpty() or self.recvDirection != "":
                continue
            str = self.buffer.pop().strip()
            if str == "left":
                self.recvDirection = Directions.WEST
            elif str == "down":
                self.recvDirection = Directions.SOUTH
            elif str == "right":
                self.recvDirection = Directions.EAST
            elif str == "up":
                self.recvDirection = Directions.NORTH
            else:
                self.recvDirection = Directions.STOP
            self.ready = True
            time.sleep(0.1)

    def getAction(self, state):
        self.server.global_state = state
        legal = state.getLegalActions(self.index)
        move = Directions.STOP

        while True:
            time.sleep(0.01)
            if self.recvDirection == "":
                continue
            else:
                move = self.recvDirection
                self.recvDirection = ""
                break
        #
        # if self.recvDirection != "":
        #     move = self.recvDirection
        #     self.recvDirection = ""
        #     self.ready = False

        # if move == Directions.STOP:
        #     # Try to move in the same direction as before
        #     if self.lastMove in legal:
        #         move = self.lastMove

        if move not in legal:
            move = Directions.STOP

        self.lastMove = move
        return move

