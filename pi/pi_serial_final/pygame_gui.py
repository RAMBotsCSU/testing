import PySimpleGUI as sg
from pyPS4Controller.controller import Controller

# Create a window with a text element
layout = [[sg.Text('Hello World!', key='text')],
          [sg.Button('Change Text', key='button'), sg.Button('Exit')]]

window = sg.Window('PS4 Controller Text Changer', layout)

# Define a custom controller class that inherits from Controller
class MyController(Controller):
    def __init__(self, window):
        Controller.__init__(self)
        self.window = window

    def on_button_press(self, button):
        if button == 'square':
            self.window['text'].update(value='Text Changed!')

# Create an instance of the custom controller class
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)

controller = MyController(window)

# Start the controller event loop
controller.listen()

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

window.close()
