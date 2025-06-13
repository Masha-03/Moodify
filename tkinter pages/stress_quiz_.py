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
#for alignment
bg_photo_tk = None # Global variable for background image (to prevent garbage collection)
bg_photo_id = None
resize_job_id=None
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
root.attributes("-fullscreen", True)  #full-screen size
root.title("Stress Level Survey")
root.configure(bg="#FFF8E1")  #change the background color of entire window

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# --- Main Canvas for Background ---
main_canvas = tk.Canvas(root, highlightthickness=0, bg="#fdf6f0")
main_canvas.pack(fill="both", expand=True)

# Load and set background image
base_dir = os.path.dirname(os.path.abspath(__file__)) 
bg_image_path = os.path.join(base_dir, "stress_bg.png") 
try:
    bg_image_original = Image.open(bg_image_path)
except FileNotFoundError:
    messagebox.showerror("Error", f"Background image not found: {bg_image_path}")
    root.destroy()
    sys.exit()

#-------------------------------------------------------------------------------------------------------------------#
#for alignment
def _perform_resize_layout(event=None):
    global bg_photo_tk, bg_photo_id

    current_width = root.winfo_width() # Use root's width
    current_height = root.winfo_height()

    print(f"--- Layout Update: Root size {current_width}x{current_height} ---") # Debugging print

    # Prevent errors if window dimensions are 0 (e.g., during initialization)
    if current_width == 1 or current_height == 1:
        print("Root size is 1x1, skipping detailed layout updates.") # Debugging print
        return

    # Resize and update background image on main_canvas
    resized_bg_image = bg_image_original.resize((current_width, current_height), Image.Resampling.LANCZOS)
    bg_photo_tk = ImageTk.PhotoImage(resized_bg_image)

    # Use a try-except block to gracefully handle the TclError for image update
    try:
        if bg_photo_id: # If image already exists on canvas, just update it
            main_canvas.itemconfig(bg_photo_id, image=bg_photo_tk)
        else: # Otherwise, create it for the first time
            bg_photo_id = main_canvas.create_image(0, 0, image=bg_photo_tk, anchor="nw")
        main_canvas.tag_lower(bg_photo_id) # Ensure background is at the lowest layer
    except tk.TclError as e:
        print(f"Error updating background image: {e}. Recreating image.")
        # If error occurs, try to delete and recreate, or simply recreate
        if bg_photo_id:
             main_canvas.delete(bg_photo_id) # Try to delete the problematic ID
        bg_photo_id = main_canvas.create_image(0, 0, image=bg_photo_tk, anchor="nw")
        main_canvas.tag_lower(bg_photo_id)

    # --- Responsive Positioning for Main UI Elements using .place() on main_canvas ---
    # All main UI elements are now placed on main_canvas instead of root directly.

    # Title label
    title.place(in_=main_canvas, relx=0.5, rely=0.03, anchor="n") # Centered, slightly from top

    # Instruction frame (holds instruction label and restart button)
    instruction_frame.place(in_=main_canvas, relx=0.5, rely=0.09, relwidth=0.75, height=50, anchor="n")
    # instruction_label and reset_btn are packed inside instruction_frame, so they'll adjust within it.

    # Progress bar - REMOVED 'height=15' from place() as it's set in constructor
    progress.place(in_=main_canvas, relx=0.5, rely=0.155, relwidth=0.7, anchor="n") # Centered, below instruction frame

    # Main container frame (holds chat on left and result/tips on right)
    main_frame.place(in_=main_canvas, relx=0.5, rely=0.22, anchor="n", relwidth=0.9, relheight=0.75) # Centered, wider and taller
    
    # Update wraplength for result_label based on right_frame's width
    # This needs to happen after right_frame has its final size from .place()
    root.update_idletasks() # Ensures frames have their sizes
    if right_frame.winfo_width() > 0:
        result_label.config(wraplength=right_frame.winfo_width() * 0.9) # 90% of right_frame width

    # Ensure scroll region is updated after layout changes
    root.update_idletasks() # Let tkinter update its internal geometry
    chat_canvas.config(scrollregion=chat_canvas.bbox("all"))

    # Debugging prints for frame sizes
    print(f"   main_frame size: {main_frame.winfo_width()}x{main_frame.winfo_height()}") # Debugging print
    print(f"   left_frame size: {left_frame.winfo_width()}x{left_frame.winfo_height()}") # Debugging print
    print(f"   right_frame size: {right_frame.winfo_width()}x{right_frame.winfo_height()}") # Debugging print
    print(f"   chat_canvas size: {chat_canvas.winfo_width()}x{chat_canvas.winfo_height()}") # Debugging print
    print(f"   chat_frame size: {chat_frame.winfo_width()}x{chat_frame.winfo_height()}") # Debugging print
    print(f"   chat_canvas scrollregion: {chat_canvas.cget('scrollregion')}") # Debugging print



