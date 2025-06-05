import tkinter as tk
import customtkinter as ctk

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#Tkinter instruction window
root = tk.Tk()
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
root.title("Moodify Instructions")
root.configure(bg="#FFF2E6")  # Soft peach background

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Title Label
title_label = tk.Label(root,text="🌼 Welcome to Moodify! 🌼",font=("Segoe UI", 20, "bold"),bg="#FFF2E6",fg="#4A4A4A",pady=20)
title_label.pack(pady=(10, 10))

# Outer frame (holds the framed instruction box)
outer_frame = tk.Frame(root, bg="#FFF2E6")
outer_frame.pack(pady=(0,10), padx=30, fill="both", expand=True)

# Inner box frame with visible border
box_frame = tk.Frame(outer_frame, bg="#FFEFE1", bd=3, relief="ridge",width=1100,height=420)
box_frame.pack(fill="x", expand=False,padx=20,pady=10)
box_frame.pack_propagate(False)

# Canvas inside the box
canvas = tk.Canvas(box_frame, bg="#FFEFE1", highlightthickness=0)
canvas.pack(side="left", fill="y")
canvas.configure(height=420,width=1100)

# Scrollbar INSIDE the box
scrollbar = tk.Scrollbar(box_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)

# Frame inside canvas for content
scrollable_frame = tk.Frame(canvas, bg="#FFEFE1")
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Auto scrollregion update
def update_scrollregion(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

scrollable_frame.bind("<Configure>", update_scrollregion)

# Enable scrolling with the mouse wheel
def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Bind mouse wheel to canvas (Windows and Linux)
canvas.bind_all("<MouseWheel>", on_mousewheel) #everytime the mouse wheel scrolled,call on_mousewheel event

# Bind mouse wheel for macOS (uses different event name)
canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Instruction Text
instruction_text = (
        "💡 How to Use:\n\n"
        "• Use the arrow keys to move your character.\n"
        "• Press Ctrl + F to toggle fullscreen mode.\n"
        "• Press Esc anytime to close the app.\n\n"
        "👀 There are *8 cool features* waiting for you to explore:\n\n"
        "📖 Tap the **books next to the radio** on the table to open your **Diary** — spill your thoughts, no judgment.\n"
        "😄 Tap the **emoji squad on the wall** to track your feels with the **Mood Tracker**.\n"
        "📅 Tap the **calendar on the wall** to throwback to your past moods and diary entries.\n"
        "🎧 Tap the **radio by the books** to vibe out with **chill sounds** — total zen.\n"
        "📊 Tap the **graph beside the calendar** to explore the **Statistics** feature and review your data.\n"
        "⏳ Tap the **hourglass by the TV** to do some **breathing exercises** — in, out, chill.\n"
        "📱 Tap the **phone under the settings icon** to take a quick **stress check quiz**.\n"
        "🌱 Tap the **plant next to the TV** to water it — help it grow like your inner peace.\n\n"
        "🔊 You can adjust or mute the background music anytime by clicking the **Settings** icon.\n"
        "✨ Bonus fun: Click the **sofa, cockroach, teddy bear, or pirate** for random cute bubble convos!\n"
        "🎮 Oh — and there are *3 hidden games* inside the computer. Go find 'em 👀\n\n"
        "🌟 This app is your chill zone. Take a break, have fun, and treat yourself!"
    )

instruction_label = tk.Label(scrollable_frame,text=instruction_text,font=("Segoe UI", 13),bg="#FFF2E6",fg="#333333",justify="left",wraplength=1000,padx=40,pady=20)
instruction_label.pack(pady=(0, 20))

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Run the app
root.mainloop()
