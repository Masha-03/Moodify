import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import time #Animations
import pygame  #For background music
import sqlite3
from datetime import datetime

#Set default timings
INHALE = 4
HOLD = 7
EXHALE = 4

#Theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

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

get_profile()

class Timer:
    def __init__(self):
        
        #Profile is fetched and stored
        self.profile = profile
        
        #Initialize Pygame for music playback
        pygame.mixer.init()
        #Load the background music 
        pygame.mixer.music.load("tkinter pages/breathing/breathing.mp3")
        pygame.mixer.music.play(loops=-1)  # -1 for infinite loop
        
        #Initialise table
        def initialise_table(): 
                #Connect to database
                connect = sqlite3.connect('moodify_database.db')
                #Create cursor
                cursor = connect.cursor()
                
                #Create the table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS breathing_exercise (
                id INTEGER PRIMARY KEY,
                profile TEXT NOT NULL,
                date TEXT NOT NULL,
                completed_sessions INTEGER NOT NULL,
                FOREIGN KEY (profile) REFERENCES user_info(profile)
                )''')
                
                #Save data, update
                connect.commit()
                #Close connection
                connect.close()
                
        #Initialise table before GUI starts        
        initialise_table()
        
        #Window setup
        self.root = tk.Tk()
        self.root.state("zoomed")
        self.root.title("Breathing Exercise")
        self.root.configure(bg="#DDEFFB")  # Soft blue background    
        
        #Title
        title=tk.Label(self.root,text="Breathing Exercise",font=("Segoe UI",18,"bold"), bg="#DDEFFB", fg="#152238")
        title.pack(pady=30)
        
        #Main container frame
        self.container = ctk.CTkFrame(self.root, width=600, height=600, corner_radius=20, fg_color="#DDEFFB")
        self.container.place(relx=0.5, rely=0.5, anchor="center")
        
        #Canvas frame with rounded corners
        self.canvas_frame = ctk.CTkFrame(self.container, width=300, height=300, corner_radius=30)
        self.canvas_frame.grid(row=0, column=0, pady=(20, 10))

        #Canvas for breathing circle
        self.canvas = tk.Canvas(self.canvas_frame, width=300, height=300, bg="#DDEFFB", highlightthickness=0)
        self.canvas.pack()
        
        #Initial circle
        self.circle = self.canvas.create_oval(100, 100, 200, 200, fill="#add8e6", outline="#87ceeb")

        #Label to show current round number
        self.round_label = ctk.CTkLabel(self.container, text="ROUND 0 OF 3", font=("Arial", 20, "bold"), text_color="#152238", fg_color="#DDEFFB")
        self.round_label.grid(row=1, column=0, pady=(0, 10))

        #Label to show countdown timer and current phase
        self.timer_label = ctk.CTkLabel(self.container, text="", font=("Arial", 30, "bold"), text_color="#00008B", fg_color="#DDEFFB")
        self.timer_label.grid(row=2, column=0, pady=(10, 20))
        
        #Instruction label 
        self.instruction_label = ctk.CTkLabel(self.container, text="", font=("Arial", 18),  text_color="#4682B4", fg_color="#DDEFFB")
        self.instruction_label.grid(row=3, column=0, pady=(10, 20))

        #Frame to hold the Start and Stop buttons
        button_frame = ctk.CTkFrame(self.container, fg_color="#DDEFFB")
        button_frame.grid(row=4, column=0, pady=(10, 0))

        #Start button
        self.start_button = ctk.CTkButton(button_frame, text="START", command=self.start_timer, width=120, height=40, corner_radius=10, fg_color="#152238", hover_color="#228B22", font=("Arial", 15))
        self.start_button.grid(row=0, column=0, padx=(0, 20), ipady=10)

        #Stop button
        self.stop_button = ctk.CTkButton(button_frame, text="STOP", command=self.stop_timer, state=tk.DISABLED,width=120, height=40, corner_radius=10, fg_color="#152238", hover_color="#FF6347", font=("Arial", 15))
        self.stop_button.grid(row=0, column=1, ipady=10)

        #Total breathing cycles
        self.total_rounds = 3
        #Completed rounds
        self.rounds_completed = 0
        #Current phase
        self.phase = "inhale"
        #Time left
        self.time_remaining = INHALE       
        self.is_running = False     
        
        self.root.mainloop()
        
    def start_timer(self):
        self.is_running = True
        #Disable start button
        self.start_button.configure(state=tk.DISABLED) 
        #Enable stop button   
        self.stop_button.configure(state=tk.NORMAL)     
        self.rounds_completed = 0
        self.phase = "inhale"
        self.time_remaining = INHALE
        #Clear the completion message when starting a new session
        self.instruction_label.configure(text="Inhale deeply...")
        self.update_timer()

    def stop_timer(self):
        self.is_running = False
        #Clear label
        self.timer_label.configure(text="")
        #Reset round                     
        self.round_label.configure(text="ROUND 0 OF 3", font=("Arial", 20, "bold"),  text_color="#152238")   
        self.start_button.configure(state=tk.NORMAL)          
        #Disable stop
        self.stop_button.configure(state=tk.DISABLED)
        #Reset circle
        self.reset_circle()
        
        #Check if stopped midway or completed
        if self.rounds_completed >= self.total_rounds:
            #Display completion message if all rounds are done
            self.instruction_label.configure(text="You've completed your breathing exercise. Well done!")
            self.record_breathing_exercise()
        else:
            #Clear the instruction if stopped midway
            self.instruction_label.configure(text="")
        
    #Main loop that updates every second
    def update_timer(self):
        if not self.is_running:
            return

        #Show countdown and rounds 
        self.timer_label.configure(text=f"{self.time_remaining:02d}s - {self.phase.capitalize()}")
        self.round_label.configure(text=f"ROUND {self.rounds_completed + 1} OF {self.total_rounds}", font=("Arial", 20, "bold"),  text_color="#152238")

        #Animate the breathing circle based on phase
        self.animate_circle(self.phase)

        if self.time_remaining > 0:
            self.time_remaining -= 1
            #Update timer every second
            self.root.after(1000, self.update_timer)  
        else:
            #Move to the next phase when time runs out
            if self.phase == "inhale":
                self.phase = "hold"
                self.time_remaining = HOLD
                self.instruction_label.configure(text="Hold your breath...")
            elif self.phase == "hold":
                self.phase = "exhale"
                self.time_remaining = EXHALE
                self.instruction_label.configure(text="Exhale slowly...")
            elif self.phase == "exhale":
                self.rounds_completed += 1
                #After 3 rounds it stops
                if self.rounds_completed >= self.total_rounds:
                    self.instruction_label.configure(text="You've completed your breathing exercise. Well done!")
                    self.stop_timer()
                    return
                
                #Pause before starting the next round
                self.instruction_label.configure(text="Resting for 2 seconds...")
                self.timer_label.configure(text="2s - Rest")
                self.root.after(2000, self.start_next_round)  # 2-second pause
                return
            
            #Start the timer
            self.update_timer()
            
    def start_next_round(self):
        self.phase = "inhale"
        self.time_remaining = INHALE
        self.instruction_label.configure(text="Inhale deeply...")
        #Start the timer for the new phase
        self.update_timer()
            
    #Adjust the size of the circle            
    def animate_circle(self, phase):
        if not self.is_running or phase == "hold":
            self.reset_circle()
            return

        if phase == "inhale":
            self.animate_resize(100, 75, 200, 225, duration=4)
        elif phase == "exhale":
            self.animate_resize(75, 100, 225, 200, duration=4)

    def animate_resize(self, start_x0, end_x0, start_x1, end_x1, duration):
        start_time = time.time()
        fps = 60

        def animate():
            #Doesn't animate circle during hold
            if not self.is_running or self.phase == "hold":
                return

            #Current time
            now = time.time()
            #How much time passed since animation started
            progress = min((now - start_time) / duration, 1.0)

            #For smooth animation(linear interpolation)
            new_x0 = start_x0 + (end_x0 - start_x0) * progress
            new_x1 = start_x1 + (end_x1 - start_x1) * progress
            #Updates coordinates of circle
            self.canvas.coords(self.circle, new_x0, new_x0, new_x1, new_x1)

            if progress < 1.0: #Animation not complete yet
                self.root.after(16, animate)  #60fps
            else: #Animation complete
                self.canvas.coords(self.circle, end_x0, end_x0, end_x1, end_x1)

        animate()
            
    def reset_circle(self):
        #Return the circle to its default size
        self.canvas.coords(self.circle, 100, 100, 200, 200)
        
    def record_breathing_exercise(self):
        #Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        #Connect to the database
        connect = sqlite3.connect('moodify_database.db')
        cursor = connect.cursor()

       #Check if an entry for the current date and profile already exists
        cursor.execute('''
            SELECT completed_sessions FROM breathing_exercise 
            WHERE profile = ? AND date = ?
        ''', (self.profile, current_date))
        
        result = cursor.fetchone()

        if result:
            #If entry exists, increment the completed sessions
            updated_sessions = result[0] + 1
            cursor.execute('''
                UPDATE breathing_exercise 
                SET completed_sessions = ? 
                WHERE profile = ? AND date = ?
            ''', (updated_sessions, self.profile, current_date))
        else:
            #If no entry exists, insert a new record
            cursor.execute('''
                INSERT INTO breathing_exercise (profile, date, completed_sessions) 
                VALUES (?, ?, ?)
            ''', (self.profile, current_date, 1))

        connect.commit()
        connect.close()
            
Timer()