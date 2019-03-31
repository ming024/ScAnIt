import pygame
import numpy as np
import time
import io
import os
import sys
import socket
import serial
import threading
import scipy.misc
import pyodbc
import requests
import RPi.GPIO as GPIO
from PIL import Image
from picamera import PiCamera

SWITCH=20
ENTER=21
GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH, GPIO.IN)
GPIO.setup(ENTER, GPIO.IN)
PyTorch_REST_API_URL = 'http://7c605c99.ngrok.io/predict'
print("out here")
dsn = 'rpitestsqlserverdatasource'
user = 'deng-fat@deng-fat-goshopping'
password = 'TJG1ul3au4a83'
database = 'Shopping_Mall_Example'
connString = 'DSN={0};UID={1};PWD={2};DATABASE={3};'.format(dsn,user,password,database)
conn = pyodbc.connect(connString)
cursor = conn.cursor()
try:
    # Python2
    from urllib2 import urlopen
except ImportError:
    # Python3
    from urllib.request import urlopen

# machine params 
os.environ['SDL_VIDEO_WINDOW_POS'] = '8, 30'
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 680
Mystate = 0
# params
HEIGHT = SCREEN_HEIGHT - 75
WIDTH = HEIGHT * 4 // 3#SCREEN_WIDTH - 16
my_pos = None
item_now = None
item_list = [ ['', 0, 0] for i in range(0, 21)]
total = 0

#background image
home_bg    = pygame.image.load('pictures/home_bg.png')
map_bg     = pygame.image.load('pictures/map_bg.png')
car_bg     = pygame.image.load('pictures/car_bg.png')
info_bg    = pygame.image.load('pictures/info_bg.png')
cab1_bg    = pygame.image.load('pictures/cab1_bg.png')
cab2_bg    = pygame.image.load('pictures/cab2_bg.png')
cab3_bg    = pygame.image.load('pictures/cab3_bg.png')
cab4_bg    = pygame.image.load('pictures/cab4_bg.png')

#item icon
scan_true  = pygame.image.load('pictures/item_scan1.png')
scan_false = pygame.image.load('pictures/item_scan0.png')
pos_true   = pygame.image.load('pictures/item_pos1.png')
pos_false  = pygame.image.load('pictures/item_pos0.png')
info_true  = pygame.image.load('pictures/item_info1.png')
info_false  = pygame.image.load('pictures/item_info0.png')
map_true   = pygame.image.load('pictures/item_map1.png')
map_false  = pygame.image.load('pictures/item_map0.png')
car_true   = pygame.image.load('pictures/item_car1.png')
car_false  = pygame.image.load('pictures/item_car0.png')
addcar_true   = pygame.image.load('pictures/item_addcar1.png')
addcar_false  = pygame.image.load('pictures/item_addcar0.png')
cab_true    = pygame.image.load('pictures/item_shelf1.png')
cab_false   = pygame.image.load('pictures/item_shelf0.png')
home_true  = pygame.image.load('pictures/item_home1.png')
home_false = pygame.image.load('pictures/item_home0.png')
my_icon    = pygame.image.load('pictures/my.png')
goal_icon  = pygame.image.load('pictures/goal.png')

def keyboard_control():
    signal = 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        signal = command['UP']
    elif keys[pygame.K_RIGHT]:
        signal = command['RIGHT']
    return signal
    

        
