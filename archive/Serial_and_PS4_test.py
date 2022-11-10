#***************************************************************
#* Combination of PS4 test script and teensy communication     *
#* script to transfer button presses to the pi and then        *
#* teensy, receving confirmation from teensie                  *
#***************************************************************

from pyPS4Controller.controller import Controller
import serial

#Function to pad the output chars to length 120 (127- serial ad-ons)
def padStr(val):
    for x in range (120-len(val)):
        val = val + "~"
    return val

#Function to remove all ~ padding
def rmPadStr(val):
    outputStr = ""
    for curChar in val:
        if curChar != '~':
            outputStr += curChar
    return outputStr
    
#Function to communicate and output to teensy by a given string
def serialRead_Write(output):
    #Write out what the pi is sending
    print("Pi: " + output)
    output = padStr(output)
    
    #Write out to the serial buffer
    ser.write(output.encode())
    
    #Collect from serial buffer, trim the extra bits, then print
    inp = str(ser.readline())
    inp = inp[2:-5]
    inp = rmPadStr(inp)
    print(inp)
    #print (str(ser.readline()))


class MyController(Controller):
    mode = 0
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

    #Code for when X has been pressed
    def on_x_press(self):
        serialRead_Write("X")

    def on_x_release(self):
    #Do nothing on X release
        pass
    
    #Code for when Square has been pressed
    def on_square_press(self):
        serialRead_Write("Square")
        
    def on_square_release(self):
        pass
    
    #Code for when circle has been pressed
    def on_circle_press(self):
        serialRead_Write("Circle")
        
    def on_circle_release(self):
        pass
    
    #Code for mode changing
    def on_R1_press(self):
        #print("Start mode: ", MyController.mode)
        MyController.mode =  0 if MyController.mode >= 5 else MyController.mode + 1
        print("Mode is now: ", MyController.mode)
        
    def on_R1_release(self):
        pass
        
    def on_L1_press(self):
        MyController.mode =  5 if MyController.mode <= 0 else MyController.mode - 1
        print("Mode is now: ", MyController.mode)
        
    def on_L1_release(self):
        pass
        
ser = serial.Serial('/dev/ttyACM0',9600)
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen(timeout=60)
print("Timeout")
print("Mode is : ", mode)