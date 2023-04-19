#TODO:
#implement teensy_serial_main_demo [MAKE SURE TO SUBTRACT 1 FROM MOVEMENT ARR VALUES]
#add trigger lock and roll
#add bountds to mode 0=walk, 1=pushups, 2=left side right side control, 3=machine learning????, 4=gyro demo

from pyPS4Controller.controller import Controller
import serial
import threading
import time
import subprocess


def rgb(m):
    if m == 0:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 255 255 255"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    elif m == 1:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 255 255 0"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    elif m == 2:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 0 255 0"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    elif m == 3:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 8 208 96"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    elif m == 4:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 255 0 255"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    elif m == -1:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 0 0 255"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    else:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 255 0 0"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

        
def joystick_map_to_range(original_value):
    mapped_value = ((original_value + 32767) / 65535) * 2 - 1
    return mapped_value

#Function to map a range of [-65534,65198] to [-1,1] with 0 in the middle
def trigger_map_to_range(value):
    if(value < 0):
        return (value/65534)
    elif(value > 0):
        return (value/65198)        
    else:
        return 0

#Function to map a range of [-65534,65198] to [-1,1] with 0 in the middle
def joey_trigger_map_to_range(value):
    newValue = (value+168)/65366
    return newValue
        
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

def serial_read_write(string): # use time library to call every 10 ms in separate thread
    ser.write(padStr(string).encode())
    
    inp = str(ser.readline())
    inp = inp[2:-5]
    inp = rmPadStr(inp)
    print("From teensy: " + inp)
    return

def driver_thread_funct(controller):
    #Create variables
    runningMode = 0
    joystickArr = [0.000, 0.000, 0.000, 0.000, 0.000]
    axisLabelArr = ["Lx", "Ly", "L2", "Rx", "Ry", "R2"]
    rgb(0)
    
    #running section
    while True:
        runningMode = controller.mode
        #0 = strafe, 1 = forback, 2 = roll, 3 = turn, 4 = pitch
        #0 = L3LR, 1 = L3UD, 2 = Triggers, 3 = R3LR, 4 = R3UD
        joystickArr[0] = joystick_map_to_range(controller.l3_horizontal)+1
        joystickArr[1] = joystick_map_to_range(controller.l3_vertical)+1
        joystickArr[2] = trigger_map_to_range(controller.triggers)+1
        joystickArr[3] = joystick_map_to_range(controller.r3_horizontal)+1
        joystickArr[4] = joystick_map_to_range(controller.r3_vertical)+1

        serial_read_write(''',{0:.3f},{1:.3f},{2:.3f},{3:.3f},{4:.3f},M:{5},LD:{6},RD:{7},UD:{8},DD:{9},Sq:{10},Tr:{11},Ci:{12},Xx:{13},Sh:{14},Op:{15},Ps:{16},L3:{17},R3:{18}'''
        .format(joystickArr[0], joystickArr[1], joystickArr[2], joystickArr[3], joystickArr[4],
        runningMode, controller.dpadArr[0], controller.dpadArr[1],
        controller.dpadArr[2], controller.dpadArr[3], controller.shapeButtonArr[0],
        controller.shapeButtonArr[1], controller.shapeButtonArr[2], controller.shapeButtonArr[3],
        controller.miscButtonArr[0], controller.miscButtonArr[1], controller.miscButtonArr[2],
        controller.miscButtonArr[3], controller.miscButtonArr[4]))

#        serial_read_write("L3: ({}, {}) R3: ({}, {}) Mode: ({})".format(controller.l3_horizontal, controller.l3_vertical, controller.r3_horizontal, controller.r3_vertical, runningMode))
        #time.sleep(0.01)