def Home():
    #Home page: can go to scan, pos, map, car items

    global Mystate, windowSurface
    # some definition
    Home_state = {'SCAN': 0, 'MAP': 1, 'CAR': 2, 'POS': 3}

    Mystate = 0 #reset mystate
    windowSurface = pygame.display.set_mode((WIDTH, HEIGHT)) #reset surface
    while True:
        #get keyboard input
        pygame.time.wait(100)
        if GPIO.input(ENTER) == 0:#enter
            if Mystate == Home_state['SCAN']:
                Scan()
            elif Mystate == Home_state['MAP']:
                Map()
            elif Mystate == Home_state['CAR']:
                Car()
            elif Mystate == Home_state['POS']:
                Pos()
        elif GPIO.input(SWITCH) == 0:#switch
            Mystate = (Mystate+1)%4

        #init items
        background = home_bg
        scan_icon = scan_true if Mystate == Home_state['SCAN'] else scan_false
        map_icon  = map_true  if Mystate == Home_state['MAP']  else map_false
        car_icon  = car_true  if Mystate == Home_state['CAR']  else car_false
        pos_icon  = pos_true  if Mystate == Home_state['POS']  else pos_false
        font = pygame.font.SysFont("arial", 30)
        if Mystate == Home_state['SCAN']:
            text = font.render("scan item", True, (50,50,50))
        elif Mystate == Home_state['MAP']:
            text = font.render("check map", True, (50,50,50))
        elif Mystate == Home_state['CAR']:
            text = font.render("check cart", True, (50,50,50))
        elif Mystate == Home_state['POS']:
            text = font.render("get position", True, (50,50,50))
    
        # build surface
        windowSurface.blit(background, (0, 0))
        windowSurface.blit(scan_icon, (200, 505))
        windowSurface.blit(map_icon,  (300, 495))
        windowSurface.blit(car_icon,  (400, 500))
        windowSurface.blit(pos_icon,  (500, 500))
        windowSurface.blit(text,  (600, 500))
        pygame.display.update()
        pygame.event.pump()

def Map():
    #Map page: can go to pos, info, cabinet, home items

    global Mystate, windowSurface, goal, my_pos
    # some definition
    Map_state = {'HOME': 0, 'INFO': 1, 'CAB': 2, 'POS': 3}

    Mystate = 0 #reset mystate
    windowSurface = pygame.display.set_mode((WIDTH, HEIGHT)) #reset surface
    while True:
        #get keyboard input
        pygame.time.wait(100)
        if GPIO.input(ENTER) == 0:
            if Mystate == Map_state['HOME']:
                my_pos = None
                Home()
            elif Mystate == Map_state['INFO']:
                my_pos = None
                Info()
            elif Mystate == Map_state['CAB']:
                Cab()
            elif Mystate == Map_state['POS']:
                my_pos = None
                Pos()
        elif GPIO.input(SWITCH)  == 0:
            Mystate = (Mystate+1)%4
            #check whether the goal is exist
            if item_now is None:
                if Mystate == Map_state['INFO'] or Mystate == Map_state['CAB']:
                    Mystate = Map_state['POS']

        #init items
        background = map_bg
        home_icon = home_true if Mystate == Map_state['HOME'] else home_false
        info_icon = info_true if Mystate == Map_state['INFO'] else info_false
        cab_icon  = cab_true  if Mystate == Map_state['CAB']  else cab_false
        pos_icon  = pos_true  if Mystate == Map_state['POS']  else pos_false
        font = pygame.font.SysFont("arial", 25)
        if Mystate == Map_state['HOME']:
            text = font.render("Home", True, (0,0,225))
        elif Mystate == Map_state['INFO']:
            text = font.render("item information", True, (0,0,225))
        elif Mystate == Map_state['CAB']:
            text = font.render("see the cabinet", True, (0,0,225))
        elif Mystate == Map_state['POS']:
            text = font.render("get position", True, (0,0,225))
    
        # build surface
        windowSurface.blit(background, (0, 0))
        windowSurface.blit(home_icon, (200, 500))
        if item_now is not None:
            windowSurface.blit(info_icon, (300, 500))
            windowSurface.blit(cab_icon,  (400, 500))
            windowSurface.blit(goal_icon, (item_now[6], item_now[7]))
        if my_pos is not None:
            windowSurface.blit(my_icon, (my_pos[0], my_pos[1]))
        windowSurface.blit(pos_icon,  (500, 500))
        windowSurface.blit(text,  (600, 500))
        pygame.display.update()
        pygame.event.pump()

    
