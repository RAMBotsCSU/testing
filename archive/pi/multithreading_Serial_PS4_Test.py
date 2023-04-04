import serial
from multiprocessing import Process, Queue
import pygame
import time

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
    
def controllerCode(q):
    pygame.init()
    j = pygame.joystick.Joystick(0)
    j.init()
    mode = 0
    message = ""
    while(1):
        using_controller = True

        while using_controller:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.JOYBUTTONDOWN:
                    #R1 Code
                    if j.get_button(5):
                        print("pressed R1")
                        mode =  0 if mode >= 5 else mode + 1
                        message = "SET_MODE_" + str(mode)
                        q.put(message)
                        using_controller = False
                    #L1 Code
                    elif j.get_button(4):
                        print("pressed L1")
                        mode =  5 if mode <= 0 else mode - 1
                        message = "SET_MODE_" + str(mode)
                        q.put(message)
                        using_controller = False

        print("loop done, mode: ", mode)


def driver(q):
    
    while True:
        if not q.empty():
            item = q.get()
            print ("Running", item)
            serialRead_Write(item)
        


if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0',9600)
    q = Queue()
    a = Process(target=controllerCode, args=(q,))
    b = Process(target=driver, args=(q,))
    a.start()
    b.start()