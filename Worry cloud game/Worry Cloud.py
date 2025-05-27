import pygame
import random
import sqlite3
from datetime import datetime

pygame.init()

# #------------------------------------------------------------------------------------------ database code #------------------------------------------------------------------------------

DB_NAME = "moodify_database.db"
RECENT_WORRIES_DISPLAY_COUNT = 3

def setup_database():
    """Connects to the SQLite database and creates the worries table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS worries (
                id INTEGER ,
                worry_text TEXT ,
                timestamp DATETIME 
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite database setup error: {e}")

def save_worry_to_db(worry_text):
    """Saves a worry text to the database."""
    if not worry_text.strip(): # Don't save empty worries
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO worries (worry_text) VALUES (?)", (worry_text,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite save error: {e}")

def get_latest_worries(count=RECENT_WORRIES_DISPLAY_COUNT):
    """Retrieves the latest 'count' worries from the database."""
    worries_list = []
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT worry_text, timestamp FROM worries ORDER BY timestamp DESC LIMIT ?", (count,))
        worries_list = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite fetch error: {e}")
    return worries_list

def get_all_worries():
    """Retrieves all worries from the database."""
    worries_list = []
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT worry_text, timestamp FROM worries ORDER BY timestamp DESC") # No LIMIT here
        worries_list = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite fetch all error: {e}")
    return worries_list

# #----------------------------------------------------------------------------- database code #------------------------------------------------------------------------------------------


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
    print(f"Could not load or play music file: {e}")


#now the rain sound.
#also check if this file exists.
rain_sound = None
rain_sound = pygame.mixer.Sound(RAIN_SOUND_PATH)
rain_sound.set_volume(0.6)
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

#try to load my preferred font, otherwise use a system default.
font = None # Main font for titles, buttons, released worry text
small_font = None # For messages
input_text_font = None # Font for text inside the input box
history_font = None # For the history display

font = pygame.font.Font(None, int(48 * min(scale_x, scale_y))) #main font, scaled
small_font = pygame.font.Font(None, int(36 * min(scale_x, scale_y))) #for smaller messages, scaled
input_text_font = pygame.font.Font(None, int(22 * min(scale_x, scale_y))) # Smaller font for input box text (adjust size as needed), scaled
history_font = pygame.font.Font(None, int(20 * min(scale_x, scale_y))) # Font for history entries



#load the background image.
background = pygame.image.load(BACKGROUND_IMG_PATH).convert()
background = pygame.transform.smoothscale(background, (screen_width, screen_height))

#load the image for my "worry" cloud.
use_image_cloud = False
cloud_img = None
worry_cloud_base_width, worry_cloud_base_height = 360, 200
scaled_worry_cloud_width = int(worry_cloud_base_width * scale_x)
scaled_worry_cloud_height = int(worry_cloud_base_height * scale_y)
original_cloud_img = pygame.image.load(CLOUD_IMG_PATH).convert_alpha()
cloud_img = pygame.transform.scale(original_cloud_img, (scaled_worry_cloud_width, scaled_worry_cloud_height))
use_image_cloud = True

# size for the drawn worry cloud fallback
drawn_worry_cloud_size = (scaled_worry_cloud_width, scaled_worry_cloud_height)


#this is for the input box for worries.
input_box_width = int(500 * scale_x)
input_box_height = int(200 * scale_y)
input_box = pygame.Rect(
    (screen_width - input_box_width) // 2,
    (screen_height - input_box_height) // 2,
    input_box_width,
    input_box_height)
text = ''
active = False

#prompt Variables
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
current_prompt = ""
prompt_display_timer = 0
PROMPT_CYCLE_INTERVAL = 300
show_prompts = True

#function to get a new random prompt
def get_new_prompt():
    global current_prompt
    new_prompt = random.choice(PROMPTS)
    if len(PROMPTS) > 1 and new_prompt == current_prompt:
        temp_prompts = [p for p in PROMPTS if p != current_prompt]
        if temp_prompts:
            new_prompt = random.choice(temp_prompts)
    current_prompt = new_prompt

# Initialize the first prompt
get_new_prompt()

#blinking cursor variables in the text box
cursor_blink_interval = 30
cursor_timer = 0
cursor_visible = True
MAX_INPUT_CHARS = 1000

#the "release" button
button_width = int(150 * scale_x)
button_height = int(50 * scale_y)
button_rect = pygame.Rect(
    (screen_width - button_width) // 2,
    input_box.bottom + int(30 * scale_y),
    button_width,
    button_height)

button_text_render = font.render("Release", True, black)
button_color = light_gray
button_hover_color = (170, 170, 170)

# view history button
view_history_button_width = int(200 * scale_x)
view_history_button_height = int(50 * scale_y)
view_history_button_rect = pygame.Rect(
    int(screen_width * 0.05), # 5% from left make it more to go to right
    screen_height - view_history_button_height - int(20 * scale_y), # 20px from bottom
    view_history_button_width,
    view_history_button_height
)
view_history_text_render = small_font.render("View History", True, black)

#back button for the history screen
back_button_width = int(150 * scale_x)
back_button_height = int(50 * scale_y)
back_button_rect = pygame.Rect(
    int(screen_width * 0.05), # 5% from left
    int(20 * scale_y), # 20px from top
    back_button_width,
    back_button_height
)
back_button_text_render = small_font.render("Back", True, black)


#settings for the fading "worry" cloud
fade_alpha = 255
fading = False
fade_pos = (0, 0)
fade_text_surface = None

#class for the little stars in the background.
class Star:
    def __init__(self):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.speed = random.uniform(0.1, 0.5) * scale_y
        self.size = random.randint(1, 2)
        self.color = (random.randint(200,255), random.randint(200,255), random.randint(200,255))

    def update(self):
        self.y += self.speed
        if self.y > screen_height:
            self.y = 0
            self.x = random.randint(0, screen_width)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

stars = [Star() for _ in range(150)]

#class for the bigger, drifting background clouds.
class BackgroundCloud:
    def __init__(self):
        self.image = None
        original_image = pygame.image.load(CLOUD2_IMG_PATH).convert_alpha()
        scale = random.uniform(0.5, 1.2)
        new_width = int(original_image.get_width() * scale * scale_x)
        new_height = int(original_image.get_height() * scale * scale_y)
        self.image = pygame.transform.scale(original_image, (new_width, new_height))
        self.width = new_width
        self.height = new_height

        self.x = random.randint(-self.width, screen_width)
        self.y = random.randint(int(50 * scale_y), screen_height // 3)
        self.speed = random.uniform(0.2, 0.7) * scale_x

    def update(self):
        self.x += self.speed
        if self.x > screen_width:
            self.x = -self.width
            self.y = random.randint(int(50 * scale_y), screen_height // 3)
            self.speed = random.uniform(0.2, 0.7) * scale_x


    def draw(self, surface_to_draw_on):
        if self.image:
            surface_to_draw_on.blit(self.image, (int(self.x), int(self.y)))
        elif hasattr(self, 'surface'):
            surface_to_draw_on.blit(self.surface, (int(self.x), int(self.y)))

background_clouds = [BackgroundCloud() for _ in range(7)]


#variables for history screen
GAME_STATE = "MAIN_GAME" # initial state
all_worries_history = [] # To store all worries when history is viewed
history_scroll_offset = 0 # for scrolling history list
HISTORY_LINE_HEIGHT = 0 # will be calculated ltr based on history_font size
HISTORY_DISPLAY_AREA = None # rect for history display area


def update_history_display_variables():
    global HISTORY_LINE_HEIGHT, HISTORY_DISPLAY_AREA, history_scroll_offset

    HISTORY_LINE_HEIGHT = history_font.get_height() + int(5 * scale_y) # Line spacing
    
    #define the area where history will be displayed
    history_area_x = int(screen_width * 0.15)
    history_area_y = int(screen_height * 0.15)
    history_area_width = int(screen_width * 0.7)
    history_area_height = int(screen_height * 0.7)
    HISTORY_DISPLAY_AREA = pygame.Rect(history_area_x, history_area_y, history_area_width, history_area_height)

    #reset scroll offset when view is updated
    history_scroll_offset = 0

#function to prepare and initiate the fading worry cloud
def release_worry(current_worry_text_param):
    global fade_text_surface, fade_pos, text, fade_alpha, fading, active, prompt_display_timer, latest_worries_for_display

    # --- database integration: save the worry to the database ---
    save_worry_to_db(current_worry_text_param)

    # Determine the dimensions of the worry cloud being displayed
    if use_image_cloud and cloud_img:
        worry_cloud_display_width = cloud_img.get_width()
        worry_cloud_display_height = cloud_img.get_height()
    else:
        worry_cloud_display_width = drawn_worry_cloud_size[0]
        worry_cloud_display_height = drawn_worry_cloud_size[1]

    #determine the maximum width for text on the worry cloud (e.g., 85% of cloud's width)
    max_text_width_on_cloud = worry_cloud_display_width * 0.85

    #render the text for the fading cloud using the main font (size 48)
    #taking only the first line and truncating for the cloud display
    display_text_on_cloud = current_worry_text_param.splitlines()[0].strip() if current_worry_text_param.strip() else ""
    if len(display_text_on_cloud) > 30:
            display_text_on_cloud = display_text_on_cloud[:30]

    temp_surface = font.render(display_text_on_cloud, True, black)
    if temp_surface.get_width() > max_text_width_on_cloud:
        #text is too long, so need to short it and add "..."
        while len(display_text_on_cloud) > 0 and font.render(display_text_on_cloud + "...", True, black).get_width() > max_text_width_on_cloud:
            display_text_on_cloud = display_text_on_cloud[:-1]

        #add .. if text was truncated AND there was original text
        if display_text_on_cloud != current_worry_text_param.splitlines()[0].strip():
            display_text_on_cloud += "..."

    fade_text_surface = font.render(display_text_on_cloud, True, black)

    #calculate position for the fading cloud - center above the input box
    fade_pos = (screen_width // 2 - worry_cloud_display_width // 2, input_box.top - worry_cloud_display_height - int(20 * scale_y))


    text = '' #clear the input box
    fade_alpha = 255 #reset alpha for the fade
    fading = True      #start the fading animation!!!
    if rain_sound: #if got rain soundd
    
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(rain_sound)
        else:
            print("No free mixer channels to play rain sound.")

    active = True #set input box to active so player can type next worry immediately
    global cursor_timer, cursor_visible #reset cursor for immediate visibility
    cursor_timer = 0
    cursor_visible = True
    prompt_display_timer = 0 # reset prompt timer when worry is released

# Function to toggle fullscreen
def toggle_fullscreen():
    global is_fullscreen, screen, background, screen_width, screen_height, font, small_font, input_text_font, history_font, input_box, button_rect, button_text_render, stars, background_clouds, scale_x, scale_y, current_prompt, prompt_display_timer, latest_worries_for_display, view_history_button_rect, view_history_text_render, back_button_rect, back_button_text_render, all_worries_history

    if not is_fullscreen:
        screen = pygame.display.set_mode((original_screen_width, original_screen_height), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((original_screen_width, original_screen_height), pygame.RESIZABLE)
            
    is_fullscreen = not is_fullscreen
 
    #after the changing display mode, get the new actual screen dimensions
    screen_width, screen_height = screen.get_size()

    #recalalculate scaling factors based on the new screen size
    scale_x = screen_width / original_screen_width
    scale_y = screen_height / original_screen_height
    background = pygame.transform.smoothscale(pygame.image.load(BACKGROUND_IMG_PATH).convert(), (screen_width, screen_height))
    
    #rescale fonts
    font = pygame.font.Font(None, int(48 * min(scale_x, scale_y)))
    small_font = pygame.font.Font(None, int(36 * min(scale_x, scale_y)))
    input_text_font = pygame.font.Font(None, int(22 * min(scale_x, scale_y)))
    history_font = pygame.font.Font(None, int(20 * min(scale_x, scale_y)))
    
    #resize input box and button
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

    # resize View History Button
    view_history_button_width = int(200 * scale_x)
    view_history_button_height = int(50 * scale_y)
    view_history_button_rect.update(
        int(screen_width * 0.05),
        screen_height - view_history_button_height - int(20 * scale_y),
        view_history_button_width,
        view_history_button_height
    )
    view_history_text_render = small_font.render("View History", True, black)

    # resize Back Button
    back_button_width = int(150 * scale_x)
    back_button_height = int(50 * scale_y)
    back_button_rect.update(
        int(screen_width * 0.05),
        int(20 * scale_y),
        back_button_width,
        back_button_height
    )
    back_button_text_render = small_font.render("Back", True, black)

    # reinitialize stars and background clouds for new scaled positions and speeds
    stars = [Star() for _ in range(150)]
    background_clouds = [BackgroundCloud() for _ in range(7)]
    
    # update current prompt text if it's visible, to ensure it's re-rendered with new font size
    if show_prompts and not active and not text.strip():
        get_new_prompt()
    prompt_display_timer = 0
    
    # --- Database Integration: Re-fetch worries on resize ---
    latest_worries_for_display = get_latest_worries()
    if GAME_STATE == "HISTORY_SCREEN":
        update_history_display_variables()
        all_worries_history = get_all_worries()


clock = pygame.time.Clock() #game clock
running = True #main loop flag
placeholder_text = "Type your worry here..." # placeholder text for the input box
placeholder_color = (150, 150, 150) # make the text gray color when input box is not active

# --- Database Integration: Initial database setup and load latest worries ---
setup_database()
latest_worries_for_display = get_latest_worries()
update_history_display_variables() # Initialize history display area variables


#main game loop
while running:
    #handle all events (mouse clicks, key presses)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #if i click the close button
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #left mouse button
                if GAME_STATE == "MAIN_GAME":
                    if input_box.collidepoint(event.pos): #did i click inside the input box?
                        active = True
                        cursor_timer = 0 #reset cursor blink on click
                        cursor_visible = True
                        # clear prompt when user starts typing
                        if show_prompts and current_prompt:
                            current_prompt = "" # Hide prompt
                    else:
                        active = False
                        # If clicking outside and input box is empty, show prompt
                        if not active and not text.strip() and show_prompts and not current_prompt:
                            get_new_prompt()
                            prompt_display_timer = 0

                    #did i click the "release" button and is there text to release?
                    if button_rect.collidepoint(event.pos) and text.strip():
                        release_worry(text) #call the function to handle releasing
                    
                    #handle view history button click
                    if view_history_button_rect.collidepoint(event.pos):
                        GAME_STATE = "HISTORY_SCREEN"
                        all_worries_history = get_all_worries() # fetch all worries
                        update_history_display_variables() # recalculate display variabless and reset scroll

                elif GAME_STATE == "HISTORY_SCREEN":
                    # Handle Back button click
                    if back_button_rect.collidepoint(event.pos):
                        GAME_STATE = "MAIN_GAME"
            
            # New: Handle mouse wheel for scrolling history
            elif event.button == 4 and GAME_STATE == "HISTORY_SCREEN": # Scroll up
                history_scroll_offset = max(0, history_scroll_offset - 1)
            elif event.button == 5 and GAME_STATE == "HISTORY_SCREEN": # Scroll down
                max_scroll_offset = max(0, len(all_worries_history) - int(HISTORY_DISPLAY_AREA.height / HISTORY_LINE_HEIGHT))
                history_scroll_offset = min(max_scroll_offset, history_scroll_offset + 1)


        elif event.type == pygame.KEYDOWN: #a key was pressed
            if GAME_STATE == "MAIN_GAME":
                if active: #only if the input box is active
                    # Clear prompt when user types
                    if show_prompts and current_prompt:
                        current_prompt = ""
                    
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
                        if not active and not text.strip(): # If enabling and box is empty
                            get_new_prompt()
                            prompt_display_timer = 0
                    else:
                        current_prompt = ""

            elif GAME_STATE == "HISTORY_SCREEN":
                # Allow 'Escape' or 'Backspace' to go back from history
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    GAME_STATE = "MAIN_GAME"
                # Scroll with Up/Down arrows
                elif event.key == pygame.K_UP:
                    history_scroll_offset = max(0, history_scroll_offset - 1)
                elif event.key == pygame.K_DOWN:
                    max_scroll_offset = max(0, len(all_worries_history) - int(HISTORY_DISPLAY_AREA.height / HISTORY_LINE_HEIGHT))
                    history_scroll_offset = min(max_scroll_offset, history_scroll_offset + 1)


        # handle window resize event
        elif event.type == pygame.VIDEORESIZE:
            if not is_fullscreen: # if not in fullscreen, assume manual resize
                screen_width, screen_height = event.w, event.h
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE) # Update screen object
                
                #recalculate scaling factors
                scale_x = screen_width / original_screen_width
                scale_y = screen_height / original_screen_height

                background = pygame.transform.smoothscale(pygame.image.load(BACKGROUND_IMG_PATH).convert(), (screen_width, screen_height))
                
                # Re-scale fonts
                try:
                    font = pygame.font.Font(None, int(48 * min(scale_x, scale_y)))
                    small_font = pygame.font.Font(None, int(36 * min(scale_x, scale_y)))
                    input_text_font = pygame.font.Font(None, int(22 * min(scale_x, scale_y)))
                    history_font = pygame.font.Font(None, int(20 * min(scale_x, scale_y)))
                except pygame.error as e:
                    print(f"problem loading default font during manual resize: {e}. using system font.")
                    font = pygame.font.SysFont(None, int(48 * min(scale_x, scale_y)))
                    small_font = pygame.font.SysFont(None, int(36 * min(scale_x, scale_y)))
                    input_text_font = pygame.font.SysFont(None, int(22 * min(scale_x, scale_y)))
                    history_font = pygame.font.SysFont(None, int(20 * min(scale_x, scale_y)))

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

                # Re-position/re-size View History Button
                view_history_button_width = int(200 * scale_x)
                view_history_button_height = int(50 * scale_y)
                view_history_button_rect.update(
                    int(screen_width * 0.05),
                    screen_height - view_history_button_height - int(20 * scale_y),
                    view_history_button_width,
                    view_history_button_height
                )
                view_history_text_render = small_font.render("View History", True, black)

                # Re-position/re-size Back Button
                back_button_width = int(150 * scale_x)
                back_button_height = int(50 * scale_y)
                back_button_rect.update(
                    int(screen_width * 0.05),
                    int(20 * scale_y),
                    back_button_width,
                    back_button_height
                )
                back_button_text_render = small_font.render("Back", True, black)


                # Re-initialize stars and background clouds for new scaled positions/speeds
                stars = [Star() for _ in range(150)]
                background_clouds = [BackgroundCloud() for _ in range(7)]
                
                # Update current prompt text if it's visible, to ensure it's re-rendered with new font size
                if show_prompts and not active and not text.strip():
                    get_new_prompt()
                prompt_display_timer = 0
                
                # --- Database Integration: Re-fetch worries on resize ---
                latest_worries_for_display = get_latest_worries()
                update_history_display_variables()
                if GAME_STATE == "HISTORY_SCREEN":
                    all_worries_history = get_all_worries()


    #update blinking cursor logic
    if GAME_STATE == "MAIN_GAME" and active:
        cursor_timer += 1
        if cursor_timer >= cursor_blink_interval:
            cursor_timer = 0
            cursor_visible = not cursor_visible
    else:
        cursor_visible = False #cursor shouldn't be visible if input is not active or not in main game

    # Prompt cycling logic
    if GAME_STATE == "MAIN_GAME" and show_prompts and not active and not text.strip():
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

    # --- Draw elements based on GAME_STATE ---
    if GAME_STATE == "MAIN_GAME":
        # Draw Prompt Text with a subtle shadow
        if show_prompts and not active and not text.strip() and current_prompt:
            prompt_center_x = screen_width // 2
            prompt_center_y = int(150 * scale_y)

            shadow_offset = int(2 * min(scale_x, scale_y))
            shadow_surf = small_font.render(current_prompt, True, black)
            shadow_rect = shadow_surf.get_rect(center=(prompt_center_x + shadow_offset, prompt_center_y + shadow_offset))
            screen.blit(shadow_surf, shadow_rect)

            prompt_surf = small_font.render(current_prompt, True, white)
            prompt_rect = prompt_surf.get_rect(center=(prompt_center_x, prompt_center_y))
            screen.blit(prompt_surf, prompt_rect)


        #draw the input box.
        pygame.draw.rect(screen, black, input_box, int(2 * min(scale_x, scale_y)), border_radius=int(5 * min(scale_x, scale_y)))
        pygame.draw.rect(screen, light_gray if active else white, input_box, 0, border_radius=int(5 * min(scale_x, scale_y)))


        # Render input text or placeholder
        text_to_render = text
        color_to_render = black
        if not active and not text:
            text_to_render = placeholder_text
            color_to_render = placeholder_color

        text_padding = int(10 * min(scale_x, scale_y))
        text_area_rect = pygame.Rect(
            input_box.x + text_padding,
            input_box.y + text_padding,
            input_box.width - 2 * text_padding,
            input_box.height - 2 * text_padding
        )

        current_y = text_area_rect.top
        lines = text_to_render.splitlines()
        if not lines and text_to_render:
            lines = [text_to_render]
        elif not lines:
            lines = ['']

        line_height = input_text_font.get_height()
        max_visible_lines = int(text_area_rect.height / line_height)

        start_line_index = max(0, len(lines) - max_visible_lines)
        
        for i in range(start_line_index, len(lines)):
            line_content = lines[i]
            line_surface = input_text_font.render(line_content, True, color_to_render)

            source_x = 0
            if line_surface.get_width() > text_area_rect.width:
                source_x = max(0, line_surface.get_width() - text_area_rect.width)
            
            screen.blit(line_surface, (text_area_rect.left, current_y), pygame.Rect(source_x, 0, text_area_rect.width, line_height))
            current_y += line_height


        #draw blinking cursor if input box is active
        if active and cursor_visible:
            last_line_content = lines[-1] if lines else ''
            last_line_surface = input_text_font.render(last_line_content, True, black)

            cursor_x_pos = text_area_rect.left + last_line_surface.get_width()
            
            if last_line_surface.get_width() > text_area_rect.width:
                cursor_x_pos = text_area_rect.left + text_area_rect.width

            cursor_y_start = text_area_rect.top + (min(len(lines), max_visible_lines) - 1) * line_height
            if not lines:
                cursor_y_start = text_area_rect.top
                
            cursor_y_end = cursor_y_start + line_height
            
            cursor_x_pos = max(text_area_rect.left, min(cursor_x_pos, text_area_rect.right))
            cursor_y_start = max(text_area_rect.top, min(cursor_y_start, text_area_rect.bottom - line_height))
            cursor_y_end = min(cursor_y_end, text_area_rect.bottom)

            if cursor_x_pos >= text_area_rect.left and cursor_x_pos <= text_area_rect.right and cursor_y_start < text_area_rect.bottom:
                pygame.draw.line(screen, black, (cursor_x_pos, cursor_y_start), (cursor_x_pos, cursor_y_end), int(2 * min(scale_x, scale_y)))


        #draw the "release" button.
        mouse_pos = pygame.mouse.get_pos()
        current_button_color = button_hover_color if button_rect.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(screen, current_button_color, button_rect, border_radius=int(10 * min(scale_x, scale_y)))
        screen.blit(button_text_render, button_text_render.get_rect(center=button_rect.center))

        # Draw View History button
        current_view_history_button_color = button_hover_color if view_history_button_rect.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(screen, current_view_history_button_color, view_history_button_rect, border_radius=int(10 * min(scale_x, scale_y)))
        screen.blit(view_history_text_render, view_history_text_render.get_rect(center=view_history_button_rect.center))


        # #---------------------------------------------------------------------------------------- database code #-------------------------------------------------------------------------------

    elif GAME_STATE == "HISTORY_SCREEN":
        #draw semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # black with 180 alpha (more transparent)
        screen.blit(overlay, (0, 0))

        #draw Back button
        mouse_pos = pygame.mouse.get_pos()
        current_back_button_color = button_hover_color if back_button_rect.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(screen, current_back_button_color, back_button_rect, border_radius=int(10 * min(scale_x, scale_y)))
        screen.blit(back_button_text_render, back_button_text_render.get_rect(center=back_button_rect.center))

        # Draw History Title
        history_title_surf = font.render("Worry History", True, white)
        history_title_rect = history_title_surf.get_rect(centerx=screen_width // 2, top=int(50 * scale_y))
        screen.blit(history_title_surf, history_title_rect)

        # Draw history display area border
        pygame.draw.rect(screen, white, HISTORY_DISPLAY_AREA, int(2 * min(scale_x, scale_y)), border_radius=int(10 * min(scale_x, scale_y)))
        # Draw background for history display area
        pygame.draw.rect(screen, (30, 30, 60), HISTORY_DISPLAY_AREA, 0, border_radius=int(10 * min(scale_x, scale_y)))

        # Display worries within the scrollable area
        display_y = HISTORY_DISPLAY_AREA.top + int(10 * scale_y) #padding from top of area
        
        #calculate start and end indices for visible worries
        start_index = history_scroll_offset
        max_visible_lines = int(HISTORY_DISPLAY_AREA.height / HISTORY_LINE_HEIGHT)
        end_index = min(len(all_worries_history), start_index + max_visible_lines)

        for i in range(start_index, end_index):
            worry_data = all_worries_history[i]
            worry_text_db, timestamp_db = worry_data

            try:
                dt_obj = datetime.strptime(timestamp_db, '%Y-%m-%d %H:%M:%S')
                formatted_timestamp = dt_obj.strftime('%Y-%m-%d %H:%M')
            except ValueError:
                formatted_timestamp = timestamp_db

            display_text = f"[{formatted_timestamp}] {worry_text_db}"
            
            # short text if it's too long to fit horizontally
            max_text_width = HISTORY_DISPLAY_AREA.width - int(20 * scale_x) # Area width minus padding
            
            # render the full text to check its width
            full_text_surf = history_font.render(display_text, True, white)
            
            # If wider, truncate and add ellipsis
            if full_text_surf.get_width() > max_text_width:
                temp_text = display_text
                while history_font.render(temp_text + "...", True, white).get_width() > max_text_width and len(temp_text) > 0:
                    temp_text = temp_text[:-1]
                display_text = temp_text + "..."
            
            #render the final shortened text for display
            history_entry_surf = history_font.render(display_text, True, white)
            
            #draw with shadow
            shadow_offset = int(1 * min(scale_x, scale_y))
            shadow_surf = history_font.render(display_text, True, black)
            screen.blit(shadow_surf, (HISTORY_DISPLAY_AREA.x + int(10 * scale_x) + shadow_offset, display_y + shadow_offset))

            screen.blit(history_entry_surf, (HISTORY_DISPLAY_AREA.x + int(10 * scale_x), display_y))
            display_y += HISTORY_LINE_HEIGHT


    #this is where the fading worry cloud.
    if fading:
        current_fade_alpha_val = max(0, int(fade_alpha))

        cloud_center_x, cloud_center_y = 0, 0
        cloud_to_draw = None

        if use_image_cloud and cloud_img:
            cloud_to_draw = cloud_img.copy()
            cloud_to_draw.set_alpha(current_fade_alpha_val)
            cloud_center_x = fade_pos[0] + cloud_img.get_width() // 2
            cloud_center_y = fade_pos[1] + cloud_img.get_height() // 2
        else:
            # For a drawn cloud, create a new surface with SRCPHAL to set alpha
            drawn_cloud_surface = pygame.Surface(drawn_worry_cloud_size, pygame.SRCALPHA)
            pygame.draw.ellipse(drawn_cloud_surface, (255, 255, 255, current_fade_alpha_val), drawn_cloud_surface.get_rect())
            cloud_to_draw = drawn_cloud_surface
            cloud_center_x = fade_pos[0] + drawn_worry_cloud_size[0] // 2
            cloud_center_y = fade_pos[1] + drawn_worry_cloud_size[1] // 2

        if cloud_to_draw:
              screen.blit(cloud_to_draw, fade_pos)


        if fade_text_surface:
            fade_text_surface.set_alpha(current_fade_alpha_val)
            text_rect = fade_text_surface.get_rect(center=(cloud_center_x, cloud_center_y))
            screen.blit(fade_text_surface, text_rect)

        fade_pos = (fade_pos[0], fade_pos[1] - (0.7 * scale_y))
        fade_alpha -= 1.5
        if fade_alpha <= 0:
            fading = False
            fade_text_surface = None


    pygame.display.flip()
    clock.tick(60)

pygame.quit()