import tkinter as tk
import customtkinter as ctk
from tkcalendar import Calendar
import sqlite3
from PIL import Image, ImageTk
import os
import sys
from tkinter import messagebox

#Global Placeholders for UI Widgets (to prevent NameErrors in functions)
title_display = None
content_text = None
mood_display = None
mooddesc_display = None
calendar = None
date_label = None
profile = None # Global for get_profile

#Dynamic Background Image Handler
#Use a list to store the PhotoImage reference, so it can be modified in the nested function scope
_bg_photo_ref = [None] #Private variable for the PhotoImage object

def update_background_image(event=None):
    #This function will be called whenever the app window size changes
    current_width = app.winfo_width()
    current_height = app.winfo_height()

    #Avoid errors if width/height are 0 during initial setup (before window is truly drawn)
    if current_width == 0 or current_height == 0:
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))
    bg_image_path = os.path.join(base_dir, "calendar_bg.png")

    try:
        original_bg_image = Image.open(bg_image_path)
        # Resize to the current window dimensions for dynamism
        resized_bg_image = original_bg_image.resize((current_width, current_height), Image.Resampling.LANCZOS)
        _bg_photo_ref[0] = ImageTk.PhotoImage(resized_bg_image) # Update the stored reference
        bg_label.configure(image=_bg_photo_ref[0]) # Update the image displayed by the label
    except FileNotFoundError:
        print(f"Background image not found at: {bg_image_path}")
    except Exception as e:
        print(f"Error loading or resizing background image: {e}")


#Asset Helper Function (for PyInstaller compatibility) 
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

def get_db_path():
    if getattr(sys, 'frozen', False):
        app_root = sys._MEIPASS
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root = os.path.dirname(script_dir)

    db_file_name = 'moodify_database.db'
    db_folder_name = 'database'

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
    # Consider creating the folder and an empty DB here if it's truly missing on first run
    # try:
    #     os.makedirs(os.path.dirname(database_file_path), exist_ok=True)
    #     print(f"Created directory: {os.path.dirname(database_file_path)}")
    # except OSError as e:
    #     print(f"Error creating directory: {e}")
        
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
        profile = result[0]   #Store the profile
    else:
        profile = None   #Set profile to None if no profile found

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
        title, content, mood, mood_desc = result[0]   #Get the title, content, mood, mood description

        #Update title
        title_display.configure(text=title)
        
        #Simulate spacing and indent for content_text
        formatted_content = "\n" + content   #Add 1 empty line at top
        indented_content = "\n".join("    " + line for line in formatted_content.splitlines()) #Indents every line of the content with 4 spaces 

        # Update content
        content_text.configure(state="normal")   #Enable editing
        content_text.delete("1.0", tk.END) #Clears existing text
        content_text.insert(tk.END, indented_content) #Display content
        # The next two lines apply tags for display effects, assuming they are defined elsewhere
        # content_text.tag_add("top_space", "1.0", "1.0 lineend")   #First line only
        # content_text.tag_add("left_margin", "1.0", "end") #For all lines
        content_text.configure(state="disabled")   #Disable editing again
        
        # Update mood & mood description
        mood_display.configure(text=mood if mood else "No mood")
        
        mooddesc_text = mood_desc if mood_desc else "No mood description"
        formatted_mooddesc = "\n" + mooddesc_text #Add 1 empty line at top
        indented_mooddesc = "\n".join("    " + line for line in formatted_mooddesc.splitlines()) #Indents every line of the content with 4 spaces 
        
        mooddesc_display.configure(state="normal") #Enable editing
        mooddesc_display.delete("1.0", tk.END) #Clears existing text
        # The next two lines apply tags for display effects, assuming they are defined elsewhere
        # mooddesc_display.tag_add("top_space", "1.0", "1.0 lineend")   #First line only
        # mooddesc_display.tag_add("left_margin", "1.0", "end") #All lines
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
        # content_text.tag_add("top_space", "1.0", "1.0 lineend")   #First line only
        # content_text.tag_add("left_margin", "1.0", "end") #All lines
        content_text.configure(state="disabled") #Disable editing
        
        #Mood and mood description
        mood_display.configure(text="No mood")
        mooddesc_display.configure(state="normal") #Enable editing
        mooddesc_display.delete("1.0", tk.END) #Clears existing text
        
        
        no_mooddesc_text = "No mood description"
        formatted_no_mooddesc = "\n" + no_mooddesc_text #Add 1 empty line at top
        indented_no_mooddesc = "\n".join("    " + line for line in formatted_no_mooddesc.splitlines()) #Indents every line of the content with 4 spaces 
    
        mooddesc_display.insert(tk.END, indented_no_mooddesc)
        # mooddesc_display.tag_add("top_space", "1.0", "1.0 lineend")   #First line only
        # mooddesc_display.tag_add("left_margin", "1.0", "end") #All lines
        mooddesc_display.configure(state="disabled") #Disable editing
   
    connect.close()

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#give users some tips
def show_help():
    messagebox.showinfo("Help", "Click on a date to view your diary and mood. Press Ctrl+F to toggle fullscreen.")

