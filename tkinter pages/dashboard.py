import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
import os
import sys
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from collections import defaultdict, Counter
import numpy as np
from tkinter import messagebox

plt.style.use('fivethirtyeight')

#Global list to track all charts
charts = [] 

def get_db_path():
    base_dir = None
    if getattr(sys, 'frozen', False):
        # When frozen (e.g., PyInstaller), sys._MEIPASS is the root where bundled files are.
        # If your 'database' folder is alongside the executable in the *final distributed package*,
        # you might need to adjust this depending on your PyInstaller --add-data configuration.
        # For now, let's assume the database folder is at the same level as the executable.
        app_root = sys._MEIPASS
    else:
        # In unfrozen mode, base_dir is 'c:\Users\Coshi\Moodify\tkinter pages'.
        # We need to go up one level to 'c:\Users\Coshi\Moodify'.
        script_dir = os.path.dirname(os.path.abspath(__file__)) # This is 'c:\Users\Coshi\Moodify\tkinter pages'
        app_root = os.path.dirname(script_dir) # This steps up to 'c:\Users\Coshi\Moodify'

    db_file_name = 'moodify_database.db'
    db_folder_name = 'database'

    # Now, join the app_root with the database folder and the file name
    db_path = os.path.join(app_root, db_folder_name, db_file_name)

    print(f"Running in {'frozen' if getattr(sys, 'frozen', False) else 'unfrozen'} mode.")
    print(f"Detected script directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Calculated application root: {app_root}")
    print(f"Calculated database path: {db_path}")

    return db_path

database_file_path = get_db_path()

# Check if the database file exists at the calculated path
if os.path.exists(database_file_path):
    print(f"Database file FOUND at: {database_file_path}")
else:
    print(f"Database file NOT FOUND at: {database_file_path}")
    print("WARNING: A new database file will likely be created here.")
    # Create the 'database' folder if it doesn't exist
    try:
        os.makedirs(os.path.dirname(database_file_path), exist_ok=True)
        print(f"Created directory: {os.path.dirname(database_file_path)}")
    except OSError as e:
        print(f"Error creating directory: {e}")

def get_profile():
    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()
    cursor.execute("SELECT profile FROM user_info ORDER BY ROWID DESC LIMIT 1")
    result = cursor.fetchone()
    connect.close()
    return result[0] if result else None

#Get profile from the database
def get_profile():
    global profile
    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()
    
    #Fetch the profile
    cursor.execute('''SELECT profile 
                   FROM user_info 
                   ORDER BY ROWID DESC LIMIT 1''') #Fetch latest profile by sorting profile from newest to oldest
    result = cursor.fetchone() #Fetch one only
    
    connect.close() #Close connection
    return result[0] if result else None

