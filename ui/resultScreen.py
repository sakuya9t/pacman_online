from button import Button
from graphicsUtils import *
from screen import Screen
import graphicsUtils

# Display game results
class ResultScreen(Screen):

    def __init__(self):
        self.name = 'Result'
        self.backButton = Button(500, 400, 'Back', 'orange', 'Menu', self.backButtonFunction)

    def draw(self):
        global result
        graphicsUtils.clear_screen()

        # Draw menu title
        graphicsUtils.rectangle((500, 100), 32, 256, 'red', 1, 0)
        graphicsUtils.text((500, 90), 'white', 'Results', 'Helvetica', 12, 'normal', None)
        graphicsUtils.text((500, 110), 'white', graphicsUtils.result, 'Helvetica', 12, 'normal', None)

        # Draw buttons
        self.backButton.draw()

    def listen(self, pos, type):
        if self.backButton.contains(pos[0], pos[1]):
            self.backButton.click()

    def backButtonFunction(self):
        graphicsUtils.transition('Menu')
