import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display (if needed)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Lofi Music App")

# Load and play background music
def play_background_music():
    pygame.mixer.init()
    pygame.mixer.music.load("lofi_music.wav")  # Make sure the file exists in your dir
    pygame.mixer.music.set_volume(0.5)         # Optional: Set volume (0.0 to 1.0)
    pygame.mixer.music.play(-1)                # -1 means loop indefinitely

play_background_music()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill screen (optional)
    screen.fill((30, 30, 30))
    pygame.display.flip()

pygame.quit()
sys.exit()
