from game import Agent
from game import Directions
import random
import socket
import thread

HOST = "10.96.231.69"
PORT = 10000

class SocketAgent(Agent):
    """
    An agent controlled by the keyboard.
    """
    # NOTE: Arrow keys also work.
    WEST_KEY = 'a'
    EAST_KEY = 'd'
    NORTH_KEY = 'w'
    SOUTH_KEY = 's'
    STOP_KEY = 'q'

    def __init__(self, index=0):

        self.lastMove = Directions.STOP
        self.recvDirection = ""
        self.index = index
        self.keys = []
        self.sr = socReceiver(HOST, PORT)
        thread.start_new_thread(self.constantReceiver, ())

    def constantReceiver(self):
        while 1:
            str = self.sr.receiveData().strip()
            if str == "a":
                self.recvDirection = Directions.WEST
            elif str == "s":
                self.recvDirection = Directions.SOUTH
            elif str == "d":
                self.recvDirection = Directions.EAST
            elif str == "w":
                self.recvDirection = Directions.NORTH
            else:
                self.recvDirection = Directions.STOP
            print self.recvDirection

    def getAction(self, state):
        legal = state.getLegalActions(self.index)
        move = self.lastMove
        if move not in legal:
            move = Directions.STOP

        if self.recvDirection != "":
            move = self.recvDirection
            self.recvDirection= ""

        if move == Directions.STOP:
            # Try to move in the same direction as before
            if self.lastMove in legal:
                move = self.lastMove

        if (self.STOP_KEY in self.keys) and Directions.STOP in legal: move = Directions.STOP

        if move not in legal:
            move = random.choice(legal)

        self.lastMove = move
        return move

    def getMove(self, legal):
        move = Directions.STOP
        if (self.WEST_KEY in self.keys or 'Left' in self.keys) and Directions.WEST in legal:  move = Directions.WEST
        if (self.EAST_KEY in self.keys or 'Right' in self.keys) and Directions.EAST in legal: move = Directions.EAST
        if (self.NORTH_KEY in self.keys or 'Up' in self.keys) and Directions.NORTH in legal:   move = Directions.NORTH
        if (self.SOUTH_KEY in self.keys or 'Down' in self.keys) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move


class SocketAgent2(SocketAgent):
    """
    A second agent controlled by the keyboard.
    """
    # NOTE: Arrow keys also work.
    WEST_KEY = 'j'
    EAST_KEY = "l"
    NORTH_KEY = 'i'
    SOUTH_KEY = 'k'
    STOP_KEY = 'u'

    def getMove(self, legal):
        move = Directions.STOP
        if (self.WEST_KEY in self.keys) and Directions.WEST in legal:  move = Directions.WEST
        if (self.EAST_KEY in self.keys) and Directions.EAST in legal: move = Directions.EAST
        if (self.NORTH_KEY in self.keys) and Directions.NORTH in legal:   move = Directions.NORTH
        if (self.SOUTH_KEY in self.keys) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move


class socReceiver():
    def __init__(self, host, port):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind((host, port))
        self.soc.listen(10)
        print 'listening'
        self.connection, soc_addr = self.soc.accept() #blocked

    def receiveData(self):
        return self.connection.recv(1024)

    def closeSocket(self):
        self.soc.close()