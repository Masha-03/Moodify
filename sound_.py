import tkinter as tk

#function for buttons
def play_sound():
        print("Playing sound...")

def pause_sound():
        print("Pausing sound...")

def resume_sound():
        print("Resuming sound...")

def stop_sound():
        print("Stopping sound...")

def next_sound():
        print("Next sound...")

def prev_sound():
        print("Previous sound...")

#----------------------------------------------------------------------------------------------------------------------#

#function for volume
def set_volume(val): #val=the value when users slide the volume slider(val is originally a string)
    volume = float(val) #float=converts it into numbers 
    print(f"Volume: {volume}")

#----------------------------------------------------------------------------------------------------------------------#

#main window
root=tk.Tk()
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}") 
root.title("Soothing Sound Player")
root.configure(bg="#e1f5fe") 

#----------------------------------------------------------------------------------------------------------------------#

#title
title=tk.Label(root,text="Relax Soothing Sound Player🎶", font=("Helvetica", 18, "bold"),bg="#e1f5fe",fg="#333")
title.pack(pady=(10,5))

#----------------------------------------------------------------------------------------------------------------------#

#frame to hold center and volume(left)
center_volume_frame=tk.Frame(root, bg="#e1f5fe")
center_volume_frame.pack(expand=True,fill="both",padx=30,pady=20)

#frame to hold playlist and buttons
playlist_button_frame=tk.Frame(center_volume_frame,bg="#e1f5fe")
playlist_button_frame.pack(side="left",expand=True,fill="both", anchor="center",padx=(150,0))

#----------------------------------------------------------------------------------------------------------------------#

#label for now playing
label_now_playing=tk.Label(playlist_button_frame, text="No sound is playing.", bg="#e1f5fe", font=("Comic Sans MS", 12))
label_now_playing.pack(pady=(3,7))

#----------------------------------------------------------------------------------------------------------------------#
#PLAYLIST

#label for playlist
label_playlist=tk.Label(playlist_button_frame, text="Playlist🎧", bg="#e1f5fe", font=("Comic Sans MS", 14))
label_playlist.pack(pady=(0,5))

#the box of playlist
playlist_box=tk.Listbox(playlist_button_frame, width=100, height=20, bg="white", fg="#333")
playlist_box.pack(pady=(0,5),anchor="center")

#frame for button
button_frame=tk.Frame(playlist_button_frame,bg="#e1f5fe")
button_frame.pack(pady=(10,10),anchor="center")

songs=["Rain sounds", "Ocean sounds"]

for songs in songs:
    playlist_box.insert(tk.END, songs)

#----------------------------------------------------------------------------------------------------------------------#
#CONTROL BUTTON

#Control buttons for the sound player
play_button=tk.Button(button_frame, text="▶️ Play", command=play_sound, relief="raised", bg="#4dd0e1")
play_button.pack(side="left",padx=10)
pause_button=tk.Button(button_frame, text="⏸️ Pause", command=pause_sound, relief="raised", bg="#4dd0e1")
pause_button.pack(side="left",padx=10)
resume_button=tk.Button(button_frame, text="▶️ Resume", command=resume_sound, relief="raised", bg="#4dd0e1")
resume_button.pack(side="left",padx=10)
stop_button=tk.Button(button_frame, text="⏹️ Stop", command=stop_sound, relief="raised", bg="#4dd0e1")
stop_button.pack(side="left",padx=10)
next_button=tk.Button(button_frame, text="⏭️ Next", command=next_sound, relief="raised", bg="#4dd0e1")
next_button.pack(side="left",padx=10)
previous_button=tk.Button(button_frame, text="⏮️ Previous", command=prev_sound, relief="raised", bg="#4dd0e1")
previous_button.pack(side="left",padx=10)

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