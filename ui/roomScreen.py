from button import Button
from input import Input
from screen import Screen
import graphicsUtils

# Join Game
class RoomScreen(Screen):

    def __init__(self):
        self.name = 'Room'
        self.connectButton = Button(700, 200, 'Connect', 'blue', 'None', self.connectButtonFunction)
        self.waitButton = Button(500, 200, 'Waiting', 'orange', 'None', self.waitButtonFunction)
        self.playButton = Button(500, 300, 'Play', 'green', 'Play', self.playButtonFunction)
        self.backButton = Button(500, 400, 'Back', 'orange', 'Menu', self.backButtonFunction)
        if graphicsUtils.host:
            self.ipInput = Input(300, 200, '127.0.0.1')
            self.portInput = Input(450, 200, '8080')

    def draw(self):
        graphicsUtils.clear_screen()

        # Draw menu title
        graphicsUtils.rectangle((500, 100), 32, 256, 'red', 1, 0)
        graphicsUtils.text((500, 90), 'white', 'Network game', 'Helvetica', 12, 'normal', None)
        graphicsUtils.text((500, 110), 'white', 'Connect to another peer', 'Helvetica', 12, 'normal', None)

        # Draw buttons
        if graphicsUtils.host:
            if graphicsUtils.connected and self.connectButton.text != 'Connected':
                self.connectButton.text = 'Connected'
                self.connectButton.color = 'Green'
            self.connectButton.draw()
            self.ipInput.draw()
            self.portInput.draw()
        else:
            if graphicsUtils.connected and self.waitButton.text != 'Connected':
                self.waitButton.text = 'Connected'
                self.waitButton.color = 'Green'
            self.waitButton.draw()

        if graphicsUtils.connected:
            self.playButton.draw()
        self.backButton.draw()

    def listen(self, pos, type):
        if graphicsUtils.host:
            if self.connectButton.contains(pos[0], pos[1]):
                self.connectButton.click()
        else:
            if self.waitButton.contains(pos[0], pos[1]):
                self.waitButton.click()
        if self.playButton.contains(pos[0], pos[1]):
            self.playButton.click()
        if self.backButton.contains(pos[0], pos[1]):
            self.backButton.click()

    def connectButtonFunction(self):
        ip = self.ipInput.get()
        port = self.portInput.get()
        connect = 'connect {} {}'.format(ip, port)
        # Simulate typing connect ip port
        graphicsUtils.server.input_queue.push({'msg': connect})

    def waitButtonFunction(self):
        pass

    def playButtonFunction(self):
        # Simulate typing gamestart
        graphicsUtils.server.input_queue.push({'msg': 'gamestart'})
        graphicsUtils.transition('Game')

    def backButtonFunction(self):
        graphicsUtils.transition('Select')
