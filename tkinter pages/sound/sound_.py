import tkinter as tk #hover effect-event binding 
from tkinter import ttk #provide theme widgets #for the layout of progress bar
from PIL import Image,ImageTk
import pygame #for pygame.mixer and inside the progress bar(handle audio playback and get current position of the song)
import os
import customtkinter as ctk

#initialize pygame mixer
pygame.mixer.init()

# Base directory of the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths for assets
AUDIO_DIR = BASE_DIR
IMAGE_DIR = BASE_DIR

#----------------------------------------------------------------------------------------------------------------------#

#load and resize the image using PIL 
def resize_image(image_name, size=(40,40)):
    image_path = os.path.join(IMAGE_DIR, image_name)
    img=Image.open(image_path)
    img=img.resize(size, Image.Resampling.LANCZOS) #Resampling=process of changing size of an image #LANCZOS=high quality resizing
    return ImageTk.PhotoImage(img)

#----------------------------------------------------------------------------------------------------------------------#
#import sound from file

#song dictionary
song_dict={
    "Rain sounds": os.path.join(AUDIO_DIR, "rain.mp3"),
    "Ocean waves sounds": os.path.join(AUDIO_DIR, "ocean.mp3"),
    "Spring sounds": os.path.join(AUDIO_DIR, "bird.mp3"),
    "Clicking keyboard sounds": os.path.join(AUDIO_DIR, "keyboard.mp3"),
    "Waterfall sounds": os.path.join(AUDIO_DIR, "waterfall.mp3")
}

#----------------------------------------------------------------------------------------------------------------------#

#current song duration and position(to make progress bar)(in milliseconds)
current_duration=0 #total length of current song
current_postion=0 #current playback position
is_playing=False #check whether if a song is playing #when program starts,no song is playing,so set to False first
current_song=None #keep track to current playing song to handle resuming #before users select a song,there is no song to tract,so set to None

#----------------------------------------------------------------------------------------------------------------------#

#function to update the progress bar
def update_progress_bar():
    global is_playing #means I want to use is_playing variable that was defined outside the function, not create a new local variable named is_playing
                      #means global bring is_playing variable which is at outside,inside this function
    
    #check if a song is playing
    if is_playing:
        current_position = pygame.mixer.music.get_pos()  #get the current position (in milliseconds)
        
        #calculate progress percentage(the green line)(using ttk)
        if current_duration > 0: #check if current song has valid duration(greater than 0)
            progress = (current_position / current_duration) * 100 #formula to calculate percentage,use to fill in the progress bar
            progress_bar['value'] = progress #updates progress bar with calculated percentage

        #check if the sound has finished #only run when no sound is playing
        if not pygame.mixer.music.get_busy(): #check whether sound sound is currently playing
            is_playing = False #functions return False if not playing
            progress_bar['value'] = 0 #set progress bar value to 0
            duration_label.config(text="00:00") #display

    #progress bar will be filled in every after 500ms
    root.after(500, update_progress_bar) #500=delay time in milliseconds,500=0.5 seconds #update_progress_bar will be called after 500ms delay
                                         #choose 500 is because it provides a balance between smooth updates and not overwhelming the CPU.
#----------------------------------------------------------------------------------------------------------------------#

