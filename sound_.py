import tkinter as tk
from PIL import Image,ImageTk
import pygame

#initialize pygame mixer
pygame.mixer.init()

#----------------------------------------------------------------------------------------------------------------------#

#load and resize the image using PIL 
def resize_image(image_path, size=(40,40)):
    img=Image.open(image_path)
    img=img.resize(size, Image.Resampling.LANCZOS) #Resampling=process of changing size of an image #LANCZOS=high quality resizing
    return ImageTk.PhotoImage(img)

#----------------------------------------------------------------------------------------------------------------------#

#function for buttons
def play_sound():
        print("Playing sound...") #(would replace them with real audio functionality)

def pause_sound():
        print("Pausing sound...")

def stop_sound():
        print("Stopping sound...")

def next_sound():
        print("Next sound...")

def prev_sound():
        print("Previous sound...")

#----------------------------------------------------------------------------------------------------------------------#

#function for volume control, it will be triggered when volume slider is moved
def set_volume(val): #val=the value when users slide the volume slider(val is originally a string)
    volume = float(val) #float=converts it into numbers 

#----------------------------------------------------------------------------------------------------------------------#

#main window
root=tk.Tk()
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}") #full-screen sized
root.title("Soothing Sound Player")
root.configure(bg="#e1f5fe") 

#----------------------------------------------------------------------------------------------------------------------#

#title
title=tk.Label(root,text="Relax Soothing Sound Player🎶", font=("Helvetica", 18, "bold"),bg="#e1f5fe",fg="#333")
title.pack(pady=(10,5)) #pady=(10,5)adds vertical spacing above and below.

#----------------------------------------------------------------------------------------------------------------------#

#frame to hold center and volume(right)
center_volume_frame=tk.Frame(root, bg="#e1f5fe")
center_volume_frame.pack(expand=True,fill="both",padx=30,pady=20)

#frame to hold playlist and buttons(left)
playlist_button_frame=tk.Frame(center_volume_frame,bg="#e1f5fe")
playlist_button_frame.pack(side="left",expand=True,fill="both", anchor="center",padx=(150,0))

#----------------------------------------------------------------------------------------------------------------------#

#label for now playing(since now dont have song yet,so display"no sound is playing")
label_now_playing=tk.Label(playlist_button_frame, text="No sound is playing.", bg="#e1f5fe", font=("Comic Sans MS", 12))
label_now_playing.pack(pady=(3,7))

#----------------------------------------------------------------------------------------------------------------------#
#PLAYLIST

#title for playlist
label_playlist=tk.Label(playlist_button_frame, text="Playlist🎧", bg="#e1f5fe", font=("Comic Sans MS", 14))
label_playlist.pack(pady=(0,5))

#the listbox to show available sound
playlist_box=tk.Listbox(playlist_button_frame, width=100, height=20, bg="white", fg="#333")
playlist_box.pack(pady=(0,5),anchor="center")

#hold all control button
button_frame=tk.Frame(playlist_button_frame,bg="#e1f5fe")
button_frame.pack(pady=(10,10),anchor="center")

#song lists
songs=["Rain sounds", "Ocean sounds"]

#loop through each elements in "songs" list
for songs in songs: #each element is temporarily stored in variable "songs" during each loop 
    playlist_box.insert(tk.END, songs) #tk.End=the song will be added to the end of the listbox

#----------------------------------------------------------------------------------------------------------------------#
#CONTROL BUTTON

#image for button
play_image=resize_image("C:/Users/qinen/project/moodify/play.png")
pause_image=resize_image("C:/Users/qinen/project/moodify/pause.png")
stop_image=resize_image("C:/Users/qinen/project/moodify/stop.png")
next_image=resize_image("C:/Users/qinen/project/moodify/next.png")
previous_image=resize_image("C:/Users/qinen/project/moodify/previous.png")

#Control buttons for the sound player
previous_button=tk.Button(button_frame, image=previous_image, command=prev_sound, relief="groove", bg="#0077be")
previous_button.pack(side="left",padx=10)
stop_button=tk.Button(button_frame, image=stop_image, command=stop_sound, relief="groove", bg="#0077be")
stop_button.pack(side="left",padx=10)
play_button=tk.Button(button_frame, image=play_image, command=play_sound, relief="groove", bg="#0077be")
play_button.pack(side="left",padx=10)
pause_button=tk.Button(button_frame, image=pause_image, command=pause_sound, relief="groove", bg="#0077be")
pause_button.pack(side="left",padx=10)
next_button=tk.Button(button_frame, image=next_image, command=next_sound, relief="groove", bg="#0077be")
next_button.pack(side="left",padx=10)

#----------------------------------------------------------------------------------------------------------------------#
#VOLUME CONTROL

volume_frame = tk.Frame(center_volume_frame, bg="#e1f5fe")
volume_frame.pack(side="right",anchor="n", padx=40)

volume_label = tk.Label(volume_frame, text="Volume 🔊", bg="#e1f5fe", font=("Times New Roman", 12))
volume_label.pack()

volume_control = tk.Scale(volume_frame, from_=0, to=30, resolution=1, orient="vertical", command=set_volume,
                          bg="#e1f5fe", fg="#333", troughcolor="#b2ebf2", width=15, sliderlength=20)
volume_control.pack()

#----------------------------------------------------------------------------------------------------------------------#

#the whole program run
root.mainloop()