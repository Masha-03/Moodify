import customtkinter as ctk
from PIL import Image, ImageTk #Handle and display images
import tkinter as tk
import time #Animations
import pygame  #For background music
import sqlite3
from datetime import datetime
import os
import sys
from tkinter import messagebox

# --- Asset Helper Function (for PyInstaller compatibility) ---
def resource_path(*relative_path_parts):
    """
    Returns the absolute path to a resource, whether running as a script
    or as a PyInstaller bundled executable.
    """
    try:
        # PyInstaller creates a temp folder and sets _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Not running as a PyInstaller executable, use current script directory
        base_path = os.path.dirname(os.path.abspath(_file_))

    return os.path.join(base_path, *relative_path_parts)

def get_db_path():
    base_dir = None
    if getattr(sys, 'frozen', False):
        # When frozen (e.g., PyInstaller), sys._MEIPASS is the root where bundled files are.
        # If your 'database' folder is alongside the executable in the *final distributed package*,
        # you might need to adjust this depending on your PyInstaller --add-data configuration.
        # For now, let's assume the database folder is at the same level as the executable.
        app_root = sys._MEIPASS
    else:
        # In unfrozen mode, base_dir is 'c:\Users\Coshi\Moodify\tkinter pages'.
        # We need to go up one level to 'c:\Users\Coshi\Moodify'.
        script_dir = os.path.dirname(os.path.abspath(__file__)) # This is 'c:\Users\Coshi\Moodify\tkinter pages'
        app_root = os.path.dirname(script_dir) # This steps up to 'c:\Users\Coshi\Moodify'

    db_file_name = 'moodify_database.db'
    db_folder_name = 'database'

    # Now, join the app_root with the database folder and the file name
    db_path = os.path.join(app_root, db_folder_name, db_file_name)

    print(f"Running in {'frozen' if getattr(sys, 'frozen', False) else 'unfrozen'} mode.")
    print(f"Detected script directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Calculated application root: {app_root}")
    print(f"Calculated database path: {db_path}")

    return db_path

database_file_path = get_db_path()

# Check if the database file exists at the calculated path
if os.path.exists(database_file_path):
    print(f"Database file FOUND at: {database_file_path}")
else:
    print(f"Database file NOT FOUND at: {database_file_path}")
    print("WARNING: A new database file will likely be created here.")
    # Create the 'database' folder if it doesn't exist
    try:
        os.makedirs(os.path.dirname(database_file_path), exist_ok=True)
        print(f"Created directory: {os.path.dirname(database_file_path)}")
    except OSError as e:
        print(f"Error creating directory: {e}")

#Get profile from the database
def get_profile():
    global profile
    connect = sqlite3.connect(database_file_path)
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