#----------------------------------------------------------------------------------------------------------------------------------------------------#

# Toggle fullscreen using the 'f' key
def toggle_fullscreen(event=None):
    if app.attributes('-fullscreen'):
        app.attributes('-fullscreen', False)
    else:
        app.attributes('-fullscreen', True)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#clear the display
def clear_display():
    if title_display: # Check if widgets exist before trying to configure
        title_display.configure(text="") #clear the title
    if content_text:
        content_text.configure(state="normal") #Makes the Text widget editable.
        content_text.delete("1.0", tk.END) #Deletes all the text inside the Text widget (content_text)
        content_text.configure(state="disabled") #Re-disables the text area to prevent user input again.
    if mood_display:
        mood_display.configure(text="") #clear the mood 
    if mooddesc_display:
        mooddesc_display.configure(state="normal")
        mooddesc_display.delete("1.0", tk.END) #delete all content
        mooddesc_display.configure(state="disabled")

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#to get the date
def grab_date():
    global profile
    get_profile()
    if calendar: # Ensure calendar is initialized
        selected_date = calendar.get_date()   #Get the selected date from the calendar
        if date_label: # Ensure date_label is initialized
            date_label.configure(text=selected_date) #update the text of date_label
        
        if profile:   #Check if a profile exists
            show_entry(selected_date)   #Show diary entries for the selected date
        else:
            print("No profile found.")   #Debug message if no profile exists
    else:
        print("Calendar widget not yet initialized.")


#----------------------------------------------------------------------------------------------------------------------------------------------------#

#Main window
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
app = ctk.CTk()

#Make app truly full screen and responsive
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
app.geometry(f"{screen_width}x{screen_height}")
#Start fullscreen 
app.attributes('-fullscreen', True) 

#Root window grid
#Row 0 for header (fixed height), Row 1 for main content (expands vertically)
app.grid_rowconfigure(0, weight=0)
app.grid_rowconfigure(1, weight=1)
#Only one column for the app as a whole, which will contain frames
app.grid_columnconfigure(0, weight=1) 

app.title("Calendar")
app.configure(bg="#FFF8F0") #change the background color of entire window

#Bind the 'f' key (lowercase only) (for fullscreen)
app.bind("<Control-f>", toggle_fullscreen)
#Bind 'esc' key to escape fullscreen
app.bind("<Escape>", toggle_fullscreen) 

# --- Background Image Handling ---
# Label to display the background image (created, but image set by update_background_image)
bg_label = tk.Label(app)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)   # Stretch it across the window
bg_label.lower() # Lower the label so it doesn’t cover other widgets

# Bind the resize event to update the background image
app.bind("<Configure>", update_background_image)
# Call it once initially to load and set the background image
update_background_image()


#----------------------------------------------------------------------------------------------------------------------------------------------------#

#Header Frame
#This frame will be placed in app's row 0
header_frame = ctk.CTkFrame(app, fg_color="#FFF8F0") # Set explicit color to match app's bg
header_frame.grid(row=0, column=0, sticky="NSEW", padx=20, pady=10)

#Configure header_frame's internal grid for dynamic button placement
header_frame.grid_rowconfigure(0, weight=1) # Allow row 0 to expand (for vertical centering of contents)
header_frame.grid_columnconfigure(0, weight=0) # Clear Button column (fixed width)
header_frame.grid_columnconfigure(1, weight=1) # Title Label column (expands horizontally to center title)
header_frame.grid_columnconfigure(2, weight=0) # Stacked Help/Exit Buttons column (fixed width)


# Clear Display button (top-left)
clear_button = ctk.CTkButton(header_frame, text="Clear Display", font=("Arial Rounded MT Bold", 14),
                              fg_color="#E6D6B8", text_color="#333", hover_color="#C0C0C0",
                              corner_radius=10, command=clear_display)
clear_button.grid(row=0, column=0, padx=(0, 10), sticky="W") # Place in header_frame's row 0, column 0


# Title label (now inside header_frame)
title_label = ctk.CTkLabel(header_frame, text="My History 🧸", font=ctk.CTkFont("Helvetica", 26, weight="bold"), text_color="#333", fg_color="#e9e2d0")
title_label.grid(row=0, column=1, sticky="NSEW", padx=10, pady=5) # NSEW to center and expand within its cell


