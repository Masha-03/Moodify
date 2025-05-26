import matplotlib.pyplot as plt #For graphs & charts
import sqlite3
from datetime import datetime, timedelta #timedelta - difference between dates
from collections import Counter #Calculate frequency

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

#Get breathing session data for the past 7 days
def get_breathing_data(profile):
    connect = sqlite3.connect('moodify_database.db')
    cursor = connect.cursor()

    today = datetime.today()
    #Create list of dates from 6 days ago till today
    last_7_days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)] #start = 6 - starts 6 days ago, stop = -1 - ends just before -1 (so includes 0)step = -1

    breathing_data = []
    for date in last_7_days:
        #Get how many sessions were completed
        cursor.execute('''
            SELECT completed_sessions FROM breathing_exercise
            WHERE profile = ? AND date = ?
        ''', (profile, date))
        result = cursor.fetchone()
        breathing_data.append(result[0] if result else 0)

    connect.close()
    return last_7_days, breathing_data

#Plot the bar chart
def plot_breathing_chart(dates, sessions):
    plt.style.use('ggplot') 

    #fig-window, ax-axes for chart
    fig, ax = plt.subplots(figsize=(12, 7))  #set figure size

    #Draw vertical bars
    bars = ax.bar(dates, sessions, color="#c3b091")
    #Title
    ax.set_title("Breathing Exercise Sessions in Past 7 Days", fontsize=16, fontweight='bold')
    #X-axis
    ax.set_xlabel("Date", fontsize=12)
    #Y-axis
    ax.set_ylabel("Completed Sessions", fontsize=12)
    #Add grid
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.tick_params(axis='x', labelsize=10)
    ax.tick_params(axis='y', labelsize=10)
    plt.xticks(rotation=45) #Rotates x-axis labels so dates don’t overlap

    #Add number on top of each bar
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, yval, ha='center', va='bottom', fontsize=10)
        
def get_weekly_mood_data(profile):
    connect = sqlite3.connect("moodify_database.db")
    cursor = connect.cursor()

    # Get mood counts from the past 7 days
    cursor.execute('''
        SELECT mood, COUNT(*) FROM mood_entries
        WHERE profile = ? AND date >= DATE('now', '-6 days')
        GROUP BY mood
    ''', (profile,))
    data = cursor.fetchall()
    connect.close()

    # Fill in zero for moods not selected
    all_moods = ["Happy", "Sad", "Angry", "Excited", "Sleepy", "Relaxed"]
    mood_counts = {mood: 0 for mood in all_moods}

    for mood, count in data:
        if mood in mood_counts:
            mood_counts[mood] = count

    # Remove moods with zero count (optional, keeps chart clean)
    filtered = {k: v for k, v in mood_counts.items() if v > 0}
    return list(filtered.keys()), list(filtered.values())

#Plot pie chart for mood tracker
def plot_mood_pie_chart(moods, counts):
    colors = ['#FFD700', '#87CEEB', '#FF6347', '#FF69B4', '#C0C0C0', '#90EE90']
    color_map = {  # Map specific colors to moods
        "Happy": '#FFD700',
        "Sad": '#87CEEB',
        "Angry": '#FF6347',
        "Excited": '#FF69B4',
        "Sleepy": '#C0C0C0',
        "Relaxed": '#90EE90'
    }
    pie_colors = [color_map[mood] for mood in moods]

    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=moods, colors=pie_colors, autopct='%1.1f%%', startangle=140)
    plt.title("Weekly Mood Distribution", fontsize=16, fontweight='bold')
    plt.axis('equal')  # Makes it a perfect circle
    plt.tight_layout()
    plt.show()
    
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

def plot_diary_line_chart(dates, counts):
    plt.style.use("fivethirtyeight")

    plt.figure(figsize=(12, 6))
    plt.plot(dates, counts, marker='o', color='#6a5acd', linewidth=2)
    plt.title("Diary Entries Over the Past 7 Days", fontsize=16, fontweight='bold')
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Number of Entries", fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)

    # Add data labels
    for i, count in enumerate(counts):
        plt.text(dates[i], count + 0.1, str(count), ha='center', fontsize=9)

    plt.tight_layout()
    plt.show()

#Run everything
get_profile()
if profile:
    dates, sessions = get_breathing_data(profile)
    plot_breathing_chart(dates, sessions)
    moods, counts = get_weekly_mood_data(profile)
    if counts:
        plot_mood_pie_chart(moods, counts)
    else:
        print("No mood data in the last 7 days.")
    dates, counts = get_diary_data(profile)
    if any(counts):
        plot_diary_line_chart(dates, counts)
    else:
        print("No diary entries in the last 7 days.")
else:
    print("No profile found.")