import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()  #initialize the mixer for sound
# -----------------------------------------------------------------------------------------------------------------------------------
#initialize the game window with adaptive scaling
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]  # get the current monitor size
WIDTH, HEIGHT = 1280, 720  # default base resolution for scaling
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)  # create a resizable window
pygame.display.set_caption("Catch the Falling Stars")  # set the window title
fullscreen = False  # track if the game is in fullscreen mode (it starts as windowed)

#define function to get the current scaling factors based on the window size
def get_scale_factors(current_width, current_height): #a function that takes the current width and height of the window as input
    return current_width / WIDTH, current_height / HEIGHT 
#these factors are used to adjust the size and speed of game

# assign the scaling factors to this variable
scale_x, scale_y = get_scale_factors(screen.get_width(), screen.get_height())
# -----------------------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------------------
# Load Background Images for Different Moods
MOODS = {
    "Calm Night": pygame.image.load("catch_star/starrynight.png").convert(),
    "Peaceful Moonlight": pygame.image.load("catch_star/moonlight.png").convert(),
    "Serene Aurora": pygame.image.load("catch_star/aurora.png").convert()
} #.convert() --> change the pixel format of an image with no arguments, to create a copy that will draw more quickly on the screen
current_mood = "Calm Night" #sets the initial background mood
BACKGROUND = pygame.transform.scale(MOODS[current_mood], (screen.get_width(), screen.get_height())) #stretches/shrinks it to match the screen size.
mood_menu_active = False
mood_options = list(MOODS.keys()) #create a list of the mood names from the MOODS dictionary above
mood_index = 0
# -----------------------------------------------------------------------------------------------------------------------------------
# load sound effect
CATCH_SOUND = pygame.mixer.Sound("catch_star/catch_sound.wav")  # catching sound

# Load background music
pygame.mixer.music.load("catch_star/background_music.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Play in a loop (-1 means infinite loop)
# -----------------------------------------------------------------------------------------------------------------------------------

# load catcher image
PLAYER_WIDTH_RATIO = 225 / WIDTH  # calculate the ratio of the basket original width to the current window width
PLAYER_HEIGHT_RATIO = 190 / HEIGHT  # calculate the ratio of the basket original height to the current window height
PLAYER_IMAGE = pygame.image.load("catch_star/catcher.png").convert_alpha() #sincge the image has transparency bg, use alpha to avoid having solid color at the back
PLAYER_WIDTH = int(PLAYER_WIDTH_RATIO * screen.get_width())  # calculate the player width based on the screen size
PLAYER_HEIGHT = int(PLAYER_HEIGHT_RATIO * screen.get_height())  # calculate the player height based on the screen size
SCALED_PLAYER = pygame.transform.scale(PLAYER_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT))  # scale the player image

