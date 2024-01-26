import pygame
from adafruit_rplidar import RPLidar
from math import cos, sin, pi

# Set up pygame and the display
pygame.init()
lcd = pygame.display.set_mode((320, 240))
pygame.mouse.set_visible(False)
lcd.fill((0, 0, 0))
pygame.display.update()

# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)

# Define the threshold distance for red dots (0.5 meters)
red_dot_threshold = 500

try:
    print(lidar.info)
    for scan in lidar.iter_scans():
        lcd.fill((0, 0, 0))  # Clear the screen for each scan
        for (_, angle, distance) in scan:
            radians = angle * pi / 180.0
            x = distance * cos(radians)
            y = distance * sin(radians)
            point = (160 + int(x), 120 + int(y))

            if 0 < distance <= red_dot_threshold:
                pygame.draw.circle(lcd, (255, 0, 0), point, 2)  # Red dot for objects within 0.5 meters
            elif distance > red_dot_threshold:
                pygame.draw.circle(lcd, (255, 255, 255), point, 2)  # White dot for objects beyond 0.5 meters

        pygame.display.update()

except KeyboardInterrupt:
    print('Stopping.')

finally:
    lidar.stop()
    lidar.disconnect()
