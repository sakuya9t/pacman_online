from button import Button
from graphicsUtils import *
from screen import Screen
import graphicsUtils

# About Description
class AboutScreen(Screen):

    def __init__(self):
        self.name = 'About'
        self.backButton = Button(500, 400, 'Back', 'orange', 'Menu', self.backButtonFunction)

    def draw(self):
        graphicsUtils.clear_screen()

        # Draw menu title
        graphicsUtils.rectangle((500, 100), 32, 256, 'red', 1, 0)
        graphicsUtils.text((500, 90), 'white', 'COMP90020 Distributed Algorithms', 'Helvetica', 12, 'normal', None)
        graphicsUtils.text((500, 110), 'white', 'Project Semester 1 2019', 'Helvetica', 12, 'normal', None)

        # Draw buttons
        self.backButton.draw()

    def listen(self, pos, type):
        if self.backButton.contains(pos[0], pos[1]):
            self.backButton.click()

    def backButtonFunction(self):
        graphicsUtils.transition('Menu')