class Timer474(ctk.CTkFrame):
    #Set default timings
    INHALE = 4
    HOLD = 7
    EXHALE = 4
        
    def __init__(self, parent, back_callback=None):    
        super().__init__(parent)
        self.parent = parent
        self.parent.configure(fg_color="#DDEFFB")
        self.back_callback = back_callback 
        
        global profile
        self.profile = profile
        
        #Initialize Pygame for music playback
        pygame.mixer.init()
        #Gets the directory of the current script
        base_dir = os.path.dirname(os.path.abspath(__file__))  
        audio_path = os.path.join(base_dir, "breathing.mp3")
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play(loops=-1)  # -1 for infinite loop

        #Initialise table
        def initialise_table(): 
                #Connect to database
                connect = sqlite3.connect(database_file_path)
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
        
        #Title
        self.title=tk.Label(self.parent,text="4-7-4 Breathing Exercise",font=("Segoe UI",18,"bold"), bg="#DDEFFB", fg="#152238")
        self.title.pack(pady=10, fill='x')
            
        backbutton_frame = ctk.CTkFrame(self.parent, width=30, height=30, corner_radius=50, fg_color="#DDEFFB")
        backbutton_frame.pack(side='top', anchor='w', padx=20, pady=20)

        back_button = ctk.CTkButton(backbutton_frame, text="⬅", width=30, command=self.back_callback)
        back_button.configure(fg_color="#152238", text_color="#FFFFFF", font=("Segoe UI", 20, "bold"), hover_color="#80B6E2")
        back_button.pack(pady=5)

        #Main container frame
        self.container = ctk.CTkFrame(self.parent, width=600, height=600, corner_radius=20, fg_color="#DDEFFB")
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
        self.time_remaining = self.INHALE       
        self.is_running = False     
        
        self.parent.mainloop()
        
    def start_timer(self):
        self.is_running = True
        #Disable start button
        self.start_button.configure(state=tk.DISABLED) 
        #Enable stop button   
        self.stop_button.configure(state=tk.NORMAL)     
        self.rounds_completed = 0
        self.phase = "inhale"
        self.time_remaining = self.INHALE
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

        #Only animate during inhale and exhale
        if self.phase == "inhale":
            self.animate_circle("inhale")
        elif self.phase == "exhale":
            self.animate_circle("exhale")
        else:
            # Cancel any running animation during rest or hold
            if self.animation_job:
                self.parent.after_cancel(self.animation_job)
                self.animation_job = None
            self.reset_circle()

        if self.time_remaining > 0:
            self.time_remaining -= 1
            #Update timer every second
            self.parent.after(1000, self.update_timer)  
        else:
            #Move to the next phase when time runs out
            if self.phase == "inhale":
                self.phase = "hold"
                self.time_remaining = self.HOLD
                self.instruction_label.configure(text="Hold your breath...")
            elif self.phase == "hold":
                self.phase = "exhale"
                self.time_remaining = self.EXHALE
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
                self.phase = "rest"
                self.timer_label.configure(text="2s - Rest")
                self.parent.after(2000, self.start_next_round)  # 2-second pause
                return
            
            #Start the timer
            self.update_timer()
            
    def start_next_round(self):
        self.phase = "inhale"
        self.time_remaining = self.INHALE
        self.instruction_label.configure(text="Inhale deeply...")
        #Start the timer for the new phase
        self.update_timer()
            
    #Adjust the size of the circle            
    def animate_circle(self, phase):
        if not self.is_running or phase in ["hold", "rest"]:
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
            if not self.is_running or self.phase not in ["inhale", "exhale"]:
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

            if progress < 1.0 and self.is_running: #Animation not complete yet
                 self.animation_job = self.parent.after(int(1000 / fps), animate)
            else: #Animation complete
                self.animation_job = None

        animate()
            
    def reset_circle(self):
        #Return the circle to its default size
        self.canvas.coords(self.circle, 100, 100, 200, 200)
        
    def record_breathing_exercise(self):
        #Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        #Connect to the database
        connect = sqlite3.connect(database_file_path)
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

################################################################################################################################################################################

