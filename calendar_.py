import tkinter as tk
from tkcalendar import Calendar

#to get the date
def grab_date():
    date_label.config(text =calendar.get_date()) #update the text of date_label
    #the config is to modify existing widget

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

#(on hold)use for history_frame
right_frame=tk.Frame(root, bg="#FCF8E8")
right_frame.pack(side="left", fill="both", expand=True)

#(on hold)frame for history
history_frame=tk.Frame(root,padx=10,pady=10, bg="#FCF8E8") #inside the frame
history_frame.pack(padx=20, pady=20, fill="x", anchor="center")

#run the whole program
root.mainloop()