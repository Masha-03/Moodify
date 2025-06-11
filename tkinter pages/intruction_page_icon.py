import tkinter as tk
import pygame
import customtkinter as ctk
import sys
import sqlite3
import subprocess #Open new window
import os
from PIL import Image,ImageTk
import time

# --- Asset Helper Function (for PyInstaller compatibility) ---
def resource_path(*relative_path_parts):
    """
    Returns the absolute path to a resource, whether running as a script
    or as a PyInstaller bundled executable.
    """
    try:
        # PyInstaller creates a temp folder and sets _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Not running as a PyInstaller executable, use current script directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, *relative_path_parts)

profile=None

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#for alignment
bg_photo_tk = None #hold PhotoImage object #keep a reference
bg_photo_id = None #to modify the existing image 
        
#-----------------------------------------------------------------------------------------------------------------------------------------------#

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
# Enable scrolling with the mouse wheel
def on_mousewheel(event):
    if event.num == 4:
        instruction_canvas.yview_scroll(-1, "units")
    elif event.num == 5:
        instruction_canvas.yview_scroll(1, "units")
    else:
        instruction_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

#-----------------------------------------------------------------------------------------------------------------------------------------------------#

def scroll_to_top():
    instruction_canvas.yview_moveto(0)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#

def increase_font_size():
    size = current_font_size.get()
    if size < 20:  # max size limit
        current_font_size.set(size + 1)
        instruction_text_widget.configure(font=("Segoe UI", current_font_size.get()))
        instruction_canvas.update_idletasks()
        instruction_canvas.configure(scrollregion=instruction_canvas.bbox("all"))

#-----------------------------------------------------------------------------------------------------------------------------------------------------#

def decrease_font_size():
    size = current_font_size.get()
    if size > 10:  # min size limit
        current_font_size.set(size - 1)
        instruction_text_widget.configure(font=("Segoe UI", current_font_size.get()))
        instruction_canvas.update_idletasks()
        instruction_canvas.configure(scrollregion=instruction_canvas.bbox("all"))
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#Tkinter instruction window
root = tk.Tk()
root.title("Moodify Instructions")
root.geometry("1280x720")

current_font_size = tk.IntVar(value=13) 
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Load and set background image
base_dir = os.path.dirname(os.path.abspath(__file__))
bg_image_path = os.path.join(base_dir, "instruction_page_bg.png")
try:
    bg_image_original = Image.open(bg_image_path)
except FileNotFoundError:
    tk.messagebox.showerror("Error", f"Background image not found: {bg_image_path}")
    root.destroy()
    sys.exit()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

main_canvas = tk.Canvas(root, highlightthickness=0)
main_canvas.pack(fill="both", expand=True)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#for alignment
outer_frame_window_id=None

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#for alignment
def resize_layout(event=None):
    global bg_photo_tk, bg_photo_id, outer_frame_window_id

    #get current width and height of main_canvas
    current_width = main_canvas.winfo_width()
    current_height = main_canvas.winfo_height()

    #safeguard
    if current_width == 1 or current_height == 1:
        return

#Resizing and placing background image
    resized_bg_image = bg_image_original.resize((current_width, current_height), Image.Resampling.LANCZOS) #takes bg_image_original and resizes it to match current height and width
    bg_photo_tk = ImageTk.PhotoImage(resized_bg_image) #convert pillow image into PhotoImage

    #Checks if the background image has already been placed on the canvas before
    if bg_photo_id:
        main_canvas.itemconfig(bg_photo_id, image=bg_photo_tk) #if  image is already on the canvas,this updates the existing image item with the new bg_photo_tk
    else:
        bg_photo_id = main_canvas.create_image(0, 0, image=bg_photo_tk, anchor="nw")  #If bg_photo_id is None (first time the function runs), it creates the image 
    main_canvas.tag_lower(bg_photo_id) #This ensures the background image stays at the very bottom layer of the canvas

