from flask import Blueprint, render_template, request, redirect, session
from services.user_service import add_user, delete_user
from services.log_service import extract_logs
from services.face_service import train_model
import sqlite3

admin = Blueprint('admin', __name__, url_prefix='/admin')


# 🔐 حماية بسيطة
def check_admin():
    return session.get('admin_id') is not None


# 📊 Dashboard
@admin.route('/dashboard')
def dashboard():

    if not check_admin():
        return redirect('/login')

    conn = sqlite3.connect("database/system.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    conn.close()

    logs = extract_logs()

    return render_template("admin.html", users=users, logs=logs)


# ➕ Add User
@admin.route('/users/add', methods=['POST'])
def add():

    if not check_admin():
        return redirect('/login')

    name = request.form['name']
    password = request.form['password']

    add_user(name, "employee", password)
    train_model()

    return redirect('/admin/dashboard')


# 🗑 Delete User
@admin.route('/users/delete/<int:user_id>')
def delete(user_id):

    if not check_admin():
        return redirect('/login')

    delete_user(user_id)
    train_model()

    return redirect('/admin/dashboard')