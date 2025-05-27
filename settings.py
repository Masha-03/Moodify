import pygame
import sys
import os
import sqlite3

# Constants for screen dimension and colors
BG_COLOR = (245, 235, 220)
SETTINGS_BG = (210, 180, 140)
TEXT_COLOR = (60, 40, 20)
BUTTON_COLOR = (205, 170, 125)
BUTTON_HOVER_COLOR = (180, 140, 100)
SLIDER_COLOR = (230, 200, 170)
SLIDER_HANDLE_COLOR = (190, 140, 90)
DROPDOWN_COLOR = (230, 210, 190)
DROPDOWN_ACTIVE_COLOR = (210, 190, 170)
DROPDOWN_OPTION_COLOR = (220, 200, 180)
DROPDOWN_OPTION_HOVER_COLOR = (200, 180, 160)
INPUT_BG_COLOR = (255, 255, 255)
INPUT_BORDER_COLOR = (180, 140, 100)
FONT = None #dont initialize here first initialize in my main code

# Load character animations (4 frames)
scale_size = 0.75

#i flipped the facing direction to make it consistent
male_frames_F_right= []
male_img = [
    pygame.image.load("male/boy_pixil_frame_0.png"),
    pygame.image.load("male/boy_pixil_frame_1.png"),
    pygame.image.load("male/boy_pixil_frame_2.png"),
    pygame.image.load("male/boy_pixil_frame_3.png")
]
male_flipped_img = []
for i in male_img :
    flipped_img = pygame.transform.flip(i,True,False)
    male_flipped_img.append(flipped_img)

male_frames = [
    pygame.transform.scale_by(
        male_flipped_img[i], scale_size
    )
    for i in range(4)
]

female_frames = [
    pygame.transform.scale_by(
        pygame.image.load(f"F-right/pixil-frame-{i}.png"), scale_size
    )
    for i in range(4)]

# Animation variables
animation_index = 0
animation_timer = 0
animation_speed = 10

# State variables
music_muted = False
current_volume = 0.5
genders = ["Male", "Female"]
selected_gender_index = 0
gender_dropdown_active = False
settings_open = False
nickname = ""
input_active = False
nickname_confirmed = False

#--------------------------------------------------------------masha---------------------------------------------------------------------------------# 

#Get profile from the database
def get_profile():
    global profile
    connect = sqlite3.connect('moodify_database.db')
    cursor = connect.cursor()
    
    #Fetch the profile
    cursor.execute("SELECT profile FROM user_info ORDER BY ROWID DESC LIMIT 1") #Fetch latest profile
    result = cursor.fetchone()
    
    connect.close() #Close connection
    if result:
        profile = result[0]  #Store the profile 
    else:
        profile = None  #Set profile to None if no profile found
        
#Database connection 
def connect_db():
    connect = sqlite3.connect("moodify_database.db")
    return connect

def get_user_data():
    #Fetch user profile data and return profile and gender
    connect = connect_db()
    cursor = connect.cursor()
    cursor.execute("SELECT profile, gender FROM user_info WHERE profile = ?", (profile,))
    user_data = cursor.fetchone()
    connect.close()

    #If data exists, return it, else use default values
    if user_data:
        return user_data[0], user_data[1]
    else:
        return "User", "Male"

#debugggg
def update_gender_in_db(new_gender):
    #Update the gender in the database when changed in the settings
    global profile 
    connect = connect_db()
    cursor = connect.cursor()
    cursor.execute("UPDATE user_info SET gender = ? WHERE profile = ?", (new_gender, profile))
    connect.commit()
    connect.close()
    
#Fetch initial data
get_profile()  #Fetch the latest profile first
profile, gender = get_user_data()  #Get profile and gender data based on the profile

#Set the selected gender index based on the current gender
selected_gender_index = genders.index(gender) if gender in genders else 0

print(f"Current Profile: {profile}")
print(f"Current Gender: {gender}")

#--------------------------------------------------------------masha---------------------------------------------------------------------------------#
# Utility functions
def draw_text(surface, text, x, y, color):
    text_surface = FONT.render(text, True, color)
    surface.blit(text_surface, (x, y))

def draw_rounded_button(surface, text, x, y, width, height, color, hover_color=None):
    rect = pygame.Rect(x, y, width, height)
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    pygame.draw.rect(surface, hover_color if is_hovered else color, rect, border_radius=12)
    text_surface = FONT.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)
    return rect


def draw_slider(surface, x, y, width, height, value):
    pygame.draw.rect(surface, SLIDER_COLOR, (x, y, width, height), border_radius=6)
    handle_x = x + (value * width) - (height / 2)
    pygame.draw.rect(surface, SLIDER_HANDLE_COLOR, (handle_x, y, height, height), border_radius=6)
    return pygame.Rect(x, y, width, height)

def draw_dropdown(surface, x, y, width, height, options, selected_index, is_active):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, DROPDOWN_COLOR, rect, border_radius=6)
    text_surface = FONT.render(options[selected_index], True, TEXT_COLOR)
    surface.blit(text_surface, text_surface.get_rect(center=rect.center))

    if is_active:
        for i, option in enumerate(options):
            option_rect = pygame.Rect(x, y + height * (i + 1), width, height)
            pygame.draw.rect(surface, DROPDOWN_OPTION_COLOR, option_rect, border_radius=6)
            option_text = FONT.render(option, True, TEXT_COLOR)
            surface.blit(option_text, option_text.get_rect(center=option_rect.center))
            if option_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(surface, DROPDOWN_OPTION_HOVER_COLOR, option_rect, border_radius=6)
                surface.blit(option_text, option_text.get_rect(center=option_rect.center))
    return rect

