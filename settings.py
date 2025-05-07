import pygame
import sys
import os

# Initialize Pygame and mixer module
pygame.init() #initialize all pygame module
pygame.mixer.init() #for playback of sound

# Constants for screen dimension and colors
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1020
BG_COLOR = (245, 235, 220)  # Soft beige bg color
SETTINGS_BG = (210, 180, 140)  # Soft brown bg for settings
TEXT_COLOR = (60, 40, 20)  # Dark brown text color
BUTTON_COLOR = (205, 170, 125) 
BUTTON_HOVER_COLOR = (180, 140, 100)
SLIDER_COLOR = (230, 200, 170) #color of the volume slider
SLIDER_HANDLE_COLOR = (190, 140, 90) #color of the slider handle
DROPDOWN_COLOR = (230, 210, 190) #dropdown button bg
DROPDOWN_ACTIVE_COLOR = (210, 190, 170) #bg when dropdown is clicked
DROPDOWN_OPTION_COLOR = (220, 200, 180) #dropdown option button bg
DROPDOWN_OPTION_HOVER_COLOR = (200, 180, 160) #hover effects for options
FONT = pygame.font.Font("texts/PressStart2P-Regular.ttf", 20) #font style and size

#window screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Settings") #create game window

#looad music
pygame.mixer.music.load("lofi_music.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

#load settings icon
settings_icon = pygame.image.load("settings/settings_icon.png")  #should be a small 40x40 icon
settings_icon = pygame.transform.scale(settings_icon, (80, 80)) #resize icon

#load character animations got (4 frames)
male_frames = [pygame.image.load(f"male/boy_pixil_frame_{i}.png") for i in range(0, 4)]
female_frames = [pygame.image.load(f"female/girl_pixil_frame_{i}.png") for i in range(0, 4)]
animation_index = 0
animation_timer = 0
animation_speed = 10

#put the variables
music_muted = False
current_volume = 0.5
genders = ["Male", "Female"]
selected_gender_index = 0
gender_dropdown_active = False
settings_open = False

#utility functions
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

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    screen.fill(BG_COLOR)
    animation_timer += 1
    if animation_timer >= animation_speed:
        animation_index = (animation_index + 1) % 4
        animation_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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
                            break

    settings_button_rect = draw_icon_button(screen, settings_icon, SCREEN_WIDTH - 90, 20) #SCREEN_WIDTH - X, Y

    if settings_open:
        pygame.draw.rect(screen, SETTINGS_BG, (100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200), border_radius=16)
        draw_text(screen, "Settings", 120, 110, TEXT_COLOR)

        start_y = 180  # move all content below this Y

        draw_text(screen, "Music:", 140, start_y, TEXT_COLOR)
        music_toggle_rect = draw_rounded_button(screen, "Mute" if not music_muted else "Unmute", 300, start_y - 10, 160, 40, BUTTON_COLOR, BUTTON_HOVER_COLOR)

        draw_text(screen, "Volume:", 140, start_y + 60, TEXT_COLOR)
        volume_slider_rect = draw_slider(screen, 300, start_y + 60, 300, 10, current_volume)

        draw_text(screen, "Gender:", 140, start_y + 120, TEXT_COLOR)
        gender_dropdown_rect = draw_dropdown(screen, 300, start_y + 110, 200, 40, genders, selected_gender_index, gender_dropdown_active)
        dropdown_total_height = 40 * (len(genders) + 1) if gender_dropdown_active else 40
        draw_text(screen, f"Selected: {genders[selected_gender_index]}", 300, start_y + 110 + dropdown_total_height + 10, TEXT_COLOR)

        #compute vertical center of the settings tab
        tab_top = 100
        tab_height = SCREEN_HEIGHT - 200
        tab_center_y = tab_top + tab_height // 2

        #character preview X to the right of the dropdown
        preview_x = 300 + 300 + 200 #dropdown_x + dropdown_width + spacing
        preview_y = tab_center_y - 300  # assuming frame height is 600, the less is going down

        draw_text(screen, "Character Preview:", preview_x, preview_y - 40, TEXT_COLOR)
        current_frame = male_frames[animation_index] if genders[selected_gender_index] == "Male" else female_frames[animation_index]
        screen.blit(current_frame, (preview_x, preview_y))
        

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
