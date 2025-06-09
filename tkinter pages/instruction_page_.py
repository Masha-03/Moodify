import tkinter as tk
import pygame
import customtkinter as ctk
import sys
import sqlite3
import subprocess #Open new window
import os
from PIL import Image,ImageTk
import time

#------------------------------------------------------------------------------------------------------------------------------------------------------#
#for animation of the button
original_y = None  # Define at the top of your file

def bob(widget, direction=1):
    global original_y
    if original_y is None:
        original_y = widget.winfo_y()
    y = widget.winfo_y() + direction
    widget.place_configure(y=y)

    if y >= original_y + 5:
        direction = -1
    elif y <= original_y - 5:
        direction = 1

    widget.after(100, lambda: bob(widget, direction))

def increase_font_size():
    size = current_font_size.get()
    if size < 20:  # max size limit
        current_font_size.set(size + 1)
        instruction_text_widget.configure(font=("Segoe UI", current_font_size.get()))

def decrease_font_size():
    size = current_font_size.get()
    if size > 10:  # min size limit
        current_font_size.set(size - 1)
        instruction_text_widget.configure(font=("Segoe UI", current_font_size.get()))

#--------------------------------------------------------------masha---------------------------------------------------------------------------------#
#Get profile from the database
def get_profile():
    global profile
    connect = sqlite3.connect('moodify_database.db')
    cursor = connect.cursor()
    
    #Fetch the profile
    cursor.execute("SELECT profile FROM user_info ORDER BY ROWID DESC LIMIT 1") #Fetch latest profile
    result = cursor.fetchone()
    
    connect.close() #Close connection
    if result:
        profile = result[0]  #Store the profile 
    else:
        profile = None  #Set profile to None if no profile found
        
def get_gender():
    if profile is None:
        return None
    connect = sqlite3.connect('moodify_database.db')
    cursor = connect.cursor()
    cursor.execute("SELECT gender FROM user_info WHERE profile = ? LIMIT 1", (profile,))
    result = cursor.fetchone()
    connect.close()
    if result:
        return result[0]
    else:
        return None
    
def start_game():
    get_profile()
    gender = get_gender()
    
    if gender is None:
        tk.messagebox.showerror("Error", "No gender found for profile.")
        return
    
    gender = gender.strip().lower()
    
    if gender == "female":
        subprocess.Popen([sys.executable, "main game code.py"])
        #Wait for 3 seconds before closing the window
        time.sleep(3)
        #Close the current Tkinter window
        root.destroy()
    elif gender == "male":
        subprocess.Popen([sys.executable, "main game code_Male.py"])
        #Wait for 3 seconds before closing the window
        time.sleep(3)
        #Close the current Tkinter window
        root.destroy()
        
#--------------------------------------------------------------masha---------------------------------------------------------------------------------#

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Moodify Game")

    running = True
    while running:
        screen.fill((0, 0, 0))  # Fill screen with black

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
def get_image_path(filename):
    # This gets the path of the current Python file
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

def scroll_to_top():
    canvas.yview_moveto(0)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#Tkinter instruction window
root = tk.Tk()
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
root.title("Moodify Instructions")

current_font_size = tk.IntVar(value=13)  # starting font size
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Load and set background image
base_dir = os.path.dirname(os.path.abspath(__file__)) 
bg_image_path = os.path.join(base_dir, "instruction_page_bg.png") 
bg_image=Image.open(bg_image_path)
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Title Label
title_label = tk.Label(root,text="🌼 Welcome to Moodify! 🌼",font=("Segoe UI", 18, "bold"),bg="#fbe4ff",fg="#4A4A4A",pady=20)
title_label.pack(pady=(10, 10))

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Outer frame (holds the framed instruction box)
outer_frame = tk.Frame(root, bg="#fbe4ff")
outer_frame.pack(pady=(0,10), padx=30, fill="both", expand=True)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Inner box frame with visible border
box_frame = tk.Frame(outer_frame, bg="#FFEFE1", bd=3, relief="ridge",width=1100,height=420)
box_frame.pack(fill="x", expand=False,padx=20,pady=10)
box_frame.pack_propagate(False)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Canvas inside the box
canvas = tk.Canvas(box_frame, bg="#FFEFE1", highlightthickness=0)
canvas.pack(side="left", fill="y")
canvas.configure(height=420,width=1100)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#SCROLLBAR
# Scrollbar INSIDE the box
scrollbar = tk.Scrollbar(box_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)

