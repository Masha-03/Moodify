import tkinter as tk
from tkinter import ttk
import sqlite3

# Create the Tkinter root window
root = tk.Tk()
root.title("database")

#Window fullscreen
root.state('zoomed')

#Styling
main_font = ("Segoe UI", 14)
label_font = ("Segoe UI", 18, "bold")
bg_color = "#e6e0d8"
frame_bg = "#ffffff"
button_color = "#d9cfc1"

#Main frame
main_frame = tk.Frame(root, bg=frame_bg, bd=2, relief="groove")
main_frame.place(relx=0.5, rely=0.5, anchor="center", width=550, height=500)

#Title
title_label = tk.Label(main_frame, text="🌿 Moodify", font=("Segoe UI", 24, "bold"), bg=frame_bg)
title_label.pack(pady=(20, 0))

#Top spacer to push down content
tk.Label(main_frame, bg=frame_bg).pack(expand=True)

#Form frame
form_frame = tk.Frame(main_frame, bg=frame_bg)
form_frame.pack()

#Profile UI and input
profile_label = tk.Label(main_frame, text="Profile Name", font=label_font, bg=frame_bg)
profile_label.pack(pady=(0, 5))
profile_entry = tk.Entry(main_frame, font=main_font, width=30)     
profile_entry.pack(pady=(0, 20)) 

#Gender UI and input
gender_label = tk.Label(main_frame, text="Gender", font=label_font, bg=frame_bg)
gender_label.pack(pady=(0, 5))
gender_combobox = ttk.Combobox(main_frame, values=["Male", "Female"], font=main_font, width=28)
gender_combobox.pack()     

#Bottom spacer to push content up
tk.Label(main_frame, bg=frame_bg).pack(expand=True)

#Save data when button is clicked
def enter_data(): 
        #Get user info
        profile = profile_entry.get()
        gender = gender_combobox.get()
        #Display received data
        print(f": {profile}, Gender: {gender}") 
        #Connect to database
        connect = sqlite3.connect('user_info.db')
        #Create cursor
        cursor = connect.cursor()
        
        #Create table
        table_create_query = """ CREATE TABLE IF NOT EXISTS user_info
                (profile TEXT, gender TEXT) """
        cursor.execute(table_create_query)

        #Insert Data
        data_insert_query = """ INSERT INTO user_info
        (profile, gender) VALUES
        (?, ?)"""
        data_insert_tuple = (profile, gender)
        connect.execute(data_insert_query, data_insert_tuple)

        #Save data, update
        connect.commit()
        #Close connection
        connect.close()
    
#Submit button   
button = tk.Button(main_frame, text="SUBMIT",font=label_font, bg=button_color, width=20, command= enter_data)  
button.pack(pady=(10, 30))                          

root.mainloop()
