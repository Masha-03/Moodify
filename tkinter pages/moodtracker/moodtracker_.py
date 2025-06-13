import tkinter as tk
import random #for ask_user
from tkinter import messagebox #for show pop-up message
from PIL import Image,ImageTk #import pillow for image resizing
import datetime
import sqlite3
import os
import customtkinter as ctk
import sys
import datetime

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

mood_quotes = {
    "Happy": "Keep shining, the world needs your light!",
    "Sad": "It's okay to be not okay. Better days are coming.",
    "Angry": "Breathe deeply. Stay calm. You're in control.",
    "Excited": "Your excitement is the spark for amazing things!",
    "Sleepy": "Rest well — even dreams need time to grow.",
    "Relaxed": "Peace of mind is the best kind of success."
}

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Global variables for responsive layout and fullscreen management
resize_job_id = None # For debouncing the resize event
last_width = 1280 # Default non-fullscreen width
last_height = 720 # Default non-fullscreen height
last_x = None # Will store the x position
last_y = None # Will store the y position
is_fullscreen = [True] # Start in fullscreen
#--------------------------------------------------------------masha---------------------------------------------------------------------------------# 

def get_db_path():
    db_file_name = 'moodify_database.db'
    db_folder_name = 'database'

    if getattr(sys, 'frozen', False):
        app_root = sys._MEIPASS
    else:
        #Running in a normal Python environment (unfrozen)
        script_dir = os.path.dirname(os.path.abspath(__file__))


        #Need to go up two levels
        #From 'mood tracker' to 'tkinter pages'
        #From 'tkinter pages' to 'Moodify'
        intermediate_dir = os.path.dirname(script_dir) 
        app_root = os.path.dirname(intermediate_dir) 

    #Join the app_root with the database folder and the file name
    db_path = os.path.join(app_root, db_folder_name, db_file_name)

    print(f"Running in {'frozen' if getattr(sys, 'frozen', False) else 'unfrozen'} mode.")
    print(f"Detected script directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Calculated application root: {app_root}")
    print(f"Calculated database path: {db_path}")

    return db_path

database_file_path = get_db_path()

# Check if the database file exists at the calculated path
if os.path.exists(database_file_path):
    print(f"Database file FOUND at: {database_file_path}")
else:
    print(f"Database file NOT FOUND at: {database_file_path}")

#Get profile from the database
def get_profile():
    global profile
    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()
    
    #Fetch the profile
    cursor.execute("SELECT profile FROM user_info ORDER BY ROWID DESC LIMIT 1") #Fetch latest profile
    result = cursor.fetchone()
    
    connect.close() #Close connection
    if result:
        profile = result[0]  # Store the profile 
    else:
        profile = None  # Set profile to None if no profile found

#Initialise table
def initialise_table(): 
        #Connect to database
        connect = sqlite3.connect(database_file_path)
        #Create cursor
        cursor = connect.cursor()
        
        #Create the diary_entries table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile TEXT,
            date DATE,
            time TEXT,
            mood TEXT,
            mood_description TEXT,
            FOREIGN KEY (profile) REFERENCES user_info(profile)
        )
        ''')
        
        #Save data, update
        connect.commit()
        #Close connection
        connect.close()
        
#Initialise table before GUI starts        
initialise_table()  

#------------------------------------------------------masha---------------------------------------------------------------------------------------------#

#function to save mood
def save_mood():
    global selected_mood
    get_profile()
    if selected_mood:
        mood_desc = text_entry.get("1.0", tk.END).strip()
        if not mood_desc:
            mood_desc = "No description."

        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d") #Get date
        current_time = now.strftime("%H:%M:%S") #Get time

        # Insert into database
        conn = sqlite3.connect(database_file_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO mood_entries (profile, date, time, mood, mood_description)
            VALUES (?, ?, ?, ?, ?)
        ''', (profile, current_date, current_time, selected_mood, mood_desc))

        conn.commit()
        conn.close()

        #Show popup after submit
        quote = mood_quotes.get(selected_mood, "No quote available.")
        messagebox.showinfo("Mood Saved!", f"Mood: {selected_mood}\n{quote}")

        #Reset entry
        text_entry.delete(1.0, tk.END)
        selected_mood = ""
    else:
        messagebox.showwarning("No Mood Selected", "Please select a mood before saving.")
        
