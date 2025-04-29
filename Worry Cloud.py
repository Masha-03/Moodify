import pygame
import os

pygame.init()

# Screen setup
screen_width, screen_height = 1920, 1020
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Worry Cloud")

# Colors and font
white = (255, 255, 255)
black = (0, 0, 0)
light_gray = (200, 200, 200)
font = pygame.font.Font(None, 48)

# Load background
background = pygame.image.load('star_bg2.jpg')
background = pygame.transform.scale(background, (screen_width, screen_height))

# Try to load cloud image
use_image_cloud = os.path.exists("cloud.png")
if use_image_cloud:
    cloud_img = pygame.image.load("cloud.png").convert_alpha()
    cloud_img = pygame.transform.scale(cloud_img, (360, 200))

# Input box
input_box = pygame.Rect(250, 270, 300, 40)
text = ''
active = False

# Button
button_rect = pygame.Rect(325, 330, 150, 40)
button_text = font.render("Release", True, black)
button_color = light_gray

# Fade settings
fade_alpha = 255
fading = False
fade_text = ''
fade_pos = (0, 0)

clock = pygame.time.Clock()
running = True

while running:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = True
            else:
                active = False

            if button_rect.collidepoint(event.pos) and text.strip():
                fade_text = text
                fade_pos = (input_box.centerx - 90, input_box.top - 100)
                text = ''
                fade_alpha = 255
                fading = True

        elif event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_BACKSPACE:
                text = text[:-1]
            elif event.key == pygame.K_RETURN:
                pass  # you can use Enter to trigger something if needed
            else:
                text += event.unicode

    # Draw input box
    pygame.draw.rect(screen, light_gray, input_box, 2)
    txt_surface = font.render(text, True, black)
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

    # Draw button
    pygame.draw.rect(screen, button_color, button_rect)
    screen.blit(button_text, button_text.get_rect(center=button_rect.center))

    # Fade cloud with text
    if fading:
        if use_image_cloud:
            cloud = cloud_img.copy()
            cloud.set_alpha(fade_alpha)
            screen.blit(cloud, fade_pos)
        else:
            cloud_surface = pygame.Surface((180, 100), pygame.SRCALPHA)
            pygame.draw.ellipse(cloud_surface, (255, 255, 255, fade_alpha), cloud_surface.get_rect())
            screen.blit(cloud_surface, fade_pos)

        fade_surface = font.render(fade_text, True, black)
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, fade_surface.get_rect(center=(fade_pos[0] + 90, fade_pos[1] + 50)))

        fade_alpha -= 5
        if fade_alpha <= 0:
            fading = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
