import tkinter as tk
import pygame
import customtkinter as ctk
import sys
import sqlite3
import subprocess
import os
from PIL import Image, ImageTk
import time




# --- Asset Helper Function (for PyInstaller compatibility) ---
def resource_path(*relative_path_parts):
    """
    Returns the absolute path to a resource, whether running as a script
    or as a PyInstaller bundled executable.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Not frozen (running in development)
        # This will get the directory of the current script file
        base_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    
    # Join all path components
    return os.path.join(base_path, *relative_path_parts)

#------------------------------------------------------------------------------------------------------------------------------------------------------#
#for the animation of the start button
# New global variables to manage bobbing animation state
bob_initial_pady = 10 # This is the initial pady value from start_button.pack(pady=(10,0))
current_bob_pady = bob_initial_pady
bob_direction = 1 # 1 for increasing pady (down), -1 for decreasing pady (up)

def bob_packed_widget(widget):
    global current_bob_pady, bob_direction

    try:
        # Calculate new pady for the animation
        current_bob_pady += bob_direction

        # Apply new pady to the widget using pack_configure
        widget.pack_configure(pady=(current_bob_pady, 0)) # Assuming 0 for bottom pady

        # Reverse direction if limits are reached (bobbing range: initial_pady +/- 5 pixels)
        if current_bob_pady >= bob_initial_pady + 5: # Bob down limit
            bob_direction = -1
        elif current_bob_pady <= bob_initial_pady - 5: # Bob up limit
            bob_direction = 1

        # Schedule the next animation frame
        widget.after(100, lambda: bob_packed_widget(widget))
    except tk.TclError:
        # Catch error if widget is destroyed (e.g., window closed)
        pass

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

import os, sys

def get_db_path():
    db_file_name = "moodify_database.db"

    if getattr(sys, 'frozen', False):
        # Running from EXE inside "Moodify/tkinter pages"
        exe_dir = os.path.dirname(sys.executable)
        app_root = os.path.abspath(os.path.join(exe_dir, ".."))  # Goes up to "Moodify/"
    else:
        # Running from .py inside "Moodify/tkinter pages"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root = os.path.abspath(os.path.join(script_dir, ".."))  # Goes up to "Moodify/"

    db_path = os.path.join(app_root, "database", db_file_name)
    print(f"INSTRUCTION PAGE: Using DB path → {db_path}")
    print("DB exists:", os.path.exists(db_path))
    return db_path


database_file_path = get_db_path()


print("INSTRUCTION PAGE: Using DB path →", get_db_path())
print("DB exists:", os.path.exists(get_db_path()))


#Check if the database file exists at the calculated path
if os.path.exists(database_file_path):
    print(f"Database file FOUND at: {database_file_path}")
else:
    print(f"Database file NOT FOUND at: {database_file_path}")

#Get profile from the database
def get_profile():
    global profile
    try:
        connect = sqlite3.connect(database_file_path)
        cursor = connect.cursor()

        #Fetch the profile
        cursor.execute("SELECT profile FROM user_info ORDER BY ROWID DESC LIMIT 1") #Fetch latest profile
        result = cursor.fetchone()

        connect.close() #Close connection
        if result:
            profile = result[0]  #Store the profile
        else:
            profile = None  #Set profile to None if no profile found
    except sqlite3.Error as e:
        print(f"Database error in get_profile: {e}")
        profile = None # Ensure profile is None on error

def get_gender():
    if profile is None:
        return None
    try:
        connect = sqlite3.connect(database_file_path)
        cursor = connect.cursor()
        cursor.execute("SELECT gender FROM user_info WHERE profile = ? LIMIT 1", (profile,))
        result = cursor.fetchone()
        connect.close()
        if result:
            return result[0]
        else:
            return None
    except sqlite3.Error as e:
        print(f"Database error in get_gender: {e}")
        return None

def start_game():
    get_profile()
    gender = get_gender()

    if gender is None:
        tk.messagebox.showerror("Error", "No gender found for profile or database error.")
        return

    gender = gender.strip().lower()

    if getattr(sys, 'frozen', False):
        # Running from PyInstaller EXE
        base_dir = os.path.dirname(sys.executable)
        exe_dir = os.path.abspath(os.path.join(base_dir, "..", "dist"))
    else:
        # Running from VS Code or Python
        script_dir = os.path.dirname(os.path.abspath(__file__))
        exe_dir = os.path.abspath(os.path.join(script_dir, "..", "dist"))

    if gender == "female":
        script_path = os.path.join(exe_dir, "main game code.exe")
    elif gender == "male":
        script_path = os.path.join(exe_dir, "main game code_Male.exe")
    else:
        tk.messagebox.showerror("Error", "Invalid gender.")
        return

    if not os.path.exists(script_path):
        tk.messagebox.showerror("Error", f"Game not found:\n{script_path}")
        return

    subprocess.Popen([script_path], close_fds=True)
    root.destroy()

#--------------------------------------------------------------masha---------------------------------------------------------------------------------#

def run_game(): # This function seems unused in your current flow
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
# Helper for mousewheel scrolling
def on_mousewheel(event):
    instruction_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#Tkinter instruction window
root = tk.Tk()
root.title("Moodify Instructions")

# Create a single canvas to hold the background image and all other widgets
main_canvas = tk.Canvas(root, bg="white") # Set a default background for the canvas
main_canvas.pack(fill="both", expand=True)

current_font_size = tk.IntVar(value=13)  # starting font size

# Load background image once
base_dir = os.path.dirname(os.path.abspath(__file__))
bg_image_original = Image.open(resource_path("instruction_page_bg.png"))
bg_photo_id = None # Store the canvas item ID for the background image
bg_photo_tk = None # Store the PhotoImage object reference

# Keep references to the window IDs for dynamic positioning
# Initialize to None, these will hold the IDs returned by main_canvas.create_window
#for alignment
title_window_id = None
outer_frame_window_id = None
button_frame_window_id = None
exit_button_window_id = None
back_to_top_btn_window_id = None
increase_font_button_window_id = None
decrease_font_button_window_id = None

#----------------------------------------------------------------------------------------------------------------------------------------------------------#
# --- Define Widgets (before resize_layout, but don't pack/place them on root) ---
# These widgets will be managed by main_canvas.create_window()

# Title Label
title_label = tk.Label(main_canvas, text="🌼 Welcome to Moodify! 🌼", font=("Segoe UI", 18, "bold"), bg="#fbe4ff", fg="#4A4A4A", pady=20)

# Outer frame (holds the framed instruction box)
outer_frame = tk.Frame(main_canvas, bg="#fbe4ff")

# Inner box frame with visible border (packed inside outer_frame)
box_frame = tk.Frame(outer_frame, bg="#FFEFE1", bd=3, relief="ridge")
box_frame.pack(fill="both", expand=True, padx=20, pady=10) # Fill the outer_frame

# Canvas inside the box (this is the one that contains the scrollable text)
instruction_canvas = tk.Canvas(box_frame, bg="#FFEFE1", highlightthickness=0)
instruction_canvas.pack(side="left", fill="both", expand=True)

# Scrollbar INSIDE the box
scrollbar = tk.Scrollbar(box_frame, orient="vertical", command=instruction_canvas.yview)
scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)

# Frame inside instruction_canvas for content
scrollable_frame = tk.Frame(instruction_canvas, bg="#FFEFE1")
instruction_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
instruction_canvas.configure(yscrollcommand=scrollbar.set)

# Auto scrollregion update
def update_scrollregion(event=None):
    # This might need to be called on outer_frame configure event or instruction_canvas resize
    instruction_canvas.configure(scrollregion=instruction_canvas.bbox("all"))
scrollable_frame.bind("<Configure>", update_scrollregion) # Bind to inner frame

# Bind mouse wheel to canvas (Windows and Linux) - global binding for root
root.bind_all("<MouseWheel>", on_mousewheel)
# Bind mouse wheel for macOS (uses different event name)
root.bind_all("<Button-4>", lambda event: instruction_canvas.yview_scroll(-1, "units"))
root.bind_all("<Button-5>", lambda event: instruction_canvas.yview_scroll(1, "units"))

# Instruction Text (using Text widget for styling)
instruction_text_widget = tk.Text(scrollable_frame, font=("Segoe UI", 13), bg="#FFF2E6", fg="#333333", wrap="word", padx=40, pady=20)
instruction_text_widget.pack(pady=(0, 20), fill="both", expand=True) # Ensure it expands within scrollable_frame

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
        "Oh — and there are *3 HIDDEN GAMES* inside the TV. Go find 'em 👀\n"
        "Press escape to exit the games window\n\n"
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

# Button frame (will be placed on main_canvas later)
button_frame = tk.Frame(main_canvas,bg="#fbe4ff")

start_button = ctk.CTkButton(button_frame,
    text="✨ Start Moodify ✨",
    font=("Segoe UI", 25, "bold"),
    fg_color="#B98EDC",
    hover_color="#9B59B6",
    text_color="#F2E6FF",
    corner_radius=35,
    height=60,
    command=start_game
)
start_button.pack(pady=(10,0)) # Pack inside button_frame

# Exit Button (will be placed on main_canvas later)
exit_button = ctk.CTkButton(
    main_canvas, # Parent set to main_canvas
    text="❌ Exit",
    font=("Segoe UI", 14),
    fg_color="#FF5151",
    hover_color="#FF6A6A",
    text_color="white",
    corner_radius=25,
    command=root.destroy
)

# Back to Top Button (will be placed on main_canvas later)
back_to_top_btn = ctk.CTkButton(
    main_canvas, # Parent set to main_canvas
    text="⬆ Back to Top",
    font=("Segoe UI", 14),
    fg_color="#48A9FF",
    hover_color="#6FC8FF",
    text_color="white",
    corner_radius=25,
    command=lambda: instruction_canvas.yview_moveto(0) # Ensure this scrolls the instruction_canvas
)

# Increase Font Button (will be placed on main_canvas later)
increase_font_button = ctk.CTkButton(
    main_canvas, # Parent set to main_canvas
    text="🔍 A+",
    font=("Segoe UI", 14),
    fg_color="#B0E0E6",
    hover_color="#87CEFA",
    text_color="black",
    command=increase_font_size,
    corner_radius=25,
    width=60
)

# Decrease Font Button (will be placed on main_canvas later)
decrease_font_button = ctk.CTkButton(
    main_canvas, # Parent set to main_canvas
    text="🔽 A-",
    font=("Segoe UI", 14),
    fg_color="#DDA0DD",
    hover_color="#DA70D6",
    text_color="black",
    command=decrease_font_size,
    corner_radius=25,
    width=60
)

#----------------------------------------------------------------------------------------------------------------------------------------------------------#
#alignment
# --- Define the responsive layout function ---
def resize_layout(event=None):
    global bg_photo_tk, bg_photo_id, title_window_id, outer_frame_window_id, button_frame_window_id, \
           exit_button_window_id, back_to_top_btn_window_id, \
           increase_font_button_window_id, decrease_font_button_window_id

    # Get current window dimensions
    current_width = root.winfo_width()
    current_height = root.winfo_height()

    if current_width == 1 or current_height == 1: # Avoid issues when minimizing window or before full rendering
        return

    # Resize background image to current window size
    resized_bg_image = bg_image_original.resize((current_width, current_height), Image.Resampling.LANCZOS)
    bg_photo_tk = ImageTk.PhotoImage(resized_bg_image) # Keep reference

    if bg_photo_id:
        main_canvas.itemconfig(bg_photo_id, image=bg_photo_tk) # Update existing image
    else:
        bg_photo_id = main_canvas.create_image(0, 0, image=bg_photo_tk, anchor="nw") # Create if first time

    # --- Position and Size Widgets Dynamically ---

    # Title Label
    rel_title_y = 0.05 # 5% from the top
    title_x = current_width / 2
    title_y = current_height * rel_title_y
    if title_window_id:
        main_canvas.coords(title_window_id, title_x, title_y)
    else:
        title_label.update_idletasks() # Ensure widget has calculated its initial size
        title_window_id = main_canvas.create_window(title_x, title_y, window=title_label, anchor="n")

    # Outer Frame (Instruction Box Container)
    rel_outer_frame_width = 0.8 # 80% of screen width
    rel_outer_frame_height = 0.6 # 60% of screen height
    outer_frame_abs_width = int(current_width * rel_outer_frame_width)
    outer_frame_abs_height = int(current_height * rel_outer_frame_height)
    outer_frame_x = (current_width - outer_frame_abs_width) / 2 # Center horizontally
    rel_outer_frame_y = 0.15 # 15% from the top
    outer_frame_y = current_height * rel_outer_frame_y

    if outer_frame_window_id:
        main_canvas.coords(outer_frame_window_id, outer_frame_x, outer_frame_y)
        main_canvas.itemconfigure(outer_frame_window_id, width=outer_frame_abs_width, height=outer_frame_abs_height)
    else:
        outer_frame.update_idletasks()
        outer_frame_window_id = main_canvas.create_window(outer_frame_x, outer_frame_y, window=outer_frame, anchor="nw",
                                                          width=outer_frame_abs_width, height=outer_frame_abs_height)

    # Button Frame (Start Button Container)
    rel_button_frame_width = 0.5
    button_frame_abs_width = int(current_width * rel_button_frame_width)
    button_frame_height = 100 # Fixed height, or make it relative too if needed
    
    # Correct X: For anchor="n" (top-center), the X should be the horizontal center of the canvas.
    button_frame_x = current_width / 2

    visual_horizontal_offset = 0 # Experiment with this value (e.g., 5, 10, 15, 20)
    button_frame_x += visual_horizontal_offset

    rel_button_frame_y = 0.85 # 85% from the top (or 15% from bottom)
    button_frame_y = current_height * rel_button_frame_y

    if button_frame_window_id:
        main_canvas.coords(button_frame_window_id, button_frame_x, button_frame_y)
        main_canvas.itemconfigure(button_frame_window_id, width=button_frame_abs_width, height=button_frame_height)
    else:
        button_frame.update_idletasks()
        button_frame_window_id = main_canvas.create_window(button_frame_x, button_frame_y, window=button_frame, anchor="n",
                                                           width=button_frame_abs_width, height=button_frame_height)

    # Exit Button
    rel_exit_x = 0.97
    rel_exit_y = 0.07
    exit_x = current_width * rel_exit_x
    exit_y = current_height * rel_exit_y
    if exit_button_window_id:
        main_canvas.coords(exit_button_window_id, exit_x, exit_y)
    else:
        exit_button.update_idletasks()
        exit_button_window_id = main_canvas.create_window(exit_x, exit_y, window=exit_button, anchor="ne")

    # Back to Top Button
    rel_back_to_top_x = 0.97
    rel_back_to_top_y = 0.84
    back_to_top_x = current_width * rel_back_to_top_x
    back_to_top_y = current_height * rel_back_to_top_y
    if back_to_top_btn_window_id:
        main_canvas.coords(back_to_top_btn_window_id, back_to_top_x, back_to_top_y)
    else:
        back_to_top_btn.update_idletasks()
        back_to_top_btn_window_id = main_canvas.create_window(back_to_top_x, back_to_top_y, window=back_to_top_btn, anchor="se")

    # Font Size Increase Button
    rel_increase_font_x = 0.10
    rel_increase_font_y = 0.78
    increase_font_x = current_width * rel_increase_font_x
    increase_font_y = current_height * rel_increase_font_y
    if increase_font_button_window_id:
        main_canvas.coords(increase_font_button_window_id, increase_font_x, increase_font_y)
    else:
        increase_font_button.update_idletasks()
        increase_font_button_window_id = main_canvas.create_window(increase_font_x, increase_font_y, window=increase_font_button, anchor="nw")

    # Font Size Decrease Button
    rel_decrease_font_x = 0.04
    rel_decrease_font_y = 0.78
    decrease_font_x = current_width * rel_decrease_font_x
    decrease_font_y = current_height * rel_decrease_font_y
    if decrease_font_button_window_id:
        main_canvas.coords(decrease_font_button_window_id, decrease_font_x, decrease_font_y)
    else:
        decrease_font_button.update_idletasks()
        decrease_font_button_window_id = main_canvas.create_window(decrease_font_x, decrease_font_y, window=decrease_font_button, anchor="nw")

    # IMPORTANT: After resizing, ensure the instruction_canvas's scrollregion is updated
    # This is critical for scrolling to work correctly after a resize.
    instruction_canvas.update_idletasks() # Ensures scrollable_frame has correct size
    instruction_canvas.configure(scrollregion=instruction_canvas.bbox("all"))

#----------------------------------------------------------------------------------------------------------------------------------------------------------#
# Track fullscreen state
is_fullscreen = [False] # Using a list to allow modification within function scope

def toggle_fullscreen(event=None):
    current_fullscreen_state = root.attributes("-fullscreen")
    if current_fullscreen_state: # Currently fullscreen, exit fullscreen
        root.attributes("-fullscreen", False)
        target_width = 1280
        target_height = 720
        
        # Calculate center coordinates for the target size
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        center_x = (screen_width - target_width) // 2
        center_y = (screen_height - target_height) // 2
        
        root.geometry(f"{target_width}x{target_height}+{center_x}+{center_y}")
    else:
        root.attributes("-fullscreen", True)
    
    is_fullscreen[0] = not current_fullscreen_state # Update state tracker
    # After toggling fullscreen, force a layout update to ensure elements reposition correctly
    root.update_idletasks() # Ensure window size is updated
    resize_layout() # Call resize_layout to adjust elements

root.bind("<Control-f>", toggle_fullscreen)

# --- Initial calls after all widgets are defined but before mainloop ---
# Set the window to fullscreen initially
root.attributes("-fullscreen", True)
# Update idletasks to ensure the window's dimensions are correct after fullscreen is set
root.update_idletasks()
# Call resize_layout once to set up the initial responsive layout
resize_layout()

def start_bob_safe():
    root.update_idletasks() # Ensure widget is fully rendered
    if start_button.winfo_exists() and start_button.winfo_ismapped():
        # Initialize current_bob_pady to its base value (10) for the bobbing animation start
        global current_bob_pady
        current_bob_pady = bob_initial_pady
        bob_packed_widget(start_button)
    else:
        # If not ready, retry after a short delay
        root.after(100, start_bob_safe)

root.after(500, start_bob_safe) # Start animation after the window has had some time to render

# Run the app
root.mainloop()