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
SPARKLE_COLOR = (255, 255, 255)

# Bubble settings
BUBBLE_MIN_RADIUS = 50
BUBBLE_MAX_RADIUS = 90
BUBBLE_SPEED = 3
BUBBLE_INTERVAL = 60  # frames between spawns for each bubbles

#particle settings
PARTICLE_COUNT = 50

#sound list
pop_sounds = []
for i in range (1,5):
    try:
        sound = pygame.mixer.Sound(f"pop{i}.wav") #load sound files
        sound.set_volume(1.0) #setting volume to max
        pop_sounds.append(sound)    #add to the list
    except:
        print(f"not playing pop{i}.wav") # shows if the sound is not playing because file missing

#play background music
def play_background_music():
    pygame.mixer.init()
    pygame.mixer.music.load("lofi_music.wav") 
    pygame.mixer.music.set_volume(0.5)      
    pygame.mixer.music.play(-1)                # -1 means loop indefinitely

#bubble class
class Bubble:
    def __init__(self):
        self.radius = random.randint(BUBBLE_MIN_RADIUS, BUBBLE_MAX_RADIUS)  #random bubble radius
        self.x = random.randint(self.radius, WIDTH - self.radius)  #random horizontol position that stays within the screen
        self.y = HEIGHT + self.radius  #starts below the screen
        self.color = BUBBLE_COLOR  #white color before popped
        self.popped = False  #not yet popped
        self.alpha = 255   # fade out on pop
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
        if self.popped and self.blast_alpha > 0:      #draw the ring effect only if the bubble is popped and the ring is not fully faded out
            ring_surface = pygame.Surface((self.blast_radius*2, self.blast_radius*2), pygame.SRCALPHA) #create a surface for the ring
            ring_color = (255, 255, 255, self.blast_alpha)       #color with alpha for fade out effect
            pygame.draw.circle(ring_surface, ring_color, (self.blast_radius, self.blast_radius), self.blast_radius, width=4) #draw the ring
            surface.blit(ring_surface, (self.x - self.blast_radius, self.y - self.blast_radius))      #draw the ring on the screen

    def check_click(self, pos):     #check if the bubble is clicked
        if not self.popped:     #check if the bubble is not yet popped
            dx, dy = self.x - pos[0], self.y - pos[1]   #calculate the distance from the click to the bubble center
            distance = (dx**2 + dy**2)**0.5     #distance formula
            return distance <= self.radius  #check if the click is within the bubble radius
        return False       #if the bubble is already popped, return false

#particle class
class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)       #random horizontal position
        self.y = random.randint(0, HEIGHT)      #random vertical position
        self.radius = random.randint(1, 3)      #random radius for the particle
        self.speed = random.uniform(0.2, 0.8)   #random speed for the particle

    def update(self):
        self.y -= self.speed
        if self.y < 0: 
            self.y = HEIGHT
            self.x = random.randint(0, WIDTH) 

    def draw(self, surface):
        pygame.draw.circle(surface, SPARKLE_COLOR, (int(self.x), int(self.y)), self.radius)

class Button:
    def __init__(self, x, y, width, height, text, onclick):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color(255, 200, 200)
        self.hover_color = (255, 170, 170)
        self.text = text
        self.onclick = onclick
        self.font = pygame.font.SysFont(None, 40)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=12)

        text_surf = self.font.render(self.text, True, (0, 128, 128))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.onclick()

current_page = "bubble_popper"
speed_modifier = 1.0 

def switch_page():
    global current_page
    current_page = "other"

def go_to_game():
    global current_page
    current_page = "bubble_popper"

def go_to_home():
    global current_page
    current_page = "home"

def go_to_tv():
    global current_page
    current_page = "tv_page"

def toggle_slow_motion():
    global speed_modifier
    if speed_modifier == 1.0:
        speed_modifier = 0.4
        pygame.mixer.music.set_volume(0.2) #lower the volume
    else:
        speed_modifier = 1.0
        pygame.mixer.music.set_volume(0.5)


#game variables 
bubbles = []
particles = [Particle() for _ in range(PARTICLE_COUNT)]
frame_count = 0
running = True
button = Button(50, 50, 200, 60, "Settings", switch_page) #create a button to switch to other page
slow_button = Button(270, 50, 200, 60, "Slow Motion", toggle_slow_motion) #create a button to toggle slow motion
game_icon_button = Button(50, 50, 100, 100, "🎮", go_to_game)  # "🎮" game emoji
home_icon_button = Button(170, 50, 100, 100, "🏠", go_to_home) # "🏠" home emoji
tv_icon_button = Button(290, 50, 100, 100, "📺", go_to_tv) # "📺" tv emoji
play_background_music() #play background music

# Main loop
running = True
while running:
    screen.fill(BG_COLOR)
    frame_count += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_page == "bubble_popper": #check if the current page is bubble popper
                for bubble in bubbles:
                    if bubble.check_click(event.pos):
                        bubble.popped = True
                        bubble.color = POP_COLOR
                        if bubble.pop_sound:
                            bubble.pop_sound.play()
                button.check_click(event.pos)
                slow_button.check_click(event.pos)
            elif current_page == "other":
                game_icon_button.check_click(event.pos)
                home_icon_button.check_click(event.pos)
                tv_icon_button.check_click(event.pos)

            elif current_page == "home":
                game_icon_button.check_click(event.pos)
        
        #add bubbles
    if current_page == "bubble_popper":
        if frame_count % BUBBLE_INTERVAL == 0:
            bubbles.append(Bubble()) #to add new bubbles 
        for particle in particles:
            particle.update()
            particle.draw(screen)
        
        # Update and draw bubbles
        bubbles = [b for b in bubbles if b.update()]
        for bubble in bubbles:
            bubble.draw(screen) 

        #update and drw the bubbles
        button.draw(screen)
        slow_button.draw(screen)

    elif current_page == "tv_page":
        screen.fill((220, 240, 255))
        font = pygame.font.SysFont(None, 60)
        txt = font.reader("Tv Page", True, (40, 80, 120))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2))
      
    elif current_page == "other":
        screen.fill((240, 220, 255))
        font = pygame.font.SysFont(None, 60)
        txt = font.render("Settings Page", True, (100, 40, 100))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2))

        game_icon_button.draw(screen) #draw the game icon button
        home_icon_button.draw(screen)
        tv_icon_button.draw(screen)
    pygame.display.flip()
    clock.tick(FPS) #maintain the frame rate    
    
pygame.quit()
sys.exit()
   




