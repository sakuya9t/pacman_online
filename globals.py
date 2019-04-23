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
    global playing

    # Set the menu screen as the point of entry
    screen = MenuScreen()
    exit = False
    playing = False
    result = ''

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
        pos, type = wait_for_click()
        screen.listen(pos, type)
        if playing:
            # Switch to pacman graphics and simulate typing gamestart
            screen = options['display']
            server.input_queue.push({'msg': 'gamestart'})

            game_runner = gameRunner(server=server, options=options)
            game_runner.start()

            # TODO: MERGE THIS WITH MAIN WHILE LOOP
            while playing:
                # pos, type = wait_for_click()
                # screen.listen(pos, type)
                continue

            game_runner.join()

            clear_screen()
            transition('Result')
    end_graphics()

def draw():
    global screen
    print(screen)
    screen.draw()
