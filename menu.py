from graphicsUtils import *

# Keeps track of the current screen displayed
currentScreen = None
exit = False

# Simple Button
class Button:

    def __init__(self, x, y, text, color, navigate):
        self.x = x
        self.y = y
        self.h = 32
        self.w = 64
        self.text = text
        self.color = color
        self.navigate = navigate

    # Renders the button and text on screen
    def draw(self):
        rectangle((self.x, self.y), self.h, self.w, self.color, filled=1, behind=0)
        text((self.x, self.y), 'white', self.text, 'Helvetica', 12, 'normal', None)

    # Returns True if a click is registered within the button area
    def contains(self, x, y):
        if (x < (self.x - self.w)) or (x > (self.x + self.w)) or (y < (self.y - self.h)) or y > (self.y + self.h):
            return False
        return True

    # Updates current screen based on button functionality
    def click(self):
        global currentScreen
        global exit
        if self.navigate == 'About':
            currentScreen = AboutScreen()
        elif self.navigate == 'Menu':
            currentScreen = MenuScreen()
        elif self.navigate == 'Room':
            currentScreen = RoomScreen()
        elif self.navigate == 'Quit':
            exit = True
        print(self.text)

# A Screen
class Screen:

    def __init__(self):
        super().__init__()

    def draw(self):
        pass

    def listen(self, pos, type):
        pass

# Main Menu
class MenuScreen(Screen):

    def __init__(self):
        self.name = 'Menu'
        self.startButton = Button(320, 300, 'Start', 'green', 'Room')
        self.aboutButton = Button(320, 400, 'About', 'blue', 'About')
        self.quitButton = Button(576, 448, 'Quit', 'red', 'Quit')

    def draw(self):
        clear_screen()

        # Draw menu title
        rectangle((320, 100), 32, 256, 'red', 1, 0)
        text((320, 90), 'white', 'Distributed Pacman', 'Helvetica', 12, 'normal', None)
        text((320, 110), 'white', 'Zijian Wang | Nai Wang | Leewei Kuo | Ivan Chee', 'Helvetica', 12, 'normal', None)

        # Pacman logo
        circle((320, 200), 32, 'red', 'yellow', None, 'pieslice', 2)

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

# Join Game
class RoomScreen(Screen):

    def __init__(self):
        self.name = 'Room'
        self.backButton = Button(320, 400, 'Back', 'orange', 'Menu')

    def draw(self):
        clear_screen()

        # Draw menu title
        rectangle((320, 100), 32, 256, 'red', 1, 0)
        text((320, 100), 'white', 'Looking for a game', 'Helvetica', 12, 'normal', None)

        # Draw buttons
        self.backButton.draw()

    def listen(self, pos, type):
        if self.backButton.contains(pos[0], pos[1]):
            self.backButton.click()

# About Description
class AboutScreen(Screen):

    def __init__(self):
        self.name = 'About'
        self.backButton = Button(320, 400, 'Back', 'orange', 'Menu')

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

# Main function
if __name__ == '__main__':

    # Initialise graphics
    begin_graphics(640, 480, formatColor(0, 0, 0), "Distributed Pacman")

    # Set the menu screen as the point of entry
    currentScreen = MenuScreen()

    # Listen for events
    while (not exit):
        currentScreen.draw()
        pos, type = wait_for_click()
        print(pos, type, currentScreen)
        currentScreen.listen(pos, type)
    end_graphics()

#square((320, 300), 32, 'red', filled=1, behind=0)
# begin_graphics()
# clear_screen()
# ghost_shape = [(x * 10 + 20, y * 10 + 20) for x, y in ghost_shape]
# g = polygon(ghost_shape, formatColor(1, 1, 1))
# move_to(g, (50, 50))
# circle((150, 150), 20, formatColor(0.7, 0.3, 0.0), endpoints=[15, - 15])
# sleep(2)