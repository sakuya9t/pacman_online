from graphicsUtils import *

# Keeps track of the current screen displayed
currentScreen = None

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

    def draw(self):
        # Renders the button and text on screen
        rectangle((self.x, self.y), self.h, self.w, self.color, filled=1, behind=0)
        text((self.x, self.y), 'white', self.text, 'Helvetica', 12, 'normal', None)

    def contains(self, x, y):
        # Returns True if a click is registered within the button area
        if (x < (self.x - self.w)) or (x > (self.x + self.w)) or (y < (self.y - self.h)) or y > (self.y + self.h):
            return False
        return True

    def click(self):
        # Updates current screen based on button functionality
        global currentScreen
        if self.navigate == 'About':
            currentScreen = AboutScreen()
        elif self.navigate == 'Menu':
            currentScreen = MenuScreen()
        elif self.navigate == 'Room':
            currentScreen = RoomScreen()
        print(self.text)

# Main Menu
class MenuScreen:

    def __init__(self):
        self.name = 'Menu'
        # Create buttons
        self.startButton = Button(320, 300, 'Start', 'green', 'Room')
        self.aboutButton = Button(320, 400, 'About', 'blue', 'About')

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

    def listen(self, pos, type):
        if self.startButton.contains(pos[0], pos[1]):
            self.startButton.click()
        if self.aboutButton.contains(pos[0], pos[1]):
            self.aboutButton.click()

# Join Game
class RoomScreen:

    def __init__(self):
        self.name = 'Room'
        # Create buttons
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
class AboutScreen:

    def __init__(self):
        self.name = 'About'
        # Create buttons
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
    while (True):
        currentScreen.draw()
        pos, type = wait_for_click()
        print(pos, type, currentScreen)
        currentScreen.listen(pos, type)

#square((320, 300), 32, 'red', filled=1, behind=0)
# begin_graphics()
# clear_screen()
# ghost_shape = [(x * 10 + 20, y * 10 + 20) for x, y in ghost_shape]
# g = polygon(ghost_shape, formatColor(1, 1, 1))
# move_to(g, (50, 50))
# circle((150, 150), 20, formatColor(0.7, 0.3, 0.0), endpoints=[15, - 15])
# sleep(2)