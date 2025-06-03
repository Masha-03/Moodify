import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import sqlite3
from PIL import Image, ImageTk

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
    connect = sqlite3.connect('moodify_database.db')
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
    connect = sqlite3.connect('moodify_database.db')
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
        content_text.config(state="normal")
        content_text.tag_add("top_space", "1.0", "1.0 lineend")  # first line only
        content_text.tag_configure("top_space", spacing1=10)  # 10 pixels top spacing
        #Indent
        content_text.tag_configure("left_margin", lmargin1=10, lmargin2=10)
        content_text.tag_add("left_margin", "1.0", "end")
        content_text.config(state="disabled")  # Disable editing again
        
        # Update mood & mood description
        mood_display.config(text=mood if mood else "No mood")
        mooddesc_display.config(state="normal")
        mooddesc_display.delete("1.0", tk.END)
        mooddesc_display.tag_add("top_space", "1.0", "1.0 lineend")  # first line only
        mooddesc_display.tag_configure("top_space", spacing1=10)  # 10 pixels top spacing
        mooddesc_display.tag_configure("left_margin", lmargin1=10, lmargin2=10)
        mooddesc_display.tag_add("left_margin", "1.0", "end")
        mooddesc_display.insert(tk.END, mood_desc if mood_desc else "No mood description")
        mooddesc_display.config(state="disabled")
        
    else:
        title_display.config(text="No title")
        content_text.config(state="normal")
        content_text.delete("1.0", tk.END)
        content_text.insert(tk.END, "No diary entry found for this date.")
        content_text.tag_add("top_space", "1.0", "1.0 lineend")  # first line only
        content_text.tag_configure("top_space", spacing1=10)  # 10 pixels top spacing
        #Indent
        content_text.tag_configure("left_margin", lmargin1=10, lmargin2=10)
        content_text.tag_add("left_margin", "1.0", "end")
        content_text.config(state="disabled")
        
        #Mood and mood description
        mood_display.config(text="No mood")
        mooddesc_display.config(state="normal")
        mooddesc_display.delete("1.0", tk.END)
        mooddesc_display.insert(tk.END, "No mood description")
        mooddesc_display.tag_add("top_space", "1.0", "1.0 lineend")  # first line only
        mooddesc_display.tag_configure("top_space", spacing1=10)  # 10 pixels top spacing
        #Indent
        mooddesc_display.tag_configure("left_margin", lmargin1=10, lmargin2=10)
        mooddesc_display.tag_add("left_margin", "1.0", "end")
        mooddesc_display.config(state="disabled")
   
    connect.close()
#----------------------------------------------------------------------------------------------------------------------------------------------------#

#main window
root=tk.Tk() #create the main app window
root.state('zoomed')#Fullscreen size
root.title("Calendar")
root.configure(bg="#FFF8F0") #change the background color of entire window

#Load and set the background image
bg_image = Image.open("tkinter pages/calendar_bg.png") 
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()))  # Resize to fullscreen
bg_photo = ImageTk.PhotoImage(bg_image)

#Label to display the background image
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Stretch it across the window
bg_label.image = bg_photo  # Keep a reference to avoid garbage collection

#Lower the label so it doesn’t cover other widgets
bg_label.lower()

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#Title label
title=tk.Label(root, text="My Calendar🧸", font=("Helvetica", 18, "bold"), bg="#FFF8F0", fg="#333") #fg=foreground/text color
title.pack(pady=20) #pack()=Places the widget inside the window or frame. Pady=Adds () pixels of vertical space around the widget.

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#frame for left side #create this frame is because pack and grid cannot use at the same time,need to seperate them
left_frame=tk.Frame(root,  bg="#FFF8F099", bd=0, highlightthickness=0) #make it 'transparent'
left_frame.pack(side="left", fill="y", padx=20, pady=20) #pack=geometry manager #padx=add horizontal padding #pady=add vertical padding

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#add a label for the title
label=tk.Label(left_frame,text="Choose on a date to view your diary",font=("Helvetica",11),fg="#777")
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
choosedate_btn = tk.Button(left_frame,text="Choose Date",font=("Arial Rounded MT Bold",18),bg="#FFD1A6"
                    ,bd=3,relief="groove",activebackground="#FFB66E", #activebackground=background while pressed
                    activeforeground="#444",command=grab_date) #activeforeground=text color on click
choosedate_btn.grid(row=2, column=0, pady=10)

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#the display of the date yyyy-mm-dd
date_label =tk.Label(left_frame,text="",font=("Arial Rounded MT Bold",15)) #display
date_label.grid(row=3, column=0, pady=(10, 0), sticky="n")

#----------------------------------------------------------------------------------------------------------------------------------------------------#

#History frame
history_frame = tk.Frame(root, bg="#FFF0D9", bd=2, relief="ridge")
history_frame.pack(expand=True, fill="both", padx=40,pady=40)

#Diary's title history
history_title=tk.Label(history_frame, text="History", font=("Arial",13,"bold"),bg="#FFF0D9", fg="#444")
history_title.pack()

#Title label and value
title_label = tk.Label(history_frame, text="Title:", font=("Arial", 12, "bold"), bg="#FFF0D9", fg="#444")
title_label.pack(anchor="w", padx=20, pady=(20, 5))

title_display = tk.Label(history_frame, text="", font=("Arial", 11), bg="white", fg="#333", bd=1, relief="groove", padx=10, pady=5, anchor="w", justify="left")
title_display.pack(fill="x", padx=20, pady=(0, 10))

#Create a frame to hold text + scrollbar 
content_frame = tk.Frame(history_frame, bg="#FFF0D9")
content_frame.pack(fill="x", padx=20, pady=10)

#Diary content 
content_text = tk.Text(content_frame, height=9, wrap="word", bg="white", fg="#333", bd=1, relief="groove", font=("Arial", 11))
content_text.pack(side="left", fill="both", expand=True)

#Scrollbar
scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=content_text.yview)
scrollbar.pack(side="right", fill="y")
content_text.config(yscrollcommand=scrollbar.set)
content_text.config(state="disabled")

#Mood label
mood_label = tk.Label(history_frame, text="Mood:", font=("Arial", 12, "bold"), bg="#FFF0D9", fg="#444")
mood_label.pack(anchor="w", padx=20, pady=(0, 5))

mood_display = tk.Label(history_frame, text="", font=("Arial", 11), bg="white", fg="#333", bd=1, relief="groove", padx=10, pady=5, anchor="w", justify="left")
mood_display.pack(fill="x", padx=20, pady=(0, 20))

#Frame to hold text + scrollbar
mooddesc_frame = tk.Frame(history_frame, bg="#FFF0D9")
mooddesc_frame.pack(fill="x", padx=20, pady=(0, 20))

#Text widget
mooddesc_display = tk.Text(mooddesc_frame, height=9, wrap="word", bg="white", fg="#333", bd=1, relief="groove", font=("Arial", 11))
mooddesc_display.pack(side="left", fill="both", expand=True)
mooddesc_display.config(state="normal") 

#Scrollbar
scrollbar = tk.Scrollbar(mooddesc_frame, orient="vertical", command=mooddesc_display.yview)
scrollbar.pack(side="right", fill="y")
mooddesc_display.config(yscrollcommand=scrollbar.set)
mooddesc_display.config(state="disabled")
#---------------------------------------------------------------------------------------------------------`-------------------------------------------#

#run the whole program
root.mainloop()