class Timer478(ctk.CTkFrame):
    #Set default timings
    INHALE = 4
    HOLD = 7
    EXHALE = 8
        
    def __init__(self, parent, back_callback=None):    
        super().__init__(parent)
        self.parent = parent
        self.parent.configure(fg_color="#DDEFFB")
        self.back_callback = back_callback 
        
        global profile
        self.profile = profile
        
        #Initialize Pygame for music playback
        pygame.mixer.init()
        #Gets the directory of the current script
        base_dir = os.path.dirname(os.path.abspath(__file__))  
        audio_path = os.path.join(base_dir, "breathing.mp3")
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play(loops=-1)  # -1 for infinite loop

        #Initialise table
        def initialise_table(): 
                #Connect to database
                connect = sqlite3.connect(database_file_path)
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
        
        #Title
        self.title=tk.Label(self.parent,text="4-7-8 Breathing Exercise",font=("Segoe UI",18,"bold"), bg="#DDEFFB", fg="#152238")
        self.title.pack(pady=10, fill='x')
            
        backbutton_frame = ctk.CTkFrame(self.parent, width=30, height=30, corner_radius=50, fg_color="#DDEFFB")
        backbutton_frame.pack(side='top', anchor='w', padx=20, pady=20)

        back_button = ctk.CTkButton(backbutton_frame, text="⬅", width=30, command=self.back_callback)
        back_button.configure(fg_color="#152238", text_color="#FFFFFF", font=("Segoe UI", 20, "bold"), hover_color="#80B6E2")
        back_button.pack(pady=5)

        #Main container frame
        self.container = ctk.CTkFrame(self.parent, width=600, height=600, corner_radius=20, fg_color="#DDEFFB")
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
        self.time_remaining = self.INHALE       
        self.is_running = False     
        
        self.parent.mainloop()
        
    def start_timer(self):
        self.is_running = True
        #Disable start button
        self.start_button.configure(state=tk.DISABLED) 
        #Enable stop button   
        self.stop_button.configure(state=tk.NORMAL)     
        self.rounds_completed = 0
        self.phase = "inhale"
        self.time_remaining = self.INHALE
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

        #Only animate during inhale and exhale
        if self.phase == "inhale":
            self.animate_circle("inhale")
        elif self.phase == "exhale":
            self.animate_circle("exhale")
        else:
            # Cancel any running animation during rest or hold
            if self.animation_job:
                self.parent.after_cancel(self.animation_job)
                self.animation_job = None
            self.reset_circle()

        if self.time_remaining > 0:
            self.time_remaining -= 1
            #Update timer every second
            self.parent.after(1000, self.update_timer)  
        else:
            #Move to the next phase when time runs out
            if self.phase == "inhale":
                self.phase = "hold"
                self.time_remaining = self.HOLD
                self.instruction_label.configure(text="Hold your breath...")
            elif self.phase == "hold":
                self.phase = "exhale"
                self.time_remaining = self.EXHALE
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
                self.phase = "rest"
                self.timer_label.configure(text="2s - Rest")
                self.parent.after(2000, self.start_next_round)  # 2-second pause
                return
            
            #Start the timer
            self.update_timer()
            
    def start_next_round(self):
        self.phase = "inhale"
        self.time_remaining = self.INHALE
        self.instruction_label.configure(text="Inhale deeply...")
        #Start the timer for the new phase
        self.update_timer()
            
    #Adjust the size of the circle            
    def animate_circle(self, phase):
        if not self.is_running or phase in ["hold", "rest"]:
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
            if not self.is_running or self.phase not in ["inhale", "exhale"]:
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

            if progress < 1.0 and self.is_running: #Animation not complete yet
                 self.animation_job = self.parent.after(int(1000 / fps), animate)
            else: #Animation complete
                self.animation_job = None

        animate()
            
    def reset_circle(self):
        #Return the circle to its default size
        self.canvas.coords(self.circle, 100, 100, 200, 200)
        
    def record_breathing_exercise(self):
        #Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        #Connect to the database
        connect = sqlite3.connect(database_file_path)
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

################################################################################################################################################################################

