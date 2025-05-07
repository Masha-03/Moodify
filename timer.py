import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkbootstrap import ttk, Style #Modern widget
import time #Animations

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
        self.style = Style(theme="simplex")
        self.style.theme_use()
        
        #Canvas frame to draw the breathing circle
        self.canvas = tk.Canvas(self.root, width=300, height=300)
        self.canvas.pack(pady=20)
        
        #Initial circle
        self.circle = self.canvas.create_oval(100, 100, 200, 200, fill="lightblue")

        #Label to show current round number
        self.round_label = tk.Label(self.root, text="Round 0 of 3", font=("Arial", 16))
        self.round_label.pack()

        #Label to show countdown timer and current phase
        self.timer_label = tk.Label(self.root, text="", font=("Arial", 24))
        self.timer_label.pack(pady=10)

        #Frame to hold the Start and Stop buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        #Start button
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_timer)
        self.start_button.pack(side=tk.LEFT, padx=10)

        #Stop button
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

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
                messagebox.showinfo("Hold", "Hold your breath.")
            elif self.phase == "hold":
                self.phase = "exhale"
                self.time_remaining = EXHALE
                messagebox.showinfo("Exhale", "Exhale slowly.")
            elif self.phase == "exhale":
                self.rounds_completed += 1
                #After 3 rounds it stops
                if self.rounds_completed >= self.total_rounds:
                    messagebox.showinfo("Done", "You’ve completed your breathing exercise!")
                    self.stop_timer()
                    return
                self.phase = "inhale"
                self.time_remaining = INHALE
                messagebox.showinfo("Inhale", "Inhale again.")
            
            #Start the timer for the new phase
            self.update_timer()
            
    #Adjust the size of the circle            
    def animate_circle(self, phase):
        if not self.is_running or phase == "hold":
            self.reset_circle()
            return

        if phase == "inhale":
            self.animate_resize(100, 75, 200, 225, INHALE) #top-left corner (first 2), bottom-right corner(last 2)
        elif phase == "exhale":
            self.animate_resize(75, 110, 225, 190, EXHALE)

    def animate_resize(self, start_x0, end_x0, start_x1, end_x1, duration):
        start_time = time.time()
        end_time = start_time + duration
        steps = 100  #For smoother animation

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