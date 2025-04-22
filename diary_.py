import tkinter as tk
import random
from datetime import datetime #to get current date and time
from tkinter import messagebox #for show pop-up message
import sqlite3

#counts how many words are in the diary
def word_count(event=None): #event=None:means it can be called with/without event
    content = text_entry.get("1.0", "end-1c")  #get full text from text widget #1.0=start from line 1,character 0(very beginning) #end-1c=means up to one character before the end 
    words = content.split() #split the entire string into a list of words
    word_count = len(words) #len(words)=count how many words in the list #len=return the length of something
    word_count_label.config(text=f"{word_count} words") #update the label

#save users entry #save as txt file(temporary) after that will change to json
#def save_entry():
    #diary_text=text_entry.get("1.0","end-1c")  #get the dairy text
    #current_date = datetime.now().strftime("%Y-%m-%d") #get current date
    #file_name=f"diary_{current_date}.txt" #create a filename with the date
    #with open(file_name, "w", encoding="utf-8") as file: #"w"=write mode #encoding="utf-8" is to ensures it can handle characters like emojis, symbols, and other non-English text correctly
        #file.write(f"Date: {current_date}\n\n") #\n\n=add two line breaks to separate the date from the diary content
        #file.write(diary_text)
    #messagebox.showinfo("Saved!", f"Your diary entry has been saved as:\n{file_name}") #print a message to show a popup

#main window
root=tk.Tk()
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}") #Full-screen size
root.title("Diary📖")
root.configure(bg="#fdf6f0")

#title label
title=tk.Label(root, text="My Diary😸", font=("Helvetica", 20, "bold"),bg="#fdf6f0",fg="#333")
title.pack(pady=10)

#get current date 
current_date = datetime.now().strftime("%B %d, %Y")  #strftime=string format time #Format:%B=Month, %d=Day, %Y=Year

#label to display the current date
cur_date_label=tk.Label(root, text=current_date, font=("Times New Roman",15),bg="#fdf6f0", fg="#333")
cur_date_label.pack(pady=5)

#print random reflection prompts
reflection_prompts=["What emotion have you felt the most today? Why?",
                    "How have you been treating yourself lately? Kindly or harshly?",
                    "What are the things that have brought you the most peace or joy today?",
                    "How are you feeling right now on a scale of 1 to 10?",
                    "Did you experience any negative thoughts today, and how did you challenge them?",
                    "Did anything interesting happen today?",
                    "What do you remember about my dreams last night?",
                    "What image or color comes to mind when you think of peace?"]
random_refle_prom=random.choice(reflection_prompts) #computer will random choose one prompts and display
print(random_refle_prom)

#label to display the reflection prompts
promts_label=tk.Label(root, text=random_refle_prom, font=("Calibri",12),bg="#fdf6f0", fg="#333", wraplength=600)
promts_label.pack(pady=10)

#frame to hold the diary area for styling
diary_frame=tk.Frame(root, bg="#fdf6f0", bd=5, relief="ridge", padx=20, pady=20)
diary_frame.pack()

#blank text area
text_entry=tk.Text(root,height=20,width=80)
text_entry.pack()

#word count
word_count_label = tk.Label(root, text="0 words", font=("Times New Roman", 12), bg="#fdf6f0", fg="#666")
word_count_label.pack(pady=(5, 10))

def save_diary():
    #Fetch all text (character 0 till end)
    entry_text = text_entry.get("1.0", tk.END).strip()

    #Check for empty entry
    if not entry_text:
        #Display warning box
        tk.messagebox.showwarning("Empty Entry", "Please write something before saving.")
        return

    #Connect to database
    connect = sqlite3.connect("C:/Users/Madhushaa/Projects/Moodify/user_info.db")
    #Create cursor
    cursor = connect.cursor()

    #Create new table in the same database file
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diary_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile TEXT,
            date TEXT,
            entry TEXT,
            FOREIGN KEY (profile) REFERENCES user_info(profile)
        )
    """) #Foreign key is to link 2 tables together

    #Check if entry already exists for the profile and exact date
    cursor.execute("SELECT * FROM diary_entries WHERE profile=? AND date=?", (profile, date))
    result = cursor.fetchone()

    if result:
        #Update entry that already exist
        cursor.execute("UPDATE diary_entries SET entry=? WHERE profile=? AND date=?", (entry_text, profile, date))
    else:
        #Insert new record into table
        cursor.execute("INSERT INTO diary_entries (profile, date, entry) VALUES (?, ?, ?)", (profile, date, entry_text))

    #Save data, update
    connect.commit()
    #Close connection
    connect.close()
    #Conformation message
    tk.messagebox.showinfo("Saved", "Diary entry saved!")
    
#create a save button
save_button=tk.Button(root,text="Save Entry", command=save_diary, font=("Times New Roman", 12), bg="#f8c9c9", fg="black") #command=save_entry is to call save_entry function to  save diary
save_button.pack(pady=10)

#connect the text box to word counter
text_entry.bind("<KeyRelease>", word_count) #everytime type/delete something,it triggers word_count 

#run the whole program
root.mainloop()