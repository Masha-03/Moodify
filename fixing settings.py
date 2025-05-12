import pygame
import sys
import os

# Initialize Pygame and mixer module
pygame.init()
pygame.mixer.init()

# Get the current monitor size for fullscreen support
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
screen = pygame.display.set_mode((1600, 900), pygame.RESIZABLE)
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
FONT = pygame.font.Font("texts/PressStart2P-Regular.ttf", 20)

# Load music
pygame.mixer.music.load("lofi_music.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Load settings icon
settings_icon = pygame.image.load("settings/settings_icon.png")
settings_icon = pygame.transform.scale(settings_icon, (80, 80))

# Load character animations (4 frames)
male_frames = [pygame.image.load(f"male/boy_pixil_frame_{i}.png") for i in range(0, 4)]
female_frames = [pygame.image.load(f"female/girl_pixil_frame_{i}.png") for i in range(0, 4)]
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
        draw_text(screen, "Music:", settings_x + 40, start_y + 60, TEXT_COLOR)
        music_toggle_rect = draw_rounded_button(screen, "Mute" if not music_muted else "Unmute", settings_x + 300, start_y + 50 , 160, 40, BUTTON_COLOR, BUTTON_HOVER_COLOR)

        draw_text(screen, "Volume:", settings_x + 40, start_y + 120, TEXT_COLOR)
        volume_slider_rect = draw_slider(screen, settings_x + 300, start_y + 120, 300, 20, current_volume)

        draw_text(screen, "Gender:", settings_x + 40, start_y + 180, TEXT_COLOR)
        gender_dropdown_rect = draw_dropdown(screen, settings_x + 300, start_y + 180, 200, 40, genders, selected_gender_index, gender_dropdown_active)
        
        draw_text(screen, "Character Preview:", settings_x + settings_width - 550, settings_y + 80, TEXT_COLOR)
        current_frame = male_frames[animation_index] if genders[selected_gender_index] == "Male" else female_frames[animation_index]
        screen.blit(current_frame, (settings_x + settings_width - 550, settings_y + 120))

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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
