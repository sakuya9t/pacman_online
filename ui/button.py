from graphicsUtils import *
import graphicsUtils

# Simple Button
class Button:

    def __init__(self, x, y, text, color, navigate, function=None):
        self.x = x
        self.y = y
        self.h = 32
        self.w = 64
        self.text = text
        self.color = color
        self.navigate = navigate
        self.function = function

    # Renders the button and text on screen
    def draw(self):
        graphicsUtils.rectangle((self.x, self.y), self.h, self.w, self.color, filled=1, behind=0)
        graphicsUtils.text((self.x, self.y), 'white', self.text, 'Helvetica', 12, 'normal', None)

    # Returns True if a click is registered within the button area
    def contains(self, x, y):
        if (x < (self.x - self.w)) or (x > (self.x + self.w)) or (y < (self.y - self.h)) or y > (self.y + self.h):
            return False
        return True

    # Updates current screen based on button functionality
    def click(self):
        print(self.text)
        self.function()
