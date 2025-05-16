import pygame
import sys 
import random
import datetime # to get user device time
import subprocess
import time

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
        rain.rect.x=random.randint(0,VIRTUAL_WIDTH)
        rain.rect.y=random.randint(-VIRTUAL_HEIGHT,-5)
        

    def update(rain):
            #when the sprite touches the the end of the screen, reuse the sprite to spawn it again
        if rain.rect.bottom >screen_height:
            rain.speedx=2
            rain.speedy= random.randint(10,20)
            rain.rect.x=random.randint(0,VIRTUAL_WIDTH)
            rain.rect.y=random.randint(-VIRTUAL_HEIGHT,-5)

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
        rain_group.draw(virtual_surface) #a screen blit for the rain group loops it one by one


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
        Female.rect.y=screen_height -Female.rect.height +25 #place the character bottom of the user screen

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
            Female.rect.x = screen_width
        #spawn at left side if cross the right
        if Female.rect.left > screen_width:
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


class dog(pygame.sprite.Sprite):
    def __init__(dog):
        pygame.sprite.Sprite.__init__(dog)
        dog.idle = dog_idle_img
        dog.walking = dog_walking_img
        dog.current_img =0
        dog.image =dog.idle[dog.current_img]
        dog.rect = dog.image.get_rect()
        dog.rect.x = random.randint(0,screen_width- dog.rect.width) # the rect will put the top left corner of the rectangle of the dog in this range(SO cannot put screen width as limit)
        dog.speedx = 3
        dog.rect.y = 495
        dog.state = "idle"
        dog.target_x =dog.rect.x
        dog.idle_time = pygame.time.get_ticks()
        
        dog.idlefacing_left =True
        dog.idlefacing_right= []
        for i in dog.idle:
            flipped_img = pygame.transform.flip(i,True,False)
            dog.idlefacing_right.append(flipped_img)

        dog.walkingfacing_left = True
        dog.walkingfacing_right = []
        for i in dog.walking:
            flipped_img = pygame.transform.flip(i,True,False)
            dog.walkingfacing_right.append(flipped_img)

        dog.animation_timer =0
        dog.animation_delay =150 
        

    def update_dog(dog):
        current_dog_time = pygame.time.get_ticks()
        
        #if the dog is idle more than 5s
        if dog.state == "idle":
            if current_dog_time - dog.idle_time > 5000:
                dog.target_x = random.randint(0, screen_width - dog.rect.width) #get target
                if dog.target_x < dog.rect.x: #to see where is the position do comparison
                    dog.speedx = -abs(dog.speedx) #abs always return positive value
                    dog.walkingfacing_left = True
                    dog.idlefacing_left = True
                else:
                    dog.speedx = abs(dog.speedx)
                    dog.walkingfacing_left = False
                    dog.idlefacing_left = False
                dog.state = "walking" #swicth to walk after comparison

        elif dog.state == "walking":
            dog.rect.x += dog.speedx #do the walking 
            if abs(dog.rect.x - dog.target_x) < abs(dog.speedx): #if its near the target then change to idle
                dog.rect.x = dog.target_x
                dog.state = "idle"
                dog.idle_time = current_dog_time

        if dog.state == "walking" :
            if current_dog_time - dog.animation_timer > dog.animation_delay:
                dog.animation_timer = current_dog_time
                dog.current_img +=1
                if dog.current_img >= len(dog.walking):
                    dog.current_img =0
            if dog.walkingfacing_left:
                    dog.image =dog.walking[dog.current_img]
            else: 
                    dog.image = dog.walkingfacing_right[dog.current_img]
        else:
            if current_dog_time - dog.animation_timer > dog.animation_delay +25:
                dog.animation_timer = current_dog_time
                dog.current_img +=1
                if dog.current_img >= len(dog.idle):
                    dog.current_img =0
            if dog.idlefacing_left:
                dog.image =dog.idle[dog.current_img]
            else: 
                dog.image = dog.idlefacing_right[dog.current_img]

