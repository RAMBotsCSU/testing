# SPDX-FileCopyrightText: 2019 Dave Astels for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Consume LIDAR measurement file and create an image for display.

Adafruit invests time and resources providing this open source code.
Please support Adafruit and open source hardware by purchasing
products from Adafruit!

Written by Dave Astels for Adafruit Industries
Copyright (c) 2019 Adafruit Industries
Licensed under the MIT license.

All text above must be included in any redistribution.
"""

import os
from math import cos, sin, pi, floor
import pygame
from adafruit_rplidar import RPLidar
import time

# Set up pygame and the display
os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
lcd = pygame.display.set_mode((400, 400))
pygame.mouse.set_visible(False)
lcd.fill((0,0,0))
pygame.display.update()

# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)# fix wrong body size error

# time values
starttime = time.time()

# Define the threshold distance for red dots
red_dot_threshold = 200 # 500 = .5 meters
white_dot_threshold = 5000 # furthest pointed picked up by lidar

# Map scaling and orientation
scale_factor = .2 # real-to-map distance scaling 
tic_spacing = int(scale_factor*1000) # tic spacing on map
angle_zero = 90 # 90 is point at bottom, + values rotates clockwise

window = 10
dist = [white_dot_threshold]*360 # stores lidar distances
avg_dist = [white_dot_threshold]*360 # stores moving averages
dist_buffer = [[]*360]

#pylint: disable=redefined-outer-name,global-statement
def process_data(data):

    # Create map
    lcd.fill((0,0,0))
    pygame.draw.line(lcd, (255, 255, 255), (200, 0), (200, 400), 1)  # Vertical line (y-axis)
    pygame.draw.line(lcd, (255, 255, 255), (0, 200), (400, 200), 1)  # Horizontal line (x-axis)
    # Mark tic marks on the x and y axes (each half meter)
    for i in range(-400, 400, tic_spacing): #(start point, stop point,tic spacing)
        pygame.draw.line(lcd, (255, 255, 255), (200 - i // 2, 0), (200 - i // 2, 5), 1)  # Horizontal tics
        pygame.draw.line(lcd, (255, 255, 255), (0, 200 + i // 2), (5, 200 + i // 2), 1)  # Vertical tics
        font = pygame.font.Font(None, 10)
        text = font.render(f"{(i-200) / (scale_factor*1000)}", True, (255, 255, 255))
        lcd.blit(text, (i+2, 5))
    
    for angle in range(360):
        distance = data[angle]
        if distance is None:
            return
        if distance > 0: # ignore initially ungathered data points
            angle_oriented = (angle + angle_zero) % 360
            radians = angle_oriented * pi / 180.0
            x = distance * cos(radians) * scale_factor
            y = distance * sin(radians) * scale_factor
            point = (200 - int(x), 200 - int(y))
            if 0 < distance <= red_dot_threshold:
                pygame.draw.circle(lcd, (255, 0, 0), point, 2)  # Red dot for objects within 1 meters
            elif distance > red_dot_threshold:
                pygame.draw.circle(lcd, (255, 255, 255), point, 2)  # White dot for objects beyond 0.5 meters

    pygame.display.update()

def update_ave_dist(dist_buffer, avg_dist):
    for angle in range(359):
        dist_sum = 0
        for arr in dist_buffer:
            dist_sum += arr[angle]
        avg_dist[angle] = dist_sum / len(dist_buffer)

# check if object is in stop proximity
def check_stop(avg_dist):
    if min(avg_dist) <= red_dot_threshold:
        return True

try:
    print(lidar.info)
    for scan in lidar.iter_scans():
        for (_, angle, distance) in scan:
            dist[min([359, floor(angle)])] = distance
        process_data(dist)
        if (time.time() - starttime) > 0.25:
            starttime = time.time()
            dist_buffer.append(dist)
            if len(dist_buffer) > window:
                dist_buffer.pop(0)
                update_ave_dist(dist_buffer, avg_dist)
                print(min(avg_dist))
                if check_stop(avg_dist):
                    print("Stop")

except KeyboardInterrupt:
    print('Stopping.')
lidar.stop()
lidar.disconnect()

