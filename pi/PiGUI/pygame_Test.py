import pygame
from pygame import mixer
import time

mixer.init()
# apt-get install git curl libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0


mixer.music.load("Resources/beep.mp3")
mixer.music.set_volume(0.7)


def imshow(filename):
    img = pygame.image.load(filename)
    size = img.get_rect().size
    #size = (600, 600)
    screen = pygame.display.set_mode(size)
    screen.blit(img, (0, 0))
    pygame.display.flip()

def imclose():
    pygame.display.quit()

mixer.music.play()

imshow('Resources/RamBOTs_Logo.bmp')
time.sleep(3)
imclose()

imshow('Resources/RamBOTs_Logo.bmp')
time.sleep(3)
imclose()