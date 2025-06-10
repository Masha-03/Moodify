import tkinter as tk
import customtkinter as ctk
from tkcalendar import Calendar
import sqlite3
from PIL import Image, ImageTk
import os
import sys
from tkinter import messagebox

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
        base_path = os.path.dirname(os.path.abspath(_file_))

    return os.path.join(base_path, *relative_path_parts)

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
    cursor.execute('''SELECT profile 
                   FROM user_info 
                   ORDER BY ROWID DESC LIMIT 1''') #Fetch latest profile by sorting profile from newest to oldest
    result = cursor.fetchone() #Fetch one only
    
    connect.close() #Close connection
    if result:
        profile = result[0]  #Store the profile
    else:
        profile = None  #Set profile to None if no profile found

def show_entry(selected_date):
    # Get the profile 
    get_profile() 
    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()

    #Fetch entry for selected date, current profile, and join mood_entries table
    cursor.execute('''
        SELECT d.title, d.content, m.mood, m.mood_description
        FROM diary_entries d
        LEFT JOIN mood_entries m ON d.profile = m.profile AND d.date = m.date
        WHERE d.profile = ? AND d.date = ?
    ''', (profile, selected_date))

    result = cursor.fetchall() #Fetch all entries on the day

    #If there are entries for the selected date
    if result: 
        title, content, mood, mood_desc = result[0]  #Get the title, content, mood, mood description

        #Update title
        title_display.configure(text=title)
        
        #Simulate spacing and indent for content_text
        formatted_content = "\n" + content  #Add 1 empty line at top
        indented_content = "\n".join("    " + line for line in formatted_content.splitlines()) #Indents every line of the content with 4 spaces 

        # Update content
        content_text.configure(state="normal")  #Enable editing
        content_text.delete("1.0", tk.END) #Clears existing text
        content_text.insert(tk.END, indented_content) #Display content
        content_text.configure(state="normal")
        content_text.tag_add("top_space", "1.0", "1.0 lineend")  #First line only
        content_text.tag_add("left_margin", "1.0", "end") #For all lines
        content_text.configure(state="disabled")  #Disable editing again
        
        # Update mood & mood description
        mood_display.configure(text=mood if mood else "No mood")
        
        mooddesc_text = mood_desc if mood_desc else "No mood description"
        formatted_mooddesc = "\n" + mooddesc_text #Add 1 empty line at top
        indented_mooddesc = "\n".join("    " + line for line in formatted_mooddesc.splitlines()) #Indents every line of the content with 4 spaces 
        
        mooddesc_display.configure(state="normal") #Enable editing
        mooddesc_display.delete("1.0", tk.END) #Clears existing text
        mooddesc_display.tag_add("top_space", "1.0", "1.0 lineend")  #First line only
        mooddesc_display.tag_add("left_margin", "1.0", "end") #All lines
        mooddesc_display.insert(tk.END, indented_mooddesc)
        mooddesc_display.configure(state="disabled") #Disable editing
        
    else:
        #If no content to show
        title_display.configure(text="No title")
        content_text.configure(state="normal") #Enable editing
        content_text.delete("1.0", tk.END) #Clears existing text

        no_entry_text = "No diary entry found for this date."
        formatted_no_entry = "\n" + no_entry_text #Add 1 empty line at top
        indented_no_entry = "\n".join("    " + line for line in formatted_no_entry.splitlines()) #Indents every line of the content with 4 spaces 
        
        content_text.insert(tk.END, indented_no_entry)
        content_text.tag_add("top_space", "1.0", "1.0 lineend")  #First line only
        content_text.tag_add("left_margin", "1.0", "end") #All lines
        content_text.configure(state="disabled") #Disable editing
        
        #Mood and mood description
        mood_display.configure(text="No mood")
        mooddesc_display.configure(state="normal") #Enable editing
        mooddesc_display.delete("1.0", tk.END) #Clears existing text
        
        
        no_mooddesc_text = "No mood description"
        formatted_no_mooddesc = "\n" + no_mooddesc_text #Add 1 empty line at top
        indented_no_mooddesc = "\n".join("    " + line for line in formatted_no_mooddesc.splitlines()) #Indents every line of the content with 4 spaces 
    
        mooddesc_display.insert(tk.END, indented_no_mooddesc)
        mooddesc_display.tag_add("top_space", "1.0", "1.0 lineend")  #First line only
        mooddesc_display.tag_add("left_margin", "1.0", "end") #All lines
        mooddesc_display.configure(state="disabled") #Disable editing
   
    connect.close()
