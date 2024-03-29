# COMP90020 Distributed Algorithms project
# Author: Zijian Wang 950618, Nai Wang 927209, Leewei Kuo 932975, Ivan Chee 736901

import thread
import time

from game import Agent
from game import Directions


class SocketAgent(Agent):
    """
    An online agent controlled by the socket.
    """

    def __init__(self, command_buffer, index, server, display):
        Agent.__init__(self, index)
        self.buffer = command_buffer
        self.lastMove = Directions.STOP
        self.recvDirection = ""
        self.index = index
        self.server = server
        self.keys = []
        self.display = display
        self.state = None
        self.ready = False
        self.life_map = self.server.life_map
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

    # returns the action of self.recvDirection
    # if no message is received and the corresponding process is not dead,
    # getAction will hold and wait until a message is received. This will
    # stuck the while loop in game.py so that other players cannot move.
    def getAction(self, state):
        self.server.global_state = state
        root_window = self.display.root_window
        legal = state.getLegalActions(self.index)

        move = Directions.STOP

        # if life_map is false, means that the process that controls
        # this agent has crashed. getAction will return Directions.STOP
        while True and self.life_map[self.index]:
            time.sleep(0.01)
            root_window.update()
            if self.recvDirection == "":
                continue
            else:
                move = self.recvDirection
                self.recvDirection = ""
                break

        if move not in legal:
            move = Directions.STOP

        self.lastMove = move
        return move

