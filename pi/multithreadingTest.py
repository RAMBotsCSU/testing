from multiprocessing import Process, Queue
import pygame
import time



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
        else:
            pass
            #print ("No jobs")
            #time.sleep(1)



if __name__ == '__main__':
    q = Queue()
    a = Process(target=controllerCode, args=(q,))
    b = Process(target=driver, args=(q,))
    a.start()
    b.start()