#Positioning Outer Frame (Instruction Box Container)
    #relative percentage-They mean the outer_frame(instruction box's container)
    rel_outer_frame_width = 0.8 
    rel_outer_frame_height = 0.7

    outer_frame_abs_width = int(current_width * rel_outer_frame_width) #Calculates the actual pixel width for the outer_frame based on the canvas's current width and the relative percentage. 
    outer_frame_abs_height = int(current_height * rel_outer_frame_height) #Calculates the actual pixel height for the outer_frame based on the canvas's current height and the relative percentage. 
    outer_frame_x = (current_width - outer_frame_abs_width) / 2 #a formula to center an object horizontally

    rel_outer_frame_y = 0.15 #outer_frame will start 15% down from the top of the canvas
    outer_frame_y = current_height * rel_outer_frame_y #Calculates the absolute pixel Y coordinate.

    if outer_frame_window_id is None: #Checks if the outer_frame has been placed on the canvas before.
        outer_frame_window_id = main_canvas.create_window(outer_frame_x, outer_frame_y, window=outer_frame, anchor="nw",
                                                          width=outer_frame_abs_width, height=outer_frame_abs_height)
    else: #If the outer_frame_window_id already exists, these lines update the position and size of the existing outer_frame item on the canvas.
        main_canvas.coords(outer_frame_window_id, outer_frame_x, outer_frame_y)
        main_canvas.itemconfigure(outer_frame_window_id, width=outer_frame_abs_width, height=outer_frame_abs_height)

    #This ensures that the instruction_canvas and its contents (scrollable_frame, instruction_text_widget) have their correct, updated sizes before you try to calculate the scroll region.
    root.update_idletasks() 
    instruction_canvas.update_idletasks()
    #This line tells the instruction_canvas to set its scrollable area (scrollregion) to encompass "all" of its contents.
    instruction_canvas.configure(scrollregion=instruction_canvas.bbox("all"))
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Title Label
title_label = tk.Label(root,text="🌼 Welcome to Moodify! 🌼",font=("Segoe UI", 20, "bold"),bg="#fbe4ff",fg="#4A4A4A",pady=20)
title_label.place(relx=0.5, rely=0.05, anchor="n")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Outer frame (holds the framed instruction box)
outer_frame = tk.Frame(root, bg="#fbe4ff")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Inner box frame with visible border
box_frame = tk.Frame(outer_frame, bg="#FFEFE1", bd=3, relief="ridge",width=1100,height=420)
box_frame.pack(fill="both", expand=True,padx=20,pady=20)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Canvas inside the box
instruction_canvas = tk.Canvas(box_frame, bg="#FFEFE1", highlightthickness=0)
instruction_canvas.pack(side="left", fill="both", expand=True)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#SCROLLBAR
# Scrollbar INSIDE the box
scrollbar = tk.Scrollbar(box_frame, orient="vertical", command=instruction_canvas.yview)
scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
instruction_canvas.configure(yscrollcommand=scrollbar.set)

# Frame inside canvas for content
scrollable_frame = tk.Frame(instruction_canvas, bg="#FFEFE1")
instruction_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw",tags="scrollable_frame")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Auto scrollregion update
def update_scrollregion(event=None):
    instruction_canvas.configure(scrollregion=instruction_canvas.bbox("all"))
    canvas_width = instruction_canvas.winfo_width()
    if canvas_width > 0:
        instruction_canvas.itemconfig("scrollable_frame", width=canvas_width)

scrollable_frame.bind("<Configure>", update_scrollregion)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Instruction Text

# Instruction Text (using Text widget for styling)
instruction_text_widget = tk.Text(scrollable_frame, font=("Segoe UI", 13), bg="#FFF2E6", fg="#333333", wrap="word", padx=40, pady=20, height=20, width=100)
instruction_text_widget.pack(fill="both",expand=True)

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

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

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

#Track fullscreen state
is_fullscreen = [False]

def toggle_fullscreen(event=None):
    current_fullscreen_state = root.attributes("-fullscreen")
    root.attributes("-fullscreen", not current_fullscreen_state)
    is_fullscreen[0] = not current_fullscreen_state

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

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

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
back_to_top_btn.place(relx=0.97, rely=0.93, anchor="se")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

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
increase_font_button.place(relx=0.10, rely=0.88)

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
decrease_font_button.place(relx=0.04, rely=0.88)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# --- Initial setup calls ---
root.attributes("-fullscreen", True) # Start in fullscreen
root.bind("<Configure>", resize_layout)
root.after(100, resize_layout)

root.bind_all("<MouseWheel>", on_mousewheel)
root.bind_all("<Button-4>", on_mousewheel)
root.bind_all("<Button-5>", on_mousewheel)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Run the app
root.mainloop()