# Frame inside canvas for content
scrollable_frame = tk.Frame(canvas, bg="#FFEFE1")
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Auto scrollregion update
def update_scrollregion(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))

scrollable_frame.bind("<Configure>", update_scrollregion)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Enable scrolling with the mouse wheel
def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Bind mouse wheel to canvas (Windows and Linux)
canvas.bind_all("<MouseWheel>", on_mousewheel) #everytime the mouse wheel scrolled,call on_mousewheel event

# Bind mouse wheel for macOS (uses different event name)
canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Instruction Text

# Instruction Text (using Text widget for styling)
instruction_text_widget = tk.Text(scrollable_frame, font=("Segoe UI", 13), bg="#FFF2E6", fg="#333333", wrap="word", padx=40, pady=20, height=20, width=100)
instruction_text_widget.pack(pady=(0, 20))

# Insert the bold, bigger "How to Use:" heading
instruction_text_widget.insert("1.0", "💡 How to Use:\n\n")
instruction_text_widget.tag_add("title", "1.0", "1.end")
instruction_text_widget.tag_config("title", font=("Segoe UI", 20, "bold"), foreground="#333333")

instruction_text = (
        "🎮 **Controls**:\n"
        "• Move: Arrow Keys\n"  
        "• Toggle Fullscreen: Ctrl + f\n"
        "• Quit: ESC\n\n"
        "👀 There are *8 COOL FEATURES* waiting for you to explore:\n\n"
        "🌼 **Core Features**\n"
        "📖 Diary\n"
        "• Tap the **books next to the radio** on the table to open your **DIARY** — spill your thoughts, no judgment.\n"
        "😄 Mood Tracker\n"
        "• Tap the **emoji squad on the wall** to track your feels with the **MOOD TRACKER**.\n"
        "📅 Calendar\n"
        "• Tap the **calendar on the wall** to throwback to your past moods and diary entries.\n\n"
        "🧘 **Mindfulness Tools**\n"
        "🎧 Chill Sounds\n"
        "• Tap the **radio by the books** to vibe out with **CHILL SOUNDS** — total zen.\n"
        "⏳ Breathing Exercise\n"
        "• Tap the **hourglass by the TV** to do some **BREATHING EXERCISE** — in, out, chill.\n"
        "📱 Stress Check Survey\n"
        "• Tap the **phone under the settings icon** to take a quick **STRESS CHECK SURVEY**.\n\n"
        "🎉 **Fun Extras**\n"
        "📊 Statistics\n"
        "• Tap the **graph beside the calendar** to explore the **STATISTICS** feature and review your data.\n"
        "🌱 Growing Plant\n"  
        "• Tap the **plant next to the TV** to water it — help it grow like your inner peace.\n"
        "🛋️ Sofa & Friends\n"
        "• Bonus fun: Click the **sofa, cockroach, teddy bear, or pirate** for random cute bubble convos!\n"
        "💻 Hidden Games\n"
        "Oh — and there are *3 HIDDEN GAMES* inside the TV. Go find 'em 👀\n\n"
        "🔊 You can adjust or mute the background music anytime by clicking the **SETTINGS** icon.\n\n"
        "🌟 This app is your chill zone. Take a break, have fun, and treat yourself!"
    )

instruction_text_widget.insert("end", instruction_text)

#Highlight keywords
def highlight_text(text_widget, keyword, tag_name, color="red", font_weight="bold"):
    start = "1.0"
    while True:
        pos = text_widget.search(keyword, start, stopindex="end")
        if not pos:
            break
        end_pos = f"{pos}+{len(keyword)}c"
        text_widget.tag_add(tag_name, pos, end_pos)
        start = end_pos
    text_widget.tag_config(tag_name, foreground=color, font=(None, 13, font_weight))