player_x = (screen.get_width() - PLAYER_WIDTH // 2)  # set the baskett in the center horizontally
player_y = int(0.9 * screen.get_height() - PLAYER_HEIGHT)  # set the basket near bottom, 10% padding
player_speed = 5 * scale_x  # player speed based on the screen size
# -----------------------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------------------

# star properties
STAR_IMAGES = [
    pygame.image.load("catch_star/star1.png").convert_alpha(),  # load the first star image
    pygame.image.load("catch_star/star2.png").convert_alpha()  # load the second star image
]

# scale the star images based on the current screen size
STAR_SIZE_RATIO = 200 / WIDTH  # RELATIVE STAR SIZE
STAR_SIZE = int(STAR_SIZE_RATIO * screen.get_width())  # scale the star size
SCALED_STAR_IMAGES = [pygame.transform.scale(img, (STAR_SIZE, STAR_SIZE)) for img in STAR_IMAGES]  # scale each star image
star_speed = int(2 / 1080 * screen.get_height())  # scale star speed based on current window height
stars = []  # list to store active stars
STAR_SPAWN_RATE = 60  # number of frames between each star spawn
# -----------------------------------------------------------------------------------------------------------------------------------

# score/Basket
resilience_points = 0 # set (number of caught stars) to zero
basket_capacity = 10  # number of stars the basket can hold
emotional_messages = [
    "Every catch is a small win, just like focusing on the good in life.",
    "Don't worry about the ones you miss; focus on the next one that comes your way.",
    "With patience and attention, you can gather moments of joy.",
    "Embrace the flow of the stars, just like you can embrace the flow of life.",
    "You are capable.",
    "Small wins count."
]
message_display = False
message_timer = 0
MESSAGE_DURATION = 180  # frames to display the message
current_message = ""

# initialize with scaling fonts
base_font_size = 36  # base font size for small text
large_font_size = 72  # base font size for large text

def get_scaled_font(size):
    return pygame.font.Font(None, int(size / 1080 * screen.get_height()))  # scale font size based on height

font = get_scaled_font(base_font_size)  # font for normal text multiplied by the ratio of the current height to the base height
large_font = get_scaled_font(large_font_size)  # font for large messages multiplied by the ratio of the current height to the base height
# -----------------------------------------------------------------------------------------------------------------------------------
def draw_player():
    screen.blit(SCALED_PLAYER, (player_x, player_y)) # draw the player at the current position

def draw_star(star_info):
    star_rect = star_info["rect"] # extract the rect object from the star_info dictionary
    image = star_info["image"]    # extract the surface object from the star_info dictionary
    screen.blit(image, star_rect)     # draw the star

def display_message():
    if message_display:
        scaled_large_font = get_scaled_font(large_font_size)  # scale font based on current height
        message_text = scaled_large_font.render(current_message, True, (0, 0, 0))  # render the message in black
        text_rect = message_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))  # creates .Rect object for the rendered text and center the message
        screen.blit(message_text, text_rect)  # draw the message

def draw_mood_menu():
     #create a semi-transparentish overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(180) # 180/255 transparency (70% opacity)
    overlay.fill((0, 0, 0)) # fill it with black
    screen.blit(overlay, (0, 0)) # covers entire screen
    scaled_large_font = get_scaled_font(large_font_size)

    for i, mood in enumerate(mood_options): #mood_options is a list of moods
        color = (255, 255, 255) if i == mood_index else (150, 150, 150)
        mood_text = scaled_large_font.render(mood, True, color)
        text_rect = mood_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 100 + i * 100))
        screen.blit(mood_text, text_rect)

# -----------------------------------------------------------------------------------------------------------------------------------
# Draw all the game elements on the screen
def draw_window():
    # scale the bg to match the current window size
    scaled_bg = pygame.transform.scale(BACKGROUND, (screen.get_width(), screen.get_height()))
    screen.blit(scaled_bg, (0, 0))  # draw the scaled background
    draw_player()  # draw the player
    for star_info in stars:  # draw each star
        draw_star(star_info)

    # draw the score text in the top left corner, display "Resilience"
    font_size = int(36 / 1080 * screen.get_height())  # scale font size based on height
    score_font = pygame.font.Font(None, font_size)  # create a scaled font
    score_text = score_font.render(f"Resilience: {resilience_points}/{basket_capacity}", True, (0, 0, 0))  # render the score text in black
    screen.blit(score_text, (int(0.10 * screen.get_width()), int(0.10 * screen.get_height())))  # 10% padding from the top left

    # draw the message if active
    display_message()
    if mood_menu_active: #if it is true, draw the mood menu
        draw_mood_menu()
    pygame.display.update()  # update the display to show the changes
# -----------------------------------------------------------------------------------------------------------------------------------