# This is the debouncing function that will be called by the <Configure> event
def resize_layout(event=None):
    global resize_job_id
    # If there's an existing scheduled job, cancel it
    if resize_job_id:
        root.after_cancel(resize_job_id)
    # Schedule the actual layout update to happen after a short delay (e.g., 50ms)
    # This ensures the layout is only updated *after* the user has stopped resizing for a moment.
    resize_job_id = root.after(50, _perform_resize_layout)

#--------------------------------------------------------------masha---------------------------------------------------------------------------------# 

def get_db_path():
    base_dir = None
    if getattr(sys, 'frozen', False):
        # For now, let's assume the database folder is at the same level as the executable.
        app_root = sys._MEIPASS
    else:
        #In unfrozen mode
        script_dir = os.path.dirname(os.path.abspath(__file__)) 
        app_root = os.path.dirname(script_dir) 

    db_file_name = 'moodify_database.db'
    db_folder_name = 'database'

    #Join the app_root with the database folder and the file name
    db_path = os.path.join(app_root, db_folder_name, db_file_name)

    print(f"Running in {'frozen' if getattr(sys, 'frozen', False) else 'unfrozen'} mode.")
    print(f"Detected script directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Calculated application root: {app_root}")
    print(f"Calculated database path: {db_path}")

    return db_path

database_file_path = get_db_path()

#Check if the database file exists at the calculated path
if os.path.exists(database_file_path):
    print(f"Database file FOUND at: {database_file_path}")
else:
    print(f"Database file NOT FOUND at: {database_file_path}")

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

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Frame to hold instruction label and restart button side by side
instruction_frame = tk.Frame(root, bg="#FFF8E1")

#instruction label to tell user what to do
instruction_label = tk.Label(instruction_frame, text="Hi! Please press one of the buttons below to answer each question.", font=("Segoe UI", 13, "italic"), bg="#FFF8E1", fg="#555", wraplength=500, justify="left")
instruction_label.pack(side="left",pady=(0, 10),padx=(200,5),anchor="w",expand=True,fill="x")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Progress bar
progress = ctk.CTkProgressBar(root, orientation="horizontal", width=700, height=15, corner_radius=10, fg_color="#FFE0B2", progress_color="#FFB74D")
progress.set(0)
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
    display_next_question(is_reset=True)

reset_btn = ctk.CTkButton(instruction_frame, text="🔁 Restart Survey", 
                           font=ctk.CTkFont("Segoe UI", 16, "bold"),
                           fg_color="#FFCC80", 
                           text_color="#6D4C41", 
                           command=reset_quiz, 
                           hover_color="#FFB380", # Darker yellow on hover
                           corner_radius=14) # Adding CustomTkinter styling
reset_btn.pack(side="right",anchor="e",pady=(3,10),padx=(10,30))

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

# Left frame for chat box
left_frame = tk.Frame(main_frame, bg="#FFFFFF", bd=2, relief="flat")
left_frame.place(relx=0, rely=0, relwidth=0.55, relheight=1)

