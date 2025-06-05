import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from collections import defaultdict, Counter

plt.style.use('fivethirtyeight') 

def get_profile():
    connect = sqlite3.connect('moodify_database.db')
    cursor = connect.cursor()
    cursor.execute("SELECT profile FROM user_info ORDER BY ROWID DESC LIMIT 1")
    result = cursor.fetchone()
    connect.close()
    return result[0] if result else None

#3 different views
def date_range(view_mode):
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

def get_breathing_data(profile, date_range_list):
    connect = sqlite3.connect('moodify_database.db')
    cursor = connect.cursor()
    sessions = []
    for day in date_range_list:
        cursor.execute('''
            SELECT completed_sessions FROM breathing_exercise
            WHERE profile = ? AND date = ?
        ''', (profile, day))
        result = cursor.fetchone()
        sessions.append(result[0] if result else 0)
    connect.close()
    return date_range_list, sessions

def get_mood_data(profile, date_range_list):
    connect = sqlite3.connect("moodify_database.db")
    cursor = connect.cursor()
    start_date = date_range_list[0]

    cursor.execute('''
        SELECT mood, COUNT(*) FROM mood_entries
        WHERE profile = ? AND date >= ?
        GROUP BY mood
    ''', (profile, start_date))
    
    data = cursor.fetchall()
    connect.close()

    all_moods = ["Happy", "Sad", "Angry", "Excited", "Sleepy", "Relaxed"]
    mood_counts = {mood: 0 for mood in all_moods}
    for mood, count in data:
        if mood in mood_counts:
            mood_counts[mood] = count
    filtered = {k: v for k, v in mood_counts.items() if v > 0}
    return list(filtered.keys()), list(filtered.values())

def get_diary_data(profile, date_range_list):
    connect = sqlite3.connect("moodify_database.db")
    cursor = connect.cursor()
    counts = []
    for day in date_range_list:
        cursor.execute('''
            SELECT COUNT(*) FROM diary_entries
            WHERE profile = ? AND date = ?
        ''', (profile, day))
        result = cursor.fetchone()
        counts.append(result[0] if result else 0)
    connect.close()
    return date_range_list, counts

def get_stress_data(profile, date_range_list):
    connect = sqlite3.connect("moodify_database.db")
    cursor = connect.cursor()
    placeholders = ','.join(['?'] * len(date_range_list))

    cursor.execute(f'''
        SELECT date, stress_level FROM stress_quiz 
        WHERE profile = ? AND date IN ({placeholders})
    ''', [profile] + date_range_list)

    results = cursor.fetchall()
    connect.close()

    level_map = {'Low': 1, 'Medium': 2, 'High': 3}
    stress_levels = {date_: level_map.get(level, 0) for date_, level in results}
    values = [stress_levels.get(day, 0) for day in date_range_list]
    return date_range_list, values

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
    mode = "weekly"  
    range_list = date_range(mode)

    dates, sessions = get_breathing_data(profile, range_list)
    dates_diary, diary_counts = get_diary_data(profile, range_list)
    dates_stress, stress_levels = get_stress_data(profile, range_list)
    moods, mood_counts = get_mood_data(profile, range_list)
        
    charts = []

    # Chart 1: Breathing Exercise - Bar Chart
    plt.style.use('fivethirtyeight')
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    bars = ax1.bar(dates, sessions, color="#c3b091")
    first_date = datetime.strptime(dates[0], '%Y-%m-%d')  # convert string to datetime
    month_year = first_date.strftime('%B %Y')  #month and year rn
    ax1.set_title(f"Breathing Sessions - {month_year}", fontsize=18)
    ax1.set_xticks(range(len(dates)))
    #Only show the day
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.setp(ax1.get_xticklabels(), rotation=0, fontsize=14)
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
    first_date = datetime.strptime(dates[0], '%Y-%m-%d')  # convert string to datetime
    month_year = first_date.strftime('%B %Y')  #month and year rn
    ax2.set_title(f"Mood Distribution - {month_year}", fontsize=18)
    fig2.tight_layout()
    charts.append(fig2)

    # Chart 3: Diary Entry - Line Chart
    plt.style.use('fivethirtyeight')
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    ax3.plot(dates_diary, diary_counts, marker='o', color='#6a5acd')
    first_date = datetime.strptime(dates[0], '%Y-%m-%d')  # convert string to datetime
    month_year = first_date.strftime('%B %Y')  #month and year rn
    ax3.set_title(f"Diary Entries - {month_year}", fontsize=18)
    ax3.set_xticks(range(len(dates_diary)))
    #Only show the day
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.setp(ax3.get_xticklabels(), rotation=0, fontsize=14)
    fig3.tight_layout()
    charts.append(fig3)

    # Chart 4: Stress Quiz - Horizontal Bar Chart
    plt.style.use('fivethirtyeight')
    fig4, ax4 = plt.subplots(figsize=(5, 4))
    ax4.barh(dates_stress, stress_levels, color='purple')
    #Only show the day
    ax4.yaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.setp(ax4.get_xticklabels(), rotation=0, fontsize=15)
    first_date = datetime.strptime(dates[0], '%Y-%m-%d')  # convert string to datetime
    month_year = first_date.strftime('%B %Y')  #month and year rn
    ax4.set_title(f"Stress Levels - {month_year}", fontsize=18)
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
        
