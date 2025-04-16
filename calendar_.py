import tkinter as tk
from tkcalendar import Calendar

#to get the date
def grab_date():
    date_label.config(text =cal.get_date()) #update the text of date_label
    #the config is to modify existing widget

#main window
root=tk.Tk() #create the main app window
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")  #Full-screen size
root.title("Calendar📅")
root.configure(bg="#fdf6f0") #change the background color of entire window

#Title label
title=tk.Label(root, text="My Calendar🧸", font=("Helvetica", 18, "bold"),bg="#fdf6f0",fg="#333") #fg=foreground/text color
title.pack(pady=10) #pack()=Places the widget inside the window or frame. Pady=Adds () pixels of vertical space around the widget.

#frame around calendar for additional 
calendar_frame=tk.Frame(root, bg="#fdf6f0", bd=2, relief="groove") #bd=border width #relief=control style of border #groove=make the border looks craved in
calendar_frame.pack(pady=10)

#create a calendar widget with themed colors
cal=Calendar(calendar_frame, selectmode="day", date_pattern="yyyy-mm-dd", 
             font=("Helvetica",11), background="#ffecd2", #calendar background
             foreground="#2c3e50", #month and year's color
             headerbackground="#ffd6d6", #background color of day names and week numbers(mon,tues....)
             normalbackground="#fefae0", #the color of weekday's date
             weekendbackground="#ffe5ec", #the color of weekend's date
             selectbackground="#ff7518", #when you click on a random date there will present an orange color.
             disabledbackground="#ccc") #the colour of the date that are not able to be clicked
#the frame around the calendar
cal.pack(padx=8, pady=10) #pack=geometry manager #padx=add horizontal padding #pady=add vertical padding

#add a label for the title
label=tk.Label(root,text="Choose on a date to view your diary",font=("Helvetica",11),bg="#fdf6f0",fg="#777")
label.pack(pady=15) #add space below it

history_frame=tk.Frame(root,padx=10,pady=10, bg="#fdf6f0") #inside the frame
history_frame.pack(padx= 20,pady=20)

#the display of the date yyyy-mm-dd
date_label =tk.Label(history_frame,text="",font=("Arial Rounded MT Bold",15),bg="#fdf6f0") #display
date_label.pack()

#choose date button
choosedate_btn = tk.Button(calendar_frame,text="Choose Date",font=("Arial Rounded MT Bold",18),bg="#ffe5ec"
                    ,bd=3,relief="groove",activebackground="#ffe5ec", #activebackground=background while pressed
                    activeforeground="black",command=grab_date) #activeforeground=text color on click
choosedate_btn.pack(pady=10)

#run the whole program
root.mainloop()