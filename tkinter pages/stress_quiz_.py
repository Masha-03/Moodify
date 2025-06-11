import tkinter as tk
from tkinter import ttk
import datetime
import sqlite3
import customtkinter as ctk
import os
import sys
from PIL import Image,ImageTk 
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
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, *relative_path_parts)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
def get_image_path(filename):
    # This gets the path of the current Python file
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#auto scroll to bottom after receive new msg
def scroll_to_bottom():
    chat_canvas.update_idletasks() #used when you modify the layout (like adding new chat messages) and want the UI to "catch up"
    chat_canvas.yview_moveto(1) #This scrolls the chat_canvas vertically to position 1, which means 100% to the bottom.

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#disable option buttons immediately after one is clicked
def on_option_click(opt, btn_frame):
    for btn in btn_frame.winfo_children(): #goes through every button inside btn_frame
        btn.configure(state="disabled") #each button is disabled to prevent the user from clicking again after making a choice.
    display_next_question(opt) 
    btn_frame.destroy() #remove old button frame

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#help function, to show users tips
def show_help():
    messagebox.showinfo("Help","Press one of the button below to answer each question. If you would like to restart the survey, press the button *restart survey*. Press Ctrl + f to toggle full screen.")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#main window
root = tk.Tk()  #create the main app window
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")  #full-screen size
root.title("Stress Level Survey")
root.configure(bg="#FFF8E1")  #change the background color of entire window

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Load and set background image
base_dir = os.path.dirname(os.path.abspath(__file__)) 
bg_image_path = os.path.join(base_dir, "stress_bg.png") 
bg_image=Image.open(bg_image_path)
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.Resampling.LANCZOS) #full screen
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

#--------------------------------------------------------------masha---------------------------------------------------------------------------------# 

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

