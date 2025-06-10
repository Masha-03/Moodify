import tkinter as tk
import random
from datetime import datetime #to get current date and time
from tkinter import messagebox #for show pop-up message
import requests #getting data from API
import tkinter.font as tkfont #use to import font module from tkinter library
import sqlite3
import os
from PIL import Image, ImageTk
import customtkinter as ctk
from datetime import datetime
from tkinter import simpledialog,messagebox

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
    db_file_name = 'moodify_database.db'
    
    if getattr(sys, 'frozen', False):
        # We are running in a bundle (e.g., PyInstaller)
        # In PyInstaller, sys._MEIPASS is the path to the temporary folder where your bundled data files are extracted.
        # You need to configure PyInstaller to include the 'database' folder.
        base_dir = sys._MEIPASS
        print(f"Running in frozen mode. Base directory: {base_dir}")
        
        # When using PyInstaller, you'd typically put your database file directly into the sys._MEIPASS directory (or a subfolder you specify in the .spec).
        # For simplicity, if you bundle the whole 'database' folder relative to your script, it will often end up directly in sys._MEIPASS or a subfolder there.
        db_path = os.path.join(base_dir, 'database', db_file_name) 
        
    else:
        # We are running in a normal Python environment (during development)
        # The script is in 'YourMainAppFolder/your_main_app.py'
        # The database is in 'YourMainAppFolder/database/moodify_database.db'
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Running in unfrozen mode. Base directory: {base_dir}")
        
        # Construct the path relative to the script's directory
        db_path = os.path.join(base_dir, 'database', db_file_name)

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

def get_image_path(filename):
    # This gets the path of the current Python file
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#main window
root=tk.Tk()
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}") #Full-screen size
root.title("Diary📖")
root.configure(bg="#fdf6f0")
#----------------------------------------------------------------------------------------------------------------------------------------------------#

# Load and set background image
base_dir = os.path.dirname(os.path.abspath(__file__)) 
bg_image_path = os.path.join(base_dir, "diary_bg.png") 
bg_image=Image.open(bg_image_path)
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

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
print(random_writ_prom)

#frame to hold prompts and button side by side
prompts_frame=tk.Frame(root, bg="#fdf6f0")
prompts_frame.pack(pady=(0,10))

#label to display the reflection prompts
promts_label=tk.Label(prompts_frame, text=random_writ_prom, font=("Comic Sans MS",11),bg="#fdf6f0", fg="#444", wraplength=600)
promts_label.pack(side="left",pady=(10,10))

#-----------------------------------------------------------------------------------------------------------------------------------------------#

#while button clicked the prompts will refresh
refresh_button=tk.Button(prompts_frame, text="New Prompt", command=refresh_prompts, font=("Comic Sans MS",10), bg="#b5d5ff", fg="#333",relief="groove")
refresh_button.pack(side="left")


#-----------------------------------------------------------------------------------------------------------------------------------------------#
#About adjust the position of current date and weather

#frame to hold the current date and weather
info_frame=tk.Frame(root, bg="#fdf6f0")
info_frame.pack(fill="x", padx=270, pady=(0,2))

#get current date 
current_date = datetime.now().strftime("%B %d, %Y")  #strftime=string format time #Format:%B=Month, %d=Day, %Y=Year

#label to display the current date
cur_date_label=tk.Label(info_frame, text=f"Date📅: {current_date}", font=("Times New Roman",14),bg="#fdf6f0", fg="#333")
cur_date_label.pack(side="left")

#label to display the current weather
weather_info = get_weather()
weather_label = tk.Label(info_frame, text=f"Weather⛅: {weather_info}", font=("Times New Roman", 13), bg="#fdf6f0", fg="#333")
weather_label.pack(side="right")

#-----------------------------------------------------------------------------------------------------------------------------------------------#
#About a text entry for users to input their diary's title

#frame for small title
smalltitle_frame = tk.Frame(root, bg="#fdf6f0")
smalltitle_frame.pack(pady=(5, 13))

#label for small title
smalltitle_label = tk.Label(smalltitle_frame, text="Title:", font=("Times New Roman", 13), bg="#fdf6f0", fg="#333")
smalltitle_label.pack(side="left")

#blank text area for small title
smalltitle_entry = tk.Entry(smalltitle_frame, width=60, font=("Times New Roman", 12))
smalltitle_entry.pack(side="left", padx=10, pady=(0,2))

#-----------------------------------------------------------------------------------------------------------------------------------------------#
#About Font selection(OptionMenu)

#list of font options to let users choose
available_fonts = ["Times New Roman", "Helvetica", "Calibri", "Arial", "Courier", "Comic Sans MS"]

#frame to hold the font selection
font_frame = tk.Frame(root, bg="#fdf6f0")
font_frame.pack(pady=(5, 0))

#create label for font selection
font_label = tk.Label(font_frame, text="Choose Font:", font=("Times New Roman", 12), bg="#fdf6f0", fg="#333")
font_label.pack(side="left",pady=(0,5))

#for storing selected font
selected_font = tk.StringVar() #Stringvar()=to store the font that selected by user from the optionmenu
selected_font.set(available_fonts[0])  #sets the default value of the OptionMenu to the first item in the list

#create the optionmenu thing
font_selection = tk.OptionMenu(font_frame, selected_font, *available_fonts, command=lambda _: update_font()) #*=used to unpack a list
font_selection.config(font=("Times New Roman", 12)) #set the font of the optionmenu itself
font_selection.pack(side="left", pady=(0,10))

#------------------------------------------------------------------------------------------------------------------------------------------------#
#clear all entry
clear_button = tk.Button(font_frame, text="Clear Entry", command=clear_entry, font=("Comic Sans MS", 10), bg="#ffd3d3", fg="#333")
clear_button.pack(side="left", padx=10, pady=(0,10))

#----------------------------------------------------------------------------------------------------------------------------------------------------#
#when press the button it auto insert the current time
timestamp_button = tk.Button(font_frame, text="Insert Timestamp", font=("Comic Sans MS", 10), command=insert_timestamp,bg="#ffe7e7")
timestamp_button.pack(side="left", padx=10, pady=(0,10))
#-----------------------------------------------------------------------------------------------------------------------------------------------#
#About main text entry

#create a fixed-size frame
text_frame = tk.Frame(root, width=800, height=330, bg="#fff0f0", bd=2)
text_frame.pack()
text_frame.pack_propagate(False)  #prevent the frame from resizing based on content

#place the text widget inside the fixed-size frame
text_entry = tk.Text(text_frame, wrap="word", bd="2", relief="groove")
text_entry.pack(expand=True, fill="both")

#-----------------------------------------------------------------------------------------------------------------------------------------------#

#word count
word_count_label = tk.Label(root, text="0 words", font=("Comic Sans MS", 12), bg="#fdf6f0", fg="#999")
word_count_label.pack(pady=(5, 5))

#-----------------------------------------------------------------------------------------------------------------------------------------------#

#create a save button
save_button=tk.Button(root,text="Save Entry", command=save_entry, font=("Comic Sans MS", 12), bg="#ffd3d3", fg="#333") #command=save_entry is to call save_entry function to  save diary
save_button.pack(pady=1)

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
#-----------------------------------------------------------------------------------------------------------------------------------------------#

#run the whole program
root.mainloop()