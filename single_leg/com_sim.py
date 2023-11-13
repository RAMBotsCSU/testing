import serial
import time
from serial.serialutil import SerialException
from pyPS4Controller.controller import Controller

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

class MyController(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        # Initialize controller attributes here
        self.dpadArr = [0, 0, 0, 0]  # L, R, U, D
        self.shapeButtonArr = [0, 0, 0, 0]  # Sq, Tr, Cir, X
        self.miscButtonArr = [0, 0, 0, 0, 0]  # Share, Options, PS, L3, R3

    # Define controller event handlers here

# Function to read from and write to the serial port
def serial_read_write(string, ser):
    ser.write(padStr(string).encode())
    inp = str(ser.readline())
    inp = inp[2:-5]
    inp = rmPadStr(inp)
    return inp

def driver_thread_funct(controller, ser):
    # Initialize joystickArr
    joystickArr = [1.000, 1.000, 1.000, 1.000, 1.000, 1.000]
    # controller.shapeButtonArr[0] = 1.00
    runningMode = 0
    index = 0
    # controller.shapeButtonArr[3] = 1
    while True:
        # Read controller inputs and perform necessary actions
        # ...
        if index > 150:
            if controller.shapeButtonArr[3] == 1:
                controller.shapeButtonArr[3] = 0
                joystickArr[1] = 1.00
            else:
                controller.shapeButtonArr[3] = 1
                joystickArr[1] = 1.5
            index = 0

            # joystickArr[1] = 1.5

        # Send data to the connected USB serial device
        data = '''J0:{0:.3f},J1:{1:.3f},J2:{2:.3f},J3:{3:.3f},J4:{4:.3f},J5:{5:.3f},M:{6},LD:{7},RD:{8},UD:{9},DD:{10},Sq:{11},Tr:{12},Ci:{13},Xx:{14},Sh:{15},Op:{16},Ps:{17},L3:{18},R3:{19},#'''.format(joystickArr[0], joystickArr[1], joystickArr[2], joystickArr[3], joystickArr[4], joystickArr[5],
        runningMode, controller.dpadArr[0], controller.dpadArr[1],
        controller.dpadArr[2], controller.dpadArr[3], controller.shapeButtonArr[0],
        controller.shapeButtonArr[1], controller.shapeButtonArr[2], controller.shapeButtonArr[3],
        controller.miscButtonArr[0], controller.miscButtonArr[1], controller.miscButtonArr[2],
        controller.miscButtonArr[3], controller.miscButtonArr[4])

        print(index, data)

        serial_read_write(data, ser)

        time.sleep(0.01)
        index += 1

def main():
    print("hello world")
    try:
        ser = serial.Serial('/dev/tty.usbmodem104477401', 9600) # Run ls /dev/tty* on mac to find teensy path
        print("Found Device")
    except SerialException as e:
        print(f"An error occurred: {e}. \nPlease unplug the USB to the Teensy, press stop, and plug it in again.")
        # Handle error and play sound
        # pygame.mixer.Sound.play(error)
        while(1):
            pass
    controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)

    driver_thread_funct(controller, ser)
    print("Done")

if __name__ == "__main__":
    main()