def Scan():
    global item_now
    global Mystate, windowSurface
    # some definition
    Mystate = 0 #reset mystate
    
    with PiCamera() as camera:
        camera.start_preview()
    
        windowSurface = pygame.display.set_mode((WIDTH, HEIGHT)) #reset surface.
        pygame.display.update()
        pygame.event.pump()
        
        while True:
            #get keyboard input
            pygame.time.wait(50)       
            if GPIO.input(ENTER) == 0:
                break
            pygame.event.pump()                                
        
        time.sleep(1)
        camera.capture('fat.jpg')        
        im = image = open('fat.jpg', 'rb').read()
        payload = {'image': im}

        # Submit the request.
        r = requests.post(PyTorch_REST_API_URL, files=payload).json()

        # Ensure the request was successful.
        if r['success']:
            # Loop over the predictions and display them.
            for (i, result) in enumerate(r['predictions']):
                print('{}. {}: {:.4f}'.format(i + 1, result['label'],
                                          result['probability']))
            print(result['label'])
        # Otherwise, the request failed.
        else:
            print('Request failed')
    
    mapping = ['computer', 'green bottle', 'corrector', 'nail clipper', 'medicine', 'mouse',\
        'soap', 'baseball', 'book', 'blue bottle', 'glove', 'chopping board', 'white scissor',\
        'pillow', 'apple juice', 'umbrella', 'tea pot', 'shampoo', 'dinasour', 'pooh', 'hat']
    string = mapping[int(result['label'])]
    string2 = "select * FROM Item WHERE(Item_Name='"+string+"');"
    cursor.execute(string2)
    item_now = cursor.fetchone()
    print(item_now)
    Info()
        
def Pos():
    global my_pos, Mystate, windowSurface
    with PiCamera() as camera:
        camera.start_preview()
    
        windowSurface = pygame.display.set_mode((WIDTH, HEIGHT)) #reset surface.
        pygame.display.update()
        pygame.event.pump()
        
        while True:
            #get keyboard input
            pygame.time.wait(50)    
            if GPIO.input(ENTER) == 0:
                break
            pygame.event.pump()                                
        
        time.sleep(1)
        camera.capture('fat.jpg')        
        im = image = open('fat.jpg', 'rb').read()
        payload = {'image': im}

        # Submit the request.
        r = requests.post(PyTorch_REST_API_URL, files=payload).json()

        # Ensure the request was successful.
        if r['success']:
            # Loop over the predictions and display them.
            for (i, result) in enumerate(r['predictions']):
                print('{}. {}: {:.4f}'.format(i + 1, result['label'],
                                          result['probability']))
            print(result['label'])
        # Otherwise, the request failed.
        else:
            print('Request failed')
    
    mapping = ['computer', 'green bottle', 'corrector', 'nail clipper', 'medicine', 'mouse',\
        'soap', 'baseball', 'book', 'blue bottle', 'glove', 'chopping board', 'white scissor',\
        'pillow', 'apple juice', 'umbrella', 'tea pot', 'shampoo', 'dinasour', 'pooh', 'hat']
    string = mapping[int(result['label'])]
    string2 = "select * FROM Item WHERE(Item_Name='"+string+"');"
    cursor.execute(string2)
    item_new = cursor.fetchone()
    my_pos = [item_new[6], item_new[7]]
    Map()