# Right frame for result tips
right_frame = tk.Frame(main_frame, bg="#FFFDE7")
right_frame.place(relx=0.56, rely=0, relwidth=0.43, relheight=1)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Scrollbar inside the chat box (direct child of left_frame)
scrollbar = ttk.Scrollbar(left_frame, orient="vertical")
scrollbar.pack(side="right", fill="y", padx=1, pady=1)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Canvas for scrollable area (direct child of left_frame)
chat_canvas = tk.Canvas(left_frame, bg="#FFFFFF", yscrollcommand=scrollbar.set, highlightthickness=0) #yscrollcommand=scrollbar.set:connects the canvas's vertical scrolling to the scrollbar
chat_canvas.pack(side="left", fill="both", expand=True, padx=1, pady=1) # Ensure fill and expand are set

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
result_label = tk.Label(right_frame, text="[Your stress level and tips will be displayed here.]", font=("Segoe UI", 14), bg="#FCF8E8", fg="#3A3D64", justify="left")
# Place result_label in the center of right_frame. wraplength will be set dynamically in resize_layout
result_label.place(relx=0.5,rely=0.30,anchor="center")    # Just below the title and chat box

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
def display_next_question(answer=None, is_reset=False): #added is_reset flag
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

        # Timestamp for user message
        timestamp = datetime.datetime.now().strftime("%I:%M %p")
        time_label = ctk.CTkLabel(chat_frame, text=timestamp, font=ctk.CTkFont("Segoe UI", 11), text_color="#888888")
        time_label.pack(anchor="e", padx=15, pady=(0, 5))

        # Call scroll_to_bottom after the user response is added
        root.after(100, scroll_to_bottom) # Use after to ensure widgets are drawn

    # Display intro message only if not resetting and it's the very first question
    # This block has been moved inside display_next_question to manage its display based on the survey flow.
    # Check if this is the very first call (current_index is 0 and no answer provided yet)
    if not is_reset and current_index == 0 and not answer:
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

        root.after(500, scroll_to_bottom) # Short delay for intro scroll


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

        for option in options:                                           
            button = ctk.CTkButton(button_frame, text=option, 
                                       fg_color="#FFAB91", # Light purple for options
                                       text_color="#4E342E", 
                                       command=lambda opt=option: [on_option_click(opt, button_frame)],
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

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Global variables to store the window's geometry before fullscreen
last_width = 1280
last_height = 720 # Set a reasonable default size
last_x = None
last_y = None

# Track fullscreen state
is_fullscreen = [True] # Still starts in fullscreen

# Toggle fullscreen using the 'f' key
def toggle_fullscreen(event=None):
    global last_width, last_height, last_x, last_y

    if is_fullscreen[0]: # Currently fullscreen, going to non-fullscreen
        # Store current fullscreen dimensions (often maxed to screen)
        # We'll rely on stored last_width/height for restoration
        
        root.attributes("-fullscreen", False)
        # Restore to last known non-fullscreen size or a default if not set
        if last_x is not None and last_y is not None:
             root.geometry(f"{last_width}x{last_height}+{last_x}+{last_y}")
        else: # Fallback to a default if no previous state was captured
             root.geometry(f"{last_width}x{last_height}")
        print(f"Exiting fullscreen: Restoring to {root.winfo_width()}x{root.winfo_height()}")

    else: # Currently non-fullscreen, going to fullscreen
        # Store current window geometry BEFORE going fullscreen
        last_width = root.winfo_width()
        last_height = root.winfo_height()
        last_x = root.winfo_x()
        last_y = root.winfo_y()
        print(f"Entering fullscreen: Stored current size {last_width}x{last_height}")
        root.attributes("-fullscreen", True)

    is_fullscreen[0] = not is_fullscreen[0]
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
exit_button.place(in_=main_canvas,relx=0.97, rely=0.04, anchor="ne")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

help_button = ctk.CTkButton(root, text="❓ Help", font=("Segoe UI", 14), fg_color="#5A9BD5", hover_color="#7AB8FF", text_color="white", corner_radius=25, command=show_help)
help_button.place(in_=main_canvas,relx=0.97, rely=0.09, anchor="ne")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# --- Initial setup calls ---
# Bind update_layout to the root window's Configure event
root.bind("<Configure>", resize_layout)
# Initial call to update_layout to set up the elements, ensuring window is drawn
# Added a small initial delay to ensure the window is fully rendered before layout calculation and first question
root.after(100, lambda: [resize_layout(), display_next_question()])


# Run the main program
root.mainloop()