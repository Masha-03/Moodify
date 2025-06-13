import tkinter as tk
from tkinter import ttk #Styled widgets
import sqlite3
from tkinter import messagebox #To show popup boxes
from PIL import Image, ImageTk #Handle and display images
import os
import sys
import subprocess
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
    # print("WARNING: A new database file will likely be created here.")
    # # Create the 'database' folder if it doesn't exist
    # try:
    #     os.makedirs(os.path.dirname(database_file_path), exist_ok=True)
    #     print(f"Created directory: {os.path.dirname(database_file_path)}")
    # except OSError as e:
    #     print(f"Error creating directory: {e}")

#Initialise shared database
def initialise_table(): 
        #Connect to database
        connect = sqlite3.connect(database_file_path)
        #Create cursor
        cursor = connect.cursor()
        
        #Create table
        cursor.execute(""" CREATE TABLE IF NOT EXISTS user_info
                (profile TEXT PRIMARY KEY, 
                gender TEXT NOT NULL) """
        )
        
        #Save data, update
        connect.commit()
        #Close connection
        connect.close()
#Initialise table before GUI starts        
initialise_table()  

#Create main window
root = tk.Tk()
root.title("Moodify")

#Window fullscreen
root.state('zoomed')

#Track fullscreen state
is_fullscreen = [False]

# Toggle fullscreen using the 'f' key
def toggle_fullscreen(event=None):
        is_fullscreen[0] = not is_fullscreen[0]
        root.attributes("-fullscreen", is_fullscreen[0])

#Bind the 'f' key (lowercase only) (for fullscreen)
root.bind("<Control-f>", toggle_fullscreen)

# ESC to exit fullscreen
def exit_fullscreen(event=None):
        root.attributes("-fullscreen", False)

root.bind("<Escape>", exit_fullscreen)

#Get actual screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

#Load and set the background image
base_dir = os.path.dirname(os.path.abspath(__file__)) 
bg_image_path = os.path.join(base_dir,"graphics", "intro_bg.png") 
bg_image=Image.open(bg_image_path)
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()))  # Resize to fullscreen
bg_photo = ImageTk.PhotoImage(bg_image)

#Image is put on a label
bg_label = tk.Label(root, image=bg_photo)
bg_label.image = bg_photo  #Keep a reference to avoid it disappering randomly
#Image stretches in the entire window
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

#Styling
root.configure(bg="#e6e0d8")
main_font = ("Segoe UI", 14)
label_font = ("Segoe UI", 18, "bold")
frame_bg = "#ffffff"
button_color = "#ECDFC8"

#Main frame
main_frame = tk.Frame(root, bg=frame_bg, bd=2, relief="groove")
main_frame.place(relx=0.5, rely=0.5, anchor="center", width=550, height=500) #Centered

#Title
title_label = tk.Label(main_frame, text="🌿 Moodify", font=("Segoe UI", 24, "bold"), bg=frame_bg)
title_label.pack(pady=(20, 0))

#Spacer to push down content
tk.Label(main_frame, bg=frame_bg).pack(expand=True)

#Form area
form_frame = tk.Frame(main_frame, bg=frame_bg)
form_frame.pack()

#Profile UI
profile_label = tk.Label(main_frame, text="Profile Name", font=label_font, bg=frame_bg)
profile_label.pack(pady=(0, 5))
#Profile input column
profile_entry = tk.Entry(main_frame, font=main_font, width=30)     
profile_entry.pack(pady=(0, 20)) 

#Gender UI
gender_label = tk.Label(main_frame, text="Gender", font=label_font, bg=frame_bg)
gender_label.pack(pady=(0, 5))
#Gender input column
gender_combobox = ttk.Combobox(main_frame, values=["Male", "Female"], font=main_font, width=28, state="readonly") #Dropdown selection
gender_combobox.pack()     

#Add empty space below the form
tk.Label(main_frame, bg=frame_bg).pack(expand=True)