#function for buttons
def play_sound():
        global current_duration,is_playing,current_postion,current_song
        selected=playlist_box.get(tk.ACTIVE) #get current selected song name from listbox #from the playlist box to get active item,like if users clicked rain sounds then it would be an active item

        #check if currently selected song is not same as the currently playing song
        if selected != current_song: #!=:not same
               pygame.mixer.music.load(song_dict[selected])  #loads mp3 file #load but doesn't playing yet
               pygame.mixer.music.play(start=current_postion/100) #play sound #start the song at 1/10th of the original time.
               current_song=selected #update to newly selected song
               current_postion=0 #starting from beginning so from 0
               current_duration = pygame.mixer.Sound(song_dict[selected]).get_length() * 1000 #get song length (in milliseconds)
               total_seconds = int(current_duration // 1000) #convert duration from milliseconds to seconds #int()=ensures result is in integer
               minutes = total_seconds // 60 #splits it into minutes
               seconds = total_seconds % 60 #splits it into seconds
               duration_label.config(text=f"{minutes:02}:{seconds:02}") #update duration label #:02=ensures two digits for both minutes and seconds
               label_now_playing.config(text=f"Now Playing: {selected}") #update label to display what currently playing
               update_progress_bar()
        else:
             pygame.mixer.music.unpause() #resume playback of song that was previously paused
             label_now_playing.config(text=f"Resuming: {selected}")

        is_playing=True #sound is currently playing
        update_progress_bar()

def pause_sound():
        global is_playing,current_postion
        pygame.mixer.music.pause() #pause current playing sound
        current_postion=pygame.mixer.music.get_pos() #get current position
        is_playing=False #not playing
        label_now_playing.config(text=f"Paused: {playlist_box.get(tk.ACTIVE)}")

def stop_sound():
        global is_playing
        pygame.mixer.music.stop() #stop current playing sound
        is_playing=False #not playing
        label_now_playing.config(text="No sound is playing.") #update label to inform there is nothing playing
        current_postion=0 #go back to 0

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
    volume = float(val) /100  #float=converts it into numbers #/100=divides it by 30 to scale it down to a number between 0.0 and 1.0.
    pygame.mixer.music.set_volume(volume) #set actual sound volume

#----------------------------------------------------------------------------------------------------------------------#

#hover effect function #they bound to widgets by using .bind()
def enter(event): #when mouse enter a widget(eg.button) it changes the widget's background to bg="#DDE6ED" #event=event subject
    event.widget.config(bg="#b8daae",width=44, height=44) #when mouse touch the button,the button will become bigger

def leave(event): #when mouse leave the widget, background colour returns to bg="#FFFFFF"
    event.widget.config(bg="#b8daae",width=40, height=40)#when mouse went out of the button,the button will reset to original size

def get_image_path(filename):
    # This gets the path of the current Python file
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)
#----------------------------------------------------------------------------------------------------------------------#

#main window
root=tk.Tk()
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}") #full-screen sized
root.title("Soothing Sound Player")

# Load and set background image
bg_image = Image.open(get_image_path("sound_bg.png"))  # Replace with your image file
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
#----------------------------------------------------------------------------------------------------------------------#

#title
title=tk.Label(root,text="Relax Soothing Sound Player🎶", font=("Segoe UI", 18, "bold"),bg="#d9e9df",fg="black")
title.pack(pady=(10,5)) #pady=(10,5)adds vertical spacing above and below.

#----------------------------------------------------------------------------------------------------------------------#

#frame to hold center and volume(right)
center_volume_frame=tk.Frame(root, bg="#d9e9df")
center_volume_frame.pack(expand=True,fill="both",padx=30,pady=20)

#frame to hold playlist and buttons(left)
playlist_button_frame=tk.Frame(center_volume_frame,bg="#d9e9df")
playlist_button_frame.pack(side="left",expand=True,fill="both", anchor="center",padx=(150,0))

#----------------------------------------------------------------------------------------------------------------------#

#label for now playing(since now dont have song yet,so display"no sound is playing")
label_now_playing=tk.Label(playlist_button_frame, text="No sound is playing.", bg="#d9e9df", font=("Segoe UI", 13,"bold"))
label_now_playing.pack(pady=(3,7))

#----------------------------------------------------------------------------------------------------------------------#
#PLAYLIST

#title for playlist
label_playlist=tk.Label(playlist_button_frame, text="Playlist🎧", bg="#d9e9df", font=("Comic Sans MS", 13))
label_playlist.pack(pady=(0,5))

#the listbox to show available sound
playlist_box=tk.Listbox(playlist_button_frame, width=100, height=20, bg="white", fg="#1a237e",selectbackground="#a3d2ca", selectforeground="black",activestyle="none", font=("Segoe UI", 10, "italic"),bd=2, relief="groove",highlightthickness=2)
playlist_box.pack(pady=(0,5),anchor="center")

#loop through each elements in the dictionary which is "song_dict"
for song_name in song_dict: #each element is temporarily stored in variable "song_name" during each loop 
    playlist_box.insert(tk.END, song_name) #tk.End=the song will be added to the end of the listbox

