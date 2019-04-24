# textDisplay.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import time
from graphicsUtils import *
from ui.screen import Screen

try:
    import pacman
except:
    pass

DRAW_EVERY = 1
SLEEP_TIME = 0  # This can be overwritten by __init__
DISPLAY_MOVES = False
QUIET = False  # Supresses output


class NullGraphics:
    def initialize(self, state, isBlue=False):
        pass

    def update(self, state):
        pass

    def checkNullDisplay(self):
        return True

    def pause(self):
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        print state

    def updateDistributions(self, dist):
        pass

    def finish(self):
        pass


class PacmanGraphics(Screen):
    def __init__(self, speed=None):
        if speed != None:
            global SLEEP_TIME
            SLEEP_TIME = speed

    def initialize(self, state, isBlue=False):
        self.drawTerminal(state)
        self.pause()
        self.turn = 0
        self.agentCounter = 0

        # Nothing to draw
        self.drawState = ''

    def update(self, state):
        numAgents = len(state.agentStates)
        self.agentCounter = (self.agentCounter + 1) % numAgents
        if self.agentCounter == 0:
            self.turn += 1
            if DISPLAY_MOVES:
                ghosts = [pacman.nearestPoint(state.getGhostPosition(i)) for i in range(1, numAgents)]
                print "%4d) P: %-8s" % (self.turn, str(
                    pacman.nearestPoint(state.getPacmanPosition()))), '| Score: %-5d' % state.score, '| Ghosts:', ghosts
            if self.turn % DRAW_EVERY == 0:
                self.drawTerminal(state)
                self.pause()
        if state._win or state._lose:
            self.drawTerminal(state)

    def pause(self):
        time.sleep(SLEEP_TIME)

    def draw(self):
        clear_screen()
        text((500, 300), 'white', self.drawState, 'Helvetica', 12, 'normal', None)

    def drawTerminal(self, state):
        print state
        self.drawState = state

    def listen(self, pos, type):
        if self.backButton.contains(pos[0], pos[1]):
            self.backButton.click()

    def finish(self):
        graphicsUtils.playing = False
        graphicsUtils.transition('Result')
        print('Game has ended')
