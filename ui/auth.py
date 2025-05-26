import sqlite3
import bcrypt

def verify_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM user WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return False

    stored_hash = result[0]
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
