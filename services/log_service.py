import cv2
import os
from flask import Flask, request, render_template
from datetime import date
from datetime import datetime
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import joblib
import sqlite3

datetoday =  date.today().strftime("%m_%d_%y")


#for logs later
def extract_logs():
    conn = sqlite3.connect("database/system.db")
    cur = conn.cursor()

    cur.execute("SELECT name, user_id, time FROM logs ORDER BY id DESC")
    rows = cur.fetchall()

    conn.close()

    names = [r[0] for r in rows]
    rolls = [r[1] for r in rows]
    times = [r[2] for r in rows]

    return names, rolls, times, len(rows)

def add_logs(user_id, username):
    current_time = datetime.now().strftime("%H:%M:%S")

    conn = sqlite3.connect("database/system.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO logs (user_id, name, time, date)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, current_time, datetoday))

    conn.commit()
    conn.close()
    
    
def get_username_from_db(user_id):
    conn = sqlite3.connect("database/system.db")
    cur = conn.cursor()

    cur.execute("SELECT name FROM users WHERE id=?", (user_id,))
    result = cur.fetchone()

    conn.close()
    return result[0] if result else "Unknown"
    
    
def totalreg():
    return len(os.listdir('static/faces'))

def add_user_db(name, role, password):
    conn = sqlite3.connect("database/system.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (name, role, password, created_at)
        VALUES (?, ?, ?, ?)
    """, (name, role, password, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    user_id = cur.lastrowid

    conn.commit()
    conn.close()

    return user_id



def getallusers():
    userlist = os.listdir('static/faces')
    names = []
    rolls = []
    l = len(userlist)

    for i in userlist:
        name, roll = i.split('_')
        names.append(name)
        rolls.append(roll)

    return userlist, names, rolls, l