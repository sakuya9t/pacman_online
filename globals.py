from ui.aboutScreen import AboutScreen
from ui.menuScreen import MenuScreen
from ui.resultScreen import ResultScreen
from ui.roomScreen import RoomScreen

# Keeps track of the current screen displayed
global screen

# Determines whether the program should exit
global exit

# Keeps track of the previous game's result
global result

# Server component
global server

# Command line options
global options

def transition(name):
    global screen
    if name == 'About':
        screen = AboutScreen()
    elif name == 'Menu':
        screen = MenuScreen()
    elif name == 'Room':
        screen = RoomScreen()
    elif name == 'Result':
        screen = ResultScreen()

def initialize():
    global screen
    global exit
    global result
    # Set the menu screen as the point of entry
    screen = MenuScreen()
    exit = False
    result = ''

def draw():
    global screen
    print(screen)
    screen.draw()
