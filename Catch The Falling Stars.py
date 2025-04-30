import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()  #initialize the mixer for sound

#define screen dimensions
WIDTH = 1920
HEIGHT = 1020
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch the Falling Stars")

#load background image
BACKGROUND = pygame.image.load("nightsky.png").convert()  #background image
BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))

#load sound effect
CATCH_SOUND = pygame.mixer.Sound("catch_sound.wav")  #catching sound

# Load background music
pygame.mixer.music.load("background_music.wav") 
pygame.mixer.music.set_volume(0.5)  
pygame.mixer.music.play(-1)  # Play in a loop (-1 means infinite loop)

#load catchet image
PLAYER_IMAGE = pygame.image.load("catcher.png").convert_alpha()   
PLAYER_WIDTH = 225
PLAYER_HEIGHT = 190
SCALED_PLAYER = pygame.transform.scale(PLAYER_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT))
player_x = (WIDTH - PLAYER_WIDTH) // 2
player_y = HEIGHT - PLAYER_HEIGHT - 20
player_speed = 5

#star properties
STAR_IMAGES = [
    pygame.image.load("star1.png").convert_alpha(),  #load first star image
    pygame.image.load("star2.png").convert_alpha()   #load second star image
]
STAR_SIZE = 200  #size of the star
SCALED_STAR_IMAGES = [pygame.transform.scale(img, (STAR_SIZE, STAR_SIZE)) for img in STAR_IMAGES]
star_speed = 2
stars = []
STAR_SPAWN_RATE = 30  #spawn a new star every X frames

#score/Basket
caught_stars = 0
basket_capacity = 10 #number of stars the basket can hold
emotional_messages = [
    "You're doing great!",
    "Keep catching those stars!",
    "You're a star catcher!",
    "Feeling the calm...",
    "Wonderful!",
    "Embrace the good feelings."
]
message_display = False
message_timer = 0
MESSAGE_DURATION = 180  #frames to display the message
current_message = ""
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

def draw_player():
    WIN.blit(SCALED_PLAYER, (player_x, player_y))

def draw_star(star_info):
    star_rect = star_info["rect"]
    image = star_info["image"]
    WIN.blit(image, star_rect)

def display_message():
    message_text = large_font.render(current_message, True, (200, 200, 200))
    text_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    WIN.blit(message_text, text_rect)

def draw_window():
    WIN.blit(BACKGROUND, (0, 0))  #draw the background
    draw_player()
    for star_info in stars:
        draw_star(star_info)
    if message_display:
        display_message()
    score_text = font.render(f"Caught: {caught_stars}/{basket_capacity}", True, (200, 200, 200))
    WIN.blit(score_text, (10, 10))
    pygame.display.update()

def main():
    global player_x, caught_stars, message_display, message_timer, current_message

    clock = pygame.time.Clock()
    run = True
    frame_count = 0

    while run:
        clock.tick(60)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        #keep player within bounds
        if player_x < 0:
            player_x = 0
        if player_x > WIDTH - PLAYER_WIDTH:
            player_x = WIDTH - PLAYER_WIDTH

        #spawn new stars
        if frame_count % STAR_SPAWN_RATE == 0:
            star_x = random.randint(0, WIDTH - STAR_SIZE)
            star_rect = pygame.Rect(star_x, -STAR_SIZE, STAR_SIZE, STAR_SIZE)
            random_image = random.choice(SCALED_STAR_IMAGES)
            stars.append({"rect": star_rect, "image": random_image})

        #move stars
        for star_info in stars[:]:
            star_rect = star_info["rect"]
            star_rect.y += star_speed
            player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
            if star_rect.colliderect(player_rect):
                CATCH_SOUND.play()  #play the catch sound
                stars.remove(star_info)
                caught_stars += 1
            elif star_rect.y > HEIGHT:
                stars.remove(star_info)

        #check if basket is full
        if caught_stars >= basket_capacity and not message_display:
            message_display = True
            current_message = random.choice(emotional_messages)
            message_timer = 0

        #handle message display timer
        if message_display:
            message_timer += 1
            if message_timer > MESSAGE_DURATION:
                message_display = False
                caught_stars = 0 #reset the basket

        draw_window()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()