def Info():
    #Info page: can go to map, addcar, scan, home items

    global Mystate, windowSurface, item_now, item_list, total
    # some definition
    Info_state = {'HOME': 0, 'MAP': 1, 'SCAN': 2, 'CAR': 3}

    Mystate = 0 #reset mystate
    windowSurface = pygame.display.set_mode((WIDTH, HEIGHT)) #reset surface.
    #get image first
    item_url = item_now[4]
    item_str = urlopen(item_url).read()
    item_file = io.BytesIO(item_str)
    image = pygame.image.load(item_file)
    while True:
        #get keyboard input
        if GPIO.input(ENTER) == 0:
            if Mystate == Info_state['HOME']:
                Home()
            elif Mystate == Info_state['MAP']:
                Map()
            elif Mystate == Info_state['SCAN']:
                Scan()
            elif Mystate == Info_state['CAR']:
                if item_list[0][2] == 0:
                    item_list[0] = [item_now[0], item_now[1], 1]
                else:
                    item_list[0][2]+=1
                total += item_now[1]
                Car()
        elif GPIO.input(SWITCH) == 0:
            Mystate = (Mystate+1)%4

        #init items
        background = info_bg
        home_icon = home_true    if Mystate == Info_state['HOME'] else home_false
        map_icon  = map_true     if Mystate == Info_state['MAP']  else map_false
        scan_icon = scan_true    if Mystate == Info_state['SCAN'] else scan_false
        car_icon  = addcar_true  if Mystate == Info_state['CAR']  else addcar_false
        font = pygame.font.SysFont("arial", 30)
        if Mystate == Info_state['HOME']:
            text = font.render("Home", True, (50,50,50))
        elif Mystate == Info_state['MAP']:
            text = font.render("search location", True, (50,50,50))
        elif Mystate == Info_state['SCAN']:
            text = font.render("scan again", True, (50,50,50))
        elif Mystate == Info_state['CAR']:
            text = font.render("add to cart", True, (50,50,50))
        #put data to surface
        name   = font.render("Name:  " + item_now[0], True, (0, 0, 255))
        price  = font.render("Price: " + str(item_now[1]), True, (0,0,255))
        remain = font.render("Remain: "+ str(item_now[2]), True, (0,0,225))
        number = font.render("buying number in last week: " + str(item_now[3]), True, (0,0,225))
    
        # build surface
        windowSurface.blit(background, (0, 0))
        windowSurface.blit(home_icon, (200, 500))
        windowSurface.blit(map_icon, (300, 500))
        windowSurface.blit(scan_icon,  (400, 500))
        windowSurface.blit(car_icon,  (500, 500))
        windowSurface.blit(text,  (600, 500))
        windowSurface.blit(name, (450, 150))
        windowSurface.blit(price, (450, 200))
        windowSurface.blit(remain, (450, 250))
        windowSurface.blit(number, (450, 300))
        windowSurface.blit(image, (0, 150)) 
        pygame.display.update()
        pygame.event.pump()

def Car():
    #Car page: can only go to home

    global Mystate, windowSurface, total, item_now, item_list

    Mystate = 0 #reset mystate
    windowSurface = pygame.display.set_mode((WIDTH, HEIGHT)) #reset surface
    while True:
        #get keyboard inputs
        pygame.time.wait(200)
        if GPIO.input(ENTER) == 0:
            Home()
        #init items
        background = car_bg
        home_icon = home_true 
        font = pygame.font.SysFont("arial", 30)
        text = font.render("Home", True, (0,0,255))
                
    
        # build surface
        windowSurface.blit(background, (0, 0))
        windowSurface.blit(home_icon, (200, 500))
        windowSurface.blit(text,  (400, 500))
        if total != 0:
            string = 'Name:    number:    price:'
            str1 = font.render(string, True, (50, 50, 50))
            windowSurface.blit(str1, (200, 150))
        count = 0
        for i in range(21):
            count+=1
            if item_list[i][2] != 0:
                string = item_list[i][0] + '    ' + str(item_list[i][2]) + '     ' + str(item_list[i][1]*item_list[i][2])
                str1 = font.render(string, True, (50,50,50))
                windowSurface.blit(str1, (200, 150+count*50))
        pygame.display.update()
        pygame.event.pump()

def Cab():
    #cab page: 
    global Mystate, windowSurface

    Mystate = 0 #reset mystate
    windowSurface = pygame.display.set_mode((WIDTH, HEIGHT)) #reset surface
    while True:
        pygame.time.wait(100)
        if GPIO.input(ENTER) == 0:
            Map()
        background = cab1_bg
        map_icon = map_true
        font = pygame.font.SysFont("arial", 30)
        text = font.render("back to map", True, (50, 50, 50))
        # build surface
        windowSurface.blit(background, (0, 0))
        windowSurface.blit(map_icon, (200, 500))
        windowSurface.blit(text,  (400, 500))
        pygame.display.update()
        pygame.event.pump()




pygame.init()
windowSurface = pygame.display.set_mode((WIDTH, HEIGHT))
Home()