class Timer2to1(ctk.CTkFrame):
    #Set default timings
    INHALE = 4
    EXHALE = 8
        
    def __init__(self, parent, back_callback=None):    
        super().__init__(parent)
        self.parent = parent
        self.parent.configure(fg_color="#DDEFFB")
        self.back_callback = back_callback 
        
        global profile
        self.profile = profile
        
        #Initialize Pygame for music playback
        pygame.mixer.init()
        #Gets the directory of the current script
        base_dir = os.path.dirname(os.path.abspath(__file__))  
        audio_path = os.path.join(base_dir, "breathing.mp3")
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play(loops=-1)  # -1 for infinite loop

        #Initialise table
        def initialise_table(): 
                #Connect to database
                connect = sqlite3.connect(database_file_path)
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
        
        #Title
        self.title=tk.Label(self.parent,text="2 to 1 Breathing Exercise",font=("Segoe UI",18,"bold"), bg="#DDEFFB", fg="#152238")
        self.title.pack(pady=10, fill='x')
            
        backbutton_frame = ctk.CTkFrame(self.parent, width=30, height=30, corner_radius=50, fg_color="#DDEFFB")
        backbutton_frame.pack(side='top', anchor='w', padx=20, pady=20)

        back_button = ctk.CTkButton(backbutton_frame, text="⬅", width=30, command=self.back_callback)
        back_button.configure(fg_color="#152238", text_color="#FFFFFF", font=("Segoe UI", 20, "bold"), hover_color="#80B6E2")
        back_button.pack(pady=5)

        #Main container frame
        self.container = ctk.CTkFrame(self.parent, width=600, height=600, corner_radius=20, fg_color="#DDEFFB")
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
        self.time_remaining = self.INHALE       
        self.is_running = False     
        
        self.parent.mainloop()
        
    def start_timer(self):
        self.is_running = True
        #Disable start button
        self.start_button.configure(state=tk.DISABLED) 
        #Enable stop button   
        self.stop_button.configure(state=tk.NORMAL)     
        self.rounds_completed = 0
        self.phase = "inhale"
        self.time_remaining = self.INHALE
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

        #Only animate during inhale and exhale
        if self.phase == "inhale":
            self.animate_circle("inhale")
        elif self.phase == "exhale":
            self.animate_circle("exhale")
        else:
            # Cancel any running animation during rest or hold
            if self.animation_job:
                self.parent.after_cancel(self.animation_job)
                self.animation_job = None
            self.reset_circle()

        if self.time_remaining > 0:
            self.time_remaining -= 1
            #Update timer every second
            self.parent.after(1000, self.update_timer)  
        else:
            #Move to the next phase when time runs out
            if self.phase == "inhale":
                self.phase = "exhale"
                self.time_remaining = self.EXHALE
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
                self.phase = "rest"
                self.timer_label.configure(text="2s - Rest")
                self.parent.after(2000, self.start_next_round)  # 2-second pause
                return
            
            #Start the timer
            self.update_timer()
            
    def start_next_round(self):
        self.phase = "inhale"
        self.time_remaining = self.INHALE
        self.instruction_label.configure(text="Inhale deeply...")
        #Start the timer for the new phase
        self.update_timer()
            
    #Adjust the size of the circle            
    def animate_circle(self, phase):
        if not self.is_running or phase in ["hold", "rest"]:
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
            if not self.is_running or self.phase not in ["inhale", "exhale"]:
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

            if progress < 1.0 and self.is_running: #Animation not complete yet
                 self.animation_job = self.parent.after(int(1000 / fps), animate)
            else: #Animation complete
                self.animation_job = None

        animate()
            
    def reset_circle(self):
        #Return the circle to its default size
        self.canvas.coords(self.circle, 100, 100, 200, 200)
        
    def record_breathing_exercise(self):
        #Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        #Connect to the database
        connect = sqlite3.connect(database_file_path)
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

################################################################################################################################################################################

