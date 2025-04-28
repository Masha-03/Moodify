import tkinter as tk
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
    connect = sqlite3.connect('moodify_database.db')
    cursor = connect.cursor()

    #Fetch the entry for the selected date and current profile
    cursor.execute('''
        SELECT content FROM diary_entries
        WHERE profile = ? AND date = ?
    ''', (profile, selected_date))

    result = cursor.fetchall() #Fetch all entries on the day

    #If there are entries for the selected date
    if result:
        #Clear any previous entries in the history frame before showing the new entries
        for widget in history_frame.winfo_children():
            widget.destroy()

        #Display the entries
        for entry in result:
            # Create a frame for each entry
            entry_frame = tk.Frame(history_frame, bg="#FCF8E8", pady=10, padx=10, bd=2, relief="solid")
            entry_frame.pack(fill="x", padx=10, pady=5)

            # Create a label for the entry text
            entry_label = tk.Label(entry_frame, text=entry[0], font=("Helvetica", 12), bg="#FCF8E8", wraplength=400)
            entry_label.pack()
    else:
        # If no entries for the selected date, show a message
        no_entry_label = tk.Label(history_frame, text="No diary entries for this date.", font=("Helvetica", 12, "italic"), bg="#FCF8E8")
        no_entry_label.pack(pady=10)
        
    connect.close()
#----------------------------------------------------------------------------------------------------------------------------------------------------#
# Get the profile from the database once at the start
get_profile() 

#main window
root=tk.Tk() #create the main app window
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")  #Full-screen size
root.title("Calendar📅")
root.configure(bg="#FCF8E8") #change the background color of entire window

#Title label
title=tk.Label(root, text="My Calendar🧸", font=("Helvetica", 18, "bold"),bg="#FCF8E8",fg="#333") #fg=foreground/text color
title.pack(pady=10) #pack()=Places the widget inside the window or frame. Pady=Adds () pixels of vertical space around the widget.

#frame for left side #create this frame is because pack and grid cannot use at the same time,need to seperate them
left_frame=tk.Frame(root, bg="#FCF8E8")
left_frame.pack(side="left", fill="y", padx=20, pady=20) #pack=geometry manager #padx=add horizontal padding #pady=add vertical padding

#add a label for the title
label=tk.Label(left_frame,text="Choose on a date to view your diary",font=("Helvetica",11),bg="#FCF8E8",fg="#777")
label.grid(row=0, column=0, padx=10, pady=(5, 10), sticky="w") #sticky="w" means stick to the west

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

#choose date button
choosedate_btn = tk.Button(left_frame,text="Choose Date",font=("Arial Rounded MT Bold",18),bg="#F7E7CE"
                    ,bd=3,relief="groove",activebackground="#F99982", #activebackground=background while pressed
                    activeforeground="black",command=grab_date) #activeforeground=text color on click
choosedate_btn.grid(row=2, column=0, pady=10)

#the display of the date yyyy-mm-dd
date_label =tk.Label(left_frame,text="",font=("Arial Rounded MT Bold",15),bg="#FCF8E8") #display
date_label.grid(row=3, column=0, pady=(10, 0), sticky="n")

# Frame for history
history_frame = tk.Frame(root, padx=10, pady=10, bg="#FCF8E8")  # inside the frame
history_frame.pack(padx=20, pady=20, fill="both", expand=True)

#run the whole program
root.mainloop()