class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.l3_horizontal = 0
        self.l3_vertical = 0
        self.r3_horizontal = 0
        self.r3_vertical = 0
        self.triggers = 0
        self.modeMax = 4
        self.mode = 0
        self.dpadArr = [0,0,0,0] #L,R,U,D
        self.shapeButtonArr = [0,0,0,0] #Sq, Tr, Cir, X
        self.miscButtonArr = [0,0,0,0,0] #Share, Options, PS, L3, R3
        self.triggerLock = 0
        

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
                
    def on_R3_up(self, value):
        self.r3_vertical = -value
        
    def on_R3_down(self, value):
        self.r3_vertical = -value

    def on_R3_left(self, value):
        self.r3_horizontal = -value
        
    def on_R3_right(self, value):
        self.r3_horizontal = -value
        
    def on_R3_x_at_rest(self):
        self.r3_horizontal = 0
         
    def on_R3_y_at_rest(self):
        self.r3_vertical = 0

    def on_L1_press(self):
        if self.mode <= 0:
            self.mode = self.modeMax
        else:
            self.mode = self.mode-1
        rgb(self.mode)
        
    def on_L1_release(self):
        pass
        
    def on_R1_press(self):
        if self.mode >= self.modeMax:
            self.mode = 0
        else:
            self.mode = self.mode+1
        rgb(self.mode)
        
    def on_R1_release(self):
        pass
        
    def on_square_press(self):
        self.shapeButtonArr[0] = 1
        
    def on_square_release(self):
        self.shapeButtonArr[0] = 0
        
    def on_triangle_press(self):
        self.shapeButtonArr[1] = 1
        
    def on_triangle_release(self):
        self.shapeButtonArr[1] = 0
        
    def on_circle_press(self):
        self.shapeButtonArr[2] = 1
        
    def on_circle_release(self):
        self.shapeButtonArr[2] = 0
        
    def on_x_press(self):
        self.shapeButtonArr[3] = 1
        
    def on_x_release(self):
        self.shapeButtonArr[3] = 0
        
    def on_up_arrow_press(self):
        self.dpadArr[2] = 1
        
    def on_up_down_arrow_release(self):
        self.dpadArr[2] = 0
        self.dpadArr[3] = 0
        
    def on_down_arrow_press(self):
        self.dpadArr[3] = 1
        
    def on_left_arrow_press(self):
        self.dpadArr[0] = 1
        
    def on_left_right_arrow_release(self):
        self.dpadArr[0] = 0
        self.dpadArr[1] = 0
        
    def on_right_arrow_press(self):
        self.dpadArr[1] = 1
        
    def on_L3_press(self):
        self.miscButtonArr[3] = 1
        
    def on_L3_release(self):
        self.miscButtonArr[3] = 0
        
    def on_R3_press(self):
        self.miscButtonArr[4] = 1
        
    def on_R3_release(self):
        self.miscButtonArr[4] = 0
        
    def on_options_press(self):
        self.miscButtonArr[1] = 1
        
    def on_options_release(self):
        self.miscButtonArr[1] = 0
        
    def on_share_press(self):
        self.miscButtonArr[0] = 1
        
    def on_share_release(self):
        self.miscButtonArr[0] = 0
        
    def on_playstation_button_press(self):
        self.miscButtonArr[2] = 1

    def on_playstation_button_release(self):
        self.miscButtonArr[2] = 0
        
    def on_R2_press(self,value):
        if(self.triggerLock == 0 or self.triggerLock == 1):
            self.triggerLock = 1
            self.triggers = value + 32431
        
    def on_R2_release(self):
        if(self.triggerLock == 1):
            self.triggerLock = 0
            self.triggers = 0
        
    def on_L2_press(self,value):
        if(self.triggerLock == 0 or self.triggerLock == 2):
            self.triggerLock = 2
            self.triggers = -1*(value + 32767)
        
    def on_L2_release(self):
        if(self.triggerLock == 2):
            self.triggerLock = 0
            self.triggers = 0
        


print("hello world")
ser = serial.Serial('/dev/ttyACM0',9600)

controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)

driver_thread = threading.Thread(target=driver_thread_funct, args=(controller,))
driver_thread.daemon = True
driver_thread.start()



controller.listen()
