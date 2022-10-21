import pygame

pygame.init()

j = pygame.joystick.Joystick(0)
j.init()
mode = 0

while(1):
    
    using_controller = True



    while using_controller:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.JOYBUTTONDOWN:
                if j.get_button(5):
                    print("pressed R1")
                    mode =  0 if mode >= 5 else mode + 1
                    using_controller = False
                elif j.get_button(4):
                    print("pressed L1")
                    mode =  5 if mode <= 0 else mode - 1
                    using_controller = False
            #elif event.type == pygame.JOYBUTTONUP:
                #print("Button Released")

    print("loop done, mode: ", mode)

#