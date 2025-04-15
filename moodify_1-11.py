import tkinter as tk
from tkinter import ttk
import sqlite3

#Connect to database
connect = sqlite3.connect('user_info.db')
    
#Create cursor
cursor = connect.cursor()

# Create the Tkinter root window
root = tk.Tk()
root.title("database")
#----------------------------------------------------------------------UI-----------------------------------------------------------------------------------
#Window fullscreen
root.state('zoomed')

#Create frame inside window
frame = tk.Frame(root)
frame.pack()

#Frames for UI
moodify_frame = tk.LabelFrame(frame, text="Moodify")
moodify_frame.grid(row=3, column=0, padx=50, pady=50)
username_label = tk.Label(moodify_frame, text="Username:")
username_label.grid(row=3, column=0)
gender_label = tk.Label(moodify_frame, text="Gender:")
gender_combobox = ttk.Combobox(moodify_frame, values=["Male", "Female"])
gender_label.grid(row=5, column=0)
                               
 #User entry box
username_entry = tk.Entry(moodify_frame)     
username_entry.grid(row=4, column=0)     
gender_combobox.grid(row=6, column=0)     

#Padding for both elements  
for widget in moodify_frame.winfo_children():
        widget.grid_configure(padx=30, pady=30)
 
 #Save data when button is clicked
def enter_data(): 
        #Get user info
        username = username_entry.get()
        gender = gender_combobox.get()
        #Display received data
        print(f"Username: {username}, Gender: {gender}") 
    
#Submit button   
button = tk.Button(moodify_frame, text="SUBMIT", command= enter_data)  
button.grid(row=7, column=0, sticky="news", padx=30, pady=30)                          

#----------------------------------------------------------------------UI-----------------------------------------------------------------------------------
       
#Create table
table_create_query = ''' CREATE TABLE IF NOT EXISTS user_data 
        (username TEXT, gender TEXT)
'''
connect.execute(table_create_query)

#Update changes
connect.commit()

#Close connection
connect.close()


root.mainloop()
