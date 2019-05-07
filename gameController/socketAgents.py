import thread
import time

from game import Agent
from game import Directions


class SocketAgent(Agent):
    """
    An agent controlled by the socket.
    """

    def __init__(self, command_buffer, index):
        Agent.__init__(self, index)
        self.buffer = command_buffer
        self.lastMove = Directions.STOP
        self.recvDirection = ""
        self.index = index
        self.keys = []
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
            time.sleep(0.1)

    def getAction(self, state):
        legal = state.getLegalActions(self.index)
        move = Directions.STOP
        if move not in legal:
            move = Directions.STOP

        if self.recvDirection != "":
            move = self.recvDirection
            self.recvDirection= ""

        # if move == Directions.STOP:
        #     # Try to move in the same direction as before
        #     if self.lastMove in legal:
        #         move = self.lastMove

        if move not in legal:
            move = Directions.STOP

        self.lastMove = move
        return move