#Initialise table
def initialise_table(): 
        #Connect to database
        connect = sqlite3.connect(database_file_path)
        #Create cursor
        cursor = connect.cursor()
        
        #Create table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stress_quiz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile TEXT,
            date DATE,
            score INTEGER,
            stress_level TEXT,
            FOREIGN KEY (profile) REFERENCES user_info(profile)
        )
        ''')
        
        #Save data, update
        connect.commit()
        #Close connection
        connect.close()
        
#Initialise table before GUI starts        
initialise_table()

def save_stress_result(score, level):
    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()

    date_today = datetime.date.today().isoformat()  #2025-05-20 fromat current date

    cursor.execute("INSERT INTO stress_quiz (profile, date, score, stress_level) VALUES (?, ?, ?, ?)",
              (profile, date_today, score, level))

    connect.commit()
    connect.close()  

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#title label
title = tk.Label(root, text="Stress Level Survey📃", font=("Arial", 20, "bold"), bg="#FCF8E8", fg="#333")
title.pack(pady=10)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Frame to hold instruction label and restart button side by side
instruction_frame = tk.Frame(root, bg="#FFF8E1")
instruction_frame.pack(pady=(0, 10))

#instruction label to tell user what to do
instruction_label = tk.Label(instruction_frame, text="Hi! Please press one of the buttons below to answer each question.", font=("Segoe UI", 13, "italic"), bg="#FFF8E1", fg="#555", wraplength=500, justify="left")
instruction_label.pack(side="left",pady=(0, 10),anchor="w")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Progress bar
progress = ctk.CTkProgressBar(root, orientation="horizontal", width=700, height=15, corner_radius=10, fg_color="#FFE0B2", progress_color="#FFB74D")
progress.set(0)
progress.pack(pady=(5, 10))

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Restart button
def reset_quiz():
    global current_index, user_scores
    current_index = 0
    user_scores = []
    progress.set(0) #progress become 0
    for widget in chat_frame.winfo_children():
        widget.destroy()
    result_label.config(text="[Your stress level and tips will be displayed here.]")
    chat_canvas.yview_moveto(0)  # Scroll to top when restarting
    display_next_question()

reset_btn = ctk.CTkButton(instruction_frame, text="🔁 Restart Survey", 
                           font=ctk.CTkFont("Segoe UI", 16, "bold"),
                           fg_color="#FFCC80", 
                           text_color="#6D4C41", 
                           command=reset_quiz, 
                           hover_color="#FFB380", # Darker yellow on hover
                           corner_radius=14) # Adding CustomTkinter styling
reset_btn.pack(side="left",anchor="e",pady=(3,10))

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#list of the quiz questions
quiz_questions=[
    "How often do you feel overwhelmed by your responsibilities?",
    "Do you have trouble sleeping due to racing thoughts?",
    "How often do you feel anxious or worried?",
    "Do you experience physical symptoms like headaches or stomachaches when stressed?",
    "How often do you feel like you can't handle things?",
    "Do you find it hard to relax even during your free time?",
    "Do you feel emotionally drained at the end of the day?",
    "How often do you feel irritable or short-tempered?",
    "Do you feel a lack of motivation or energy?",
    "How often do you procrastinate tasks due to feeling overwhelmed?"
]

# Define total number of questions for progress bar calculation
TOTAL_QUESTIONS = len(quiz_questions)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#list of the answers options for each question 
quiz_options=[
    ["Rarely", "Sometimes", "Frequently", "Always"],
    ["Never", "Sometimes", "Often", "Every night"],
    ["Seldom", "Occasionally", "Often", "Constantly"],
    ["Rarely", "Sometimes", "Frequently", "Always"],
    ["Never", "Sometimes", "Often", "Always"],
    ["Rarely", "Sometimes", "Frequently", "Always"],
    ["Rarely", "Sometimes", "Frequently", "Always"],
    ["Never", "Occasionally", "Often", "Always"],
    ["Rarely", "Sometimes", "Often", "Always"],
    ["Never", "Occasionally", "Often", "Always"]
]

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#assign scores to options
quiz_options_score=[
    [0,1,2,3],
    [0,1,2,3],
    [0,1,2,3],
    [0,1,2,3],
    [0,1,2,3],
    [0,1,2,3],
    [0,1,2,3],
    [0,1,2,3],
    [0,1,2,3],
    [0,1,2,3]
]

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#variable to keep track the current question index
current_index = 0 #set 0 to display the first question first
user_scores=[] #list to store user's selected scores

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Container frame to hold chat on the left and result/tips on the right
main_frame = tk.Frame(root, bg="#FFF8E1")
main_frame.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.9, relheight=0.6)

# Left frame for chat box
left_frame = tk.Frame(main_frame, bg="#FFFFFF", bd=2, relief="flat")
left_frame.place(relx=0, rely=0, relwidth=0.55, relheight=1)

# Right frame for result tips
right_frame = tk.Frame(main_frame, bg="#FFFDE7")
right_frame.place(relx=0.56, rely=0, relwidth=0.43, relheight=1)

# Outer frame with border acting as the "box"
chat_box = tk.Frame(left_frame, bg="#FFFFFF", bd=2, relief="flat")
chat_box.place(relx=0.5, rely=0.45, anchor="center", width=600, height=400) #relx=horizontal,value between 0.0 (left) and 1.0 (right) #rely=vertical.value between 0.0 (top) and 1.0 (bottom)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Scrollbar inside the chat box
scrollbar = ttk.Scrollbar(left_frame, orient="vertical")
scrollbar.pack(side="right", fill="y")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Canvas for scrollable area
chat_canvas = tk.Canvas(left_frame, bg="#FFFFFF", yscrollcommand=scrollbar.set, highlightthickness=0) #yscrollcommand=scrollbar.set:connects the canvas's vertical scrolling to the scrollbar
chat_canvas.pack(side="left", fill="both", expand=True)
scrollbar.config(command=chat_canvas.yview) #when move the scrollbar, it scrolls the canvas vertically using .yview()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Frame inside canvas where chat messages will appear
chat_frame = tk.Frame(chat_canvas, bg="#FFFFFF")
chat_canvas.create_window((0, 0), window=chat_frame, anchor="nw")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Update the scroll region when adding new widgets
def update_scroll_region(event=None): #event=None:allow function to be called automatically by an event
    chat_canvas.configure(scrollregion=chat_canvas.bbox("all")) #chat_canvas.configure(scrollregion=...): Updates the scrollable area of the canvas so that it fits all its content
                                                                #chat_canvas.bbox("all"): Gets the bounding box (min and max x/y coordinates) of everything inside the canvas.
chat_frame.bind("<Configure>", update_scroll_region)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Enable scrolling with the mouse wheel
def on_mousewheel(event):
    chat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Bind mouse wheel to canvas (Windows and Linux)
chat_canvas.bind_all("<MouseWheel>", on_mousewheel) #everytime the mouse wheel scrolled,call on_mousewheel event

# Bind mouse wheel for macOS (uses different event name)
chat_canvas.bind_all("<Button-4>", lambda event: chat_canvas.yview_scroll(-1, "units"))
chat_canvas.bind_all("<Button-5>", lambda event: chat_canvas.yview_scroll(1, "units"))


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Result label (outside and below the chat interface)
result_label = tk.Label(right_frame, text="[Your stress level and tips will be displayed here.]", font=("Segoe UI", 14), bg="#FCF8E8", fg="#3A3D64", wraplength=480, justify="left")
# Place result_label just below the chat_box
result_label.place(relx=0.5,rely=0.30,anchor="center")  # Just below the title and chat box

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#


# Function to calculate stress level and update the result label
def calculate_stress_level():
    total_score = sum(user_scores)
    
    # Determine stress level and tips
    if total_score <= 7:
        level = "Low Stress😊"
        tips = (
            "You're managing your stress well. Keep up the good work!\n"
            "• Maintain a balanced lifestyle\n"
            "• Exercise regularly to boost mood\n"
            "• Practice gratitude journaling daily\n"
            "• Ensure good sleep hygiene"
        )
    elif 8 <= total_score <= 15:
        level = "Moderate Stress🤔"
        tips = (
            "Take some time to relax. Practice deep breathing and mindfulness.\n"
            "• Take short breaks during work or study\n"
            "• Engage in hobbies you enjoy\n"
            "• Avoid caffeine and sugar close to bedtime\n"
            "• Try progressive muscle relaxation"
        )
    elif 16 <= total_score <= 22:
        level = "High Stress😵‍💫"
        tips = (
            "Your stress levels are getting high. Consider talking to a trusted friend or engaging in a calming activity.\n"
            "• Schedule regular 'me-time' to unwind\n"
            "• Practice deep breathing exercises or guided imagery\n"
            "• Limit exposure to stress triggers\n"
            "• Talk to supportive friends or counselors"
        )
    else:
        level = "Severe Stress🤒"
        tips = (
            "Your stress levels are quite high. It might be helpful to seek support from a mental health professional.\n"
            "• Consider professional counseling or therapy\n"
            "• Explore mindfulness-based stress reduction\n"
            "• Keep a stress diary to track triggers\n"
            "• Prioritize self-care routines and set boundaries"
        )
    
    # Add result to chat_frame like a message
    result_label.config(text=f"✨ Stress Level: {level}\n💡 Tips: {tips}", font=("Comic Sans MS", 14, "bold"))
    
    #Save to database
    save_stress_result(total_score, level.split()[0])  #Use only "Low", "Moderate", "High"

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#animation for button
def pop_button(button, initial_pady):
    # Move up slightly (reduce pady to top)
    button.pack_configure(pady=(initial_pady[0] - 2, initial_pady[1] + 2))
    root.after(70, lambda: button.pack_configure(pady=initial_pady)) # Move back to original position

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#function to display next question
def display_next_question(answer=None): #answer=None:parameter that stores the selected answer #if users selected a answer it will pass to a function
    global current_index #used to track which question in the quiz is currently being displayed

    #show the user response
    if answer:
        # Save the score of the selected answer
        question_index = current_index - 1  # because current_index was incremented after displaying question
        option_idx = quiz_options[question_index].index(answer)
        score = quiz_options_score[question_index][option_idx]
        user_scores.append(score)
        #user response bubble
        user_bubble_frame = ctk.CTkFrame(chat_frame, fg_color="#FFD54F", corner_radius=15) # Light blue bubble
        user_bubble_frame.pack(pady=(5, 2), padx=(100,25), anchor="e", ipadx=5, ipady=3) # Anchor right
        
        response_label = ctk.CTkLabel(user_bubble_frame, text=f"🧍 You: {answer}", 
                                      font=ctk.CTkFont("Calibri", 17, "bold"), 
                                      text_color="#6D4C41", 
                                      wraplength=380, justify="left")
        response_label.pack(padx=10, pady=5, anchor="e")

        # Inside display_next_question(), after displaying the user response
        # Timestamp for user message
        timestamp = datetime.datetime.now().strftime("%I:%M %p")
        time_label = ctk.CTkLabel(chat_frame, text=timestamp, font=ctk.CTkFont("Segoe UI", 11), text_color="#888888")
        time_label.pack(anchor="e", padx=15, pady=(0, 5))

        # Call scroll_to_bottom after the user response is added
        root.after(100, scroll_to_bottom) # Use after to ensure widgets are drawn

    #move to the next question if there's a new answer
    if current_index < len(quiz_questions): #check if there are more question to display
        #display the question as a chat bubble
        #label to display the question
        bot_bubble_frame = ctk.CTkFrame(chat_frame, fg_color="#FBE9E7", corner_radius=15) # Light grey bubble
        bot_bubble_frame.pack(pady=(5, 2), padx=10, anchor="w", fill="x", ipadx=5, ipady=3) # Anchor left

        question_label = ctk.CTkLabel(bot_bubble_frame, text=f"🤖 Q{current_index+1}: {quiz_questions[current_index]}", 
                                      font=ctk.CTkFont("Calibri", 17, "bold"), 
                                      text_color="#3E2723", 
                                      wraplength=560, justify="left")
        question_label.pack(padx=10, pady=5, anchor="w")

        # Timestamp for bot message
        timestamp = datetime.datetime.now().strftime("%I:%M %p")
        time_label = ctk.CTkLabel(chat_frame, text=timestamp, font=ctk.CTkFont("Segoe UI", 11), text_color="#888888")
        time_label.pack(anchor="w", padx=15, pady=(0, 5))

        #display options as buttons
        options = quiz_options[current_index]
        button_frame = ctk.CTkFrame(chat_frame, fg_color="transparent") # Transparent background
        button_frame.pack(pady=10, anchor="w", padx=10)

        for option in options:                                                         #When clicked, it calls display_next_question(opt), passing the selected option as the answer #button_frame to remove the options after a selection
            button = ctk.CTkButton(button_frame, text=option, 
                                   fg_color="#FFAB91", # Light purple for options
                                   text_color="#4E342E", 
                                   command=lambda opt=option: [display_next_question(opt), button_frame.destroy()],
                                   hover_color="#FF8A65", # Darker purple on hover
                                   corner_radius=6,
                                   font=ctk.CTkFont("Segoe UI", 15, "bold"),
                                   width=120, height=35)
            button.pack(side="left", padx=5)
            root.after(100 + options.index(option) * 50, lambda b=button: pop_button(b, (5,5)))
        current_index += 1 #+1 and move to next question
        progress.set(current_index / TOTAL_QUESTIONS)
        # Call scroll_to_bottom after the bot message and options are added
        root.after(100, scroll_to_bottom) 
    else:
        calculate_stress_level()
        root.after(100, scroll_to_bottom)

#-----------------------------------------------------------------------------------------------------------------------------------------------#

# Display an intro message before the first question
intro_bubble_frame = ctk.CTkFrame(chat_frame, fg_color="#FFE0B2", corner_radius=15) # Light purple intro bubble
intro_bubble_frame.pack(pady=10, padx=(10, 100), anchor="w", ipadx=5, ipady=3)

intro_label = ctk.CTkLabel(intro_bubble_frame, text="👋 Hi! I'm here to check your stress level. Let's begin the survey!", 
                           font=ctk.CTkFont("Calibri", 18, "bold"), 
                           text_color="#795548", 
                           wraplength=560, justify="left") # Reduced wraplength
intro_label.pack(padx=10, pady=5, anchor="w")

# Timestamp for intro message
timestamp = datetime.datetime.now().strftime("%I:%M %p")
time_label = ctk.CTkLabel(chat_frame, text=timestamp, font=ctk.CTkFont("Segoe UI", 11), text_color="#757575")
time_label.pack(anchor="w", padx=10, pady=(0, 5))

# Delay the first question slightly to simulate a chat feel
root.after(1000, display_next_question)  # delay 1 second before showing the first question

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#Track fullscreen state
is_fullscreen = [False]

# Toggle fullscreen using the 'f' key
def toggle_fullscreen(event=None):
    is_fullscreen[0] = not is_fullscreen[0]
    root.attributes("-fullscreen", is_fullscreen[0])

# Bind the 'f' key (lowercase only)
root.bind("<Control-f>", toggle_fullscreen)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#exit button incase the ctrl+f key doesnt works
exit_button = ctk.CTkButton(
    root,
    text="❌ Exit",
    font=("Segoe UI", 14),
    fg_color="#FF5151",
    hover_color="#FF6A6A",
    text_color="white",
    corner_radius=25,
    command=root.destroy
)
exit_button.place(relx=0.97, rely=0.04, anchor="ne")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

help_button = ctk.CTkButton(root, text="❓ Help", font=("Segoe UI", 14), fg_color="#5A9BD5", hover_color="#7AB8FF", text_color="white", corner_radius=25, command=show_help)
help_button.place(relx=0.97, rely=0.09, anchor="ne")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Run the main program
root.mainloop()