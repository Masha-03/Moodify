import tkinter
from tkinter import*
from PIL import ImageTk, Image
import pygame
import sqlite3

root = Tk()
root.title('database')
root.geometry("400x400")

#Create database or connect to existing one
conc = sqlite3.connect('users.db')

#Create cursor
cur = conc.cursor()

#Create table
cur.execute("""CREATE TABLE username (
            username text, 
            gender text,
            )""")


#Update changes
conc.commit()
#Close conection
conc.close()
root.mainloop()
