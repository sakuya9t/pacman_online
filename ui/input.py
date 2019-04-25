import graphicsUtils
import Tkinter

# Text Input
class Input:

    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.input = Tkinter.Entry(graphicsUtils._canvas, width=20, borderwidth=0, justify=Tkinter.CENTER)

        self.input.insert(12, value)
        self.input.pack()
        # self.input.focus_force()

    # Renders the text input
    def draw(self):
        graphicsUtils.rectangle((self.x, self.y), 32, 64, 'white', filled=1, behind=0)
        graphicsUtils.entry((self.x, self.y), self.input)

    # Gets the value of the text input
    def get(self):
        return self.input.get()
