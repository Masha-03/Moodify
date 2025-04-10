import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
# set default full screen set the dimentsion and flag

#game main loop
while True:
    for event in pygame.event.get(): #collects all the events and goes through it one by one
        if event.type ==pygame.QUIT: #check one by one if there is a quit event
            pygame.quit()
            exit()

    pygame.display.update() 
    #update the display of the screen on top