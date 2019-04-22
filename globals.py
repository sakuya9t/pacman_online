from graphicsUtils import *
from ui.aboutScreen import AboutScreen
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
        print('A game has ended')
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
    begin_graphics(640, 480, formatColor(0, 0, 0), "Distributed Pacman")

    # Listen for events
    while (not exit):
        screen.draw()
        pos, type = wait_for_click()
        screen.listen(pos, type)
        if playing:
            end()
            game_runner = gameRunner(server=server, options=options)
            game_runner.start()
            while playing:
                continue
            game_runner.join()
            print('joined')
            end_graphics()
            print('end')
            begin_graphics(480, 640, formatColor(0, 0, 0), "Hi Pacman")
            #begin_graphics(640, 480, formatColor(0, 0, 0), "Distributed Pacman")
            screen = ResultScreen()
            # globals.reinitialize()
            # globals.transition('Result')
        # if screen == None:
        #     print('RESULT:',result)
        #     begin_graphics(640, 480, formatColor(0, 0, 0), "Distributed Pacman")

def draw():
    global screen
    print(screen)
    screen.draw()

def end():
    global screen
    screen = None
    end_graphics()
