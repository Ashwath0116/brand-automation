
import sqlite3

try:
    conn = sqlite3.connect('backend/bizforge.db')
    cursor = conn.cursor()
    
    email = 'rockashwath12@gmail.com'
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if user:
        print(f"User found: {user}")
        cursor.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (email,))
        conn.commit()
        print(f"Successfully promoted {email} to admin.")
    else:
        print(f"User {email} not found in database.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
