import pygame
import random
import sys
import time
import subprocess

calming_words = [
    "Fail", "Weak", "Loser", "Alone", "Broken",
    "Fake", "Empty", "Lost", "Stuck", "Worthless"
]

# Initialize Pygame
pygame.init()
word_font = pygame.font.SysFont(None, 28)  # font for the words in the bubble

# Screen settings
# Set the minimum resolution
MIN_SCREEN_WIDTH = 1280
MIN_SCREEN_HEIGHT = 720

screen_width, screen_height = MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Bubble Popper")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Colors
BG_COLOR = (180, 220, 255)
BUBBLE_COLOR = (255, 255, 255)
POP_COLOR = (200, 200, 255)
SPARKLE_COLOR = (255, 255, 255)
LOADING_COLOR = (180, 220, 255)

# Bubble settings
BUBBLE_MIN_RADIUS = 50
BUBBLE_MAX_RADIUS = 90
BUBBLE_SPEED = 2  # reduced base speed for better realism
BUBBLE_INTERVAL = 30  # frames between spawns for each bubbles

# particle settings
PARTICLE_COUNT = 50

# sound list
pop_sounds = []
for i in range(1, 5):
    try:
        sound = pygame.mixer.Sound(f"bubble sound/pop{i}.wav")  # load sound files
        sound.set_volume(1.0)  # setting volume to max
        pop_sounds.append(sound)  # add to the list
    except:
        print(f"not playing pop{i}.wav")  # shows if the sound is not playing because file missing

def show_loading_screen():
    screen.fill(LOADING_COLOR)  # Fill with light blue
    loading_text = font.render("Returning to Main Game...", True, (0, 0, 0))  # Text to show on loading screen
    text_rect = loading_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(loading_text, text_rect)  # Position the loading text
    pygame.display.update()  # Refresh the screen immediately
    pygame.event.clear()  # Prevent needing to click before it responds
    pygame.time.delay(2000)  # Wait 2 seconds without freezing rendering

# bubble class
class Bubble:
    def __init__(self):
        self.original_radius = random.randint(BUBBLE_MIN_RADIUS, BUBBLE_MAX_RADIUS)
        self.radius = self.original_radius
        self.x = random.randint(self.radius, screen_width - self.radius)
        self.y = screen_height + self.radius
        self.color = BUBBLE_COLOR
        self.popped = False
        self.alpha = 255
        self.pop_sound = random.choice(pop_sounds) if pop_sounds else None
        self.show_text = random.random() < 0.4
        self.word = random.choice(calming_words) if self.show_text else ""
        self.vertical_speed = BUBBLE_SPEED + random.uniform(-0.5, 0.5)
        self.horizontal_drift = random.uniform(-0.2, 0.2)
        self.size_change_rate = random.uniform(-0.05, 0.05)
        self.color_offset = [random.uniform(-10, 10) for _ in range(3)]
        self.alpha_change_rate = random.uniform(-1, 1)
        self.rotation_angle = 0
        self.rotation_speed = random.uniform(-0.02, 0.02)
        self.blast_radius = self.radius
        self.blast_alpha = 255

    def update(self):
        global screen_width, screen_height
        scale_factor_width = screen_width / MIN_SCREEN_WIDTH
        scale_factor_height = screen_height / MIN_SCREEN_HEIGHT

        if not self.popped:
            self.y -= self.vertical_speed * speed_modifier * scale_factor_height
            self.x += self.horizontal_drift * speed_modifier * scale_factor_width
            self.radius = self.original_radius * min(scale_factor_width, scale_factor_height)
            self.radius += self.size_change_rate * speed_modifier * min(scale_factor_width, scale_factor_height)
            self.alpha += self.alpha_change_rate * speed_modifier
            self.rotation_angle += self.rotation_speed * speed_modifier

            self.radius = max(BUBBLE_MIN_RADIUS * 0.8 * min(scale_factor_width, scale_factor_height),
                              min(self.radius, BUBBLE_MAX_RADIUS * 1.2 * min(scale_factor_width, scale_factor_height)))
            self.alpha = max(50, min(self.alpha, 255))

            if self.x < -self.radius:
                self.x = screen_width + self.radius
            elif self.x > screen_width + self.radius:  # Changed screen_height to screen_width
                self.x = -self.radius
        else:
            self.alpha -= 10
            self.blast_radius += 3 * min(scale_factor_width, scale_factor_height)
            self.blast_alpha -= 15
            if self.alpha <= 0 and self.blast_alpha <= 0:
                return False
        return True

    def draw(self, surface):
        if self.alpha > 0:
            bubble_surface = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            draw_color = (
                int(max(0, min(255, self.color[0] + self.color_offset[0]))),
                int(max(0, min(255, self.color[1] + self.color_offset[1]))),
                int(max(0, min(255, self.color[2] + self.color_offset[2]))),
                int(self.alpha)
            )
            pygame.draw.circle(bubble_surface, draw_color, (int(self.radius), int(self.radius)), int(self.radius))

            rotated_surface = pygame.transform.rotate(bubble_surface, self.rotation_angle)
            rotated_rect = rotated_surface.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(rotated_surface, rotated_rect)

            if not self.popped:
                word_surf = word_font.render(self.word, True, (80, 80, 120))
                word_rect = word_surf.get_rect(center=(int(self.x), int(self.y)))
                surface.blit(word_surf, word_rect)

        if self.popped and self.blast_alpha > 0:
            ring_surface = pygame.Surface((int(self.blast_radius * 2), int(self.blast_radius * 2)), pygame.SRCALPHA)
            ring_color = (255, 255, 255, self.blast_alpha)
            pygame.draw.circle(ring_surface, ring_color, (int(self.blast_radius), int(self.blast_radius)), int(self.blast_radius), width=4)
            surface.blit(ring_surface, (self.x - self.blast_radius, self.y - self.blast_radius))

    def check_click(self, pos):
        if not self.popped:
            dx, dy = self.x - pos[0], self.y - pos[1]
            distance = (dx**2 + dy**2)**0.5
            return distance <= self.radius
        return False

