import pygame
import sys 
import random
import datetime # to get user device time

#create the rain sprite and set up its speed and postion
class Rain(pygame.sprite.Sprite): 
    def __init__(rain): #set up the sprite image for image manipulation (runs automatically)
        pygame.sprite.Sprite.__init__(rain) #calling the sprite(rain variable) and set up the properties
        rain.image=raindrops #set the image
        rain.rect= rain.image.get_rect() # create a rectangle, get_rect from image automatically assign the value
        #set the speed for in x and y for raindrops
        rain.speedx=2
        rain.speedy= random.randint(10,20)
        #tells where the raindrops should spawn
        rain.rect.x=random.randint(0,window_width)
        rain.rect.y=random.randint(-window_height,-5)
        

    def update(rain):
            #when the sprite touches the the end of the screen, reuse the sprite to spawn it again
        if rain.rect.bottom >window_height:
            rain.speedx=2
            rain.speedy= random.randint(10,20)
            rain.rect.x=random.randint(0,window_width)
            rain.rect.y=random.randint(-window_height,-5)

        #add value keep on update the rain
        rain.rect.x=rain.rect.x + rain.speedx 
        rain.rect.y=rain.rect.y+rain.speedy

#random to rain or not
def rain_or_not():
    num_rain = random.randint(1,3) #random the num
    rain_group = pygame.sprite.Group() #make it as a group of sprite

    if num_rain == 1 or num_rain == 3:
        for i in range (100): #run the group sprite one by one 100 times
            rain = Rain() #runs the set up to spawn the rain, position and speed and add it to the group
            rain_group.add(rain) 
        return rain_group
    else:
        return None

#make it as a function to call it in the main loop
def display_rain(rain_group):
    if rain_group : #if there is a sprite
        rain_group.update() #moves all the raindrops
        rain_group.draw(screen) #a screen blit for the rain group loops it one by one


class FemaleCharacter(pygame.sprite.Sprite):
    def __init__(Female):
        pygame.sprite.Sprite.__init__(Female)
        Female.character =character_image
        Female.current_image = 0 #showing index 0 img
        Female.image = Female.character[Female.current_image] #link the sprite to the list
        Female.rect=Female.image.get_rect()
        Female.speedx =5
        Female.rect.x=-1
        Female.rect.y=window_height -Female.rect.height #place the character bottom of the user screen
        
        #where the character facing
        Female.facing_left = pygame.transform.flip(Female.image,True,False)
        Female.facing_right = True

    def update_character(Female):
        keys = pygame.key.get_pressed() #user press key
            
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            Female.rect.x=Female.rect.x-Female.speedx
            Female.facing_right = False
            
                    
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            Female.rect.x = Female.rect.x + Female.speedx
            Female.facing_right = True
                    
        #spawn right side of the screen if cross the left side
        if Female.rect.right < 0:
            Female.rect.x = window_width
        #spawn at left side if cross the right
        if Female.rect.left > window_width:
            Female.rect.right= 0 
            #fixed the jumping issue here before: rect.x=0

        if Female.facing_right:
            Female.image = Female.character[Female.current_image]
        else:
            Female.image =Female.facing_left



#setting up pygame
pygame.init() # to start the system: sound,graphics etc of pygame module
#screen here is like a canvas to store the window and u can draw/ add other images
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
# tells pygame automatically set to full-screen on users computer 
Time = pygame.time.Clock()
#set game speed



#to get the height and width of screen
window_width,window_height = screen.get_size()

#to get the users device time
current_hour = datetime.datetime.now().hour 



#images
#raining image
raindrops= pygame.image.load("Moodify/graphics/raindrops.png").convert_alpha()

#night time image
night_background = pygame.image.load("Moodify/graphics/night.png").convert()

# day time image
sunny_background = pygame.image.load("Moodify/graphics/sunny day background.png").convert()

#background image
background_surface =pygame.image.load("Moodify/graphics/main game page no window.png").convert_alpha()
# to scale background image to match full screen of user
screen_width,screen_height = screen.get_size()
background_surface = pygame.transform.scale(background_surface,(screen_width,screen_height))

#character image (female)
character_image = [
    pygame.image.load("Moodify/F-right/pixil-frame-0.png"),
    pygame.image.load("Moodify/F-right/pixil-frame-1.png"),
    pygame.image.load("Moodify/F-right/pixil-frame-2.png"),
    pygame.image.load("Moodify/F-right/pixil-frame-3.png"),
]
#(Spawn only once) 
#determine will rain or not
rain_group = rain_or_not()
#the female character 
Female_character=FemaleCharacter()

#game main loop
while True:
    for event in pygame.event.get(): #collects all the events and goes through it one by one
        if event.type == pygame.KEYDOWN:#check if any key is press 
            if event.key == pygame.K_ESCAPE: #if its the ESC key
                pygame.quit() # shut down eveythig u open/ initialized (includes the program that is running in the background)
                sys.exit() 

    #the night and day background
    current_hour = datetime.datetime.now().hour
    if 7 <= current_hour < 18: #set time between  7 to 6pm
        screen.blit(sunny_background, (570,50))
    else:
        screen.blit(night_background, (600,50))

    #if it rain the display if not None
    display_rain(rain_group)

    #background
    screen.blit(background_surface,(0,0))

    Female_character.update_character()
    screen.blit(Female_character.image,Female_character.rect)
    

    pygame.display.update() #update the display of the screen 
    Time.tick(60)# tells loop dont just faster then 60 fps