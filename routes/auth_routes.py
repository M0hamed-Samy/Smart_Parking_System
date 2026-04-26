from flask import Blueprint, request, render_template, session, redirect
import sqlite3

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("database/system.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name
            FROM users
            WHERE name=? AND password=? AND role='admin'
        """, (username, password))

        admin = cur.fetchone()
        conn.close()

        if admin:
            session['admin_id'] = admin[0]
            return redirect('/admin/dashboard')

        return render_template("login.html", error="Invalid admin credentials")

    return render_template("login.html")


@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/login')