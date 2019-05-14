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

    def getAction(self, state):
        self.multicastGameState()
        self.server.global_state = state
        root_window = self.display.root_window
        if self.server.sequencer is None:
            self.updateGameStateAccordingtoDecision(root_window, state)
        legal = self.server.game.state.getLegalActions(self.index)

        move = Directions.STOP
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
        count = 0
        while True:
            # if timeout in 2 seconds, no synchronize
            if count > 200:
                break
            if curr_time in decision_map.keys():
                # unpack decision and update self.server.game.state.data
                data = self.server.game.state.data
                received_data = decision_map[curr_time]
                data.score = received_data['score']
                data.timeleft = received_data['timeleft']
                data.food.data = received_data['food']['data']
                data.capsules = received_data['capsules']
                data._agentMoved = received_data['agentMoved']
                for agent_id in range(4):
                    agent_state = data.agentStates[agent_id]
                    recv_agent_state = received_data['agentStates'][agent_id]
                    agent_state.isPacman = recv_agent_state['isPacman']
                    agent_state.scaredTimer = recv_agent_state['scaredTimer']
                    agent_state.numCarrying = recv_agent_state['numCarrying']
                    agent_state.numReturned = recv_agent_state['numReturned']
                    agent_state.configuration.direction = recv_agent_state['configuration']['direction']
                    agent_state.configuration.pos = recv_agent_state['configuration']['pos']
                if data._agentMoved is not None:
                    self.server.display.update(data)
                del decision_map[curr_time]
                break
            root_window.update()
            time.sleep(0.01)
            count += 1
