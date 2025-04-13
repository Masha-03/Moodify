import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
# set default full screen set the dimentsion and flag

#game main loop
while True:
    for event in pygame.event.get(): #collects all the events and goes through it one by one
        if event.type == pygame.KEYDOWN:#check if any key is press 
            if event.key == pygame.K_ESCAPE: #if its the ESC key
                pygame.quit() # shut down eveythig u open/ initialized (includes the program that is running in the background)
                exit() 

    pygame.display.update() 
    #update the display of the screen on top