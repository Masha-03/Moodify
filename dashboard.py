import matplotlib.pyplot as plt #For grpahs & charts
import sqlite3
from datetime import datetime, timedelta #timedelta - difference between dates

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

    #Make window fullscreen
    mng = plt.get_current_fig_manager()
    try:
        mng.window.state('zoomed')  #For Tk backend
    except:
        try:
            mng.full_screen_toggle()  #For Qt backend(GUI system)
        except:
            pass  #If all else fails, skip fullscreen

    plt.tight_layout()
    plt.show() #Open Matplotlib window

#Run everything
get_profile()
if profile:
    dates, sessions = get_breathing_data(profile)
    plot_breathing_chart(dates, sessions)
else:
    print("No profile found.")
    