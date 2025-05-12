import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkbootstrap import Style #Modern widget
import time #Animations
import random

#Set default timings
INHALE = 4
HOLD = 7
EXHALE = 4

class Timer:
    def __init__(self):
        #Window setup
        self.root = tk.Tk()
        self.root.state("zoomed")
        self.root.title("Breathing Exercise")
        self.style = Style(theme="morph")
        self.style.theme_use()
        
        #Main container frame
        self.container = ttk.Frame(self.root, padding=(40, 30))
        self.container.pack(expand=True)
        
        #Canvas frame to draw the breathing circle
        self.canvas = tk.Canvas(self.container, width=300, height=300, bg="#f0f0f0", highlightthickness=0)
        self.canvas.grid(row=0, column=0, pady=(0, 30))
        
        #Initial circle
        self.circle = self.canvas.create_oval(100, 100, 200, 200, fill="#add8e6", outline="#87ceeb")

        #Label to show current round number
        self.round_label = ttk.Label(self.container, text="Round 0 of 3", font=("Arial", 16), bootstyle="primary")
        self.round_label.grid(row=1, column=0, pady=(0, 10))

        #Label to show countdown timer and current phase
        self.timer_label = ttk.Label(self.container, text="", font=("Arial", 24), bootstyle="secondary")
        self.timer_label.grid(row=2, column=0, pady=(10, 20))
        
        #Instruction label 
        self.instruction_label = ttk.Label(self.container, text="", font=("Arial", 14), bootstyle="secondary")
        self.instruction_label.grid(row=3, column=0, pady=(10, 20))

        #Frame to hold the Start and Stop buttons
        button_frame = ttk.Frame(self.container)
        button_frame.grid(row=4, column=0, pady=(10, 0))

        #Start button
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_timer, bootstyle="success-outline", width=12)
        self.start_button.grid(row=0, column=0, padx=(0, 20), ipady=5)

        #Stop button
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_timer, state=tk.DISABLED,bootstyle="danger-outline", width=12)
        self.stop_button.grid(row=0, column=1, ipady=5)

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
        self.start_button.config(state=tk.DISABLED) 
        #Enable stop button   
        self.stop_button.config(state=tk.NORMAL)     
        self.rounds_completed = 0
        self.phase = "inhale"
        self.time_remaining = INHALE
        #Clear the completion message when starting a new session
        self.instruction_label.config(text="Inhale deeply...")
        self.update_timer()

    def stop_timer(self):
        self.is_running = False
        #Clear label
        self.timer_label.config(text="")
        #Reset round                     
        self.round_label.config(text="Round 0 of 3")   
        self.start_button.config(state=tk.NORMAL)          
        #Disable stop
        self.stop_button.config(state=tk.DISABLED)
        #Reset circle
        self.reset_circle()
        #Check if stopped midway or completed
        if self.rounds_completed >= self.total_rounds:
            #Display completion message if all rounds are done
            self.instruction_label.config(text="You've completed your breathing exercise. Well done!")
        else:
            #Clear the instruction if stopped midway
            self.instruction_label.config(text="")
        
    #Main loop that updates every second
    def update_timer(self):
        if not self.is_running:
            return

        #Show countdown and rounds 
        self.timer_label.config(text=f"{self.time_remaining:02d}s - {self.phase.capitalize()}")
        self.round_label.config(text=f"Round {self.rounds_completed + 1} of {self.total_rounds}")

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
                self.instruction_label.config(text="Hold your breath...")
            elif self.phase == "hold":
                self.phase = "exhale"
                self.time_remaining = EXHALE
                self.instruction_label.config(text="Exhale slowly...")
            elif self.phase == "exhale":
                self.rounds_completed += 1
                #After 3 rounds it stops
                if self.rounds_completed >= self.total_rounds:
                    self.instruction_label.config(text="You've completed your breathing exercise. Well done!")
                    self.stop_timer()
                    return
                
                #Pause before starting the next round
                self.instruction_label.config(text="Resting for 2 seconds...")
                self.timer_label.config(text="2s - Rest")
                self.root.after(2000, self.start_next_round)  # 2-second pause
                return
            
            #Start the timer
            self.update_timer()
            
    def start_next_round(self):
        self.phase = "inhale"
        self.time_remaining = INHALE
        self.instruction_label.config(text="Inhale deeply...")
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
        steps = 60 

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
            
Timer()