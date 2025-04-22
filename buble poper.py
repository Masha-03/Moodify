import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1920, 1020
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
BUBBLE_MIN_RADIUS = 50
BUBBLE_MAX_RADIUS = 90
BUBBLE_SPEED = 2 
BUBBLE_INTERVAL = 60  # frames between spawns

#sound list
pop_sounds = []
for i in range (1,4):
    try:
        sound = pygame.mixer.Sound(f"pop{i}.wav")
        sound.set_volume(1.0)
        pop_sounds.append(sound)    
    except:
        print(f"not playing pop{i}.wav")

# Bubble class
class Bubble:
    def __init__(self):
        self.radius = random.randint(BUBBLE_MIN_RADIUS, BUBBLE_MAX_RADIUS)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = HEIGHT + self.radius
        self.color = BUBBLE_COLOR
        self.popped = False
        self.alpha = 255  # fade out on pop
        self.pop_sound = random.choice(pop_sounds) if pop_sounds else None

        # Blast effect
        self.blast_radius = self.radius
        self.blast_alpha = 255
       

    def update(self):
        if not self.popped:
            self.y -= BUBBLE_SPEED
        else:
            self.alpha -= 10
            self.blast_radius += 3
            self.blast_alpha -= 15
            if self.alpha <= 0 and self.blast_alpha <= 0:
                return False
        return True

    def draw(self, surface):
        # bubble
        if self.alpha > 0: 
            bubble_surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            draw_color = (*self.color, self.alpha)
            pygame.draw.circle(bubble_surface, draw_color, (self.radius, self.radius), self.radius)
            surface.blit(bubble_surface, (self.x - self.radius, self.y - self.radius))

        # blast effect ring coming out of the buble
        if self.popped and self.blast_alpha > 0:
            ring_surface = pygame.Surface((self.blast_radius*2, self.blast_radius*2), pygame.SRCALPHA)
            ring_color = (255, 255, 255, self.blast_alpha)
            pygame.draw.circle(ring_surface, ring_color, (self.blast_radius, self.blast_radius), self.blast_radius, width=4)
            surface.blit(ring_surface, (self.x - self.blast_radius, self.y - self.blast_radius))

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
                    if bubble.pop_sound:
                        bubble.pop_sound.play()
                

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