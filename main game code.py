import pygame
import sys 
import datetime # to get user device time
    
    
pygame.init() # to start the system: sound,graphics etc of pygame module
#screen here is like a canvas to store the window and u can draw/ add other images
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
# tells pygame automatically set to full-screen on users computer 
Time = pygame.time.Clock()
#set game speed

current_hour = datetime.datetime.now().hour

#images

#raining image
raindrops= pygame.image.load("Moodify/graphics/raindrops.png")

#night time image
night_background = pygame.image.load("Moodify/graphics/night.png").convert()

# day time image
sunny_background = pygame.image.load("Moodify/graphics/sunny day background.png").convert()

#background image
background_surface =pygame.image.load("Moodify/graphics/main game page no window.png").convert_alpha()
# to scale background image to match full screen of user
screen_width,screen_height = screen.get_size()
background_surface = pygame.transform.scale(background_surface,(screen_width,screen_height))





#game main loop
while True:
    for event in pygame.event.get(): #collects all the events and goes through it one by one
        if event.type == pygame.KEYDOWN:#check if any key is press 
            if event.key == pygame.K_ESCAPE: #if its the ESC key
                pygame.quit() # shut down eveythig u open/ initialized (includes the program that is running in the background)
                sys.exit() 

    current_hour = datetime.datetime.now().hour
    if 7 <= current_hour < 18: #set time between  7 to 6pm
        screen.blit(sunny_background, (570,50))
    else:
        screen.blit(night_background, (600,50))
    
    screen.blit(background_surface,(0,0))

    pygame.display.update() #update the display of the screen 
    Time.tick(60)# tells loop dont just faster then 60 fps