#Save data into database when button is clicked
def enter_data(): 
        #Get user info
        profile = profile_entry.get().strip()
        gender = gender_combobox.get()
        
        #Connect to database
        connect = sqlite3.connect(database_file_path)
        #Create cursor
        cursor = connect.cursor()
        
        #Check for any empty field
        if not profile or not gender:
                #Warning box
                messagebox.showwarning("Incomplete Information", "Please fill in both Profile Name and Gender")
                #Clear field after profile input
                profile_entry.delete(0, tk.END)
                profile_entry.focus_set()  #Puts the cursor back in the profile box
                #Reset gender to blank
                gender_combobox.set("")
                return
        
        #Display received data
        print(f": {profile}, Gender: {gender}") 

        #Check for exact match (same profile name, same gender)
        cursor.execute("SELECT * FROM user_info WHERE profile = ? AND gender = ?", (profile, gender))
        exact_match_result = cursor.fetchone()

        if exact_match_result:
            proceed = messagebox.askyesno(
                "Profile Exists",
                f"The profile name '{profile}' already exists.\nAre you this user and want to continue?"
            )

            if proceed:
                #Delete the old entry (same)
                cursor.execute("DELETE FROM user_info WHERE profile = ? AND gender = ?", (profile, gender))
                #Save data, update
                connect.commit()

                #Re-insert the same profile (becomes the last row)
                data_insert_query = """ INSERT INTO user_info
                (profile, gender) VALUES (?, ?)"""
                data_insert_tuple = (profile, gender)
                cursor.execute(data_insert_query, data_insert_tuple)
                #Save data, update
                connect.commit()

                messagebox.showinfo("Success", "Lesgooo! Profile saved successfully!")

                #Connect to next page after successful entry
                instruction_script_path = resource_path("tkinter pages", "instruction_page_.py")
                subprocess.Popen([sys.executable, instruction_script_path])

                #Wait for 3 seconds before closing the window
                time.sleep(3)
                #Close the current Tkinter window
                root.destroy()
                sys.exit()
            else:
                messagebox.showinfo("Profile Name Taken", "Please enter a different profile name.")
                #Clear field after profile input
                profile_entry.delete(0, tk.END)
                profile_entry.focus_set()  #Puts the cursor back in the profile box
                #Reset gender to blank
                gender_combobox.set("")

        else:
            #Check for same profile name with any gender
            cursor.execute("SELECT gender FROM user_info WHERE profile = ?", (profile,))
            profile_name_exists_result = cursor.fetchone() #Fetches gender if profile name exists

            if profile_name_exists_result:
                messagebox.showinfo(
                    "Profile Name Taken",
                    f"The profile name '{profile}' is already used by someone else.\nPlease choose a different name."
                )
                #Clear field after profile input
                profile_entry.delete(0, tk.END)
                profile_entry.focus_set()  #Puts the cursor back in the profile box
                #Reset gender to blank
                gender_combobox.set("")
            else:
                #No duplicate profile name found at all, so insert
                data_insert_query = """ INSERT INTO user_info
                (profile, gender) VALUES (?, ?)"""
                data_insert_tuple = (profile, gender)
                cursor.execute(data_insert_query, data_insert_tuple)
                #Save data, update
                connect.commit()
                #Close connection
                connect.close() 

                messagebox.showinfo("Success", "Lesgooo! Profile saved successfully!")

                #Connect to next page after successful entry
                instruction_script_path = resource_path("tkinter pages", "instruction_page_.py")
                subprocess.Popen([sys.executable, instruction_script_path])

                #Wait for 3 seconds before closing the window
                time.sleep(3)
                #Close the current Tkinter window
                root.destroy()
                sys.exit()
                
        #Save data, update
        connect.commit()
        #Close connection
        connect.close() 
        #Clear field after profile input
        profile_entry.delete(0, tk.END)
        profile_entry.focus_set()  #Puts the cursor back in the profile box
        #Reset gender to blank
        gender_combobox.set("")
         
    
#Submit button   
button = tk.Button(main_frame, text="SUBMIT",font=label_font, bg=button_color, width=20, command= enter_data)  
button.pack(pady=(10, 30))                  

root.mainloop()