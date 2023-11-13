import csv
import pygame
import time
from math import cos, sin, pi

# Set up pygame and the display
pygame.init()
lcd = pygame.display.set_mode((320,240))
pygame.mouse.set_visible(False)
lcd.fill((0,0,0))
pygame.display.update()

# Read Lidar data from the CSV file
input_file = 'lidar_data.csv'

with open(input_file, 'r', newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    lidar_data = list(csv_reader)

max_distance = 0

# Function to draw Lidar data on the Pygame window
def draw_lidar_data(data):
	global max_distance
	lcd.fill((0,0,0))
	for angle in range(360):
		distance = float(data[angle])
		if distance > 0:                  # ignore initially ungathered data points
			max_distance = max([min([5000, distance]), max_distance])
			radians = angle * pi / 180.0
			x = distance * cos(radians)
			y = distance * sin(radians)
			point = (160 + int(x / max_distance * 119), 120 + int(y / max_distance * 119))
			lcd.set_at(point, pygame.Color(255, 255, 255))
	pygame.display.update()

running = True
current_index = 0

# Main loop to display Lidar data
while running:
	if current_index < len(lidar_data):
		draw_lidar_data(lidar_data[current_index])
		current_index += 1
		time.sleep(.2)
		print('Frame updated.')
	else:
		running = False

pygame.quit()
