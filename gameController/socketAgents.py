# COMP90020 Distributed Algorithms project
# Author: Zijian Wang 950618, Nai Wang 927209, Leewei Kuo 932975, Ivan Chee 736901

import thread
import time

from game import Agent
from game import Directions


MESSAGE_TYPE_GAME_STATE = 'sync_game_state'


class SocketAgent(Agent):
    """
    An agent controlled by the socket.
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
        self.multicastGameState()
        self.server.global_state = state
        legal = state.getLegalActions(self.index)
        root_window = self.display.root_window
        if self.server.sequencer is None:
            self.updateGameStateAccordingtoDecision(root_window, state)

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

    def multicastGameState(self):
        data = self.server.game.state.data
        seq = self.server.sequencer
        if seq is not None and data is not None:
            data_dump = data.json()
            self.server.sendToAllOtherPlayers(MESSAGE_TYPE_GAME_STATE, data_dump)

    def updateGameStateAccordingtoDecision(self, root_window, state):
        curr_time = state.data.timeleft
        decision_map = self.server.decision_map
        while True:
            if curr_time in decision_map.keys():
                # todo: unpack decision and update self.server.game.state.data
                del decision_map[curr_time]
                break
            root_window.update()
            time.sleep(0.01)
