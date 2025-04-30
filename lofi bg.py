import pygame
import sys

# Initialize Pygame
pygame.init()

# Window dimensions
screen_width = 1920
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Lofi Game with Settings")
font = pygame.font.Font(None, 36)  # Default font, can be changed
text_color = (255, 255, 255)  # White text
button_color = (50, 50, 50)  #dark grey button
button_hover_color = (70, 70, 70)  #slightly lighter on hover
slider_color = (100, 100, 100)  #grey slider
slider_handle_color = (150, 150, 150)  #lighter grey handle
dropdown_color = (50, 50, 50)
dropdown_active_color = (70, 70, 70)
dropdown_option_color = (60, 60, 60)
dropdown_option_hover_color = (80, 80, 80)

# Music settings
pygame.mixer.init()
music_file = "lofi_music.wav"  
pygame.mixer.music.load(music_file)
pygame.mixer.music.set_volume(0.5)  # Initial volume
pygame.mixer.music.play(-1)  # Loop indefinitely
music_muted = False
current_volume = 0.5

# Character appearance settings
genders = ["Male", "Female"]
selected_gender_index = 0
#  images would be loaded, not just names
character_images = {
    "Male": pygame.Surface((50, 50)),  # Placeholder, replace with actual image loading
    "Female": pygame.Surface((50, 50)), # Placeholder
}
selected_gender = genders[selected_gender_index]

# Settings window state
settings_open = False
# Function to draw text


def draw_text(surface, text, x, y, color):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

# Function to draw a button


def draw_button(surface, text, x, y, width, height, color, hover_color=None):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, color, rect)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)
    if hover_color:
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, hover_color, rect)
            surface.blit(text_surface, text_rect)  # Keep text on top
    return rect

# Function to draw a slider


def draw_slider(surface, x, y, width, height, slider_value, color, handle_color):
    # Background of the slider
    pygame.draw.rect(surface, color, (x, y, width, height))
    # Calculate position of the slider handle
    handle_pos = x + (slider_value * width) - (height / 2)
    # Draw the slider handle
    pygame.draw.rect(surface, handle_color, (handle_pos, y, height, height))
    return pygame.Rect(x, y, width, height)  # Return the rect of the whole slider

def draw_dropdown(surface, x, y, width, height, options, selected_index, color, active_color, option_color, option_hover_color, is_active):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, color, rect)
    text_surface = font.render(options[selected_index], True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

    if is_active:
        # Draw the dropdown options
        for i, option in enumerate(options):
            option_rect = pygame.Rect(x, y + height * (i + 1), width, height)
            pygame.draw.rect(surface, option_color, option_rect)
            option_text_surface = font.render(option, True, text_color)
            option_text_rect = option_text_surface.get_rect(center=option_rect.center)
            surface.blit(option_text_surface, option_text_rect)
            mouse_pos = pygame.mouse.get_pos()
            if option_rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, option_hover_color, option_rect)
                surface.blit(option_text_surface, option_text_rect)
    return rect

# Main loop
running = True
settings_button_rect = None  # Declare it here
volume_slider_rect = None
gender_dropdown_rect = None
gender_dropdown_active = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if settings_button_rect and settings_button_rect.collidepoint(mouse_pos):
                settings_open = not settings_open
            elif settings_open:
                if music_toggle_rect.collidepoint(mouse_pos):
                    music_muted = not music_muted
                    if music_muted:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                if volume_slider_rect and volume_slider_rect.collidepoint(mouse_pos):
                    # Convert mouse position to volume (0.0 to 1.0)
                    slider_x, slider_y = volume_slider_rect.topleft
                    slider_width, slider_height = volume_slider_rect.size
                    # Ensure the click is within the slider's bounds
                    if slider_x <= mouse_pos[0] <= slider_x + slider_width:
                        new_volume = (mouse_pos[0] - slider_x) / slider_width
                        new_volume = max(0, min(1, new_volume))  # Clamp to 0-1 range
                        current_volume = new_volume
                        pygame.mixer.music.set_volume(current_volume)
                if gender_dropdown_rect and gender_dropdown_rect.collidepoint(mouse_pos):
                    gender_dropdown_active = not gender_dropdown_active
                elif gender_dropdown_active:
                    # Check which gender option was clicked
                    for i, _ in enumerate(genders):
                        option_rect = pygame.Rect(gender_dropdown_rect.x, gender_dropdown_rect.y + gender_dropdown_rect.height * (i + 1), gender_dropdown_rect.width, gender_dropdown_rect.height)
                        if option_rect.collidepoint(mouse_pos):
                            selected_gender_index = i
                            selected_gender = genders[selected_gender_index]
                            gender_dropdown_active = False
                            break  # Exit the loop after handling the click

    # Fill the screen
    screen.fill((30, 30, 30))

    # Draw settings button
    settings_button_rect = draw_button(screen, "Settings", screen_width - 100, 20, 80, 30, button_color, button_hover_color)

    # Draw settings window if open
    if settings_open:
        # Background for the settings window
        pygame.draw.rect(screen, (0, 0, 0), (100, 100, screen_width - 200, screen_height - 200))
        draw_text(screen, "Settings", 350, 120, text_color)

        # Music toggle
        draw_text(screen, "Music:", 150, 170, text_color)
        music_toggle_rect = draw_button(screen, "Mute" if not music_muted else "Unmute", 250, 160, 100, 30, button_color, button_hover_color)

        # Volume slider
        draw_text(screen, "Volume:", 150, 220, text_color)
        volume_slider_rect = draw_slider(screen, 250, 210, 200, 10, current_volume, slider_color, slider_handle_color)

        # Gender selection
        draw_text(screen, "Gender:", 150, 270, text_color)
        gender_dropdown_rect = draw_dropdown(screen, 250, 260, 150, 30, genders, selected_gender_index, dropdown_color, dropdown_active_color, dropdown_option_color, dropdown_option_hover_color, gender_dropdown_active)
        draw_text(screen, f"Selected: {selected_gender}", 250, 300, text_color) # display selected gender

        # Character preview (placeholder)
        draw_text(screen, "Character Preview:", 150, 350, text_color)
        # Display the character image based on the selected gender
        screen.blit(character_images[selected_gender], (250, 350))  #  display image

    pygame.display.flip()

pygame.quit()
sys.exit()
