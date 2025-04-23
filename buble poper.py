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
BUBBLE_SPEED = 3
BUBBLE_INTERVAL = 60  # frames between spawns for each bubbles

#sound list
pop_sounds = []
for i in range (1,5):
    try:
        sound = pygame.mixer.Sound(f"pop{i}.wav") #load sound files
        sound.set_volume(1.0) #setting volume to max
        pop_sounds.append(sound)    #add to the list
    except:
        print(f"not playing pop{i}.wav") # shows if the sound is not playing because file missing

# Bubble class
class Bubble:
    def __init__(self):
        self.radius = random.randint(BUBBLE_MIN_RADIUS, BUBBLE_MAX_RADIUS) #random bubble radius
        self.x = random.randint(self.radius, WIDTH - self.radius) #random horizontol position that stays within the screen
        self.y = HEIGHT + self.radius #starts below the screen
        self.color = BUBBLE_COLOR #white color before popped
        self.popped = False #not yet popped
        self.alpha = 255  # fade out on pop
        self.pop_sound = random.choice(pop_sounds) if pop_sounds else None #assign random pop sound if available

        # Blast effect
        self.blast_radius = self.radius #ring effect same size with the bbbles starts
        self.blast_alpha = 255 #ring is fully available at first
       

    def update(self):
        if not self.popped:
            self.y -= BUBBLE_SPEED #move up the screen
        else:
            self.alpha -= 10 #fade out the bubble
            self.blast_radius += 3 #increase the ring size
            self.blast_alpha -= 15 #fade out the ring effect
            if self.alpha <= 0 and self.blast_alpha <= 0: #remove the bubble and ring effect when fully faded out
                return False #remove bubble from the list
        return True

    def draw(self, surface):
        # bubble
        if self.alpha > 0: 
            bubble_surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA) #create a surface for the bubble
            draw_color = (*self.color, self.alpha)                                              #color with alpha for fade out effect
            pygame.draw.circle(bubble_surface, draw_color, (self.radius, self.radius), self.radius) #draw the bubble
            surface.blit(bubble_surface, (self.x - self.radius, self.y - self.radius)) #draw the bubble on the screen

        # blast effect ring coming out of the buble
        if self.popped and self.blast_alpha > 0: #draw the ring effect only if the bubble is popped and the ring is not fully faded out
            ring_surface = pygame.Surface((self.blast_radius*2, self.blast_radius*2), pygame.SRCALPHA) #create a surface for the ring
            ring_color = (255, 255, 255, self.blast_alpha) #color with alpha for fade out effect
            pygame.draw.circle(ring_surface, ring_color, (self.blast_radius, self.blast_radius), self.blast_radius, width=4) #draw the ring
            surface.blit(ring_surface, (self.x - self.blast_radius, self.y - self.blast_radius)) #draw the ring on the screen

    def check_click(self, pos): #check if the bubble is clicked
        if not self.popped: #check if the bubble is not yet popped
            dx, dy = self.x - pos[0], self.y - pos[1] #calculate the distance from the click to the bubble center
            distance = (dx**2 + dy**2)**0.5 #distance formula
            return distance <= self.radius #check if the click is within the bubble radius
        return False #if the bubble is already popped, return false

def play_background_music():
    pygame.mixer.init()
    pygame.mixer.music.load("lofi_music.wav") 
    pygame.mixer.music.set_volume(0.5)      
    pygame.mixer.music.play(-1)                # -1 means loop indefinitely

play_background_music()


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
    bubbles = [b for b in bubbles if b.update()] #remove bubbles that are fully faded out
    for bubble in bubbles:
        bubble.draw(screen) #draw the bubbles and ring effect

    pygame.display.flip() #update the screen
    clock.tick(FPS) #maintain the frame rate




