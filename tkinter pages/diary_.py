import tkinter as tk
import random
from datetime import datetime #to get current date and time
from tkinter import messagebox #for show pop-up message
import requests #getting data from API
import tkinter.font as tkfont #use to import font module from tkinter library
import sqlite3
import os
from PIL import Image, ImageTk
import os
import sys
import customtkinter as ctk
from datetime import datetime
from tkinter import simpledialog,messagebox

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

#----------------------------------------------------------------------------------------------------------------------------------------------------#
#for alignment
#Global variables for canvas items (background)
bg_photo_tk = None
bg_photo_id = None
#----------------------------------------------------------------------------------------------------------------------------------------------------#

#counts how many words are in the diary
def word_count(event=None): #event=None:means it can be called with/without event
    content = text_entry.get("1.0", "end-1c")  #get full text from text widget #1.0=start from line 1,character 0(very beginning) #end-1c=means up to one character before the end 
    words = content.split() #split the entire string into a list of words
    word_count = len(words) #len(words)=count how many words in the list #len=return the length of something
    word_count_label.config(text=f"{word_count} words") #update the label

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#function for the weather
def get_weather():
    api_key= "84fef18519a48ec1188bd03abd5494e5" #the api key from OpenWeatherApp #without api key,api will reject your requests
    city= "Kuala Lumpur"
    url= f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric" #units=metric:return temperature in celsius,wind speed in meters/second #to request weather data

    try:
        response = requests.get(url) #format used to send a get request to the specific URL #it try to connect openweather's server and download the data
        data = response.json()#takes weather data from internet(which come in a format-JSON) and change it into python dictionary,so can read and use the information easily

        if data["cod"] == 200: #"cod"=code #200=success
            temp = data["main"]["temp"] #data"main"=a dictionary that contain temperature and other weather details #"temp"=give the current temperature
            weather = data["weather"][0]["description"].capitalize() #data"weather"=give a list of weather condition #0=get the first item in the list #description=is like:"rain","clear sky"
            return f"{weather}, {temp}°C" #here display what user see #returns a formatted string combining both values 
        else:  #if cod not equal to 200,then display
            return "Failed to load weather"
    except: #if something breaks
        return "Error fetching weather" #catches any unexpected error

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#function to refresh the prompts
def refresh_prompts():
    new_prompt=random.choice(writing_prompts)
    promts_label.config(text=new_prompt)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#function for update the font
def update_font():
    chosen_font = selected_font.get()
    text_entry.configure(font=(chosen_font, 12))
    smalltitle_entry.configure(font=(chosen_font,12)) #let the smalltitle can change the font too

#----------------------------------------------------------------------------------------------------------------------------------------------------#
#function for clear entry
def clear_entry():
    text_entry.delete("1.0", "end")
    smalltitle_entry.delete(0, "end")
    word_count_label.config(text="0 words")

#----------------------------------------------------------------------------------------------------------------------------------------------------#    
def show_help():
    messagebox.showinfo("Help", "Write your diary entry, choose a font, and click Save. Press Ctrl+F to toggle fullscreen.")

#----------------------------------------------------------------------------------------------------------------------------------------------------#
#auto save reminder
def auto_save_reminder():
    messagebox.showinfo("Reminder", "Don't forget to save your diary entry!")
    root.after(600000, auto_save_reminder)  # every 10 minutes

#----------------------------------------------------------------------------------------------------------------------------------------------------#

def insert_timestamp():
    now = datetime.now().strftime("%B %d, %Y")
    text_entry.insert(tk.END, f"\n[{now}] ")

#--------------------------------------------------------------masha---------------------------------------------------------------------------------# 

def get_db_path():
    base_dir = None
    if getattr(sys, 'frozen', False):
        #Database folder is at the same level as the executable.
        app_root = sys._MEIPASS
    else:
        #In unfrozen mode
        script_dir = os.path.dirname(os.path.abspath(__file__)) 
        app_root = os.path.dirname(script_dir) 

    db_file_name = 'moodify_database.db'
    db_folder_name = 'database'

    #Join the app_root with the database folder and the file name
    db_path = os.path.join(app_root, db_folder_name, db_file_name)

    print(f"Running in {'frozen' if getattr(sys, 'frozen', False) else 'unfrozen'} mode.")
    print(f"Detected script directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Calculated application root: {app_root}")
    print(f"Calculated database path: {db_path}")

    return db_path