def create_monthly_charts(profile, container):
    for widget in container.winfo_children():
        widget.destroy()

    mode = "monthly"  
    range_list = date_range(mode)
    dates, sessions = get_breathing_data(profile, range_list)
    dates_diary, diary_counts = get_diary_data(profile, range_list)
    dates_stress, stress_levels = get_stress_data(profile, range_list)
    moods, mood_counts = get_mood_data(profile, range_list)
    
    filtered_sessions = [(d, s) for d, s in zip(dates, sessions) if s > 0]
    if filtered_sessions:
        dates, sessions = zip(*filtered_sessions)
    else:
        dates, sessions = [], []

    #Chart 1: Breathing Exercise - Bar Chart
    charts = []
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    ax1.bar(dates, sessions, color="#c3b091")
    first_date = datetime.strptime(dates[0], '%Y-%m-%d')  # convert string to datetime
    month_year = first_date.strftime('%B %Y')  #month and year rn
    ax1.set_title(f"Breathing Sessions - {month_year}", fontsize=18)
    ax1.set_xticks(range(len(dates)))
     #Only show the day
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.setp(ax1.get_xticklabels(), rotation=0, fontsize=14)
    fig1.tight_layout()
    charts.append(fig1)

    # Chart 2: Mood Tracker - Pie Chart
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    color_map = {
        "Happy": '#FFD700', "Sad": '#87CEEB', "Angry": '#FF6347',
        "Excited": '#FF69B4', "Sleepy": '#C0C0C0', "Relaxed": '#90EE90'
    }
    pie_colors = [color_map[mood] for mood in moods]
    ax2.pie(mood_counts, labels=moods, autopct='%1.1f%%', colors=pie_colors, startangle=140)
    first_date = datetime.strptime(dates[0], '%Y-%m-%d')  # convert string to datetime
    month_year = first_date.strftime('%B %Y')  #month and year rn
    ax2.set_title(f"Mood Distribution - {month_year}", fontsize=18)
    fig2.tight_layout()
    charts.append(fig2)

    # Chart 3: Diary Entry - Line Chart
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    ax3.plot(dates_diary, diary_counts, marker='o', color='#6a5acd')
    first_date = datetime.strptime(dates[0], '%Y-%m-%d')  # convert string to datetime
    month_year = first_date.strftime('%B %Y')  #month and year rn
    ax3.set_title(f"Diary Entries - {month_year}", fontsize=18)
    ax3.set_xticks(range(len(dates_diary)))
     #Only show the day
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.setp(ax3.get_xticklabels(), rotation=0, fontsize=8)
    fig3.tight_layout()
    charts.append(fig3)

    # Chart 4: Stress Quiz - Horizontal Bar Chart
    fig4, ax4 = plt.subplots(figsize=(5, 4))
    ax4.barh(dates_stress, stress_levels, color='purple')
    #Only show the day
    ax4.yaxis.set_major_formatter(mdates.DateFormatter('%d'))
    ax4.tick_params(axis='y', labelsize=6)
    first_date = datetime.strptime(dates[0], '%Y-%m-%d')  # convert string to datetime
    month_year = first_date.strftime('%B %Y')  #month and year rn
    ax4.set_title(f"Stress Levels - {month_year}", fontsize=18)
    ax4.set_xlim(0, 4)
    ax4.set_xticks([1, 2, 3])
    ax4.set_xticklabels(['Low', 'Medium', 'High'])
    fig4.tight_layout()
    charts.append(fig4)

    for i, fig in enumerate(charts):
        frame = tk.Frame(container, bg='white')
        frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')
        container.grid_rowconfigure(i // 2, weight=1)
        container.grid_columnconfigure(i % 2, weight=1)
        embed_chart(fig, frame)

# Get mood entries for annual average calculation
def get_annual_mood_data(profile, date_list):
    connect = sqlite3.connect("moodify_database.db")
    cursor = connect.cursor()
    placeholders = ','.join('?' * len(date_list))
    cursor.execute(f'''
        SELECT date, mood FROM mood_entries
        WHERE profile = ? AND date IN ({placeholders})
    ''', [profile] + date_list)
    results = cursor.fetchall()
    connect.close()
    dates = [row[0] for row in results]
    mood_levels = [row[1] for row in results]  # numeric mood level assumed
    return dates, mood_levels

def calculate_mood_frequencies(mood_names):
    freq = Counter(mood_names)
    labels = list(freq.keys())
    counts = list(freq.values())
    return labels, counts

def calculate_monthly_average(dates, values):
    monthly_totals = defaultdict(list)

    for date_str, value in zip(dates, values):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        month_label = date_obj.strftime('%b')  # e.g., Jan, Feb, etc.
        monthly_totals[month_label].append(value)

    # Ensure months appear in calendar order
    months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    monthly_averages = []
    for month in months_order:
        values = monthly_totals.get(month, [])
        avg = sum(values) / len(values) if values else 0
        monthly_averages.append(avg)
    
    return months_order, monthly_averages

def create_annual_charts(profile, container):
    for widget in container.winfo_children():
        widget.destroy()

    mode = "annual"  
    range_list = date_range(mode)
    dates, sessions = get_breathing_data(profile, range_list)
    dates_diary, diary_counts = get_diary_data(profile, range_list)
    dates_stress, stress_levels = get_stress_data(profile, range_list)
    mood_dates, mood_levels = get_annual_mood_data(profile, range_list)
    moods, mood_counts = get_mood_data(profile, range_list)

    charts = []
    
    # Chart 1: Breathing Sessions - Bar Chart
    months, avg_sessions = calculate_monthly_average(dates, sessions)
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    ax1.bar(months, avg_sessions, color="#c3b091")
    ax1.set_title("Breathing Sessions - Annual")
    ax1.set_xticks(range(len(months)))
    ax1.set_xticklabels(months, fontsize=10)
    fig1.tight_layout()
    charts.append(fig1)

    # Chart 2: Mood Distribution - Pie Chart
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    color_map = {
        "Happy": '#FFD700', "Sad": '#87CEEB', "Angry": '#FF6347',
        "Excited": '#FF69B4', "Sleepy": '#C0C0C0', "Relaxed": '#90EE90'
    }
    pie_colors = [color_map[mood] for mood in moods]
    ax2.pie(mood_counts, labels=moods, autopct='%1.1f%%', colors=pie_colors, startangle=140)
    ax2.set_title("Mood Distribution -Annual")
    fig2.tight_layout()
    charts.append(fig2)

    # Chart 3: Diary Entries - Line Chart
    _, diary_avg = calculate_monthly_average(dates_diary, diary_counts)
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    ax3.plot(months, diary_avg, color='#6a5acd', linestyle='--', marker='s')
    ax3.set_title("Diary Entries - Annual")
    ax3.set_xticks(range(len(months)))
    ax3.set_xticklabels(months, fontsize=10)
    fig3.tight_layout()
    charts.append(fig3)
    
    # Chart 4: Stress Quiz - Horizontal Bar Chart
    _, stress_avg = calculate_monthly_average(dates_stress, stress_levels)
    fig4, ax4 = plt.subplots(figsize=(5, 4))
    ax4.barh(months, stress_avg, color='purple')
    ax4.set_title("Stress Levels - Annual")
    ax4.set_xlim(0, 4)
    ax4.set_xticks([1, 2, 3])
    ax4.set_xticklabels(['Low', 'Medium', 'High'])
    fig4.tight_layout()
    charts.append(fig4)

    for i, fig in enumerate(charts):
        frame = tk.Frame(container, bg='white')
        frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')
        container.grid_rowconfigure(i // 2, weight=1)
        container.grid_columnconfigure(i % 2, weight=1)
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
            if tab.lower() == "weekly":
                btn.config(command=lambda: create_weekly_charts(profile, main_area))
            elif tab.lower() == "monthly":
                btn.config(command=lambda: create_monthly_charts(profile, main_area))
            elif tab.lower() == "annual":
                btn.config(command=lambda: create_annual_charts(profile, main_area))

    # Load default view
    load_weekly()

    root.mainloop()

if __name__ == "__main__":
    main()