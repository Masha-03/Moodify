import pygame
import random

pygame.init()

#paths for my files.
# Direct paths are used here. Using forward slashes '/' for better cross-platform compatibility
# with Pygame's loading functions, even on Windows
MUSIC_PATH = "Worry_cloud/calm_music.wav"
RAIN_SOUND_PATH = "Worry_cloud/rain_sound.wav"
BACKGROUND_IMG_PATH = "Worry_cloud/star_bg2.jpg"
CLOUD_IMG_PATH = "Worry_cloud/cloud.png" #for the worry cloud
CLOUD2_IMG_PATH = "Worry_cloud/cloud2.png" #for background clouds

#play the ambient music.
#first, check if the music file actually exists.
try:
    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.set_volume(0.5) #not too loud
    pygame.mixer.music.play(-1) #loop it forever
except pygame.error as e:
    print(f"self-note: Could not load or play music file: {e}")


#now the rain sound.
#also check if this file exists.
rain_sound = None # Initialize to None
try:
    rain_sound = pygame.mixer.Sound(RAIN_SOUND_PATH)
    rain_sound.set_volume(0.6)
except pygame.error as e:
    print(f"self-note: Could not load rain sound file: {e}")


music_on = True #keep track of whether music is playing

#setting up the screen.
original_screen_width, original_screen_height = 1920, 1020 #my preferred dimensions
screen_width, screen_height = original_screen_width, original_screen_height

screen = None
try:
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE) # Allow resizing for fullscreen toggle
except pygame.error as e:
    #if the big resolution fails, try a smaller one.
    print(f"oops, couldn't set display mode: {e}")
    print("trying 1280x720 instead...")
    screen_width, screen_height = 1280, 720
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE) # Allow resizing for fullscreen toggle

# Calculate scaling factors based on the actual screen size
scale_x = screen_width / original_screen_width
scale_y = screen_height / original_screen_height

# Store initial flags for toggling fullscreen
initial_screen_flags = screen.get_flags()
is_fullscreen = False

pygame.display.set_caption("Worry Cloud") # title

#define my colors and font.
white = (255, 255, 255)
black = (0, 0, 0)
light_gray = (200, 200, 200)
#using a slightly different cloud color for drawn background clouds if image fails
drawn_bg_cloud_color = (220, 220, 240, 150) # Added alpha

#try to load my preferred font, otherwise use a system default.
font = None # Main font for titles, buttons, released worry text
small_font = None # For messages
input_text_font = None # Font for text inside the input box

try:
    font = pygame.font.Font(None, int(48 * min(scale_x, scale_y))) #main font, scaled
    small_font = pygame.font.Font(None, int(36 * min(scale_x, scale_y))) #for smaller messages, scaled
    input_text_font = pygame.font.Font(None, int(22 * min(scale_x, scale_y))) # Smaller font for input box text (adjust size as needed), scaled

except pygame.error as e:
    print(f"problem loading default font: {e}. using system font for now.")
    font = pygame.font.SysFont(None, int(48 * min(scale_x, scale_y)))
    small_font = pygame.font.SysFont(None, int(36 * min(scale_x, scale_y)))
    input_text_font = pygame.font.SysFont(None, int(22 * min(scale_x, scale_y)))


#load the background image.
try:
    background = pygame.image.load(BACKGROUND_IMG_PATH).convert() # Added .convert() for smoothscale
    background = pygame.transform.smoothscale(background, (screen_width, screen_height)) # Changed to smoothscale
except pygame.error as e:
    print(f"couldn't load background image: {e}. i'll use a solid color for now.")
    background = pygame.Surface((screen_width, screen_height))
    background.fill((20, 20, 50)) #a dark blue as a fallback (keeping original fallback)

#load the image for my "worry" cloud.
# Use pygame.image.load to check existence as well, by catching the error if it fails
use_image_cloud = False
cloud_img = None # Initialize cloud_img
# Increased worry cloud size
worry_cloud_base_width, worry_cloud_base_height = 360, 200 # Increased base size for the cloud
scaled_worry_cloud_width = int(worry_cloud_base_width * scale_x)
scaled_worry_cloud_height = int(worry_cloud_base_height * scale_y)

