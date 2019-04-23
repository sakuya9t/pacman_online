from graphicsUtils import *
from ui.aboutScreen import AboutScreen
from captureGraphicsDisplay import PacmanGraphics
from ui.menuScreen import MenuScreen
from ui.resultScreen import ResultScreen
from ui.roomScreen import RoomScreen
from gameController.gameRunner import gameRunner

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

# Whether a game is in progress
global playing

# Switch to another screen
def transition(name):
    global screen
    global options
    if name == 'About':
        screen = AboutScreen()
    elif name == 'Game':
        # Switch to pacman graphics and simulate typing gamestart
        screen = options['display']
        startGameRunner()
    elif name == 'Menu':
        screen = MenuScreen()
    elif name == 'Room':
        screen = RoomScreen()
    elif name == 'Result':
        screen = ResultScreen()

# Initialise global variables
def initialize():
    global screen
    global exit
    global result
    global playing

    # Set the menu screen as the point of entry
    screen = MenuScreen()
    exit = False
    playing = False
    result = ''

# Main loop of the UI component
def run():
    global screen
    global exit
    global result
    global playing
    global server
    global options

    # Initialise graphics
    begin_graphics(1000.0, 640.0, formatColor(0, 0, 0), "Distributed Pacman")

    # Listen for events
    while (not exit):
        screen.draw()
        if not playing:
            pos, type = wait_for_click()
            screen.listen(pos, type)

    # Destroy graphics
    end_graphics()

# Start GameRunner class
def startGameRunner():
    global playing
    playing = True
    server.input_queue.push({'msg': 'gamestart'})

    game_runner = gameRunner(server=server, options=options)
    game_runner.start()

# def endGameRunner():
#     game_runner.join()
