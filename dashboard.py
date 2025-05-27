import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from datetime import date, datetime, timedelta

plt.style.use('fivethirtyeight') 

def get_profile():
    connect = sqlite3.connect('moodify_database.db')
    cursor = connect.cursor()
    cursor.execute("SELECT profile FROM user_info ORDER BY ROWID DESC LIMIT 1")
    result = cursor.fetchone()
    connect.close()
    return result[0] if result else None

#3 different views
def get_date_range(view_mode):
    today = datetime.today()
    if view_mode == 'weekly':
        return [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    elif view_mode == 'monthly':
        return [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]
    elif view_mode == 'annual':
        return [(today.replace(month=1, day=1) + timedelta(days=i)).strftime('%Y-%m-%d') 
                for i in range((today - today.replace(month=1, day=1)).days + 1)]
    else:
        return []

def get_breathing_data(profile):
    connect = sqlite3.connect('moodify_database.db')
    cursor = connect.cursor()
    today = datetime.today()
    last_7_days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    breathing_data = []
    for date in last_7_days:
        cursor.execute('''
            SELECT completed_sessions FROM breathing_exercise
            WHERE profile = ? AND date = ?
        ''', (profile, date))
        result = cursor.fetchone()
        breathing_data.append(result[0] if result else 0)
    connect.close()
    return last_7_days, breathing_data

def get_mood_data(profile):
    connect = sqlite3.connect("moodify_database.db")
    cursor = connect.cursor()
    cursor.execute('''
        SELECT mood, COUNT(*) FROM mood_entries
        WHERE profile = ? AND date >= DATE('now', '-6 days')
        GROUP BY mood
    ''', (profile,))
    data = cursor.fetchall()
    connect.close()
    all_moods = ["Happy", "Sad", "Angry", "Excited", "Sleepy", "Relaxed"]
    mood_counts = {mood: 0 for mood in all_moods}
    for mood, count in data:
        if mood in mood_counts:
            mood_counts[mood] = count
    filtered = {k: v for k, v in mood_counts.items() if v > 0}
    return list(filtered.keys()), list(filtered.values())

def get_diary_data(profile):
    connect = sqlite3.connect("moodify_database.db")
    cursor = connect.cursor()
    today = datetime.today()
    last_7_days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    entry_counts = []
    for date in last_7_days:
        cursor.execute('''
            SELECT COUNT(*) FROM diary_entries
            WHERE profile = ? AND date = ?
        ''', (profile, date))
        result = cursor.fetchone()
        entry_counts.append(result[0] if result else 0)
    connect.close()
    return last_7_days, entry_counts

def get_stress_data(profile):
    connect = sqlite3.connect("moodify_database.db")
    cursor = connect.cursor()
    today = date.today()
    last_7_days = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    placeholders = ','.join(['?'] * len(last_7_days))
    cursor.execute(f'''
        SELECT date, stress_level FROM stress_quiz 
        WHERE profile = ? AND date IN ({placeholders})
    ''', [profile] + last_7_days)
    results = cursor.fetchall()
    connect.close()
    stress_levels = {date_: level for date_, level in results}
    level_map = {'Low': 1, 'Medium': 2, 'High': 3}
    values = [level_map.get(stress_levels.get(day), 0) for day in last_7_days]
    return last_7_days, values

#Embed Matplotlib chart inside Tkinter frame
def embed_chart(fig, parent):
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill='both')

