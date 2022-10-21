import serial
from multiprocessing import Process, Queue
import pygame
import time
import subprocess
import math

#Function to change the RGB of the controller based on mode
def rgb(m):
    if m == 0:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 255 255 255"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    elif m == 1:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 255 0 0"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    elif m == 2:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 0 255 0"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    elif m == -1:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 0 0 255"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    else:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 255 0 255"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        
        
#Function to pad the output chars to length 120 (127- serial ad-ons)
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
    
    
#Function to communicate and output to teensy by a given string
def serialRead_Write(output):
    #Write out what the pi is sending
    #print("Pi: " + output)
    output = padStr(output)
    
    #Write out to the serial buffer
    ser.write(output.encode())
    
    #Collect from serial buffer, trim the extra bits, then print
    inp = str(ser.readline())
    inp = inp[2:-5]
    inp = rmPadStr(inp)
    print(inp)
   
#Function to round to the nearest 0.05 for joysticks and triggers
def round_val(val):
    roundTo = 0.2
    #The -int part removes values of .00000000000001
    return round(round(val/roundTo)*roundTo,-int(math.floor(math.log10(roundTo))))
    
#Controller Thread
def controllerCode(q):
    pygame.init()
    j = pygame.joystick.Joystick(0)
    j.init()
    mode = 0
    rgb(mode)
    message = ""
    threadTerm = 0
    #Create arrays for Lx, Ly, L2, Rx, Ry, R2
    #Lx = strafe, Ly = forback, L2,R2 = roll, Rx = turn, Ry = pitch, D-pad up/down = height
    oldAxisArr = [0., 0., 0., 0., 0., 0.]
    newAxisArr = [0., 0., 0., 0., 0., 0.]
    axisLabelArr = ["Lx", "Ly", "L2", "Rx", "Ry", "R2"]
    while(threadTerm == 0):
        using_controller = True

        while using_controller:
            events = pygame.event.get()
            for event in events:
                #print(event)
                #Axis event
                if event.type == pygame.JOYAXISMOTION:
                    #for i in range(6):
                    i = event.axis
                    if (i == 1 or i == 4):
                        newAxisArr[i] = -1.*round_val(j.get_axis(i))
                    else:
                        newAxisArr[i] = round_val(j.get_axis(i))
                    if (oldAxisArr[i] != newAxisArr[i]):
                        #print(axisLabelArr[i], ": ", newAxisArr[i])
                        message = "Ar{}:{},".format(i,newAxisArr[i])
                        q.put(message)
                    oldAxisArr[i] = newAxisArr[i]
                    
                    
                        
                #Button Event
                elif event.type == pygame.JOYBUTTONDOWN:
                    #X
                    if j.get_button(0):
                        print("X")
                    #Circle
                    elif j.get_button(1):
                        print("Circle")
                    #Triangle
                    elif j.get_button(2):
                        print("Triangle")
                    #Square
                    elif j.get_button(3):
                        print("Square")
                    #L1
                    elif j.get_button(4):
                        mode =  3 if mode <= 0 else mode - 1
                        message = "SET_MODE_" + str(mode)
                        q.put(message)
                        rgb(mode)
                    #R1
                    elif j.get_button(5):
                        mode =  0 if mode >= 3 else mode + 1
                        message = "SET_MODE_" + str(mode)
                        q.put(message)
                        rgb(mode)
                    #L2 Half Way
                    elif j.get_button(6):
                        pass
                        #print("L2")
                    #R2 Half Way
                    elif j.get_button(7):
                        pass
                        #print("R2")
                    #Share
                    elif j.get_button(8):
                        print("Share")
                    #Option
                    elif j.get_button(9):
                        print("Option")
                    #Playstation Button
                    elif j.get_button(10):
                        q.put("TERMINATE")
                        threadTerm = 1
                        using_controller = False
                    #L3 (Joystick Press)
                    elif j.get_button(11):
                        print("L3")
                    #R3 (Joystick Press)
                    elif j.get_button(12):
                        print("R3")
                
                #Hat Event
                elif event.type == pygame.JOYHATMOTION:                        
                    #D-Pad Values
                    dx,dy = j.get_hat(0)
                    if(dx == 1):
                        print("Right")
                    elif(dx == -1):
                        print("Left")
                    if(dy == 1):
                        print("Up")
                    elif(dy == -1):
                        print("Down")
                    elif(dy == 0):
                        print("Dy: released")
                        
    #After leaving ThreadTerm
    print("CONTROLLER TERMINATING")

#Driver Thread
def driver(q):
    threadTerm = 0
    while (threadTerm == 0):
        if not q.empty():
            item = q.get()
            if(len(item)!=0):
                #print ("Running", item)
                if(item[0] == "A"):
                    serialRead_Write(item)
                elif (item[0] == "S"):
                    print(item)
                elif item == "TERMINATE":
                    time.sleep(0.5)
                    threadTerm = 1
            else:
                print("Recived nothing")
    print("DRIVER TERMINATING")
        


if __name__ == '__main__':
    
    ser = serial.Serial('/dev/ttyACM0',9600)
    q = Queue()
    a = Process(target=controllerCode, args=(q,))
    b = Process(target=driver, args=(q,))
    a.start()
    b.start()
    a.join()
    b.join()
    rgb(-1)
    print("Exiting :)")
