import tkinter as tk
from PIL import Image,ImageTk
import pygame #for pygame.mixer

#initialize pygame mixer
pygame.mixer.init()

#----------------------------------------------------------------------------------------------------------------------#

#load and resize the image using PIL 
def resize_image(image_path, size=(40,40)):
    img=Image.open(image_path)
    img=img.resize(size, Image.Resampling.LANCZOS) #Resampling=process of changing size of an image #LANCZOS=high quality resizing
    return ImageTk.PhotoImage(img)

#----------------------------------------------------------------------------------------------------------------------#
#import sound from file

#song dictionary
song_dict={
       "Rain sounds":"C:/Users/qinen/project/moodify/rain.mp3",
       "Ocean waves sounds":"C:/Users/qinen/project/moodify/ocean.mp3",
       "Spring sounds":"C:/Users/qinen/project/moodify/bird.mp3",
       "Clicking keyboard sounds":"C:/Users/qinen/project/moodify/keyboard.mp3",
       "Waterfall sounds":"C:/Users/qinen/project/moodify/waterfall.mp3"
}

#----------------------------------------------------------------------------------------------------------------------#

#function for buttons
def play_sound():
        selected=playlist_box.get(tk.ACTIVE) #get current selected song name from listbox
        if selected:
               pygame.mixer.music.load(song_dict[selected])  #loads mp3 file
               pygame.mixer.music.play() #start playing the sound 
               label_now_playing.config(text=f"Now Playing: {selected}") #update label to display what currently playing

def pause_sound():
        pygame.mixer.music.pause() #pause current playing sound

def stop_sound():
        pygame.mixer.music.stop() #stop current playing sound
        label_now_playing.config(text="No sound is playing.") #update label to inform there is nothing playing

def next_sound():
    current_index = playlist_box.curselection() #curselection()=returns tuple of selected index(get current song's index)
    if current_index:
        next_index = (current_index[0] + 1) % playlist_box.size() #(current_index[0] + 1)=adds 1 to move to the next item #% playlist_box.size()=ensures that if you are at the last item, it loops back to the first
        playlist_box.selection_clear(0, tk.END) #unselects all
        playlist_box.selection_set(next_index)
        playlist_box.activate(next_index) #select next song
        play_sound()

def prev_sound():
    current_index = playlist_box.curselection()
    if current_index:
        prev_index = (current_index[0] - 1) % playlist_box.size()
        playlist_box.selection_clear(0, tk.END)
        playlist_box.selection_set(prev_index)
        playlist_box.activate(prev_index)
        play_sound()

#----------------------------------------------------------------------------------------------------------------------#

#function for volume control, it will be triggered when volume slider is moved
def set_volume(val): #val=the value when users slide the volume slider(val is originally a string)
    volume = float(val) /30  #float=converts it into numbers #/30=divides it by 30 to scale it down to a number between 0.0 and 1.0.
    pygame.mixer.music.set_volume(volume) #set actual sound volume

#----------------------------------------------------------------------------------------------------------------------#

#main window
root=tk.Tk()
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}") #full-screen sized
root.title("Soothing Sound Player")
root.configure(bg="#e1f5fe") 

#----------------------------------------------------------------------------------------------------------------------#

#title
title=tk.Label(root,text="Relax Soothing Sound Player🎶", font=("Segoe UI", 18, "bold"),bg="#e1f5fe",fg="#01579b")
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
label_now_playing=tk.Label(playlist_button_frame, text="No sound is playing.", bg="#e1f5fe", font=("Segoe UI", 13,"bold"))
label_now_playing.pack(pady=(3,7))

#----------------------------------------------------------------------------------------------------------------------#
#PLAYLIST

#title for playlist
label_playlist=tk.Label(playlist_button_frame, text="Playlist🎧", bg="#e1f5fe", font=("Comic Sans MS", 15))
label_playlist.pack(pady=(0,5))

#the listbox to show available sound
playlist_box=tk.Listbox(playlist_button_frame, width=100, height=20, bg="white", fg="#1a237e",selectbackground="#bbdefb", selectforeground="#0d47a1")
playlist_box.pack(pady=(0,5),anchor="center")

#hold all control button
button_frame=tk.Frame(playlist_button_frame,bg="#e1f5fe")
button_frame.pack(pady=(10,10),anchor="center")

#loop through each elements in the dictionary which is "song_dict"
for song_name in song_dict: #each element is temporarily stored in variable "song_name" during each loop 
    playlist_box.insert(tk.END, song_name) #tk.End=the song will be added to the end of the listbox

#----------------------------------------------------------------------------------------------------------------------#
#CONTROL BUTTON

#image for button
play_image=resize_image("C:/Users/qinen/project/moodify/play.png")
pause_image=resize_image("C:/Users/qinen/project/moodify/pause.png")
stop_image=resize_image("C:/Users/qinen/project/moodify/stop.png")
next_image=resize_image("C:/Users/qinen/project/moodify/next.png")
previous_image=resize_image("C:/Users/qinen/project/moodify/previous.png")

#Control buttons for the sound player
previous_button=tk.Button(button_frame, image=previous_image, command=prev_sound, relief="flat", bg="#4fc3f7", activebackground="#29b6f6",bd=0, highlightthickness=0)
previous_button.pack(side="left",padx=10)
stop_button=tk.Button(button_frame, image=stop_image, command=stop_sound, relief="flat", bg="#4fc3f7", activebackground="#29b6f6",bd=0, highlightthickness=0)
stop_button.pack(side="left",padx=10)
play_button=tk.Button(button_frame, image=play_image, command=play_sound, relief="flat", bg="#4fc3f7", activebackground="#29b6f6",bd=0, highlightthickness=0)
play_button.pack(side="left",padx=10)
pause_button=tk.Button(button_frame, image=pause_image, command=pause_sound, relief="flat", bg="#4fc3f7", activebackground="#29b6f6",bd=0, highlightthickness=0)
pause_button.pack(side="left",padx=10)
next_button=tk.Button(button_frame, image=next_image, command=next_sound, relief="flat", bg="#4fc3f7", activebackground="#29b6f6",bd=0, highlightthickness=0)
next_button.pack(side="left",padx=10)

#----------------------------------------------------------------------------------------------------------------------#
#VOLUME CONTROL

volume_frame = tk.Frame(center_volume_frame, bg="#e1f5fe")
volume_frame.pack(side="right",anchor="n", padx=40)

volume_label = tk.Label(volume_frame, text="Volume 🔊", bg="#e1f5fe", fg="#0d47a1", font=("Segoe UI", 12))
volume_label.pack()

#volume control slider                                 #resolution=1:slider moves in steps of 1 unit                                   #troughcolor=the track colour
volume_control = tk.Scale(volume_frame, from_=0, to=30, resolution=1, orient="vertical", command=set_volume,bg="#e1f5fe", fg="#0d47a1", troughcolor="#b3e5fc", width=15, sliderlength=20)
volume_control.set(15) #set default volume position to 15,like when users open this window the volume will be at 15
volume_control.pack()

#----------------------------------------------------------------------------------------------------------------------#

#the whole program run
root.mainloop()