def scale_bg():
    scaled_bg = pygame.transform.scale(background_surface, (screen_width, screen_height))
    return scaled_bg

        
# Load and play background music
def play_background_music():
    pygame.mixer.init()
    pygame.mixer.music.load("Moodify/sound effect/lofi_music.wav") 
    pygame.mixer.music.set_volume(0.5)      
    pygame.mixer.music.play(-1)  # -1 means loop indefinitely

raining_sound = None
def play_rain_sound():
    global raining_sound
    if raining_sound is None: 
        raining_sound = pygame.mixer.Sound("Moodify/sound effect/raining sound.mp3")
        raining_sound.set_volume(0.4)
    raining_sound.play(-1) 
    
def stop_rain_sound():
    global raining_sound
    if raining_sound: #if its a sound
        raining_sound.stop()

def picture_speech():
    speech_forpicture =["Arrr matey! Ready for an adventure?",
                        "Who dares disturb the captain's nap?",
                        "Legends say this painting hides a secret...",
                        "Shiver me timbers! Someone touched me painting!",
                        "Yo-ho-ho! Find the treasure if ye dare!"]
    speech = random.choice(speech_forpicture)
    return speech

def teddy_speech():
    speech_forteddy =["Shh... Teddy is sleeping",
                        "Teddy wants a cup of tea!",
                        "Mr. Bean will be back soon!",
                        "Teddy feels cozy here"]
    speech = random.choice(speech_forteddy)
    return speech 

def cockroach_speech():
    speech_forck =["You can't catch me!",
                        "Home sweet... kitchen!",
                        "I'm faster than you think!",
                        "Oops! You saw me!",
                        "Just passing through!",
                        "I'm tiny but mighty!"]
    speech = random.choice(speech_forck)
    return speech 

def plant_speech():
    speech_forplant =["Don't forget to water this one!",
                        "Ah, a little greenery to brighten the room!",
                        "A plant that never complains...",
                        "This plant's looking a bit thirsty...",
                        "If only it could talk, what would it say?",
                        "Hmm, should I name it? Maybe 'Leafy'?"]
    speech = random.choice(speech_forplant)
    return speech 

def sofa_speech():
    speech_forsofa =["Ah, a perfect spot to relax!",
                        "This looks like the comfiest seat in the house!",
                        "Is this where the magic of napping happens?",
                        "I could definitely spend a whole day on this.",
                        "This is where all the best TV shows are watched.",
                        "This sofa has ‘comfort’ written all over it!"]
    speech = random.choice(speech_forsofa)
    return speech 
#tried to fix the fullscreen alignment problem but failed using a virtual surface
VIRTUAL_WIDTH = 1280
VIRTUAL_HEIGHT = 720
#setting up pygame
pygame.init() # to start the system: sound,graphics etc of pygame module

screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
fullscreen =False
Time = pygame.time.Clock()
#set game speed
#get monitor size info (only accept current_w)
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
screen_width,screen_height = screen.get_size()
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))


#to get the users device time
current_hour = datetime.datetime.now().hour 

#----------------------------------------------------------------------------
#images
#raining image
raindrops= pygame.image.load("Moodify/graphics/raindrops.png").convert_alpha()

#night time image
night_background = pygame.image.load("Moodify/graphics/night.png").convert()

# day time image
sunny_background = pygame.image.load("Moodify/graphics/sunny day background.png").convert()

#background image
background_surface =pygame.image.load("Moodify/graphics/main game page no window.png").convert_alpha()
# to scale background image on the virtual surface
background_surface = scale_bg()


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

dog_walking_img =[ 
    pygame.image.load("Moodify/dog frames/pixil-frame-0.png"),
    pygame.image.load("Moodify/dog frames/pixil-frame-1.png"),
    pygame.image.load("Moodify/dog frames/pixil-frame-2.png"),
    pygame.image.load("Moodify/dog frames/pixil-frame-3.png"),
]

