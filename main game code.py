import pygame
from sys import exit

pygame.init() # to start the system: sound,graphics etc of pygame module
#screen here is like a canvas to store the window and u can draw/ add other images
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
# tells pygame automatically set to full-screen on users computer 
Time = pygame.time.Clock()
#set game speed

#background image
background_surface =pygame.image.load("Moodify/graphics/Game main page.png")
# to scale background image to match full screen of user
screen_width,screen_height = screen.get_size()
background_surface = pygame.transform.scale(background_surface,(screen_width,screen_height))

#game main loop
while True:
    for event in pygame.event.get(): #collects all the events and goes through it one by one
        if event.type == pygame.KEYDOWN:#check if any key is press 
            if event.key == pygame.K_ESCAPE: #if its the ESC key
                pygame.quit() # shut down eveythig u open/ initialized (includes the program that is running in the background)
                exit() 
    
    screen.blit(background_surface,(0,0))

    pygame.display.update() #update the display of the screen 
    Time.tick(60)# tells loop dont just faster then 60 fps