def draw_input_box(surface, text, x, y, width, height, active):
    color = INPUT_BORDER_COLOR if active else BUTTON_COLOR
    pygame.draw.rect(surface, color, (x, y, width, height), border_radius=8)
    pygame.draw.rect(surface, INPUT_BG_COLOR, (x + 2, y + 2, width - 4, height - 4), border_radius=8)
    text_surface = FONT.render(text + ("|" if active else ""), True, TEXT_COLOR)
    surface.blit(text_surface, (x + 10, y + 10))
    return pygame.Rect(x, y, width, height)


#from the main loop i bring to here 
def draw(screen, screen_width, screen_height, animation_index, profile):
        settings_width = int(screen_width * 0.8) #######################################################################################################
        settings_height = int(screen_height * 0.8)
        settings_x = int((screen_width - settings_width) / 2)
        settings_y = int((screen_height - settings_height) / 2)
        pygame.draw.rect(screen, SETTINGS_BG, (settings_x, settings_y, settings_width, settings_height), border_radius=16)
        draw_text(screen, "Settings", settings_x + 20, settings_y + 20, TEXT_COLOR)
        
        start_y = settings_y + 100 #move all content below this Y
        draw_text(screen, f"Profile: {profile}", settings_x + 40, start_y + 400, TEXT_COLOR) #Masha added profile name
        draw_text(screen, "Music:", settings_x + 40, start_y + 60, TEXT_COLOR)
        music_toggle_rect = draw_rounded_button(screen, "Mute" if not music_muted else "Unmute", settings_x + 300, start_y + 50 , 160, 40, BUTTON_COLOR, BUTTON_HOVER_COLOR) ##################################################

        draw_text(screen, "Volume:", settings_x + 40, start_y + 120, TEXT_COLOR)
        volume_slider_rect = draw_slider(screen, settings_x + 300, start_y + 120, 300, 20, current_volume) #################################################################################

        draw_text(screen, "Gender:", settings_x + 40, start_y + 180, TEXT_COLOR)
        gender_dropdown_rect = draw_dropdown(screen, settings_x + 300, start_y + 180, 200, 40, genders, selected_gender_index, gender_dropdown_active)
        
        draw_text(screen, "Character Preview:", settings_x + settings_width - 450, settings_y + 80, TEXT_COLOR)
        current_frame = male_frames[animation_index] if genders[selected_gender_index] == "Male" else female_frames[animation_index]
        screen.blit(current_frame, (settings_x + settings_width - 450, settings_y + 120))

        # Draw nickname input
        draw_text(screen, "Nickname:", settings_x + 40, start_y + 320, TEXT_COLOR) ####################################################################
        nickname_input_rect = draw_input_box(screen, nickname, settings_x + 300, start_y + 300, 250, 50, input_active)
        
        # Draw nickname preview only if confirmed
        if nickname_confirmed:
            draw_text(screen, nickname, settings_x + settings_width - 400
            , settings_y + 500, TEXT_COLOR)

        #here i added a bit become a string so it can pass to the handle_event function (if not will be undefine)
        return {
        "music_toggle_rect": music_toggle_rect,
        "volume_slider_rect": volume_slider_rect,
        "gender_dropdown_rect": gender_dropdown_rect,
        "nickname_input_rect": nickname_input_rect
        }

def handle_event(event, rects):
    global music_muted, input_active, nickname, nickname_confirmed, selected_gender_index, gender_dropdown_active, current_volume

    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()
        if settings_open: #all i change to string if not will be undefine the word "rects" is from my main game code
            if rects.get("music_toggle_rect") and rects["music_toggle_rect"].collidepoint(mouse_pos):
                music_muted = not music_muted
                pygame.mixer.music.pause() if music_muted else pygame.mixer.music.unpause()
                        #it will check from rects(dictionary) see it exits or not, then check the collidepoint
            if rects.get("volume_slider_rect") and rects["volume_slider_rect"].collidepoint(mouse_pos):
                rel_x = mouse_pos[0] - rects["volume_slider_rect"].x
                current_volume = max(0, min(1, rel_x / rects["volume_slider_rect"].width))
                pygame.mixer.music.set_volume(current_volume)

            if rects.get("gender_dropdown_rect") and rects["gender_dropdown_rect"].collidepoint(mouse_pos):
                gender_dropdown_active = not gender_dropdown_active
            elif gender_dropdown_active:
                for i in range(len(genders)):
                    option_rect = pygame.Rect(
                        rects["gender_dropdown_rect"].x,
                        rects["gender_dropdown_rect"].y + rects["gender_dropdown_rect"].height * (i + 1),
                        rects["gender_dropdown_rect"].width,
                        rects["gender_dropdown_rect"].height,
                    )
                    if option_rect.collidepoint(mouse_pos):
                        selected_gender_index = i
                        gender_dropdown_active = False
                        # Update gender in DB here if needed
                        break

            if rects.get("nickname_input_rect"):
                input_active = rects["nickname_input_rect"].collidepoint(mouse_pos)
                if not input_active:
                    nickname_confirmed = True

    if event.type == pygame.KEYDOWN:
        if input_active:
            if event.key == pygame.K_BACKSPACE:
                nickname = nickname[:-1]
            elif event.key == pygame.K_RETURN:
                input_active = False
                nickname_confirmed = True
            elif len(nickname) < 11:  # Limit nickname length to 10 characters
                nickname += event.unicode


def update_animation():
    global animation_index, animation_timer

    animation_timer += 1
    if animation_timer >= animation_speed:
        animation_index = (animation_index + 1) % 4
        animation_timer = 0

