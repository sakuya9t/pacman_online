from button import Button
from graphicsUtils import *
from screen import Screen
import graphicsUtils

# Join Game
class RoomScreen(Screen):

    def __init__(self):
        self.name = 'Room'
        self.playButton = Button(500, 300, 'Play', 'green', 'Play', self.playButtonFunction)
        self.backButton = Button(500, 400, 'Back', 'orange', 'Menu', self.backButtonFunction)

    def draw(self):
        graphicsUtils.clear_screen()

        # Draw menu title
        graphicsUtils.rectangle((500, 100), 32, 256, 'red', 1, 0)
        graphicsUtils.text((500, 90), 'white', '*To be implemented* Looking for a game', 'Helvetica', 12, 'normal', None)
        graphicsUtils.text((500, 110), 'white', 'Click "Play" for default game', 'Helvetica', 12, 'normal', None)

        # Draw buttons
        self.playButton.draw()
        self.backButton.draw()

    def listen(self, pos, type):
        if self.playButton.contains(pos[0], pos[1]):
            self.playButton.click()
        if self.backButton.contains(pos[0], pos[1]):
            self.backButton.click()

    def playButtonFunction(self):
        graphicsUtils.transition('Game')

    def backButtonFunction(self):
        graphicsUtils.transition('Menu')
