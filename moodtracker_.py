import tkinter as tk
import random #for ask_user
from tkinter import messagebox #for show pop-up message
from PIL import Image,ImageTk #import pillow for image resizing
import datetime
import sqlite3

mood_quotes = {
    "Happy": "Keep shining, the world needs your light!",
    "Sad": "It's okay to be not okay. Better days are coming.",
    "Angry": "Breathe deeply. Stay calm. You're in control.",
    "Excited": "Your excitement is the spark for amazing things!",
    "Sleepy": "Rest well — even dreams need time to grow.",
    "Relaxed": "Peace of mind is the best kind of success."
}

#--------------------------------------------------------------masha---------------------------------------------------------------------------------# 
#Get profile from the database
def get_profile():
    global profile
    connect = sqlite3.connect('moodify_database.db')
    cursor = connect.cursor()
    
    #Fetch the profile
    cursor.execute("SELECT profile FROM user_info ORDER BY ROWID DESC LIMIT 1") #Fetch latest profile
    result = cursor.fetchone()
    
    connect.close() #Close connection
    if result:
        profile = result[0]  # Store the profile 
    else:
        profile = None  # Set profile to None if no profile found

#Initialise table
def initialise_table(): 
        #Connect to database
        connect = sqlite3.connect('moodify_database.db')
        #Create cursor
        cursor = connect.cursor()
        
        #Create the diary_entries table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile TEXT,
            date DATE,
            time TEXT,
            mood TEXT,
            mood_description TEXT,
            FOREIGN KEY (profile) REFERENCES user_info(profile)
        )
        ''')
        
        #Save data, update
        connect.commit()
        #Close connection
        connect.close()
        
#Initialise table before GUI starts        
initialise_table()  

#function to save mood
def save_mood():
    global selected_mood
    get_profile()
    if selected_mood:
        mood_desc = text_entry.get("1.0", tk.END).strip()
        if not mood_desc:
            mood_desc = "No description."

        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d") #Get date
        current_time = now.strftime("%H:%M:%S") #Get time

        # Insert into database
        conn = sqlite3.connect('moodify_database.db')
        cursor = conn.cursor()
        
        #Check for any empty field
        if not selected_mood: 
                #Warning box
                messagebox.showwarning("Incomplete Information", "Please select mood or write about it~")
                return
            
        cursor.execute('''
            INSERT INTO mood_entries (profile_name, date, time, mood, mood_description)
            VALUES (?, ?, ?, ?, ?)
        ''', (profile, current_date, current_time, selected_mood, mood_desc))

        conn.commit()
        conn.close()

        #Show popup after submit
        quote = mood_quotes.get(selected_mood, "No quote available.")
        messagebox.showinfo("Mood Saved!", f"Mood: {selected_mood}\n{quote}")

        #Reset entry
        text_entry.delete(1.0, tk.END)
        selected_mood = ""
    else:
        messagebox.showwarning("No Mood Selected", "Please select a mood before saving.")
        
#----------------------------------------------------------------------------------------------------------------------------------------------------#

#function to handle the button click
def set_mood(mood):
    global selected_mood
    selected_mood = mood #save clicked mood button
    
    if mood=="Happy":
        bg_colour="#fff9c4"
        btn_colour="#ffe082"
    elif mood=="Sad":
        bg_colour="#cfd8dc"
        btn_colour="#90a4ae"
    elif mood=="Angry":
        bg_colour="#ffcdd2"
        btn_colour="#ef9a9a"
    elif mood=="Excited":
        bg_colour="#ffe0b2"
        btn_colour="#ffb74d"
    elif mood=="Sleepy":
        bg_colour="#e1f5fe"
        btn_colour="#81d4fa"
    elif mood=="Relaxed":
        bg_colour="#dcedc8"
        btn_colour="#aed581"
    else:
        bg_colour="#fdf6f0"
        btn_colour="#f8c9c9"

    #Update background & text colors
    root.configure(bg=bg_colour)
    title.configure(bg=bg_colour)
    ask_user_label.configure(bg=bg_colour)
    label.configure(bg=bg_colour)
    text_entry.configure(bg="white", fg="#000")  # keep text box simple
    frame_button.configure(bg=bg_colour)

    #update all buttons to match the theme
    for button in emoji_buttons:
        button.configure(bg=btn_colour)

#main window
root=tk.Tk()
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}") #full-screen size
root.title("Mood Tracker")
root.configure(bg="#fdf6f0") 

title=tk.Label(root,text="Mood Tracker⭐", font=("Helvetica", 18, "bold"),bg="#fdf6f0",fg="#333")
title.pack(pady=10)

#some sentence to ask about users' current mood
ask_user=["How are you feeling today?",
          "How do you feel today?",
          "How's your mood today?",
          "What are you feeling right now?"]
random_ask_user=random.choice(ask_user) #computer will random display the question
print(random_ask_user) #print the sentence

#label to display the ask_user sentences
ask_user_label=tk.Label(root,text=random_ask_user, font=("Times New Roman",15),bg="#fdf6f0", fg="#333", wraplength=600) #wraplength=control text wrapping,will break the text into new line once it reaches specific pixel width.
ask_user_label.pack(pady=(10,10))

#create frame to hold emoji button and centre them
frame_button=tk.Frame(root,bg="#FCF8E8")
frame_button.pack(pady=20)

#list of emoji buttons
emoji_buttons=[]

#load and resize the image using PIL 
def resize_image(image_path, size=(100,50)):
    img=Image.open(image_path)
    img=img.resize(size, Image.Resampling.LANCZOS) #Resampling=process of changing size of an image #LANCZOS=high quality resizing
    return ImageTk.PhotoImage(img)

#image for button
happy_image=resize_image("C:/Users/qinen/project/moodify/happy.png")
sad_image=resize_image("C:/Users/qinen/project/moodify/sad.png")
angry_image=resize_image("C:/Users/qinen/project/moodify/angry.png")
excited_image=resize_image("C:/Users/qinen/project/moodify/excited.png")
sleepy_image=resize_image("C:/Users/qinen/project/moodify/sleepy.png")
relaxed_image=resize_image("C:/Users/qinen/project/moodify/relaxed.png")


#button to choose the mood
button_happy=tk.Button(frame_button,text="Happy😊", font=("Arial",12), bg="#f8c9c9", relief="groove", command=lambda:set_mood("Happy")) #command=lambda is to bind a function to button/expression 
button_sad=tk.Button(frame_button,text="Sad😢", font=("Arial",12), bg="#f8c9c9", relief="groove", command=lambda:set_mood("Sad"))       #when button clicked lambda calls set_mood("") function
button_angry=tk.Button(frame_button,text="Angry😠", font=("Arial",12), bg="#f8c9c9", relief="groove", command=lambda:set_mood("Angry"))
button_excited=tk.Button(frame_button,text="Excited😆", font=("Arial",12), bg="#f8c9c9", relief="groove", command=lambda:set_mood("Excited"))
button_sleepy=tk.Button(frame_button,text="Sleepy😴", font=("Arial",12), bg="#f8c9c9", relief="groove", command=lambda:set_mood("Sleepy"))
button_relaxed=tk.Button(frame_button,text="Relaxed😌", font=("Arial",12), bg="#f8c9c9", relief="groove", command=lambda:set_mood("Relaxed"))

#add all buttons to the list
emoji_buttons.extend([
    button_happy, button_sad, button_angry,
    button_excited, button_sleepy, button_relaxed
])

#place the emoji button to make it align horizontally
button_happy.pack(side="left", padx=10)
button_sad.pack(side="left", padx=10)
button_angry.pack(side="left", padx=10)
button_excited.pack(side="left", padx=10)
button_sleepy.pack(side="left", padx=10)
button_relaxed.pack(side="left", padx=10)

#blank text area for user to input something
text_entry=tk.Text(root,height=20,width=70)
text_entry.pack()

#Add a instruction label for users
label=tk.Label(root,text="Choose a button or describe your mood inside the blank box.",font=("Helvetica",11),bg="#fdf6f0",fg="#777")
label.pack(pady=(7,5))    

#save Button to save the mood
save_button = tk.Button(root, text="Save Mood", font=("Arial", 12), bg="white", relief="groove", command=save_mood)
save_button.pack(pady=10)

#global variable to store selected mood
selected_mood = ""

#run the whole program
root.mainloop()