# Create all figures
def create_weekly_charts(profile, container):
    for widget in container.winfo_children():
        widget.destroy()

    #Retrieve data
    dates, sessions = get_breathing_data(profile)
    moods, mood_counts = get_mood_data(profile)
    dates_diary, diary_counts = get_diary_data(profile)
    dates_stress, stress_levels = get_stress_data(profile)
    
    charts = []

    #Chart 1: Breathing Exercise - Bar Chart
    plt.style.use('fivethirtyeight')
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    bars = ax1.bar(dates, sessions, color="#c3b091")
    ax1.set_title("Breathing Sessions")
    ax1.set_xticks(range(len(dates)))
    ax1.set_xticklabels(dates, rotation=45)
    fig1.tight_layout()
    charts.append(fig1)

    # Chart 2: Mood Tracker - Pie Chart
    plt.style.use('fivethirtyeight')
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    colors = ['#FFD700', '#87CEEB', '#FF6347', '#FF69B4', '#C0C0C0', '#90EE90']
    color_map = {
        "Happy": '#FFD700', "Sad": '#87CEEB', "Angry": '#FF6347',
        "Excited": '#FF69B4', "Sleepy": '#C0C0C0', "Relaxed": '#90EE90'
    }
    pie_colors = [color_map[mood] for mood in moods]
    ax2.pie(mood_counts, labels=moods, autopct='%1.1f%%', colors=pie_colors, startangle=140)
    ax2.set_title("Mood Distribution")
    fig2.tight_layout()
    charts.append(fig2)

    # Chart 3: Diary Entry - Line Chart
    plt.style.use('fivethirtyeight')
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    ax3.plot(dates_diary, diary_counts, marker='o', color='#6a5acd')
    ax3.set_title("Diary Entries")
    ax3.set_xticks(range(len(dates_diary)))
    ax3.set_xticklabels(dates_diary, rotation=45)
    fig3.tight_layout()
    charts.append(fig3)

    # Chart 4: Stress Quiz - Horizontal Bar Chart
    plt.style.use('fivethirtyeight')
    fig4, ax4 = plt.subplots(figsize=(5, 4))
    ax4.barh(dates_stress, stress_levels, color='purple')
    ax4.set_title("Stress Levels")
    ax4.set_xlim(0, 4)
    ax4.set_xticks([1, 2, 3])
    ax4.set_xticklabels(['Low', 'Medium', 'High'])
    fig4.tight_layout()
    charts.append(fig4)

    #Layout
    for i, fig in enumerate([fig1, fig2, fig3, fig4]):
        frame = tk.Frame(container, bg='white')
        frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')
         # Allow each frame to resize properly
        container.grid_rowconfigure(i // 2, weight=1)
        container.grid_columnconfigure(i % 2, weight=1)

        for widget in frame.winfo_children():
            widget.destroy()

        embed_chart(fig, frame)

def main():
    profile = get_profile()
    if not profile:
        print("No profile found.")
        return

    #Setup main Tkinter window
    root = tk.Tk()
    root.title("Moodify Dashboard")
    root.state("zoomed")
    root.configure(bg='white')

    #Sidebar
    sidebar = tk.Frame(root, width=200, bg="#2E2E2E")
    sidebar.pack(side="left", fill="y")

    tab_label = tk.Label(sidebar, text="VIEW BY", fg="#ffffff", bg="#2E2E2E", font=("Segoe UI", 14, "bold"))
    tab_label.pack(pady=20)
    
    #Main area for charts
    main_area = tk.Frame(root, bg="white")
    main_area.pack(side="right", expand=True, fill="both")
    
    #Make the main_area resizable in grid
    main_area.grid_rowconfigure((0,1), weight=1)
    main_area.grid_columnconfigure((0,1), weight=1)

    def on_hover(e): e.widget.config(bg="#5C5C5C")
    def on_leave(e): e.widget.config(bg="#3C3C3C")

    def load_weekly():
        create_weekly_charts(profile, main_area)
        
        #Ceate sidebar buttons
        for tab in ["Weekly", "Monthly", "Annual"]:
            btn = tk.Button(
                sidebar, text=tab, fg="#ffffff", bg="#3C3C3C", relief="flat", font=("Segoe UI", 12), width=18, height=2, activebackground="#5C5C5C"
            )
            btn.pack(pady=10)
            btn.bind("<Enter>", on_hover)
            btn.bind("<Leave>", on_leave)
            btn.config(command=lambda t=tab.lower(): create_weekly_charts(profile, main_area))

    # Load default view
    load_weekly()

    root.mainloop()

if __name__ == "__main__":
    main()