#----------------------------------------------------------------------------------------------------------------------------------------------------#
#give users some tips
def show_help():
    messagebox.showinfo("Help", "Click on a date to view your diary and mood. Press Ctrl+F to toggle fullscreen.")

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#Track fullscreen state
is_fullscreen = [False]

# Toggle fullscreen using the 'f' key
def toggle_fullscreen(event=None):
    if app.attributes('-fullscreen'):
        app.attributes('-fullscreen', False)
    else:
        app.attributes('-fullscreen', True)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#clear the display
def clear_display():
    title_display.configure(text="") #clear the title
    content_text.configure(state="normal") #Makes the Text widget editable.
    content_text.delete("1.0", tk.END) #Deletes all the text inside the Text widget (content_text)
    content_text.configure(state="disabled") #Re-disables the text area to prevent user input again.

    mood_display.configure(text="") #clear the mood 
    mooddesc_display.configure(state="normal")
    mooddesc_display.delete("1.0", tk.END) #delete all content
    mooddesc_display.configure(state="disabled")

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#to get the date
def grab_date():
    global profile
    get_profile()
    selected_date = calendar.get_date()  #Get the selected date from the calendar
    date_label.configure(text=selected_date) #update the text of date_label
    #the config is to modify existing widget
    
    if profile:  #Check if a profile exists
        show_entry(selected_date)  #Show diary entries for the selected date
    else:
        print("No profile found.")  #Debug message if no profile exists

#main window
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
app = ctk.CTk()

app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}") #Full-screen size
   
app.title("Calendar")
app.configure(bg="#FFF8F0") #change the background color of entire window

#Bind the 'f' key (lowercase only) (for fullscreen)
app.bind("<Control-f>", toggle_fullscreen)

#Load and set the background image
base_dir = os.path.dirname(os.path.abspath(__file__)) 
bg_image_path = os.path.join(base_dir, "calendar_bg.png") 
bg_image=Image.open(bg_image_path)
bg_image = bg_image.resize((app.winfo_screenwidth(), app.winfo_screenheight()), Image.Resampling.LANCZOS)  # Resize to fullscreen
bg_photo = ImageTk.PhotoImage(bg_image)

