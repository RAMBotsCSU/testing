import pygame
from pygame import mixer
import time
import random

mixer.init()
# apt-get install git curl libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0

sheep1 = pygame.mixer.Sound('Sounds/sheep1.mp3')
sheep2 = pygame.mixer.Sound('Sounds/sheep2.mp3')
sheep3 = pygame.mixer.Sound('Sounds/sheep3.mp3')
sheep4 = pygame.mixer.Sound('Sounds/sheep4.mp3')
sheep_sounds = [sheep1,sheep2,sheep3,sheep4]
#pygame.mixer.Sound.play(random.choice(sheep_sounds))


def imshow(filename):
    img = pygame.image.load(filename)
    size = img.get_rect().size
    #size = (600, 600)
    screen = pygame.display.set_mode(size)
    screen.blit(img, (0, 0))
    pygame.display.flip()

def imclose():
    pygame.display.quit()

pygame.mixer.Sound.play(random.choice(sheep_sounds))

time.sleep(2)

pygame.mixer.Sound.play(random.choice(sheep_sounds))

time.sleep(2)

pygame.mixer.Sound.play(random.choice(sheep_sounds))

time.sleep(2)

pygame.mixer.Sound.play(random.choice(sheep_sounds))


#imshow('Resources/RamBOTs_Logo.bmp')
#time.sleep(3)
#imclose()

#imshow('Resources/RamBOTs_Logo.bmp')
#time.sleep(3)
#imclose()