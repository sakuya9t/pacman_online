from button import Button
from graphicsUtils import *
from screen import Screen
import globals

# Display game results
class ResultScreen(Screen):

    def __init__(self):
        self.name = 'Result'
        self.backButton = Button(320, 400, 'Back', 'orange', 'Menu', self.backButtonFunction)
        begin_graphics(640, 480, formatColor(0, 0, 0), "Distributed Pacman")

    def draw(self):
        global result
        clear_screen()

        # Draw menu title
        rectangle((320, 100), 32, 256, 'red', 1, 0)
        text((320, 90), 'white', 'Results', 'Helvetica', 12, 'normal', None)
        text((320, 110), 'white', globals.result, 'Helvetica', 12, 'normal', None)

        # Draw buttons
        self.backButton.draw()

    def listen(self, pos, type):
        if self.backButton.contains(pos[0], pos[1]):
            self.backButton.click()

    def backButtonFunction(self):
        globals.transition('Menu')