#----------------------------------------------------------------------------------------------------------------------#
#Progress bar(ttk)

#progress bar frame
progress_frame = tk.Frame(playlist_button_frame, bg="#d9e9df")
progress_frame.pack(pady=(5, 10), fill="x")

#progress bar
progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate") #mode="determinate":bar filled as percentage(from 0 to 100)
progress_bar.pack(side="left", expand=True, fill="x", padx=(5, 5))

#----------------------------------------------------------------------------------------------------------------------#
#Duration

#label to display the sound duration
duration_label = tk.Label(progress_frame, text="00:00", bg="#d9e9df", font=("Segoe UI", 10))
duration_label.pack(side="left", padx=(5, 10))

#----------------------------------------------------------------------------------------------------------------------#
#CONTROL BUTTON

#hold all control button
button_frame=tk.Frame(playlist_button_frame,bg="#d9e9df")
button_frame.pack(pady=(10,15))

#image for button
play_image = resize_image("play.png")
pause_image = resize_image("pause.png")
stop_image = resize_image("stop.png")
next_image = resize_image("next.png")
previous_image = resize_image("previous.png")

#store references to all button images.If no,image might get garbage collected by Python, cause them to disappear
image_references = [previous_image,stop_image,play_image, pause_image, next_image]

#----------------------------------------------------------------------------------------------------------------------#

#function to create button
def create_button(frame, image,command): #frame=where button will be place #image=image that display on the button #command=function to be executed when button is clicked
    #create button
    button = tk.Button(frame, image=image, bg="#78a45c", relief="groove", command=command,cursor="hand2") #command=command:function that will be called when the button is clicked
    button.image = image  #assigns image to a property of the button object itself.Prevent garbage collection,ensure the image remain visible                                                 #cursor=hand2:make the mouse become a small hand when clicking the button
    button.bind("<Enter>", enter)  #when mouse enter the button area,enter() function will be triggered
    button.bind("<Leave>", leave) #when mouse went out the button area,leave() function will be triggered
    return button  #exit a function and send a value back to the caller

#----------------------------------------------------------------------------------------------------------------------#

#create and arrange the position of buttons  
button_previous = create_button(button_frame, previous_image, prev_sound)
button_previous.grid(row=0, column=0, padx=10, pady=5) #column=to adjust the position from left to right
button_stop = create_button(button_frame, stop_image, stop_sound)
button_stop.grid(row=0, column=1, padx=10, pady=5)
button_play = create_button(button_frame, play_image, play_sound)
button_play.grid(row=0, column=2, padx=10, pady=5)
button_pause = create_button(button_frame, pause_image, pause_sound)
button_pause.grid(row=0, column=3, padx=10, pady=5)
button_next = create_button(button_frame, next_image, next_sound)
button_next.grid(row=0, column=4, padx=10, pady=5)


#----------------------------------------------------------------------------------------------------------------------#
#VOLUME CONTROL

volume_frame = tk.Frame(center_volume_frame, bg="#d9e9df")
volume_frame.pack(side="right",anchor="n", padx=40)

volume_label = tk.Label(volume_frame, text="Volume 🔊", bg="#d9e9df", fg="#5e7f68", font=("Segoe UI", 12))
volume_label.pack()

#volume control slider                                 #resolution=1:slider moves in steps of 1 unit                                   #troughcolor=the track colour
volume_control = tk.Scale(volume_frame, from_=0, to=100, resolution=1, orient="vertical", command=set_volume,bg="#d9e9df", fg="#5e7f68", troughcolor="#7fa06a", width=15, sliderlength=20)
volume_control.set(50) #set default volume position to 50,like when users open this window the volume will be at 50
volume_control.pack()

#----------------------------------------------------------------------------------------------------------------------#

#Track fullscreen state
is_fullscreen = [False]

# Toggle fullscreen using the 'f' key
def toggle_fullscreen(event=None):
    is_fullscreen[0] = not is_fullscreen[0]
    root.attributes("-fullscreen", is_fullscreen[0])

# Bind the 'f' key (lowercase only)
root.bind("<Control-f>", toggle_fullscreen)

#-----------------------------------------------------------------------------------------------------------------------#

#the whole program run
root.mainloop()