# particle class
class Particle:
    def __init__(self):
        self.original_x = random.randint(0, MIN_SCREEN_WIDTH)
        self.original_y = random.randint(0, MIN_SCREEN_HEIGHT)
        self.x = self.original_x
        self.y = self.original_y
        self.original_radius = random.randint(1, 3)
        self.radius = self.original_radius
        self.original_speed = random.uniform(0.2, 0.8)
        self.speed = self.original_speed

    def update(self):
        global screen_width, screen_height
        scale_factor_height = screen_height / MIN_SCREEN_HEIGHT
        scale_factor_width = screen_width / MIN_SCREEN_WIDTH

        self.y -= self.speed * scale_factor_height
        self.radius = self.original_radius * min(scale_factor_width, scale_factor_height)
        self.speed = self.original_speed * scale_factor_height

        if self.y < 0:
            self.y = screen_height
            self.x = random.randint(0, screen_width)

    def draw(self, surface):
        pygame.draw.circle(surface, SPARKLE_COLOR, (int(self.x), int(self.y)), int(self.radius))

class Button:
    def __init__(self, x, y, width, height, text, onclick):
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = self.original_rect.copy()
        self.color = pygame.Color(255, 200, 200)
        self.hover_color = (255, 170, 170)
        self.text = text
        self.onclick = onclick
        self.font = pygame.font.SysFont(None, 40)
        self.text_surf = self.font.render(self.text, True, (0, 128, 128))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        self.image = None

    def update_position(self):
        global screen_width, screen_height
        scale_factor_width = screen_width / MIN_SCREEN_WIDTH
        scale_factor_height = screen_height / MIN_SCREEN_HEIGHT

        self.rect.x = int(self.original_rect.x * scale_factor_width)
        self.rect.y = int(self.original_rect.y * scale_factor_height)
        self.rect.width = int(self.original_rect.width * scale_factor_width)
        self.rect.height = int(self.original_rect.height * scale_factor_height)

        # Re-render text for proper scaling
        font_size = int(40 * min(scale_factor_width, scale_factor_height))
        self.font = pygame.font.SysFont(None, font_size)
        self.text_surf = self.font.render(self.text, True, (0, 128, 128))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)


    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        if self.image is not None:
            surface.blit(self.image, self.image.get_rect(center=self.rect.center))
        else:
            surface.blit(self.text_surf, self.text_rect)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.onclick()

current_page = "bubble_popper"
speed_modifier = 1.0
fullscreen = False

def switch_page():
    global running
    show_loading_screen()
    running = False

def toggle_slow_motion():
    global speed_modifier
    if speed_modifier == 1.0:
        speed_modifier = 0.4
        pygame.mixer.music.set_volume(0.2)
    else:
        speed_modifier = 1.0
        pygame.mixer.music.set_volume(0.5)

def toggle_fullscreen():
    global fullscreen, screen, screen_width, screen_height
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        screen_width, screen_height = screen.get_size()
    else:
        screen_width, screen_height = MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    
    # Update button positions after screen resize
    button.update_position()
    slow_button.update_position()


# game variables
bubbles = []
particles = [Particle() for _ in range(PARTICLE_COUNT)]
frame_count = 0
running = True
button = Button(50, 50, 200, 60, "Back", switch_page)
slow_button = Button(270, 50, 200, 60, "Slow Motion", toggle_slow_motion)

# text font size
font = pygame.font.Font(None, 40)
# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                show_loading_screen()
                running = False
            elif event.key == pygame.K_f:
                toggle_fullscreen()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_page == "bubble_popper":
                for bubble in bubbles:
                    if bubble.check_click(event.pos):
                        bubble.popped = True
                        bubble.color = POP_COLOR
                        if bubble.pop_sound:
                            bubble.pop_sound.play()
                button.check_click(event.pos)
                slow_button.check_click(event.pos)
        elif event.type == pygame.VIDEORESIZE:
            if not fullscreen:
                new_width = max(event.w, MIN_SCREEN_WIDTH)
                new_height = max(event.h, MIN_SCREEN_HEIGHT)
                screen_width, screen_height = new_width, new_height
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
                
                # Update button positions after screen resize
                button.update_position()
                slow_button.update_position()


    screen.fill(BG_COLOR)
    frame_count += 1

    if current_page == "bubble_popper":
        if frame_count % BUBBLE_INTERVAL == 0:
            bubbles.append(Bubble())

        for particle in particles:
            particle.update()
            particle.draw(screen)

        bubbles = [b for b in bubbles if b.update()]
        for bubble in bubbles:
            bubble.draw(screen)

        button.draw(screen)
        slow_button.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.mixer.quit()
pygame.quit()
sys.exit()