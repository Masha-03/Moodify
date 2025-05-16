import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import sqlite3

#to get the date
def grab_date():
    selected_date = calendar.get_date()  #Get the selected date from the calendar
    date_label.config(text =calendar.get_date()) #update the text of date_label
    #the config is to modify existing widget
    
    show_entry(selected_date)  #Show diary entries for the selected date
    if profile:  #Check if a profile exists
        show_entry(selected_date)  #Show diary entries for the selected date
    else:
        print("No profile found.")  #Debug message if no profile exists

#--------------------------------------------------------------masha---------------------------------------------------------------------------------# 
#Get profile from the database
def get_profile():
    global profile
    connect = sqlite3.connect('Moodify/moodify_database.db')
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

#----------------------------------------------------------------------------------------------------------------------------------------------------#

def show_entry(selected_date):
    # Get the profile 
    get_profile() 
    connect = sqlite3.connect('Moodify/moodify_database.db')
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
        title, content, mood, mood_desc = result[0]  # Get the title, content, mood, mood description

        # Update title
        title_display.config(text=title)

        # Update content
        content_text.config(state="normal")  # Enable editing to update
        content_text.delete("1.0", tk.END)
        content_text.insert(tk.END, content)
        content_text.config(state="disabled")  # Disable editing again
        
        # Update mood & mood description
        mood_display.config(text=mood if mood else "No mood")
        mooddesc_display.config(text=mood_desc if mood_desc else "No mood description")
    else:
        title_display.config(text="No title")
        content_text.config(state="normal")
        content_text.delete("1.0", tk.END)
        content_text.insert(tk.END, "No diary entry found for this date.")
        content_text.config(state="disabled")
        
        #Mood and mood description
        mood_display.config(text="No mood")
        mooddesc_display.config(text="No mood description")
   
    connect.close()
#----------------------------------------------------------------------------------------------------------------------------------------------------#

#main window
root=tk.Tk() #create the main app window
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")  #Full-screen size
root.title("Calendar📅")
root.configure(bg="#FCF8E8") #change the background color of entire window

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#Title label
title=tk.Label(root, text="My Calendar🧸", font=("Helvetica", 18, "bold"),bg="#FCF8E8",fg="#333") #fg=foreground/text color
title.pack(pady=10) #pack()=Places the widget inside the window or frame. Pady=Adds () pixels of vertical space around the widget.

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#frame for left side #create this frame is because pack and grid cannot use at the same time,need to seperate them
left_frame=tk.Frame(root, bg="#FCF8E8")
left_frame.pack(side="left", fill="y", padx=20, pady=20) #pack=geometry manager #padx=add horizontal padding #pady=add vertical padding

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#add a label for the title
label=tk.Label(left_frame,text="Choose on a date to view your diary",font=("Helvetica",11),bg="#FCF8E8",fg="#777")
label.grid(row=0, column=0, padx=10, pady=(5, 10), sticky="w") #sticky="w" means stick to the west

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#create a calendar widget with themed colors
calendar=Calendar(left_frame, selectmode="day", date_pattern="yyyy-mm-dd", 
             font=("Helvetica",11), background="#FF7518", #calendar background
             foreground="#2c3e50", #month and year's text color
             headersbackground="#F4A460", #background color of day names and week numbers(mon,tues....)
             normalbackground="#EDC9AF", #the color of weekday's date
             weekendbackground="#FFEFD5", #the color of weekend's date
             selectbackground="#F08080", #when you click on a random date there will present an orange color.
             disabledbackground="#ccc") #the colour of the date that are not able to be clicked
#the frame around the calendar
calendar.grid(row=1, column=0, padx=10, pady=10) 

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#choose date button
choosedate_btn = tk.Button(left_frame,text="Choose Date",font=("Arial Rounded MT Bold",18),bg="#F7E7CE"
                    ,bd=3,relief="groove",activebackground="#F99982", #activebackground=background while pressed
                    activeforeground="black",command=grab_date) #activeforeground=text color on click
choosedate_btn.grid(row=2, column=0, pady=10)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#the display of the date yyyy-mm-dd
date_label =tk.Label(left_frame,text="",font=("Arial Rounded MT Bold",15),bg="#FCF8E8") #display
date_label.grid(row=3, column=0, pady=(10, 0), sticky="n")

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#History frame
history_frame = tk.Frame(root, bg="#FFF0D9", bd=2, relief="ridge")
history_frame.pack(expand=True, fill="both", padx=20, pady=20)

#history title
history_title=tk.Label(history_frame, text="History📖", font=("Comic Sans MS",13,"bold"),bg="#FFF0D9",fg="#333")
history_title.pack(pady=(0,4))

#Title label and value
title_label = tk.Label(history_frame, text="Title:", font=("Arial", 12, "bold"), bg="#FFF0D9", fg="#444")
title_label.pack(anchor="w", padx=20, pady=(20, 5))

title_display = tk.Label(history_frame, text="", font=("Arial", 11), bg="white", fg="#333", bd=1, relief="groove", padx=10, pady=5)
title_display.pack(fill="x", padx=20, pady=(0, 10))

#Content text box
content_text = tk.Text(history_frame, height=15, wrap="word", bg="white", fg="#333", bd=1, relief="groove", font=("Arial", 11))
content_text.pack(fill="both", expand=True, padx=20, pady=10)
content_text.config(state="disabled")  #Make read-only by default

#Mood label
mood_label = tk.Label(history_frame, text="Mood:", font=("Arial", 12, "bold"), bg="#FFF0D9", fg="#444")
mood_label.pack(anchor="w", padx=20, pady=(0, 5))

mood_display = tk.Label(history_frame, text="", font=("Arial", 11), bg="white", fg="#333", bd=1, relief="groove", padx=10, pady=5)
mood_display.pack(fill="x", padx=20, pady=(0, 10))

#Mood description label
mooddesc_label = tk.Label(history_frame, text="Mood Description:", font=("Arial", 12, "bold"), bg="#FFF0D9", fg="#444")
mooddesc_label.pack(anchor="w", padx=20, pady=(0, 5))

mooddesc_display = tk.Label(history_frame, text="", font=("Arial", 11), bg="white", fg="#333", bd=1, relief="groove", padx=10, pady=5, anchor="center", justify="left", wraplength=500)
mooddesc_display.pack(fill="x", padx=20, pady=(0, 10))

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#run the whole program
root.mainloop()