database_file_path = get_db_path()

#Check if the database file exists at the calculated path
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diary_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile TEXT,
                date DATE,
                time TEXT,
                title TEXT,
                content TEXT,
                FOREIGN KEY (profile) REFERENCES user_info(profile)
            )
        """)
        
        #Save data, update
        connect.commit()
        #Close connection
        connect.close()
        
#Initialise table before GUI starts        
initialise_table()  

#Function to save diary entry with profile
def save_entry():
    get_profile() #Retrieve profile
    #If no profile found
    if not profile:
        messagebox.showwarning("No Profile", "No active profile found. Please set up a profile.")
        return
    
    #Get user input
    diary_text = text_entry.get("1.0", "end-1c") #Get diary content text
    title_text = smalltitle_entry.get().strip() #Get title text
    current_date = datetime.now().strftime("%Y-%m-%d") #Get current date
    current_time = datetime.now().strftime("%H:%M:%S")  #Get current time

    # Database connection
    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()

    #Check for any empty field
    if not title_text or not diary_text: 
            #Warning box
            messagebox.showwarning("Incomplete Information", "Please fill in both Title and Diary Content")
            return

    # Save the diary entry
    cursor.execute('''
        INSERT INTO diary_entries (profile, date, time, title, content)
        VALUES (?, ?, ?, ?, ?)
    ''', (profile, current_date, current_time, title_text, diary_text))
    
    #Save data, update
    connect.commit()
    messagebox.showinfo("Saved!", "Your diary entry has been saved.")

    #Clear text entry after saving
    text_entry.delete("1.0", "end")
    smalltitle_entry.delete(0, "end")
    #reset the word count to 0 word
    word_count_label.config(text="0 words")

    #Close connection
    connect.close()

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#main window
root=tk.Tk()
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}") #Full-screen size
root.title("Diary📖")
root.configure(bg="#fdf6f0")
#----------------------------------------------------------------------------------------------------------------------------------------------------#
# --- Main Canvas for Background ---
main_canvas = tk.Canvas(root, highlightthickness=0, bg="#fdf6f0")
main_canvas.pack(fill="both", expand=True)

# Load and set background image
base_dir = os.path.dirname(os.path.abspath(__file__)) 
bg_image_path = os.path.join(base_dir, "diary_bg.png") 
try:
    bg_image_original = Image.open(bg_image_path)
except FileNotFoundError:
    messagebox.showerror("Error", f"Background image not found: {bg_image_path}")
    root.destroy()
    sys.exit()

#---------------------------------------------------------------------------------------------------------------------------------#
#for alignment
def resize_layout(event=None):
    global bg_photo_tk, bg_photo_id

    current_width = root.winfo_width() # Use root's width, as canvas fills root
    current_height = root.winfo_height()

    if current_width == 1 or current_height == 1:
        return

    # 1. Resize and place background image on main_canvas
    resized_bg_image = bg_image_original.resize((current_width, current_height), Image.Resampling.LANCZOS)
    bg_photo_tk = ImageTk.PhotoImage(resized_bg_image)

    if bg_photo_id:
        main_canvas.itemconfig(bg_photo_id, image=bg_photo_tk)
    else:
        bg_photo_id = main_canvas.create_image(0, 0, image=bg_photo_tk, anchor="nw")
    main_canvas.tag_lower(bg_photo_id) # Ensure background is at the lowest layer

    # --- Responsive Positioning for Main UI Elements using .place() on root ---
    # Values adjusted for a balanced look. Feel free to tweak these percentages.

    # Title label
    title.place(relx=0.5, rely=0.03, anchor="n") # Centered, slightly from top

    # Prompts frame (holds prompt label and refresh button)
    prompts_frame.place(relx=0.5, rely=0.1, relwidth=0.7, height=80, anchor="n") # Centered, width 70%, fixed height
    # Label and button inside prompts_frame remain packed within it.

    # Info frame (holds date and weather)
    info_frame.place(relx=0.5, rely=0.19, relwidth=0.5, height=30, anchor="n") # Centered, width 50%, fixed height

    # Small title frame (holds title label and entry)
    smalltitle_frame.place(relx=0.5, rely=0.23, relwidth=0.6, height=30, anchor="n") # Centered, width 60%, fixed height

    # Font selection frame (holds font options, clear, timestamp buttons)
    font_frame.place(relx=0.5, rely=0.27, relwidth=0.6, height=40, anchor="n") # Centered, width 60%, fixed height

    # Main text entry frame
    text_frame.place(relx=0.5, rely=0.33, relwidth=0.6, relheight=0.45, anchor="n") # Centered, width 60%, height 45%

    # Word count label
    word_count_label.place(relx=0.5, rely=0.79, anchor="n") # Centered below text frame

    # Save button
    save_button.place(relx=0.5, rely=0.84, anchor="n") # Centered below word count

    # The Exit and Help buttons are already placed on root with relx/rely, so they'll automatically adapt.

    # Update the internal scrollregion for the text_entry
    root.update_idletasks() # Ensure all new 'place' geometries are resolved
    text_entry.update_idletasks()
    # No direct scrollregion for Text widget, but ensure parent frame is sized correctly.
    # The pack(expand=True, fill="both") for text_entry handles it within text_frame.

#-----------------------------------------------------------------------------------------------------------------------------------------------#

#title label
title=tk.Label(root, text="My Diary😸", font=("Helvetica", 21, "bold"),bg="#fdf6f0",fg="#444")
title.pack(pady=(10,5))

#-----------------------------------------------------------------------------------------------------------------------------------------------#
#About random prompts

#print random writing prompts
writing_prompts=["What emotion have you felt the most today? Why?",
                    "How have you been treating yourself lately? Kindly or harshly?",
                    "What are the things that have brought you the most peace or joy today?",
                    "How are you feeling right now on a scale of 1 to 10?",
                    "Did you experience any negative thoughts today, and how did you challenge them?",
                    "Did anything interesting happen today?",
                    "What do you remember about your dreams last night?",
                    "What image or color comes to mind when you think of peace?"]
random_writ_prom=random.choice(writing_prompts) #computer will random choose one prompts and display

#frame to hold prompts and button side by side
prompts_frame=tk.Frame(root, bg="#fdf6f0")

#label to display the reflection prompts
promts_label=tk.Label(prompts_frame, text=random_writ_prom, font=("Comic Sans MS",11),bg="#fdf6f0", fg="#444", wraplength=600)
promts_label.pack(side="left",pady=(10,10),padx=(10,5),expand=True,fill="x")

#-----------------------------------------------------------------------------------------------------------------------------------------------#

#while button clicked the prompts will refresh
refresh_button=tk.Button(prompts_frame, text="New Prompt", command=refresh_prompts, font=("Comic Sans MS",10), bg="#b5d5ff", fg="#333",relief="groove")
refresh_button.pack(side="left",padx=(5,10))

#-----------------------------------------------------------------------------------------------------------------------------------------------#
#About adjust the position of current date and weather

#frame to hold the current date and weather
info_frame=tk.Frame(root, bg="#fdf6f0")

#get current date 
current_date = datetime.now().strftime("%B %d, %Y")  #strftime=string format time #Format:%B=Month, %d=Day, %Y=Year

#label to display the current date
cur_date_label=tk.Label(info_frame, text=f"Date📅: {current_date}", font=("Times New Roman",14),bg="#fdf6f0", fg="#333")
cur_date_label.pack(side="left",padx=10,expand=True)

#label to display the current weather
weather_info = get_weather()
weather_label = tk.Label(info_frame, text=f"Weather⛅: {weather_info}", font=("Times New Roman", 13), bg="#fdf6f0", fg="#333")
weather_label.pack(side="right",padx=10,expand=True)

#-----------------------------------------------------------------------------------------------------------------------------------------------#
#About a text entry for users to input their diary's title

#frame for small title
smalltitle_frame = tk.Frame(root, bg="#fdf6f0")

#label for small title
smalltitle_label = tk.Label(smalltitle_frame, text="Title:", font=("Times New Roman", 13), bg="#fdf6f0", fg="#333")
smalltitle_label.pack(side="left",padx=(0,5))

#blank text area for small title
smalltitle_entry = tk.Entry(smalltitle_frame, width=60, font=("Times New Roman", 12))
smalltitle_entry.pack(side="left", padx=10, pady=(0,2),fill="x",expand=True)

#-----------------------------------------------------------------------------------------------------------------------------------------------#
#About Font selection(OptionMenu)

#frame to hold the font selection
font_frame = tk.Frame(root, bg="#fdf6f0")

#\Create an inner frame to center the controls ---
font_controls_inner_frame = tk.Frame(font_frame, bg="#fdf6f0")
font_controls_inner_frame.pack(expand=True) # This will center the inner frame horizontally

#list of font options to let users choose
available_fonts = ["Times New Roman", "Helvetica", "Calibri", "Arial", "Courier", "Comic Sans MS"]

#create label for font selection
font_label = tk.Label(font_controls_inner_frame, text="Choose Font:", font=("Times New Roman", 12), bg="#fdf6f0", fg="#333")
font_label.pack(side="left",pady=(0,5),padx=(0,5))

#for storing selected font
selected_font = tk.StringVar() #Stringvar()=to store the font that selected by user from the optionmenu
selected_font.set(available_fonts[0])  #sets the default value of the OptionMenu to the first item in the list

#create the optionmenu thing
font_selection = tk.OptionMenu(font_controls_inner_frame, selected_font, *available_fonts, command=lambda _: update_font()) #*=used to unpack a list
font_selection.config(font=("Times New Roman", 12)) #set the font of the optionmenu itself
font_selection.pack(side="left", pady=(0,10),padx=(0,10))

#------------------------------------------------------------------------------------------------------------------------------------------------#
#clear all entry
clear_button = tk.Button(font_controls_inner_frame, text="Clear Entry", command=clear_entry, font=("Comic Sans MS", 10), bg="#ffd3d3", fg="#333")
clear_button.pack(side="left", padx=10, pady=(0,10))

#----------------------------------------------------------------------------------------------------------------------------------------------------#
#when press the button it auto insert the current time
timestamp_button = tk.Button(font_controls_inner_frame, text="Insert Timestamp", font=("Comic Sans MS", 10), command=insert_timestamp,bg="#ffe7e7")
timestamp_button.pack(side="left", padx=10, pady=(0,10))
#-----------------------------------------------------------------------------------------------------------------------------------------------#
#About main text entry

#create a fixed-size frame
text_frame = tk.Frame(root, bg="#fff0f0", bd=2,relief="flat")
text_frame.pack_propagate(False)  #prevent the frame from resizing based on content

#place the text widget inside the fixed-size frame
text_entry = tk.Text(text_frame, wrap="word", bd="2", relief="groove")
text_entry.pack(expand=True, fill="both")

#-----------------------------------------------------------------------------------------------------------------------------------------------#

#word count
word_count_label = tk.Label(root, text="0 words", font=("Comic Sans MS", 12), bg="#fdf6f0", fg="#999")

#-----------------------------------------------------------------------------------------------------------------------------------------------#

#create a save button
save_button=tk.Button(root,text="Save Entry", command=save_entry, font=("Comic Sans MS", 12), bg="#ffd3d3", fg="#333") #command=save_entry is to call save_entry function to  save diary
#-----------------------------------------------------------------------------------------------------------------------------------------------#

#connect the text box to word counter
text_entry.bind("<KeyRelease>", word_count) #everytime type/delete something,it triggers word_count #<KeyRelease>=when a key is pressed(event binding system from tkinter library)

#-----------------------------------------------------------------------------------------------------------------------------------------------#

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

#----------------------------------------------------------------------------------------------------------------------------------------------------#

help_button = ctk.CTkButton(root, text="❓ Help", font=("Segoe UI", 14), fg_color="#5A9BD5", hover_color="#7AB8FF", text_color="white", corner_radius=25, command=show_help)
help_button.place(relx=0.97, rely=0.09, anchor="ne")

#-----------------------------------------------------------------------------------------------------------------------------------------------#

# Start auto reminder
root.after(600000, auto_save_reminder)

# --- Initial setup calls ---
root.attributes("-fullscreen", True) # Start in fullscreen
# Bind update_layout to the root window's Configure event
root.bind("<Configure>", resize_layout)
# Initial call to update_layout to set up the elements
root.after(100, resize_layout) # Ensure window has rendered before calculating sizes

#-----------------------------------------------------------------------------------------------------------------------------------------------#

#run the whole program
root.mainloop()