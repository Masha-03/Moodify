import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# main window
root = tk.Tk()
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")  # full-screen size
root.title("Stress Level Quiz")
root.configure(bg="#F1F3F6")  # background color

# title label
title = tk.Label(root, text="Stress Level Quiz", font=("Segoe UI", 18, "bold"), bg="#F1F3F6", fg="#34495E")
title.pack(pady=10)

# Load and resize robot image
robot_img = Image.open("robot.png")
robot_img = robot_img.resize((40, 40))
robot_photo = ImageTk.PhotoImage(robot_img)

# total 5 quiz questions
quiz_questions = [
    "How often do you feel overwhelmed by your responsibilities?",
    "Do you have trouble sleeping due to racing thoughts?",
    "How often do you feel anxious or worried?",
    "Do you experience physical symptoms like headaches or stomachaches when stressed?",
    "How often do you feel like you can't handle things?"
]

# options for users to choose 
quiz_options = [
    ["Rarely", "Sometimes", "Frequently", "Always"],
    ["Never", "Sometimes", "Often", "Every night"],
    ["Seldom", "Occasionally", "Often", "Constantly"],
    ["Rarely", "Sometimes", "Frequently", "Always"],
    ["Never", "Sometimes", "Often", "Always"]
]

# variable to track the current question index
current_index = 0

# frame for chat area with scrollbar
container = tk.Frame(root, bg="#F1F3F6")
container.pack(pady=10, padx=20, fill="both", expand=True)

canvas = tk.Canvas(container, bg="#F1F3F6")
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
chat_frame = tk.Frame(canvas, bg="#F1F3F6")

chat_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.create_window((0, 0), window=chat_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# function to create chat bubble
def create_bubble(text, align="left", bg_color="#D1E7FD", fg_color="#333333", with_image=False):
    bubble_frame = tk.Frame(chat_frame, bg="#F1F3F6")
    bubble_frame.pack(anchor="w" if align == "left" else "e", pady=5)

    if with_image:
        img_label = tk.Label(bubble_frame, image=robot_photo, bg="#F1F3F6")
        img_label.pack(side="left", padx=5)

    bubble = tk.Label(
        bubble_frame,
        text=text,
        font=("Segoe UI", 12),
        bg=bg_color,
        fg=fg_color,
        wraplength=500,
        padx=10,
        pady=5,
        justify="left"
    )
    bubble.pack(side="left")
    bubble.config(borderwidth=1, relief="solid", bd=2)
    bubble.update()

# function to display the next question
def display_next_question(answer=None):
    global current_index

    if answer:
        create_bubble(answer, align="right", bg_color="#A7D2CB", fg_color="#333333")

    if current_index < len(quiz_questions):
        create_bubble(quiz_questions[current_index], align="left", bg_color="#FFFFFF", fg_color="#34495E", with_image=True)

        # Display options as buttons
        options = quiz_options[current_index]
        button_frame = tk.Frame(chat_frame, bg="#F1F3F6")
        button_frame.pack(anchor="e", pady=5)

        for option in options:
            button = tk.Button(
                button_frame,
                text=option,
                bg="#A7D2CB",
                fg="#333333",
                font=("Segoe UI", 10),
                command=lambda opt=option: [display_next_question(opt), button_frame.destroy()]
            )
            button.pack(side="left", padx=5)
        
        current_index += 1
    else:
        create_bubble("You have completed the quiz. Thank you!", align="left", bg_color="#FFFFFF", fg_color="#34495E", with_image=True)

# Display the first question
display_next_question()

# run the main program
root.mainloop()
