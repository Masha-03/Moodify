import pygame
import sys
import os
import sqlite3

# Initialize Pygame and mixer module
pygame.init()
pygame.mixer.init()

# Get the current monitor size for fullscreen support
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
fullscreen = False

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
FONT = pygame.font.Font("texts/PressStart2P-Regular.ttf", 20)

# Load music
pygame.mixer.music.load("lofi_music.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Load settings icon
settings_icon = pygame.image.load("settings/settings_icon.png")
settings_icon = pygame.transform.scale(settings_icon, (80, 80))

# Load character animations (4 frames)
scale_size = 0.75

male_frames = [
    pygame.transform.scale_by(
        pygame.image.load(f"male/boy_pixil_frame_{i}.png"), scale_size
    )
    for i in range(4)]

female_frames = [
    pygame.transform.scale_by(
        pygame.image.load(f"female/girl_pixil_frame_{i}.png"), scale_size
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
profile_name = ""  # Renamed from nickname to profile_name
input_active = False
profile_name_confirmed = False # Added profile_name_confirmed.  Not used.

#--------------------------------------------------------------masha---------------------------------------------------------------------------------#

#Get profile from the database
def get_profile():
    global profile_name
    connect = sqlite3.connect('moodify_database.db')
    cursor = connect.cursor()

    #Fetch the profile
    cursor.execute("SELECT profile FROM user_info ORDER BY ROWID DESC LIMIT 1") #Fetch latest profile
    result = cursor.fetchone()

    connect.close() #Close connection
    if result:
        profile_name = result[0]  #Store the profile
    else:
        profile_name = "User"    #Changed default value

#Database connection
def connect_db():
    connect = sqlite3.connect("moodify_database.db")
    return connect

def get_user_data():
    #Fetch user profile data and return profile and gender
    connect = connect_db()
    cursor = connect.cursor()
    cursor.execute("SELECT profile, gender FROM user_info WHERE profile = ?", (profile_name,))
    user_data = cursor.fetchone()
    connect.close()

    #If data exists, return it, else use default values
    if user_data:
        return user_data[0], user_data[1]
    else:
        return "User", "Male"

def update_gender_in_db(new_gender, current_profile_name):
    #Update the gender in the database when changed in the settings
    connect = connect_db()
    cursor = connect.cursor()
    cursor.execute("UPDATE user_info SET gender = ? WHERE profile = ?", (new_gender, current_profile_name))
    connect.commit()
    connect.close()

def update_profile_name_in_db(new_profile_name, old_profile_name):
    """Updates the user's profile name in the database."""
    connect = connect_db()
    cursor = connect.cursor()
    try:
        # Check if a profile with the new name already exists
        cursor.execute("SELECT profile FROM user_info WHERE profile = ?", (new_profile_name,))
        existing_profile = cursor.fetchone()

        if existing_profile and new_profile_name != old_profile_name:
            print(f"Profile name '{new_profile_name}' already exists.")
            return False  # Indicate failure
        elif old_profile_name == "":
             cursor.execute("INSERT INTO user_info (profile, gender) VALUES (?, ?)", (new_profile_name, "Male"))
             conn.commit()
             return True
        else:
            # Update the profile name
            cursor.execute("UPDATE user_info SET profile = ? WHERE profile = ?", (new_profile_name, old_profile_name))
            connect.commit()
            return True #Indicate success
    except sqlite3.Error as e:
        print(f"Error updating profile name: {e}")
        connect.rollback()
        return False  # Indicate failure
    finally:
        connect.close()

#Fetch initial data
get_profile()  #Fetch the latest profile first
profile, gender = get_user_data()  #Get profile and gender data based on the profile
profile_name = profile #sync

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

def draw_icon_button(surface, icon, x, y):
    rect = pygame.Rect(x, y, icon.get_width(), icon.get_height())
    screen.blit(icon, (x, y))
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

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    screen.fill(BG_COLOR)
    animation_timer += 1
    if animation_timer >= animation_speed:
        animation_index = (animation_index + 1) % 4
        animation_timer = 0

    # Get dynamic positions based on current screen size
    screen_width, screen_height = screen.get_size()
    settings_button_rect = draw_icon_button(screen, settings_icon, screen_width - 100, 20)

    if settings_open:
        settings_width = int(screen_width * 0.8)
        settings_height = int(screen_height * 0.8)
        settings_x = int((screen_width - settings_width) / 2)
        settings_y = int((screen_height - settings_height) / 2)
        pygame.draw.rect(screen, SETTINGS_BG, (settings_x, settings_y, settings_width, settings_height), border_radius=16)
        draw_text(screen, "Settings", settings_x + 20, settings_y + 20, TEXT_COLOR)

        start_y = settings_y + 100 #move all content below this Y
        # Draw profile name input
        draw_text(screen, "Profile Name:", settings_x + 40, start_y + 320, TEXT_COLOR)
        profile_name_input_rect = draw_input_box(screen, profile_name, settings_x + 300, start_y + 300, 250, 50, input_active)

        draw_text(screen, f"Profile: {profile_name}", settings_x + 40, start_y + 400, TEXT_COLOR) #Masha added profile name
        draw_text(screen, "Music:", settings_x + 40, start_y + 60, TEXT_COLOR)
        music_toggle_rect = draw_rounded_button(screen, "Mute" if not music_muted else "Unmute", settings_x + 300, start_y + 50 , 160, 40, BUTTON_COLOR, BUTTON_HOVER_COLOR)

        draw_text(screen, "Volume:", settings_x + 40, start_y + 120, TEXT_COLOR)
        volume_slider_rect = draw_slider(screen, settings_x + 300, start_y + 120, 300, 20, current_volume)

        draw_text(screen, "Gender:", settings_x + 40, start_y + 180, TEXT_COLOR)
        gender_dropdown_rect = draw_dropdown(screen, settings_x + 300, start_y + 180, 200, 40, genders, selected_gender_index, gender_dropdown_active)

        draw_text(screen, "Character Preview:", settings_x + settings_width - 450, settings_y + 80, TEXT_COLOR)
        current_frame = male_frames[animation_index] if genders[selected_gender_index] == "Male" else female_frames[animation_index]
        screen.blit(current_frame, (settings_x + settings_width - 450, settings_y + 120))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            if not fullscreen:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_f:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((screen.get_width(), screen.get_height()), pygame.RESIZABLE)
            if input_active:
                if event.key == pygame.K_BACKSPACE:
                    profile_name = profile_name[:-1]
                elif event.key == pygame.K_RETURN:
                    input_active = False
                    profile_name_confirmed = True
                    if update_profile_name_in_db(profile_name, profile):
                         profile = profile_name #update
                elif len(profile_name) < 11:  # Limit profile name length to 10 characters
                    profile_name += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if settings_button_rect.collidepoint(mouse_pos):
                settings_open = not settings_open
            elif settings_open:
                if music_toggle_rect.collidepoint(mouse_pos):
                    music_muted = not music_muted
                    pygame.mixer.music.pause() if music_muted else pygame.mixer.music.unpause()
                if volume_slider_rect.collidepoint(mouse_pos):
                    rel_x = mouse_pos[0] - volume_slider_rect.x
                    current_volume = max(0, min(1, rel_x / volume_slider_rect.width))
                    pygame.mixer.music.set_volume(current_volume)
                if gender_dropdown_rect.collidepoint(mouse_pos):
                    gender_dropdown_active = not gender_dropdown_active
                elif gender_dropdown_active:
                    for i in range(len(genders)):
                        option_rect = pygame.Rect(gender_dropdown_rect.x, gender_dropdown_rect.y + gender_dropdown_rect.height * (i + 1), gender_dropdown_rect.width, gender_dropdown_rect.height)
                        if option_rect.collidepoint(mouse_pos):
                            selected_gender_index = i
                            gender_dropdown_active = False
                            update_gender_in_db(genders[selected_gender_index], profile)
                            break
                input_active = profile_name_input_rect.collidepoint(mouse_pos)
                if not input_active:
                    profile_name_confirmed = True
                    if update_profile_name_in_db(profile_name, profile):
                         profile = profile_name #update

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
