import tkinter as tk
from tkinter import ttk

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

#instruction label to tell user what to do
instruction_label = tk.Label(root, text="Hi! Please press one of the buttons below to answer each question.", font=("Segoe UI", 12, "italic"), bg="#FCF8E8", fg="#555", wraplength=600, justify="center")
instruction_label.pack(pady=(0, 10))

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
chat_box = tk.Frame(root, bg="white", bd=3, relief="solid")
chat_box.place(relx=0.5, rely=0.43, anchor="center", width=600, height=400) #relx=horizontal,value between 0.0 (left) and 1.0 (right) #rely=vertical.value between 0.0 (top) and 1.0 (bottom)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Scrollbar inside the chat box
scrollbar = ttk.Scrollbar(chat_box, orient="vertical")
scrollbar.pack(side="right", fill="y")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Canvas for scrollable area
chat_canvas = tk.Canvas(chat_box, bg="white", yscrollcommand=scrollbar.set, highlightthickness=0) #yscrollcommand=scrollbar.set:connects the canvas's vertical scrolling to the scrollbar
chat_canvas.pack(side="left", fill="both", expand=True)
scrollbar.config(command=chat_canvas.yview) #when move the scrollbar, it scrolls the canvas vertically using .yview()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Frame inside canvas where chat messages will appear
chat_frame = tk.Frame(chat_canvas, bg="white")
chat_canvas.create_window((0, 0), window=chat_frame, anchor="nw")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Update the scroll region when adding new widgets
def update_scroll_region(event=None): #event=None:allow function to be called automatically by an event
    chat_canvas.configure(scrollregion=chat_canvas.bbox("all")) #chat_canvas.configure(scrollregion=...): Updates the scrollable area of the canvas so that it fits all its content
                                                                #chat_canvas.bbox("all"): Gets the bounding box (min and max x/y coordinates) of everything inside the canvas.
chat_frame.bind("<Configure>", update_scroll_region)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Result label (outside and below the chat interface)
result_label = tk.Label(root, text="Your stress level and tips will be displayed here.", font=("Segoe UI", 14), bg="#FCF8E8", fg="#333", wraplength=800, justify="left")
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
    result_label.config(text=f"Your Stress Level: {level}\nTips: {tips}", font=("Comic Sans MS", 14, "bold"))

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
        response_label = tk.Label(chat_frame, text=answer, font=("Segoe UI", 14), bg="#d3ffd3", fg="#333", wraplength=600, justify="left", padx=10, pady=5)
        response_label.pack(pady=5, anchor="e")

    #move to the next question if there's a new answer
    if current_index < len(quiz_questions): #check if there are more question to display
        #display the question as a chat bubble
        #label to display the question
        question_label = tk.Label(chat_frame, text=quiz_questions[current_index], font=("Segoe UI", 14), bg="#f2f2f2", fg="#333", wraplength=600, justify="left", padx=10, pady=5)
        question_label.pack(pady=5, anchor="center",expand=True,fill="x")

        #display options as buttons
        options = quiz_options[current_index]
        button_frame = tk.Frame(chat_frame, bg="white")
        button_frame.pack(pady=5, anchor="center")

        for option in options:                                                         #When clicked, it calls display_next_question(opt), passing the selected option as the answer #button_frame to remove the options after a selection
            button = tk.Button(button_frame, text=option, bg="#ffe0e0", relief="flat", command=lambda opt=option: [display_next_question(opt), button_frame.destroy()], font=("Segoe UI", 12))
            button.pack(side="left", padx=5)
        
        current_index += 1 #+1 and move to next question
    else:
        calculate_stress_level()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Display the first question
display_next_question()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Run the main program
root.mainloop()
