import tkinter as tk
from tkinter import ttk #Styled widgets
import sqlite3
from tkinter import messagebox #To show popup boxes
from PIL import Image, ImageTk #Handle and display images
import os

# Find the folder where the current Python file is
base_dir = os.path.dirname(os.path.abspath(__file__))
# Always save database in same folder
db_path = os.path.join(base_dir, 'moodify_database.db')
connect = sqlite3.connect(db_path)

#Initialise shared database
def initialise_table(): 
        #Connect to database
        connect = sqlite3.connect('moodify_database.db')
        #Create cursor
        cursor = connect.cursor()
        
        #Create table
        table_create_query = """ CREATE TABLE IF NOT EXISTS user_info
                (profile TEXT UNIQUE NOT NULL, 
                gender TEXT NOT NULL) """
        cursor.execute(table_create_query)
        
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

#Get actual screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

#Load and resize image to fill the screen
bg_image = Image.open("intro_bg.png")
bg_image = bg_image.resize((screen_width, screen_height))
#Converts image into a format Tkinter can use
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
gender_combobox = ttk.Combobox(main_frame, values=["Male", "Female"], font=main_font, width=28) #Dropdown selection
gender_combobox.pack()     

#Add empty space below the form
tk.Label(main_frame, bg=frame_bg).pack(expand=True)

#Save data into database when button is clicked
def enter_data(): 
        #Get user info
        profile = profile_entry.get().strip()
        gender = gender_combobox.get()
        
        #Connect to database
        connect = sqlite3.connect('moodify_database.db')
        #Create cursor
        cursor = connect.cursor()
        
        #Check for any empty field
        if not profile or not gender:
                #Warning box
                messagebox.showwarning("Incomplete Information", "Please fill in both Profile Name and Gender")
                return
        
        #Display received data
        print(f": {profile}, Gender: {gender}") 
        
        #Check for duplicate profile name
        cursor.execute("SELECT profile FROM user_info WHERE profile = ?", (profile,))
        result = cursor.fetchone() #Fetches matching profile name

        #If profile name is already taken
        if result:
                #Pop up box to inform
                tk.messagebox.showwarning("Duplicate Entry", "Heyyy, sorry, pick a different profile name XD")
        else:
                #Insert only if no duplicate profile name
                data_insert_query = """ INSERT INTO user_info
                (profile, gender) VALUES
                (?, ?)"""
                data_insert_tuple = (profile, gender)
                connect.execute(data_insert_query, data_insert_tuple)
                #Successful pop up box
                tk.messagebox.showinfo("Success", "Lesgooo! Profile saved successfully!")
        
        #Clear field after profile input
        profile_entry.delete(0, tk.END)
        profile_entry.focus_set()  #Puts the cursor back in the profile box
        #Reset gender to blank
        gender_combobox.set("")

        #Save data, update
        connect.commit()
        #Close connection
        connect.close()

        #Close the current Tkinter window
        root.destroy()  
    
#Submit button   
button = tk.Button(main_frame, text="SUBMIT",font=label_font, bg=button_color, width=20, command= enter_data)  
button.pack(pady=(10, 30))                  

root.mainloop()