# --- Button Stack Frame (for Help and Exit buttons) ---
# This frame will hold Help and Exit buttons stacked vertically
button_stack_frame = ctk.CTkFrame(header_frame, fg_color="transparent") # Use transparent to match header_frame
button_stack_frame.grid(row=0, column=2, sticky="E") # Place in header_frame's row 0, column 2, right-aligned

# Configure button_stack_frame's internal grid for vertical stacking
button_stack_frame.grid_columnconfigure(0, weight=1) # Single column for buttons
button_stack_frame.grid_rowconfigure(0, weight=1) # Help button row
button_stack_frame.grid_rowconfigure(1, weight=1) # Exit button row


# Help button (top-right, stacked above exit button)
help_button = ctk.CTkButton(button_stack_frame, text="❓ Help", font=("Segoe UI", 14), fg_color="#5A9BD5", hover_color="#7AB8FF", text_color="white", corner_radius=25, command=show_help)
help_button.grid(row=0, column=0, padx=5, pady=(0, 2), sticky="E") # Place in button_stack_frame


# Exit button (top-rightmost, stacked below help button)
exit_button = ctk.CTkButton(
    button_stack_frame, # Parent is now button_stack_frame
    text="❌ Exit",
    font=("Segoe UI", 14),
    fg_color="#FF5151",
    hover_color="#FF6A6A",
    text_color="white",
    corner_radius=25,
    command=app.destroy
)
exit_button.grid(row=1, column=0, padx=5, pady=(2, 0), sticky="E") # Place in button_stack_frame


#----------------------------------------------------------------------------------------------------------------------------------------------------#

# --- Main Content Area Frame (to hold left_frame and history_frame side-by-side) ---
# This frame will be placed in app's row 1
main_content_frame = ctk.CTkFrame(app, fg_color="#FFF8F0") # Set explicit color to match app's bg
main_content_frame.grid(row=1, column=0, sticky="NSEW", padx=20, pady=10) # Spans the single app column

# Configure main_content_frame's internal grid for side-by-side layout
main_content_frame.grid_rowconfigure(0, weight=1) # Only one row for content, expands vertically
main_content_frame.grid_columnconfigure(0, weight=1) # Column for left_frame (expands)
main_content_frame.grid_columnconfigure(1, weight=2) # Column for history_frame (expands twice as much)


#----------------------------------------------------------------------------------------------------------------------------------------------------#

# frame for left side (now inside main_content_frame)
left_frame = ctk.CTkFrame(main_content_frame, fg_color="#FFF8F0") # Set explicit color
left_frame.grid(row=0, column=0, sticky="NSEW", padx=(0, 20), pady=0) # Place in main_content_frame, left column

# Configure left_frame's internal grid to be dynamic
left_frame.grid_columnconfigure(0, weight=1) # The single column containing all widgets will expand horizontally

# Configure rows inside left_frame:
left_frame.grid_rowconfigure(0, weight=0) # "Choose a date" label (fixed height)
left_frame.grid_rowconfigure(1, weight=1) # Calendar widget (expands vertically)
left_frame.grid_rowconfigure(2, weight=0) # Choose Date button (fixed height)
left_frame.grid_rowconfigure(3, weight=1) # Flexible empty row to push date_label down
left_frame.grid_rowconfigure(4, weight=0) # Date label (fixed height)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#add a label for the title
label=ctk.CTkLabel(left_frame, text="Choose on a date to view your diary", font=("Helvetica", 15), text_color="#777")
label.grid(row=0, column=0, padx=250, pady=(20, 20))

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
calendar.grid(row=1, column=0, padx=10, pady=10, sticky="NSEW") # Add sticky="NSEW"

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#choose date button
choosedate_btn = ctk.CTkButton(left_frame,
    text="Choose Date",
    font=("Arial Rounded MT Bold", 18),
    fg_color="#FFD1A6",      #background color
    text_color="#444",       #text color
    hover_color="#FFB66E",   #color when hovered or clicked
    corner_radius=10,        #for rounded edges
    command=grab_date)
choosedate_btn.grid(row=2, column=0, pady=10)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#the display of the date (YYYY-mm-dd)
date_label = ctk.CTkLabel(left_frame, text="", font=ctk.CTkFont("Arial Rounded MT Bold", 15), text_color="#444")
date_label.grid(row=3, column=0, pady=(5, 10), sticky="n")

#----------------------------------------------------------------------------------------------------------------------------------------------------#
# History Frame (now inside main_content_frame)
history_frame = ctk.CTkFrame(main_content_frame, corner_radius=15, fg_color="#E6D6B8")
history_frame.grid(row=0, column=1, sticky="NSEW", padx=(20, 0), pady=0) # Place in main_content_frame, right column

