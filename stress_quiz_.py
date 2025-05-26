import tkinter as tk
from tkinter import ttk
import datetime

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#main window
root = tk.Tk()  #create the main app window
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")  #full-screen size
root.title("Stress Level Survey")
root.configure(bg="#FCF8E8")  #change the background color of entire window

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

# Restart button
def reset_quiz():
    global current_index, user_scores
    current_index = 0
    user_scores = []
    for widget in chat_frame.winfo_children():
        widget.destroy()
    result_label.config(text="[Your stress level and tips will be displayed here.]")
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
    "How often do you feel like you can't handle things?"
]

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#list of the answers options for each question 
quiz_options=[
    ["Rarely", "Sometimes", "Frequently", "Always"],
    ["Never", "Sometimes", "Often", "Every night"],
    ["Seldom", "Occasionally", "Often", "Constantly"],
    ["Rarely", "Sometimes", "Frequently", "Always"],
    ["Never", "Sometimes", "Often", "Always"]
]

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#assign scores to options
quiz_options_score=[
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
# Outer frame with border acting as the "box"
chat_box = tk.Frame(root, bg="#FFFFFF", bd=2, relief="flat")
chat_box.place(relx=0.5, rely=0.45, anchor="center", width=600, height=400) #relx=horizontal,value between 0.0 (left) and 1.0 (right) #rely=vertical.value between 0.0 (top) and 1.0 (bottom)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Scrollbar inside the chat box
scrollbar = ttk.Scrollbar(chat_box, orient="vertical")
scrollbar.pack(side="right", fill="y")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Canvas for scrollable area
chat_canvas = tk.Canvas(chat_box, bg="#FFFFFF", yscrollcommand=scrollbar.set, highlightthickness=0) #yscrollcommand=scrollbar.set:connects the canvas's vertical scrolling to the scrollbar
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

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Result label (outside and below the chat interface)
result_label = tk.Label(root, text="[Your stress level and tips will be displayed here.]", font=("Segoe UI", 14), bg="#FCF8E8", fg="#3A3D64", wraplength=800, justify="left")
# Place result_label just below the chat_box
result_label.pack(pady=(420, 20))  # Just below the title and chat box

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Function to calculate stress level and update the result label
def calculate_stress_level():
    total_score = sum(user_scores)
    
    # Determine stress level and tips
    if total_score <= 4:
        level = "Low Stress😊"
        tips = "You're managing your stress well. Keep up the good work!"
    elif 5 <= total_score <= 8:
        level = "Moderate Stress🤔"
        tips = "Take some time to relax. Practice deep breathing and mindfulness."
    elif 9 <= total_score <= 12:
        level = "High Stress😵‍💫"
        tips = "Your stress levels are getting high. Consider talking to a trusted friend or engaging in a calming activity."
    else:
        level = "Severe Stress🤒"
        tips = "Your stress levels are quite high. It might be helpful to seek support from a mental health professional."
    
    # Add result to chat_frame like a message
    result_label.config(text=f"✨ Stress Level: {level}\n💡 Tips: {tips}", font=("Comic Sans MS", 14, "bold"))

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
    else:
        calculate_stress_level()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Display an intro message before the first question
intro_label = tk.Label(chat_frame, text="🤖 Hi! I'm here to check your stress level. Let's begin the survey.", 
                       font=("Calibri", 13, "bold"), bg="#FFF3E0", fg="#4E342E", wraplength=560, padx=10, pady=5)
intro_label.pack(pady=10, anchor="w")

# Delay the first question slightly to simulate a chat feel
root.after(1000, display_next_question)  # delay 1 second before showing the first question

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Run the main program
root.mainloop()