#Label to display the background image
bg_label = tk.Label(app, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Stretch it across the window
bg_label.image = bg_photo  # Keep a reference to avoid garbage collection

#Lower the label so it doesn’t cover other widgets
bg_label.lower()

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#Title label
title_label = ctk.CTkLabel(app, text="My History 🧸", font=ctk.CTkFont("Helvetica", 26, weight="bold"), text_color="#333", fg_color="#e9e2d0")
title_label.pack(pady=(20, 10)) #pack()=Places the widget inside the window or frame. Pady=Adds () pixels of vertical space around the widget.

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#frame for left side #create this frame is because pack and grid cannot use at the same time,need to seperate them
left_frame = ctk.CTkFrame(app, width=300, height=200, fg_color="transparent")
left_frame.pack(side="left", fill="y", padx=40, pady=20) #pack=geometry manager #padx=add horizontal padding #pady=add vertical padding

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#add a label for the title
label=ctk.CTkLabel(left_frame, text="Choose on a date to view your diary", font=("Helvetica", 15), text_color="#777")
label.grid(row=0, column=0, padx=50, pady=(5, 10), sticky="w") #sticky="w" means stick to the west

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#create a calendar widget with themed colors
calendar=Calendar(left_frame, selectmode="day", date_pattern="yyyy-mm-dd", 
             font=("Helvetica",11), background="#FFDAB3", #calendar background
             foreground="#6F4E37", #month and year's text color
             headersbackground="#FFBC80", #background color of day names and week numbers(mon,tues....)
             normalbackground="#FFE6CC", #the color of weekday's date
             weekendbackground="#FFF1E0", #the color of weekend's date
             selectbackground="#FF9F45", #when you click on a random date there will present an orange color.
             disabledbackground="#ccc") #the colour of the date that are not able to be clicked
#the frame around the calendar
calendar.grid(row=1, column=0, padx=10, pady=10) 

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#choose date button
choosedate_btn = ctk.CTkButton(left_frame,
    text="Choose Date",
    font=("Arial Rounded MT Bold", 18),
    fg_color="#FFD1A6",     #background color
    text_color="#444",      #text color
    hover_color="#FFB66E",  #color when hovered or clicked
    corner_radius=10,       #for rounded edges
    command=grab_date)
choosedate_btn.grid(row=2, column=0, pady=10)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#the display of the date yyyy-mm-dd
date_label = ctk.CTkLabel(left_frame, text="", font=ctk.CTkFont("Arial Rounded MT Bold", 15), text_color="#444")
date_label.grid(row=4, column=0, pady=(10, 20), sticky="n")

#----------------------------------------------------------------------------------------------------------------------------------------------------#
# History Frame
history_frame = ctk.CTkFrame(app, corner_radius=15, fg_color="#E6D6B8")
history_frame.pack(expand=True, fill="both", padx=40, pady=40)

# Container
container = ctk.CTkFrame(history_frame, fg_color="#E6D6B8", corner_radius=15)
container.pack(expand=True, fill="both", padx=20, pady=10)

# Diary Title
ctk.CTkLabel(container, text="Title:", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(10, 5))
title_display = ctk.CTkLabel(container, text="", fg_color="white", corner_radius=6, anchor="w")
title_display.pack(fill="x", pady=(0, 10))

# Diary Entry
ctk.CTkLabel(container, text="Entry:", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(5, 5))
content_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=6)
content_frame.pack(fill="x", pady=(0, 10))

content_text = ctk.CTkTextbox(content_frame, wrap="word", fg_color="white", corner_radius=0, height=100, font=ctk.CTkFont(size=14))
content_text.pack(side="left", fill="both", expand=True)
content_scroll = ctk.CTkScrollbar(content_frame, orientation="vertical", command=content_text.yview)
content_scroll.pack(side="right", fill="y")
content_text.configure(yscrollcommand=content_scroll.set, state="disabled")

# Mood
ctk.CTkLabel(container, text="Mood:", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(10, 5))
mood_display = ctk.CTkLabel(container, text="", fg_color="white", corner_radius=6, anchor="w")
mood_display.pack(fill="x", pady=(0, 10))

# Mood Description
ctk.CTkLabel(container, text="Mood Description:", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(5, 5))
mooddesc_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=6)
mooddesc_frame.pack(fill="x", pady=(0, 10))

mooddesc_display = ctk.CTkTextbox(mooddesc_frame, wrap="word", fg_color="white", corner_radius=0, height=100, font=ctk.CTkFont(size=14))
mooddesc_display.pack(side="left", fill="both", expand=True)
mooddesc_scroll = ctk.CTkScrollbar(mooddesc_frame, orientation="vertical", command=mooddesc_display.yview)
mooddesc_scroll.pack(side="right", fill="y")
mooddesc_display.configure(yscrollcommand=mooddesc_scroll.set, state="disabled")

#---------------------------------------------------------------------------------------------------------`-------------------------------------------#
#exit button
exit_button = ctk.CTkButton(
    app,
    text="❌ Exit",
    font=("Segoe UI", 14),
    fg_color="#FF5151",
    hover_color="#FF6A6A",
    text_color="white",
    corner_radius=25,
    command=app.destroy
)
exit_button.place(relx=0.97, rely=0.03, anchor="ne")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

help_button = ctk.CTkButton(app, text="❓ Help", font=("Segoe UI", 14), fg_color="#5A9BD5", hover_color="#7AB8FF", text_color="white", corner_radius=25, command=show_help)
help_button.place(relx=0.97, rely=0.06, anchor="ne")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

clear_button = ctk.CTkButton(app, text="Clear Display", font=("Arial Rounded MT Bold", 14),
                              fg_color="#E6D6B8", text_color="#333", hover_color="#C0C0C0",
                              corner_radius=10, command=clear_display)
clear_button.place(relx=0.04, rely=0.06, anchor="w")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#run the whole program
app.mainloop()