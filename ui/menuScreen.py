from button import Button
from graphicsUtils import *
from screen import Screen
import globals

# Main Menu
class MenuScreen(Screen):

    def __init__(self):
        self.name = 'Menu'
        self.startButton = Button(500, 300, 'Start', 'green', 'Room', self.startButtonFunction)
        self.aboutButton = Button(500, 400, 'About', 'blue', 'About', self.aboutButtonFunction)
        self.quitButton = Button(500, 500, 'Quit', 'red', 'Quit', self.quitButtonFunction)

    def draw(self):
        clear_screen()

        # Draw menu title
        rectangle((500, 100), 32, 256, 'red', 1, 0)
        text((500, 90), 'white', 'Distributed Pacman', 'Helvetica', 12, 'normal', None)
        text((500, 110), 'white', 'Zijian Wang | Nai Wang | Leewei Kuo | Ivan Chee', 'Helvetica', 12, 'normal', None)

        # Pacman logo
        circle((500, 200), 32, 'red', 'yellow', None, 'pieslice', 2)

        # Draw buttons
        self.startButton.draw()
        self.aboutButton.draw()
        self.quitButton.draw()

    def listen(self, pos, type):
        if self.startButton.contains(pos[0], pos[1]):
            self.startButton.click()
        if self.aboutButton.contains(pos[0], pos[1]):
            self.aboutButton.click()
        if self.quitButton.contains(pos[0], pos[1]):
            self.quitButton.click()

    def startButtonFunction(self):
        globals.transition('Room')

    def aboutButtonFunction(self):
        globals.transition('About')

    def quitButtonFunction(self):
        globals.exit = True