# Handle the screen resizing events to keep everything in scale
def handle_resize(event):
    global scale_x, scale_y, PLAYER_WIDTH, PLAYER_HEIGHT, SCALED_PLAYER, player_x, player_y, star_speed, STAR_SIZE, SCALED_STAR_IMAGES, BACKGROUND

    scale_x, scale_y = get_scale_factors(event.w, event.h)  # takes the new width (event.w) and new height (event.h) of the resized window from the event object

    # update player size and position
    PLAYER_WIDTH = int(225 * scale_x)  # scale player width
    PLAYER_HEIGHT = int(190 * scale_y)  # scale player height
    SCALED_PLAYER = pygame.transform.scale(PLAYER_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT))  # scale player image
    player_x = int((event.w - PLAYER_WIDTH) // 2)  # reposition player horizontally
    player_y = int((event.h - PLAYER_HEIGHT - 20))  # reposition player vertically

    # update star sizes and images
    STAR_SIZE = int(200 * scale_x)
    SCALED_STAR_IMAGES = [pygame.transform.scale(img, (STAR_SIZE, STAR_SIZE)) for img in STAR_IMAGES]
    for star_info in stars:
        star_info["rect"].width = STAR_SIZE
        star_info["rect"].height = STAR_SIZE
        star_info["image"] = random.choice(SCALED_STAR_IMAGES)

    # update star speed based on the new vertical scale
    star_speed = int(2 / 1080 * event.h)

    # scale bg to fit the new screen size
    BACKGROUND = pygame.transform.scale(MOODS[current_mood], (event.w, event.h))
# -----------------------------------------------------------------------------------------------------------------------------------

def main():
    global player_x, resilience_points, message_display, message_timer, current_message, mood_menu_active, mood_index, current_mood, BACKGROUND, frame_count, stars

    clock = pygame.time.Clock()
    run = True
    frame_count = 0

    while run:
        clock.tick(60)
        frame_count += 1

        for event in pygame.event.get(): # iterates through all the events that happened ( mouse clicks, key presses, window resizing).
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event)  # handle window resizing
            elif event.type == pygame.KEYDOWN: #checks if any key is pressed
                if event.key == pygame.K_f:
                    if screen.get_flags() & pygame.FULLSCREEN: # returns the current display flags (like FULLSCREEN RESIZABLE), the & (bitwise AND) checks if FULLSCREEN flag is active
                        pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)  # exit fullscreen
                    else:
                        pygame.display.set_mode((monitor_size[0], monitor_size[1]), pygame.FULLSCREEN)  # enter fullscreen
                    handle_resize(pygame.event.Event(pygame.VIDEORESIZE, {"w": screen.get_width(), "h": screen.get_height()}))
                elif event.key == pygame.K_m:
                    mood_menu_active = not mood_menu_active  # toggle mood menu
                elif mood_menu_active:
                    if event.key == pygame.K_UP:
                        mood_index = (mood_index - 1) % len(mood_options)  # cycle up
                    elif event.key == pygame.K_DOWN:
                        mood_index = (mood_index + 1) % len(mood_options)  # cycle down
                    elif event.key == pygame.K_RETURN:
                        current_mood = mood_options[mood_index]
                        BACKGROUND = pygame.transform.scale(MOODS[current_mood], (screen.get_width(), screen.get_height()))
                        mood_menu_active = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        # keep player within bounds
        if player_x < 0:
            player_x = 0
        if player_x > screen.get_width() - PLAYER_WIDTH:
            player_x = screen.get_width() - PLAYER_WIDTH

        # spawn new stars
        if not mood_menu_active: #Stars will only spawn if the mood menu is not active
            if frame_count % STAR_SPAWN_RATE == 0:
                star_x = random.randint(0, screen.get_width() - STAR_SIZE) # randomize number for x from possible positions
                star_rect = pygame.Rect(star_x, -STAR_SIZE, STAR_SIZE, STAR_SIZE)
                random_image = random.choice(SCALED_STAR_IMAGES)
                stars.append({"rect": star_rect, "image": random_image}) #stores the star images

            # move stars
            for star_info in stars[:]:
                star_rect = star_info["rect"]
                star_rect.y += star_speed # increases the star vertical position (y), making it fall down the screen
                player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
                if star_rect.colliderect(player_rect):
                    CATCH_SOUND.play()  # play the catch sound
                    stars.remove(star_info)
                    resilience_points += 1  # Increment resilience_points
                elif star_rect.y > screen.get_height():
                    stars.remove(star_info)

            # check if basket is full
            if resilience_points >= basket_capacity and not message_display:  # Check resilience_points
                message_display = True
                current_message = random.choice(emotional_messages)
                message_timer = 0

            # handle message display timer
            if message_display:
                message_timer += 1
                if message_timer > MESSAGE_DURATION:
                    message_display = False
                    resilience_points = 0  # Reset resilience_points
        else:
            stars = [] # Clear stars when mood menu is active

        draw_window()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

    #this is it