# Apply highlights with balanced colors
highlight_text(instruction_text_widget, "DIARY", "diary_tag", color="#FF80C6", font_weight="bold")
highlight_text(instruction_text_widget, "MOOD TRACKER", "mood_tag", color="#FF80C6", font_weight="bold")
highlight_text(instruction_text_widget, "STATISTICS", "stats_tag", color="#9B59B6", font_weight="bold")
highlight_text(instruction_text_widget, "Arrow Keys", "arrow_keys_tag", color="#E67E22", font_weight="bold")
highlight_text(instruction_text_widget, "Ctrl + f", "ctrl_f_tag", color="#E67E22", font_weight="bold")
highlight_text(instruction_text_widget, "ESC", "esc_tag", color="#E67E22", font_weight="bold")
highlight_text(instruction_text_widget, "8 COOL FEATURES", "cool_features_tag", color="#48A9FF", font_weight="bold")
highlight_text(instruction_text_widget, "CHILL SOUNDS", "chill_sounds_tag", color="#22B5E6", font_weight="bold")
highlight_text(instruction_text_widget, "BREATHING EXERCISE", "breathing_tag", color="#22B5E6", font_weight="bold")
highlight_text(instruction_text_widget, "STRESS CHECK SURVEY", "stress_tag", color="#22B5E6", font_weight="bold")
highlight_text(instruction_text_widget, "SETTINGS", "settings_tag", color="#95A5A6", font_weight="bold")
highlight_text(instruction_text_widget, "3 HIDDEN GAMES", "hidden_games_tag", color="#9B59B6", font_weight="bold")
highlight_text(instruction_text_widget, "Controls", "controls_tag", color="#E67E22", font_weight="bold")
highlight_text(instruction_text_widget, "Core Features", "core_tag", color="#FF80C6", font_weight="bold")
highlight_text(instruction_text_widget, "Mindfulness Tools", "mind_tag", color="#22B5E6", font_weight="bold")
highlight_text(instruction_text_widget, "Fun Extras", "fun_tag", color="#9B59B6", font_weight="bold")
highlight_text(instruction_text_widget, "sofa, cockroach, teddy bear, or pirate", "sofa_tag", color="#9B59B6", font_weight="bold")
highlight_text(instruction_text_widget, "plant next to the TV", "plant_tag", color="#9B59B6", font_weight="bold")

# Disable editing
instruction_text_widget.config(state="disabled")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
button_frame = tk.Frame(root,bg="#fbe4ff")
button_frame.pack(side='bottom', pady=(0,10))

start_button = ctk.CTkButton(button_frame,
    text="✨ Start Moodify ✨",
    font=("Segoe UI", 25, "bold"),
    fg_color="#B98EDC",         # background color
    hover_color="#9B59B6",      # on hover
    text_color="#F2E6FF",        # text color
    corner_radius=35,           # roundness
    height=60,
    command=start_game
)
start_button.pack(pady=(45,0)) # Center bottom

#for animation of button
def start_bob_safe():
    global original_y
    original_y = start_button.winfo_y()
    bob(start_button)

root.after(500, start_bob_safe)    # Start animation

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#Track fullscreen state
is_fullscreen = [False]

def toggle_fullscreen(event=None):
    is_fullscreen = root.attributes("-fullscreen")
    root.attributes("-fullscreen", not is_fullscreen)
    # After toggling fullscreen, update scrollregion to ensure scrolling works correctly
    root.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

root.bind("<Control-f>", toggle_fullscreen)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#exit button incase the ctrl+f key doesnt works
exit_button = ctk.CTkButton(
    root,
    text="❌ Exit",
    font=("Segoe UI", 14),
    fg_color="#FF5151",
    hover_color="#FF6A6A",
    text_color="white",
    corner_radius=25,
    command=root.destroy
)
exit_button.place(relx=0.97, rely=0.07, anchor="ne")

back_to_top_btn = ctk.CTkButton(
    root,
    text="⬆ Back to Top",
    font=("Segoe UI", 14),
    fg_color="#48A9FF",
    hover_color="#6FC8FF",
    text_color="white",
    corner_radius=25,
    command=scroll_to_top
)
back_to_top_btn.place(relx=0.97, rely=0.84, anchor="se")

increase_font_button = ctk.CTkButton(
    root,
    text="🔍 A+",
    font=("Segoe UI", 14),
    fg_color="#B0E0E6",
    hover_color="#87CEFA",
    text_color="black",
    command=increase_font_size,
    corner_radius=25,
    width=60
)
increase_font_button.place(relx=0.10, rely=0.78)

decrease_font_button = ctk.CTkButton(
    root,
    text="🔽 A-",
    font=("Segoe UI", 14),
    fg_color="#DDA0DD",
    hover_color="#DA70D6",
    text_color="black",
    command=decrease_font_size,
    corner_radius=25,
    width=60
)
decrease_font_button.place(relx=0.04, rely=0.78)

#---------------------------------------------------------------------------------------------------------------------------------------------#

# Run the app
root.mainloop()