dog_idle_img =[
    pygame.image.load("Moodify/dog idle frame/pixil-frame-0.png"),
    pygame.image.load("Moodify/dog idle frame/pixil-frame-1.png"),
    pygame.image.load("Moodify/dog idle frame/pixil-frame-2.png"),
    pygame.image.load("Moodify/dog idle frame/pixil-frame-3.png"),
]
#TV and radio img
TV_mini_games_img =pygame.image.load("Moodify/graphics/mini games interface.png")
quit_button_img = pygame.image.load("Moodify/graphics/cancel button.png")
radio_img = pygame.image.load("Moodify/graphics/radio interface.png")
plant_img =pygame.image.load("Moodify/graphics/plant interface.png")
watering_pot =pygame.image.load("Moodify/graphics/watering pot.png")
waterdrops = pygame.image.load("Moodify/graphics/water drops.png")
water_button = pygame.image.load("Moodify/graphics/water button.png")
watering_button_rect = water_button.get_rect()

#icon in TV
bubble_icon = pygame.image.load("Moodify/bubble popper/1.png").convert_alpha()
bubble_icon_rect = bubble_icon.get_rect(center=(300, 200)) 
open_bubble_popper = False

# speech bar position and img
Speech_bar =pygame.image.load("Moodify/graphics/speech bar.png")
speechbar_rect =Speech_bar.get_rect()
speechbar_rect.x = 300
speechbar_rect.y =520
show_text =False

#to other feature img
hourglass_img = pygame.image.load("Moodify/graphics/hourglass.png")
hourglass_rect = hourglass_img.get_rect()
hourglass_rect.x = 130
hourglass_rect.y = 355
breathing_process = None

diary_img = pygame.image.load("Moodify/graphics/diary.png")
diary_rect = diary_img.get_rect()
diary_rect.x = 920
diary_rect.y = 455
diary_process = None

moodtracker_img = pygame.image.load("Moodify/graphics/mood tracker.png")
moodtracker_rect = moodtracker_img.get_rect()
moodtracker_rect.x= 350
moodtracker_rect.y= 70
moodtracker_process = None

play_button_img = pygame.image.load("Moodify/graphics/play button.png")
play_button_rect = play_button_img.get_rect()
play_button_rect.x = 550
play_button_rect.y = 400
tkinterradio_process = None

calendar_img = pygame.image.load("Moodify/graphics/calendar.png")
calendar_rect = calendar_img.get_rect()
calendar_rect.x= 370
calendar_rect.y= 140
calendar_process = None


#--------------------------------------------------------------------------

#determine will rain or not
rain_group = rain_or_not()
#the female character 
Female_character=FemaleCharacter()
dog_character=dog()

#Tv plant and radio entry
radio_entry = pygame.Rect(800, 480, 130, 80) 
TV_entry = pygame.Rect(251, 275, 230, 150) 
plant_entry =pygame.Rect(500,290,100,140)
watering_button_rect.topleft=(60,50)
show_tv_screen = False
show_radio =False
show_plant = False
watering = False
watering_timer =0 
waterdrop_y = 0

#interaction points
picture = pygame.Rect(90,55,250,180)
teddy = pygame.Rect(1150,420,80,120)
cockroach = pygame.Rect(54,550,40,50)
sofa = pygame.Rect(220,470,530,180)


#bg music
play_background_music()

#text font size 
font =pygame.font.Font(None,30)




