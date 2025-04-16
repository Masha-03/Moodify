import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Popper")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Colors
BG_COLOR = (180, 220, 255)
BUBBLE_COLOR = (255, 255, 255)
POP_COLOR = (200, 200, 255)

# Bubble settings
BUBBLE_RADIUS = 30
BUBBLE_SPEED = 1
BUBBLE_INTERVAL = 60  # frames between the spawns

# Sound (optional: replace 'popsound.wav' with poppping sound file)
try:
    pop_sound = pygame.mixer.Sound("popsound.wav")
except:
    pop_sound = None

# Background music (optional) for now
try:
    pygame.mixer.music.load("lofi.mp3")
    pygame.mixer.music.play(-1)
except:
    pass

# Bubble class
class Bubble:
    def __init__(self):
        self.x = random.randint(BUBBLE_RADIUS, WIDTH - BUBBLE_RADIUS)
        self.y = HEIGHT + BUBBLE_RADIUS
        self.radius = BUBBLE_RADIUS
        self.color = BUBBLE_COLOR
        self.popped = False
        self.alpha = 255  # fade out on pop

    def update(self):
        if not self.popped:
            self.y -= BUBBLE_SPEED
        else:
            self.alpha -= 10
            if self.alpha <= 0:
                return False
        return True

    def draw(self, surface):
        bubble_surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        draw_color = (*self.color, self.alpha)
        pygame.draw.circle(bubble_surface, draw_color, (self.radius, self.radius), self.radius)
        surface.blit(bubble_surface, (self.x - self.radius, self.y - self.radius))

    def check_click(self, pos):
        if not self.popped:
            dx, dy = self.x - pos[0], self.y - pos[1]
            distance = (dx**2 + dy**2)**0.5
            return distance <= self.radius
        return False

# Main loop
bubbles = []
frame_count = 0

running = True
while running:
    screen.fill(BG_COLOR)
    frame_count += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for bubble in bubbles:
                if bubble.check_click(event.pos):
                    bubble.popped = True
                    bubble.color = POP_COLOR
                    if pop_sound:
                        pop_sound.play()

    # Add bubbles
    if frame_count % BUBBLE_INTERVAL == 0:
        bubbles.append(Bubble())

    # Update and draw bubbles
    bubbles = [b for b in bubbles if b.update()]
    for bubble in bubbles:
        bubble.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()