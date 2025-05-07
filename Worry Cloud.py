import pygame
import os
import random

pygame.init() #gotta start pygame

#paths for my files. need to make sure 'worry_cloud' folder is there.
MUSIC_PATH = os.path.join("Worry_cloud", "calm_music.wav")
RAIN_SOUND_PATH = os.path.join("Worry_cloud", "rain_sound.wav")
# Keeping the background as star_bg2.jpg 
BACKGROUND_IMG_PATH = os.path.join("Worry_cloud", "star_bg2.jpg")
CLOUD_IMG_PATH = os.path.join("Worry_cloud", "cloud.png") #for the worry cloud
CLOUD2_IMG_PATH = os.path.join("Worry_cloud", "cloud2.png") #for background clouds

#play the ambient music.
#first, check if the music file actually exists.
pygame.mixer.music.load(MUSIC_PATH)
pygame.mixer.music.set_volume(0.5) #not too loud
pygame.mixer.music.play(-1) #loop it forever


#now the rain sound.
#also check if this file exists.
rain_sound = None # Initialize to None
rain_sound = pygame.mixer.Sound(RAIN_SOUND_PATH)
rain_sound.set_volume(0.6)


music_on = True #keep track of whether music is playing 

#setting up the screen.
screen_width, screen_height = 1920, 1020 #my preferred dimensions
try:
    screen = pygame.display.set_mode((screen_width, screen_height))
except pygame.error as e:
    #if the big resolution fails, try a smaller one.
    print(f"oops, couldn't set display mode: {e}")
    print("trying 1280x720 instead...")
    screen_width, screen_height = 1280, 720
    screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Worry Cloud") # title

#define my colors and font.
white = (255, 255, 255)
black = (0, 0, 0)
light_gray = (200, 200, 200)
#using a slightly different cloud color for drawn background clouds if image fails
drawn_bg_cloud_color = (220, 220, 240, 150)

#try to load my preferred font, otherwise use a system default.
font = None # Main font for titles, buttons, released worry text
small_font = None # For messages
input_text_font = None # Font for text inside the input box

try:
    font = pygame.font.Font(None, 48) #main font
    small_font = pygame.font.Font(None, 36) #for smaller messages
    input_text_font = pygame.font.Font(None, 22) # Smaller font for input box text (adjust size as needed)

except pygame.error as e:
    print(f"problem loading default font: {e}. using system font for now.")
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    input_text_font = pygame.font.SysFont(None, 22)


#load the background image.
try:
    background = pygame.image.load(BACKGROUND_IMG_PATH)
    background = pygame.transform.scale(background, (screen_width, screen_height)) #scale it to fit screen
except pygame.error as e:
    print(f"couldn't load background image: {e}. i'll use a solid color for now.")
    background = pygame.Surface((screen_width, screen_height))
    background.fill((20, 20, 50)) #a dark blue as a fallback (keeping original fallback)

#load the image for my "worry" cloud.
use_image_cloud = os.path.exists(CLOUD_IMG_PATH) #check if i have the image
cloud_img = None # Initialize cloud_img
if use_image_cloud:
    try:
        original_cloud_img = pygame.image.load(CLOUD_IMG_PATH).convert_alpha() #use convert_alpha for transparency
        cloud_img = pygame.transform.scale(original_cloud_img, (240, 130)) #resize it (keeping original size)
    except pygame.error as e:
        print(f"couldn't load cloud image: {e}. i'll draw one instead.")
        use_image_cloud = False #fallback to drawing
else:
    print(f"self-note: cloud image {CLOUD_IMG_PATH} not found. i'll draw the worry cloud.")

# Dimensions for the drawn worry cloud fallback (keeping original size)
drawn_worry_cloud_size = (180, 100)


#this is for the input box where i'll type my worries.
input_box_width = 500 # Increased width
input_box_height = 200 # Increased height
input_box = pygame.Rect(
    (screen_width - input_box_width) // 2, #center it horizontally
    (screen_height - input_box_height) // 2, #center it vertically
    input_box_width,
    input_box_height)
