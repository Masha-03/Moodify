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
        play_rain_sound()
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
        Female.idle = Fcharacter_image_idle
        Female.walking = Fcharacter_walking_img
        Female.current_image = 0 #showing index 0 img
        Female.image = Female.idle[Female.current_image] #link the idle sprite to the list
        Female.rect=Female.image.get_rect()
        Female.speedx =5
        Female.rect.x=-1
        Female.rect.y=window_height -Female.rect.height +25 #place the character bottom of the user screen

        #where the character facing for idle
        Female.facing_right = True
        Female.facing_left = []
        for i in Female.idle:
            flipped_img = pygame.transform.flip(i,True,False)
            Female.facing_left.append(flipped_img)

        #facing walking image 
        Female.walkingfacing_right = True
        Female.walkingfacing_left = []
        for i in Female.walking:
            flipped_img = pygame.transform.flip(i,True,False)
            Female.walkingfacing_left.append(flipped_img)

        Female.animation_timer =0
        Female.animation_delay =150 

    def update_character(Female):
        keys = pygame.key.get_pressed() #user press key

        moving = False
            
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            Female.rect.x=Female.rect.x-Female.speedx
            Female.facing_right = False
            Female.walkingfacing_right = False
            moving = True
            
                    
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            Female.rect.x = Female.rect.x + Female.speedx
            Female.facing_right = True
            Female.walkingfacing_right = True
            moving =True
                    
        #spawn right side of the screen if cross the left side
        if Female.rect.right < 0:
            Female.rect.x = window_width
        #spawn at left side if cross the right
        if Female.rect.left > window_width:
            Female.rect.right= 0 
            #fixed the jumping issue here before: rect.x=0

        #check if its moving or idle
        current_time = pygame.time.get_ticks()
        if moving: #animation timing
            if current_time - Female.animation_timer > Female.animation_delay +50:
                Female.animation_timer = current_time
                Female.current_image += 1
                if Female.current_image >= len(Female.walking):
                    Female.current_image = 0
            if Female.walkingfacing_right : #decides which one to show left or right
                Female.image = Female.walking[Female.current_image]
            else:
                Female.image = Female.walkingfacing_left[Female.current_image]
        #idle
        else:
            if current_time - Female.animation_timer > Female.animation_delay: #check if it alr 150ms
                Female.animation_timer =current_time 
                Female.current_image += 1 
                if Female.current_image >=len(Female.idle):
                    Female.current_image =0
            if Female.facing_right:
                Female.image = Female.idle[Female.current_image]
            else:
                Female.image =Female.facing_left[Female.current_image]
            
# Load and play background music
def play_background_music():
    pygame.mixer.init()
    pygame.mixer.music.load("Moodify/sound effect/lofi_music.wav") 
    pygame.mixer.music.set_volume(0.5)      
    pygame.mixer.music.play(-1)  # -1 means loop indefinitely

def play_rain_sound():
    raining_sound = pygame.mixer.Sound("Moodify/sound effect/raining sound.mp3") 
    raining_sound.set_volume(0.4)
    raining_sound.play(-1)
    

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
Fcharacter_image_idle = [
    pygame.image.load("Moodify/F-right/pixil-frame-0.png"),
    pygame.image.load("Moodify/F-right/pixil-frame-1.png"),
    pygame.image.load("Moodify/F-right/pixil-frame-2.png"),
    pygame.image.load("Moodify/F-right/pixil-frame-3.png"),
]

Fcharacter_walking_img =[
    pygame.image.load("Moodify/F-walking/pixil-frame-0.png"),
    pygame.image.load("Moodify/F-walking/pixil-frame-1.png"),
    pygame.image.load("Moodify/F-walking/pixil-frame-2.png"),
    pygame.image.load("Moodify/F-walking/pixil-frame-3.png"),
]



#(Spawn only once) 
#determine will rain or not
rain_group = rain_or_not()
#the female character 
Female_character=FemaleCharacter()

radio_entry = pygame.Rect(1000, 595, 160, 110) 

#bg music
play_background_music()





#game main loop
while True:
    for event in pygame.event.get(): #collects all the events and goes through it one by one
        if event.type == pygame.KEYDOWN:#check if any key is press 
            if event.key == pygame.K_ESCAPE: #if its the ESC key
                pygame.quit() # shut down eveythig u open/ initialized (includes the program that is running in the background)
                sys.exit() 
        if event.type == pygame.MOUSEBUTTONDOWN:
            if radio_entry.collidepoint(event.pos):
                print("Radio clicked")

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