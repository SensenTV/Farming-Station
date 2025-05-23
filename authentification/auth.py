import sqlite3
import bcrypt

def verify_user(username, password):
    conn = sqlite3.connect('SQLight/users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM user WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return False, None

    stored_hash, role = result
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return True, role
    return False, None