#game main loop
while True:
    for event in pygame.event.get(): #collects all the events and goes through it one by one
        if event.type == pygame.QUIT:
            if calendar_process and calendar_process.poll() is None:# if its not open = None for first statement no action taken / open before but closed alr, poll() will check and see if its open if open poll()=None 
                calendar_process.terminate()
            if diary_process and diary_process.poll() is None:
                diary_process.terminate()
            if moodtracker_process and moodtracker_process.poll() is None:
                moodtracker_process.terminate()
            if tkinterradio_process and tkinterradio_process.poll() is None:
                tkinterradio_process.terminate()
            if breathing_process and breathing_process.poll()is None:
                breathing_process.terminate()
            sys.exit() 
        if event.type == pygame.KEYDOWN:#check if any key is press 
            if event.key == pygame.K_ESCAPE: #if its the ESC key
                pygame.quit() # shut down eveythig u open/ initialized (includes the program that is running in the background)
                sys.exit() 
            if event.key == pygame.K_f:
                if fullscreen == False:
                    screen = pygame.display.set_mode((monitor_size),pygame.FULLSCREEN)
                    fullscreen = True 
                elif fullscreen == True:
                    screen = pygame.display.set_mode((VIRTUAL_WIDTH,VIRTUAL_HEIGHT)) 
                    fullscreen = False
                #rescale bg to fit the current screen
                screen_width, screen_height = screen.get_size()
                scaled_bg = scale_bg()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if show_tv_screen:
                if TV_quit_button_rect.collidepoint(event.pos):
                    show_tv_screen = False
                    pygame.mixer.music.unpause()
                    play_rain_sound()
                if bubble_icon_rect.collidepoint(event.pos):
                    open_bubble_popper = True
            if show_radio:
                if Radio_quit_button_rect.collidepoint(event.pos):
                    show_radio =False
                if play_button_rect.collidepoint(event.pos):
                    if not tkinterradio_process or tkinterradio_process is not None:
                        pygame.mixer.music.stop() #stop the music
                        stop_rain_sound()
                        subprocess.Popen(["Python","Moodify/tkinter pages/sound/sound_.py"])
                        
            if show_plant:
                if plant_quit_button_rect.collidepoint(event.pos):
                    show_plant =False
                if watering_button_rect.collidepoint(event.pos):
                    watering = True
                    watering_timer = pygame.time.get_ticks()
                    waterdrop_y =350
                    

            elif not show_tv_screen and not show_radio and not show_plant:
                if radio_entry.collidepoint(event.pos): #where it click on and check if its inside the box
                    show_radio =True
                if TV_entry.collidepoint(event.pos):
                    show_tv_screen = True
                if plant_entry.collidepoint(event.pos):
                    show_plant = True
                if teddy.collidepoint(event.pos):
                    show_text =True
                    text_surface = font.render(teddy_speech(),True,(0,0,0))
                    text_rect =text_surface.get_rect(center =speechbar_rect.center)
                if cockroach.collidepoint(event.pos):
                    show_text =True
                    text_surface = font.render(cockroach_speech(),True,(0,0,0))
                    text_rect =text_surface.get_rect(center =speechbar_rect.center)
                if sofa.collidepoint(event.pos):
                    show_text =True
                    text_surface = font.render(sofa_speech(),True,(0,0,0))
                    text_rect =text_surface.get_rect(center =speechbar_rect.center)
                if picture.collidepoint(event.pos):
                    show_text =True
                    text_surface = font.render(picture_speech(),True,(0,0,0))
                    text_rect =text_surface.get_rect(center =speechbar_rect.center)
                
                    
                # Only close the speech bar if not clicking on any important object
                if not (teddy.collidepoint(event.pos) or cockroach.collidepoint(event.pos) or sofa.collidepoint(event.pos) or picture.collidepoint(event.pos)):
                    show_text = False
                
                if diary_rect.collidepoint(event.pos):
                    if not diary_process or diary_process.poll() is not None:
                        subprocess.Popen(["Python","Moodify/tkinter pages/diary_.py"]) 

                if calendar_rect.collidepoint(event.pos):
                    if not calendar_process or calendar_process.poll() is not None:#if its not open yet or close rn poll()is not None = closed
                        calendar_process = subprocess.Popen(["Python","Moodify/tkinter pages/calendar_.py"])

                if moodtracker_rect.collidepoint(event.pos):
                    if not moodtracker_process or moodtracker_process.poll() is not None:
                        calendar_process = subprocess.Popen(["Python","Moodify/tkinter pages/moodtracker/moodtracker_.py"])
                
                if hourglass_rect.collidepoint(event.pos):
                    if not breathing_process or moodtracker_process.poll() is not None:
                        breathing_process = subprocess.Popen(["Python","Moodify/tkinter pages/breathing/timer.py"])
    
    scaled_surface = pygame.transform.scale(virtual_surface, (screen_width, screen_height))
    screen.blit(scaled_surface,(0,0))

    #the night and day background
    current_hour = datetime.datetime.now().hour
    if 7 <= current_hour < 18: #set time between  7 to 6pm
        virtual_surface.blit(sunny_background, (420,40))
    else:
        virtual_surface.blit(night_background, (460,40))

    #if it rain the display if not None
    display_rain(rain_group)

    virtual_surface.blit(background_surface,(0,0))

    virtual_surface.blit(diary_img,diary_rect)
    virtual_surface.blit(calendar_img,calendar_rect)
    virtual_surface.blit(moodtracker_img,moodtracker_rect)
    virtual_surface.blit(hourglass_img,hourglass_rect)

    dog_character.update_dog()
    virtual_surface.blit(dog_character.image,dog_character.rect)

    Female_character.update_character()
    virtual_surface.blit(Female_character.image,Female_character.rect)

    
    #for the Tv mini game interface
    if show_tv_screen:
        scaled_tv_image = pygame.transform.scale(TV_mini_games_img,(VIRTUAL_WIDTH,VIRTUAL_HEIGHT))
        virtual_surface.blit(scaled_tv_image,(0,0))
        TV_quit_button_rect = quit_button_img.get_rect()
        TV_quit_button_rect.topright =(1145,80) 
        virtual_surface.blit(quit_button_img,TV_quit_button_rect)
        virtual_surface.blit(bubble_icon, bubble_icon_rect)

    if show_radio:
        scaled_radio_img = pygame.transform.scale(radio_img,(VIRTUAL_WIDTH,VIRTUAL_HEIGHT))
        virtual_surface.blit(scaled_radio_img,(0,0))
        Radio_quit_button_rect = quit_button_img.get_rect()
        Radio_quit_button_rect.topright =(1100,130) 
        virtual_surface.blit(quit_button_img,Radio_quit_button_rect)
        virtual_surface.blit(play_button_img,play_button_rect)
        
    
    if show_plant:
        scaled_plant_img =pygame.transform.scale(plant_img,(VIRTUAL_WIDTH,VIRTUAL_HEIGHT))
        virtual_surface.blit(scaled_plant_img,(0,0))
        plant_quit_button_rect = quit_button_img.get_rect()
        plant_quit_button_rect.topright =(1200,40) 
        virtual_surface.blit(quit_button_img,plant_quit_button_rect)
        virtual_surface.blit(water_button,watering_button_rect)
        
    if watering :
        virtual_surface.blit(watering_pot,(710,150))
        virtual_surface.blit(waterdrops,(630,waterdrop_y))
        waterdrop_y+=3
        #reset waterdrops
        if waterdrop_y> 420:
            waterdrop_y =350

        if pygame.time.get_ticks() - watering_timer >3000 :
            watering = False


    if show_text:
        virtual_surface.blit(Speech_bar,speechbar_rect)
        virtual_surface.blit(text_surface,text_rect)

    if open_bubble_popper:
        process =subprocess.Popen([sys.executable,"Moodify/bubble popper/buble poper.py"]) #without freezing the main game
        open_bubble_popper =False #avoid open multiple times

  
    

    
    
    
        

    pygame.display.update() #update the display of the screen 
    Time.tick(60)# tells loop dont just faster then 60 fps