text = '' #this will store the text i type
active = False #is the input box currently active?

#blinking cursor variables
cursor_blink_interval = 30  #frames (e.g., 30 frames = 0.5s at 60fps)
cursor_timer = 0
cursor_visible = True

# Increased the character limit to fit around 100 words
MAX_INPUT_CHARS = 1000 # Allowing up to approx 1000 characters


#the "release" button.
button_width = 150
button_height = 50
button_rect = pygame.Rect(
    (screen_width - button_width) // 2, #center it
    input_box.bottom + 30,  #position it below the input box
    button_width,
    button_height)

button_text_render = font.render("Release", True, black) #text for the button
button_color = light_gray #normal button color
button_hover_color = (170, 170, 170) #color when mouse is over it

#settings for the fading "worry" cloud.
fade_alpha = 255 #initial alpha value (fully opaque)
fading = False #is it currently fading?
fade_pos = (0, 0) #position of the fading cloud
fade_text_surface = None #i'll pre-render the (potentially truncated) fading text onto this surface.

#class for the little stars in the background.
class Star:
    def __init__(self):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.speed = random.uniform(0.1, 0.5) #nice and slow drift
        self.size = random.randint(1, 2)      #keep them small
        self.color = (random.randint(200,255), random.randint(200,255), random.randint(200,255)) #slightly different shades of white

    def update(self):
        self.y += self.speed #move downwards
        if self.y > screen_height:
            self.y = 0 #reset to the top
            self.x = random.randint(0, screen_width) #give it a new x position

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

stars = [Star() for _ in range(150)] #let's have 150 stars.

