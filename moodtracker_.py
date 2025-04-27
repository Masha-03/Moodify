import tkinter as tk
import random #for ask_user
from tkinter import messagebox #for show pop-up message

mood_quotes = {
    "Happy": "Keep shining, the world needs your light!",
    "Sad": "It's okay to be not okay. Better days are coming.",
    "Angry": "Breathe deeply. Stay calm. You're in control.",
    "Excited": "Your excitement is the spark for amazing things!",
    "Sleepy": "Rest well — even dreams need time to grow.",
    "Relaxed": "Peace of mind is the best kind of success."
}

#function to handle the button click
def set_mood(mood):
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

    #get the matching quote
    quote=mood_quotes.get(mood,"")

    messagebox.showinfo("Mood Selected!", f"Mood Saved! {quote}") #display a messagebox to let users know their mood has been selected

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

emoji_buttons=[]

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

#run the whole program
root.mainloop()