#3 different views
def date_range(view_mode):
    #Get today's date
    today = datetime.today()
    if view_mode == 'weekly':
        #list of last 7 days
        return [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)] #start, stop, step
    elif view_mode == 'monthly':
         #First day of this month
        first_day = today.replace(day=1)
        #Get last day of month
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        #Subtract 1 day from the first day of the next month to get the last day of the current month.
        last_day = next_month - timedelta(days=1)
        
        #Get how many days in a month
        days_in_month = (last_day - first_day).days + 1
        
        #Create list of dates strings for current month
        return [(first_day + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days_in_month)]
    
    elif view_mode == 'annual':
        #Jan 1 of current year
        year_start = today.replace(month=1, day=1)
        #Dec 31 of the current year
        year_end = today.replace(month=12, day=31)
        #Calculate number of days in the whole year
        total_days = (year_end - year_start).days + 1
        return [(year_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(total_days)]
    else:
        return []

def get_breathing_data(profile, date_range_list):
    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()
    sessions = []
    for day in date_range_list:
        cursor.execute('''
            SELECT completed_sessions FROM breathing_exercise
            WHERE profile = ? AND date = ?
        ''', (profile, day))
        result = cursor.fetchone()
        sessions.append(result[0] if result else 0) #if no result, then 0
    connect.close()
    return date_range_list, sessions

def get_mood_data(profile, date_range_list):
    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()
    start_date = date_range_list[0]
    #Count how many mood for the mood selected
    cursor.execute('''
        SELECT mood, COUNT(*) FROM mood_entries
        WHERE profile = ? AND date >= ?
        GROUP BY mood
    ''', (profile, start_date))
    
    data = cursor.fetchall()
    connect.close()

    all_moods = ["Happy", "Sad", "Angry", "Excited", "Sleepy", "Relaxed"]
    mood_counts = {mood: 0 for mood in all_moods} #Make sure all moods appear even if count 0
    for mood, count in data:
        if mood in mood_counts:
            mood_counts[mood] = count
    filtered = {k: v for k, v in mood_counts.items() if v > 0} #k=mood, v=count (only keep if count more than 0)
    return list(filtered.keys()), list(filtered.values()) #split mood and count into 2 different list

def get_diary_data(profile, date_range_list):
    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()
    #Count how many diary entries for each day
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
    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()
    placeholders = ','.join(['?'] * len(date_range_list))

    cursor.execute(f'''
        SELECT date, stress_level FROM stress_quiz 
        WHERE profile = ? AND date IN ({placeholders})
    ''', [profile] + date_range_list) #profile match date in list then get stress level

    results = cursor.fetchall()
    connect.close()

    level_map = {'Low': 1, 'Medium': 2, 'High': 3} #Create levels for charts (int to str)
    stress_levels = {date_: level_map.get(level, 0) for date_, level in results} #key=date, value=number of stress level
    values = [stress_levels.get(day, 0) for day in date_range_list] #Get stress level for each date even if 0
    return date_range_list, values

#Embed Matplotlib chart inside Tkinter frame
def embed_chart(fig, parent):
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw() #Draws chart on the canvas
    canvas.get_tk_widget().pack(expand=True, fill='both')

################################################################################################################################################################################

#Create all weekly charts
def create_weekly_charts(profile, container, bg_photo):
    #Clear everything on screen
    for widget in container.winfo_children():
        widget.destroy()

    #Background picture
    bg_label = tk.Label(container, image=bg_photo)
    bg_label.image = bg_photo  #Prevent garbage collection
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    #Retrieve weekly data
    mode = "weekly"  
    range_list = date_range(mode)

    dates, sessions = get_breathing_data(profile, range_list)
    dates_diary, diary_counts = get_diary_data(profile, range_list)
    dates_stress, stress_levels = get_stress_data(profile, range_list)
    moods, mood_counts = get_mood_data(profile, range_list)
    
    charts=[]

    # Chart 1: Breathing Exercise - Bar Chart
    plt.style.use('fivethirtyeight')
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    #Convert date strings to datetime object
    date_objects = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
    bars = ax1.bar(date_objects, sessions, color="#c3b091") #Draw vertical bars
    first_date = date_objects[0] #First date in list
    month_year = first_date.strftime('%B %Y')  #Month and year rn
    ax1.set_title(f"Breathing Sessions - {month_year}", fontsize=18) #Title
    ax1.set_xlabel("Date", fontsize=12, color='gray')
    ax1.set_ylabel("Number of Sessions", fontsize=12, color='gray')
    #Only show the day
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.setp(ax1.get_xticklabels(), rotation=0, fontsize=14)
    fig1.tight_layout() #Make sure nothing overlaps
    charts.append(fig1) #Saves chartyes pl

    # Chart 2: Mood Tracker - Pie Chart
    plt.style.use('fivethirtyeight')
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    #Convert date strings to datetime objects
    date_objects = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
    colors = ['#FFD700', '#87CEEB', '#FF6347', '#FF69B4', '#C0C0C0', '#90EE90']
    color_map = {
        "Happy": '#FFD700', "Sad": '#87CEEB', "Angry": '#FF6347',
        "Excited": '#FF69B4', "Sleepy": '#C0C0C0', "Relaxed": '#90EE90'
    } #Disctionary to represent colour for each mood
    pie_colors = [color_map[mood] for mood in moods]
    ax2.pie(mood_counts, labels=moods, autopct='%1.1f%%', colors=pie_colors, startangle=140) #Draw pie chart, autopct=show percentage of each sector
    first_date = date_objects[0] #First entry date
    month_year = first_date.strftime('%B %Y')  #Month and year rn
    start_date = datetime.strptime(dates_diary[0], '%Y-%m-%d')
    end_date = datetime.strptime(dates_diary[-1], '%Y-%m-%d')
    ax2.set_title(f"Mood Distribution - {month_year}", fontsize=18) 
    date_range_str = f"{start_date.strftime('%d %b')} – {end_date.strftime('%d %b %Y')}"
    #Add descriptive text below, centered 
    fig2.text(0.5, 0.03, f"Data from {date_range_str}", ha='center', fontsize=12, color='gray')
    fig2.tight_layout() #Make sure doesn't overlap
    charts.append(fig2) #Save chart

    # Chart 3: Diary Entry - Line Chart
    plt.style.use('fivethirtyeight')
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    #Convert date string to datetime objects
    date_objects = [datetime.strptime(d, '%Y-%m-%d') for d in dates_diary]
    ax3.plot(date_objects, diary_counts, marker='o', color='#6a5acd') #Marker=show dot at each data point
    first_date =date_objects[0] #First entry date
    month_year = first_date.strftime('%B %Y')  #Month and year rn
    ax3.set_title(f"Diary Entries - {month_year}", fontsize=18)
    ax3.set_xlabel("Date", fontsize=12, color='gray')
    ax3.set_ylabel("Number of Entries", fontsize=12, color='gray')
    #Only show the day
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.setp(ax3.get_xticklabels(), rotation=0, fontsize=14)
    fig3.tight_layout() #Make sure it doesn't overlap
    charts.append(fig3) #Save chart into list

    # Chart 4: Stress Quiz - Horizontal Bar Chart
    plt.style.use('fivethirtyeight')
    fig4, ax4 = plt.subplots(figsize=(5, 4))
    #Convert date string to datetime objects
    date_objects = [datetime.strptime(d, '%Y-%m-%d') for d in dates_stress]
    ax4.barh(date_objects, stress_levels, color='purple')
    #Only show the day
    ax4.yaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.setp(ax4.get_xticklabels(), rotation=0, fontsize=15)
    first_date = date_objects[0]
    month_year = first_date.strftime('%B %Y')  #Month and year rn
    ax4.set_title(f"Stress Levels - {month_year}", fontsize=18)
    ax4.set_xlim(0.5, 3.5)  #Centers ticks on bars
    ax4.set_xticks([1, 2, 3])
    ax4.set_xticklabels(['Low', 'Medium', 'High']) #Changes numbers to strings
    ax4.set_xlabel("Stress Level", fontsize=12, color='gray')
    ax4.set_ylabel("Date", fontsize=12, color='gray')
    ax4.invert_yaxis() #Show recent date at top
    fig4.tight_layout() #Make sure doesn't overlap
    charts.append(fig4) #Save chart to list

    #Layout 2x2 grid
    for i, fig in enumerate([fig1, fig2, fig3, fig4]): #Enumerate=get both the index and the item when looping
        frame = tk.Frame(container, bg='white') #Big outer frame
        frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew') #Place for each chart in frame
        #Allow each frame to resize properly
        container.grid_rowconfigure(i // 2, weight=1)
        container.grid_columnconfigure(i % 2, weight=1)

        #Clear screen
        for widget in frame.winfo_children():
            widget.destroy()

        embed_chart(fig, frame)
        
################################################################################################################################################################################
        
def create_monthly_charts(profile, container, bg_photo):
    #Clear screen
    for widget in container.winfo_children():
        widget.destroy()
        
    #Background picture
    bg_label = tk.Label(container, image=bg_photo)
    bg_label.image = bg_photo  #Prevent garbage collection
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    #Retrieve all monthly data
    mode = "monthly"  
    range_list = date_range(mode)
    dates, sessions = get_breathing_data(profile, range_list)
    dates_diary, diary_counts = get_diary_data(profile, range_list)
    dates_stress, stress_levels = get_stress_data(profile, range_list)
    moods, mood_counts = get_mood_data(profile, range_list)
    
    filtered_sessions = [(d, s) for d, s in zip(dates, sessions) if s > 0] #Only include sessions more than 0, Go through 2 list together using zip
    if filtered_sessions:
        dates, sessions = zip(*filtered_sessions) #Unzips list back into 2 separate list
    else:
        dates, sessions = [], []

    filtered_session_2 = [(d, s) for d, s in zip(dates_stress, stress_levels) if s > 0] #Only include sessions more than 0, Go through 2 list together using zip
    if filtered_sessions:
        dates_stress, stress_levels = zip(*filtered_session_2) #Unzips list back into 2 separate list
    else:
        dates, sessions = [], []
    
    charts=[]
    
    #Chart 1: Breathing Exercise - Bar Chart
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    ax1.bar(dates, sessions, color="#c3b091") #Draw vertical bar 
    #Get current date and time
    now = datetime.now() 
    month_year = now.strftime('%B %Y') #Month and year rn
    ax1.set_title(f"Breathing Sessions - {month_year}", fontsize=18)
    ax1.set_xticks(range(len(dates)))
    ax1.set_xlabel("Date", fontsize=12, color='gray')
    ax1.set_ylabel("Number of Sessions", fontsize=12, color='gray')
     #Only show the day
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.setp(ax1.get_xticklabels(), rotation=0, fontsize=12)
    fig1.tight_layout() #Make sure nothing overlaps
    charts.append(fig1) #Save chart to list

    # Chart 2: Mood Tracker - Pie Chart
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    color_map = {
        "Happy": '#FFD700', "Sad": '#87CEEB', "Angry": '#FF6347',
        "Excited": '#FF69B4', "Sleepy": '#C0C0C0', "Relaxed": '#90EE90'
    } #Moods and its colours
    pie_colors = [color_map[mood] for mood in moods]
    ax2.pie(mood_counts, labels=moods, autopct='%1.1f%%', colors=pie_colors, startangle=140) #autopct to show percentage
    #Get current date and time
    now = datetime.now() 
    month_year = now.strftime('%B %Y')#Month and year rn
    ax2.set_title(f"Mood Distribution - {month_year}", fontsize=18)
    #Add descriptive text below, centered 
    fig2.text(0.5, 0.03, f"Data from {month_year}", ha='center', fontsize=12, color='gray')
    fig2.tight_layout() #Make sure not overlap
    charts.append(fig2) #Save chart to list

    # Chart 3: Diary Entry - Line Chart
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    ax3.plot(dates_diary, diary_counts, marker='o', color='#6a5acd') #Marker = dot at data point
    #Get current date and time
    now = datetime.now() 
    month_year = now.strftime('%B %Y')#Month and year rn
    ax3.set_title(f"Diary Entries - {month_year}", fontsize=18)
    ax3.set_xticks(range(len(dates_diary)))
    ax3.set_xlabel("Date", fontsize=12, color='gray')
    ax3.set_ylabel("Number of Entries", fontsize=12, color='gray')
    #Only show the day
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.setp(ax3.get_xticklabels(), rotation=0, fontsize=8)
    fig3.tight_layout() #Make sure not overlap
    charts.append(fig3) #Save chart to list

    # Chart 4: Stress Quiz - Horizontal Bar Chart
    fig4, ax4 = plt.subplots(figsize=(5, 4))
    ax4.barh(dates_stress, stress_levels, color='purple')
    #Only show the day
    ax4.yaxis.set_major_formatter(mdates.DateFormatter('%d'))
    ax4.tick_params(axis='y')
    #Get current date and time
    now = datetime.now() 
    month_year = now.strftime('%B %Y')#Month and year rn
    ax4.set_title(f"Stress Levels - {month_year}", fontsize=18)
    ax4.set_xlim(0.5, 3.5) #Centers bar
    ax4.set_xticks([1, 2, 3])
    ax4.set_xticklabels(['Low', 'Medium', 'High']) #Change numbers to text
    ax4.set_xlabel("Stress Level", fontsize=12, color='gray')
    ax4.set_ylabel("Date", fontsize=12, color='gray')
    ax4.invert_yaxis() #Show recent date at top
    fig4.tight_layout() #Make sure no overlap
    charts.append(fig4) #Save chart to list

    for i, fig in enumerate(charts): #Enumerate=get both the index and the item when looping
        frame = tk.Frame(container, bg='white') #Big frame
        frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew') #Place for each chart
        container.grid_rowconfigure(i // 2, weight=1)
        container.grid_columnconfigure(i % 2, weight=1)
        embed_chart(fig, frame)
        
################################################################################################################################################################################ 
       
#Get mood entries for annual average calculation
def get_annual_mood_data(profile, date_list):
    connect = sqlite3.connect(database_file_path)
    cursor = connect.cursor()
    placeholders = ','.join('?' * len(date_list))
    cursor.execute(f'''
        SELECT date, mood FROM mood_entries
        WHERE profile = ? AND date IN ({placeholders})
    ''', [profile] + date_list)
    results = cursor.fetchall()
    connect.close()
    dates = [row[0] for row in results] #Date list
    mood_entries = [row[1] for row in results]  #Mood level list (numeric)
    return dates, mood_entries

def calculate_mood_frequencies(mood_names):
    freq = Counter(mood_names) #Count number of mood
    labels = list(freq.keys()) #Mood name
    counts = list(freq.values()) #Frequency of mood
    return labels, counts

#Convert numbers to text values
def convert_stress_number_to_label(level):
    if level == 1:
        return "Low"
    elif level == 2:
        return "Moderate"
    elif level == 3:
        return "High"
    elif level == 4:
        return "Severe"
    else:
        return "Unknown"

def calculate_monthly_average(dates, values):
    
    #Creates disctionary with empty list
    monthly_totals = defaultdict(list)

    for date_str, value in zip(dates, values): #Pairs each date with mood
        #Convert string to datetime object
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        month_label = date_obj.strftime('%b')  #Get month name
        monthly_totals[month_label].append(value)

    #Ensure months appear in calendar order
    months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    monthly_averages = []
    #Calculate average for each month
    for month in months_order:
        values = monthly_totals.get(month, [])
        avg = sum(values) / len(values) if values else 0
        monthly_averages.append(avg)
    
    return months_order, monthly_averages

def create_annual_charts(profile, container, bg_photo):
    for widget in container.winfo_children():
        widget.destroy()

    #Background picture
    bg_label = tk.Label(container, image=bg_photo)
    bg_label.image = bg_photo  #Prevent garbage collection
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    #Retrieve annual data
    mode = "annual"  
    range_list = date_range(mode)
    dates, sessions = get_breathing_data(profile, range_list)
    dates_diary, diary_counts = get_diary_data(profile, range_list)
    dates_stress, stress_levels = get_stress_data(profile, range_list)
    mood_dates, mood_levels = get_annual_mood_data(profile, range_list)
    moods, mood_counts = get_mood_data(profile, range_list)
    
    charts=[]
    
    # Chart 1: Breathing Sessions - Bar Chart
    months, avg_sessions = calculate_monthly_average(dates, sessions)
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    ax1.bar(months, avg_sessions, color="#c3b091")
    #Date and time now
    now = datetime.now() 
    year = now.strftime('%Y') #Year rn
    ax1.set_title(f"Breathing Sessions - {year}")
    ax1.set_ylabel("Average Number of Sessions", fontsize=12, color='gray')
    ax1.set_xlabel("Month", fontsize=12, color='gray')
    ax1.set_xticks(range(len(months)))
    ax1.set_xticklabels(months, fontsize=12)
    fig1.tight_layout() #Make sure no overlapping
    charts.append(fig1) #Save chart to list

    # Chart 2: Mood Tracker - Pie Chart
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    color_map = {
        "Happy": '#FFD700', "Sad": '#87CEEB', "Angry": '#FF6347',
        "Excited": '#FF69B4', "Sleepy": '#C0C0C0', "Relaxed": '#90EE90'
    } #Mood and its colours
    pie_colors = [color_map[mood] for mood in moods]
    ax2.pie(mood_counts, labels=moods, autopct='%1.1f%%', colors=pie_colors, startangle=140) #autopct for percentages
    #Date and time now
    now = datetime.now() 
    year = now.strftime('%Y') #Year rn
    ax2.set_title(f"Mood Distribution -{year}")
    #Add descriptive text below, centered 
    fig2.text(0.5, 0.03, f"Data from {year}", ha='center', fontsize=12, color='gray')
    fig2.tight_layout() #Make sure no overlapping
    charts.append(fig2) #Save chart to list

    # Chart 3: Diary Entries - Line Chart
    _, diary_avg = calculate_monthly_average(dates_diary, diary_counts)
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    ax3.plot(months, diary_avg, color='#6a5acd', marker='o') #marker=dot on graph exact date
    #Date and time now
    now = datetime.now() 
    year = now.strftime('%Y') #Year rn
    ax3.set_title(f"Diary Entries - {year}")
    ax3.set_ylabel("Average Number of Entries",fontsize=12, color='gray')
    ax3.set_xlabel("Month", fontsize=12, color='gray')
    ax3.set_xticks(range(len(months)))
    ax3.set_xticklabels(months, fontsize=12)
    fig3.tight_layout() #Make sure no overlapping
    charts.append(fig3) #Save chart
    
    # Chart 4: Stress Quiz - Horizontal Bar Chart
    #Create dictionary that counts monthly_stress of each
    monthly_stress = defaultdict(lambda: Counter())

    #Combine date and stress level together
    for date_str, level in zip(dates_stress, stress_levels):
        #Convert string to datetime object
        month = datetime.strptime(date_str, '%Y-%m-%d').strftime('%b') #Gets month abbreviation
        monthly_stress[month][level] += 1
        
    months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    stress_labels = ['Low', 'Moderate', 'High', 'Severe']
    
    #Prepare count for each stress level per month
    low_counts = [monthly_stress[m][1] for m in months_order]
    moderate_counts = [monthly_stress[m][2] for m in months_order]
    high_counts = [monthly_stress[m][3] for m in months_order]
    severe_counts = [monthly_stress[m][4] for m in months_order]
    
    #Creates array for y-axis (month), then show as text
    ind = np.arange(len(months_order))
    fig4, ax4 = plt.subplots(figsize=(5, 4))
    #Plot stacked bars horizontally
    ax4.barh(ind, low_counts, color='green', label='Low') #low bar
    ax4.barh(ind, moderate_counts, left=low_counts, color='orange', label='Moderate') #moderate bar, starts after green ends
    ax4.barh(ind, high_counts, left=[i+j for i,j in zip(low_counts, moderate_counts)], color='red', label='High') #high bar, calculates how far to the right (after green, orange) 
    ax4.barh(ind, severe_counts, left=[i+j+k for i,j,k in zip(low_counts, moderate_counts, high_counts)], color='maroon', label='Severe') #severe bar, starts after green, orange, red
    
    #Date and time now
    now = datetime.now() 
    year = now.strftime('%Y') #Year rn
    ax4.set_title(f"Stress Levels - {year}")
    ax4.set_ylabel("Month", fontsize=12, color='gray')
    ax4.set_xlabel("Frequency", fontsize=12, color='gray')
    ax4.set_yticks(ind)
    ax4.set_yticklabels(months_order)
    ax4.invert_yaxis()  #Show Jan at top
    ax4.set_xlim(0.5, 3.5) #Centers bart
    ax4.legend() #Show what ech colour represents
    fig4.tight_layout() #Make sure no overlapping
    charts.append(fig4) #Save chart

    for i, fig in enumerate(charts): #Enumerate= get both the index and the item when looping
        frame = tk.Frame(container, bg='white') #Big frame
        frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew') #Place for every chart
        container.grid_rowconfigure(i // 2, weight=1)
        container.grid_columnconfigure(i % 2, weight=1)
        embed_chart(fig, frame)

################################################################################################################################################################################

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
    
    # Ensure window is fully opaque (explicitly set, even if not needed)
    root.attributes('-alpha', 1.0) 
    
    #Solve issue of not closing properly
    def on_close():
        for fig in charts:
            plt.close(fig)
            plt.close('all')  #Just incase to close anything left open

        #Forcefully terminate the application to prevent lingering events
        sys.exit()
    
    #Background picture
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    bg_image_path = os.path.join(base_dir, "dashboard_bg.png") 
    bg_image = Image.open(bg_image_path)  #Open the image first
    bg_photo = ImageTk.PhotoImage(bg_image)  #Convert to PhotoImage

    #Track fullscreen state
    is_fullscreen = [False]

    # Toggle fullscreen using the 'f' key
    def toggle_fullscreen(event=None):
        is_fullscreen[0] = not is_fullscreen[0]
        root.attributes("-fullscreen", is_fullscreen[0])
        
    #Bind the 'f' key (lowercase only) (for fullscreen)
    root.bind("<Control-f>", toggle_fullscreen)
    
    # ESC to exit fullscreen
    def exit_fullscreen(event=None):
        root.attributes("-fullscreen", False)

    root.bind("<Escape>", exit_fullscreen)

    #Wrap sidebar and main_area in a content frame
    content_frame = tk.Frame(root, bg="white")
    content_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # Fills entire window

    #Sidebar
    sidebar = tk.Frame(content_frame, width=200, bg="#545454")
    sidebar.pack(side="left", fill="y")

    tab_label = tk.Label(sidebar, text="VIEW BY", fg="#ffffff", bg="#545454", font=("Segoe UI", 14, "bold"))
    tab_label.pack(pady=20)
    
    #Help with tips
    def show_help():
        messagebox.showinfo("Help", "Click on different views to get statistic on your app usage. There are 3 views: weekly, monthy and annual. You can find breathing session chart, mood distribution chart, diary entry chart and stress level chart.")

    #Exit button (bottom left in sidebar)
    exit_button = ctk.CTkButton(
        sidebar,
        text="❌ Exit",
        font=("Segoe UI", 14),
        fg_color="#FF5151",
        hover_color="#FF6A6A",
        text_color="white",
        corner_radius=25,
        command=on_close
    )
    exit_button.pack(side="bottom", anchor="w", padx=10, pady=(0, 10))  #Bottom-left with spacing

    #Help button (above exit)
    help_button = ctk.CTkButton(
        sidebar,
        text="❓ Help",
        font=("Segoe UI", 14),
        fg_color="#5A9BD5",
        hover_color="#7AB8FF",
        text_color="white",
        corner_radius=25,
        command=show_help
    )
    help_button.pack(side="bottom", anchor="w", padx=10, pady=(0, 10))  #Bottom-left, slightly above exit
    
    #Main area for charts (right)
    main_area = tk.Frame(content_frame, bg="white")
    main_area.pack(side="right", expand=True, fill="both")
    
    #Make the main_area resizable in grid
    main_area.grid_rowconfigure((0,1), weight=1)
    main_area.grid_columnconfigure((0,1), weight=1)
    
    def set_main_bg():
        width = main_area.winfo_width()
        height = main_area.winfo_height()

        #Prevent error
        if width < 10 or height < 10:
            #If size too small retry after 100ms
            root.after(100, set_main_bg)
            return

        #Resize to fit main area
        resized = bg_image.resize((width, height))
        #Convert to tkinter
        bg_photo_resized = ImageTk.PhotoImage(resized)
        #Create label for picture
        bg_label = tk.Label(main_area, image=bg_photo_resized)
        bg_label.image = bg_photo_resized  #Keep reference
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        #Lower the label so it doesn’t cover other widgets
        bg_label.lower()
        
    root.after(100, set_main_bg)  # Wait for geometry to be available

    def on_hover(e): e.widget.config(bg="#5C5C5C")
    def on_leave(e): e.widget.config(bg="#3C3C3C")

    def load_weekly():
        create_weekly_charts(profile, main_area, bg_photo)
        
        #Ceate sidebar buttons
        for tab in ["Weekly", "Monthly", "Annual"]:
            btn = tk.Button(
                sidebar, text=tab, fg="#ffffff", bg="#545454", relief="flat", font=("Segoe UI", 12), width=18, height=2, activebackground="#5C5C5C"
            )
            btn.pack(pady=10)
            btn.bind("<Enter>", on_hover)
            btn.bind("<Leave>", on_leave)
            if tab.lower() == "weekly":
                btn.config(command=lambda: create_weekly_charts(profile, main_area, bg_photo)) #weekly button
            elif tab.lower() == "monthly":
                btn.config(command=lambda: create_monthly_charts(profile, main_area, bg_photo))
            elif tab.lower() == "annual":
                btn.config(command=lambda: create_annual_charts(profile, main_area, bg_photo)) #lambda=delay execution till button is actually clicked

    # Load default view
    load_weekly()
    
    #Close all figures to resolve memory issue
    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()

if __name__ == "__main__":
    main()