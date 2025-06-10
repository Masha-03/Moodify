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

mood_quotes = {
    "Happy": "Keep shining, the world needs your light!",
    "Sad": "It's okay to be not okay. Better days are coming.",
    "Angry": "Breathe deeply. Stay calm. You're in control.",
    "Excited": "Your excitement is the spark for amazing things!",
    "Sleepy": "Rest well — even dreams need time to grow.",
    "Relaxed": "Peace of mind is the best kind of success."
}

#--------------------------------------------------------------masha---------------------------------------------------------------------------------# 

def get_db_path():
    base_dir = None
    if getattr(sys, 'frozen', False):
        # When frozen (e.g., PyInstaller), sys._MEIPASS is the root where bundled files are.
        # If your 'database' folder is alongside the executable in the *final distributed package*,
        # you might need to adjust this depending on your PyInstaller --add-data configuration.
        # For now, let's assume the database folder is at the same level as the executable.
        app_root = sys._MEIPASS
    else:
        # In unfrozen mode, base_dir is 'c:\Users\Coshi\Moodify\tkinter pages'.
        # We need to go up one level to 'c:\Users\Coshi\Moodify'.
        script_dir = os.path.dirname(os.path.abspath(__file__)) # This is 'c:\Users\Coshi\Moodify\tkinter pages'
        app_root = os.path.dirname(script_dir) # This steps up to 'c:\Users\Coshi\Moodify'

    db_file_name = 'moodify_database.db'
    db_folder_name = 'database'

    # Now, join the app_root with the database folder and the file name
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
    print("WARNING: A new database file will likely be created here.")
    # Create the 'database' folder if it doesn't exist
    try:
        os.makedirs(os.path.dirname(database_file_path), exist_ok=True)
        print(f"Created directory: {os.path.dirname(database_file_path)}")
    except OSError as e:
        print(f"Error creating directory: {e}")

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
    root.configure(bg="#fdf6f0")
    title.configure(bg="#fdf6f0")
    ask_user_label.configure(bg="#fdf6f0")
    label.configure(bg="#fdf6f0")
    frame_button.configure(bg="#FCF8E8")
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
    root.configure(bg=bg_colour)
    title.configure(bg=bg_colour)
    ask_user_label.configure(bg=bg_colour)
    label.configure(bg=bg_colour)
    text_entry.configure(bg="white", fg="#000")  #keep text box simple
    frame_button.configure(bg=bg_colour)
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
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}") #full-screen size
root.title("Mood Tracker")
root.configure(bg="#fdf6f0") 

#----------------------------------------------------------------------------------------------------------------------------------------------------#

title=tk.Label(root,text="Mood Tracker⭐", font=("Helvetica", 18, "bold"),bg="#fdf6f0",fg="#333")
title.pack(pady=10)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#some sentence to ask about users' current mood
ask_user=["How are you feeling today?",
          "How do you feel today?",
          "How's your mood today?",
          "What are you feeling right now?"]
random_ask_user=random.choice(ask_user) #computer will random display the question
print(random_ask_user) #print the sentence

#label to display the ask_user sentences
ask_user_label=tk.Label(root,text=random_ask_user, font=("Comic Sans MS",15),bg="#fdf6f0", fg="#555", wraplength=800) #wraplength=control text wrapping,will break the text into new line once it reaches specific pixel width.
ask_user_label.pack(pady=(10,10))

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#create frame to hold emoji button and centre them
frame_button=tk.Frame(root,bg="#FCF8E8")
frame_button.pack(pady=20)

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
button_happy=tk.Button(frame_button, image=happy_image, bg="#ffe0e0", relief="flat", command=lambda:set_mood("Happy")) #command=lambda is to bind a function to button/expression 
button_sad=tk.Button(frame_button, image=sad_image, bg="#ffe0e0", relief="flat", command=lambda:set_mood("Sad"))       #when button clicked lambda calls set_mood("") function
button_angry=tk.Button(frame_button, image=angry_image, bg="#ffe0e0", relief="flat", command=lambda:set_mood("Angry")) #flat=has no 3D effect
button_excited=tk.Button(frame_button, image=excited_image, bg="#ffe0e0", relief="flat", command=lambda:set_mood("Excited"))
button_sleepy=tk.Button(frame_button, image=sleepy_image, bg="#ffe0e0", relief="flat", command=lambda:set_mood("Sleepy"))
button_relaxed=tk.Button(frame_button, image=relaxed_image, bg="#ffe0e0", relief="flat", command=lambda:set_mood("Relaxed"))

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
text_entry=tk.Text(root,font=("Comic Sans MS",12), height=13, width=70, bd=2, relief="groove", highlightthickness=1, highlightbackground="#ccc")
text_entry.pack()

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#Add a instruction label for users
label=tk.Label(root,text="Choose a button or describe your mood inside the blank box.",font=("Comic Sans MS",11),bg="#fdf6f0",fg="#777")
label.pack(pady=(7,5))      

#----------------------------------------------------------------------------------------------------------------------------------------------------#
word_count_label = tk.Label(root, text="Words: 0", font=("Comic Sans MS", 10), bg="#fdf6f0", fg="#555")
word_count_label.pack()

text_entry.bind("<KeyRelease>", update_word_count)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#

#save Button to save the mood
save_button = tk.Button(root, text="Save Mood", font=("Comic Sans MS", 12), bg="white", relief="groove", command=save_mood)
save_button.pack(pady=10)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#global variable to store users' selected mood
selected_mood = ""

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#Track fullscreen state
is_fullscreen = [False]

# Toggle fullscreen using the 'f' key
def toggle_fullscreen(event=None):
    is_fullscreen[0] = not is_fullscreen[0]
    root.attributes("-fullscreen", is_fullscreen[0])

# Bind the 'f' key (lowercase only)
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
exit_button.place(relx=0.97, rely=0.04, anchor="ne")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

clear_button = ctk.CTkButton(root, text="Clear Entry", font=("Segoe UI", 14), hover_color="#FFA9FF", text_color="black",fg_color="#ffd3d3", corner_radius=25,command=clear_entry)
clear_button.place(relx=0.03, rely=0.13, anchor="w")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

timestamp_button = ctk.CTkButton(root, text="Insert Timestamp",fg_color="#ffadad", hover_color="#F7CDFF", font=("Segoe UI", 14),text_color="black", corner_radius=25,command=insert_timestamp)
timestamp_button.place(relx=0.03, rely=0.08, anchor="w")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

help_button = ctk.CTkButton(root, text="❓ Help", font=("Segoe UI", 14), fg_color="#5A9BD5", hover_color="#7AB8FF", text_color="white", corner_radius=25, command=show_help)
help_button.place(relx=0.97, rely=0.09, anchor="ne")
#--------------------------------------------------------------------------------------------------------------------------------------------------------#

#run the whole program
root.mainloop()


