#***************************************************************
#* Combination of PS4 test script and teensy communication     *
#* script to transfer button presses to the pi and then        *
#* teensy, receving confirmation from teensie                  *
#***************************************************************

from pyPS4Controller.controller import Controller
import serial

class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

    def on_x_press(self):

        print("Pi: X")
        ser.write("X".encode())
        print (str(ser.readline()))
        #print (str(ser.readline()))

    def on_x_release(self):
        pass
    
    def on_square_press(self):
        print("Pi: Square")
        ser.write("Square".encode())
        print (str(ser.readline()))
        #print (str(ser.readline()))
        
    def on_square_release(self):
        pass
    
    def on_circle_press(self):
        print("Pi: Circle")
        ser.write("Circle".encode())
        print (str(ser.readline()))
        #print (str(ser.readline()))
    
    def on_circle_release(self):
        pass
    
ser = serial.Serial('/dev/ttyACM0',9600)
#print (str( ser.readline() ))
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()
print("test")