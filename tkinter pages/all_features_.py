import tkinter as tk
from PIL import Image,ImageTk

#load and resize the image using PIL 
def resize_image(image_path, size=(70,70)):
    img=Image.open(image_path)
    img=img.resize(size, Image.Resampling.LANCZOS) #Resampling=process of changing size of an image #LANCZOS=high quality resizing
    return ImageTk.PhotoImage(img)

#------------------------------------------------------------------------------------------------------------------------------------------------#

#hover effect function #they bound to widgets by using .bind()
def enter(event): #when mouse enter a widget(eg.button) it changes the widget's background to bg="#DDE6ED" #event=event subject
    event.widget.config(bg="#DDE6ED") #changing the properties of the widget that triggered the event

def leave(event): #when mouse leave the widget, background colour returns to bg="#FFFFFF"
    event.widget.config(bg="#FFFFFF")

#------------------------------------------------------------------------------------------------------------------------------------------------#

#main window
root=tk.Tk() #create the main app window
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")  #Full-screen size   
root.title("All Features")
root.configure(bg="#F0F9F1") #change the background color of entire window

#------------------------------------------------------------------------------------------------------------------------------------------------#

#title
title_label = tk.Label(root, text="Welcome To Your Mental Health App--Moodify🌿", font=("Segoe UI", 20, "bold"), bg="#F0F9F1",fg="#2F4F4F")
title_label.pack(pady=(40,30))

#------------------------------------------------------------------------------------------------------------------------------------------------#

#subtitle
label=tk.Label(root,text="Choose a feature to start your self-care journey!",font=("Segoe UI",14),bg="#F0F9F1",fg="#4F7061")
label.pack(pady=(0,40))

#------------------------------------------------------------------------------------------------------------------------------------------------#
#For the button

#hold four features in a row
feature_frame=tk.Frame(root,bg="#F0F9F1")
feature_frame.pack()

#import the image
diary_image=resize_image("C:/Users/qinen/project/moodify/diary.png")
calendar_image=resize_image("C:/Users/qinen/project/moodify/calendar.png")
moodtracker_image=resize_image("C:/Users/qinen/project/moodify/moodtracker.png")
sound_image=resize_image("C:/Users/qinen/project/moodify/sound.png")
hourglass_image=resize_image("C:/Users/qinen/project/moodify/hourglass.png")

#create a single feature card
def create_feature(parent, image, text): #parent=where to place the card #image=the image you want to show #text=label below the image
    card = tk.Frame(parent, bg="#FFFFFF", width=140, height=140, relief="raised", bd=2) #card=a white frame acts as background box for button and label
    card.pack_propagate(False) #prevent auto resizing to fit content
    card.grid_propagate(False) #prevent auto resizing to fit content

    #button
    button = tk.Button(card, image=image, bg="#FFFFFF", relief="flat", activebackground="#D0F0E0",bd=0,cursor="hand2") #button that display the image #the background when pressed
    button.image = image                                                                                               #cursor=hand2:make the mouse become a small hand when clicking the button
    button.pack(pady=(12, 6))
    
    #label
    label = tk.Label(card, text=text, font=("Segoe UI", 11, "bold"), bg="#FFFFFF", fg="#444")
    label.pack()

    #hover effect changes
    def card_enter(event): #when move the mouse into of the card, all parts of it change color together
        card.config(bg="#D0F0E0")
        button.config(bg="#D0F0E0", activebackground="#D0F0E0")
        label.config(bg="#D0F0E0")

    def card_leave(event): #when move the mouse out of the card, all parts of it change color together
        card.config(bg="#FFFFFF")
        button.config(bg="#FFFFFF", activebackground="#FFFFFF")
        label.config(bg="#FFFFFF")

    #bind hover functions to all parts card including frame,image button and label
    widgets = [card, button, label]
    for w in widgets:
        w.bind("<Enter>", card_enter)
        w.bind("<Leave>", card_leave)

    return card #returns full card widget so can place it anywhere on the screen

#to display the cards (image and label)
features = [
    (diary_image, "Diary"),
    (calendar_image, "Calendar"),
    (moodtracker_image, "Mood Tracker"),
    (sound_image, "Soothing Sounds"),
    (hourglass_image, "Breathing Timer")
]

#loop through each image/text pair
for i, (img, text) in enumerate(features): #enumerate=use it when loop through a list and also to keep track of the index (position) of the items in that list
    card = create_feature(feature_frame, img, text) #call create_feature() to make a card
    card.grid(row=0, column=i, padx=20, pady=10)

#------------------------------------------------------------------------------------------------------------------------------------------------#

#the whole program run
root.mainloop()