# Configure history_frame's internal grid for responsiveness
history_frame.grid_rowconfigure(0, weight=1) # The 'container' row will expand
history_frame.grid_columnconfigure(0, weight=1) # The 'container' column will expand

# Container (now inside history_frame)
container = ctk.CTkFrame(history_frame, fg_color="#E6D6B8", corner_radius=15)
container.grid(row=0, column=0, sticky="NSEW", padx=20, pady=10) # Place in history_frame

# Configure container's internal grid for content layout
container.grid_columnconfigure(0, weight=1) # Make the single content column expand horizontally

# Configure rows for vertical expansion within the container
container.grid_rowconfigure(0, weight=0) # Title Label "Title:" (fixed height)
container.grid_rowconfigure(1, weight=0) # title_display (fixed height)
container.grid_rowconfigure(2, weight=0) # Entry Label "Entry:" (fixed height)
container.grid_rowconfigure(3, weight=3) # content_frame (will expand vertically much more)
container.grid_rowconfigure(4, weight=0) # Mood Label "Mood:" (fixed height)
container.grid_rowconfigure(5, weight=0) # mood_display (fixed height)
container.grid_rowconfigure(6, weight=0) # Mood Description Label (fixed height)
container.grid_rowconfigure(7, weight=1) # mooddesc_frame (will expand vertically)
container.grid_rowconfigure(8, weight=0) # Any potential footer or extra space

# Diary Title
ctk.CTkLabel(container, text="Title:", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, sticky="w", pady=(10, 5))
title_display = ctk.CTkLabel(container, text="", fg_color="white", corner_radius=6, anchor="w")
title_display.grid(row=1, column=0, sticky="EW", pady=(0, 10)) # sticky="EW" to stretch horizontally

# Diary Entry
ctk.CTkLabel(container, text="Entry:", font=ctk.CTkFont(size=15, weight="bold")).grid(row=2, column=0, sticky="w", pady=(5, 5))
content_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=6)
content_frame.grid(row=3, column=0, sticky="NSEW", pady=(0, 10)) # sticky="NSEW" to stretch in both directions

# Configure content_frame's internal grid (for Textbox and Scrollbar)
content_frame.grid_rowconfigure(0, weight=1) # The row with textbox will expand vertically
content_frame.grid_columnconfigure(0, weight=1) # The column with textbox will expand horizontally

content_text = ctk.CTkTextbox(content_frame, wrap="word", fg_color="white", corner_radius=0, # REMOVED height=100
                              font=ctk.CTkFont(size=14))
content_text.grid(row=0, column=0, sticky="NSEW") # Changed from pack to grid, sticky to fill
content_scroll = ctk.CTkScrollbar(content_frame, orientation="vertical", command=content_text.yview)
content_scroll.grid(row=0, column=1, sticky="NS") # Changed from pack to grid, sticky="NS" for vertical fill
content_text.configure(yscrollcommand=content_scroll.set, state="disabled")

# Mood
ctk.CTkLabel(container, text="Mood:", font=ctk.CTkFont(size=15, weight="bold")).grid(row=4, column=0, sticky="w", pady=(10, 5))
mood_display = ctk.CTkLabel(container, text="", fg_color="white", corner_radius=6, anchor="w")
mood_display.grid(row=5, column=0, sticky="EW", pady=(0, 10)) # sticky="EW" to stretch horizontally

# Mood Description
ctk.CTkLabel(container, text="Mood Description:", font=ctk.CTkFont(size=15, weight="bold")).grid(row=6, column=0, sticky="w", pady=(5, 5))
mooddesc_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=6)
mooddesc_frame.grid(row=7, column=0, sticky="NSEW", pady=(0, 10)) # sticky="NSEW" to stretch in both directions

# Configure mooddesc_frame's internal grid (for Textbox and Scrollbar)
mooddesc_frame.grid_rowconfigure(0, weight=1) # The row with textbox will expand vertically
mooddesc_frame.grid_columnconfigure(0, weight=1) # The column with textbox will expand horizontally

mooddesc_display = ctk.CTkTextbox(mooddesc_frame, wrap="word", fg_color="white", corner_radius=0, # REMOVED height=100
                                  font=ctk.CTkFont(size=14))
mooddesc_display.grid(row=0, column=0, sticky="NSEW") # Changed from pack to grid, sticky to fill
mooddesc_scroll = ctk.CTkScrollbar(mooddesc_frame, orientation="vertical", command=mooddesc_display.yview)
mooddesc_scroll.grid(row=0, column=1, sticky="NS") # Changed from pack to grid, sticky="NS" for vertical fill
mooddesc_display.configure(yscrollcommand=mooddesc_scroll.set, state="disabled")


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#run the whole program
app.mainloop()