#class for the bigger, drifting background clouds.
class BackgroundCloud:
    def __init__(self):
        self.image = None #to store the loaded cloud image
        try:
            #try loading cloud2.png
            original_image = pygame.image.load(CLOUD2_IMG_PATH).convert_alpha()
            #randomly scale the image
            scale = random.uniform(0.5, 1.2) #scale between 50% and 120% of original size
            new_width = int(original_image.get_width() * scale)
            new_height = int(original_image.get_height() * scale)
            self.image = pygame.transform.scale(original_image, (new_width, new_height))
            self.width = new_width
            self.height = new_height
        except pygame.error as e:
            print(f"self-note: couldn't load {CLOUD2_IMG_PATH} for background cloud: {e}. drawing one instead.")
            #fallback to drawn ellipse if image loading fails
            self.width = random.randint(100, 300)
            self.height = random.randint(50, 150)
            self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA) #surface for transparency
            # Use the drawn_bg_cloud_color which has transparency
            pygame.draw.ellipse(self.surface, drawn_bg_cloud_color, (0, self.height * 0.2, self.width * 0.7, self.height * 0.7))
            pygame.draw.ellipse(self.surface, drawn_bg_cloud_color, (self.width * 0.3, 0, self.width * 0.7, self.height * 0.8))
            pygame.draw.ellipse(self.surface, drawn_bg_cloud_color, (self.width * 0.1, self.height*0.1, self.width * 0.8, self.height*0.9))


        self.x = random.randint(-self.width, screen_width) #some can start off-screen
        self.y = random.randint(50, screen_height // 3) #keep them in the upper part
        self.speed = random.uniform(0.2, 0.7) #different speeds for variety


    def update(self):
        self.x += self.speed #move horizontally
        if self.x > screen_width:
            self.x = -self.width #if it goes off-screen right, reset to the left
            self.y = random.randint(50, screen_height // 3) #maybe a new y position too
            self.speed = random.uniform(0.2, 0.7) # new random speed


    def draw(self, surface_to_draw_on):
        if self.image:
            surface_to_draw_on.blit(self.image, (int(self.x), int(self.y)))
        elif hasattr(self, 'surface'): #if using fallback drawn cloud
            surface_to_draw_on.blit(self.surface, (int(self.x), int(self.y)))

background_clouds = [BackgroundCloud() for _ in range(7)] #about 7 of these should be good.

#for displaying messages like "music on/off".
message_text = ""
message_alpha = 0 #start fully transparent
message_timer = 0 #how long the message stays

#function to show a message on screen for a bit.
def display_message(text_to_show, duration=120): #duration in frames (120 frames = 2 secs at 60fps)
    global message_text, message_alpha, message_timer #need to modify these global ones
    message_text = text_to_show
    message_alpha = 255 #make it fully visible
    message_timer = duration #set how long it shows

#function to prepare and initiate the fading worry cloud
def release_worry(current_worry_text_param):
    global fade_text_surface, fade_pos, text, fade_alpha, fading, active #allow modification of globals

    # Determine the dimensions of the worry cloud being displayed (keeping original size)
    if use_image_cloud and cloud_img:
        worry_cloud_display_width = cloud_img.get_width()
        worry_cloud_display_height = cloud_img.get_height()
    else: # Drawn worry cloud fallback
        worry_cloud_display_width = drawn_worry_cloud_size[0]
        worry_cloud_display_height = drawn_worry_cloud_size[1]


    #determine the maximum width for text on the worry cloud (e.g., 85% of cloud's width)
    max_text_width_on_cloud = worry_cloud_display_width * 0.85

    # Render the text for the fading cloud using the main font (size 48)
    # Taking only the first line and truncating for the cloud display
    display_text_on_cloud = current_worry_text_param.splitlines()[0].strip() if current_worry_text_param.strip() else ""
    if len(display_text_on_cloud) > 30: # Arbitrary limit for the cloud display text before fine truncation
         display_text_on_cloud = display_text_on_cloud[:30]


    temp_surface = font.render(display_text_on_cloud, True, black)
    if temp_surface.get_width() > max_text_width_on_cloud:
        #text is too long, so i need to truncate it and add "..."
        while len(display_text_on_cloud) > 0 and font.render(display_text_on_cloud + "...", True, black).get_width() > max_text_width_on_cloud:
             display_text_on_cloud = display_text_on_cloud[:-1]

        # Add ellipsis if text was truncated AND there was original text
        if display_text_on_cloud != current_worry_text_param.splitlines()[0].strip():
             display_text_on_cloud += "..."


    fade_text_surface = font.render(display_text_on_cloud, True, black)

    #calculate position for the fading cloud - center above the input box
    fade_pos = (screen_width // 2 - worry_cloud_display_width // 2, input_box.top - worry_cloud_display_height - 20) # position it above the input box


    text = '' #clear the input box
    fade_alpha = 255 #reset alpha for the fade
    fading = True    #start the fading animation!
    if rain_sound: #if i have the rain sound loaded
        try:
             # Play on an available channel
             channel = pygame.mixer.find_channel()
             if channel:
                 channel.play(rain_sound)
             else:
                 print("self-note: No free mixer channels to play rain sound.")
        except pygame.error as e:
             print(f"self-note: Failed to play rain sound: {e}")


    active = True #set input box to active so player can type next worry immediately
    global cursor_timer, cursor_visible #reset cursor for immediate visibility
    cursor_timer = 0
    cursor_visible = True


clock = pygame.time.Clock() #my game clock
running = True #main loop flag

#this is my main game loop!
while running:
    #handle all events (mouse clicks, key presses, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #if i click the close button
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #left mouse button
                if input_box.collidepoint(event.pos): #did i click inside the input box?
                    active = True
                    cursor_timer = 0 #reset cursor blink on click
                    cursor_visible = True
                else:
                    active = False

                #did i click the "release" button and is there text to release?
                if button_rect.collidepoint(event.pos) and text.strip():
                    release_worry(text) #call the function to handle releasing

        elif event.type == pygame.KEYDOWN: #a key was pressed
            if active: #only if the input box is active
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1] #delete last character
                    cursor_timer = 0 #reset cursor blink
                    cursor_visible = True
                elif event.key == pygame.K_RETURN: #if i press enter
                     # Check for Shift+Enter for new line, otherwise release
                     # Note: This basic implementation doesn't visually wrap text in the box
                     if event.mod & pygame.KMOD_SHIFT:
                         # Add a newline character if within limit
                         if len(text) < MAX_INPUT_CHARS:
                              text += '\n'
                         cursor_timer = 0
                         cursor_visible = True
                     elif text.strip(): # Only release if there's non-whitespace text
                         release_worry(text) #call the function to handle releasing

                else:
                    #add typed character to my text, but limit length
                    if len(text) < MAX_INPUT_CHARS: # Use the increased limit
                        text += event.unicode
                    cursor_timer = 0 #reset cursor blink
                    cursor_visible = True

            # Removed the music toggle ('m' key) functionality as requested
            # if event.key == pygame.K_m: #'m' key for music toggle
            #     ... (removed)


    #update blinking cursor logic
    if active:
        cursor_timer += 1
        if cursor_timer >= cursor_blink_interval:
            cursor_timer = 0
            cursor_visible = not cursor_visible
    else:
        cursor_visible = False #cursor shouldn't be visible if input is not active


    #update all my game elements.
    for star_obj in stars:
        star_obj.update()

    for bg_cloud_obj in background_clouds:
        bg_cloud_obj.update()

    #drawing everything on the screen, order matters (back to front).
    screen.blit(background, (0, 0)) #1. my main background image/color.

    for star_obj in stars: #2. draw the stars.
        star_obj.draw(screen)

    for bg_cloud_obj in background_clouds: #3. draw the drifting background clouds.
        bg_cloud_obj.draw(screen)

    #draw the input box.
    # Draw box border first, then fill, or fill first then border, depending on desired look
    pygame.draw.rect(screen, black, input_box, 2, border_radius=5) #the border
    pygame.draw.rect(screen, light_gray if active else white, input_box, 0, border_radius=5) # Fill


    # Render input text using the smaller input_text_font.
    txt_surface_for_input = input_text_font.render(text, True, black)

    # Calculate the inner rectangle where text should be displayed
    text_padding = 10
    text_area_rect = pygame.Rect(
        input_box.x + text_padding,
        input_box.y + text_padding, # Position from top-left with padding
        input_box.width - 2 * text_padding, # Visible width
        input_box.height - 2 * text_padding # Visible height
    )

    # Calculate the portion of the text surface to blit (for horizontal scrolling effect)
    text_surface_width = txt_surface_for_input.get_width()
    visible_area_width = text_area_rect.width

    # Determine the starting x-coordinate on the source text surface
    # If text is wider than the visible area, blit from the right part of the text surface
    source_x = max(0, text_surface_width - visible_area_width)

    # Define the area rectangle on the source text surface to copy
    # The height of the area should match the height of the rendered text line, not the text_area_rect height
    text_surface_height = input_text_font.get_height() # Use font height as the rendered surface height will vary
    source_area = pygame.Rect(source_x, 0, visible_area_width, text_surface_height)

    # Blit the calculated area from the text surface to the screen at the text area's topleft
    # Added a check to ensure text surface is not empty before blitting
    if txt_surface_for_input.get_width() > 0 and txt_surface_for_input.get_height() > 0:
         screen.blit(
             txt_surface_for_input,
             text_area_rect.topleft, # Destination position on the screen
             source_area # Area on the source surface to blit
         )


    #draw blinking cursor if input box is active
    if active and cursor_visible:
        # Calculate cursor position relative to the start of the visible text area
        # The cursor's x-position is the left edge of the text area plus the width of the text
        # that is currently visible (which is the total text width minus the scrolled-off part).
        # Using the actual rendered width might be better if the text contains leading/trailing spaces
        # cursor_x_pos = text_area_rect.left + txt_surface_for_input.get_width() - source_x # Using rendered width
        # Simpler approach assuming single line and left alignment within the clip:
        # Position is at the left edge of the text area + width of the currently rendered text surface
        cursor_x_pos = text_area_rect.left + txt_surface_for_input.get_width()

        # Ensure cursor stays within the horizontal bounds of the visible text area
        cursor_x_pos = min(cursor_x_pos, text_area_rect.right) # Don't draw past the right edge

        # The cursor vertical position is aligned with the top of the text line
        cursor_y_start = text_area_rect.top
        cursor_y_end = cursor_y_start + input_text_font.get_height() # Cursor height matches font height

        # Only draw the cursor if its horizontal position is within the visible text area
        if cursor_x_pos >= text_area_rect.left and cursor_x_pos <= text_area_rect.right:
             pygame.draw.line(screen, black, (cursor_x_pos, cursor_y_start), (cursor_x_pos, cursor_y_end), 2)


    #draw the "release" button.
    mouse_pos = pygame.mouse.get_pos() #where is the mouse?
    # Keeping original button hover behavior (highlights regardless of text)
    current_button_color = button_hover_color if button_rect.collidepoint(mouse_pos) else button_color
    pygame.draw.rect(screen, current_button_color, button_rect, border_radius=10) #rounded corners look nice

    # Ensure button text is centered even if button color changes
    screen.blit(button_text_render, button_text_render.get_rect(center=button_rect.center))


    #this is where i handle the fading "worry" cloud.
    if fading:
        current_fade_alpha_val = max(0, int(fade_alpha)) #alpha can't be negative.

        cloud_center_x, cloud_center_y = 0, 0
        cloud_to_draw = None # Surface to blit for the cloud graphic

        if use_image_cloud and cloud_img: #if i'm using the worry cloud image and it loaded
            cloud_to_draw = cloud_img.copy() #copy so original isn't changed
            cloud_to_draw.set_alpha(current_fade_alpha_val)
            # screen.blit(cloud_to_draw, fade_pos) # Blit handled below after getting center
            cloud_center_x = fade_pos[0] + cloud_img.get_width() // 2
            cloud_center_y = fade_pos[1] + cloud_img.get_height() // 2
        else:
            #if no image, i'll draw a simple ellipse for the worry cloud.
            # Create a temporary surface with transparency for the drawn cloud
            drawn_cloud_surface = pygame.Surface(drawn_worry_cloud_size, pygame.SRCALPHA)
            # Draw the ellipse onto this temporary surface
            # Use white color for the main worry cloud drawing
            pygame.draw.ellipse(drawn_cloud_surface, (255, 255, 255, current_fade_alpha_val), drawn_cloud_surface.get_rect())
            cloud_to_draw = drawn_cloud_surface # Assign the drawn surface to cloud_to_draw
            # screen.blit(worry_cloud_surface_render, fade_pos) # Blit handled below after getting center
            cloud_center_x = fade_pos[0] + drawn_worry_cloud_size[0] // 2
            cloud_center_y = fade_pos[1] + drawn_worry_cloud_size[1] // 2

        # Blit the cloud image/surface at the calculated fading position
        if cloud_to_draw:
             screen.blit(cloud_to_draw, fade_pos)


        if fade_text_surface: #if i have my pre-rendered (and truncated) text
            fade_text_surface.set_alpha(current_fade_alpha_val) #apply the same alpha
            text_rect = fade_text_surface.get_rect(center=(cloud_center_x, cloud_center_y))
            screen.blit(fade_text_surface, text_rect)

        #update parameters for the next frame of the fade.
        fade_pos = (fade_pos[0], fade_pos[1] - 0.7)  #move it up slowly
        fade_alpha -= 1.5   #fade it out slowly
        if fade_alpha <= 0: #if it's fully faded
            fading = False #stop fading
            fade_text_surface = None #clear the pre-rendered surface, don't need it now
            # Removed rain sound stop on fade out, as it wasn't in the original code


    #display any messages (like "music on/off").
    if message_alpha > 0: #if there's a message to show
        # Use small_font for messages
        msg_surf = small_font.render(message_text, True, white)
        msg_surf.set_alpha(message_alpha)
        msg_rect = msg_surf.get_rect(center=(screen_width // 2, screen_height - 50)) #position at bottom-center
        screen.blit(msg_surf, msg_rect)
        message_timer -= 1 #count down
        if message_timer <= 0: #timer's up
            message_alpha = 0 #make it disappear


    pygame.display.flip() #this updates the whole screen to show what i've drawn.
    clock.tick(60) #try to keep it at 60 fps.

pygame.quit() #clean up pygame when the loop ends.