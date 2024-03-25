import serial
import time
from serial.serialutil import SerialException
import pygame
import threading
from pygame.locals import *
import re
# Function to map joystick value to a range of [-1, 1]
def joystick_map_to_range(original_value):
    return ((original_value + 32767) / 65535) * 2 - 1

# Function to map a range of [-65534, 65198] to [-1, 1] with 0 in the middle
def trigger_map_to_range(value):
    if value < 0:
        return value / 65534
    elif value > 0:
        return value / 65198
    else:
        return 0

# Function to pad a string with '~' to a fixed length
def padStr(val):
    for _ in range(120 - len(val)):
        val = val + "~"
    return val

# Function to remove all '~' padding from a string
def rmPadStr(val):
    return val.replace('~', '')

class MyController:
    def __init__(self):
        # Initialize controller attributes here
        self.dpadArr = [0, 0, 0, 0]  # L, R, U, D
        self.shapeButtonArr = [0, 0, 0, 0]  # Sq, Tr, Cir, X
        self.miscButtonArr = [0, 0, 0, 0, 0]  # Share, Options, PS, L3, R3

    # Define controller event handlers here
        
def process_odrive_params(params):
    print("Error with params")
    exit()

# Function to read from and write to the serial port
def serial_read_write(string, ser):
    ser.write(padStr(string).encode())
    return getLineSerial(ser)

def getLineSerial(ser):
    line = str(ser.readline())
    line = line[2:-5]
    line = rmPadStr(line)
    return line

def driver_thread_funct(ser):
    # Initialize joystickArr
    joystickArr = [1.000, 1.000, 1.000, 1.000, 1.000, 1.000]
    dpadArr = [0, 0, 0, 0]
    shapeButtonArr = [0, 0, 0, 0]
    miscButtonArr = [0, 0, 0, 0, 0]

    curr_odrive = ""

    odrive_params = {"odrive1": {"axis0":{}, "axis1": {}},
                     "odrive2": {"axis0":{}, "axis1": {}},
                     "odrive3": {"axis0":{}, "axis1": {}},
                     "odrive4": {"axis0":{}, "axis1": {}},
                     "odrive5": {"axis0":{}, "axis1": {}},
                     "odrive6": {"axis0":{}, "axis1": {}}}

    runningMode = 0
    modeMax = 6
    joystick_threshold = 0.1
    index = 0
    # controller.shapeButtonArr[3] = 1
    while True:
        # Read controller inputs and perform necessary actions
        # ...
        for event in pygame.event.get():
            # Call controller.update from the main thread
            if (event.type == JOYBUTTONUP):
                if (event.dict['button'] == 0): # X btn release
                    shapeButtonArr[3] = 0

            if (event.type == JOYBUTTONDOWN):
                if (event.dict['button'] == 15): # TOuchpad press
                    print("EXIT")
                    exit()
                if (event.dict['button'] == 0): # X button
                    shapeButtonArr[3] = 1

                if (event.dict['button'] == 9): # Left Bumper
                    if runningMode <= 0:
                        runningMode = modeMax
                    else:
                        runningMode = runningMode-1
                    print("Mode:", runningMode)

                if (event.dict['button'] == 10): # Right Bumper
                    if runningMode >= modeMax:
                        runningMode = 0
                    else:
                        runningMode = runningMode+1
                    print("Mode:", runningMode)

            if (event.type == JOYAXISMOTION):
                # print(event.dict)
                if (event.dict['axis'] == 0):
                    if (abs(event.dict["value"]) > joystick_threshold):
                        joystickArr[0] = event.dict["value"] + 1
                    else:
                        joystickArr[0] = 1.0
                elif (event.dict['axis'] == 1):
                    if (abs(event.dict["value"]) > joystick_threshold):
                        joystickArr[1] = event.dict["value"] + 1
                    else:
                        joystickArr[1] = 1.0



        # Send data to the connected USB serial device
        data = '''J0:{0:.3f},J1:{1:.3f},J2:{2:.3f},J3:{3:.3f},J4:{4:.3f},J5:{5:.3f},M:{6},LD:{7},RD:{8},UD:{9},DD:{10},Sq:{11},Tr:{12},Ci:{13},Xx:{14},Sh:{15},Op:{16},Ps:{17},L3:{18},R3:{19},#'''.format(joystickArr[0], joystickArr[1], joystickArr[2], joystickArr[3], joystickArr[4], joystickArr[5],
        runningMode, dpadArr[0], dpadArr[1],
        dpadArr[2], dpadArr[3], shapeButtonArr[0],
        shapeButtonArr[1], shapeButtonArr[2], shapeButtonArr[3],
        miscButtonArr[0], miscButtonArr[1], miscButtonArr[2],
        miscButtonArr[3], miscButtonArr[4])

        data_returned = serial_read_write(data, ser)
        print(index, data_returned)

        if (runningMode == 6):
            line = getLineSerial(ser)
            if ("odrive" in line):
                # Header print statement indicating which odrive is being dumped
                curr_odrive = line

                while True:
                    line = getLineSerial(ser)

                    print(line)
                    if ("END" in line):
                        runningMode = 0
                        print("Params:",odrive_params)
                        break

                    elif ("odrive" in line):
                        # Header print statement indicating which odrive is being dumped
                        curr_odrive = line

                    else:
                        data_return_val_num = len(line.split(" "))
                        if data_return_val_num == 2:
                            key = line.split(" ")[0]
                            value = line.split(" ")[1]
                            odrive_params[curr_odrive][key] = value
                        elif data_return_val_num == 3:
                            axis = line.split(" ")[0]
                            key = line.split(" ")[1]
                            value = line.split(" ")[2]
                            odrive_params[curr_odrive][axis][key] = value
                

        # time.sleep(0.1)
        index += 1

# def controller_listen():
#     # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
#     # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
#     running = True
#     while running:
        # Handle events

        

device_path = "/dev/tty.usbmodem147121401" # Teensy on Single Leg
# device_path = "/dev/tty.usbmodem104477401" # Teensy on Robot

def main():
    print("hello world")
    try:
        ser = serial.Serial(device_path, 9600) # Run ls /dev/tty.* on mac to find teensy path
        print("Found Device")
    except SerialException as e:
        print(f"An error occurred: {e}. \nPlease unplug the USB to the Teensy, press stop, and plug it in again.")
        # Handle error and play sound
        # pygame.mixer.Sound.play(error)
        while(1):
            pass
    

    # Initialize Pygame
    pygame.init()
    # Initialize Pygame's joystick module
    pygame.joystick.init()

    # Check for available joysticks
    joystick_count = pygame.joystick.get_count()
    print("joystick_count", joystick_count)
    # Iterate through available joysticks to find the PS4 controller
    for i in range(joystick_count):
        joystick_name = pygame.joystick.Joystick(i).get_name()
        print(joystick_name)
        if "Controller" in joystick_name:
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            print("PS4 controller found:", joystick_name)
            break
    else:
        print("PS4 controller not found.")
        # exit()

    # Start the driver thread
    # controller_thread = threading.Thread(target=controller_listen)
    # controller_thread.daemon = True
    # controller_thread.start()

    driver_thread_funct(ser)

    print("Done")

if __name__ == "__main__":
    main()