try:
    original_cloud_img = pygame.image.load(CLOUD_IMG_PATH).convert_alpha() #use convert_alpha for transparency
    cloud_img = pygame.transform.scale(original_cloud_img, (scaled_worry_cloud_width, scaled_worry_cloud_height)) #resize it (keeping original size)
    use_image_cloud = True # Set to True if loading was successful
except pygame.error as e:
    print(f"couldn't load cloud image: {e}. i'll draw one instead.")
    use_image_cloud = False #fallback to drawing

if not use_image_cloud:
    print(f"self-note: cloud image {CLOUD_IMG_PATH} not found or failed to load. i'll draw the worry cloud.")


# Dimensions for the drawn worry cloud fallback (keeping original size)
drawn_worry_cloud_size = (scaled_worry_cloud_width, scaled_worry_cloud_height)


#this is for the input box where i'll type my worries.
input_box_width = int(500 * scale_x) # Increased width, scaled
input_box_height = int(200 * scale_y) # Increased height, scaled
input_box = pygame.Rect(
    (screen_width - input_box_width) // 2, #center it horizontally
    (screen_height - input_box_height) // 2, #center it vertically
    input_box_width,
    input_box_height)
text = '' #this will store the text i type
active = False #is the input box currently active?

# Guided Prompt Variables
PROMPTS = [
    "What's one thing you can let go of right now?",
    "What's on your mind today?",
    "What small worry feels big right now?",
    "What thought is holding you back?",
    "What's one thing you're ready to release?",
    "If you could whisper a worry to the clouds, what would it be?",
    "Is there something you've been carrying that you're ready to set down?",
    "What's a feeling you want to acknowledge and release?"
]
current_prompt = "" # The prompt currently being displayed
prompt_display_timer = 0 # How long the prompt has been displayed (to cycle them)
PROMPT_CYCLE_INTERVAL = 300 # How often to change prompts (frames, e.g., 5 seconds at 60fps)
show_prompts = True # Toggle for showing prompts (set to True initially)

# Function to get a new random prompt
def get_new_prompt():
    global current_prompt
    new_prompt = random.choice(PROMPTS)
    # Ensure the new prompt is different from the current one if possible
    if len(PROMPTS) > 1 and new_prompt == current_prompt:
        temp_prompts = [p for p in PROMPTS if p != current_prompt]
        if temp_prompts:
            new_prompt = random.choice(temp_prompts)
    current_prompt = new_prompt

# Initialize the first prompt
get_new_prompt()

#blinking cursor variables
cursor_blink_interval = 30 #frames (e.g., 30 frames = 0.5s at 60fps)
cursor_timer = 0
cursor_visible = True

# Increased the character limit to fit around 100 words
MAX_INPUT_CHARS = 1000 # Allowing up to approx 1000 characters


