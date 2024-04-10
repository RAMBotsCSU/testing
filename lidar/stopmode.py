import pygame
from adafruit_rplidar import RPLidar
from math import cos, sin, pi
import time

# Set up pygame
pygame.init()


# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0'
#PORT_NAME = '/dev/tty.usbserial-0001'

while(True):
    try:
        lidar = RPLidar(None, PORT_NAME, timeout=3)
        print("Lidar connected.")
        break
    except: 
        print("Error connecting to lidar. Trying again")

# create map
map_width = 400 # map size
lcd = pygame.display.set_mode((map_width, map_width))
lcd.fill((0,0,0))
pygame.display.update()

# CSV file name
output_file = 'lidar_data.csv'


# Define Parameters for Map
red_dot_threshold = 1000 # 500=.5m (?); threshhold for detecting close object
white_dot_threshold = 5000 # furthest distance factored into calculations
scale_data = int(white_dot_threshold/map_width) # scale of real data to printed map
  

def process_data(data):
    lcd.fill((0,0,0))
    # Initialize a list to store Lidar data
    processed_data = []
    for angle in range(360):
        distance = float(data[angle])
        if distance > 0:  # ignore initially ungathered data points
            radians = angle * pi / 180.0
            y = distance * cos(radians)
            x = -distance * sin(radians)
            point = (int(int(x)/scale_data + map_width/2), int(int(y)/scale_data + map_width/2))
            if distance <= red_dot_threshold:
                pygame.draw.circle(lcd, pygame.Color(255, 55, 55), point, 1, 1)
            elif distance <= white_dot_threshold:
                pygame.draw.circle(lcd, pygame.Color(255, 255, 255), point, 1, 1)
        processed_data.append(distance)
    pygame.draw.line(lcd, pygame.Color(255,255,255), (0, map_width/2), (map_width, map_width/2), 1)
    pygame.draw.line(lcd, pygame.Color(255,255,255), (map_width/2, 0), (map_width/2, map_width), 1)
    for i in range(-white_dot_threshold + int(white_dot_threshold%500), white_dot_threshold, 500): # tick every .5 meters
        if i == 0 or i == -white_dot_threshold:
            continue
        tick_placement = int(i/(scale_data))+int(map_width/2)
        pygame.draw.line(lcd, pygame.Color(255, 255, 255), (tick_placement, (map_width/2)+2), (tick_placement, (map_width/2)-2), 2) # x-ticks
        pygame.draw.line(lcd, pygame.Color(255, 255, 255), ((map_width/2)+2, tick_placement), ((map_width/2)-2, tick_placement), 2) # y-ticks
        label = str(i/1000)
        font = pygame.font.SysFont(None, 12)
        text = font.render(label, True, (255, 255, 255))
        lcd.blit(text, (int(map_width/2 + 5), tick_placement - 5)) # x-axis
        lcd.blit(text, (tick_placement - 5, int(map_width/2 + 5))) # y-axis
    pygame.draw.circle(lcd, pygame.Color(255, 50, 50), (int(map_width/2), int(map_width/2)), red_dot_threshold/scale_data, width=1)
    label = str(red_dot_threshold/1000) + ' m'
    font = pygame.font.SysFont(None, 12)
    text = font.render(label, True, (255, 50, 50))
    lcd.blit(text, (int(map_width/2) + int(red_dot_threshold*0.6/scale_data), int(map_width/2) + int(red_dot_threshold*0.8/scale_data)))
    pygame.display.update()
    return processed_data

scan_data = [white_dot_threshold] * 360
lidar_data = []
start_time = 0

# define parameters for stop mode
starttime = time.time()
window = 10
avg_dist = [white_dot_threshold]*(int(360/5)) # stores moving averages
dist_buffer = [[]*360]

# avg_dist is updated to the average data set of all data sets in dist_buffer
def update_avg_dist(dist_buffer):
    temp_avg = [white_dot_threshold]*360
    for angle_step in range(0, 360, 5):# 360 angle values
        dist_sum = 0 # temp hold distance sum of each angle
        for i in range(5):
            for arr in dist_buffer: # check same angle of each data set
                dist_sum += arr[angle_step + i]  # sum all distances at one angle
        temp_avg[angle_step] = dist_sum / (len(dist_buffer)*5) # average distance by size of dist_buffer
    return temp_avg

while(True):
    try:
        for scan in lidar.iter_scans():
            for (_, angle, distance) in scan:
                scan_data[min([359, int(angle)])] = distance 
            process_data(scan_data)

            if (time.time() - starttime) > 0.25: # every .25s
                starttime = time.time() # restart timer
                dist_buffer.append(scan_data) # add new data set to dist_buffer
                if len(dist_buffer) > window: # more data sets than window parameter
                    dist_buffer.pop(0) # remove oldest data set
                    avg_dist = update_avg_dist(dist_buffer) # get average of all data sets
                    #if min(avg_dist) <= red_dot_threshold: # any distance within stop proximity?
                        #print("Stop Proximity.")
    except:
        print("Issue with lidar. Trying again.")
        time.sleep(1)
        while(True):
            try:
                lidar = RPLidar(None, PORT_NAME, timeout=3)
                print("Lidar connected.")
                break
            except: 
                print("Error connecting to lidar. Trying again")