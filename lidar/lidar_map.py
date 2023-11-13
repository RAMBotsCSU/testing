import time
import os
from math import cos, sin, pi, floor
import pygame
import csv
from adafruit_rplidar import RPLidar

# Set up pygame and the display
os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
lcd = pygame.display.set_mode((320,240))
pygame.mouse.set_visible(False)
lcd.fill((0,0,0))
pygame.display.update()


# CSV file name
output_file = 'lidar_data.csv'

# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)
 
#def open_lidar():
#    try:
#        lidar = RPLidar(None, PORT_NAME, timeout=3)
 #   except Exception as e:
 #       print(f"Error: {e}")
 #       lidar.stop()
 #       lidar.disconnect()
  #      open_lidar
    	
max_distance = 0

def process_data(data):
	global max_distance
	lcd.fill((0,0,0))
	# Initialize a list to store Lidar data
	processed_data = []
	for angle in range(360):
		distance = float(data[angle])
		if distance > 0:                  # ignore initially ungathered data points
			max_distance = max([min([5000, distance]), max_distance])
			radians = angle * pi / 180.0
			x = distance * cos(radians)
			y = distance * sin(radians)
			point = (160 + int(x / max_distance * 119), 120 + int(y / max_distance * 119))
			lcd.set_at(point, pygame.Color(255, 255, 255))
		processed_data.append(distance)
	pygame.display.update()
	return processed_data
	



scan_data = [0] * 360
lidar_data = []
start_time = 0
try:
    print(lidar.info)
    for scan in lidar.iter_scans():
        for (_, angle, distance) in scan:
            scan_data[min([359, int(angle)])] = distance 
        if time.time() - start_time > .2:
            start_time = time.time()
            # lidar_data.append(scan_data)
            lidar_data.append(process_data(scan_data))
            print('Data written to csv.')
        
        
        
except KeyboardInterrupt:
    lidar.stop()
    lidar.disconnect()
    with open(output_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(lidar_data)  
    print('Data collection stopped.')
    print(f'Lidar data saved to {output_file}')

#except Exception as e:
#    print(f"Error: {e}")
#    lidar.stop()
 #   lidar.disconnect()
#    open_lidar




    