class Timer5_5(ctk.CTkFrame):
    #Set default timings
    INHALE = 5
    EXHALE = 5
        
    def __init__(self, parent, back_callback=None):    
        super().__init__(parent)
        self.parent = parent
        self.parent.configure(fg_color="#DDEFFB")
        self.back_callback = back_callback 
        
        global profile
        self.profile = profile
        
        #Initialize Pygame for music playback
        pygame.mixer.init()
        #Gets the directory of the current script
        base_dir = os.path.dirname(os.path.abspath(__file__))  
        audio_path = os.path.join(base_dir, "breathing.mp3")
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play(loops=-1)  # -1 for infinite loop

        #Initialise table
        def initialise_table(): 
                #Connect to database
                connect = sqlite3.connect(database_file_path)
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
        
        #Title
        self.title=tk.Label(self.parent,text="5-5 Breathing Exercise",font=("Segoe UI",18,"bold"), bg="#DDEFFB", fg="#152238")
        self.title.pack(pady=10, fill='x')
            
        backbutton_frame = ctk.CTkFrame(self.parent, width=30, height=30, corner_radius=50, fg_color="#DDEFFB")
        backbutton_frame.pack(side='top', anchor='w', padx=20, pady=20)

        back_button = ctk.CTkButton(backbutton_frame, text="⬅", width=30, command=self.back_callback)
        back_button.configure(fg_color="#152238", text_color="#FFFFFF", font=("Segoe UI", 20, "bold"), hover_color="#80B6E2")
        back_button.pack(pady=5)

        #Main container frame
        self.container = ctk.CTkFrame(self.parent, width=600, height=600, corner_radius=20, fg_color="#DDEFFB")
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
        self.time_remaining = self.INHALE       
        self.is_running = False     
        
        self.parent.mainloop()
        
    def start_timer(self):
        self.is_running = True
        #Disable start button
        self.start_button.configure(state=tk.DISABLED) 
        #Enable stop button   
        self.stop_button.configure(state=tk.NORMAL)     
        self.rounds_completed = 0
        self.phase = "inhale"
        self.time_remaining = self.INHALE
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

        #Only animate during inhale and exhale
        if self.phase == "inhale":
            self.animate_circle("inhale")
        elif self.phase == "exhale":
            self.animate_circle("exhale")
        else:
            # Cancel any running animation during rest or hold
            if self.animation_job:
                self.parent.after_cancel(self.animation_job)
                self.animation_job = None
            self.reset_circle()

        if self.time_remaining > 0:
            self.time_remaining -= 1
            #Update timer every second
            self.parent.after(1000, self.update_timer)  
        else:
            #Move to the next phase when time runs out
            if self.phase == "inhale":
                self.phase = "exhale"
                self.time_remaining = self.EXHALE
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
                self.phase = "rest"
                self.timer_label.configure(text="2s - Rest")
                self.parent.after(2000, self.start_next_round)  # 2-second pause
                return
            
            #Start the timer
            self.update_timer()
            
    def start_next_round(self):
        self.phase = "inhale"
        self.time_remaining = self.INHALE
        self.instruction_label.configure(text="Inhale deeply...")
        #Start the timer for the new phase
        self.update_timer()
            
    #Adjust the size of the circle            
    def animate_circle(self, phase):
        if not self.is_running or phase in ["hold", "rest"]:
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
            if not self.is_running or self.phase not in ["inhale", "exhale"]:
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

            if progress < 1.0 and self.is_running: #Animation not complete yet
                 self.animation_job = self.parent.after(int(1000 / fps), animate)
            else: #Animation complete
                self.animation_job = None

        animate()
            
    def reset_circle(self):
        #Return the circle to its default size
        self.canvas.coords(self.circle, 100, 100, 200, 200)
        
    def record_breathing_exercise(self):
        #Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        #Connect to the database
        connect = sqlite3.connect(database_file_path)
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

################################################################################################################################################################################

#Set appearance and theme
ctk.set_appearance_mode("light")  
ctk.set_default_color_theme("blue")  

#Create app window
app = ctk.CTk()
app.title("Breathing Exercise")

def on_close():
    if not app.winfo_exists():
        return

    #Forcefully terminate the application to prevent lingering events
    sys.exit()

app.protocol("WM_DELETE_WINDOW", on_close)

#Fullscreen size
app.update_idletasks()
try:
    app.state('zoomed')  # Works on Windows
    app.update()
except:
    # Fallback: manually set to full screen size
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    app.geometry(f"{screen_width}x{screen_height}")

# ESC to exit fullscreen
def exit_fullscreen(event=None):
    app.attributes("-fullscreen", False)

app.bind("<Escape>", exit_fullscreen)

#Track fullscreen state
is_fullscreen = [False]