#the "release" button.
button_width = int(150 * scale_x)
button_height = int(50 * scale_y)
button_rect = pygame.Rect(
    (screen_width - button_width) // 2, #center it
    input_box.bottom + int(30 * scale_y), #position it below the input box
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
        self.speed = random.uniform(0.1, 0.5) * scale_y #nice and slow drift, scaled
        self.size = random.randint(1, 2) #keep them small
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
        # Attempt to load cloud2.png directly
        try:
            original_image = pygame.image.load(CLOUD2_IMG_PATH).convert_alpha()
            #randomly scale the image
            scale = random.uniform(0.5, 1.2) #scale between 50% and 120% of original size
            new_width = int(original_image.get_width() * scale * scale_x) # Apply overall scaling
            new_height = int(original_image.get_height() * scale * scale_y) # Apply overall scaling
            self.image = pygame.transform.scale(original_image, (new_width, new_height))
            self.width = new_width
            self.height = new_height
        except pygame.error as e:
            print(f"self-note: couldn't load {CLOUD2_IMG_PATH} for background cloud: {e}. drawing one instead.")
            #fallback to drawn ellipse if image loading fails
            self.width = int(random.randint(100, 300) * scale_x) # Scaled
            self.height = int(random.randint(50, 150) * scale_y) # Scaled
            self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA) #surface for transparency
            # Use the drawn_bg_cloud_color which has transparency
            pygame.draw.ellipse(self.surface, drawn_bg_cloud_color, (0, self.height * 0.2, self.width * 0.7, self.height * 0.7))
            pygame.draw.ellipse(self.surface, drawn_bg_cloud_color, (self.width * 0.3, 0, self.width * 0.7, self.height * 0.8))
            pygame.draw.ellipse(self.surface, drawn_bg_cloud_color, (self.width * 0.1, self.height*0.1, self.width * 0.8, self.height*0.9))


        self.x = random.randint(-self.width, screen_width) #some can start off-screen
        self.y = random.randint(int(50 * scale_y), screen_height // 3) #keep them in the upper part, scaled
        self.speed = random.uniform(0.2, 0.7) * scale_x #different speeds for variety, scaled


    def update(self):
        self.x += self.speed #move horizontally
        if self.x > screen_width:
            self.x = -self.width #if it goes off-screen right, reset to the left
            self.y = random.randint(int(50 * scale_y), screen_height // 3) #maybe a new y position too
            self.speed = random.uniform(0.2, 0.7) * scale_x # new random speed


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
    global fade_text_surface, fade_pos, text, fade_alpha, fading, active, prompt_display_timer

    # Determine the dimensions of the worry cloud being displayed (keeping original size)
    if use_image_cloud and cloud_img: #if i'm using the worry cloud image and it loaded
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
    fade_pos = (screen_width // 2 - worry_cloud_display_width // 2, input_box.top - worry_cloud_display_height - int(20 * scale_y)) # position it above the input box


    text = '' #clear the input box
    fade_alpha = 255 #reset alpha for the fade
    fading = True      #start the fading animation!
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
    prompt_display_timer = 0 # Reset prompt timer when worry is released

# Function to toggle fullscreen
def toggle_fullscreen():
    global is_fullscreen, screen, background, screen_width, screen_height, font, small_font, input_text_font, input_box, button_rect, button_text_render, stars, background_clouds, scale_x, scale_y, current_prompt, prompt_display_timer
    
    if not is_fullscreen:
        screen = pygame.display.set_mode((original_screen_width, original_screen_height), pygame.FULLSCREEN)
        display_message("Fullscreen ON")
    else:
        screen = pygame.display.set_mode((original_screen_width, original_screen_height), pygame.RESIZABLE)
        display_message("Fullscreen OFF")
        
    is_fullscreen = not is_fullscreen
    
    # After changing display mode, get the new actual screen dimensions
    screen_width, screen_height = screen.get_size()
    
    # Recalculate scaling factors based on the new screen size
    scale_x = screen_width / original_screen_width
    scale_y = screen_height / original_screen_height

    # Re-scale background
    background = pygame.transform.smoothscale(pygame.image.load(BACKGROUND_IMG_PATH).convert(), (screen_width, screen_height))
    
    # Re-scale fonts
    try:
        font = pygame.font.Font(None, int(48 * min(scale_x, scale_y)))
        small_font = pygame.font.Font(None, int(36 * min(scale_x, scale_y)))
        input_text_font = pygame.font.Font(None, int(22 * min(scale_x, scale_y)))
    except pygame.error as e:
        print(f"problem loading default font during resize: {e}. using system font.")
        font = pygame.font.SysFont(None, int(48 * min(scale_x, scale_y)))
        small_font = pygame.font.SysFont(None, int(36 * min(scale_x, scale_y)))
        input_text_font = pygame.font.SysFont(None, int(22 * min(scale_x, scale_y)))

    # Re-position/re-size input box and button
    input_box_width = int(500 * scale_x)
    input_box_height = int(200 * scale_y)
    input_box.update(
        (screen_width - input_box_width) // 2,
        (screen_height - input_box_height) // 2,
        input_box_width,
        input_box_height
    )

    button_width = int(150 * scale_x)
    button_height = int(50 * scale_y)
    button_rect.update(
        (screen_width - button_width) // 2,
        input_box.bottom + int(30 * scale_y),
        button_width,
        button_height
    )
    button_text_render = font.render("Release", True, black)

    # Re-initialize stars and background clouds for new scaled positions/speeds
    stars = [Star() for _ in range(150)]
    background_clouds = [BackgroundCloud() for _ in range(7)]
    
    # Update current prompt text if it's visible, to ensure it's re-rendered with new font size
    if show_prompts and not active and not text.strip():
        get_new_prompt() # Re-select a prompt if the screen resized while prompt was visible
    prompt_display_timer = 0 # Reset prompt timer on resize


clock = pygame.time.Clock() #my game clock
running = True #main loop flag
placeholder_text = "Type your worry here..." # Placeholder text for the input box
placeholder_color = (150, 150, 150) # Gray color for placeholder text

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
                    # Clear prompt when user starts typing
                    if show_prompts and current_prompt:
                        current_prompt = "" # Hide prompt
                else:
                    active = False
                    # If clicking outside and input box is empty, show prompt
                    if not active and not text.strip() and show_prompts and not current_prompt:
                        get_new_prompt()
                        prompt_display_timer = 0 # Reset timer for new prompt


                #did i click the "release" button and is there text to release?
                if button_rect.collidepoint(event.pos) and text.strip():
                    release_worry(text) #call the function to handle releasing

        elif event.type == pygame.KEYDOWN: #a key was pressed
            if active: #only if the input box is active
                # Clear prompt when user types
                if show_prompts and current_prompt:
                    current_prompt = "" # Hide prompt
                
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1] #delete last character
                    cursor_timer = 0 #reset cursor blink
                    cursor_visible = True
                elif event.key == pygame.K_RETURN: #if i press enter
                    # Check for Shift+Enter for new line, otherwise release
                    if event.mod & pygame.KMOD_SHIFT:
                        # Add a newline character if within limit
                        if len(text) < MAX_INPUT_CHARS:
                            text += '\n'
                        cursor_timer = 0
                        cursor_visible = True
                    elif text.strip(): # Only release if there's non-whitespace text
                        release_worry(text) #call the function to handle releasing
                        # After releasing, if prompts are enabled, immediately get a new one
                        if show_prompts:
                            get_new_prompt()
                            prompt_display_timer = 0

                else:
                    #add typed character to my text, but limit length
                    if len(text) < MAX_INPUT_CHARS: # Use the increased limit
                        text += event.unicode
                    cursor_timer = 0 #reset cursor blink
                    cursor_visible = True
            
            # Toggle fullscreen with 'f' key, but only if input box is not active
            if event.key == pygame.K_f and not active:
                toggle_fullscreen()
                
            # Toggle prompts with 'p' key
            elif event.key == pygame.K_p:
                show_prompts = not show_prompts
                if show_prompts:
                    display_message("Prompts ON")
                    if not active and not text.strip(): # If enabling and box is empty
                        get_new_prompt() # Show a prompt
                        prompt_display_timer = 0
                else:
                    display_message("Prompts OFF")
                    current_prompt = ""


        # Handle window resize event (e.g., when exiting fullscreen)
        elif event.type == pygame.VIDEORESIZE:
            if not is_fullscreen: # If not in fullscreen, assume manual resize
                screen_width, screen_height = event.w, event.h
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE) # Update screen object
                
                # Recalculate scaling factors
                scale_x = screen_width / original_screen_width
                scale_y = screen_height / original_screen_height

                background = pygame.transform.smoothscale(pygame.image.load(BACKGROUND_IMG_PATH).convert(), (screen_width, screen_height))
                
                # Re-scale fonts
                try:
                    font = pygame.font.Font(None, int(48 * min(scale_x, scale_y)))
                    small_font = pygame.font.Font(None, int(36 * min(scale_x, scale_y)))
                    input_text_font = pygame.font.Font(None, int(22 * min(scale_x, scale_y)))
                except pygame.error as e:
                    print(f"problem loading default font during manual resize: {e}. using system font.")
                    font = pygame.font.SysFont(None, int(48 * min(scale_x, scale_y)))
                    small_font = pygame.font.SysFont(None, int(36 * min(scale_x, scale_y)))
                    input_text_font = pygame.font.SysFont(None, int(22 * min(scale_x, scale_y)))

                # Re-position/re-size input box and button
                input_box_width = int(500 * scale_x)
                input_box_height = int(200 * scale_y)
                input_box.update(
                    (screen_width - input_box_width) // 2,
                    (screen_height - input_box_height) // 2,
                    input_box_width,
                    input_box_height
                )

                button_width = int(150 * scale_x)
                button_height = int(50 * scale_y)
                button_rect.update(
                    (screen_width - button_width) // 2,
                    input_box.bottom + int(30 * scale_y),
                    button_width,
                    button_height
                )
                button_text_render = font.render("Release", True, black)

                # Re-initialize stars and background clouds for new scaled positions/speeds
                stars = [Star() for _ in range(150)]
                background_clouds = [BackgroundCloud() for _ in range(7)]
                
                # Update current prompt text if it's visible, to ensure it's re-rendered with new font size
                if show_prompts and not active and not text.strip():
                    get_new_prompt()
                prompt_display_timer = 0


    #update blinking cursor logic
    if active:
        cursor_timer += 1
        if cursor_timer >= cursor_blink_interval:
            cursor_timer = 0
            cursor_visible = not cursor_visible
    else:
        cursor_visible = False #cursor shouldn't be visible if input is not active

    # Prompt cycling logic
    if show_prompts and not active and not text.strip(): # Only cycle if prompts are ON, input box is inactive, and empty
        prompt_display_timer += 1
        if prompt_display_timer >= PROMPT_CYCLE_INTERVAL:
            get_new_prompt()
            prompt_display_timer = 0


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

    # Draw Prompt Text with a subtle shadow
    if show_prompts and not active and not text.strip() and current_prompt:
        prompt_center_x = screen_width // 2
        prompt_center_y = int(300 * scale_y) # This is where you adjust the vertical position

        # Render shadow text first (dark color, slightly offset)
        shadow_offset = int(2 * min(scale_x, scale_y)) # Scaled shadow offset
        shadow_surf = small_font.render(current_prompt, True, black) # Black shadow
        shadow_rect = shadow_surf.get_rect(center=(prompt_center_x + shadow_offset, prompt_center_y + shadow_offset))
        screen.blit(shadow_surf, shadow_rect)

        # Render main text on top (white)
        prompt_surf = small_font.render(current_prompt, True, white)
        prompt_rect = prompt_surf.get_rect(center=(prompt_center_x, prompt_center_y))
        screen.blit(prompt_surf, prompt_rect)


    #draw the input box.
    # Draw box border first, then fill, or fill first then border, depending on desired look
    pygame.draw.rect(screen, black, input_box, int(2 * min(scale_x, scale_y)), border_radius=int(5 * min(scale_x, scale_y))) #the border
    pygame.draw.rect(screen, light_gray if active else white, input_box, 0, border_radius=int(5 * min(scale_x, scale_y))) # Fill


    # Render input text or placeholder
    text_to_render = text
    color_to_render = black
    if not active and not text:
        text_to_render = placeholder_text
        color_to_render = placeholder_color

    # Render input text using the smaller input_text_font.
    text_padding = int(10 * min(scale_x, scale_y))
    text_area_rect = pygame.Rect(
        input_box.x + text_padding,
        input_box.y + text_padding,
        input_box.width - 2 * text_padding,
        input_box.height - 2 * text_padding
    )

    # Multi-line text rendering
    current_y = text_area_rect.top
    lines = text_to_render.splitlines()
    if not lines and text_to_render: # Handle cases where text might end with a newline leading to an empty last line
        lines = [text_to_render]
    elif not lines: # If text is completely empty
        lines = ['']

    # Filter lines to only show those that fit
    line_height = input_text_font.get_height()
    max_visible_lines = int(text_area_rect.height / line_height)

    # Determine which lines to draw from the end if text is too long
    start_line_index = max(0, len(lines) - max_visible_lines)
    
    for i in range(start_line_index, len(lines)):
        line_content = lines[i]
        line_surface = input_text_font.render(line_content, True, color_to_render)

        # Handle horizontal scrolling for each line if it's too wide
        source_x = 0
        if line_surface.get_width() > text_area_rect.width:
            source_x = max(0, line_surface.get_width() - text_area_rect.width)
        
        screen.blit(line_surface, (text_area_rect.left, current_y), pygame.Rect(source_x, 0, text_area_rect.width, line_height))
        current_y += line_height


    #draw blinking cursor if input box is active
    if active and cursor_visible:
        # Calculate cursor position for multi-line input
        # Position at the end of the last line
        last_line_content = lines[-1] if lines else ''
        last_line_surface = input_text_font.render(last_line_content, True, black)

        cursor_x_pos = text_area_rect.left + last_line_surface.get_width()
        
        # If the last line is horizontally scrolled, adjust cursor X
        if last_line_surface.get_width() > text_area_rect.width:
            cursor_x_pos = text_area_rect.left + text_area_rect.width

        cursor_y_start = text_area_rect.top + (min(len(lines), max_visible_lines) - 1) * line_height
        if not lines: # If no lines, cursor is at the very top of the text area
            cursor_y_start = text_area_rect.top
            
        cursor_y_end = cursor_y_start + line_height
        
        # Ensure cursor stays within the bounds of the input box's text area
        cursor_x_pos = max(text_area_rect.left, min(cursor_x_pos, text_area_rect.right))
        cursor_y_start = max(text_area_rect.top, min(cursor_y_start, text_area_rect.bottom - line_height))
        cursor_y_end = min(cursor_y_end, text_area_rect.bottom)

        if cursor_x_pos >= text_area_rect.left and cursor_x_pos <= text_area_rect.right and cursor_y_start < text_area_rect.bottom:
            pygame.draw.line(screen, black, (cursor_x_pos, cursor_y_start), (cursor_x_pos, cursor_y_end), int(2 * min(scale_x, scale_y)))


    #draw the "release" button.
    mouse_pos = pygame.mouse.get_pos() #where is the mouse?
    current_button_color = button_hover_color if button_rect.collidepoint(mouse_pos) else button_color
    pygame.draw.rect(screen, current_button_color, button_rect, border_radius=int(10 * min(scale_x, scale_y))) #rounded corners look nice

    # The button text remains black on a light background, so no shadow needed here.
    screen.blit(button_text_render, button_text_render.get_rect(center=button_rect.center))


    #this is where i handle the fading "worry" cloud.
    if fading:
        current_fade_alpha_val = max(0, int(fade_alpha)) #alpha can't be negative.

        cloud_center_x, cloud_center_y = 0, 0
        cloud_to_draw = None # Surface to blit for the cloud graphic

        if use_image_cloud and cloud_img: #if i'm using the worry cloud image and it loaded
            cloud_to_draw = cloud_img.copy() #copy so original isn't changed
            cloud_to_draw.set_alpha(current_fade_alpha_val)
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
        fade_pos = (fade_pos[0], fade_pos[1] - (0.7 * scale_y)) #move it up slowly, scaled
        fade_alpha -= 1.5   #fade it out slowly
        if fade_alpha <= 0: #if it's fully faded
            fading = False #stop fading
            fade_text_surface = None #clear the pre-rendered surface, don't need it now


    #display any messages (like "music on/off").
    if message_alpha > 0: #if there's a message to show
        # Use small_font for messages
        msg_surf = small_font.render(message_text, True, white)
        msg_surf.set_alpha(message_alpha)
        msg_rect = msg_surf.get_rect(center=(screen_width // 2, screen_height - int(50 * scale_y))) #position at bottom-center
        screen.blit(msg_surf, msg_rect)
        message_timer -= 1 #count down
        if message_timer <= 0: #timer's up
            message_alpha = 0


    pygame.display.flip() #this updates the whole screen to show what i've drawn.
    clock.tick(60) #try to keep it at 60 fps.

pygame.quit() #clean up pygame when the loop ends.