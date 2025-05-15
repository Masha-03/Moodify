import tkinter as tk

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#main window
root = tk.Tk()  #create the main app window
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")  #full-screen size
root.title("Stress Level Quiz")
root.configure(bg="#FCF8E8")  #change the background color of entire window

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#title label
title = tk.Label(root, text="Stress Level Survey", font=("Segoe UI", 18, "bold"), bg="#FCF8E8", fg="#333")
title.pack(pady=10)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#list of the quiz questions
quiz_questions = [
    "How often do you feel overwhelmed by your responsibilities?",
    "Do you have trouble sleeping due to racing thoughts?",
    "How often do you feel anxious or worried?",
    "Do you experience physical symptoms like headaches or stomachaches when stressed?",
    "How often do you feel like you can't handle things?"
]

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#list of the answers options for each question 
quiz_options = [
    ["Rarely", "Sometimes", "Frequently", "Always"],
    ["Never", "Sometimes", "Often", "Every night"],
    ["Seldom", "Occasionally", "Often", "Constantly"],
    ["Rarely", "Sometimes", "Frequently", "Always"],
    ["Never", "Sometimes", "Often", "Always"]
]

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#variable to keep track the current question index
current_index = 0 #set 0 to display the first question first

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#frames for the messages and buttons
chat_frame = tk.Frame(root, bg="#FCF8E8")
chat_frame.pack(pady=10, padx=20)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#function to display next question
def display_next_question(answer=None): #answer=None:parameter that stores the selected answer #if users selected a answer it will pass to a function
    global current_index #used to track which question in the quiz is currently being displayed

    #show the user response
    if answer:
        response_label = tk.Label(chat_frame, text=answer, font=("Segoe UI", 14), bg="#d3ffd3", fg="#333", wraplength=600, justify="left", padx=10, pady=5)
        response_label.pack(pady=5, anchor="e")

    #move to the next question if there's a new answer
    if current_index < len(quiz_questions): #check if there are more question to display
        #display the question as a chat bubble
        #label to display the question
        question_label = tk.Label(chat_frame, text=quiz_questions[current_index], font=("Segoe UI", 14), bg="#f2f2f2", fg="#333", wraplength=600, justify="left", padx=10, pady=5)
        question_label.pack(pady=5, anchor="w")

        #display options as buttons
        options = quiz_options[current_index]
        button_frame = tk.Frame(chat_frame, bg="#FCF8E8")
        button_frame.pack(pady=5, anchor="e")

        for option in options:                                                         #When clicked, it calls display_next_question(opt), passing the selected option as the answer #button_frame to remove the options after a selection
            button = tk.Button(button_frame, text=option, bg="#ffe0e0", relief="flat", command=lambda opt=option: [display_next_question(opt), button_frame.destroy()], font=("Segoe UI", 12))
            button.pack(side="left", padx=5)
        
        current_index += 1 #+1 and move to next question
    else:
        #end message after the last question
        end_label = tk.Label(chat_frame, text="You have completed the quiz. Thank you!", font=("Segoe UI", 14), bg="#f2f2f2", fg="#333", wraplength=600, justify="left", padx=10, pady=5)
        end_label.pack(pady=5, anchor="w")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Display the first question
display_next_question()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Run the main program
root.mainloop()
