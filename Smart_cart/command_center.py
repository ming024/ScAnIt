import pygame
import numpy as np
import time
import os
import sys
import socket
import serial
import threading
import scipy.misc
from video_serial_client import video_serial_client

# machine params 
os.environ['SDL_VIDEO_WINDOW_POS'] = '8, 30'
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# params
HEIGHT = SCREEN_HEIGHT - 75
WIDTH = HEIGHT * 4 // 3#SCREEN_WIDTH - 16
command = {'UP': 1, 'DOWN': 2, 'LEFT': 4, 'RIGHT': 8, 'EXIT': 16}
state_map = {'control': True, 'auto': False, 'attack': False}

# icons
up_yellow = pygame.image.load('pictures/up_yellow.png')
down_yellow = pygame.image.load('pictures/down_yellow.png')
left_yellow = pygame.image.load('pictures/left_yellow.png')
right_yellow = pygame.image.load('pictures/right_yellow.png')
up_blue = pygame.image.load('pictures/up_blue.png')
down_blue = pygame.image.load('pictures/down_blue.png')
left_blue = pygame.image.load('pictures/left_blue.png')
right_blue = pygame.image.load('pictures/right_blue.png')
logo = pygame.image.load('pictures/logo.png')
quit_black = pygame.image.load('pictures/quit_black.png')
quit_red = pygame.image.load('pictures/quit_red.png')

def keyboard_control():
    signal = 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        signal += command['UP']
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        signal += command['DOWN']
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        signal += command['LEFT']
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        signal += command['RIGHT']
        
    return signal
    
def make_surface(image, windowsSurface, keyboard_signal):
    # concatenate the image and the icons to the surface and return exit if needed
    
    # some definition
    quit_center = np.array([WIDTH - 40, 40])
    quit_angle = quit_center - [25, 25]
    
    # choose proper icon
    up_icon = up_yellow if keyboard_signal % 2 else up_blue
    down_icon = down_yellow if keyboard_signal % (2 * command['DOWN']) >= command['DOWN'] else down_blue
    left_icon = left_yellow if keyboard_signal % (2 * command['LEFT']) >= command['LEFT'] else left_blue
    right_icon = right_yellow if keyboard_signal % (2 * command['RIGHT']) >= command['RIGHT'] else right_blue
    logo_icon = logo
    
    # build surface
    windowSurface.blit(pygame.surfarray.make_surface(image), (0, 0))
    windowSurface.blit(up_icon, (WIDTH - 197, HEIGHT - 205))
    windowSurface.blit(down_icon, (WIDTH - 197, HEIGHT - 105))
    windowSurface.blit(left_icon, (WIDTH - 284, HEIGHT - 155))
    windowSurface.blit(right_icon, (WIDTH - 110, HEIGHT - 155))
    windowSurface.blit(logo_icon, (0, 0))
    
    # return exit if necessary
    if keyboard_signal % (2 * command['EXIT']) >= command['EXIT']:
        return True
    else:
        return False
    
pygame.init()
windowSurface = pygame.display.set_mode((WIDTH, HEIGHT))


count = 0
while True:
    image = np.zeros((WIDTH, HEIGHT, 3), dtype = np.int8) + 50
    
    
    # get keyboard and mouse state
    keyboard_signal = keyboard_control()
    
    # send encoded data to arduino bluetooth emitter
    
    exit = make_surface(image, windowSurface, keyboard_signal)
    
    if exit:
        pygame.quit()
        sys.exit()  
        receiver.socket.close()
        
    pygame.display.update()
    pygame.event.pump()
    count += 1
