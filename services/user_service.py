from services.db_service import get_connection
from datetime import datetime
import os

def add_user(name, role, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (name, role, password, created_at)
        VALUES (?, ?, ?, ?)
    """, (name, role, password, datetime.now()))

    user_id = cur.lastrowid

    conn.commit()
    conn.close()

    os.makedirs(f"static/faces/{user_id}", exist_ok=True)

    return user_id


def delete_user(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE id=?", (user_id,))

    conn.commit()
    conn.close()