from button import Button
from screen import Screen
import graphicsUtils

# Join Game
class SelectScreen(Screen):

    def __init__(self):
        self.name = 'Select'
        self.networkHostButton = Button(400, 200, 'Network\nHost', 'blue', 'Network', self.networkHostButtonFunction)
        self.networkJoinButton = Button(600, 200, 'Network\nJoin', 'blue', 'Network', self.networkJoinButtonFunction)
        self.localButton = Button(500, 300, 'Local', 'green', 'Local', self.localButtonFunction)
        self.backButton = Button(500, 400, 'Back', 'orange', 'Menu', self.backButtonFunction)

    def draw(self):
        graphicsUtils.clear_screen()

        # Draw menu title
        graphicsUtils.rectangle((500, 100), 32, 256, 'red', 1, 0)
        graphicsUtils.text((500, 90), 'white', 'Game Selection', 'Helvetica', 12, 'normal', None)
        graphicsUtils.text((500, 110), 'white', 'Select a game type', 'Helvetica', 12, 'normal', None)

        # Draw buttons
        self.networkHostButton.draw()
        self.networkJoinButton.draw()
        self.localButton.draw()
        self.backButton.draw()

    def listen(self, pos, type):
        if self.networkHostButton.contains(pos[0], pos[1]):
            self.networkHostButton.click()
        if self.networkJoinButton.contains(pos[0], pos[1]):
            self.networkJoinButton.click()
        if self.localButton.contains(pos[0], pos[1]):
            self.localButton.click()
        if self.backButton.contains(pos[0], pos[1]):
            self.backButton.click()

    def networkHostButtonFunction(self):
        graphicsUtils.host = True
        graphicsUtils.transition('Room')

    def networkJoinButtonFunction(self):
        graphicsUtils.host = False
        graphicsUtils.transition('Room')

    def localButtonFunction(self):
        graphicsUtils.transition('Local')

    def backButtonFunction(self):
        graphicsUtils.transition('Menu')
