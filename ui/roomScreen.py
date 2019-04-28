from button import Button
from input import Input
from screen import Screen
import graphicsUtils

# Join Game
class RoomScreen(Screen):

    def __init__(self):
        self.name = 'Room'
        self.connectButton = Button(700, 200, 'Connect', 'blue', 'None', self.connectButtonFunction)
        self.playButton = Button(500, 300, 'Play', 'green', 'Play', self.playButtonFunction)
        self.backButton = Button(500, 400, 'Back', 'orange', 'Menu', self.backButtonFunction)
        self.ip = Input(300, 200, '127.0.0.1')
        self.port = Input(450, 200, '8080')

    def draw(self):
        graphicsUtils.clear_screen()

        # Draw menu title
        graphicsUtils.rectangle((500, 100), 32, 256, 'red', 1, 0)
        graphicsUtils.text((500, 90), 'white', 'Network game', 'Helvetica', 12, 'normal', None)
        graphicsUtils.text((500, 110), 'white', 'Connect to another peer', 'Helvetica', 12, 'normal', None)

        # Draw buttons
        self.playButton.draw()
        self.backButton.draw()
        self.connectButton.draw()

        self.ip.draw()
        self.port.draw()

    def listen(self, pos, type):
        if self.connectButton.contains(pos[0], pos[1]):
            self.connectButton.click()
        if self.playButton.contains(pos[0], pos[1]):
            self.playButton.click()
        if self.backButton.contains(pos[0], pos[1]):
            self.backButton.click()

    def connectButtonFunction(self):
        print(self.ip.get(), self.port.get())

    def playButtonFunction(self):
        graphicsUtils.transition('Game')

    def backButtonFunction(self):
        graphicsUtils.transition('Select')