#----------------------------------------------------------------------------------------------------------------------------------------------------#
def clear_entry():
    text_entry.delete("1.0", "end")
    global selected_mood
    selected_mood = ""
    # Optionally reset background to default
    current_bg_color = "#fdf6f0"
    main_canvas.configure(bg=current_bg_color) # Update main_canvas background
    title.configure(bg=current_bg_color)
    ask_user_label.configure(bg=current_bg_color)
    label.configure(bg=current_bg_color)
    frame_button.configure(bg="#FCF8E8")
    emoji_buttons_inner_frame.configure(bg="#FCF8E8")
    word_count_label.configure(bg=current_bg_color)
    for button in emoji_buttons:
        button.configure(bg="#ffe0e0")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def show_help():
    messagebox.showinfo("Help", "Select your mood by clicking an emoji or type your mood in the box. You can press the *Insert Timestamp* button to insert current time. Then click 'Save Mood'. Press Ctrl+F to toggle fullscreen.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def update_word_count(event=None):
    text = text_entry.get("1.0", "end").strip()
    words = len(text.split()) if text else 0
    word_count_label.config(text=f"Words: {words}")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def insert_timestamp():
    now = datetime.datetime.now().strftime("%B %d, %Y")
    text_entry.insert(tk.END, f"\n[{now}] ")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#function to handle the button click
def set_mood(mood):
    global selected_mood
    selected_mood = mood #save clicked mood button
    
    if mood=="Happy":
        bg_colour="#fff9c4"
        btn_colour="#ffe082"
    elif mood=="Sad":
        bg_colour="#cfd8dc"
        btn_colour="#90a4ae"
    elif mood=="Angry":
        bg_colour="#ffcdd2"
        btn_colour="#ef9a9a"
    elif mood=="Excited":
        bg_colour="#ffe0b2"
        btn_colour="#ffb74d"
    elif mood=="Sleepy":
        bg_colour="#e1f5fe"
        btn_colour="#81d4fa"
    elif mood=="Relaxed":
        bg_colour="#dcedc8"
        btn_colour="#aed581"
    else:
        bg_colour="#fdf6f0"
        btn_colour="#f8c9c9"

    #Update background & text colors
    main_canvas.configure(bg=bg_colour)
    title.configure(bg=bg_colour)
    ask_user_label.configure(bg=bg_colour)
    label.configure(bg=bg_colour)
    text_entry.configure(bg="white", fg="#000")
    frame_button.configure(bg=bg_colour)
    emoji_buttons_inner_frame.configure(bg=bg_colour)
    word_count_label.configure(bg=bg_colour)

    #update all buttons to match the theme
    for button in emoji_buttons:
        button.configure(bg=btn_colour)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Get current file directory
base_dir = os.path.dirname(__file__)

# Build image paths safely
def get_image_path(filename):
    return os.path.join(base_dir, filename)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Resize image using PIL
def resize_image(image_path, size=(50, 50)):
    img = Image.open(image_path)
    img = img.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#main window
root=tk.Tk()
root.attributes("-fullscreen", True) # Start in true fullscreen
root.title("Mood Tracker")
root.configure(bg="#fdf6f0") 

# --- Main Canvas to manage all UI elements for responsive layout ---
# All other widgets will be placed inside this canvas.
main_canvas = tk.Canvas(root, highlightthickness=0, bg="#fdf6f0")
main_canvas.pack(fill="both", expand=True) # Canvas fills the entire root window
#----------------------------------------------------------------------------------------------------------------------------------------------------#

title=tk.Label(main_canvas,text="Mood Tracker⭐", font=("Helvetica", 18, "bold"),bg="#fdf6f0",fg="#333")

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#some sentence to ask about users' current mood
ask_user=["How are you feeling today?",
          "How do you feel today?",
          "How's your mood today?",
          "What are you feeling right now?"]
random_ask_user=random.choice(ask_user) #computer will random display the question

#label to display the ask_user sentences
ask_user_label=tk.Label(main_canvas,text=random_ask_user, font=("Comic Sans MS",15),bg="#fdf6f0", fg="#555", wraplength=800) #wraplength=control text wrapping,will break the text into new line once it reaches specific pixel width.
#----------------------------------------------------------------------------------------------------------------------------------------------------#

#create frame to hold emoji button and centre them
frame_button=tk.Frame(main_canvas,bg="#FCF8E8")

# This inner frame will be packed with expand=True, which centers its contents.
emoji_buttons_inner_frame = tk.Frame(frame_button, bg=frame_button.cget('bg'))
emoji_buttons_inner_frame.pack(fill="none",expand=True,anchor="center") # This centers the inner frame horizontally within frame_button

#list of emoji buttons
emoji_buttons=[]

# Load images using relative paths
happy_image = resize_image(get_image_path("happy.png"))
sad_image = resize_image(get_image_path("sad.png"))
angry_image = resize_image(get_image_path("angry.png"))
excited_image = resize_image(get_image_path("excited.png"))
sleepy_image = resize_image(get_image_path("sleepy.png"))
relaxed_image = resize_image(get_image_path("relaxed.png"))


#button to choose the mood
button_happy=tk.Button(emoji_buttons_inner_frame, image=happy_image, bg="#ffe0e0", relief="flat", command=lambda:set_mood("Happy")) #command=lambda is to bind a function to button/expression 
button_sad=tk.Button(emoji_buttons_inner_frame, image=sad_image, bg="#ffe0e0", relief="flat", command=lambda:set_mood("Sad"))       #when button clicked lambda calls set_mood("") function
button_angry=tk.Button(emoji_buttons_inner_frame, image=angry_image, bg="#ffe0e0", relief="flat", command=lambda:set_mood("Angry")) #flat=has no 3D effect
button_excited=tk.Button(emoji_buttons_inner_frame, image=excited_image, bg="#ffe0e0", relief="flat", command=lambda:set_mood("Excited"))
button_sleepy=tk.Button(emoji_buttons_inner_frame, image=sleepy_image, bg="#ffe0e0", relief="flat", command=lambda:set_mood("Sleepy"))
button_relaxed=tk.Button(emoji_buttons_inner_frame, image=relaxed_image, bg="#ffe0e0", relief="flat", command=lambda:set_mood("Relaxed"))

#add all buttons to the list
emoji_buttons.extend([
    button_happy, button_sad, button_angry,
    button_excited, button_sleepy, button_relaxed
])

#place the emoji button to make it align horizontally
button_happy.pack(side="left", padx=20)
button_sad.pack(side="left", padx=20)
button_angry.pack(side="left", padx=20)
button_excited.pack(side="left", padx=20)
button_sleepy.pack(side="left", padx=20)
button_relaxed.pack(side="left", padx=20)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#blank text area for user to input something
text_entry=tk.Text(main_canvas,font=("Comic Sans MS",12), height=13, width=70, bd=2, relief="groove", highlightthickness=1, highlightbackground="#ccc")

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#Add a instruction label for users
label=tk.Label(main_canvas,text="Choose a button or describe your mood inside the blank box.",font=("Comic Sans MS",11),bg="#fdf6f0",fg="#777")    

#----------------------------------------------------------------------------------------------------------------------------------------------------#
word_count_label = tk.Label(main_canvas, text="Words: 0", font=("Comic Sans MS", 10), bg="#fdf6f0", fg="#555")

text_entry.bind("<KeyRelease>", update_word_count)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#

#save Button to save the mood
save_button = tk.Button(root, text="Save Mood", font=("Comic Sans MS", 12), bg="white", relief="groove", command=save_mood)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#global variable to store users' selected mood
selected_mood = ""

#----------------------------------------------------------------------------------------------------------------------------------------------------#
# Function to toggle fullscreen mode
def toggle_fullscreen(event=None):
    global last_width, last_height, last_x, last_y, is_fullscreen

    if is_fullscreen[0]: # Currently fullscreen, going to non-fullscreen
        root.attributes("-fullscreen", False)
        # Restore to last known non-fullscreen size and position
        if last_x is not None and last_y is not None:
             root.geometry(f"{last_width}x{last_height}+{last_x}+{last_y}")
        else: # Fallback to a default size (centered roughly)
            # If no non-fullscreen size was ever stored (e.g., app started fullscreen)
            # Set to the desired default non-fullscreen size (1280x720)
            target_width = 1280  # Force 1280
            target_height = 720  # Force 720

            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            # Center the window based on the desired target size
            center_x = (screen_width - target_width) // 2
            center_y = (screen_height - target_height) // 2
            
            root.geometry(f"{target_width}x{target_height}+{center_x}+{center_y}")
            
            # Store these values for subsequent toggles
            last_width = target_width
            last_height = target_height
            last_x = center_x
            last_y = center_y


    else: # Currently non-fullscreen, going to fullscreen
        # Store current window geometry BEFORE going fullscreen
        last_width = root.winfo_width()
        last_height = root.winfo_height()
        last_x = root.winfo_x()
        last_y = root.winfo_y()
        root.attributes("-fullscreen", True)

    is_fullscreen[0] = not is_fullscreen[0]
    # Immediately re-layout after fullscreen toggle
    _perform_resize_layout()

# Function to perform the actual layout adjustments
def _perform_resize_layout(event=None):
    global resize_job_id
    
    current_canvas_width = main_canvas.winfo_width()
    current_canvas_height = main_canvas.winfo_height()

    if current_canvas_width == 1 or current_canvas_height == 1: # Avoid division by zero or tiny windows
        return

    # Place elements using relative coordinates and sizes on main_canvas
    # These values are carefully chosen percentages to maintain visual balance.
    title.place(relx=0.5, rely=0.04, anchor="n")
    ask_user_label.place(relx=0.5, rely=0.10, anchor="n", relwidth=0.8)
    
    # Adjust wraplength for text labels dynamically based on their relative width
    ask_user_label.config(wraplength=int(current_canvas_width * 0.75)) # 75% of its relwidth

    frame_button.place(relx=0.5, rely=0.20, anchor="n", relwidth=0.9, relheight=0.1) # Relative size for the emoji frame
    # Note: The emoji buttons inside `frame_button` use `pack`, which is fine,
    # as `frame_button` itself is now responsively placed.

    text_entry.place(relx=0.5, rely=0.35, anchor="n", relwidth=0.7, relheight=0.4)

    label.place(relx=0.5, rely=0.76, anchor="n")
    word_count_label.place(relx=0.5, rely=0.80, anchor="n")
    save_button.place(relx=0.5, rely=0.87, anchor="n")

    # Position side buttons (Exit, Clear, Timestamp, Help) relative to main_canvas
    exit_button.place(relx=0.97, rely=0.04, anchor="ne")
    clear_button.place(relx=0.03, rely=0.13, anchor="w")
    timestamp_button.place(relx=0.03, rely=0.08, anchor="w")
    help_button.place(relx=0.97, rely=0.09, anchor="ne")


# Debouncing function to prevent excessive calls during resizing
def resize_layout(event=None):
    global resize_job_id
    if resize_job_id:
        root.after_cancel(resize_job_id)
    resize_job_id = root.after(50, _perform_resize_layout) # Schedule _perform_resize_layout after 50ms

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
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

clear_button = ctk.CTkButton(main_canvas, text="Clear Entry", font=("Segoe UI", 14), hover_color="#FFA9FF", text_color="black",fg_color="#ffd3d3", corner_radius=25,command=clear_entry)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

timestamp_button = ctk.CTkButton(main_canvas, text="Insert Timestamp",fg_color="#ffadad", hover_color="#F7CDFF", font=("Segoe UI", 14),text_color="black", corner_radius=25,command=insert_timestamp)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

help_button = ctk.CTkButton(main_canvas, text="❓ Help", font=("Segoe UI", 14), fg_color="#5A9BD5", hover_color="#7AB8FF", text_color="white", corner_radius=25, command=show_help)

#--------------------------------------------------------------------------------------------------------------------------------------------------------#

# --- Initial setup calls ---
# Bind the 'f' key (lowercase only) for fullscreen toggle
root.bind("<Control-f>", toggle_fullscreen)

# Bind the main layout update function to the root window's Configure event
# This means _perform_resize_layout will run whenever the window is resized.
root.bind("<Configure>", resize_layout)

# Initial call to set up the layout after all widgets are created
# A small delay ensures the window has initialized its dimensions
root.after(100, _perform_resize_layout)


#run the whole program
root.mainloop()

