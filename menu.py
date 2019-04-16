from graphicsUtils import *

# Simple Button
class Button:

    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.h = 32
        self.w = 64
        self.text = text
        self.color = color

    def draw(self):
        rectangle((self.x, self.y), self.h, self.w, self.color, filled=1, behind=0)
        text((self.x, self.y), 'yellow', self.text, 'Helvetica', 12, 'normal', None)

    def contains(self, x, y):
        if x < (self.x - self.w):
            return False
        if x > (self.x + self.w):
            return False
        if y < (self.y - self.h):
            return False
        if y > (self.y + self.h):
            return False
        return True

    def click(self):
        print(self.text)

# Main function
if __name__ == '__main__':

    # Initialise graphics
    begin_graphics(640, 480, formatColor(0, 0, 0), "Distributed Pacman")
    clear_screen()

    # Draw menu title
    rectangle((320, 100), 32, 256, 'red', 1, 0)
    text((320, 90), 'yellow', 'Distributed Pacman', 'Helvetica', 12, 'normal', None)
    text((320, 110), 'yellow', 'Zijian Wang | Nai Wang | Leewei Kuo | Ivan Chee', 'Helvetica', 12, 'normal', None)

    # Pacman logo
    circle((320, 200), 32, 'red', 'yellow', None, 'pieslice', 2)

    # Create buttons
    startButton = Button(320, 300, 'Start', 'green')
    aboutButton = Button(320, 400, 'About', 'blue')
    startButton.draw()
    aboutButton.draw()

    # Listen for events
    while (True):
        pos, type = wait_for_click()
        print(pos, type)
        if startButton.contains(pos[0], pos[1]):
            startButton.click()
        if aboutButton.contains(pos[0], pos[1]):
            aboutButton.click()

#square((320, 300), 32, 'red', filled=1, behind=0)
# begin_graphics()
# clear_screen()
# ghost_shape = [(x * 10 + 20, y * 10 + 20) for x, y in ghost_shape]
# g = polygon(ghost_shape, formatColor(1, 1, 1))
# move_to(g, (50, 50))
# circle((150, 150), 20, formatColor(0.7, 0.3, 0.0), endpoints=[15, - 15])
# sleep(2)