from pyPS4Controller.controller import Controller
import serial
import threading
import time
import PySimpleGUI as sg    

print ("Hello from pi_gui.py!")

sg.theme('DarkGreen2')

x1 = "hello"

tab1_layout = [[sg.Text('Hello World!', key='text')],
          [sg.Button('Change Text', key='button'), sg.Button('Exit')]]

tab2_layout = [[sg.Submit(), sg.Cancel()]] 

tab3_layout = [[sg.Submit(), sg.Cancel()]]  

layout = [[sg.TabGroup([[sg.Tab('Feed', tab1_layout, tooltip='tip'), sg.Tab('Settings', tab2_layout, tooltip='TIP3'), sg.Tab('Info', tab3_layout)]], tooltip='TIP2')],    
          [sg.Button('Read')]]    

window = sg.Window('RamBOTs', layout, size=(800,420))    

def print_controller_values(controller):
    count = 0
    global teensy_message
    teensy_message = ""
    print(teensy_message)
    while True:
        teensy_message = serial_write("L3: ({}, {}) R3: ({}, {})".format(controller.l3_horizontal, controller.l3_vertical, controller.r3_horizontal, controller.r3_vertical))
        time.sleep(0.01)
        if (count < 100):  # delay to allow GUI to set up
            count = count + 1
        else:
            window['text'].update(value=teensy_message)

        
def gui_handler(teensy):
    while True:
        event, values = window.read()    
        print(event,values)    
        if event == sg.WIN_CLOSED:           # way out of UI    
            break
        if event == 'inp':                  # Check if inp changed
            print("inp changed")
            x1 = values['inp']              # Update x1 with the new value of inp
            window['x1'].update(x1)         # Update the value of x1 in the window

def padStr(val):
    for _ in range (120-len(val)):
        val = val + "~"
    return val

#Function to remove all ~ padding
def rmPadStr(val):
    outputStr = ""
    for curChar in val:
        if curChar != '~':
            outputStr += curChar
    return outputStr

def serial_write(string): # use time library to call every 10 ms in separate thread
    ser.write(padStr(string).encode())
    
    inp = str(ser.readline())
    inp = inp[2:-5]
    inp = rmPadStr(inp)
    print("From teensy: " + inp)
    return inp

class MyTeensy:
    def __init__(self):
        self.current_message = ""

    def update_current_message(self, message):
        self.current_message = message     

class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.l3_horizontal = 0
        self.l3_vertical = 0
        self.r3_horizontal = 0
        self.r3_vertical = 0

    def on_L3_up(self, value):
        self.l3_vertical = -value
        
    def on_L3_down(self, value):
        self.l3_vertical = -value

    def on_L3_left(self, value):
        self.l3_horizontal = value
        
    def on_L3_right(self, value):
        self.l3_horizontal = value
        
    def on_L3_x_at_rest(self):
        self.l3_horizontal = 0
        
    def on_L3_y_at_rest(self):
        self.l3_vertical = 0

# Right joystick

    def on_R3_up(self, value):
        self.r3_vertical = -value
        
    def on_R3_down(self, value):
        self.r3_vertical = -value

    def on_R3_left(self, value):
        self.r3_horizontal = value
        
    def on_R3_right(self, value):
        self.r3_horizontal = value
        
    def on_R3_x_at_rest(self):
        self.r3_horizontal = 0
         
    def on_R3_y_at_rest(self):
        self.r3_vertical = 0

# Buttons

    def on_triangle_press(self):
        print("Triangle button pressed")
        window['text'].update(value=teensy_message)

    def on_triangle_release(self):
        print("Triangle button released")



print("hello world")
ser = serial.Serial('/dev/ttyACM0',9600)

controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
teensy = MyTeensy()

print_controller_thread = threading.Thread(target=print_controller_values, args=(controller,))
print_controller_thread.daemon = True
print_controller_thread.start()

pi_gui_thread = threading.Thread(target=gui_handler, args=(teensy,))
pi_gui_thread.daemon = True
pi_gui_thread.start()

controller.listen()