# Toggle fullscreen using the 'f' key
def toggle_fullscreen(event=None):
    is_fullscreen[0] = not is_fullscreen[0]
    app.attributes("-fullscreen", is_fullscreen[0])
    
#Bind the 'f' key (lowercase only) (for fullscreen)
app.bind("<Control-f>", toggle_fullscreen)

#Main title (outside the frame, centered)
title_label = ctk.CTkLabel(
    app,
    text="Breathing Exercise",
    font=("Helvetica", 28, "bold"),
    text_color="#3a3a3a", fg_color="#cee6f4"
)
title_label.pack(pady=(30, 10))

#Load and set the background image
base_dir= os.path.dirname(os.path.abspath(__file__))
bg_image_path = os.path.join(base_dir, "breathing_bg.png")
bg_image = Image.open(bg_image_path) 
bg_image = bg_image.resize((app.winfo_screenwidth(), app.winfo_screenheight()))  # Resize to fullscreen
bg_photo = ImageTk.PhotoImage(bg_image)

#Label to display the background image
bg_label = tk.Label(app, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Stretch it across the window
bg_label.image = bg_photo  # Keep a reference to avoid garbage collection

#Lower the label so it doesn’t cover other widgets
bg_label.lower()

#Define the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

#Load and resize an image
def load_image(filename, size=(100, 100)):
    image_path = os.path.join(base_dir, filename)
    img = Image.open(image_path)
    img = img.resize(size, Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)

#Load all images
img_calm = load_image("calm.png")
img_balance = load_image("balance.png")
img_release = load_image("release.png")
img_relax = load_image("relax.png")

# Button style
button_style = {
    "width": 250,
    "height": 70,
    "corner_radius": 20,
    "font": ("Helvetica", 18, "bold")
}

#give users some tips
def show_help():
    messagebox.showinfo("Help", "Click on a breathing exercise based on your preference. Press Ctrl+F to toggle fullscreen.")

#exit button
exit_button = ctk.CTkButton(
    app,
    text="❌ Exit",
    font=("Segoe UI", 14),
    fg_color="#FF5151",
    hover_color="#FF6A6A",
    text_color="white",
    corner_radius=25,
    command=on_close
)
exit_button.place(relx=0.97, rely=0.04, anchor="ne")

help_button = ctk.CTkButton(app, text="❓ Help", font=("Segoe UI", 14), fg_color="#5A9BD5", hover_color="#7AB8FF", text_color="white", corner_radius=25, command=show_help)
help_button.place(relx=0.97, rely=0.09, anchor="ne")


################################################################################################################################################################################

def clear_app_widgets():
    if not app.winfo_exists():
        return 
    
    for widget in app.winfo_children():
        widget.destroy()

def go_home():
    try:
        pygame.mixer.music.stop()
    except Exception as e:
        print("Error stopping music:", e)
        
    clear_app_widgets()
    global main_frame
    global title_label

    #Load and set the background image
    bg_image = Image.open("tkinter pages/breathing/breathing_bg.png") 
    bg_image = bg_image.resize((app.winfo_screenwidth(), app.winfo_screenheight()))  # Resize to fullscreen
    bg_photo = ImageTk.PhotoImage(bg_image)

    #Label to display the background image
    bg_label = tk.Label(app, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Stretch it across the window
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection

    #Lower the label so it doesn’t cover other widgets
    bg_label.lower()
    
    #exit button
    exit_button = ctk.CTkButton(
        app,
        text="❌ Exit",
        font=("Segoe UI", 14),
        fg_color="#FF5151",
        hover_color="#FF6A6A",
        text_color="white",
        corner_radius=25,
        command=on_close
    )
    exit_button.place(relx=0.97, rely=0.04, anchor="ne")

    help_button = ctk.CTkButton(app, text="❓ Help", font=("Segoe UI", 14), fg_color="#5A9BD5", hover_color="#7AB8FF", text_color="white", corner_radius=25, command=show_help)
    help_button.place(relx=0.97, rely=0.09, anchor="ne")
    
    title_label = ctk.CTkLabel(
        app,
        text="Breathing Exercise 🧘",
        font=("Helvetica", 28, "bold"),
        text_color="#3a3a3a", fg_color="#cee6f4"
    )
    title_label.pack(pady=(30, 10))

    center_frame = ctk.CTkFrame(app, fg_color="#cee6f4")
    center_frame.pack(expand=True)

    main_frame = ctk.CTkFrame(center_frame, corner_radius=20, fg_color="#cee6f4")
    main_frame.pack(pady=20, padx=40)

    # Button creator
    def create_icon_button(parent, image, text, command):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.columnconfigure(0, weight=1)

        label = ctk.CTkLabel(frame, image=image, text="", width=80, height=80)
        label.grid(row=0, column=0, pady=(10, 5))

        button = ctk.CTkButton(frame, text=text, image=None, command=command, **button_style)
        button.grid(row=1, column=0, pady=(0, 10))

        return frame

    # Place buttons again
    create_icon_button(main_frame, img_calm, "4-7-4 Breathing Exercise", open_4_7_4).grid(row=0, column=0, padx=40, pady=30)
    create_icon_button(main_frame, img_balance, "5-5 Breathing Exercise", open_5_5).grid(row=0, column=1, padx=40, pady=30)
    create_icon_button(main_frame, img_release, "4-7-8 Breathing Exercise", open_4_7_8).grid(row=1, column=0, padx=40, pady=30)
    create_icon_button(main_frame, img_relax, "2 to 1 Breathing Exercise", open_2to1).grid(row=1, column=1, padx=40, pady=30)

#Button functions
def open_4_7_4(): 
    if not app.winfo_exists():
        print("App window was destroyed. Cannot load 4-7-4 page.")
        return
    
    clear_app_widgets()  # removes all widgets inside app
    
    global main_frame
    main_frame = ctk.CTkFrame(app, fg_color="#f3f3f3", corner_radius=20)
    if app.winfo_exists():
        main_frame.pack(expand=True, fill="both", padx=40, pady=20)
    
    
    #Load and set the background image
    base_dir= os.path.dirname(os.path.abspath(__file__))
    bg_image_path = os.path.join(base_dir, "breathing_bg.png")
    bg_image = Image.open(bg_image_path) 
    bg_image = bg_image.resize((app.winfo_screenwidth(), app.winfo_screenheight()))  # Resize to fullscreen
    bg_photo = ImageTk.PhotoImage(bg_image)

    #Label to display the background image
    bg_label = tk.Label(app, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Stretch it across the window
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    
    #Lower the label so it doesn’t cover other widgets
    bg_label.lower()
    
    # Then create timer inside main_frame
    if app.winfo_exists():
        page = Timer474(main_frame, back_callback=go_home)
        page.pack(expand=True, fill="both")
    
def open_5_5():
    if not app.winfo_exists():
        print("App window was destroyed. Cannot load 4-7-4 page.")
        return
    
    clear_app_widgets()  # removes all widgets inside app
    
    global main_frame
    main_frame = ctk.CTkFrame(app, fg_color="#f3f3f3", corner_radius=20)
    if app.winfo_exists():
        main_frame.pack(expand=True, fill="both", padx=40, pady=20)
    
    #Load and set the background image
    base_dir= os.path.dirname(os.path.abspath(__file__))
    bg_image_path = os.path.join(base_dir, "breathing_bg.png")
    bg_image = Image.open(bg_image_path) 
    bg_image = bg_image.resize((app.winfo_screenwidth(), app.winfo_screenheight()))  # Resize to fullscreen
    bg_photo = ImageTk.PhotoImage(bg_image)

    #Label to display the background image
    bg_label = tk.Label(app, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Stretch it across the window
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    
    #Lower the label so it doesn’t cover other widgets
    bg_label.lower()
    
    # Then create timer inside main_frame
    if app.winfo_exists():
        page = Timer5_5(main_frame, back_callback=go_home)
        page.pack(expand=True, fill="both")
    
def open_4_7_8(): 
    if not app.winfo_exists():
        print("App window was destroyed. Cannot load 4-7-4 page.")
        return
    
    clear_app_widgets()  # removes all widgets inside app
    
    global main_frame
    main_frame = ctk.CTkFrame(app, fg_color="#f3f3f3", corner_radius=20)
    if app.winfo_exists():
        main_frame.pack(expand=True, fill="both", padx=40, pady=20)
    
    #Load and set the background image
    base_dir= os.path.dirname(os.path.abspath(__file__))
    bg_image_path = os.path.join(base_dir, "breathing_bg.png")
    bg_image = Image.open(bg_image_path) 
    bg_image = bg_image.resize((app.winfo_screenwidth(), app.winfo_screenheight()))  # Resize to fullscreen
    bg_photo = ImageTk.PhotoImage(bg_image)

    #Label to display the background image
    bg_label = tk.Label(app, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Stretch it across the window
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    
    #Lower the label so it doesn’t cover other widgets
    bg_label.lower()
    
    # Then create timer inside main_frame
    if app.winfo_exists():
        page = Timer478(main_frame, back_callback=go_home)
        try:
            page.pack(expand=True, fill="both")
        except tk.TclError:
            print("Widget was destroyed before packing.")
    
def open_2to1(): 
    if not app.winfo_exists():
        print("App window was destroyed. Cannot load 4-7-4 page.")
        return
    
    clear_app_widgets()  # removes all widgets inside app
    
    global main_frame
    main_frame = ctk.CTkFrame(app, fg_color="#f3f3f3", corner_radius=20)
    if app.winfo_exists():
        main_frame.pack(expand=True, fill="both", padx=40, pady=20)
    
    #Load and set the background image
    base_dir= os.path.dirname(os.path.abspath(__file__))
    bg_image_path = os.path.join(base_dir, "breathing_bg.png")
    bg_image = Image.open(bg_image_path) 
    bg_image = bg_image.resize((app.winfo_screenwidth(), app.winfo_screenheight()))  # Resize to fullscreen
    bg_photo = ImageTk.PhotoImage(bg_image)

    #Label to display the background image
    bg_label = tk.Label(app, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Stretch it across the window
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    
    #Lower the label so it doesn’t cover other widgets
    bg_label.lower()
    
    # Then create timer inside main_frame
    if app.winfo_exists():
        page = Timer2to1(main_frame, back_callback=go_home)
        page.pack(expand=True, fill="both")

################################################################################################################################################################################

# Center layout
center_frame = ctk.CTkFrame(app, fg_color="#cee6f4")
center_frame.pack(expand=True)

main_frame = ctk.CTkFrame(center_frame, corner_radius=20, fg_color="#f3f3f3")
main_frame.pack(pady=20, padx=40)

# Function to create image + button vertically
def create_icon_button(parent, image, text, command):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.columnconfigure(0, weight=1)

    label = ctk.CTkLabel(frame, image=image, text="", width=80, height=80)
    label.grid(row=0, column=0, pady=(10, 5))

    button = ctk.CTkButton(frame, text=text, image=None, command=command, **button_style)
    button.grid(row=1, column=0, pady=(0, 10))

    return frame

# Place buttons
create_icon_button(main_frame, img_calm, "4-7-4 Breathing Exercise", open_4_7_4).grid(row=0, column=0, padx=40, pady=30)
create_icon_button(main_frame, img_balance, "5-5 Breathing Exercise", open_5_5).grid(row=0, column=1, padx=40, pady=30)
create_icon_button(main_frame, img_release, "4-7-8 Breathing Exercise", open_4_7_8).grid(row=1, column=0, padx=40, pady=30)
create_icon_button(main_frame, img_relax, "2 to 1 Breathing Exercise", open_2to1).grid(row=1, column=1, padx=40, pady=30)

#Run the app
app.mainloop()
