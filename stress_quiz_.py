import tkinter as tk
from tkinter import ttk
import datetime
import sqlite3

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#main window
root = tk.Tk()  #create the main app window
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")  #full-screen size
root.title("Stress Level Survey")
root.configure(bg="#FCF8E8")  #change the background color of entire window

#--------------------------------------------------------------masha---------------------------------------------------------------------------------# 
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

#Initialise table
def initialise_table(): 
        #Connect to database
        connect = sqlite3.connect('moodify_database.db')
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
    connect = sqlite3.connect('moodify_database.db')
    cursor = connect.cursor()

    date_today = datetime.date.today().isoformat()  #2025-05-20 fromat current date

    cursor.execute("INSERT INTO stress_quiz (profile, date, score, stress_level) VALUES (?, ?, ?, ?)",
              (profile, date_today, score, level))

    connect.commit()
    connect.close()  

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#title label
title = tk.Label(root, text="Stress Level Survey📃", font=("Comic Sans MS", 18, "bold"), bg="#FCF8E8", fg="#333")
title.pack(pady=10)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Frame to hold instruction label and restart button side by side
instruction_frame = tk.Frame(root, bg="#FCF8E8")
instruction_frame.pack(pady=(0, 10))

#instruction label to tell user what to do
instruction_label = tk.Label(instruction_frame, text="Hi! Please press one of the buttons below to answer each question.", font=("Segoe UI", 13, "italic"), bg="#FCF8E8", fg="#555", wraplength=500, justify="left")
instruction_label.pack(side="left",pady=(0, 10),anchor="w")

# Progress bar
progress = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
progress.place(relx=0.532, rely=0.19, anchor="e")
progress["maximum"] = 10

# Restart button
def reset_quiz():
    global current_index, user_scores
    current_index = 0
    user_scores = []
    progress["value"] = 0
    for widget in chat_frame.winfo_children():
        widget.destroy()
    result_label.config(text="[Your stress level and tips will be displayed here.]")
    chat_canvas.yview_moveto(0)  # Scroll to top when restarting
    display_next_question()

reset_btn = tk.Button(instruction_frame, text="🔁 Restart Survey", font=("Segoe UI", 12, "bold"),bg="#FFECB3", fg="#333", command=reset_quiz, relief="ridge", padx=5, pady=3)
reset_btn.pack(side="left",anchor="e")

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
main_frame = tk.Frame(root, bg="#FCF8E8")
main_frame.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.9, relheight=0.6)

# Left frame for chat box
left_frame = tk.Frame(main_frame, bg="#FFFFFF", bd=2, relief="flat")
left_frame.place(relx=0, rely=0, relwidth=0.55, relheight=1)

# Right frame for result tips
right_frame = tk.Frame(main_frame, bg="#FCF8E8")
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
        response_label = tk.Label(chat_frame, text=f"🧍 You: {answer}", font=("Calibri", 14), bg="#E1F5FE", fg="#2A3C5B", wraplength=560, justify="right", padx=10, pady=5,anchor="e")
        response_label.pack(pady=5, anchor="e")

    # Inside display_next_question(), after displaying the user response
    timestamp = datetime.datetime.now().strftime("%I:%M %p")
    time_label = tk.Label(chat_frame, text=timestamp, font=("Segoe UI", 8), bg="#FFFFFF", fg="#888")
    time_label.pack(anchor="e", padx=10)

    #move to the next question if there's a new answer
    if current_index < len(quiz_questions): #check if there are more question to display
        #display the question as a chat bubble
        #label to display the question
        question_label = tk.Label(chat_frame, text=f"🤖 Q{current_index+1}: {quiz_questions[current_index]}", font=("Calibri", 13,"bold"), bg="#F3E5F5", fg="#3D3D3D", wraplength=560,  padx=10, pady=5)
        question_label.pack(pady=10, anchor="w")

        #display options as buttons
        options = quiz_options[current_index]
        button_frame = tk.Frame(chat_frame, bg="white")
        button_frame.pack(pady=5, anchor="center")

        for option in options:                                                         #When clicked, it calls display_next_question(opt), passing the selected option as the answer #button_frame to remove the options after a selection
            button = tk.Button(button_frame, text=option, bg="#D1C4E9",fg="#222222", relief="flat", command=lambda opt=option: [display_next_question(opt), button_frame.destroy()],activebackground="#B39DDB",activeforeground="white",font=("Segoe UI", 12))
            button.pack(side="left", padx=5)
        
        current_index += 1 #+1 and move to next question
        progress["value"] = current_index
    else:
        calculate_stress_level()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Display an intro message before the first question
intro_label = tk.Label(chat_frame, text="🤖 Hi! I'm here to check your stress level. Let's begin the survey!", 
                       font=("Calibri", 13, "bold"), bg="#FFF3E0", fg="#4E342E", wraplength=560, padx=10, pady=5)
intro_label.pack(pady=10, anchor="w")

# Delay the first question slightly to simulate a chat feel
root.after(1000, display_next_question)  # delay 1 second before showing the first question

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Run the main program
root.mainloop()
