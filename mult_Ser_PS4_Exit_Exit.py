import serial
from multiprocessing import Process, Queue
import pygame
import time
import subprocess

#Function to change the RGB of the controller based on mode
def rgb(m):
    if m == 0:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/color_test.sh 255 255 255"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
    elif m == 1:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/color_test.sh 255 0 0"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
    elif m == 2:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/color_test.sh 0 255 0"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
    elif m == -1:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/color_test.sh 0 0 255"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
    else:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/color_test.sh 255 0 255"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        
        
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
    
    
#Controller Thread
def controllerCode(q):
    pygame.init()
    j = pygame.joystick.Joystick(0)
    j.init()
    mode = 0
    rgb(mode)
    message = ""
    threadTerm = 0
    while(threadTerm == 0):
        using_controller = True

        while using_controller:
            events = pygame.event.get()
            for event in events:
                
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
                
                #Joysticks
                lx = j.get_axis(0)
                ly = -1*j.get_axis(1)
                if(abs(lx) >= 0.1):
                    print("lX: ", lx)
                if(abs(ly) >= 0.1):
                    print("lY: ", ly)
                rx = j.get_axis(3)
                ry = -1*j.get_axis(4)
                if(abs(rx) >= 0.1):
                    print("rX: ", rx)
                if(abs(ry) >= 0.1):
                    print("rY: ", ry)
                l2 = j.get_axis(2)
                r2 = j.get_axis(5)
                if(l2 != -1):
                    print("l2: ", l2)
                if(r2 != -1):
                    print("r2: ", r2)
                    
                #Button Presses
                if event.type == pygame.JOYBUTTONDOWN:
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
    #After leaving ThreadTerm
    print("CONTROLLER TERMINATING")

#Driver Thread
def driver(q):
    threadTerm = 0
    while (threadTerm == 0):
        if not q.empty():
            item = q.get()
            print ("Running", item)
            serialRead_Write(item)
            if item == "TERMINATE":
                time.sleep(0.5)
                threadTerm = 1
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
