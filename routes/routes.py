from flask import Blueprint, request, render_template, redirect, session
from services.log_service import extract_logs
import os
from routes.face_routes import totalreg
from datetime import date
import sqlite3

auth = Blueprint('auth', __name__)

main = Blueprint('main', __name__)

datetoday2 = date.today().strftime("%d-%B-%Y")


##main routes
@main.route('/')
def home():
    names, rolls, times, l = extract_logs()
    return render_template(
        'home.html',
        names=names,
        rolls=rolls,
        times=times,
        l=l,
        totalreg=totalreg(),
        datetoday2=datetoday2
    )
    
## auth routes
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("database/system.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, role 
            FROM users 
            WHERE name=? AND password=?
        """, (username, password))

        user = cur.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]

            # 🔥 redirect حسب role
            if user[2] == "admin":
                return redirect('/admin')
            else:
                return redirect('/user')

        return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/login')