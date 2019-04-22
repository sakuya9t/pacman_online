from button import Button
from graphicsUtils import *
from screen import Screen
import globals

# About Description
class AboutScreen(Screen):

    def __init__(self):
        self.name = 'About'
        self.backButton = Button(320, 400, 'Back', 'orange', 'Menu', self.backButtonFunction)

    def draw(self):
        clear_screen()

        # Draw menu title
        rectangle((320, 100), 32, 256, 'red', 1, 0)
        text((320, 90), 'white', 'COMP90020 Distributed Algorithms', 'Helvetica', 12, 'normal', None)
        text((320, 110), 'white', 'Project Semester 1 2019', 'Helvetica', 12, 'normal', None)

        # Draw buttons
        self.backButton.draw()

    def listen(self, pos, type):
        if self.backButton.contains(pos[0], pos[1]):
            self.backButton.click()

    def backButtonFunction(self):
        globals.transition('Menu')
