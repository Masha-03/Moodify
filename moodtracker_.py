import tkinter as tk
import random #for ask_user
from tkinter import messagebox #for show pop-up message

#function to handle the button click
def set_mood(mood):
    messagebox.showinfo("Mood Selected!", f"Mood Saved! Your mood for today is: {mood}") #display a messagebox to let users know their mood has been selected

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
ask_user_label.pack(pady=10)

#Add a instruction label for users
label=tk.Label(root,text="Choose a button or describe your mood inside the blank box.",font=("Helvetica",11),bg="#fdf6f0",fg="#777")
label.pack(pady=5)

#create frame to hold emoji button and centre them
frame_button=tk.Frame(root,bg="#FCF8E8")
frame_button.pack(pady=20)

#button to choose the mood
button_happy=tk.Button(frame_button,text="Happy😊", font=("Arial",12), bg="#f8c9c9", relief="groove", command=lambda:set_mood("Happy")) #command=lambda is to bind a function to button/expression 
button_sad=tk.Button(frame_button,text="Sad😢", font=("Arial",12), bg="#f8c9c9", relief="groove", command=lambda:set_mood("Sad"))       #when button clicked lambda calls set_mood("") function
button_angry=tk.Button(frame_button,text="Angry😠", font=("Arial",12), bg="#f8c9c9", relief="groove", command=lambda:set_mood("Angry"))
button_excited=tk.Button(frame_button,text="Excited😆", font=("Arial",12), bg="#f8c9c9", relief="groove", command=lambda:set_mood("Excited"))
button_sleepy=tk.Button(frame_button,text="Sleepy😴", font=("Arial",12), bg="#f8c9c9", relief="groove", command=lambda:set_mood("Sleepy"))
button_relaxed=tk.Button(frame_button,text="Relaxed😌", font=("Arial",12), bg="#f8c9c9", relief="groove", command=lambda:set_mood("Relaxed"))

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
    
#run the whole program
root.mainloop()


